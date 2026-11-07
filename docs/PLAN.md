# DealerDesk: living plan

Budget: about 6-8 h in total. Each phase ends with a review and waits for approval before the next one starts.

## Phase status

| Phase | Scope | Est. | Status |
|---|---|---|---|
| 0 | Verify workspace (no spec) | 15 min | done |
| 1 | Discovery: CODEMAP, specs/README, minimal CLAUDE.md (no spec) | 45 min | done, awaiting review |
| 2 | Spec 001: Makefile, .gitignore/.gitattributes, CI build (gcc + clang) | 45 min | done, awaiting review |
| 3 | Spec 002: golden-master harness, `make test`, ASan in CI | 1 h 45 | not started |
| 4 | Spec 003: agent setup (settings, hook, slash commands, reviewer subagent) | 45 min | not started |
| 5 | Spec 004: TICKET-142, three gates | 2 h 15 | not started |
| 6 | NOTES.md, `make demo`, traceability table, walkthrough dry run | 45 min | not started |

Cut order if time runs short: differential test, then `/spec` polish, then the ASan CI job (keep the gcc/clang job).

## Spec index

| Spec | Title | Review mode | Status |
|---|---|---|---|
| 001 | build-ci | bundled | implemented (verify pending) |
| 002 | characterisation-harness | bundled | not drafted |
| 003 | agent-setup | bundled | not drafted |
| 004 | fleet-discount (TICKET-142) | 3 gates | not drafted |

Status values: draft, approved, implemented, verified.

## Plan change log

| Date | Change | Reason |
|---|---|---|
| 2026-11-07 | Initial plan approved. CI moved into spec 001 (was a separate phase 3). | A green check on every later commit is worth 30 min early. |
