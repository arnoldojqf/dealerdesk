# Spec 004: fleet discount (TICKET-142): requirements

**Review mode:** three gates (requirements, then design, then tasks), each approved on its own.
**Status:** draft

## Problem
Sales staff give fleet customers (taxi firms, rental companies, delivery services; Greenway Taxis is the first) their discount by typing it into the salesman discount field. It is applied inconsistently and it uses up the salesperson's 0-15% negotiating room. The business wants the discount to be automatic, separate from the salesman discount, and visible as its own line.

Everything else must behave exactly as today (`specs/README.md`, principles 1 and 2).

## Facts from the code that shape the requirements
(`docs/CODEMAP.md`, all re-read on 2026-11-07)
- A customer has a type, `R` or `T` (`globals.h:33`). Add Customer asks only "Trade customer (Y/N)?" (`main.c:245`). **There is no way to change an existing customer** (customer menu: list, add, find; `main.c:284-287`).
- Trade discount is `rnd2(list * 0.10)`, shown on its own quote line only when above 0 (`calc.c:29`, `main.c:340-341`).
- The salesman discount is a percentage clamped to 0-15, taken from list minus trade discount (`calc.c:36`).
- VAT is charged on net plus delivery (`calc.c:40`), so any new discount also lowers VAT (B4 in CODEMAP).
- A stored invoice has one combined `disc` field (`globals.h:42`, `main.c:400`), and the invoice screen prints one `Discounts` line (`main.c:461`). So today the trade discount is **not** a separate line on invoices.
- The data loader ignores extra trailing fields and defaults missing ones to 0 (`dbfile.c`; CODEMAP "Data files").
- Sample invoice 50232 (Greenway Taxis, 8% by hand) is the hand-given discount the ticket describes. It is history and stays as it is.

## User stories
- As a sales person, I want to mark a customer as a fleet customer when I add them, so the discount applies without me typing it.
- As a sales person, I want to mark an existing customer (for example Greenway Taxis) as a fleet customer, so the first fleet deal can use the feature.
- As a sales person, I want a fleet discount of 4% off the vehicle price to be applied automatically and to appear on its own line, so the customer and the manager can see it, and my own discount allowance stays free.
- As the Sales Director, I want fees (delivery, registration) left undiscounted.
- As any staff member, I want quotes and invoices for other customers, and all existing records, to stay exactly as they are.

## Acceptance criteria
In the examples, money is rounded as today (`rnd2`, round half up, to the penny).

- **R1 (mark when adding).** Given the Add Customer screen, when the user answers that the customer is a fleet customer, then the customer is saved as a fleet customer and the customer list and find screens show their type as `Fleet`.
- **R2 (mark an existing customer).** Given an existing customer who is not fleet, when the user marks them as fleet through the app, then the change is saved, the customer shows as `Fleet`, and all their other fields are unchanged.
- **R3 (one kind per customer).** A customer is exactly one of Retail, Trade or Fleet. A fleet customer gets no trade discount, and a trade customer gets no fleet discount.
- **R4 (fleet discount amount).** Given a quote for a fleet customer, then the fleet discount is `rnd2(list * 4%)`. Example: list 10000.00 gives 400.00; list 10495.00 gives 419.80.
- **R5 (own line on the quote).** Given a quote for a fleet customer, then it shows a line `Fleet discount` with the negative amount, in the place where the trade discount line appears for trade customers, and only when the amount is above 0. The customer line reads `(Fleet)`.
- **R6 (fees not discounted).** For a fleet customer the delivery (150.00) and registration (55.00) amounts are the same as for any other customer. VAT is calculated as today, on net price plus delivery, so it falls with the discount.
- **R7 (correct total).** Given a fleet customer, 0% salesman discount and no trade-in, list 10000.00 gives net 9600.00, VAT 1950.00 and total 11755.00; list 10495.00 gives net 10075.20, VAT 2045.04 and total 12325.24.
- **R8 (salesman discount still works).** Given a fleet customer and a salesman discount of p%, then the salesman discount is p% (clamped 0-15 as today) of list minus the fleet discount, and it appears on its own line as today. Example: list 10495.00, 8%: fleet 419.80, salesman 806.02, net 9269.18, VAT 1883.84, total 11358.02 with no trade-in.
- **R9 (trade-in).** The trade-in is subtracted from the total as entered, unchanged for fleet customers.
- **R10 (invoice).** Given a confirmed sale to a fleet customer, then the invoice is stored with the same total as the quote, and viewing it shows the fleet discount on its own line labelled `Fleet discount`. See open question Q1 for how the amount is stored.
- **R11 (non-fleet unchanged).** For a retail or trade customer, every quote, invoice preview and stored invoice, and the invoice view, is byte-identical to today for the same inputs, including the `Discounts -0.00` quirk (B10).
- **R12 (existing data loads).** `customers.dat`, `invoices.dat`, `stock.dat` and `next_ids.dat` in today's format load without conversion. Existing invoices display exactly as today.
- **R13 (files stay compatible).** A save made when there are no fleet customers and no fleet invoices writes the same bytes as today's program writes for the same data.
- **R14 (existing tests).** Every existing golden stays byte-identical, except those on screens that R1 and R2 deliberately change (the customer menu, the Add Customer prompts, and anything that scripts them). Each such golden is updated through the harness with the criterion cited in the commit.

