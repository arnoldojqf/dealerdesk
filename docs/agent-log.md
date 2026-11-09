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

## 2026-11-07: assumed settings apply the moment they are written (spec 003)
- What: I wrote `.claude/settings.json` (deny `git push`, build hook) and planned to prove the rules in the same session. A `git push --dry-run origin master` ran unblocked and a broken scratch `.c` produced no hook feedback.
- Caught by: attempting the proof (T6) before claiming it. I chose a dry run for the push and skipped the golden-edit attempt, because an unenforced deny rule would have changed a golden.
- Consequence: nothing was pushed (`origin/master` stayed at 82d74b5) and nothing was modified. The scripted check still proves the hook script and the rule text. Enforcement is marked pending in the spec, to be shown in a fresh session.
- Likely cause (not verified): settings and hooks are read at session start.
- Update (later the same day): wrong cause. A session launched from the repo root enforced the deny rules (T6 a, b), so the launch directory was the problem.

## 2026-11-07: allow rule was broader than the spec, so `--update` was not prompted (spec 003 T6)
- What: R5 says the harness is allowed "without `--update`", but `settings.json` allowed `Bash(python3 tests/golden.py:*)`, which also matches `--update`. In the live proof `--update` ran with no prompt.
- Caught by: running T6 d instead of trusting that the rule text was present (`make check-agent` only checked the text).
- Fix: allow only the exact commands `golden.py` and `golden.py --selfcheck`. Not yet separated from `defaultMode: auto`; re-run in an interactive session.
- Also: the build hook uses `$CLAUDE_PROJECT_DIR`, so it cannot be shown from a background worktree. I first read the silence as "hook broken" and checked before claiming either way.

## 2026-11-07: "pass" marks that rested on manual one-offs (spec 002, found by /verify)
- What: spec 002's traceability marked R3, R5 and part of R15 "pass" on checks I had run once by hand, and R2 on a stderr capture that only the ASan run enforced. Spec text had also drifted (28 vs 34 scenarios, a reserved-vehicle scenario with no criterion, the `---` format).
- Caught by: the independent `spec-reviewer` pass (fresh context, told nothing about the implementation). I had considered the spec finished.
- Fix: automated each check in `make test-selfcheck`, made stderr always fatal, corrected the spec, committed the report with a disposition for every finding.
- Lesson: ask the author-side question "could this check fail?" for every pass, and let a reviewer who did not write it ask it too.

## 2026-11-07: repo cloned into a subdirectory of the launch directory (phase 0 setup, found in phase 4)
- What: the session was started in `~/src` and the repo cloned to `~/src/dealerdesk`. I never told the owner to relaunch inside the repo. The project settings, hook, commands and agent from spec 003 were therefore never loaded, and a `git push --dry-run` ran unblocked twice (before and after a restart).
- Caught by: attempting the live proof (spec 003 T6) instead of claiming the rules worked, then checking where Claude Code keeps its per-project data (`~/.claude/projects/` has no entry for the repo) and that `~/src/.claude` does not exist.
- Consequence: no damage (dry runs only, nothing pushed). The earlier explanation I logged ("settings are read at session start") was incomplete; the correction is in the spec 003 change log. CLAUDE.md now says to launch from the repo root.
- Status: hypothesis, to be confirmed by relaunching from the repo root and rerunning T6.

## 2026-11-07: hook silence in a worktree read as "not loaded" (spec 003 T6 c)
- What: a broken scratch `.c` file written in a git worktree produced no hook feedback. I first took it as the hook not firing, which was the earlier "settings not loaded" theory again.
- Caught by: running `make warn` by hand (it fails, so the file would trip the hook) and reading the script: it does `cd "$CLAUDE_PROJECT_DIR"`, so it built the main checkout, where the file does not exist.
- Fix: the hook builds the tree that holds the edited file (`check-agent` case written first and seen to fail). The agent's attempt to edit the hook was refused by the auto-mode classifier ("Self-Modification"); the owner applied the edit.
- Lesson: a silent check is not evidence either way until you know what it checked. Guard rails are changed by the person they protect, not by the agent they constrain.

