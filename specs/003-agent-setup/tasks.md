# Spec 003: agent setup: tasks

**Status:** approved. Each task is its own commit, message `spec 003 Tn: ...`. No product files change. The check script is written first and fails until the files exist.

- [ ] **T1.** Write `scripts/check-agent-setup.py` and `make check-agent`, with the checks for R1-R9. Run it: it must fail on every missing file (tests first). Serves R9.
- [ ] **T2.** `.claude/settings.json` (allow, ask, deny, hook wiring), `.claude/hooks/rebuild-on-c-edit.sh`, `.gitignore` line. Serves R2-R6.
  Proof: the settings and hook checks pass; the hook gives exit 2 on a deliberate error and exit 0 on clean code, in a temp copy.
- [ ] **T3.** `.claude/agents/spec-reviewer.md` and `.claude/commands/{spec,implement,verify}.md`. Serves R7, R8.
  Proof: file and front-matter checks pass.
- [ ] **T4.** Rewrite `CLAUDE.md`: commands, layout, code-map summary, spec workflow, hard rules (including the A2 caveat and "explain C diffs before committing"). Serves R1.
  Proof: the R1 check passes.
- [ ] **T5.** CI step running `make check-agent`. Serves R9.
  Proof: green run (push needs your OK).
- [ ] **T6.** Live proofs, each shown to the owner: (a) attempt `git push --dry-run origin master` through the tool and show it blocked; (b) attempt an Edit of a file under `tests/golden/` and show it blocked; (c) create a scratch `.c` file with a deliberate error, show the hook's feedback, delete it; (d) show that `python3 tests/golden.py --update` asks. Serves R3, R4, R6 (A7).
- [ ] **T7.** Run `/verify 002` (or the A6 fallback). Commit its report to `specs/002-characterisation-harness/verify-report.md`. Fix or record each gap. Serves R10.
- [ ] **T8.** Close out: traceability, statuses, `docs/PLAN.md`, `docs/agent-log.md`; check `git diff baseline -- '*.c' '*.h' data` is empty. Serves R11.

## Traceability

| Criterion | Proving test | Status |
|---|---|---|
| R1 | `check-agent-setup.py` (targets and paths in CLAUDE.md exist) | todo |
| R2 | `check-agent-setup.py` (settings.json shape) | todo |
| R3 | `check-agent-setup.py` (deny rules present); manual T6 a, b | todo |
| R4 | `check-agent-setup.py` (ask rules present); manual T6 d | todo |
| R5 | `check-agent-setup.py` (allow rules present) | todo |
| R6 | `check-agent-setup.py` (hook run against clean, broken and non-C input); manual T6 c | todo |
| R7 | `check-agent-setup.py` (files and front matter); behaviour manual: used on spec 004 | todo |
| R8 | `check-agent-setup.py`; behaviour manual: T7 | todo |
| R9 | CI run with the `make check-agent` step | todo |
| R10 | `specs/002-characterisation-harness/verify-report.md` committed | todo |
| R11 | `git diff baseline -- '*.c' '*.h' data` empty | todo |

## Change log
(none yet)