## Scope
**In:** a fleet flag on customers (set when adding and for existing customers); the 4% fleet discount in the quote and sale; its own line on quote, invoice preview and invoice view; the displayed customer type; tests for all of the above; the matching docs (`docs/CODEMAP.md`, `docs/DECISIONS.md`).

**Out:**
- Changing the real `data/`: marking Greenway Taxis as fleet in production is done by staff through the new screen. The sample `data/` is not edited.
- Any change to the 10% trade discount, the 0-15% salesman clamp, VAT, delivery or registration rules.
- Rewriting or recalculating existing invoices, including 50232.
- Un-marking a fleet customer, deleting or editing other customer fields (not asked for; Q3).
- Fixing B1-B10 (recorded, not fixed). In particular B2 (empty phone shifts fields on reload) will also lose a fleet flag on such a customer, as it does for Trade today.
- Updating `README.md` and the in-app help text (both wrong in places already, and the help screen is pinned by a golden; Q4).

## Assumptions
Each one is an ambiguity in the ticket and the call made here. They are repeated in `docs/DECISIONS.md` when the design is approved.
- **A1.** "4% off the vehicle price" means 4% of the list price (the stock price), the same base as the trade discount, rounded with `rnd2`.
- **A2.** Fleet and trade do not stack (R3). The ticket does not mention a customer who is both; the file format has one type character.
- **A3.** The salesman percentage applies after the fleet discount (R8), as it does after the trade discount. The alternative (percentage of list) would give salesmen more room on fleet deals than on trade deals.
- **A4.** The rate is fixed at 4% in the program. The ticket gives no per-customer rate.
- **A5.** Greenway Taxis stays Retail in the sample data until staff change it in the app (Out of scope). Invoice 50232 keeps its hand-given 8%.
- **A6.** The quote line label is `Fleet discount`, shown only when above 0, to match the trade line. The percentage is not printed on it (the trade line does not print one either).
- **A7.** A fleet customer's quote may still be at a reserved vehicle and so on exactly as for other customers; nothing about vehicle rules changes.

## Open questions (to settle at this gate or the design gate)
- **Q1. Invoice storage.** The ticket wants the fleet discount as its own line on invoices, but a stored invoice holds one combined discount today. Options: (a) add a trailing `fleet_disc` field to `invoices.dat` (old data loads as 0; an old binary ignores it); (b) derive it from the customer's current type when viewing. I recommend (a), because (b) shows wrong figures if the customer's type changes later. Whatever is chosen, R11 and R12 must still hold. **Needs your answer.**
- **Q2. Changed prompts.** To mark a customer when adding, Add Customer needs one more question, and the existing customer needs a new menu action. Both change screens that today's goldens pin (R14). Is that acceptable? The alternative of avoiding it (for example a single new menu option "Add fleet customer") still changes the customer menu. **Needs your answer.**
- **Q3.** Should staff be able to un-mark a fleet customer (for a contract that ends)? Assumed no (Out).
- **Q4.** Should the README and help screen mention fleet? Assumed no (Out).

## Change log
- 2026-11-07: first draft.
