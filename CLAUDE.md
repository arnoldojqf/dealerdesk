# DealerDesk: agent instructions (minimal; grows in later phases)

Menu-driven C app for dealerships, in production for years. The job: make changes safe, then ship TICKET-142 (fleet discount). Code is the truth; README and help text are wrong in places (see `docs/CODEMAP.md`, B1-B9).

## Commands
- Build: `gcc -o dealerdesk *.c -lm`, run from the repo root with `./dealerdesk`
- Reset sample data: `git checkout -- data`
- Remotes: `origin` is mine (public). `upstream` is the original and is read-only.

## Hard rules
1. No code without an approved spec in `specs/` (see `specs/README.md`). Read-only discovery is fine.
2. Preserve existing behaviour exactly, bugs included. Record bugs in `docs/CODEMAP.md`; fix only if the owner agrees.
3. Never write to the real `data/`. Tests use temp copies. `git status` must stay free of data changes.
4. Keep C changes minimal. Do not reformat code you are not otherwise changing.
5. Before any commit that changes C, explain the diff line by line to the owner (they are new to C).
6. Never push, force-push, change remotes or open pull requests without asking. Never open a PR against upstream.
7. Commit small, tests passing, message cites spec and task (`spec 004 T3: ...`).
8. Verify before claiming: run the build or test and show the output.
9. Log agent or human mistakes in `docs/agent-log.md` when caught.

## Where things are
- Plan and status: `docs/PLAN.md`. Decisions: `docs/DECISIONS.md`. Code map: `docs/CODEMAP.md`.
