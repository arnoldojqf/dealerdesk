# Spec 002: characterisation harness: requirements

**Review mode:** bundled. `requirements.md`, `design.md` and `tasks.md` are reviewed in one go.
**Status:** implemented

## Problem
There are no tests. Any change to this program, including TICKET-142, can silently alter what staff see or what gets saved. We need a safety net that records today's behaviour, bugs included, and fails when it changes.

## User stories
- As a maintainer, I run `make test` and learn within seconds whether any screen or saved file changed.
- As a reviewer, I can read an approved output file and see exactly what the program printed and saved.
- As the author of TICKET-142, I can prove non-fleet output is unchanged to the penny, because those goldens stay byte-identical.

## Principle
This is a **characterisation** suite. It records what the program does now, not what it should do. A "wrong" behaviour (see bugs B1-B9 in `docs/CODEMAP.md`) is recorded as-is and named after its bug ID. Nothing is fixed here.

## Acceptance criteria
- **R1 (isolation).** Given any run of the suite, when it finishes, then the repository's `data/` directory is byte-for-byte unchanged and `git status --porcelain` is empty. Each scenario runs the binary with a temporary directory as its working directory, holding a copy of the fixture data.
- **R2 (capture).** For each scenario the suite feeds the scripted keystrokes on stdin, with a timeout, and captures stdout, the exit code, stderr, and every `.dat` file the run changed.
- **R3 (determinism).** Given two consecutive runs on the same binary, both produce identical captured output. Today's date (the only time dependence, `main.c:395-396`) is masked as `<TODAY>`, and the escape character in screen-clear codes is shown as `<ESC>`.
- **R4 (comparison).** When captured output equals the approved files in `tests/golden/<scenario>/`, the suite exits 0 and prints a pass summary. When anything differs, it exits non-zero and prints a unified diff that names the scenario and the file.
- **R5 (approval).** `--update` rewrites approved files from the current output. It refuses to run when the `CI` environment variable is set. A scenario with no approved files yet fails with a message pointing to `--update`.
- **R6 (no hangs).** If the binary does not finish within the timeout, the scenario fails with a timeout message and the suite still finishes.
- **R7 (stock).** Scenarios record: list stock, list all vehicles, add vehicle, find by plate (hit and miss), change price, reserve and release.
- **R8 (customers).** Scenarios record: list, add retail, add trade, find customer, and the empty-phone bug B2 (a Trade customer reloads as Retail).
- **R9 (quotes).** Scenarios record: retail quote without and with trade-in, trade-customer quote, salesman discount, discount clamped at 15% (input 20), negative discount treated as 0, a discount that lands on a half-penny, and the refusals (vehicle sold, vehicle not found, customer not found).
- **R10 (sales).** Scenarios record: a confirmed sale (new invoice line in `invoices.dat`, vehicle becomes sold, `next_ids.dat` advanced) followed by viewing that invoice, a cancelled sale (nothing saved), and a sale combining trade customer, salesman discount and trade-in.
- **R11 (invoices).** Scenarios record: list invoices, view each of the three existing invoices (50230, 50231, 50232), and view a missing invoice.
- **R12 (menus).** Scenarios record: the help screen, an invalid menu option, and end of input in the middle of a screen (exit code 0, no further output).
- **R13 (bugs kept).** Every scenario that captures a known bug is named with its ID (e.g. `bug_B2_...`) and its approved output contains the buggy result. Nothing in this spec changes behaviour.
- **R14 (regression detected).** `make test-selfcheck` builds a deliberately altered copy of the program (trade discount 10% changed to 11%) and passes only if the suite reports at least one failing scenario. It also checks a binary that hangs fails with a timeout (R6).
- **R15 (any binary).** `--bin PATH` runs the suite against another binary. `make test` uses the gcc build; `make test-asan` uses `dealerdesk-asan` and also fails if anything is written to stderr.
- **R16 (CI).** The CI workflow runs `make test`, `make test-asan` and `make test-selfcheck` on gcc, and `make test` and `make test-asan` on clang, using the same approved files for both compilers.
- **R17 (no code change).** No `.c` or `.h` file changes. Existing sample data in `data/` is untouched.

## Scope
**In:** `tests/golden.py`, `tests/scenarios/*.txt`, `tests/golden/**`, `tests/fixtures/data/**`, Makefile targets `test`, `test-asan`, `test-selfcheck`, CI steps, `.gitattributes` if needed, and updating spec 001 R4 (see assumptions).
**Out:** fixing any bug; unit tests of C functions; comparing the baseline and new binaries (spec 004); random or differential testing (a stretch goal in spec 004); coverage metrics; Windows.

## Open questions and assumptions
- **A1 (recommended call).** Scenarios run on a frozen copy of the sample data in `tests/fixtures/data/`, not on `data/`. Reason: TICKET-142 or a future edit might legitimately change `data/`, and the goldens must not silently follow it. The fixture equals `data/` at the `baseline` tag, which also makes it the "existing data files" for the compatibility criteria in spec 004. Cost: two copies of 4 small files.
- **A2.** Spec 001's R4 ("`make test` says no tests yet") is superseded by this spec. It is recorded in spec 001's change log, and the CI step is replaced.
- **A3.** Only .dat files whose content changed are stored in a golden folder. A file not stored is asserted to equal the fixture.
- **A4.** Goldens are stored as text with `<ESC>` in place of the escape byte, so they can be read in a terminal and reviewed in a diff. This differs from the earlier plan (raw bytes); recorded in `docs/DECISIONS.md` D9.
- **A5.** Output is compared as exact bytes after masking. Floating point formatting is identical across gcc, clang and ASan on x86-64; CI will confirm.
- **A6.** Python 3 standard library only, no third-party packages.
- **A7.** Each golden is reviewed by a human when created, and at least three totals are recomputed independently (throwaway script, not committed) before they are approved. Without that, a golden could enshrine a typo in a scenario.

## Change log
(none yet)
