# Spec 001 verify report (2026-11-09)

Two runs of the `spec-reviewer` agent. The first could not run any command (its Bash calls were refused), so it was a static read and did not count; see `docs/agent-log.md`. The second, below, ran its commands. Its report is reproduced unchanged, followed by what was done about it.

## Reviewer report (second run, unchanged)

Review of specs/001-build-ci. R1 to R3, R5 to R9 and R11 are covered. R10 is only partly covered, and R4 is superseded. Every CI step is read-only inspected. I ran the equivalent commands locally and could not run CI. I did not run clang, because it is not installed.

I did not run `make check-agent`, because this spec is about build and CI, not the agent setup.

Commands run:
- `make test`: exit 0, 47 passed, 0 failed.
- `make test-asan`: exit 0, 47 passed, 0 failed.
- `make test-selfcheck`: exit 0, ends "selfcheck: ok".
- `make warn`: exit 0, no warnings printed.
- `make clean`, then `make`, then `cmp` against `gcc -o raw calc.c dbfile.c main.c screen.c -lm`: identical.
- `git status --porcelain`: empty after the builds.
- `git diff baseline c1143ff --stat -- '*.c' '*.h' data` (the spec 001 end commit): empty.

| Criterion | Evidence | Verdict | Note |
|---|---|---|---|
| R1 | CI step "001 R1 binary identical to the brief's command" runs `cmp dealerdesk dealerdesk-raw` on the same compiler. Local `cmp` of `make` against the raw gcc command was identical. The Makefile `all` has no extra flags. | covered | `cmp` would fail if flags or sources differed. |
| R2 | CI step "001 R2" runs `make warn \| tee` and then greps for `-Wall -Wextra`. Local `make warn` exited 0. | covered | The exit-0-with-warnings half is not tested, because the baseline has no warnings. The pipe has no `pipefail`, but GitHub's default bash shell sets it. |
| R3 | CI step "001 R3" runs `nm dealerdesk-asan` and greps for `__asan_init` and `__ubsan_handle`. | covered | Not run locally by me; `make test-asan` did build `dealerdesk-asan` and pass. |
| R4 | Superseded by spec 002. `make test` runs 47 scenarios. | superseded | Matches the traceability table. |
| R5 | CI step "001 R5" runs `make clean`, then `ls dealerdesk*` and `git status --porcelain`. Local `make clean` removed only the three binaries. | covered | A deleted tracked file under `data/` would fail the status check. |
| R6 | The CI matrix has a `clang` job. | partly covered | The workflow shows it; I could not run clang locally. The table's "pass" rests on run 42415644246 and run 42626459810, which I did not re-check with `gh`. |
| R7 | CI step "001 R7, R8" checks status after make, warn and asan, and again after clean. Locally, status was empty with binaries built. The C and data diff to c1143ff is empty. | covered | Because `.gitignore` hides the binaries, the status check cannot tell a stray tracked-file edit from a build artefact. It still fails on a modified tracked file, which is what the criterion needs. |
| R8 | Same CI step. `.gitignore` lists `dealerdesk`, `dealerdesk-warn`, `dealerdesk-asan` and `*.o`. Locally, built binaries did not show in `git status`. | covered | |
| R9 | `.gitattributes` is `* text=auto eol=lf`. CI step "001 R9" runs `git add --renormalize .` and then `git diff --cached --quiet`. | covered | I did not run it locally. My `--dry-run` listed every file, so it told me nothing. Both the dry-run and the real renormalize step would touch the index. |
| R10 | `ci.yml` triggers on push and pull_request, with a gcc and clang matrix. It runs make, warn, asan, the raw command, and the R1, R7 and R9 checks. `fail-fast` is false. | partly covered | A step failing makes its job fail, which is the default. Green runs are cited in the table but I did not verify them. |
| R11 | `git diff baseline HEAD -- README.md` shows exactly one changed line, the BUILD command. | covered (manual) | The justification for staying manual is plausible. A `git diff --stat`-style check could be automated. |

**Not covered by the spec**
- The Makefile has extra targets: `test`, `test-asan`, `test-selfcheck`, `check-agent`, `demo`. design.md's change log records them.
- `.gitignore` has an extra `.claude/settings.local.json` line, recorded in tasks.md.
- `git diff baseline` shows C changes in `calc.c`, `calc.h`, `dbfile.c`, `globals.h` and `main.c`, plus the fleet goldens. These belong to spec 004 and are not spec 001's. The "no C change" promise is verified only against c1143ff, so on current HEAD R7's "`.c`, `.h` and `data/` untouched" no longer holds literally.
- CI step order differs from design.md. This is recorded.

**Spec/code drift**
- requirements.md R10 says CI runs `make`, `make warn`, `make asan`, the raw command, and checks R1, R7 and R9. It does not list the later steps (golden tests, selfcheck, check-agent), which are in `ci.yml`. design.md's change log notes this, but the R10 text itself is unchanged.
- design.md describes `clean`, `test` and `all` as written at T2. The Makefile now has `test: all` running the golden suite, and `all` is not literally "always rebuild" in the way the design text suggests; it is `.PHONY`, which matches.
- tasks.md traceability row R1 cites the step name "R1 byte-identical". The workflow step is now "001 R1 binary identical to the brief's command", so the name is stale.
- Statuses read "implemented" in all three files, which matches the commits.

**Overclaims**
- The R10 row cites green runs by ID. I did not check them, and nothing in the repo proves them.
- The R6 row says "pass" on the clang job. Clang has never run locally. The row rests entirely on those CI runs.
- Requirements A3 says the baseline is warning-free. I confirmed that for gcc only.

**Verdict:** Spec 001 holds up. Every criterion has a test that could fail, and the local runs passed. The remaining weak points are the unverified R6 and R10 evidence, the stale R1 step name in the traceability table, and spec 004's C changes on HEAD.

## What was done about it

No criterion failed, so spec 001 is set to verified. Findings and responses:

- **R6, R10 "partly covered" / unverified run IDs:** the runs were checked with `gh` the same day. 42415644246 (659d345) shows gcc and clang green; 42626459810 (8113a38) and 42629508463 (324040e, the first run with the T6 steps) are green too. The IDs are now in the tasks.md R6 row.
- **Stale R1 step name:** tasks.md R1 row now uses the current name.
- **R10 text omits later CI steps:** a sentence pointing to the design.md change log was added to R10.
- **R7 "untouched" no longer literal on HEAD:** reworded to "this spec's commits", with the diff command that checks it.
- **A3 gcc only:** A3 now says so. Clang warnings are still unchecked locally.
- **R2 exit-0-with-warnings half untested, R9 not run locally by the reviewer, R11 manual:** accepted. The baseline has no warnings to test with, R9 runs in CI on every push, and R11 stays manual for the reason in the R11 row.
- **design.md T2 text vs the Makefile today:** accepted. The 2026-11-09 design.md change log entry says the current files are the source of truth.
