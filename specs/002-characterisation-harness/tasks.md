# Spec 002: characterisation harness: tasks

**Status:** approved. Each task is its own commit, message `spec 002 Tn: ...`. No C file changes. `--update` is run only to create the goldens of the scenarios in that task, then the output is reviewed before committing.

- [ ] **T1.** Harness core and fixture. Add `tests/fixtures/data/` (copy of baseline `data/`), `tests/golden.py` (run, normalise, compare, `--update`, `--bin`, timeout, data-untouched check), and a first scenario `stock_list`. Makefile `test` runs the harness. Serves R1-R6, R15 (default binary).
  Proof: `make test` passes; deleting one line of the golden makes it fail with a diff; `--update` under `CI=1` refuses; real `data/` hash unchanged.
- [ ] **T2.** Self-check. `--selfcheck` and `make test-selfcheck` (mutation to 11% plus hanging binary). Serves R6, R14.
  Proof: `make test-selfcheck` passes; run by hand with the mutation left in a copy to show the failing scenario names.
- [ ] **T3.** Stock and menu scenarios (R7, R12 part): the `stock_*` set, `help_screen`, `menu_invalid_option`, `eof_mid_screen`.
- [ ] **T4.** Customer scenarios (R8, R13): the `cust_*` set and `bug_B2_empty_phone`.
- [ ] **T5.** Quote scenarios (R9): the `quote_*` set.
- [ ] **T6.** Sale and invoice scenarios (R10, R11): `sell_*` and `inv_*`.
- [ ] **T7.** Golden review gate (A7). Independently recompute at least three quote totals and one saved invoice by a throwaway script (not committed), plus read every scenario's stdout. Report to the owner; fix scenario scripts only, never goldens by hand.
- [ ] **T8.** `make test-asan`, CI steps, replace the R4 placeholder. Update spec 001 change log (R4 superseded) and `docs/DECISIONS.md` D9 (`<ESC>`). Serves R15, R16.
  Proof: green CI run, gcc and clang, with both test steps and the selfcheck on gcc.
- [ ] **T9.** Close out: traceability table, spec statuses, `docs/PLAN.md`, `docs/agent-log.md`, `docs/CODEMAP.md` (bugs confirmed by goldens). Serves R17 (empty diff on `*.c`, `*.h`, `data/` versus `baseline`).

## Traceability

| Criterion | Proving test | Status |
|---|---|---|
| R1 | harness data-hash check + CI "tree clean" step | todo |
| R2 | every scenario (stdout, exit code, stderr, changed .dat) | todo |
| R3 | `sell_retail_view` (date mask); two consecutive `make test` runs | todo |
| R4 | break-a-golden check in T1; every failing run in selfcheck | todo |
| R5 | `CI=1 --update` refusal check; missing-golden message check | todo |
| R6 | selfcheck, hanging-binary part | todo |
| R7 | `stock_*` scenarios | todo |
| R8 | `cust_*`, `bug_B2_empty_phone` | todo |
| R9 | `quote_*` scenarios | todo |
| R10 | `sell_*` scenarios | todo |
| R11 | `inv_*` scenarios | todo |
| R12 | `help_screen`, `menu_invalid_option`, `eof_mid_screen` | todo |
| R13 | `bug_B2_empty_phone` golden contains the buggy output | todo |
| R14 | `make test-selfcheck` | todo |
| R15 | `make test`, `make test-asan` | todo |
| R16 | CI run, gcc and clang | todo |
| R17 | `git diff baseline -- '*.c' '*.h' data` is empty | todo |

## Change log
(none yet)
