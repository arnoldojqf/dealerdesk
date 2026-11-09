# Cross-cutting decisions

Spec-specific decisions live in each spec. Format: decision, reasoning, status.

## D1. Fleet flag stored as customer type `F` (confirmed 2026-11-07, spec 004 design gate)
No file-format change. An old binary writes the `%c` back unchanged, so rolling back to `dealerdesk.old` is safe. Cost: a customer cannot be both Trade and Fleet.

## D8. Existing bugs are recorded, not fixed
Behaviour is preserved, bugs included (B-IDs in CODEMAP). Fixing is a separate decision for the user.

## D9. Harness uses the Python standard library only
No pip step in CI. The date is masked as `<TODAY>`. The ANSI escape byte is stored as the text `<ESC>` (changed from "raw bytes" during spec 002: raw escapes clear the terminal when a golden is `cat`ed and make diffs unreadable).

## D10. clang runs in CI only
It is not installed locally. Installing it is the user's call.

## D11. Default branch stays `master`
That is what upstream uses. Keeps the history comparable.

## D12. Fleet discount stored in an optional 12th field of `invoices.dat` (2026-11-07, spec 004)
Written only when above 0, so a save with no fleet invoice is byte-identical to today's. The loader defaults a missing field to 0, and an old binary ignores the extra one. `disc` stays "all discounts together", so `net = list - disc` still holds and an old binary shows the right total. Chosen over deriving the amount from the customer's current type (wrong if the type changes) and over always writing 12 fields (changes every saved file and every sale golden). Cost: a file can mix 11- and 12-field lines.

## Spec 004 assumptions A1-A8 (fleet discount, TICKET-142; made 2026-11-07, approved at gates 1-2)
The ticket is silent on each of these; the call made is listed here. The full wording is in `specs/004-fleet-discount/requirements.md`.
- **A1. Base of the 4%.** "4% off the vehicle price" is 4% of the list price (the stock price), the same base as the trade discount, rounded with `rnd2`.
- **A2. Fleet and trade do not stack.** A customer is exactly one of Retail, Trade or Fleet (the file has one type character, D1).
- **A3. Order with the salesman discount.** The salesman percentage applies after the fleet discount, as it does after the trade discount. Percentage of list would give salesmen more room on fleet deals than on trade deals.
- **A4. Fixed rate.** 4% is fixed in the program; the ticket gives no per-customer rate.
- **A5. Sample data stays as it is.** Greenway Taxis stays Retail in the sample data until staff mark it in the app; invoice 50232 keeps its hand-given 8%.
- **A6. Label.** The quote line is `Fleet discount`, shown only when above 0, with no percentage, to match the trade line.
- **A7. Vehicle rules.** Nothing about reserved or sold vehicles changes for fleet customers.
- **A8. Marking an existing customer.** Allowed only for a Retail customer, after a confirm question. A Trade customer is refused (it would silently swap the 10% trade discount for 4%), a Fleet customer is told they are already fleet, and there is no un-mark (Q3).

## D13. `make demo` replays existing fleet scenarios on a temp copy of the fixtures (2026-11-09, phase 6)
`scripts/demo.py` imports `read_sessions` and `FIXTURE` from `tests/golden.py` and runs the binary on a temporary copy of `tests/fixtures/data/`, so it never touches `data/` (rule 2) and needs no new scenario files. It shows `fleet_quote_10000` (a fleet quote with its own "Fleet discount" line) and `fleet_sell_view` (a fleet sale, then the stored invoice viewed after a reload). It compares nothing and writes nothing, so it is not a test; the goldens remain the check. Screen-clear escapes are replaced by a rule line so the output reads in a terminal log. No C change.