## 2026-11-07: `--update` ran with no prompt in an interactive session (spec 003 T6 d)
- What: `python3 tests/golden.py --update cust_list` was expected to hit the ask rule `Bash(python3 tests/golden.py --update:*)` and be answered No. It printed `UPDATED cust_list` with no prompt. `git status` and `git diff --stat tests/golden` were empty (identical bytes), so nothing changed.
- Caught by: running the proof instead of assuming the narrowed allow rule was enough.
- Likely cause (not verified): `defaultMode: auto` in `~/.claude/settings.json`, where the auto-mode classifier approves the command and the ask rule is not consulted. Not separated from rule precedence.
- Lesson: R4 is not proven by the rule text. Rerun from a session started with `claude --permission-mode default`. Until then `--update` is guarded only by CLAUDE.md rule 1 and by reviewing `git diff tests/golden` before each commit.

## 2026-11-08: owner's `!` run read as a test of the ask rule; CLAUDE.md claimed a confirmation that does not exist (spec 003 T6 d)
- What: the owner ran `python3 tests/golden.py --update cust_list` with `!` in a default-mode session. I reported only "no diff, nothing to revert" and did not say at once that `!` commands bypass the permission system, so the missing prompt proved nothing. Separately, CLAUDE.md said `--update` "asks for confirmation", but `tests/golden.py` has none; the only confirmation is the Claude Code ask rule.
- Caught by: reading `golden.py` while planning the retest, then running the proof through the Bash tool in a default-mode session: the prompt appeared (No left the files untouched; Yes rewrote identical bytes).
- Fix: CLAUDE.md now says where the confirmation comes from and when it is skipped; project settings set `defaultMode: default`; the `make CC=...` bypass is recorded as a known limit.
- Lesson: before reading a missing prompt as a result, ask whether the path goes through the permission engine at all.

## 2026-11-08: an edit shortened an untouched line and shifted the invoice view (spec 004 T5)
- What: while replacing the `Discounts` line in `view_invoice`, my edit text ended in the start of the next line (`Net price `) and the tool dropped one space of the unchanged `Net price` line. Every invoice view moved the number one column left.
- Caught by: five existing goldens failing (`inv_view_50230`-`50232`, `sell_retail_view`, `sell_trade_salesman_tradein`). Their diffs were one space in the `Net price` line. I had not looked at the line myself and my first read of my own scenario output missed the shift.
- Fix: restored the line exactly; `git diff -U0 -- main.c | grep -c "Net price"` is 0. All 43 existing tests pass again.
- Lesson: an edit should match only the lines it changes. The golden tests are what stopped this, so never approve a golden to make such a failure go away; read the diff first.

## 2026-11-08: R13 marked "pass" on evidence the reviewer found indirect; no test saved a fleet invoice twice (spec 004 `/verify`)
- What: I marked R13 "pass" citing three existing goldens that were not written for R13, without saying so, and I had no test that loads a stored 12-field invoice and saves again.
- Caught by: the fresh-context `spec-reviewer` (R13 "partly covered"); the round-trip gap I found while checking its note against the design.
- Fix: T8 `fleet_sell_then_sell`, shown to fail on a throwaway saver that drops the 12th field; the R13, R11 and R14 rows now say what the evidence is.
- Lesson: when a table says "pass", say whether the test was written for that criterion. A feature that adds an optional field needs a load, save, load round trip, not only a load and a view.

## 2026-11-09: three `Write(...)` deny rules never matched (spec 003 T2, found at session start)
- What: `.claude/settings.json` listed `Write(data/**)`, `Write(tests/golden/**)` and `Write(tests/fixtures/**)`. Claude Code 2.1.319 warned `Deny rule Write(...) never matches · use Edit(...)`. File rules are looked up as `Edit(path)` for every file-editing tool, so the Write entries did nothing, and the checker required them.
- Caught by: the startup warning, not by any test. T6 (b) proved only an Edit under `tests/golden/`; the Write path was assumed.
- Fix: checker changed first (new R3 check rejecting `Write(`/`MultiEdit(` rules, seen failing), settings edit by the owner, spec 003 wording and T6e (live Write proof) added.
- Lesson: prove each tool path a rule claims to block, and read startup warnings as findings.
