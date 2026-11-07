# DealerDesk code map

STATUS: preliminary. These are findings from the planning read-through. Phase 1 completes and re-verifies every line reference against the clone.

Baseline: upstream `a2ba708`.

## Modules
- `main.c` (540 lines): menus, screens, quote and invoice printing, sale creation.
- `calc.c` / `calc.h`: pricing (`calc_quote`, `rnd2`).
- `dbfile.c` / `dbfile.h`: flat-file load and save.
- `screen.c` / `screen.h`: terminal helpers and input.
- `globals.h`: record structs and limits.

## Data files (`data/*.dat`)
- Pipe-delimited text, one record per line, parsed with `strtok`. Extra trailing fields are ignored. `dbfile.c:32-58,73-92,106-136`
- customers: `id|name|phone|email|type`, type is `R` or `T`. `dbfile.c:193`
- invoices: 11 fields, `disc` is all discounts combined. `globals.h:42`, `dbfile.c:210`
- `next_ids.dat`: `vehicle=`, `customer=`, `invoice=` lines. `dbfile.c:226`

## Money
- `double`. `rnd2` = `floor(x*100+0.5)/100`. `calc.c:18-21`
- Rounded: trade discount, salesman discount, VAT. `net` and `total` are unrounded sums. `calc.c:29,36,38,40,44`
- Order: trade 10% of list, salesman % (clamped 0-15) of (list - trade), VAT 20% of (net + 150 delivery), then +55 registration, minus trade-in.
- Quote prints separate trade and salesman lines. `main.c:339-351`. The invoice prints one "Discounts" line. `main.c:461`

## Input and time
- All reads go through `read_line`, which calls `exit(0)` at EOF. `screen.c:29-32`
- `|` is replaced by `/` on input. `screen.c:40-42`
- Data directory is relative: `data/`. `dbfile.c:13`
- Only non-determinism: invoice date from `localtime(time())`. `main.c:395-396`. Screens begin with ANSI clear. `screen.c:11`

## Discrepancies and bugs (recorded, not fixed)
- B1: README and help say trade discount is 5%; code is 10%. `README.md:66`, `main.c:500`, `calc.c:29`
- B2: `strtok` collapses empty fields, so an empty phone shifts email and type. A Trade customer reloads as Retail. `dbfile.c:78-89`
- B3: README and help mention a manager PIN above 10%; code clamps at 15% with no PIN. `README.md:67`, `main.c:501`, `calc.c:33`
- B4: README says VAT on list price and delivery VAT-exempt; code taxes net + delivery. `README.md:64,68`, `calc.c:40`
- B5: help says plates are upper-cased; this was removed. `main.c:499`
- B6: README names `report.c`, omits `calc.c` and `-lm`, says v2.1 (header says v2.3), and cites `C:\DEALERDESK\DATA`. `README.md:29,39`, `screen.c:18`
