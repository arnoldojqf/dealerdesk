# Spec 003: agent setup: requirements

**Review mode:** bundled. `requirements.md`, `design.md` and `tasks.md` are reviewed in one go.
**Status:** draft

## Problem
The agent currently follows a minimal `CLAUDE.md` and rules that live only in the chat. Nothing stops it from pushing, editing sample data, hand-editing a golden file, or leaving a compiler warning behind. The spec workflow (`specs/README.md`) is followed by hand, and independent review means pasting a prompt. Part 1 of the brief asks for the agent setup to be committed and reusable, and TICKET-142 will be built through it.

## User stories
- As the owner, I want the dangerous or irreversible actions blocked or confirmed, so a lapse by the agent cannot touch upstream, the sample data or the approved goldens.
- As the owner, I want a C edit that breaks the build or adds a warning reported to the agent immediately, so it fixes it before the next step.
- As a reviewer, I want to see the workflow as commands I can run (`/spec`, `/implement`, `/verify`), not as prose.
- As the owner, I want an independent check of an implementation against its acceptance criteria, made by an agent that did not write it.

## Acceptance criteria
- **R1 (instructions).** `CLAUDE.md` states the build, warn, asan, test, test-asan, test-selfcheck and reset commands, the layout, the spec workflow and the hard rules. Every `make` target it names exists, and every file path it names exists.
- **R2 (settings valid).** `.claude/settings.json` is valid JSON with `permissions.allow`, `permissions.ask`, `permissions.deny` and a `hooks.PostToolUse` entry.
- **R3 (blocked).** The deny list blocks: `git push`, `gh pr`, `gh repo`, changes to remotes (`git remote add|set-url|remove|rename`), `rm -rf`, and Edit/Write of `data/**`, `tests/golden/**` and `tests/fixtures/**`.
- **R4 (confirmed).** The ask list requires confirmation for `python3 tests/golden.py --update`, `git tag`, `git checkout`, `git reset` and `gh api`.
- **R5 (allowed).** The allow list lets the agent run `make`, the test harness without `--update`, read-only git (`status`, `diff`, `log`, `show`, `remote -v`), `git add`, `git commit`, and `gh run` reads, so routine work does not prompt.
- **R6 (build hook).** When the agent edits or writes a `.c` or `.h` file, a hook runs `make warn`. If the build fails or prints any compiler warning or error, the hook reports it to the agent (exit code 2 with the compiler output). If the build is clean, or the file is not `.c` or `.h`, it is silent and exits 0.
- **R7 (commands).** `.claude/commands/spec.md`, `implement.md` and `verify.md` exist, each with a description and an argument hint.
  - `/spec <name>` drafts `requirements.md`, `design.md` and `tasks.md` of the next numbered folder in stages and stops for approval at each gate required by `specs/README.md`.
  - `/implement <spec>` works through `tasks.md` in order, tests first, one commit per task citing the spec and task, a line-by-line explanation before any commit that changes C, and stops to update the spec if it proves wrong.
  - `/verify <spec>` starts the reviewer subagent and reports every acceptance criterion as covered, partly covered or gap.
- **R8 (reviewer).** `.claude/agents/spec-reviewer.md` defines a read-only reviewer with a fresh context that, for each R-ID, finds the test that cites it, runs the tests, and checks the diff for changes the spec does not allow.
- **R9 (checked in CI).** `scripts/check-agent-setup.py` checks R1, R2, R3, R4, R5, R6 (against a temporary copy with a deliberate error and a clean one) and R7/R8 (files exist with required front matter). `make check-agent` runs it, and CI runs it.
- **R10 (real use).** `/verify 002` has been run, and its report is committed in `specs/002-characterisation-harness/verify-report.md`. Any gap it finds is either fixed or recorded with a reason.
- **R11 (no product change).** No `.c`, `.h`, `data/` or test-golden file changes.

## Scope
**In:** `CLAUDE.md`, `.claude/settings.json`, `.claude/hooks/`, `.claude/commands/`, `.claude/agents/`, `scripts/check-agent-setup.py`, a `make check-agent` target, a CI step, `.gitignore` entry for `.claude/settings.local.json`.
**Out:** MCP servers; user-level settings in `~/.claude`; pre-commit or pre-push git hooks; skills beyond the three commands; model or cost settings; a fully automated test of what the commands do (see A5).

## Open questions and assumptions
- **A1.** The hook script parses the hook's JSON input with `python3`, not `jq`, so it works on any machine that can run the test harness.
- **A2.** The deny list is a guard against slips, **not a security boundary**: Claude Code matches command prefixes, so a determined bypass (`bash -c "git push"`) is possible. The hard rules in `CLAUDE.md` remain the primary control. Stated in the file.
- **A3.** The hook runs `make warn` only. The sanitizer build and the test suite are slower and run in CI and on demand.
- **A4.** The baseline compiles with zero warnings on gcc and clang (CI), so any warning the hook sees is new. This is why the hook treats any warning as feedback.
- **A5.** What `/spec`, `/implement` and `/verify` do depends on a model, so they cannot be unit-tested. The automated check proves they exist and are well formed. Their behaviour is proven by use: `/spec` and `/implement` on spec 004, `/verify` on spec 002 now (R10). The traceability table says "manual" for these.
- **A6.** Project-level commands and subagents may only load when a session starts. If they are not available in this session, `/verify` is run by launching a general-purpose subagent with the exact text of `spec-reviewer.md` as its prompt, and the report says so.
- **A7.** Deny and ask rules are proven by attempting a harmless blocked action in this session (manual), because the permission engine is not available to the script.

## Change log
(none yet)
