# Spec 002: characterisation harness: design

**Status:** approved

## Approach
A black-box golden-master harness in one Python file. It treats the program as a box that takes keystrokes and produces screens and data files. That needs no change to the C and works for any later binary (including the baseline, for spec 004).

### Layout
```
tests/
  golden.py               the harness (stdlib only)
  scenarios/NAME.txt      scripted keystrokes, one input line per line
  fixtures/data/*.dat     frozen copy of data/ at tag baseline
  golden/NAME/stdout.txt  approved screen output
  golden/NAME/exit_code.txt
  golden/NAME/data/X.dat  approved content of each .dat file the run changed
```

### Scenario files
One line of input per line. A blank line is ENTER. A line `---` starts a new run of the program on the same data (added in T4, see change log). Lines starting with `#` are comments (the first lines say what the scenario shows and which R-ID it serves). The program's menu numbers are in `main.c:517-531`. Every screen ends with "Press ENTER" (`screen.c:59-63`), so scripts need a blank line after each screen.

### How a scenario runs
1. Create a temp dir, copy `tests/fixtures/data` to `<tmp>/data` (the program reads `data/` relative to its working directory, `dbfile.c:13`).
2. Record today's date before.
3. Run `[binary]` with cwd = temp dir, stdin = the script, timeout 10 s, stdout and stderr captured.
4. Record today's date after. If it differs from "before" (midnight), run the scenario once more; if it still straddles, fail with a clear message.
5. Read all four `.dat` files. Keep those that differ from the fixture.
6. Normalise text: decode as latin-1 (lossless), replace today's date with `<TODAY>`, replace the byte `\x1b` with `<ESC>`.
7. Compare with `tests/golden/NAME/`, or write them in `--update` mode.

The program always ends at EOF with `exit(0)` (`screen.c:29-32`), so no scenario can wait for input forever; the timeout only guards against a hang.

### Command line
`python3 tests/golden.py [--bin PATH] [--update] [--selfcheck] [NAME...]`
- default binary `./dealerdesk`
- `--update` refuses when `CI` is set, and prints which approved files it wrote
- `--fail-on-stderr` fails a scenario if the program wrote anything to stderr (used for the ASan run, R15)
- `--selfcheck`: (a) copies the sources to a temp dir, changes `0.10` to `0.11` in `calc.c`, builds it, runs the suite against it, passes only if at least one scenario fails; (b) runs the suite with a fake binary that sleeps and passes only if every scenario reports a timeout, using a short timeout. (R14, R6)
- After running, it hashes the repo's `data/` before and after and fails if it differs (R1).

### Makefile
- `test`: depends on `all`, runs `python3 tests/golden.py`
- `test-asan`: depends on `asan`, runs `ASAN_OPTIONS=detect_leaks=1 python3 tests/golden.py --bin ./dealerdesk-asan --fail-on-stderr`
- `test-selfcheck`: runs `python3 tests/golden.py --selfcheck`
- `.PHONY` updated.

### Scenarios (about 28)
| R | Scenarios |
|---|---|
| R7 | `stock_list`, `stock_list_all`, `stock_add_vehicle`, `stock_find_plate_hit`, `stock_find_plate_miss`, `stock_change_price`, `stock_reserve_release` |
| R8 | `cust_list`, `cust_add_retail`, `cust_add_trade`, `cust_find`, `bug_B2_empty_phone` |
| R9 | `quote_retail`, `quote_retail_tradein`, `quote_trade`, `quote_salesman_8pct`, `quote_clamp_20pct`, `quote_negative_pct`, `quote_half_penny`, `quote_sold_vehicle`, `quote_no_vehicle`, `quote_no_customer` |
| R10 | `sell_retail_view`, `sell_cancelled`, `sell_trade_salesman_tradein` |
| R11 | `inv_list`, `inv_view_50230`, `inv_view_50231`, `inv_view_50232`, `inv_view_missing` |
| R12 | `help_screen`, `menu_invalid_option`, `eof_mid_screen` |

Scenario inputs are chosen from the sample data (`data/stock.dat`, `customers.dat`), e.g. vehicle 1008 with customers 2003 (retail), 2002 (trade), 2008 (Greenway Taxis, retail). The half-penny scenario uses a salesman 7.5% on a price where `rnd2` matters (rounding at `calc.c:36`).

### CI
Add steps to the existing job: `make test` and `make test-asan` on both compilers; `make test-selfcheck` on gcc only (it builds its own mutated binary with `CC`). The step "R4 make test placeholder" is replaced.

### .gitattributes
No change needed: goldens are plain text with LF and `<ESC>` tokens.

## Code touched
No `.c` or `.h`. `Makefile:test` (placeholder at the `test:` target), `.github/workflows/ci.yml` (R4 step), `docs/DECISIONS.md` (D9), spec 001 change log.

## Alternatives considered
- **pytest / a test framework:** adds a pip step to CI and a dependency for the reviewers; the harness is about 150 lines. Rejected (D9).
- **C unit tests of `calc_quote`:** needs test hooks or a separate build of the C, and says nothing about screens or saved files. Rejected; black-box covers `calc_quote` through the screens.
- **Expect/pty driver (`pexpect`):** simulates a terminal, which we don't need because the program reads plain stdin. More moving parts. Rejected.
- **Raw ESC bytes in goldens:** unreadable in a terminal and noisy in diffs. Replaced by `<ESC>` (A4).
- **Running scenarios on `data/` directly:** goldens would silently follow data edits. Rejected (A1).
- **Storing all four .dat files per scenario:** about 4 times the files to review for no extra information. Rejected (A3).
- **Re-deriving expected totals in the harness:** a second implementation of pricing would be tested against itself. Rejected; the goldens record real output and a human spot-checks totals (A7).

## Data and compatibility impact
None to the program or its data. `tests/fixtures/data` is a copy used read-only: the harness copies it before each run.

## Risks
- **Wrong keystrokes** produce a golden that records an error screen rather than the intended one. Mitigation: each golden is read when created, the scenario headers state the intent, and A7 spot checks.
- **Goldens that follow the bug.** Intended. They are named by bug ID and cited in CODEMAP.
- **Platform differences** (compilers, libc, locale). The date format and `printf` are locale-independent here (no `setlocale` call). CI runs gcc and clang on the same files to confirm.
- **Timezone at the day boundary**: handled by the before/after date check in step 4.
- **Stale approved files** after an intended change: `--update` is manual, refuses in CI, and each use must cite a criterion in the commit message.

## Change log
(none yet)
- 2026-11-07: scenario files may contain `---` lines that start a further program run on the same temp data. `stdout.txt` then holds `=== run N ===` sections and `exit_code.txt` one code per run; single-run output is unchanged. Reason: R8 requires showing that a Trade customer *reloads* as Retail (B2), which cannot be seen within one process. Found while writing the B2 scenario. Also useful for spec 004 (sell in one run, view the invoice after a reload).
