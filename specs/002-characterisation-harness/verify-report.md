# Verify report: spec 002 (characterisation harness)

**Date:** 2026-11-07
**How it was produced:** `/verify 002`, fallback path (spec 003 A6). The `spec-reviewer` agent type was not loaded in the session that created `.claude/agents/`, so a general-purpose subagent in a fresh context was told to read `.claude/agents/spec-reviewer.md` and follow it exactly, and was given only the spec folder path. The role is read-only by instruction; the fallback agent had the general-purpose tool set, so that restriction rested on its instructions rather than on a tool list. The report below is the agent's output, unedited. Treat it as model output: findings were checked before acting (see Disposition).

## Reviewer report

**Evidence run (repo root):**
- `make test`: 34 passed, 0 failed, exit 0.
- `make test-asan`: 34 passed, 0 failed, exit 0.
- `make test-selfcheck`: the 11% mutant fails `quote_trade` and `sell_trade_salesman_tradein`. The hanging binary fails with "timed out after 1s". Output ends "selfcheck: ok", exit 0.
- `git status --porcelain` is empty.
- `git diff baseline -- '*.c' '*.h' data` is empty (0 lines).
- `diff -r data tests/fixtures/data` shows no difference.
- I did not run `make check-agent`, because the spec does not involve the agent setup. I did not run `--update`, because the role is read-only. My first command included a `CI=1 --update` probe and the permission system denied it.
- I did not run clang (not installed locally) or inspect the CI run (no network).

| Criterion | Evidence | Verdict | Note |
|---|---|---|---|
| R1 isolation | `hash_data()` before and after in `main()` (golden.py), plus `git status` clean after the runs | covered | The harness hash covers only the 4 `.dat` files in `data/`. The `git status` part is not enforced by the harness itself, only by a CI step. |
| R2 capture | `run_once` captures stdout, exit code, stderr and changed `.dat` files; 34 scenarios pass | partly covered | stderr is not stored in goldens or compared. It is checked only under `--fail-on-stderr`, which is used only for the ASan run. A stderr regression in `make test` would go unnoticed. |
| R3 determinism | `<TODAY>` and `<ESC>` masks in `normalise`; the `sell_*` goldens | partly covered | No automated test runs the suite twice and compares. The traceability row cites "two identical consecutive runs", which is a manual claim. |
| R4 comparison | `run_suite` prints a unified diff via `diff()` naming the scenario and file; the selfcheck mutation fails `quote_trade` | covered | The "tamper a golden" proof in T1 was manual. The selfcheck exercises the fail path. |
| R5 approval | `main()` refuses `--update` when `CI` is set; the missing-golden message is in `run_suite` | partly covered | The code exists, but no automated test. The traceability row says "(T1)", a one-off manual check. I did not run it because the role forbids `--update`. |
| R6 no hangs | Selfcheck hang part: "FAIL bug_B2_empty_phone: timed out after 1s", exit 0 | covered | It runs only the first scenario (`names[:1]`). The timeout path returns early before `--fail-on-stderr`. |
| R7 stock | The 7 `stock_*` scenarios exist and pass. `stock_add_vehicle` and `stock_change_price` hold changed `.dat` goldens. | covered | The scenarios and goldens exist. I did not read every golden against the program. |
| R8 customers | `cust_list`, `cust_add_retail`, `cust_add_trade`, `cust_find`, `bug_B2_empty_phone` all pass | covered | The traceability row says "`cust_*` (4)", which matches. |
| R9 quotes | The 10 listed `quote_*` scenarios exist and pass, including `quote_half_penny`, `quote_clamp_20pct` and `quote_negative_pct`. | covered | `quote_reserved_vehicle` is an extra scenario (see below). So there are 11 `quote_*`, not 10. |
| R10 sales | `sell_retail_view`, `sell_cancelled`, `sell_trade_salesman_tradein` pass | covered | `sell_retail_view` has `invoices.dat`, `next_ids.dat` and `stock.dat` goldens. `sell_cancelled` has none, so it correctly stores no data file. |
| R11 invoices | `inv_list`, `inv_view_50230`, `inv_view_50231`, `inv_view_50232`, `inv_view_missing` | covered | |
| R12 menus | `help_screen`, `menu_invalid_option`, `eof_mid_screen` pass | covered | |
| R13 bugs kept | `bug_B2_empty_phone` plus a two-run scenario | covered | Only B2 is captured as a bug-named scenario. The criterion's text only requires naming by ID for those that capture a bug, so this is acceptable. B10 is pinned inside other goldens without a B10-named scenario. |
| R14 regression detected | `make test-selfcheck`: 2 scenarios fail under the 11% mutant | covered | The mutation relies on the literal `list * 0.10` in `calc.c` (assert in `selfcheck()`). It would break loudly if that line is refactored. |
| R15 any binary | `--bin` option; `make test-asan` passes with `--fail-on-stderr` | covered | The "fake-stderr binary check" in the traceability row has no committed test. It was manual. |
| R16 CI | `.github/workflows/ci.yml` has `make test`, `make test-asan` on both compilers and `test-selfcheck` on gcc only | partly covered | The config matches the criterion. The cited run (42417079234) and the clang results are unverifiable here. |
| R17 no code change | `git diff baseline -- '*.c' '*.h' data` is empty | covered | |

