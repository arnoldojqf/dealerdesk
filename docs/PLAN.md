# DealerDesk: living plan

Budget: about 6-8 h in total. Each phase ends with a review and waits for approval before the next one starts.

## Phase status

| Phase | Scope | Est. | Status |
|---|---|---|---|
| 0 | Verify workspace (no spec) | 15 min | done |
| 1 | Discovery: CODEMAP, specs/README, minimal CLAUDE.md (no spec) | 45 min | done |
| 2 | Spec 001: Makefile, .gitignore/.gitattributes, CI build (gcc + clang) | 45 min | done |
| 3 | Spec 002: golden-master harness, `make test`, ASan in CI | 1 h 45 | done |
| 4 | Spec 003: agent setup (settings, hook, slash commands, reviewer subagent) | 45 min | built; live proofs pending a new session |
| 5 | Spec 004: TICKET-142, three gates | 2 h 15 | in progress (tasks gate) |
| 6 | NOTES.md, `make demo`, traceability table, walkthrough dry run | 45 min | not started |

Cut order if time runs short: differential test, then `/spec` polish, then the ASan CI job (keep the gcc/clang job).

## Spec index

| Spec | Title | Review mode | Status |
|---|---|---|---|
| 001 | build-ci | bundled | implemented (verify pending) |
| 002 | characterisation-harness | bundled | implemented (verify pending) |
| 003 | agent-setup | bundled | implemented, open items (T6 c and d live proofs; CI run done) |
| 004 | fleet-discount (TICKET-142) | 3 gates | requirements and design approved (gates 1-2), tasks pending |

Status values: draft, approved, implemented, verified.

## Plan change log

| Date | Change | Reason |
|---|---|---|
| 2026-11-07 | Initial plan approved. CI moved into spec 001 (was a separate phase 3). | A green check on every later commit is worth 30 min early. |
| 2026-11-07 | Added a step at the start of the next session: spec 003 T6 live proofs (deny rules, ask rules, build hook), before Phase 5 starts. Spec 002 got T10 after `/verify 002`. | Settings and hooks written mid-session were not enforced in that session. The review found manual-only "pass" marks. |
| 2026-11-07 | Spec 003 T6 partly done: deny rules proven live (a, b). Hook (c) and ask rule (d) still open, to be run in an interactive session from the repo root. Allow rule for the harness narrowed so `--update` is not allowed by prefix. | The hook builds `$CLAUDE_PROJECT_DIR`, so it cannot be shown from a background worktree. `--update` ran without a prompt. |
