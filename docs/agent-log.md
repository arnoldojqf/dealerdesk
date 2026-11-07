# Agent log

Moments where the agent or the human got something wrong, and how it was caught. Raw material for NOTES.md.

## 2026-11-07: challenge summary omitted VAT behaviour
- What: the task summary said "4% off the vehicle price" and nothing about VAT. The README says VAT is on list price and delivery is VAT-exempt.
- Caught by: reading `calc.c:36-40`. The code applies VAT to (net + delivery), so a fleet discount also lowers VAT.
- Consequence: the fleet total cannot be estimated as "price minus 4%". Tests need hand-calculated expected values.
- Also: README and help text contradict the code in several places (B1-B6 in CODEMAP). Code is treated as the truth.

## 2026-11-07: CI step would have failed (spec 001 T3)
- What: the "R5 clean removes the binaries" step checked `ls dealerdesk*`, but the earlier `cmp` step leaves `dealerdesk-raw`, which `make clean` does not remove and the glob matches. The step would have failed on the first run.
- Caught by: rereading my own workflow before committing, then replaying its shell steps locally in order.
- Fix: delete `dealerdesk-raw` right after the `cmp`. First CI run (42415644246) went green on gcc and clang.
- Also: my first R2 evidence printed `$?` of `tail`, not `make`. Re-ran `make warn` on its own to get the real exit status.

## 2026-11-07: `gh` silently pointed at the upstream repo (phase 3)
- What: `gh run view` resolved the repository to `felipeamarante/dealerdesk` (the `upstream` remote) and returned a 404. My `grep -c warning:` over that output printed 0, which I had reported as "zero compiler warnings" for the first CI run.
- Caught by: a second filter returning nothing at all, so I looked at the raw output and saw the 404 and the wrong repo.
- Fix: re-read the real logs with `-R arnoldojqf/dealerdesk` (the 0 warnings claim held: 338 log lines, 0 matches) and ran `gh repo set-default arnoldojqf/dealerdesk` so no `gh` command can default to upstream (rule: never open a PR against it).
- Lesson: an empty or zero result from a filter is not evidence until the input is shown to be non-empty.

## 2026-11-07: scenario design drift caught while writing tests (spec 002)
- What: the spec assumed B2 (empty phone) could be shown in one program run, and that `stock_list` alone was enough for the self-check.
- Caught by: writing the scenarios. B2 only appears after a reload; the 11% mutation is invisible without a trade-customer quote.
- Fix: both recorded in the spec change-logs (`---` run separator; `quote_trade` moved to T2). The self-check was shown to fail when no sensitive scenario exists.
