# DealerDesk: living plan

Budget: about 6-8 h in total. Each phase ends with a review and waits for approval before the next one starts.

## Phase status

| Phase | Scope | Est. | Status |
|---|---|---|---|
| 0 | Verify workspace (no spec) | 15 min | done |
| 1 | Discovery: CODEMAP, specs/README, minimal CLAUDE.md (no spec) | 45 min | done |
| 2 | Spec 001: Makefile, .gitignore/.gitattributes, CI build (gcc + clang) | 45 min | done |
| 3 | Spec 002: golden-master harness, `make test`, ASan in CI | 1 h 45 | done |
| 4 | Spec 003: agent setup (settings, hook, slash commands, reviewer subagent) | 45 min | done; live proofs a-d and T6e (Write blocked by the Edit rules) shown; verified 2026-11-09; ask rule reported working in a plain session 2026-11-09 (owner report) |
| 5 | Spec 004: TICKET-142, three gates | 2 h 15 | spec 004 done: implemented, verified, pushed, CI green on gcc and clang |
| 6 | NOTES.md, `make demo`, traceability table, walkthrough dry run | 45 min | done: `make demo` (D13), NOTES.md (856 words, ticket table inside), dry run from a fresh clone passed |

Cut order if time runs short: differential test, then `/spec` polish, then the ASan CI job (keep the gcc/clang job).

## Spec index

| Spec | Title | Review mode | Status |
|---|---|---|---|
| 001 | build-ci | bundled | verified 2026-11-09 (`/verify 001`, report in `specs/001-build-ci/verify-report.md`, T6 fixes done) |
| 002 | characterisation-harness | bundled | verified 2026-11-07 (`/verify 002`, report in `specs/002-characterisation-harness/verify-report.md`, T10 fixes done) |
| 003 | agent-setup | bundled | verified 2026-11-09 (`/verify 003`, report in `specs/003-agent-setup/verify-report.md`, T9 fixes done) |
| 004 | fleet-discount (TICKET-142) | 3 gates | verified (T1-T8, `/verify 004` done); pushed, CI green on gcc and clang |

Status values: draft, approved, implemented, verified.

## Plan change log

| Date | Change | Reason |
|---|---|---|
| 2026-11-07 | Initial plan approved. CI moved into spec 001 (was a separate phase 3). | A green check on every later commit is worth 30 min early. |
| 2026-11-07 | Added a step at the start of the next session: spec 003 T6 live proofs (deny rules, ask rules, build hook), before Phase 5 starts. Spec 002 got T10 after `/verify 002`. | Settings and hooks written mid-session were not enforced in that session. The review found manual-only "pass" marks. |
| 2026-11-07 | Spec 003 T6 partly done: deny rules proven live (a, b). Hook (c) and ask rule (d) still open, to be run in an interactive session from the repo root. Allow rule for the harness narrowed so `--update` is not allowed by prefix. | The hook builds `$CLAUDE_PROJECT_DIR`, so it cannot be shown from a background worktree. `--update` ran without a prompt. |
| 2026-11-07 | Spec 003 T6: (c) hook shown live from the main checkout and a worktree. (d) failed: `--update` ran with no prompt under `defaultMode: auto`. | Rerun (d) with `claude --permission-mode default`; meanwhile review `git diff tests/golden` before every commit. |
| 2026-11-08 | Spec 003 T6 (d) shown live in default mode; T6 closed. Project settings now set `defaultMode: default`; CLAUDE.md corrected and the `make CC=` gap recorded. | The 2026-11-07 failure was `defaultMode: auto` skipping the ask rule. Confirm the new setting in a later session without `--permission-mode`. |
| 2026-11-08 | Spec 004 gate 3 passed and T1-T6 implemented, one commit per task. | Tasks reviewed against the code and fixtures first; four small edits made to `tasks.md`. |
| 2026-11-08 | `/verify 004` run; T8 added (`fleet_sell_then_sell`), report saved. | The review found no failing criterion; one test gap (a stored fleet invoice saved again) and wording on R13, R11, R14. |
| 2026-11-08 | Spec 004 pushed to `origin/master`; CI run 42522889926 green on gcc and clang (47 tests each, plain and ASan/UBSan). | Closes the clang item (D10). |
| 2026-11-08 | Spec index: 002 set to verified (its `/verify` report and fixes exist); 001 reworded to say it was checked by hand only. | The rows still said "verify pending" after the 002 review had been run and fixed. 001 has no independent review, so it is not marked verified. |
| 2026-11-09 | Spec 003: dead `Write(...)` deny rules removed from the spec and checker; T6e (live Write proof) added. | Claude Code 2.1.319 warns that `Write(path)` rules never match; `Edit(path)` covers all file-editing tools. |
| 2026-11-09 | Spec 003 status line and R7 row updated (T6 and T6e closed; commands used on spec 004). Ask-rule follow-up not closed: a background session ran `golden.py --update cust_list` through the Bash tool with no visible denial and no diff, but the agent cannot see whether a prompt appeared or which permission mode applies. | Needs the owner to run it once in an interactive session started without `--permission-mode` and report whether a prompt shows. |
| 2026-11-09 | Phase 6 done. Dry run from a fresh local clone of `1db9663`: `make`, `make warn`, `make test`, `make test-asan`, `make test-selfcheck`, `make check-agent`, `make demo` all exit 0 (47 passed twice). CI for `8629e92` green on gcc and clang. | Remaining open items are in NOTES.md "What I would do next". |
| 2026-11-09 | Ask-rule follow-up closed. In a session started without `--permission-mode`, `python3 tests/golden.py --update cust_list` showed a permission prompt (reported by the owner, who approved it); `git status` stayed clean (identical bytes). `/verify 001` first run was static only (reviewer's Bash refused); spec 001 got T6 (stronger CI checks for R2, R3, R5, R7), its change logs and traceability rows were corrected, and the reviewer prompt now says to run commands one at a time. Spec 001 stays "implemented" until a rerun that really runs them. | The `defaultMode: default` setting works as intended. Update: the `/verify 001` rerun ran its commands (47 passed twice, selfcheck ok, `cmp` identical) and found no failing criterion, so spec 001 is now verified; CI run 42629508463 on 324040e green on gcc and clang. The agent could not see the prompt itself, so this rests on the owner's report. |
| 2026-11-09 | `/verify 003` run (its commands ran: `make test` 47 passed, `make check-agent` 17 ok); no criterion failed. T9: `defaultMode` check added to `scripts/check-agent-setup.py`, rows R2, R4, R7, R8, R11 and the design corrected, spec 003 set to verified (its status lines still said "implemented with open items"). Clang `make warn` read from the CI log of run 42631838729: no warnings, so spec 001 A3 now covers both compilers. | The reviewer found the setting that makes the ask rules work (`defaultMode: default`) could be reverted without any check failing, and several rows claiming more than their evidence. |
