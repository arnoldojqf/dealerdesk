# Spec 001: build and CI: tasks

**Status:** approved. Each task is its own commit, message `spec 001 Tn: ...`. The proving test for most criteria is a CI step (see design), run locally first with the same command.

- [ ] **T1.** Add `.gitignore` and `.gitattributes`. Serves R8, R9.
  Proof: `make`-free check locally: `git add --renormalize . && git diff --cached --quiet`; later the CI renormalize step.
- [ ] **T2.** Add `Makefile` with `all`, `warn`, `asan`, `test`, `clean`. Serves R1-R5, R7.
  Proof locally: `make && gcc -o /tmp/raw *.c -lm && cmp dealerdesk /tmp/raw`; `make warn asan test clean`; `git status --porcelain` empty.
- [ ] **T3.** Add `.github/workflows/ci.yml` with the eight steps, each named with its R-IDs. Serves R6, R10 (and runs the proofs for R1-R5, R7-R9 on gcc and clang).
  Proof: green run for both matrix jobs on `origin/master`. Push needs your OK.
- [ ] **T4.** Fix the README BUILD command line. Serves R11.
  Proof: `git diff -- README.md` shows exactly one changed line.
- [ ] **T5.** Update `docs/PLAN.md` (spec index 001 to implemented), run `/verify`-equivalent check by hand (the fresh-context reviewer subagent arrives in spec 003), record anything caught in `docs/agent-log.md`.

## Traceability

| Criterion | Proving test | Status |
|---|---|---|
| R1 | CI step "R1 byte-identical"; local `cmp` | todo |
| R2 | CI step "R2 warn" | todo |
| R3 | CI step "R3 asan" | todo |
| R4 | CI step "R4 test placeholder" | todo |
| R5 | CI step "R5 clean leaves no binaries" | todo |
| R6 | CI matrix `clang` job | todo |
| R7 | CI step "R7/R8 tree clean" | todo |
| R8 | same step as R7 | todo |
| R9 | CI step "R9 renormalize" | todo |
| R10 | CI run itself, green on both jobs | todo |
| R11 | manual: `git diff -- README.md` is one line (no automated test; stated honestly) | todo |

## Change log
(none yet)
