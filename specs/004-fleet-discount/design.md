# Spec 004: fleet discount (TICKET-142): design

**Status:** draft (gate 2 pending). Requirements approved 2026-11-07.

## Approach
Four small changes, all in existing code, no new files in the program:

1. **Fleet flag = customer type `F`** (proposed as D1 in `docs/DECISIONS.md`; confirmed here if you approve this design). The customer file already has a one-character type field that the loader keeps as read (`dbfile.c:89`) and the saver writes back as is (`dbfile.c:195`). No change to `customers.dat` layout.
2. **Discount in `calc_quote`** (`calc.c`): a new `fleet_disc` in `QUOTE` (`calc.h:6`). For type `F` it is `rnd2(list * 0.04)`, else exactly `0`. The salesman discount is taken from `list - trade_disc - fleet_disc`; `net = list - trade_disc - fleet_disc - disc`.
3. **Invoice carries the amount** in a new `fleet_disc` member of `INVOICE` (`globals.h:42`), saved as an optional 12th field of `invoices.dat` (decision Q1 = a).
4. **Screens**: quote and invoice print a `Fleet discount` line; customer screens show `Fleet`; Add Customer gets one more question; the customer menu gets one more action.

### Why the non-fleet output cannot change (R11)
Every new term is `0.0` for retail and trade customers, and `x - 0.0` and `x + 0.0` give exactly `x` in IEEE doubles, so every intermediate value is bit-identical to today's. New output lines print only when `fleet_disc > 0`. The invoice file writes the extra field only for fleet invoices (below), so non-fleet saves write the same bytes (R13). The `Discounts -0.00` line (B10) is untouched for non-fleet invoices.

## Code touched
Line numbers are from the current tree, checked 2026-11-07.

| File:line | Change |
|---|---|
| `calc.h:6` | add `double fleet_disc;` after `trade_disc` |
| `calc.c:27-29` | next to the trade discount: `q->fleet_disc = 0; if (cust_type == 'F') q->fleet_disc = rnd2(list * 0.04);` |
| `calc.c:36` | salesman base becomes `(list - q->trade_disc - q->fleet_disc)` |
| `calc.c:38` | `net = list - q->trade_disc - q->fleet_disc - q->disc` |
| `calc.c:4-13` | header comment is already wrong (B1, B3, B4, B9); only a fleet line is added, nothing else corrected |
| `globals.h:33` | comment: `R = retail, T = trade, F = fleet` |
| `globals.h:42` | add `double fleet_disc;  /* part of disc that is the fleet discount */` to `INVOICE` |
| `dbfile.c:134` | after `total`, read a 12th field: `t = strtok(NULL, "\|"); i->fleet_disc = t ? atof(t) : 0;` |
| `dbfile.c:210-213` | save: unchanged format for `fleet_disc == 0`; for `> 0` write the extra `\|%.2f` (a second `fprintf` branch) |
| `main.c:215`, `main.c:336` | the `Trade`/`Retail` choice becomes three-way. One small `static const char *type_name(char t)` returning `Fleet`, `Trade` or `Retail` (anything else `Retail`, as today), used by both |
| `main.c:245` | after the Trade question, if the answer was No, ask `Fleet customer (Y/N)?`; type `F` on Yes, else `R` |
| `main.c:283-292` | new menu line `4. Mark customer as fleet` and `case 4:` calling a new `mark_fleet()` |
| `main.c` (new, near `add_customer`) | `mark_fleet()`: see "Marking an existing customer" |
| `main.c:340-341` | after the Trade line: `if (q->fleet_disc > 0) printf("  Fleet discount           %12.2f\n", -q->fleet_disc);` |
| `main.c:400` | `i->disc = q.trade_disc + q.fleet_disc + q.disc;` and `i->fleet_disc = q.fleet_disc;` |
| `main.c:461` | invoice view, see "Invoice view" |

### Add Customer prompts (R1)
```
  Trade customer (Y/N)?   <- unchanged; Y keeps today's flow, so the trade path is byte-identical
  Fleet customer (Y/N)?   <- NEW, asked only when the Trade answer was not Y
```
Only the retail path changes, and only by this one prompt. A retail answer script for `cust_add_retail` therefore needs one extra input line, which is the intended golden change (R14).

### Marking an existing customer (R2, R3)
New customer menu action `4. Mark customer as fleet`, which:
1. asks `Customer ID :` through `read_int`; unknown ID prints `Customer not found.` (same wording as the quote screen, `main.c:320`);
2. **Retail** customer: asks `Mark <name> as fleet (Y/N)?` through `confirm`, since there is no un-mark (Q3). Yes sets type `F`, calls `save_customers()`, prints `Customer <id> marked as fleet.`; No prints `Cancelled.`;
3. **Fleet** customer: prints `<name> is already a fleet customer.`, no change;
4. **Trade** customer: refused with `<name> is a trade customer and cannot be changed to fleet.`, no change. (New decision **A8**: silently replacing the 10% trade discount with 4% would be a surprise price change for staff, and R3 says a customer is one kind.)
Each branch ends with `pause_enter()`, like the neighbouring screens.

