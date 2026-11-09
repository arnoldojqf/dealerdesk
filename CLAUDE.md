# DealerDesk: agent instructions

Menu-driven C terminal app for car dealerships, in production for years. Work happens in two parts: make changes safe to deliver (specs 001-003, done), then ship TICKET-142, a fleet discount (`TICKET-142.md`, spec 004). The brief is `BRIEF.md`. **The code is the truth**: the in-app help and some code comments are wrong in places (`docs/CODEMAP.md`, B1-B10); the README was corrected under D15.

## Commands
Run from the repository root. The program reads and writes `data/`, so never run it for testing; use the harness.

| Do | Command |
|---|---|
| Build (same as `gcc -o dealerdesk *.c -lm`) | `make` |
| Build with warnings (baseline has zero) | `make warn` |
| Build with ASan and UBSan | `make asan` |
| Golden-master tests | `make test` |
| Same tests on the sanitizer build | `make test-asan` |
| Prove the tests catch a regression | `make test-selfcheck` |
| Check this agent setup | `make check-agent` |
| Restore the sample data (humans only) | `git checkout -- data` |
| Remove built binaries | `make clean` |

Other compiler: `make CC=clang`. CI (`.github/workflows/ci.yml`) runs all of the above on gcc and clang.

## Layout
Launch Claude Code from the repository root (`cd ~/src/dealerdesk && claude`). Project settings, hooks, commands and agents are read from the launch directory; from a parent directory none of the guard rails below are active.

- `main.c`, `calc.c`, `dbfile.c`, `screen.c` and their headers: the program (about 900 lines).
- `specs/`: one folder per piece of work, `specs/README.md` has the rules.
- `tests/golden.py`: the harness. `tests/scenarios/` keystroke scripts, `tests/golden/` approved output, `tests/fixtures/data/` frozen copy of the sample data.
- `docs/PLAN.md` (phases, spec index, plan change log), `docs/CODEMAP.md`, `docs/DECISIONS.md`, `docs/agent-log.md`.
- `.claude/settings.json` permissions and the build hook, `.claude/commands/` and `.claude/agents/` the workflow.

## What to know about the code (details and line numbers in `docs/CODEMAP.md`)
- Money is `double`, rounded with `rnd2` (round half up) for the discounts and VAT only; net and total are unrounded sums. Output is `%.2f`.
- Price build-up in `calc.c`: trade discount 10% of list (trade customers), salesman % (clamped 0-15) of list minus trade, VAT 20% of net plus delivery 150, registration 55, minus trade-in.
- Data files are pipe-delimited text; extra trailing fields are ignored by the loader. `strtok` collapses empty fields (B2). An invoice stores one combined `disc`.
- Every prompt reads through `read_line`, which exits 0 at end of input, so piped keystrokes always terminate.
- Quirks are pinned by tests on purpose, for example `Discounts -0.00` on an undiscounted invoice (B10).

## Spec workflow
No code without an approved spec. Read `specs/README.md`. Commands: `/spec <name>` drafts requirements, design and tasks in stages and stops at each gate; `/implement <spec>` works through `tasks.md` tests first with one commit per task; `/verify <spec>` runs the fresh-context `spec-reviewer` agent against every acceptance criterion. TICKET-142 has three separate gates (requirements, design, tasks). If a spec turns out to be wrong, stop, fix the spec, log the change with the reason, then continue.

## Tests and goldens
- Every acceptance criterion maps to an automated test whose name or comment cites the ID. Commit messages cite spec and task: `spec 004 T3: ...`.
- Goldens change only for an intended behaviour change, through `python3 tests/golden.py --update <scenario>` (the script does not ask: the confirmation is the Claude Code ask rule, which applies in default permission mode only, so `!` commands and auto mode skip it; the script itself refuses when `CI` is set). Never edit files under `tests/golden/` or `tests/fixtures/` by hand. The commit message names the criterion.
- When TICKET-142 lands, every quote, sale and invoice golden must stay byte-identical. Only the five customer-menu goldens may change, and only under spec 004 R14 (they show the new menu line).

## Hard rules
1. Preserve existing behaviour exactly, bugs included. Record bugs in `docs/CODEMAP.md`; fix one only if the owner agrees.
2. Never write to the real `data/`. `git status` must stay free of data changes.
3. Keep C changes minimal and do not reformat code you are not otherwise changing. The owner is new to C: before any commit that changes C, explain the diff line by line and wait.
4. Never push, force-push, change remotes, tag, or open a pull request without asking. Never open a pull request against `upstream` (the original repo). `origin` is the owner's public repo.
5. Small commits, tests passing at each one.
6. Ambiguity: make a reasonable call and record it in the spec or `docs/DECISIONS.md`, then tell the owner.
7. Verify before claiming: run it and show the output. An empty or zero result proves nothing until you know the input was not empty.
8. When you or the owner get something wrong and it is caught, add it to `docs/agent-log.md`.

## Guard rails and their limits
`.claude/settings.json` denies `git push`, `gh pr`, `gh repo`, remote changes, `rm -rf` and edits to `data/`, `tests/golden/` and `tests/fixtures/`, asks before `--update`, `git tag`, `git checkout`, `git reset` and `gh api`, and runs `make warn` after every `.c` or `.h` edit (exit 2 with the output if anything is wrong). These are prefix matches that guard against slips; they are **not a security boundary** (for example `bash -c "git push"` is not caught). A second gap: `make:*` is allowed and `make test-selfcheck CC=...` puts `CC` into a shell line, so it can carry any command past the ask rule. The settings set `defaultMode: default` so the ask rules apply even when the user-level mode is `auto`; this takes effect from the next session. Ask rules were shown live in default mode on 2026-11-08 (spec 003 T6 d). Rules 1-8 are the primary control.
