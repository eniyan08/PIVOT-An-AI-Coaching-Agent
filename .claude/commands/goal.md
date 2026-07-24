---
argument-hint: [status|set] [date]
description: Track the standing CKA exam deadline (or other goal date). Usage: /goal status, /goal set <YYYY-MM-DD>
allowed-tools: Read, Write, Bash
---

State file: `.claude/pivot-state/goal.json` (shape: `{"label": "...", "target_date": "YYYY-MM-DD"}`).

Arguments given: $ARGUMENTS (subcommand: $0, date if any: $1)

Behavior:

- If $0 is "status" (or no arguments given):
  1. Read `.claude/pivot-state/goal.json`.
  2. Compute days remaining from today's actual date to `target_date`.
  3. Read `.claude/pivot-state/verdicts.jsonl` if it exists and is non-empty; look at the most recent entries for `"coach": "k8s-coach"` and summarize whether recent quiz results look on-track (mostly correct) or concerning (repeated misses / weak spots piling up), in one or two sentences. If the file is empty or has no k8s-coach entries yet, just say there's no session history yet.
  4. Report: the label, the target date, days remaining, and the on-track read. Keep it to a short paragraph, not a report.

- If $0 is "set" and $1 is a date (YYYY-MM-DD):
  1. Overwrite `.claude/pivot-state/goal.json` with `{"label": <existing label or "CKA" if none>, "target_date": "$1"}`.
  2. Confirm the new date back to the user in one sentence.

- If arguments don't match either form, explain the correct usage (`/goal status` or `/goal set <YYYY-MM-DD>`) and stop.
