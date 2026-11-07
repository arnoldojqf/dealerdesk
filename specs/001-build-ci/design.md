# Spec 001: build and CI: design

**Status:** implemented

## Approach
A small `Makefile`, two dotfiles and one workflow. No C changes.

### Makefile
- `CC = gcc` (a plain assignment, so `make CC=clang` overrides it; make's built-in default would be `cc`).
- `SRC = $(wildcard *.c)`, the same set as `*.c` in the brief's command.
- Targets, all `.PHONY` except the binaries:
  - `all` (default): `$(CC) -o dealerdesk $(SRC) -lm`, no extra flags, so it matches the brief command.
  - `warn`: `$(CC) -Wall -Wextra -o dealerdesk-warn $(SRC) -lm`.
  - `asan`: `$(CC) -fsanitize=address,undefined -g -o dealerdesk-asan $(SRC) -lm`.
  - `test`: prints `no tests yet (see specs/002)`, exits 0.
  - `clean`: `rm -f dealerdesk dealerdesk-warn dealerdesk-asan`.
- `all` is declared always-rebuild (phony). The project has five files, so incremental builds buy nothing and a stale binary is the failure we want to rule out.

### .gitignore
`dealerdesk`, `dealerdesk-warn`, `dealerdesk-asan`, `*.o`. Nothing under `data/` is ignored.

### .gitattributes
`* text=auto eol=lf`. The sample `.dat` files are already LF (`file` reports ASCII text), so the rule changes nothing today; it stops a Windows-side git from rewriting them to CRLF. Spec 002 will add `tests/golden/** -text` because goldens contain raw ANSI bytes.

### CI (`.github/workflows/ci.yml`)
- Triggers: `push` and `pull_request`.
- One job, matrix `cc: [gcc, clang]`, `ubuntu-latest`, `actions/checkout@v4`. Both compilers are preinstalled on the runner.
- Steps, each named with its criteria:
  1. `make CC=$cc` (R1, R6)
  2. `make CC=$cc warn` (R2)
  3. `make CC=$cc asan` (R3)
  4. Raw command into a different file, `$cc -o dealerdesk-raw *.c -lm`, then `cmp dealerdesk dealerdesk-raw` (R1)
  5. `make test` (R4, informational)
  6. `make clean`, then fail if any binary is left (R5)
  7. `test -z "$(git status --porcelain)"` after all builds (R7, R8)
  8. `git add --renormalize . && git diff --cached --quiet` (R9)
- Clang and gcc output differs, so the `cmp` always compares the same compiler with itself.

## Code touched
No `.c` or `.h` file. `README.md:29` only (the BUILD command line).

## Alternatives considered
- **CMake / Meson:** heavier than a five-file C program; reviewers would have to learn it. Rejected.
- **Plain shell script `build.sh`:** no `make test`/`make demo` target structure to grow into, and no CC override convention. Rejected.
- **Incremental `.o` build:** faster in theory, but adds object files and stale-state risk for a one-second build. Rejected.
- **`-Werror` now:** would break the build on any existing warning, and fixing warnings means changing C, which this spec forbids. Deferred; recorded as a next step.
- **Install clang locally:** requires sudo and is not needed. clang runs in CI (D10).

## Data and compatibility impact
None. No source, data or behaviour changes. `data/` is never touched by any target.

## Risks
- Clang may emit warnings gcc does not. `warn` does not fail on warnings, so CI stays green; they are recorded in the run log.
- The `cmp` check assumes the compiler is deterministic for identical input and flags, which holds for gcc and clang on this single build. If it proves flaky, the fallback is to compare `objdump -d` output instead, via a spec change.
- The matrix job could fail on the first push for an unforeseen runner reason. Mitigation: push the workflow on its own commit and read the run before building further.

## Change log
- 2026-11-07: CI step 4 also deletes `dealerdesk-raw` after the `cmp`. Reason: otherwise the R5 step (`ls dealerdesk*`) finds it and fails. Found by rereading the workflow before the first run.
