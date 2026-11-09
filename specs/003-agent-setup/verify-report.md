# Spec 003 verify report (2026-11-09)

One run of the `spec-reviewer` agent, with its commands run (`make test`, `make check-agent`). Its report is reproduced unchanged, followed by what was done about it.

## Reviewer report (unchanged)

Spec 003 review. Every criterion has an automated check, but R3, R4 and R6 enforcement and R7/R8 behaviour rest on manual proof. I ran `make test` (exit 0, 47 passed, 0 failed) and `make check-agent` (exit 0, all 17 checks ok, "agent setup ok"). I did not run `make test-asan` or `make test-selfcheck`, because the spec ships no C and no test changes. `make check-agent` is the only automated proof for R1-R9.

| Criterion | Evidence | Verdict | Note |
|---|---|---|---|
| R1 CLAUDE.md | `check_claude_md` in `/home/arnoldojqf/src/dealerdesk/scripts/check-agent-setup.py` requires the listed commands, the four section headings, that every `make X` is a Makefile target, and that every backticked path exists. Ran: ok. | covered | The path check skips tokens containing whitespace, `git `, `make` or a leading `-`. It would miss a wrong path written inside a command. |
| R2 settings valid | The check does a JSON load and requires the three permission keys and a non-empty PostToolUse list. It also requires the hook command to name `rebuild-on-c-edit.sh`. Ran: ok. | covered | |
| R3 deny | The check requires all 11 deny strings, and `R3 file rules` rejects any `Write(` or `MultiEdit(` rule. The enforcement proofs are manual (T6a, T6b, T6e). | partly covered | The script proves only that the rule text is present. The `git push` and `Edit(tests/golden)` proofs are in the change log, not in a test. This follows A7, since the permission engine is not available to a script. |
| R4 ask | The check requires the 5 ask strings. The enforcement proof is manual (T6d, plus the owner's report on 2026-11-09). | partly covered | Same limit as R3. The 2026-11-09 confirmation is "reported by the owner" and cannot be checked. |
| R5 allow | The check requires 12 allow strings. | covered | The settings also allow `ls` and `grep`, `check-agent-setup.py` and `--selfcheck`. The checker does not require them and R5 does not name them. |
| R6 hook | Five hook cases against a temp copy: clean build silent with exit 0, error gives exit 2, warning gives exit 2, `.md` file does not run make (its Makefile is `false`), and a different tree is built. Ran: all ok. Each case would fail if the hook were broken. | covered | Live firing was shown manually on 2026-11-07. |
| R7 commands | `R7 /spec`, `/implement` and `/verify` check that the files exist and have `description` and `argument-hint`. I read `spec.md` and `verify.md` and they match the sub-bullets. | partly covered | The check proves form only. The behaviour sub-bullets (stops at gates, one commit per task) are not tested, which A5 accepts. The traceability table says "shown in use on spec 004", not "manual". |
| R8 reviewer | The check requires `name`, `description` and `tools`, and that the tools do not include Edit or Write. `spec-reviewer.md` has `tools: Read, Grep, Glob, Bash`, and its steps match R8. | partly covered | Bash is not constrained to read-only by anything but the prompt. |
| R9 checked in CI | `Makefile:31` has the `check-agent` target and `.github/workflows/ci.yml:48` runs it. Locally ok. | covered | The CI run 42421288067 cited in tasks.md was not re-checked. `gh` was not used. |
| R10 real use | `specs/002-characterisation-harness/verify-report.md` exists. Fix commit a88edf5 follows it. | covered | The 003 tasks.md says the T7 run used the A6 fallback. I did not audit each disposition. |
| R11 no product change | `git log 65ce2d9^..fa12ade -- '*.c' '*.h' data tests/golden tests/fixtures` is empty. That range covers the spec 003 implementation commits. | covered | `git diff baseline -- '*.c' '*.h' data` is NOT empty, because spec 004 changed `calc.c`, `calc.h`, `dbfile.c`, `main.c` and `globals.h`. The tasks.md command is correct only for the 003 commit range. Later 003 commits (`55a62f8`, `27d7a12`) touch only `.claude/` and docs. |

**Not covered by the spec**
- `.claude/settings.json` sets `defaultMode: default`. This is recorded in the change log but is not in any R. No check requires it, so a revert would pass `make check-agent`.
- The hook walks up to the nearest Makefile, which is logged and tested.
- `Bash(ls:*)`, `Bash(grep:*)`, `Bash(python3 scripts/check-agent-setup.py:*)` and `Bash(python3 tests/golden.py --selfcheck)` are allowed. R5 does not name them and the checker does not require them.
- `.gitattributes` and `scripts/demo.py` are in the baseline diff but are not in the 003 scope list. They belong to other specs.

**Spec/code drift**
- `requirements.md` and `design.md` say "implemented with open items", but `tasks.md` says "implemented" and every box is ticked. `docs/PLAN.md:25` says "implemented; T6 live proofs a-d done (CI run done)", which is stale next to line 13.
- `docs/PLAN.md:44` says the ask-rule follow-up is "not closed". `tasks.md` R4 says it was confirmed on 2026-11-09, and commit 324040e is titled "close ask-rule follow-up".
- The design's Approach section says the golden and fixture paths are denied through `Edit(path)`, consistent with the code. Its settings sketch omits `defaultMode`, `Bash(python3 tests/golden.py)` and `--selfcheck`, so it differs from the actual file. The narrowing is logged in the tasks change log but the design was not updated.
- The design says the check "exits non-zero on the first failure of each check". The script runs all checks and then lists the problems, so the wording is stale.
- The R9 text says the script checks R1-R8 "files exist with required front matter". It does not check the body of the commands.

**Overclaims**
- The R4 row says the prompt was "confirmed 2026-11-09" by "reported by the owner". The evidence is an unverifiable owner report. The 2026-11-08 default-mode run is the real evidence. `PLAN.md:44` contradicts the confirmation.
- The R7 row says "shown in use" for `/spec` and `/implement`. The only artifact I checked is the commit history, which does not show that the commands were the ones invoked.
- The R8 row says "behaviour: partly". The 2026-11-09 change log says `/verify 001` ran with every Bash call denied, so reviewer behaviour is not fully shown. I ran this review from the prompt text only.
- Hook "silent on clean" is tested only against calc.c. I judged that sufficient.

**Verdict:** The automated checks pass and the form of R1-R9 holds. Enforcement of R3, R4 and R6 in the live permission engine rests on manual logs, and R7/R8 behaviour is unproven by tests, which A5 and A7 accept. Fix the status and PLAN drift, add a `defaultMode` check, and change the R11 command to a 003 commit range.

## What was done about it

No criterion failed, so spec 003 is set to verified. Findings and responses (tasks.md T9 and its change log):

- **`defaultMode` not checked:** `scripts/check-agent-setup.py` now fails when `permissions.defaultMode` is not `default`. Shown failing on a copy of the settings with `auto` ("FAIL R4 default mode: ... not 'auto'") and passing on the real file. R2's text and the design were updated.
- **R11 command:** the row now uses the 003 commit range, which is empty (rechecked: 0 lines), and says why `git diff baseline` is no longer empty.
- **R4 overclaim:** the row now says the 2026-11-08 run is the evidence in the repo and the 2026-11-09 confirmation is an owner report.
- **R7 and R8 wording:** both rows now say what the evidence is. R8 mentions the first `/verify 001` that ran nothing and the prompt fix.
- **Design drift:** the settings sketch and the checker description now match the file and the script.
- **Status drift:** requirements, design and tasks all say verified. `docs/PLAN.md` was updated.
- **Accepted without change:** the hook "silent on clean" case uses `calc.c` only; `Bash` in the reviewer's tool list is not restricted to read-only commands beyond the prompt and the deny rules; R3/R4 live enforcement stays manual (A7); the extra allow rules (`ls`, `grep`, `--selfcheck`, the checker) are not required by the checker; the R1 path check skips tokens inside commands.
