# Spec 004: fleet discount (TICKET-142): tasks

**Status:** approved 2026-11-08 (gate 3). Requirements and design approved 2026-11-07.
**Review mode:** three gates. Each task is its own commit, message `spec 004 Tn: ...`, citing the criteria. Tests pass at every commit.

## How every task runs (tests first)
1. Write the scenario(s) in `tests/scenarios/` with the hand-calculated figures in a `#` comment. Run them on the current binary and look at the output: a new scenario must fail for the right reason (feature missing), not just for lack of a golden.
2. Make the smallest C change. `make warn` must stay at zero warnings (the hook checks it).
3. Compare the output with the hand figures. Only then approve the golden with `python3 tests/golden.py --update <scenario>`, one scenario at a time. The commit message names the criterion.
4. Run `make test`, `make test-asan`, `git diff --stat tests/golden` (only the files the task names may change) and `git status` (no `data/` change).
5. For a task that changes C: explain the diff line by line and wait for the owner's acknowledgement before committing (CLAUDE.md rule 3).

Fleet customers are made inside the scenarios (mark Greenway Taxis 2008, or Add Customer). Fixtures and goldens are never edited by hand. Prices: stock 1002 is 10995.00 and unsold; other prices are set with stock option 5 on unsold vehicle 1004. Menus: main 3 = quote, 4 = sell, 5 = invoices; customer menu gains option 4.

## Tasks

- [x] **T1. Calculation (R4, R8, R11).** `calc.h`: `fleet_disc` in `QUOTE`. `calc.c`: `fleet_disc = rnd2(list * 0.04)` for type `F`, else 0; salesman base and `net` subtract it.
  Test first: no new scenario can show it yet (no screen prints it, no customer is `F`). The proof is that all 34 existing goldens stay byte-identical, which is the R-a argument ("adding 0.0 changes nothing") checked on gcc and under ASan/UBSan. No golden changes.
- [ ] **T2. Type name and Mark as fleet (R2, R3, R14, A8).** `main.c`: `type_name()` used by the customer row and the quote customer line; menu line `4. Mark customer as fleet`; `mark_fleet()`. `globals.h:33` comment.
  Tests first (fail: option 4 is "Invalid option"):
  - `fleet_mark_greenway`: mark 2008 (Y), list shows `Fleet`, mark again says already fleet, `---`, list again (persisted). `customers.dat` differs from the fixture only in 2008's type.
  - `fleet_mark_refused`: trade 2002 refused, unknown 9999 `Customer not found.`, retail 2001 answered N gives `Cancelled.`. No data file changes.
  Goldens updated under R14: `cust_add_trade`, `cust_add_retail`, `cust_find`, `cust_list`, `bug_B2_empty_phone`. The diff of each must be the new menu line and nothing else; shown to the owner before approval.
- [ ] **T3. Add Customer asks Fleet (R1, R14).** `main.c`: after a No to Trade, ask `Fleet customer (Y/N)?`. Write the C prompt first; then, in the same commit, add the extra `N` line to `tests/scenarios/cust_add_retail.txt` (a scenario, not protected) and update its golden (the new prompt line only; the other four are not touched again). Before the prompt exists the extra `N` would be read as the ENTER, so the two changes belong together.
  Test first: `fleet_add_customer` (Trade N, Fleet Y, list, `---`, find shows `Fleet`; `customers.dat` ends `|F`). Fails before the prompt exists.
- [ ] **T4. Fleet line on the quote (R3-R9).** `main.c`: customer line `(Fleet)` via `type_name()` (done in T2) and `Fleet discount` line when above 0, after the Trade line.
  Tests first. Before T4 they show the right totals but no `Fleet discount` line; after T4 they match the figures in the comment:
  - `fleet_quote_1002` (R5, R6): 1002 at 10995.00, 0%: fleet 439.80, net 10555.20, VAT 2141.04, total 12901.24. No Trade line.
  - `fleet_quote_10000` (R4, R7): price set to 10000.00: fleet 400.00, net 9600.00, VAT 1950.00, total 11755.00.
  - `fleet_quote_10495` (R4, R7, R8): price 10495.00, two quotes. 0%: fleet 419.80, net 10075.20, VAT 2045.04, total 12325.24. 8%: salesman 806.02, net 9269.18, VAT 1883.84, total 11358.02.
  - `fleet_quote_rounding` (R4): price 10000.13: fleet 400.01 (4% is 400.0052), net 9600.12, VAT 1950.02, total 11755.14.
  - `fleet_quote_tradein` (R9): 1002, trade-in 2000.00: total 10901.24.
  - `fleet_quote_trade_unchanged` (R3): Trade customer 2002 on 1002 still gets 10% and no Fleet line (`quote_trade` already pins vehicle 1008; this adds the contrast in one scenario with a fleet quote). Hand figures: 1002 at 10995.00, 0%, no trade-in: trade 1099.50, net 9895.50, VAT 2009.10, total 12109.60.
