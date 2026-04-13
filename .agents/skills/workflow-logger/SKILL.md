---
name: workflow-logger
description: Log work session actions to a markdown file in logs/sessions/. Use at session start to create the file, and after any non-trivial step to append what was done. Keeps a live per-session log that is always ready to commit and ship with a PR.
---

# Workflow Logger

Log what happens during a work session to `logs/sessions/YYYY-MM-DD_<slug>.md`.
One session = one feature branch = one PR. The file grows live and is always
in a state ready to commit.

## At session start

Create `logs/sessions/YYYY-MM-DD_<slug>.md` where `<slug>` is a kebab-case
name matching the feature branch (ask the user if unclear). Add a header
with the session goal in one line. Commit the new file.

## During the session

After any non-trivial step, append a bullet with local time and a short
description of what was done. Example:

```
- [14:32] Loaded visits.csv, verified FK integrity against patients.csv.
- [14:51] Rejected Great Expectations in favor of Pandera — too heavy for scope.
```

Bullets are operational facts, not essays. One line each.

## Do not

- Do not batch-write at the end of the session. Append live.
- Do not run `gh pr create`. Opening the PR is the user's action.