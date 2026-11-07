# Spec 002: characterisation harness: tasks

**Status:** implemented. Each task is its own commit, message `spec 002 Tn: ...`. No C file changes. `--update` is run only to create the goldens of the scenarios in that task, then the output is reviewed before committing.

- [x] **T1.** Harness core and fixture. Add `tests/fixtures/data/` (copy of baseline `data/`), `tests/golden.py` (run, normalise, compare, `--update`, `--bin`, timeout, data-untouched check), and a first scenario `stock_list`. Makefile `test` runs the harness. Serves R1-R6, R15 (default binary).
  Proof: `make test` passes; deleting one line of the golden makes it fail with a diff; `--update` under `CI=1` refuses; real `data/` hash unchanged.
- [x] **T2.** Self-check. `--selfcheck` and `make test-selfcheck` (mutation to 11% plus hanging binary). Serves R6, R14.
  Proof: `make test-selfcheck` passes; run by hand with the mutation left in a copy to show the failing scenario names.
- [x] **T3.** Stock and menu scenarios (R7, R12 part): the `stock_*` set, `help_screen`, `menu_invalid_option`, `eof_mid_screen`.
- [x] **T4.** Customer scenarios (R8, R13): the `cust_*` set and `bug_B2_empty_phone`.
- [x] **T5.** Quote scenarios (R9): the `quote_*` set.
- [x] **T6.** Sale and invoice scenarios (R10, R11): `sell_*` and `inv_*`.
- [x] **T7.** Golden review gate (A7). Independently recompute at least three quote totals and one saved invoice by a throwaway script (not committed), plus read every scenario's stdout. Report to the owner; fix scenario scripts only, never goldens by hand.
- [x] **T8.** `make test-asan`, CI steps, replace the R4 placeholder. Update spec 001 change log (R4 superseded) and `docs/DECISIONS.md` D9 (`<ESC>`). Serves R15, R16.
  Proof: green CI run, gcc and clang, with both test steps and the selfcheck on gcc.
- [x] **T10.** (added after `/verify 002`) Fix what the independent review found: automate the manual proofs for R2-R5 and R15 in `--selfcheck`, make stderr always fatal, correct the spec text. Serves R2, R3, R4, R5, R14, R15.
- [x] **T9.** Close out: traceability table, spec statuses, `docs/PLAN.md`, `docs/agent-log.md`, `docs/CODEMAP.md` (bugs confirmed by goldens). Serves R17 (empty diff on `*.c`, `*.h`, `data/` versus `baseline`).

## Traceability

| Criterion | Proving test | Status |
|---|---|---|
| R1 | harness data-hash check in every run; CI "tree clean" step | pass |
| R2 | all 34 scenarios; stderr output fails (selfcheck) | pass |
| R3 | `make test-selfcheck` (two runs identical, date masked) | pass |
| R4 | `make test-selfcheck` (tampered golden fails) and the mutation check | pass |
| R5 | `make test-selfcheck` (missing golden fails; `--update` refused under `CI`, golden unchanged) | pass |
| R6 | selfcheck hanging-binary part | pass |
| R7 | `stock_*` (7) | pass |
| R8 | `cust_*` (4), `bug_B2_empty_phone` | pass |
| R9 | `quote_*` (11, including `quote_reserved_vehicle`) | pass |
| R10 | `sell_*` (3) | pass |
| R11 | `inv_*` (5) | pass |
| R12 | `help_screen`, `menu_invalid_option`, `eof_mid_screen` | pass |
| R13 | `bug_B2_empty_phone` golden holds the buggy output | pass |
| R14 | `make test-selfcheck`, CI run 42417079234 (gcc) | pass |
| R15 | `make test`, `make test-asan`; stderr-only difference caught by `make test-selfcheck` | pass |
| R16 | CI run 42417079234: 34/34 on gcc and clang, with and without ASan/UBSan | pass |
| R17 | `git diff baseline -- *.c *.h data` is empty | pass |

## Change log
- 2026-11-07: scenario `quote_trade` created in T2 instead of T5. Reason: the self-check mutation (trade 10% to 11%) is only detectable by a trade-customer quote; with only `stock_list` the self-check would have failed. Verified by removing it: self-check exits 2.
- 2026-11-07 (after `/verify 002`): added T10. The review found that R3, R5 and the fake-stderr part of R15 were marked "pass" on one-off manual checks, and that R2's stderr capture was not enforced outside the ASan run. All are now automated; the traceability rows say where. Scenario counts: 34 total, 11 `quote_*`.