- [ ] **T5. Sale, storage and invoice view (R10, R12, R13).** `globals.h`: `fleet_disc` in `INVOICE`. `main.c`: `i->disc` includes it, `i->fleet_disc` set, invoice view per the design. `dbfile.c`: optional 12th field on load, written only when above 0.
  Tests first:
  - `fleet_sell_view` (R9, R10, R12): mark 2008, sell 1002 at 8% with trade-in 1500.00 (Confirm sale: Y). Fleet 439.80, salesman 844.42, net 9710.78, VAT 1972.16, total 10387.94. `invoices.dat` gains `50233|...|439.80` as a 12th field. `---`, view 50233: `Fleet discount -439.80` and `Discounts -844.42`; then list invoices (11- and 12-field lines side by side).
  - `fleet_sell_no_salesman` (R10, R12): 0%: view has no `Discounts` line; total 12901.24 equals the quote. `invoices.dat` line ends `|439.80`. Then `---` (reload) and view 50233 again: same output, so the 12th field survives a reload.
  R11 and R13: the existing sale, invoice and add-customer goldens (data files included) stay byte-identical; `git diff --stat tests/golden` shows none of them.
- [ ] **T6. Known-bug interplay and docs, no C (R-b, A1-A8).** Scenario `fleet_B2_empty_phone`: add a Fleet customer with an empty phone, reload, list: type shows `Retail` (pins B2 as it does for Trade). `docs/CODEMAP.md`: B2 note and where the fleet code lives. `docs/DECISIONS.md`: A1-A8 (the requirements promised this, and it is missing today). `docs/PLAN.md` statuses.
- [ ] **T7. Close-out (R11, R13, R14).** `make warn`, `make test`, `make test-asan`, `make test-selfcheck`, `make check-agent`. `git diff --stat f8e6762 -- tests/golden`: only the five R14 goldens (T2, T3) and new `fleet_*` directories may appear; no `quote_*`, `sell_*`, `inv_*` or `stock_*`. `git diff baseline -- data` empty. clang runs in CI after the owner pushes (D10). Fill in the table below and set the statuses.

## Traceability

| Criterion | Proving test | Task | Status |
|---|---|---|---|
| R1 mark when adding | `fleet_add_customer` | T3 | pending |
| R2 mark existing | `fleet_mark_greenway`, `fleet_mark_refused` | T2 | pending |
| R3 one kind | `fleet_mark_refused` (trade refused), `fleet_quote_1002` (no Trade line for fleet), `fleet_quote_trade_unchanged`, `quote_trade` | T2, T4 | pending |
| R4 amount | `fleet_quote_10000`, `fleet_quote_10495`, `fleet_quote_rounding` | T1, T4 | calculation done (T1), tests pending (T4) |
| R5 own line, `(Fleet)` | `fleet_quote_1002` | T4 | pending |
| R6 fees, VAT | Delivery, VAT, Registration lines of every `fleet_quote_*` | T4 | pending |
| R7 total | `fleet_quote_10000`, `fleet_quote_10495` | T4 | pending |
| R8 salesman | `fleet_quote_10495` (8%), `fleet_sell_view` | T4, T5 | pending |
| R9 trade-in | `fleet_quote_tradein`, `fleet_sell_view` | T4, T5 | pending |
| R10 invoice | `fleet_sell_view`, `fleet_sell_no_salesman` | T5 | pending |
| R11 non-fleet unchanged | every existing `quote_*`, `sell_*`, `inv_*` golden unchanged; T1 run | T1, T7 | T1: 34 goldens byte-identical on gcc, ASan/UBSan (2026-11-08); T7 pending |
| R12 existing data loads | `inv_view_50230`-`50232`, `inv_list`, `fleet_sell_view` run 2, `fleet_sell_no_salesman` run 2 | T5 | pending |
| R13 files same bytes | data files in `sell_retail_view`, `sell_trade_salesman_tradein`, `cust_add_trade` | T5, T7 | pending |
| R14 existing tests | `git diff --stat` on `tests/golden` (T7), five goldens named in T2 | T2, T7 | pending |

Each test name above is also cited in a `#` comment at the top of its scenario file (`# R4, R7: ...`).

## Rules for changes to this file
If a task shows a figure, prompt text or criterion to be wrong, stop, fix the spec, log it below with the reason, tell the owner, then continue.

## Change log
- 2026-11-07: first draft for gate 3. Hand figures re-derived before writing: all match the design. Added two scenarios beyond the design's list: `fleet_quote_trade_unchanged` (R3 contrast) and `fleet_B2_empty_phone` (R-b), and a docs task (A1-A8 into `docs/DECISIONS.md`).
- 2026-11-08: gate 3 passed, with four edits after a review against the code and fixtures: hand figures added for `fleet_quote_trade_unchanged`; `fleet_quote_1002` cited under R3; a reload added to `fleet_sell_no_salesman` (also cited under R12); wording fixed in T3 (prompt, extra `N` and golden in one commit) and T5 (`Confirm sale: Y`). All other hand figures re-derived and match.
