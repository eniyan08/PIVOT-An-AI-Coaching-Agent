---
description: Run one Pivot study cycle - picks the next coach in rotation, runs its quiz session, and logs the verdict. Designed to be driven by /loop.
---

State files:
- `.claude/pivot-state/rotation.json` - shape `{"sequence": [...coach names...], "index": N}`
- `.claude/pivot-state/verdicts.jsonl` - one JSON object per line, append-only

Do the following, with no manual confirmation needed from the user (this runs unattended under `/loop`):

1. Read `.claude/pivot-state/rotation.json`. Let `coach = sequence[index]`.
2. Dispatch to that subagent (matching its `name:` in `.claude/agents/<coach>.md`) to run one full coaching session: 2 quiz questions (ask, wait for the user's real answer, evaluate it), 1 hands-on task, and its JSON verdict as specified in its own agent definition.
   - If no one is present to answer quiz questions interactively (e.g. this is a fully unattended background run), have the coach note in `quiz_results` that the questions were asked but unanswered (`"correct": null, "notes": "unattended run - no answer given"`), still assign the hands-on task, and still return the JSON verdict shape.
3. Take the coach's returned JSON verdict, add a `"cycle_date"` field set to today's actual date, and append it as a single line to `.claude/pivot-state/verdicts.jsonl`.
4. Advance rotation: `index = (index + 1) % len(sequence)`. Write the updated `{"sequence": ..., "index": ...}` back to `.claude/pivot-state/rotation.json`.
5. Report back in one short sentence: which coach ran and a one-line summary of the verdict (e.g. "k8s-coach: 1/2 correct, hands-on task assigned, weak spot logged: NetworkPolicies").
