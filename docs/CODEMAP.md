# DealerDesk code map

Baseline: upstream `a2ba708` (tag `baseline`). Every `file:line` below was checked against that tree in Phase 1.

## Modules
| File | Lines | Role |
|---|---|---|
| `main.c` | 540 | Globals and arrays (18-27), menus, screens, quote printing (332-352), sale creation (367-414), invoice screens (418-470), `main()` (509) |
| `calc.c` / `calc.h` | 45 / 20 | Pricing: `rnd2` (18), `calc_quote` (23). `QUOTE` struct in `calc.h:4-15` |
| `dbfile.c` / `dbfile.h` | 229 / 10 | Flat-file `load_*` (21-154) and `save_*` (164-229) |
| `screen.c` / `screen.h` | 70 / 12 | `header` (14), `read_line` (22), `read_int` (45), `read_money` (52), `confirm` (65) |
| `globals.h` | 61 | `VEHICLE`, `CUSTOMER`, `INVOICE`, limits 500/500/2000 (7-9) |

## Data files (`data/*.dat`)
Pipe-delimited text, one record per line, loaded with `strtok`. Blank lines and `#` lines are skipped (`dbfile.c:34,75,108`). Extra trailing fields are ignored. Missing trailing fields default to 0 or empty (numeric ones via `t ? atof(t) : 0`).

| File | Layout | Load | Save |
|---|---|---|---|
| `stock.dat` | `id\|plate\|make\|model\|year\|mileage\|cost\|price\|status` (status 0 stock, 1 reserved, 2 sold) | `dbfile.c:21-60` | `175` |
| `customers.dat` | `id\|name\|phone\|email\|type` (type `R` or `T`; missing type defaults `R`) | `62-93` (type at 89) | `193` |
| `invoices.dat` | `no\|date\|veh_id\|cust_id\|list\|disc\|net\|vat\|fees\|tradein\|total` (11 fields, money `%.2f`) | `95-138` | `210` |
| `next_ids.dat` | `vehicle=N`, `customer=N`, `invoice=N` lines | `140-154` | `226` |

- Every save rewrites the whole file with `fopen(..., "w")` and no temp file (`dbfile.c:169,187,204,221`).
- `INVOICE.disc` holds all discounts combined (`globals.h:42`, `main.c:400`). There is no per-discount breakdown on stored invoices.
- Data directory is the relative path `data/` (`dbfile.c:13`), so the program must run from the repo root.

## Money
- All amounts are `double`, printed and saved with `%.2f`.
- `rnd2(x) = floor(x*100+0.5)/100` (`calc.c:20`). Applied to: trade discount (29), salesman discount (36), VAT (40). **Not** applied to `net` (38) or `total` (44).
- Build-up in `calc_quote` (`calc.c:23-45`):
  1. trade discount = `rnd2(list * 0.10)` for customer type `T` (29)
  2. salesman % clamped to 0..15 (31-34), discount = `rnd2((list - trade) * pct / 100)` (36)
  3. `net = list - trade - disc` (38)
  4. delivery 150.00 (39), `vat = rnd2((net + delivery) * 0.20)` (40), registration 55.00 (41)
  5. `total = net + delivery + vat + reg - tradein` (44). Trade-in is subtracted as entered, with no validation.
- Quote prints Trade discount and Discount lines separately, each only if above 0 (`main.c:340-343`).
- Sale copies the quote into an invoice (`main.c:392-406`): `disc = trade_disc + disc`, `fees = delivery + reg_fee`.
- Invoice view prints one "Discounts" line, always, even when 0 (`main.c:461`), and prints Fees before VAT (463-464). The quote prints Delivery, VAT, Registration in that order (345-347).

## Input and end of input
- Every prompt goes through `read_line` (`screen.c:22`). At EOF it prints a newline and calls `exit(0)` (29-32), so scripted stdin always terminates and never hangs.
- Over-long lines are truncated to the buffer size and the rest is drained (36-38).
- `|` is replaced with `/` on every input (40-42). Plates are stored exactly as typed (sample data has lower-case plates, e.g. `yf20 hbn`).
- `read_int` and `read_money` use `atoi` / `atof`, so non-numeric text reads as 0 (`screen.c:49,56`).
- `confirm` accepts only `Y` or `y` (`screen.c:69`); anything else is No.

## Time and environment dependence
- Only the sale date: `strftime("%Y-%m-%d", localtime(time()))` (`main.c:395-396`).
- Screens start with ANSI clear `\033[2J\033[H` (`screen.c:11`). Header shows version `v2.3` (`screen.c:18`).
- Quote "valid 7 days" is text only (`main.c:362`), nothing checks it.

## Behaviours worth knowing
- Reserved vehicles can be quoted and sold; only sold vehicles are refused (`main.c:314`).
- Find by plate is an exact, case-sensitive `strcmp` (`main.c:124`); find customer is a case-sensitive substring match (`269`).
- The invoice number is taken before the sale is saved (`main.c:394`) and the three saves are separate (`409-411`), so a crash between them can leave files inconsistent.

## Sample data and what each invoice exercises
- 50230: retail customer, no trade discount, trade-in 1500.00
- 50231: trade customer 2002, disc 1349.50 = 10% of 13495.00
- 50232: Greenway Taxis (2008, retail), disc 839.60 = 8% of 10495.00, the hand-given "fleet" discount from the ticket

## Discrepancies and bugs (recorded, not fixed)
| ID | What | Where |
|---|---|---|
| B1 | README and help say trade discount is 5%; code gives 10% | `README.md:66`, `main.c:500`, `calc.c:29` |
| B2 | `strtok` collapses empty fields. An empty phone shifts email into phone and type into email; a Trade customer reloads as Retail, and the next save makes it permanent. Reproduced on a scratch copy. | `dbfile.c:78-89` |
| B3 | README and help describe a manager PIN above 10%; code has no PIN and clamps at 15% | `README.md:67`, `main.c:501`, `calc.c:33` |
| B4 | README says VAT is on list price and delivery is VAT-exempt; code charges VAT on net + delivery | `README.md:64,68`, `calc.c:40` |
| B5 | Help says plates are upper-cased automatically; that was removed | `main.c:5,499` |
| B6 | README build line names `report.c`, omits `calc.c` and `-lm`; says v2.1 (header v2.3); data path `C:\DEALERDESK\DATA` | `README.md:29,39`, `screen.c:18` |
| B7 | Main menu has no option 6 although README lists Reports; reports were removed | `README.md:57`, commit `399a544` |
| B8 | Negative or unlimited trade-in is accepted | `main.c:324`, `calc.c:42` |
| B9 | `calc.c` header comment says "VAT 20% on list price" | `calc.c:10` |
