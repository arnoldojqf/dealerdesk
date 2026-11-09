# Spec 001: build and CI: tasks

**Status:** verified (2026-11-09, `/verify 001`, report in `verify-report.md`). Each task is its own commit, message `spec 001 Tn: ...`. The proving test for most criteria is a CI step (see design), run locally first with the same command.

- [x] **T1.** Add `.gitignore` and `.gitattributes`. Serves R8, R9.
  Proof: `make`-free check locally: `git add --renormalize . && git diff --cached --quiet`; later the CI renormalize step.
- [x] **T2.** Add `Makefile` with `all`, `warn`, `asan`, `test`, `clean`. Serves R1-R5, R7.
  Proof locally: `make && gcc -o /tmp/raw *.c -lm && cmp dealerdesk /tmp/raw`; `make warn asan test clean`; `git status --porcelain` empty.
- [x] **T3.** Add `.github/workflows/ci.yml` with the eight steps, each named with its R-IDs. Serves R6, R10 (and runs the proofs for R1-R5, R7-R9 on gcc and clang).
  Proof: green run for both matrix jobs on `origin/master`. Push needs your OK.
- [x] **T4.** Fix the README BUILD command line. Serves R11.
  Proof: `git diff -- README.md` shows exactly one changed line.
- [x] **T5.** Update `docs/PLAN.md` (spec index 001 to implemented), run `/verify`-equivalent check by hand (the fresh-context reviewer subagent arrives in spec 003), record anything caught in `docs/agent-log.md`.

- [x] **T6.** Strengthen the CI checks that `/verify 001` found weaker than their criteria (R2, R3, R5, R7) and prefix every CI step name with its spec. Serves R2, R3, R5, R7.
  Proof locally: the commands in the new steps pass on `make warn`, `make asan`, `make clean`; `nm` finds no `__asan_init` or `__ubsan_handle` in the plain `dealerdesk` (0), so the R3 check can fail. CI run after the push.

## Traceability

| Criterion | Proving test | Status |
|---|---|---|
| R1 | CI step "001 R1 binary identical to the brief's command"; local `cmp` | pass |
| R2 | CI step "001 R2 warnings build": greps the echoed command for `-Wall -Wextra`; make's exit status 0 | pass (T6) |
| R3 | CI step "001 R3 sanitizer build": `nm dealerdesk-asan` has `__asan_init` and `__ubsan_handle` | pass (T6) |
| R4 | superseded by spec 002 T1; `make test` is now covered by spec 002 R15/R16 (CI steps "002 R15, R16 ...") | superseded |
| R5 | CI step "001 R5 clean removes the binaries and nothing else": no `dealerdesk*` left and `git status --porcelain` empty (a deleted tracked file, such as under `data/`, would fail it) | pass (T6) |
| R6 | CI matrix `clang` job: green in runs 42415644246 (659d345), 42626459810 (8113a38) and 42629508463 (324040e, first run with the T6 steps), checked with `gh run view` / `gh run list` on 2026-11-09. Clang is not installed locally (D10) | pass |
| R7 | CI step "001 R7, R8 tree is clean after building and after clean": status empty after make, warn, asan, and again after `make clean` | pass (T6) |
| R8 | same step as R7 | pass |
| R9 | CI step "001 R9 line endings: renormalize changes nothing" | pass |
| R10 | CI run 42415644246 on 659d345: gcc and clang jobs green (rechecked 2026-11-09 with `gh run view`; run 42626459810 on 8113a38 also green). The `test-selfcheck` step runs on gcc only; that is spec 002's step, not an R10 requirement | pass |
| R11 | manual: `git diff baseline HEAD -- README.md` changes exactly one line, the BUILD command (checked 2026-11-09). Kept manual: it was a one-time edit, and an automated check would need `fetch-depth: 0` in CI to reach the `baseline` tag for one line | pass (manual) |

## Change log
- 2026-11-09: T6 added after the first `/verify 001` run (static only, its Bash was denied). Reason: R2, R3, R5 and R7 were marked pass on CI steps that checked less than the criterion states. All CI step names now start with their spec number, because "R9" named both this spec's line-ending step and spec 003's agent-setup step. Spec 003's table keeps the old step name for run 42421288067, which is what that run showed.
- 2026-11-09: R4 row set to "superseded" (see requirements.md change log); R10 and R11 rows now state their evidence and why R11 stays manual. `git diff baseline c1143ff -- '*.c' '*.h' data` is empty (spec 001 changed no C or data). The extra `.claude/settings.local.json` line in `.gitignore` comes from spec 003 T2, not this spec.
- 2026-11-09: `/verify 001` rerun with commands actually run (47 passed twice, selfcheck ok, `cmp` identical). No criterion failed. Fixes from its findings: R1 row uses the current step name; R6 row cites the run IDs; requirements.md R7, R10 and A3 reworded (see its change log). Status set to verified.
- 2026-11-09: the CI file has also changed since T3 for later specs (golden tests, selfcheck, `check-agent`; steps and order differ from design.md). Recorded in design.md.
