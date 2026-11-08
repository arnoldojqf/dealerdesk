# Verify report: spec 004 (fleet discount, TICKET-142)

**Date:** 2026-11-08
**How it was produced:** `/verify 004`. The `spec-reviewer` agent type (read-only tools: Read, Grep, Glob, Bash) was launched in a fresh context and given only the spec folder path, with no description of the implementation. The report below is the agent's output, unedited. Treat it as model output: its findings were checked before acting (see Disposition). The review ran on commit `962df7d` (46 tests); task T8 was added afterwards.

## Reviewer report

**Review of specs/004-fleet-discount**

**Evidence run**
- `make test`: 46 passed, 0 failed, exit 0.
- `make test-asan`: 46 passed, 0 failed.
- `make test-selfcheck`: "selfcheck: ok".
- `make check-agent`: "agent setup ok".
- `make warn`: clean, no output besides the compile line.
- `git status`: clean.
- `git diff baseline -- data`: empty.

**Diff**
- The baseline diff of `*.c` and `*.h` touches `calc.c`, `calc.h`, `dbfile.c`, `globals.h` and `main.c`: 69 insertions, 9 deletions.
- I read the whole C diff. It matches design.md, with no stray reformatting.
- `git diff f8e6762 -- tests/golden`, excluding `fleet_*`, shows only the five R14 goldens: `bug_B2_empty_phone`, `cust_add_retail`, `cust_add_trade`, `cust_find` and `cust_list`.
  - Four of them gain only the `4. Mark customer as fleet` menu line (`cust_find` and `cust_list` I did not open; their diff stats show 2 lines each).
  - `cust_add_retail` also gains the `Fleet customer (Y/N)?` prompt.
  - No quote, sale, invoice or stock golden changed.

| Criterion | Evidence | Verdict | Note |
|---|---|---|---|
| R1 | `fleet_add_customer`. Its golden shows the new prompt and `Fleet` in the list; I did not open the find screen or the `customers.dat` ending `\|F`. | covered | The scenario fails without the prompt, because the keystrokes would shift. |
| R2 | `fleet_mark_greenway` (mark, already fleet, reload) and `fleet_mark_refused` (Trade refused, unknown ID, N answer). | covered | I read the scenario headers and the C branches. I did not open the `fleet_mark_*` goldens. |
| R3 | `fleet_mark_refused`, `fleet_quote_1002` (no Trade line), `fleet_quote_trade_unchanged`, `quote_trade`. | covered | The C code guards the two discounts independently by type. |
| R4 | `fleet_quote_10000`, `fleet_quote_10495`, `fleet_quote_rounding` (400.01 from 400.0052). | covered | I did not open the quote goldens; I checked the figures only against the spec's hand figures and the `fleet_sell_view` golden. |
| R5 | `fleet_quote_1002`. | covered | The golden has the `(Fleet)` customer line. |
| R6 | Delivery, registration and VAT lines in the `fleet_quote_*` goldens. | covered | The VAT formula is untouched in `calc.c`. |
| R7 | `fleet_quote_10000` and `fleet_quote_10495`. | covered | The figures in the golden match the spec. |
| R8 | `fleet_quote_10495` at 8%, and `fleet_sell_view` (844.42 salesman discount). | covered | The salesman base is now `list - trade - fleet`. |
| R9 | `fleet_quote_tradein` and `fleet_sell_view`. | covered | |
| R10 | `fleet_sell_view`: the 12th field `\|439.80` is stored, and the view shows both the Fleet discount and Discounts lines. `fleet_sell_no_salesman`: no Discounts line, reload. | covered | I read only the `fleet_sell_view` golden (invoice view and list) and the `fleet_sell_no_salesman` scenario header. |
| R11 | All existing quote, sale and invoice goldens are byte-identical and pass. | covered | Passing under both gcc and ASan is proof. The clang run is pending (CI after push), as the spec says. |
| R12 | `inv_view_50230` to `50232`, `inv_list`, and the reloads in the two fleet sell scenarios. | covered | The invoice list mixes 11-field and 12-field lines. |
| R13 | Data files in the existing sale and add-customer goldens are unchanged. | partly covered | No test targets R13. It is covered only indirectly: no non-fleet golden changed. That does exercise the `fleet_disc == 0` save branch, but only via a handful of scenarios. |
| R14 | Exactly the five named goldens changed, and the diff is only the intended lines. | covered | It is checked by the T7 diff stat, not by an automated test. That is acceptable, since it is a process criterion. |

