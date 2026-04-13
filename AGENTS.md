# AGENTS.md

Instructions for AI agents (Codex, Claude Code) working on this repository.

This is a recruitment task for the **AI Data Engineer** position at Telemedi.
One deliverable is a log showing how AI was used during the task.

## Logging

Log every work session to `logs/sessions/YYYY-MM-DD_<slug>.md` using the
`workflow-logger` skill. One session = one feature branch = one PR. The
session file is created at the start of the session and updated live so
the branch is always ready for `gh pr create`.

See `.agents/skills/workflow-logger/SKILL.md` for details.

## Skill discovery

The skill lives at `.agents/skills/workflow-logger/` (Codex). A symlink at
`.claude/skills/workflow-logger` points to the same directory so Claude Code
finds it too. Edit only the physical file under `.agents/`.