### Invoice view (R10, R11)
```
fleet_disc == 0   ->  exactly the current lines (including Discounts -0.00 for B10)
fleet_disc  > 0   ->  List price
                      Fleet discount      -419.80      NEW
                      Discounts           -806.02      only if rnd2(disc - fleet_disc) > 0
                      Net price ...
```
`disc` still holds all discounts together (fleet + salesman), so `net = list - disc` still holds, the total is unchanged and an old binary reading the file shows the same combined `Discounts`. The `rnd2(...)` guard avoids a stray `0.00` line caused by subtracting two stored two-decimal values.

### Invoice preview in the sale flow
`sell_vehicle` calls the same `print_quote` (`main.c:385`), so the preview gets the `Fleet discount` line with no extra code.

## Data and compatibility impact
- `customers.dat`: format identical. A fleet customer has `F` in the type column.
- `invoices.dat`: 11 fields as today for every non-fleet invoice, 12 for a fleet one. The loader ignores a missing 12th field (value 0) and an old binary ignores an extra one. Mixed files are fine because each line is parsed on its own.
- Rolling back to the previous binary (`dealerdesk.old`): fleet customers appear as `Retail` and quote at full price, and their stored invoices show the combined `Discounts` line with the right total. Nothing is lost and nothing needs converting. A customer marked `F` and re-saved by the old binary keeps `F` (it writes the `%c` back).
- No change to `stock.dat`, `next_ids.dat` or the sample `data/` (rule 2).

## Test approach (detail in `tasks.md`)
- Tests first: scenarios for each criterion are written and approved against the *current* binary where they should not change, so a pass proves no drift. Fleet scenarios will first fail (no fleet feature), then pass.
- The fixtures are frozen and must not be edited by hand. Fleet scenarios therefore create their fleet customer through the app (Add Customer with Fleet = Y, or mark Greenway Taxis through the new action) inside the same scenario, using the harness `---` separator where a reload is needed (R12, persisted `F`).
- Hand-calculated expected figures from the requirements (R4, R7, R8) are checked against the goldens before they are approved.
- `make test-selfcheck` and the ASan run must still pass.

## Rejected alternatives
- **Separate `fleet` column in `customers.dat`** (a boolean beside `type`): would allow Fleet+Trade, but a change in the customer file layout breaks `strtok` handling when a field is empty (B2) and an old binary would drop the column on save. Rejected: more risk for a combination nobody asked for (A2).
- **Derive the invoice fleet line from the customer's type when viewing (Q1 b):** no file change, but the figures would be wrong if the customer's type ever changed. Rejected at gate 1.
- **Separate `fleet_disc` for every invoice (always write 12 fields):** simpler code, but every saved `invoices.dat` changes, which breaks R13 and the data goldens of every existing sale scenario. Rejected.
- **Store a per-customer rate** (A4): not asked for; would need a new field.
- **Percentage printed on the fleet line** (like `Discount (8.0%)`): the trade line has no percentage, and the ticket says "the same way the trade discount does" (A6).
- **A single new menu option "Add fleet customer"** instead of the extra question: still changes the customer menu and gives two ways to add a customer. Rejected.

## Risks
- **R-a. Float behaviour.** The "adding 0.0 changes nothing" argument is exact for IEEE doubles, but it is proved by the goldens, not assumed: all existing quote and sale goldens must stay byte-identical (R11, R14) on gcc and clang and under ASan/UBSan.
- **R-b. B2 on reload.** A fleet customer with an empty phone number is shifted by `strtok` and reloads as Retail (as a Trade customer does today). Recorded in `docs/CODEMAP.md` under B2 when this lands; not fixed.
- **R-c. Unmarking.** There is none (Q3). A wrongly marked customer needs a manual edit of `customers.dat`. The confirm question is the only guard.
- **R-d. Mixed `invoices.dat`.** Anyone parsing the file by field count will see 11 or 12. The program does not; an external spreadsheet export might. Noted for the owner.
- **R-e. Golden churn.** R14 changes `cust_add_retail`, anything scripting the customer menu or Add Customer, and adds the `mark_fleet` ones. The commit for each cites its criterion.
- **R-f. Hook and review.** The `make warn` hook (zero-warning baseline) runs after each C edit; each C commit is explained line by line before it is made (CLAUDE.md rule 3).

## Change log
- 2026-11-07: first draft after gate 1. New decision A8 (trade customers cannot be changed to fleet) added here because the requirements did not cover it; it is mirrored into the requirements assumptions if the design is approved.
