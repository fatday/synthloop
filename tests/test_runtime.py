"""Offline acceptance scenarios; no model, scheduler or generation service calls."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("synthloop", ROOT / "tools/synthloop.py")
sl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sl)


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.infra = self.root / "infra"
        self.infra.mkdir()
        self.git("init", "-q")
        self.git("config", "user.email", "fixture@example.invalid")
        self.git("config", "user.name", "Fixture")
        (self.infra / "generator.py").write_text("# offline fixture\n")
        self.git("add", "generator.py")
        self.git("commit", "-qm", "fixture")
        self.commit = self.git("rev-parse", "HEAD").strip()
        self.inputs = {}
        for role in sl.INPUT_ROLES:
            path = self.root / f"{role}.txt"
            path.write_text(f"approved {role}\n")
            self.inputs[role] = sl.reference(self.root, path)
        self.baseline = {
            "schema_version": 1, "target": .95, "min_generated": 100,
            "min_per_cohort": 40, "max_tv_distance": .2, "max_cycles": 6,
            "max_cost_usd": 100, "max_wall_seconds": 10000,
            "rubric_sha256": self.inputs["rubric"]["sha256"],
            "contract_sha256": self.inputs["contract"]["sha256"],
            "cohorts": {"easy": {"min_accepted": 40, "baseline_share": .5},
                        "hard": {"min_accepted": 40, "baseline_share": .5}},
        }
        self.write("baseline.json", self.baseline)
        self.state = sl.read(ROOT / "templates/state.json")
        self.state.update(project_id="fixture", stage="quality", cursor="smoke",
                          baseline=sl.reference(self.root, self.root / "baseline.json"),
                          rollback_anchor=self.commit)
        self.state["design_approval"] = self.approval(self.root / "baseline.json")
        self.write("state.json", self.state)

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.infra), *args], text=True,
                                       stderr=subprocess.DEVNULL)

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value))
        return path

    def approval(self, path):
        return {"source": "fixture user decision", "approved_at": "2026-09-20T00:00:00Z",
                "subject_sha256": sl.digest(path)}

    def batch(self, batch_id="b1", seed=1, easy=50):
        inventory = [{"id": f"{batch_id}-{i}", "cohort": "easy" if i < easy else "hard"}
                     for i in range(100)]
        inv = self.write(f"{batch_id}/inventory.json", inventory)
        data = self.write(f"{batch_id}/data.json", [{**r, "text": "fixture"} for r in inventory])
        m = {"schema_version": 1, "batch_id": batch_id, "purpose": "validation",
             "generator_commit": self.commit, "framework_commit": self.commit,
             "model_id": "fixture-model", "seed": seed, "generated_count": 100,
             "inputs": copy.deepcopy(self.inputs), "inventory": sl.reference(self.root, inv),
             "data": sl.reference(self.root, data)}
        mp = self.write(f"{batch_id}/manifest.json", m)
        r = {"schema_version": 1, "batch_id": batch_id, "manifest_sha256": sl.digest(mp),
             "rubric_sha256": self.baseline["rubric_sha256"], "edited_during_cycle": False,
             "raw_read_complete": True, "no_new_raw_concerns": True,
             "refutation_complete": True, "ratchet_passed": True, "critical_findings": 0,
             "cost_usd": 1, "wall_seconds": 10,
             "rows": [{"id": v["id"], "a_pass": True, "b_pass": True} for v in inventory]}
        rp = self.write(f"{batch_id}/review.json", r)
        return mp, rp

    def change_review(self, rp, **changes):
        r = sl.read(rp)
        r.update(changes)
        self.write(rp, r)

    def evaluate(self, mp, rp):
        return sl.evaluate(self.root, self.baseline, sl.reference(self.root, mp), sl.reference(self.root, rp))

    def record(self, mp, rp):
        return sl.update(self.root, sl.load_state(self.root)["revision"], manifest=mp, review=rp)

    def patch(self, **values):
        return sl.update(self.root, sl.load_state(self.root)["revision"], patch=values)

    def approved_plan(self):
        self.record(*self.batch("b1", 1))
        self.record(*self.batch("b2", 2))
        _, results = sl.history_results(self.root, sl.load_state(self.root))
        config = self.write("scale_config.json", {"rows": 1000})
        plan = {"schema_version": 1, "fingerprint": results[-1]["fingerprint"],
                "command": ["generator", "--rows", "1000"], "max_rows": 1000,
                "max_cost_usd": 50, "max_wall_seconds": 1000, "unratified_deltas": [],
                "scale_config": sl.reference(self.root, config), "current_inputs": self.inputs}
        path = self.write("launch_plan.json", plan)
        self.patch(scale_approval=self.approval(path))
        return path

    def test_disjoint_track_failures_do_not_pass_joint_gate(self):
        mp, rp = self.batch()
        r = sl.read(rp)
        for row in r["rows"][:5]:
            row["a_pass"] = False
        for row in r["rows"][5:10]:
            row["b_pass"] = False
        self.write(rp, r)
        result = self.evaluate(mp, rp)
        self.assertEqual((result["a_rate"], result["b_rate_reviewed"], result["joint_rate"]), (.95, .95, .9))
        self.assertFalse(result["pass"])

    def test_survivor_only_report_is_invalid(self):
        mp, rp = self.batch()
        r = sl.read(rp)
        r["rows"].pop()
        self.write(rp, r)
        with self.assertRaisesRegex(sl.Invalid, "full generated inventory"):
            self.evaluate(mp, rp)

    def test_sampled_b_is_unknown_not_a_full_pass(self):
        mp, rp = self.batch()
        r = sl.read(rp)
        r["rows"][0]["b_pass"] = None
        self.write(rp, r)
        result = self.evaluate(mp, rp)
        self.assertFalse(result["pass"])
        self.assertIsNone(result["joint_rate"])
        self.assertEqual(result["b_reviewed"], 99)

    def test_normal_coverage_fluctuation_can_pass(self):
        self.record(*self.batch("b1", 1, easy=50))
        self.record(*self.batch("b2", 2, easy=49))
        self.assertEqual(sl.resume(self.root)["action"], "await_scale_approval")

    def test_worst_cohort_cannot_hide_in_global_average(self):
        mp, rp = self.batch()
        r = sl.read(rp)
        for row in r["rows"][:4]:
            row["b_pass"] = False
        self.write(rp, r)
        result = self.evaluate(mp, rp)
        self.assertEqual(result["joint_rate"], .96)
        self.assertFalse(result["pass"])

    def test_functional_smoke_cannot_count_as_validation(self):
        mp, rp = self.batch()
        m = sl.read(mp)
        m["purpose"] = "functional"
        self.write(mp, m)
        self.change_review(rp, manifest_sha256=sl.digest(mp))
        self.assertFalse(self.evaluate(mp, rp)["pass"])

    def test_first_pass_requests_confirmation_second_stops(self):
        self.record(*self.batch("b1", 1))
        self.assertEqual(sl.resume(self.root)["action"], "confirmation_run")
        self.record(*self.batch("b2", 2))
        self.assertEqual(sl.resume(self.root)["action"], "await_scale_approval")

    def test_duplicate_batch_cannot_advance_history(self):
        mp, rp = self.batch()
        self.record(mp, rp)
        before = (self.root / "state.json").read_bytes()
        with self.assertRaisesRegex(sl.Invalid, "already counted"):
            self.record(mp, rp)
        self.assertEqual(before, (self.root / "state.json").read_bytes())

    def test_same_seed_does_not_establish_confirmation(self):
        self.record(*self.batch("b1", 1))
        self.record(*self.batch("b2", 1))
        self.assertEqual(sl.resume(self.root)["clean_pass_streak"], 1)

    def test_edit_between_passes_breaks_streak(self):
        self.record(*self.batch("b1", 1))
        mp, rp = self.batch("b2", 2)
        self.change_review(rp, edited_during_cycle=True)
        self.record(mp, rp)
        self.record(*self.batch("b3", 3))
        self.assertEqual(sl.resume(self.root)["clean_pass_streak"], 1)

    def test_changed_model_starts_new_streak(self):
        self.record(*self.batch("b1", 1))
        mp, rp = self.batch("b2", 2)
        m = sl.read(mp)
        m["model_id"] = "different-model"
        self.write(mp, m)
        self.change_review(rp, manifest_sha256=sl.digest(mp))
        self.record(mp, rp)
        self.assertEqual(sl.resume(self.root)["clean_pass_streak"], 1)

    def test_active_job_is_reconciled_not_relaunched(self):
        self.patch(active_job={"id": "submission-key", "batch_id": "b1", "backend": "fixture"})
        self.assertEqual(sl.resume(self.root)["action"], "reconcile_job")
        with self.assertRaisesRegex(sl.Invalid, "Reconcile generation"):
            self.record(*self.batch())

    def test_partial_review_resumes_only_missing_chunks(self):
        self.patch(review_cursor={"batch_id": "b1", "planned_chunks": ["a", "b"], "completed_chunks": ["a"]})
        self.assertEqual(sl.resume(self.root)["remaining_chunks"], ["b"])
        with self.assertRaisesRegex(sl.Invalid, "chunks incomplete"):
            self.record(*self.batch())
        self.patch(review_cursor={"batch_id": "b1", "planned_chunks": ["a", "b"], "completed_chunks": ["a", "b"]})
        self.record(*self.batch())
        self.assertIsNone(sl.load_state(self.root)["review_cursor"])

    def test_stale_writer_cannot_overwrite_state(self):
        self.patch(cursor="review")
        with self.assertRaisesRegex(sl.Invalid, "Stale state revision"):
            sl.update(self.root, 0, patch={"cursor": "smoke"})
        self.assertEqual(sl.load_state(self.root)["cursor"], "review")

    def test_concurrent_writer_lock_is_not_stolen(self):
        lock = self.root / ".state.lock"
        lock.mkdir()
        with self.assertRaisesRegex(sl.Invalid, "writer already active"):
            self.patch(cursor="review")
        self.assertTrue(lock.exists())

    def test_budget_and_explicit_stop_survive_resume(self):
        mp, rp = self.batch()
        self.change_review(rp, cost_usd=100)
        self.record(mp, rp)
        self.assertEqual(sl.resume(self.root)["action"], "stop")
        self.patch(stop_reason="needs human baseline decision")
        self.assertEqual(sl.resume(self.root)["reason"], "needs human baseline decision")

    def test_scale_authorization_survives_fresh_load(self):
        plan = self.approved_plan()
        result = sl.scale_gate(self.root, plan, self.infra, framework=self.infra)
        self.assertTrue(result["pass"])
        self.assertFalse(result["command_executed"])

    def test_scale_without_approval_is_blocked(self):
        plan = self.approved_plan()
        self.patch(scale_approval=None)
        with self.assertRaisesRegex(sl.Invalid, "Scale approval missing"):
            sl.scale_gate(self.root, plan, self.infra, framework=self.infra)

    def test_changed_plan_invalidates_old_approval(self):
        plan = self.approved_plan()
        p = sl.read(plan)
        p["max_rows"] = 2000
        self.write(plan, p)
        with self.assertRaisesRegex(sl.Invalid, "Scale approval missing or stale"):
            sl.scale_gate(self.root, plan, self.infra, framework=self.infra)

    def test_dirty_generator_blocks_scale(self):
        plan = self.approved_plan()
        (self.infra / "generator.py").write_text("# changed\n")
        with self.assertRaisesRegex(sl.Invalid, "worktree is dirty"):
            sl.scale_gate(self.root, plan, self.infra, framework=self.infra)

    def test_changed_rubric_or_review_artifact_is_detected(self):
        self.record(*self.batch())
        (self.root / "b1/review.json").write_text("{}")
        with self.assertRaisesRegex(sl.Invalid, "Artifact changed"):
            sl.resume(self.root)

    def test_modified_raw_data_invalidates_evidence(self):
        mp, rp = self.batch()
        (self.root / "b1/data.json").write_text("[]")
        with self.assertRaisesRegex(sl.Invalid, "Artifact changed"):
            self.evaluate(mp, rp)

    def test_changed_rubric_cannot_replace_evaluation_pin(self):
        mp, rp = self.batch()
        candidate = self.write("candidate.json", {"relaxed": True})
        m = sl.read(mp)
        m["inputs"]["rubric"] = sl.reference(self.root, candidate)
        self.write(mp, m)
        self.change_review(rp, manifest_sha256=sl.digest(mp))
        with self.assertRaisesRegex(sl.Invalid, "rubric differs"):
            self.evaluate(mp, rp)

    def test_changed_contract_cannot_replace_approved_task(self):
        mp, rp = self.batch()
        m = sl.read(mp)
        m["inputs"]["contract"] = sl.reference(self.root, self.write("new-task.json", {"scope": "new"}))
        self.write(mp, m)
        self.change_review(rp, manifest_sha256=sl.digest(mp))
        with self.assertRaisesRegex(sl.Invalid, "contract differs"):
            self.evaluate(mp, rp)

    def test_reusing_raw_batch_with_new_id_and_seed_is_not_confirmation(self):
        self.record(*self.batch("b1", 1))
        mp, rp = self.batch("b2", 2)
        m = sl.read(mp)
        m["data"] = sl.reference(self.root, self.root / "b1/data.json")
        self.write(mp, m)
        self.change_review(rp, manifest_sha256=sl.digest(mp))
        self.record(mp, rp)
        self.assertEqual(sl.resume(self.root)["clean_pass_streak"], 1)

    def test_changed_generator_commit_blocks_scale(self):
        plan = self.approved_plan()
        self.git("commit", "--allow-empty", "-qm", "new version")
        with self.assertRaisesRegex(sl.Invalid, "Generator HEAD differs"):
            sl.scale_gate(self.root, plan, self.infra, framework=self.infra)

    def test_changed_framework_commit_blocks_scale(self):
        plan = self.approved_plan()
        framework = self.root / "framework"
        subprocess.check_call(["git", "clone", "-q", str(self.infra), str(framework)])
        subprocess.check_call(["git", "-C", str(framework), "-c", "user.name=Fixture",
                               "-c", "user.email=fixture@example.invalid", "commit", "--allow-empty", "-qm", "new framework"])
        with self.assertRaisesRegex(sl.Invalid, "Framework HEAD differs"):
            sl.scale_gate(self.root, plan, self.infra, framework=framework)

    def test_unratified_delta_blocks_even_with_plan_approval(self):
        plan = self.approved_plan()
        p = sl.read(plan)
        p["unratified_deltas"] = ["new capability"]
        self.write(plan, p)
        self.patch(scale_approval=self.approval(plan))
        with self.assertRaisesRegex(sl.Invalid, "Unratified design deltas"):
            sl.scale_gate(self.root, plan, self.infra, framework=self.infra)

    def test_history_cannot_be_replaced_by_state_patch(self):
        self.record(*self.batch())
        with self.assertRaisesRegex(sl.Invalid, "protected state fields"):
            self.patch(history=[])

    def test_cli_batch_failure_and_invalid_evidence_are_distinct(self):
        mp, rp = self.batch()
        self.change_review(rp, critical_findings=1)
        command = [sys.executable, str(ROOT / "tools/synthloop.py"), "check-batch", str(self.root),
                   "--manifest", str(mp), "--review", str(rp)]
        failed = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(failed.returncode, 1, failed.stderr)
        self.assertFalse(json.loads(failed.stdout)["pass"])
        self.write(rp, {})
        invalid = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(invalid.returncode, 2)
        self.assertIn("error", json.loads(invalid.stderr))

    def test_unknown_schema_and_nan_fail_closed(self):
        self.state["schema_version"] = 2
        self.write("state.json", self.state)
        with self.assertRaisesRegex(sl.Invalid, "schema_version"):
            sl.load_state(self.root)
        self.baseline["target"] = float("nan")
        with self.assertRaises(sl.Invalid):
            sl.baseline_check(self.baseline)

    def test_cli_success_and_blocked_gate_exit_codes(self):
        cmd = [sys.executable, str(ROOT / "tools/synthloop.py")]
        ok = subprocess.run(cmd + ["validate-state", str(self.root)], capture_output=True, text=True)
        self.assertEqual(ok.returncode, 0, ok.stderr)
        self.assertTrue(json.loads(ok.stdout)["valid"])
        self.patch(stop_reason="fixture stop")
        blocked = subprocess.run(cmd + ["resume", str(self.root)], capture_output=True, text=True)
        self.assertEqual(blocked.returncode, 1)
        self.assertEqual(json.loads(blocked.stdout)["action"], "stop")


if __name__ == "__main__":
    unittest.main()