**Not covered by the spec**
- `quote_reserved_vehicle` (scenario and golden) has no criterion. R9 lists only sold, not-found and no-customer refusals.
- The diff against `baseline` also holds work outside spec 002: specs 001 and 003, the `.claude/` setup, `scripts/check-agent-setup.py`, `CLAUDE.md`, `docs/*`, `.gitignore`, `.gitattributes` and the `README.md` edit. Those belong to other specs, so this is not an issue for 002.
- The multi-run `---` separator and the `=== run N ===` output format are not in any R-criterion. They are logged only in the design change log and are used by `bug_B2_empty_phone`.

**Spec/code drift**
- design.md says the suite has "about 28" scenarios and R2 in tasks.md says 34. The actual count is 34, and the design table lists 33 names. `quote_reserved_vehicle` is missing from the design's R9 row, and the traceability says `quote_*` (10), but there are 11.
- `design.md` and `requirements.md` both end their Change log with "(none yet)" followed by real entries. `requirements.md` has no entry for the `---` multi-run feature, which changes the scenario format R2 relies on. `tasks.md` has no entry for `quote_reserved_vehicle` or the 34-vs-28 count.
- design.md says the CI step "R4 make test placeholder" is replaced. The spec 001 change log records it, and the CI file now has the golden steps. Consistent.
- design.md's selfcheck step says to hash `data/` before and after. The code does this in `main()` for normal runs only, not for `--selfcheck`.
- design.md's "Code touched" omits `scripts/` and the reviewer-agent files, which is fine, but it mentions a ".gitattributes no change needed" line. A `.gitattributes` change exists in the diff (1 line), though it is attributed to spec 001, so no issue.

**Overclaims**
- Traceability R3 ("two identical consecutive `make test` runs") and R5 ("`CI=1 --update` refusal and missing-golden message") are marked "pass" with only manual one-time checks. No committed automated test backs them. The R15 "fake-stderr binary check" has the same problem.
- R2 is marked "pass", but stderr is not captured into the goldens (see table).
- R16 and R14 cite CI run 42417079234. I could not verify it.
- T1's proof ("deleting one line of the golden makes it fail") is a manual step with no committed test.

**Verdict:** Core criteria are covered: 34/34 pass on gcc and ASan, the selfcheck catches both a regression and a hang, and there is no code or data drift. R2, R3, R5 and R16 are only partly covered or rely on manual checks, and the spec text has not been updated for the 34-scenario set, `quote_reserved_vehicle` and the multi-run format.

## Disposition (author, same day)

| Finding | Checked | Action |
|---|---|---|
| R2: stderr only enforced under `--fail-on-stderr` | True: `fail_on_stderr` was a flag used only by `make test-asan`. | **Fixed.** Any stderr output now fails a scenario in every run. `make test-selfcheck` proves it with a wrapper that writes to stderr while stdout stays identical. |
| R3: determinism only a manual claim | True. | **Fixed.** Self-check runs `sell_retail_view` twice and requires identical output with `<TODAY>` present. |
| R4: tamper check manual | True (the mutation check covered the failing path, the tamper check was manual). | **Fixed.** Self-check tampers a temp copy of the goldens and requires a failure. The real goldens are not written. |
| R5: `--update` refusal and missing golden manual | True. | **Fixed.** Self-check runs `--update` with `CI=1` as a subprocess, requires exit 2 and an unchanged golden, and requires a failure for an empty golden folder. |
| R15: fake-stderr check manual | True. | **Fixed**, same check as R2. |
| Spec drift: 28 vs 34, `quote_reserved_vehicle`, `---` | True. | **Fixed** in requirements, design and tasks, each with a dated change-log entry (spec 002 T10). |
| R1: `git status` cleanliness enforced by CI only | True, and intended: the harness hashes `data/`; CI checks the tree. | **Accepted.** No change. |
| R6: timeout test runs one scenario only | True. | **Accepted.** One scenario proves the mechanism. |
| R14: mutation depends on literal `list * 0.10` | True. | **Accepted.** It asserts loudly if the line moves. Documented in the design change log. |
| `--selfcheck` does not hash `data/` | True. | **Accepted.** It never touches the real data directory. Documented. |
| R13: B10 pinned without a B10-named scenario | True. | **Accepted.** Pinned by `sell_retail_view` and noted in `docs/CODEMAP.md`. |
| R16 / R14 CI run "unverifiable" | The reviewer had no network. The author read run 42417079234 (gcc and clang, 34/34 each, self-check ok). | **No change**, but see the note below. |
| "Permission system denied my `CI=1 --update` probe" | Not reproducible or verifiable by the author. The probe would have asked under the `ask` rule in `.claude/settings.json`. Whether the denial came from that rule, from the subagent running without a way to answer a prompt, or from something else is unknown. | **Recorded, not used as evidence** for spec 003 R4. The live proofs in spec 003 T6 are still pending a new session. |
| Out-of-scope diff (specs 001, 003, docs, config) | Correct, and not a spec 002 matter. | None. |

Note on the CI row: the fixes above change `tests/golden.py`, the self-check and spec text, so the cited run no longer describes the final state. A new run is needed after the push and will be recorded in `tasks.md`.

## Lessons for the process
- A "pass" resting on a manual check I ran once is worth much less than one a committed test backs. The reviewer found three of these in work I considered finished. The traceability table now says "manual" where that is the truth.
- The reviewer was right to call stderr capture a partial pass: the code captured it but only the sanitizer run acted on it.