**Not covered by the spec**
- The screen title `Mark Customer as Fleet` and the message wordings were chosen in code. The tasks change log records this.
- A Retail-only guard: `c.type == 'R' && confirm(...)` in `add_customer`. This is equivalent to the design.
- `fleet_B2_empty_phone` (Fleet reloads as Retail) pins a bug on purpose. It is in the spec as R-b.
- Nothing else surprising.

**Spec/code drift**
- The Status line in `tasks.md` says "`/verify 004` and the clang CI run pending". That is still accurate now.
- The design's "Code touched" line numbers are from before the change, which is expected.
- Not drift: `docs/CODEMAP.md` carries current line numbers in its fleet section, but I only spot-checked it.

**Overclaims**
- The R13 row in `tasks.md` is marked "pass", but no scenario shows a no-fleet save writing the same bytes. It rests on existing goldens that happen to include data files. That is weak but real evidence.
- R14 and R11 depend on the T7 manual diff stat. The "pass" is fair.
- Nothing else I could find.

**Verdict:** All 14 criteria have working automated tests or equivalent evidence, with 46 of 46 passing on gcc and ASan, and the diff stays within the spec. The remaining gaps are that R13 has only indirect coverage and the clang run is outstanding.

## Disposition (author, same day)

| Finding | Checked | Action |
|---|---|---|
| R13 "partly covered": no test targets R13; "pass" is an overclaim | Partly true. `sell_retail_view` re-saves the three old 11-field invoice lines, `cust_add_trade` covers `customers.dat`, and the sale golden covers `stock.dat` and `next_ids.dat`, all by byte comparison on every run. They are real automated comparisons, but they were not written for R13 and the table did not say so. | **Wording fixed.** The R13 row now says the evidence is existing goldens not written for R13, and "indirect". |
| (Found while checking the note above, not raised by the reviewer.) No test loads a 12-field invoice line and then saves again | True. `fleet_sell_view` and `fleet_sell_no_salesman` reload only to view. A saver that dropped the fleet field on a later sale would have passed all 46 tests. | **Fixed: T8, `fleet_sell_then_sell`** (test only, no C). Shown to fail on a throwaway saver without the 12th-field write: 50233 loses `\|439.80` and the view shows `Discounts -439.80` with no Fleet line. R10 and R12 rows cite it. |
| R11 and R14 rest partly on the T7 manual diff stat | True. | **Accepted.** The rows now say "automated goldens plus the manual T7 diff stat" (R11) and "manual T7 diff stat, a process criterion" (R14). |
| Goldens and screens the reviewer did not open (`cust_find`, `cust_list`, `fleet_mark_*`, the quote goldens, the find screen for R1) | True for the reviewer. The author read each against the hand figures while approving it (T2 to T5). | **Accepted.** The suite passes and the reviewer ran the evidence commands itself. |
| Screen title `Mark Customer as Fleet` and the message wording chosen in code | True, and already recorded in the `tasks.md` change log (the design left them open). | **Accepted.** No change. |
| Retail-only guard in `add_customer` | Equivalent to the design. | None. |
| clang not run | Expected: it runs only in CI after a push, which is the owner's decision (rule 4, D10). | **Open.** Record the CI run in `tasks.md` after the push. |
| `docs/CODEMAP.md` line numbers only spot-checked | The author checked every number cited in the fleet section against the files at T6. | None. |

## Lessons for the process
- A table that says "pass" should say whether the test was written for that criterion. R13 was true but indirect.
- A feature that adds an optional field needs a load, save, load round trip, not only a load and a view. The reviewer's R13 note led to a gap it had not named.
