# Spec 001: build and CI: requirements

**Review mode:** bundled. `requirements.md`, `design.md` and `tasks.md` are reviewed in one go.
**Status:** implemented

## Problem
There is no reliable build and no CI. The only build instruction is a README line that is wrong (`README.md:29` names `report.c`, omits `calc.c` and `-lm`). Nothing checks a commit. Every later spec needs a one-command build, warning and sanitizer builds, and a CI check on each commit.

## User stories
- As a maintainer, I run `make` and get exactly the binary the brief's command produces.
- As a maintainer, I can see compiler warnings and run a sanitizer build without changing any C.
- As a reviewer, I see a green or red check on every commit, built by gcc and clang.

## Acceptance criteria
- **R1.** Given a clean checkout, when I run `make`, then `./dealerdesk` is built with the command `gcc -o dealerdesk <all .c files> -lm` and is byte-identical to the binary from the brief's command `gcc -o dealerdesk *.c -lm`.
- **R2.** When I run `make warn`, the sources compile with `-Wall -Wextra`, warnings are printed, and the exit status is 0 even if there are warnings (warnings are not yet errors).
- **R3.** When I run `make asan`, a binary `dealerdesk-asan` is built with AddressSanitizer and UndefinedBehaviorSanitizer.
- **R4.** *(Superseded by spec 002 T1, 2026-11-07; see the change log.)* When I run `make test`, it exits 0 and says there are no tests yet. (Real tests arrive with spec 002.)
- **R5.** When I run `make clean`, all built binaries are removed and nothing else (in particular nothing under `data/`).
- **R6.** When I run `make CC=clang`, the same targets work with clang.
- **R7.** Building changes no tracked file: `git status --porcelain` is empty after `make`, `make warn`, `make asan` and `make clean`, and `.c`, `.h` and `data/` are untouched by this spec.
- **R8.** Built binaries are ignored by git (`.gitignore`).
- **R9.** Line endings are LF: `.gitattributes` sets `* text=auto eol=lf`, and `git add --renormalize .` changes no existing file.
- **R10.** On every push and pull request, a GitHub Actions workflow runs on a gcc and a clang job: `make`, `make warn`, `make asan`, the brief's raw command, and checks R1, R7 and R9. The workflow fails if any step fails.
- **R11.** The README BUILD command is corrected to the real command, and no other line of the README changes.

## Scope
**In:** `Makefile`, `.gitignore`, `.gitattributes`, `.github/workflows/ci.yml`, one line of `README.md`.
**Out:** any C change; the test harness (spec 002); making warnings fatal; clang installed locally; the other README errors (B1, B3, B4, B6 data path), which are only recorded; Windows builds.

## Open questions and assumptions
- A1. `make warn` and `make asan` use their own output names (`dealerdesk-warn`, `dealerdesk-asan`) so they never overwrite the plain build.
- A2. Only the README build line is fixed. Staff may read the README, and the other errors describe behaviour, so correcting them is a visible change and out of scope (decision D8).
- A3. Whether `gcc -Wall -Wextra` is warning-free on the baseline was only seen on gcc 15 locally. clang results are unknown until CI runs. Warnings are recorded, not fixed.
- A4. `make test` is a placeholder that CI does not call yet.

## Change log
- 2026-11-07: R4 superseded by spec 002 T1: `make test` now runs the golden-master suite instead of printing a placeholder. Reason: that is what the placeholder was for. Its coverage is now spec 002 R15/R16. (Also recorded in design.md.)
- 2026-11-09: after `/verify 001`, CI checks for R2, R3, R5 and R7 strengthened (tasks.md T6). Criteria unchanged.
