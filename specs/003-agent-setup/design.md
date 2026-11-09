# Spec 003: agent setup: design

**Status:** verified

## Approach
Plain files in the repo, in the places Claude Code reads them. One small script checks that they are well formed, so the setup cannot rot unnoticed.

```
CLAUDE.md                           instructions (grown from the Phase 1 version)
.claude/settings.json               permissions + hook wiring (shared, committed)
.claude/hooks/rebuild-on-c-edit.sh  PostToolUse hook for .c / .h edits
.claude/commands/spec.md            /spec <name>
.claude/commands/implement.md       /implement <spec>
.claude/commands/verify.md          /verify <spec>
.claude/agents/spec-reviewer.md     fresh-context reviewer
scripts/check-agent-setup.py        automated check (make check-agent, CI)
```
`.claude/settings.local.json` (personal overrides) is added to `.gitignore`.

### settings.json
```
permissions.defaultMode: default (auto mode skips the ask rules; T6 d, T9)
permissions.allow: Bash(make:*), Bash(python3 tests/golden.py), Bash(python3 tests/golden.py --selfcheck),
  Bash(python3 scripts/check-agent-setup.py:*),
  Bash(git status:*), Bash(git diff:*), Bash(git log:*), Bash(git show:*), Bash(git remote -v), Bash(git add:*),
  Bash(git commit:*), Bash(gh run list:*), Bash(gh run view:*), Bash(ls:*), Bash(grep:*)
permissions.ask:   Bash(python3 tests/golden.py --update:*), Bash(git tag:*), Bash(git checkout:*),
  Bash(git reset:*), Bash(gh api:*)
permissions.deny:  Bash(git push:*), Bash(gh pr:*), Bash(gh repo:*), Bash(git remote add:*),
  Bash(git remote set-url:*), Bash(git remote remove:*), Bash(git remote rename:*), Bash(rm -rf:*),
  Edit(data/**), Edit(tests/golden/**), Edit(tests/fixtures/**)
hooks.PostToolUse: matcher "Edit|Write|MultiEdit" -> .claude/hooks/rebuild-on-c-edit.sh
```
Deny beats allow, so `git push` stays blocked even if a broader rule appears later. The golden and fixture paths are denied through `Edit(path)` rules (Claude Code applies them to every file-editing tool, Write included, and never looks up `Write(path)` rules) so approved output can only change through `golden.py --update`, which asks first. `--update` is already refused when `CI` is set (spec 002 R5).
`git commit` is allowed because the workflow commits after every task; the rule "explain C diffs line by line before committing" lives in `CLAUDE.md` and in `/implement`, because a permission rule cannot express it.

### The hook
`rebuild-on-c-edit.sh` reads the hook JSON from stdin, takes `tool_input.file_path` (via `python3`), exits 0 at once unless it ends in `.c` or `.h`, then runs `make warn` in `${CLAUDE_PROJECT_DIR:-$PWD}`. If `make` fails or the output contains `warning:` or `error:`, it prints the output to stderr and exits 2, which Claude Code feeds back to the agent. Otherwise silent, exit 0. About one second per C edit.

### Commands (prompts)
Each is a markdown file with front matter (`description`, `argument-hint`) and a body that tells the agent what to do and where to stop. They point at `specs/README.md` for the rules instead of repeating them, so there is one source.
- **spec.md**: find the next number in `specs/`, ask for the problem if not given, draft `requirements.md`, stop; after approval draft `design.md`, stop; after approval `tasks.md`, stop. Bundled mode (specs 001-003 style) is used only when the user says so. Always cites `file:line` and lists rejected alternatives.
- **implement.md**: read the spec's three files, refuse to start unless status is `approved`; for each task: write or update the test first and see it fail, implement, run `make test`, explain C diffs line by line, commit with `spec NNN Tn:`, tick the box. If the spec is wrong, stop, edit the spec, add a change-log line, then continue. Never `--update` a golden without naming the criterion.
- **verify.md**: launch `spec-reviewer` on the named spec and show its table. Does not edit anything.

### Reviewer subagent
`spec-reviewer.md`: `tools: Read, Grep, Glob, Bash`, instructions to stay read-only (the deny list also applies). It reads the spec, builds an R-ID to test table by searching tests and scenario headers for each ID, runs `make test` (and `make test-asan` if the spec touches C), runs `git diff baseline --stat` for forbidden changes, and returns a table: criterion, evidence, covered / partly / gap, plus a list of things the spec does not cover that the diff changed. It is told it did not write the code and must not assume the author is right.

### check-agent-setup.py (Python standard library)
Checks R1 (every `make X` named in `CLAUDE.md` is a Makefile target; every backticked path exists), R2/R3/R4/R5 (JSON loads; each required rule string is present in the right list), R6 (runs the hook with sample JSON against a temp copy of the repo: a clean `.c` edit exits 0 and prints nothing; a `.c` with a deliberate error exits 2 with output; a `.md` path exits 0 without running make), R7/R8 (files exist; front matter has `description`; `spec-reviewer` lists its tools). Every check runs and prints one line (`ok`, or `FAIL` with the reasons); the exit status is non-zero if any failed. R2 also requires `permissions.defaultMode` to be `default` (T9).
`make check-agent` runs it; CI gets one step.

## Code touched
No `.c`, `.h`, `data` or golden file. `Makefile` (new target), `.github/workflows/ci.yml` (one step), `.gitignore` (one line), `CLAUDE.md` (rewritten from the Phase 1 version).

## Alternatives considered
- **A pre-commit git hook for "run tests before commit":** runs for humans too and slows every commit; the rule is "tests pass at each commit", which `/implement` and CI already enforce. Rejected for now.
- **`jq` in the hook:** shorter, but not installed everywhere; python3 is already required. Rejected (A1).
- **Making all warnings fatal (`-Werror`) in the hook only:** equivalent here, but `-Werror` in the Makefile is a separate decision about the product build. The hook just reads output.
- **A custom MCP server for spec tracking:** heavy for markdown files and a grep. Rejected.
- **Deny `git commit`:** would stop the agent doing what the brief asks (commit as you go). Rejected; the control is the C-diff explanation rule.
- **One big skill instead of three commands:** commands are explicit and appear in the history as small files a reviewer can read. Rejected.

## Data and compatibility impact
None. Nothing under the program or its data changes.

## Risks
- **Hook noise or slowness** makes the agent distrust it. Mitigation: silent on success, 1 s, only `.c`/`.h`.
- **Deny patterns are prefix matches** (A2). Documented; hard rules remain.
- **Commands or the subagent not loaded** in the running session (A6). Fallback documented; the files are still what the reviewers read.
- **The check script tests the form, not the behaviour,** of the commands (A5). The traceability table is honest about it.
- **Hook edits could break the agent's own work** if `make warn` fails for an unrelated reason (for example a half-finished edit across two files). The message says which file triggered it; a failing hook does not block the edit, it only reports.

## Change log
- 2026-11-09: settings sketch brought in line with the file (`defaultMode`, the narrowed harness allow rules from the 2026-11-07 tasks entry) and the checker description corrected (it runs every check; it does not stop at the first failure). Found by `/verify 003`.
- 2026-11-09: removed the three `Write(...)` deny rules from the design. Claude Code 2.1.319 warned at startup `Deny rule Write(data/**) never matches · use Edit(data/**)` (same for `tests/golden/**`, `tests/fixtures/**`). `make check-agent` now fails if any `Write(` or `MultiEdit(` rule appears.
