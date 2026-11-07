---
description: Implement an approved spec task by task, tests first, one commit per task
argument-hint: <spec number or folder name>
---

Implement the spec `$ARGUMENTS` (a folder under `specs/`). Rules are in
`specs/README.md` and `CLAUDE.md`; read both first.

1. Read the spec's three files. If the status of `requirements.md`, `design.md`
   or `tasks.md` is not `approved`, STOP and say so. No code without an approved spec.
2. Work through `tasks.md` in order, one task at a time:
   a. Write or update the test first and run it to see it fail for the right reason.
   b. Make the smallest change that satisfies the task. Do not reformat or restyle
      code you are not otherwise changing. Preserve existing behaviour, bugs included.
   c. Run `make test`; for C changes also `make warn` and `make test-asan`. Show the output.
   d. If the task changes C, explain the diff to the owner line by line (they are
      new to C) BEFORE committing, and wait for them to acknowledge.
   e. Commit with the message `spec NNN Tn: <what and why>`, citing the criteria
      (R-IDs). A golden may be updated only for an intended behaviour change: name
      the criterion in the commit message, and run `--update` only for that scenario.
   f. Tick the task in `tasks.md` and update the traceability table.
3. If implementing shows the spec is wrong or incomplete, STOP. Fix the spec, add a
   Change log line with the date and the reason, tell the owner, then continue.
   Never let code and spec drift apart silently.
4. Never push, force-push, change remotes or open pull requests; ask the owner.
5. At the end, report: commits made, criterion-by-criterion test results, spec
   changes, and mistakes caught (add them to `docs/agent-log.md`).
