# Spec 003: agent setup: tasks

**Status:** implemented with open items (T6, R9 CI run, live behaviour of the commands; see traceability). Each task is its own commit, message `spec 003 Tn: ...`. No product files change. The check script is written first and fails until the files exist.

- [x] **T1.** Write `scripts/check-agent-setup.py` and `make check-agent`, with the checks for R1-R9. Run it: it must fail on every missing file (tests first). Serves R9.
- [x] **T2.** `.claude/settings.json` (allow, ask, deny, hook wiring), `.claude/hooks/rebuild-on-c-edit.sh`, `.gitignore` line. Serves R2-R6.
  Proof: the settings and hook checks pass; the hook gives exit 2 on a deliberate error and exit 0 on clean code, in a temp copy.
- [x] **T3.** `.claude/agents/spec-reviewer.md` and `.claude/commands/{spec,implement,verify}.md`. Serves R7, R8.
  Proof: file and front-matter checks pass.
- [x] **T4.** Rewrite `CLAUDE.md`: commands, layout, code-map summary, spec workflow, hard rules (including the A2 caveat and "explain C diffs before committing"). Serves R1.
  Proof: the R1 check passes.
- [x] **T5.** CI step running `make check-agent`. Serves R9.
  Proof: green run (push needs your OK).
- [ ] **T6.** (BLOCKED until a new session, see change log.) Live proofs, each shown to the owner: (a) attempt `git push --dry-run origin master` through the tool and show it blocked; (b) attempt an Edit of a file under `tests/golden/` and show it blocked; (c) create a scratch `.c` file with a deliberate error, show the hook's feedback, delete it; (d) show that `python3 tests/golden.py --update` asks. Serves R3, R4, R6 (A7).
- [x] **T7.** Run `/verify 002` (or the A6 fallback). Commit its report to `specs/002-characterisation-harness/verify-report.md`. Fix or record each gap. Serves R10.
- [x] **T8.** Close out: traceability, statuses, `docs/PLAN.md`, `docs/agent-log.md`; check `git diff baseline -- '*.c' '*.h' data` is empty. Serves R11.

## Traceability

| Criterion | Proving test | Status |
|---|---|---|
| R1 | `make check-agent` (targets and paths in CLAUDE.md exist; shown to fail on a bogus target and path) | pass |
| R2 | `make check-agent` (settings.json shape and hook wiring) | pass |
| R3 | `make check-agent` (all deny rules present) | rules present: pass. **Enforcement: pending** (T6 needs a new session; a `git push --dry-run` was not blocked in the writing session) |
| R4 | `make check-agent` (all ask rules present) | rules present: pass. **Enforcement: pending** (T6 d) |
| R5 | `make check-agent` (all allow rules present) | pass |
| R6 | `make check-agent` runs the hook on clean, broken, warning and non-C input in a temp copy | script behaviour: pass. **Live firing: pending** (no feedback seen in the writing session) |
| R7 | `make check-agent` (files, description, argument-hint) | form: pass. **Behaviour: manual, pending** (used for the first time on spec 004) |
| R8 | `make check-agent` (front matter, read-only tool list); reviewer run in T7 | form: pass. Behaviour: partly (T7 used the A6 fallback because the agent type was not loaded) |
| R9 | CI run with the `make check-agent` step | **pending the push** |
| R10 | `specs/002-characterisation-harness/verify-report.md` | pass (report committed, every finding has a disposition) |
| R11 | `git diff baseline -- *.c *.h data` empty | pass |

## Change log
- 2026-11-07: T6 live proofs could not be completed in the session that wrote the settings. A `git push --dry-run origin master` was **not** blocked and a deliberately broken scratch `.c` file produced **no hook feedback**, although `.claude/settings.json` contained the deny rule and the hook. Most likely cause: Claude Code reads settings and hooks when a session starts, so mid-session edits are not applied (not verified from inside the session). Nothing was pushed (`origin/master` stayed at 82d74b5; the command was a dry run) and the scratch file was deleted. What is proven now: the hook script's behaviour (R6) by `make check-agent`, and the rule text (R3-R5). What is not: that the permission engine enforces the rules. T6 is moved to the first action of the next session; R3, R4 and R6 stay "pending" in the table until then. The edit of `tests/golden/` was deliberately not attempted, since an unenforced deny rule would have modified a golden.
