#!/usr/bin/env python3
"""Offline workflow checks shared by Claude Code and Codex (Python 3.10+)."""

import argparse
from contextlib import contextmanager
import hashlib
import json
import math
import os
from pathlib import Path
import subprocess
import sys
import tempfile


class Invalid(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise Invalid(message)


def read(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    return json.loads(Path(path).read_text(), object_pairs_hook=pairs)


def digest(path):
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def fingerprint(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, allow_nan=False).encode()).hexdigest()


def number(value, name, minimum=0, maximum=None, integer=False):
    require(type(value) in ((int,) if integer else (int, float)), f"{name}: invalid number")
    require(math.isfinite(value) and value >= minimum, f"{name}: below minimum or non-finite")
    require(maximum is None or value <= maximum, f"{name}: above maximum")
    return value


def string(value, name):
    require(isinstance(value, str) and bool(value.strip()), f"{name}: required string")
    return value


def boolean(value, name):
    require(type(value) is bool, f"{name}: required boolean")
    return value


def version(value):
    require(isinstance(value, dict), "Expected a JSON object")
    require(type(value.get("schema_version")) is int and value["schema_version"] == 1,
            "Unsupported schema_version; expected 1")


def artifact(root, ref):
    require(isinstance(ref, dict), "Expected artifact {path, sha256}")
    path = Path(root) / string(ref.get("path"), "artifact.path")
    require(digest(path) == ref.get("sha256"), f"Artifact changed: {path}")
    return path


def reference(root, path):
    path = Path(path).resolve()
    return {"path": os.path.relpath(path, Path(root).resolve()), "sha256": digest(path)}


def baseline_check(b):
    version(b)
    for key in ("rubric_sha256", "contract_sha256"):
        value = b[key]
        require(isinstance(value, str) and len(value) == 64 and
                all(c in "0123456789abcdef" for c in value), f"{key}: expected SHA-256")
    number(b["target"], "target", 0, 1)
    number(b["min_generated"], "min_generated", 1, integer=True)
    number(b["min_per_cohort"], "min_per_cohort", 1, integer=True)
    number(b["max_tv_distance"], "max_tv_distance", 0, 1)
    number(b["max_cycles"], "max_cycles", 1, integer=True)
    for key in ("max_cost_usd", "max_wall_seconds"):
        number(b[key], key, 0.000001)
    require(isinstance(b["cohorts"], dict) and b["cohorts"], "Define coverage cohorts")
    for name, cell in b["cohorts"].items():
        string(name, "cohort name")
        number(cell["min_accepted"], "min_accepted", 0, integer=True)
        number(cell["baseline_share"], "baseline_share", 0, 1)
    require(math.isclose(sum(c["baseline_share"] for c in b["cohorts"].values()), 1),
            "Baseline shares must sum to 1")


INPUT_ROLES = {"config", "prompt", "rubric", "contract", "launcher", "dependencies"}


def evaluate(root, baseline, manifest_ref, review_ref):
    """Recompute a verdict from all generated IDs, never a survivor-only count."""
    baseline_check(baseline)
    manifest_path = artifact(root, manifest_ref)
    review_path = artifact(root, review_ref)
    m, r = read(manifest_path), read(review_path)
    version(m)
    version(r)
    for key in ("batch_id", "generator_commit", "framework_commit", "model_id"):
        string(m[key], key)
    number(m["seed"], "seed", 0, integer=True)
    number(m["generated_count"], "generated_count", 1, integer=True)
    require(m["purpose"] in {"functional", "validation", "scale"}, "Invalid batch purpose")
    require(INPUT_ROLES <= m["inputs"].keys(), "Missing provenance input roles")
    for ref in m["inputs"].values():
        artifact(root, ref)
    artifact(root, m["data"])
    require(m["inputs"]["rubric"]["sha256"] == baseline["rubric_sha256"],
            "Evaluation rubric differs from approved baseline")
    require(m["inputs"]["contract"]["sha256"] == baseline["contract_sha256"],
            "Task contract differs from approved baseline")
    require(r["batch_id"] == m["batch_id"], "Review belongs to another batch")
    require(r["manifest_sha256"] == manifest_ref["sha256"], "Review manifest mismatch")
    require(r["rubric_sha256"] == baseline["rubric_sha256"], "Review rubric mismatch")
    for key in ("edited_during_cycle", "raw_read_complete", "no_new_raw_concerns",
                "refutation_complete", "ratchet_passed"):
        boolean(r[key], key)
    number(r["critical_findings"], "critical_findings", 0, integer=True)
    for key in ("cost_usd", "wall_seconds"):
        number(r[key], key)

    inventory = read(artifact(root, m["inventory"]))
    require(isinstance(inventory, list) and len(inventory) == m["generated_count"],
            "Inventory must contain every generated row, including rejected rows")
    require(isinstance(r["rows"], list), "Review rows must be an array")
    rows = {}
    for row in inventory:
        row_id = string(row["id"], "row id")
        require(row_id not in rows, "Duplicate generated row id")
        require(row["cohort"] in baseline["cohorts"], "Unknown cohort")
        rows[row_id] = row
    reviewed = {}
    for row in r["rows"]:
        require(row["id"] in rows and row["id"] not in reviewed, "Unknown or duplicate reviewed id")
        boolean(row["a_pass"], "a_pass")
        require(row["b_pass"] is None or type(row["b_pass"]) is bool, "Invalid b_pass")
        reviewed[row["id"]] = row
    require(rows.keys() == reviewed.keys(), "Track A must cover the full generated inventory")

    n = len(rows)
    a = sum(v["a_pass"] for v in reviewed.values())
    b_n = sum(v["b_pass"] is not None for v in reviewed.values())
    b = sum(v["b_pass"] is True for v in reviewed.values())
    joint = sum(v["a_pass"] and v["b_pass"] is True for v in reviewed.values())
    cells = {}
    reasons = []
    for name, spec in baseline["cohorts"].items():
        members = [reviewed[k] for k, v in rows.items() if v["cohort"] == name]
        accepted = sum(v["a_pass"] and v["b_pass"] is True for v in members)
        rate = accepted / len(members) if members else 0
        cells[name] = {"generated": len(members), "joint_accepted": accepted,
                       "joint_rate": rate if all(v["b_pass"] is not None for v in members) else None,
                       "joint_observed_lower_bound": rate}
        if len(members) < baseline["min_per_cohort"]:
            reasons.append(f"Insufficient sample for cohort {name}")
        if accepted < spec["min_accepted"] or rate < baseline["target"]:
            reasons.append(f"Coverage floor or joint target failed for cohort {name}")
    tv = (sum(abs(cells[k]["joint_accepted"] / joint - v["baseline_share"])
              for k, v in baseline["cohorts"].items()) / 2) if joint else 1.0
    if m["purpose"] != "validation":
        reasons.append("Only validation batches count toward the scale checkpoint")
    if n < baseline["min_generated"]:
        reasons.append("Insufficient generated sample")
    if b_n != n:
        reasons.append("Track B is sampled/incomplete; no full-batch pass is established")
    if joint / n < baseline["target"]:
        reasons.append("Joint pass rate below target")
    if tv > baseline["max_tv_distance"]:
        reasons.append("Coverage drift exceeds approved budget")
    if r["edited_during_cycle"]:
        reasons.append("Edited cycle cannot pass")
    for key in ("raw_read_complete", "no_new_raw_concerns", "refutation_complete", "ratchet_passed"):
        if not r[key]:
            reasons.append(f"Unmet evidence: {key}")
    if r["critical_findings"]:
        reasons.append("Surviving critical findings")
    identity = {k: m[k] for k in ("generator_commit", "framework_commit", "model_id")}
    identity["inputs"] = {k: v["sha256"] for k, v in m["inputs"].items()}
    identity["baseline"] = fingerprint(baseline)
    return {"pass": not reasons, "reasons": reasons, "batch_id": m["batch_id"],
            "fingerprint": fingerprint(identity), "seed": m["seed"], "data_sha256": m["data"]["sha256"],
            "generated": n, "a_rate": a / n, "b_reviewed": b_n,
            "b_rate_reviewed": b / b_n if b_n else None,
            "joint_rate": joint / n if b_n == n else None,
            "joint_observed_lower_bound": joint / n, "cohorts": cells,
            "tv_distance": tv, "cost_usd": r["cost_usd"], "wall_seconds": r["wall_seconds"]}


def state_check(root, state):
    version(state)
    string(state["project_id"], "project_id")
    number(state["revision"], "revision", 0, integer=True)
    require(state["stage"] in {"context", "design", "implement", "quality", "scale", "complete"},
            "Invalid stage")
    for key in ("cursor", "next_action"):
        string(state[key], key)
    require(state["stop_reason"] is None or isinstance(state["stop_reason"], str), "Invalid stop reason")
    require(state["rollback_anchor"] is None or isinstance(state["rollback_anchor"], str), "Invalid anchor")
    require(isinstance(state["history"], list), "Invalid history")
    job = state["active_job"]
    if job is not None:
        for key in ("id", "batch_id", "backend"):
            string(job[key], f"active_job.{key}")
    review = state["review_cursor"]
    if review is not None:
        string(review["batch_id"], "review_cursor.batch_id")
        for key in ("planned_chunks", "completed_chunks"):
            require(isinstance(review[key], list) and all(isinstance(v, str) for v in review[key]),
                    f"Invalid {key}")
            require(len(review[key]) == len(set(review[key])), f"Duplicate {key}")
        require(set(review["completed_chunks"]) <= set(review["planned_chunks"]), "Unknown review chunk")
    if state["baseline"] is not None:
        baseline_check(read(artifact(root, state["baseline"])))
    for key in ("design_approval", "scale_approval"):
        approval = state[key]
        if approval is not None:
            for field in ("source", "approved_at", "subject_sha256"):
                string(approval[field], f"{key}.{field}")
    return state


def load_state(root):
    return state_check(root, read(Path(root) / "state.json"))


def history_results(root, state):
    require(state["baseline"] is not None, "Approved baseline is missing")
    baseline = read(artifact(root, state["baseline"]))
    results, ids = [], set()
    for entry in state["history"]:
        result = evaluate(root, baseline, entry["manifest"], entry["review"])
        require(result["batch_id"] not in ids, "Batch already counted")
        ids.add(result["batch_id"])
        results.append(result)
    return baseline, results


def streak(results):
    if not results:
        return 0
    count, seeds, datasets = 0, set(), set()
    for r in reversed(results):
        if (not r["pass"] or r["fingerprint"] != results[-1]["fingerprint"] or
                r["seed"] in seeds or r["data_sha256"] in datasets):
            break
        count += 1
        seeds.add(r["seed"])
        datasets.add(r["data_sha256"])
    return count


def budget_reasons(baseline, results):
    reasons = []
    if len(results) >= baseline["max_cycles"]:
        reasons.append("Cycle budget exhausted")
    if sum(r["cost_usd"] for r in results) >= baseline["max_cost_usd"]:
        reasons.append("Cost budget exhausted")
    if sum(r["wall_seconds"] for r in results) >= baseline["max_wall_seconds"]:
        reasons.append("Wall-time budget exhausted")
    return reasons


def resume(root):
    state = load_state(root)
    result = {"stage": state["stage"], "cursor": state["cursor"],
              "revision": state["revision"], "next_action": state["next_action"]}
    if state["stop_reason"]:
        result.update(action="stop", reason=state["stop_reason"])
    elif state["active_job"]:
        result.update(action="reconcile_job", job=state["active_job"])
    elif state["review_cursor"]:
        c = state["review_cursor"]
        result.update(action="resume_review", batch_id=c["batch_id"],
                      remaining_chunks=[v for v in c["planned_chunks"] if v not in c["completed_chunks"]])
    elif state["stage"] != "quality":
        result.update(action="follow_stage")
    else:
        baseline, results = history_results(root, state)
        count = streak(results)
        reasons = budget_reasons(baseline, results)
        approval = state["design_approval"]
        if not approval or approval["subject_sha256"] != state["baseline"]["sha256"]:
            result.update(action="stop", reason="Design approval missing or stale")
        elif count >= 2:
            result.update(action="await_scale_approval", clean_pass_streak=count)
        elif reasons:
            result.update(action="stop", reason="; ".join(reasons))
        else:
            result.update(action="confirmation_run" if count == 1 else "follow_next_action",
                          clean_pass_streak=count)
    return result


def verify_checkout(path, expected_commit, label):
    head = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
    dirty = subprocess.check_output(["git", "-C", str(path), "status", "--porcelain"], text=True)
    require(not dirty, f"{label} worktree is dirty")
    require(head == expected_commit, f"{label} HEAD differs from reviewed commit")


def scale_gate(root, plan_path, infra, framework=None):
    state = load_state(root)
    require(state["stage"] in {"quality", "scale"}, "Project is not ready for scaling")
    require(not state["stop_reason"] and state["active_job"] is None and state["review_cursor"] is None,
            "Resolve the stop, active job, or incomplete review before scaling")
    baseline, results = history_results(root, state)
    require(streak(results) >= 2, "Two consecutive clean passes with distinct seeds are required")
    approval = state["design_approval"]
    require(approval is not None and approval["subject_sha256"] == state["baseline"]["sha256"],
            "Design approval missing or stale")
    plan = read(plan_path)
    version(plan)
    require(plan["fingerprint"] == results[-1]["fingerprint"], "Launch plan uses a different validated version")
    require(plan["unratified_deltas"] == [], "Unratified design deltas block scale")
    for field in ("max_rows", "max_cost_usd", "max_wall_seconds"):
        number(plan[field], field, 0.000001, integer=field == "max_rows")
    require(isinstance(plan["command"], list) and plan["command"] and
            all(isinstance(v, str) and v for v in plan["command"]), "Record the exact launch command")
    artifact(root, plan["scale_config"])
    last_manifest = read(artifact(root, state["history"][-1]["manifest"]))
    require(plan["current_inputs"].keys() == last_manifest["inputs"].keys(), "Current input roles differ")
    for role, ref in plan["current_inputs"].items():
        artifact(root, ref)
        require(ref["sha256"] == last_manifest["inputs"][role]["sha256"], f"Current {role} differs")
    verify_checkout(infra, last_manifest["generator_commit"], "Generator")
    verify_checkout(framework or Path(__file__).resolve().parents[1],
                    last_manifest["framework_commit"], "Framework")
    approval = state["scale_approval"]
    require(approval is not None and approval["subject_sha256"] == digest(plan_path),
            "Scale approval missing or stale for this exact launch plan")
    return {"pass": True, "clean_pass_streak": streak(results), "plan_sha256": digest(plan_path),
            "approval_source": approval["source"], "command_executed": False}


@contextmanager
def locked(root):
    lock = Path(root) / ".state.lock"
    try:
        lock.mkdir()
    except FileExistsError as exc:
        raise Invalid("State writer already active; reconcile stale lock before retrying") from exc
    try:
        yield
    finally:
        lock.rmdir()


def atomic_write(path, data):
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".state-")
    try:
        with os.fdopen(fd, "w") as stream:
            json.dump(data, stream, indent=2, allow_nan=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def update(root, expected_revision, patch=None, manifest=None, review=None):
    with locked(root):
        state = load_state(root)
        require(state["revision"] == expected_revision, "Stale state revision; reload before writing")
        if patch is not None:
            allowed = {"stage", "cursor", "next_action", "stop_reason", "active_job", "review_cursor",
                       "rollback_anchor", "design_approval", "scale_approval", "baseline"}
            require(isinstance(patch, dict) and patch.keys() <= allowed, "Patch contains protected state fields")
            require("baseline" not in patch or not state["history"],
                    "Baseline changes require a new checkpoint directory; retain old evidence")
            state.update(patch)
        else:
            require(state["stage"] == "quality", "Record validation reviews in quality stage")
            baseline, results = history_results(root, state)
            manifest_ref, review_ref = reference(root, manifest), reference(root, review)
            result = evaluate(root, baseline, manifest_ref, review_ref)
            require(result["batch_id"] not in {r["batch_id"] for r in results}, "Batch already counted")
            require(state["active_job"] is None, "Reconcile generation completion before recording review")
            cursor = state["review_cursor"]
            if cursor is not None:
                require(cursor["batch_id"] == result["batch_id"], "Review cursor belongs to another batch")
                require(set(cursor["completed_chunks"]) == set(cursor["planned_chunks"]), "Review chunks incomplete")
            state["history"].append({"manifest": manifest_ref, "review": review_ref})
            state["review_cursor"] = None
            count = streak(results + [result])
            state["cursor"] = "ready_for_approval" if count >= 2 else "pass_1" if count else "diagnose"
            state["next_action"] = ("Present checkpoint and exact scale plan" if count >= 2 else
                                    "Generate an independent confirmation batch" if count else
                                    "Diagnose the review reasons before repairing")
        state["revision"] += 1
        state_check(root, state)
        atomic_write(Path(root) / "state.json", state)
        return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("validate-state", "resume", "check-gates", "update-state", "record-review"):
        p = commands.add_parser(name)
        p.add_argument("project", type=Path)
        if name == "check-gates":
            p.add_argument("--plan", type=Path, required=True)
            p.add_argument("--infra", type=Path, required=True)
        if name in {"update-state", "record-review"}:
            p.add_argument("--expected-revision", type=int, required=True)
        if name == "update-state":
            p.add_argument("--patch", type=Path, required=True)
        if name == "record-review":
            p.add_argument("--manifest", type=Path, required=True)
            p.add_argument("--review", type=Path, required=True)
    p = commands.add_parser("check-batch")
    p.add_argument("project", type=Path)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--review", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "validate-state":
            state = load_state(args.project)
            if state["history"]:
                history_results(args.project, state)
            result = {"valid": True, "revision": state["revision"]}
        elif args.command == "resume":
            result = resume(args.project)
        elif args.command == "check-gates":
            result = scale_gate(args.project, args.plan, args.infra)
        elif args.command == "check-batch":
            state = load_state(args.project)
            baseline = read(artifact(args.project, state["baseline"]))
            result = evaluate(args.project, baseline, reference(args.project, args.manifest),
                              reference(args.project, args.review))
        elif args.command == "update-state":
            result = update(args.project, args.expected_revision, patch=read(args.patch))
        else:
            result = update(args.project, args.expected_revision, manifest=args.manifest, review=args.review)
        print(json.dumps(result, indent=2, allow_nan=False))
        return 1 if result.get("pass") is False or result.get("action") == "stop" else 0
    except (OSError, ValueError, KeyError, TypeError, AttributeError, OverflowError, subprocess.SubprocessError) as exc:
        print(json.dumps({"error": str(exc)}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
