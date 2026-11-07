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
