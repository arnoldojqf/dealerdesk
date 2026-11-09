# Spec 001: build and CI: tasks

**Status:** implemented. Each task is its own commit, message `spec 001 Tn: ...`. The proving test for most criteria is a CI step (see design), run locally first with the same command.

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
| R1 | CI step "R1 byte-identical"; local `cmp` | pass |
| R2 | CI step "001 R2 warnings build": greps the echoed command for `-Wall -Wextra`; make's exit status 0 | pass (T6) |
| R3 | CI step "001 R3 sanitizer build": `nm dealerdesk-asan` has `__asan_init` and `__ubsan_handle` | pass (T6) |
| R4 | CI step "R4 test placeholder" | pass |
| R5 | CI step "001 R5 clean removes the binaries and nothing else": no `dealerdesk*` left and `git status --porcelain` empty (a deleted tracked file, such as under `data/`, would fail it) | pass (T6) |
| R6 | CI matrix `clang` job | pass |
| R7 | CI step "001 R7, R8 tree is clean after building and after clean": status empty after make, warn, asan, and again after `make clean` | pass (T6) |
| R8 | same step as R7 | pass |
| R9 | CI step "001 R9 line endings: renormalize changes nothing" | pass |
| R10 | CI run 42415644246 on 659d345: gcc and clang jobs green | pass |
| R11 | manual: `git diff -- README.md` is one line (no automated test; stated honestly) | pass (manual) |

## Change log
- 2026-11-09: T6 added after the first `/verify 001` run (static only, its Bash was denied). Reason: R2, R3, R5 and R7 were marked pass on CI steps that checked less than the criterion states. All CI step names now start with their spec number, because "R9" named both this spec's line-ending step and spec 003's agent-setup step. Spec 003's table keeps the old step name for run 42421288067, which is what that run showed.
- 2026-11-09: the CI file has also changed since T3 for later specs (golden tests, selfcheck, `check-agent`; steps and order differ from design.md). Recorded in design.md.
