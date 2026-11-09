# NOTES

## What I changed, and why in this order

The ticket is small. The risk is changing a program with no tests, so I made changes safe first and shipped TICKET-142 last. Each step is a spec in `specs/` and has its own commits; `docs/PLAN.md` has the phases.

1. **Build and CI (spec 001).** `Makefile` (`make` is the same as the old `gcc` line, plus `warn` and `asan`), and a GitHub Actions job on gcc and clang. Cheapest step, and every later commit gets a green check.
2. **Golden-master harness (spec 002).** `tests/golden.py` replays keystroke scripts (`tests/scenarios/`) against a frozen copy of the sample data and compares screens and data files with approved output (`tests/golden/`). It never touches `data/`. `make test-selfcheck` proves the suite fails when behaviour changes. This is what lets me say "unchanged to the penny" with evidence.
3. **Agent setup (spec 003).** `CLAUDE.md` with hard rules (preserve bugs, never write `data/`, never push without asking), project permissions, a hook that runs `make warn` after every C edit, `/spec`, `/implement`, `/verify` commands and a read-only `spec-reviewer` agent. `make check-agent` checks the setup.
4. **TICKET-142 (spec 004).** Three approval gates (requirements, design, tasks), then eight tasks, tests first, one commit each.
5. **Delivery aids.** `make demo` shows a fleet quote and a fleet sale on a temp copy of the fixtures (D13).

The code is the truth: the README and help text disagree with it in places. Those are recorded as B1-B10 in `docs/CODEMAP.md` and left unfixed (rule 1, D8).

## Ticket against evidence

| Ticket criterion | Spec 004 | Proof |
|---|---|---|
| Mark customers fleet, new and existing | R1, R2 | `fleet_add_customer`, `fleet_mark_greenway`, `fleet_mark_refused` |
| Fleet line and correct total on a quote | R4-R9 | `fleet_quote_*` (hand-calculated figures in each scenario's comment) |
| Non-fleet unchanged, to the penny | R11, R13, R14 | every existing quote, sale and invoice golden byte-identical; only the five customer-menu goldens changed (new menu line) |
| Existing data loads, old invoices display | R12 | `inv_view_50230`-`50232`, `inv_list`, `fleet_sell_then_sell` (11- and 12-field lines in one file) |

Last check before this note: 47 tests pass on gcc and clang, plain and under ASan/UBSan, in CI. `/verify 004` found no failing criterion (`specs/004-fleet-discount/verify-report.md`).

## How I worked with the agent, and where it went wrong

Full list in `docs/agent-log.md`. The ones that taught me most:

- **"Zero warnings" that was a 404.** `gh` pointed at the upstream repo, returned an error, and my `grep -c warning:` printed 0. Caught because a second filter also returned nothing, so I read the raw output. An empty result is not evidence until the input is shown to be non-empty. Now `gh repo set-default` is set.
- **"Pass" marks on one-off checks.** The fresh-context reviewer found that spec 002 and spec 004 marked criteria "pass" on manual checks or indirect goldens. Fixed by automating the checks and adding T8 (a fleet invoice must survive a later save). A reviewer that did not write the code asks "could this check fail?" better than the author.
- **A one-space edit slipped into an untouched line** (`Net price` in the invoice view). Five existing goldens failed. I read the diff instead of approving a new golden.
- **Guard rails I assumed worked.** Settings written mid-session, a launch directory one level too high, an ask rule skipped by auto mode, and three `Write(...)` deny rules that never matched. Each was found by trying to break the rule, not by reading it. `CLAUDE.md` lists the limits (prefix rules are not a security boundary; `make CC=...` can carry a command).

## Assumptions (full wording: `docs/DECISIONS.md`)

- Fleet is stored as customer type `F` (D1): no file-format change, so rolling back to the old binary is safe. A customer is Retail, Trade or Fleet, never two.
- 4% is of the list price, rounded with `rnd2`, fixed in the program (A1, A4). VAT is applied after the discount, so the total is not "price minus 4%". It is VAT on a lower base (agent-log, 2026-11-07).
- The salesman percentage applies after the fleet discount, as it does after the trade discount (A3).
- A stored invoice keeps the fleet amount in an optional 12th field, written only when above 0 (D12), so a save with no fleet invoice is byte-identical to today's.
- Greenway Taxis stays Retail in the sample data until staff mark it in the app; invoice 50232 keeps its hand-given 8% (A5).
- A Trade customer cannot be marked fleet: it would silently swap the 10% trade discount for 4% (A8). There is no un-mark.

## What I would do next

- Run `/verify 001`: it is the only spec reviewed by hand only.
- Confirm that the `--update` ask rule fires in a plain interactive session (open item in `docs/PLAN.md`), and close the `make CC=...` gap.
- Decide with the owner which of B1-B10 to fix, each as its own spec.
- Add a flag or table for the fleet rate if the Sales Director wants per-customer rates.
- Install clang locally; today it only runs in CI (D10).
