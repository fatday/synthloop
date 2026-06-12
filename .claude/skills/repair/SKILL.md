---
name: repair
description: Diagnose-then-patch the confirmed findings from the latest review of a generator project, with ratchet tests and gate-impact checks. Usage - /repair <generator-name>
---

# /repair <generator-name>

1. Read the latest review summary, `data_projects/<name>/project_memory.md`
   (known traps), and `playbook/03_quality_loop.md` section 3.4.
2. For each confirmed finding, **write the diagnosis before touching code**:
   the mechanism traced to root cause, reproduced offline (use the project's
   replay twins/fixtures). If you cannot reproduce or explain it, say so and
   investigate further - do not patch blind.
3. Apply the scope rule:
   - Prompts, steering lines, thresholds, keyword lists, sampling weights:
     patch directly.
   - Anything in code (parsers, scoring, schema rendering, state machines):
     minimal fix + a NEW test that would have caught the bug. Run the
     project's test suite.
4. **Ratchet**: every confirmed finding gets a permanent guard (test,
   validation, counter alert), even the prompt-level ones where feasible.
5. **Gate-impact check**: if the repair adds or tightens any accept/reject
   gate, measure accept-rate before vs after on the same batch and inspect a
   sample of newly-rejected rows. A gate that rejects mostly-good rows gets
   reworked, not shipped.
6. If reviewer behavior should change, write
   `review_instructions/v<n+1>.md` with a changelog line.
7. Record each diagnosis + change in `project_memory.md` (one paragraph). If
   a lesson generalizes, ALSO update `playbook/` in the same change.
8. Update `progress.md` next action to re-run `/smoke` (the loop continues
   until two consecutive passing cycles).
