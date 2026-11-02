# Workspace hygiene

**Purpose**: keep the workspace under its quota and readable for the next agent.
Every artifact a run creates has an owner, a place and a deletion trigger. The
home directory is not scratch space.

## Where things go

- [ ] **Job temp and scratch** goes in a job-scoped directory: node-local temp
      when the job allows it, otherwise one subdirectory per job under the
      workspace's scratch root (recorded in `data_projects/ENVIRONMENT.md`).
      Point every tool's temp setting there (`TMPDIR`, framework caches, a test
      runner's `--basetemp`). The job removes it, or the next audit does once the
      job has ended. A test run never writes to the home root.
- [ ] **Worktrees and repo copies** live under one parent per repo (e.g.
      `<repo>-worktrees/<round>-<purpose>`), never as siblings in the home root.
      `progress.md` lists each one with its branch and purpose. A worktree is
      removed when its round is merged or abandoned (removal steps below).
- [ ] **Data**: a smoke batch stays while a review or decision cites it (the
      batch ledger names the reference batches). Raw scale output stays until the
      release is verified. Local export copies go once the published copy is
      verified and its rollback revision is recorded in `progress.md`.
- [ ] **Caches** (model hubs, package managers, container layers) are
      regenerable: prune them by last access, not wholesale, while jobs run. A
      package-cache clean can block on a lock held by running jobs; wait for
      them rather than forcing it.

## Audit (at every stage exit, and whenever usage nears the quota)

1. **Measure on a compute node.** `du` over millions of small files is slow and
   stalls a shared login node. Run one `du` per top-level directory in parallel,
   write the output to shared storage (a compute node's `/tmp` is not visible
   from the login node), and count allocated blocks (what the quota counts), not
   apparent size.
2. **Classify every large item**:
   - regenerable: caches, temp of finished jobs;
   - duplicate: a published or archived copy exists and was verified;
   - finished: worktrees and scratch of closed rounds;
   - live: anything a running or pending job references (check each job's
     command, working directory and output paths in the scheduler);
   - someone else's: another session's or user's workspace.
   Never delete live or someone else's items; list them for their owner.
3. **Present** size, last-modified date, owner and a recommendation per group.
   Delete only the groups the human approves.
4. **Save before removing a worktree**:
   - uncommitted changes and untracked files go to a stash or a WIP commit on
     its branch;
   - a detached HEAD that no branch contains gets an archive branch;
   - a submodule must be clean, with its commit pushed, before a forced removal.
   A cleanup never deletes branches.
5. **Delete exact lists, never patterns typed at delete time.** Write each
   group's paths to a file, check every path against the prefix that group may
   touch, delete in a scheduled job, and log every path. Directories made
   read-only (published outputs, some test fixtures) need write permission
   restored first.
6. **Verify**: every target is gone, the totals are recomputed, and the audit's
   own temporary files are removed.

## Exit criteria

- Usage is below the quota with headroom.
- No worktree, temp directory or data copy exists without an owner and a reason
  in `progress.md`.

## Common failure modes

- A test runner pointed at the home directory: one folder per run.
- A worktree per experiment round and none removed: many repo copies, each with
  unsaved work at risk.
- Keeping a local export "just in case" next to its published copy. The
  published revision history is the rollback; record the revision instead.
- Measuring on the login node, or writing measurement output to a compute
  node's `/tmp`.
- Reading an empty job log as a stuck job. A log piped through a filter is
  block-buffered (use a line-buffered filter); check the job's CPU and I/O
  counters before cancelling it.
