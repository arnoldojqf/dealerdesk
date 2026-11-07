# Specs

Every piece of work goes through a spec before code. Plain markdown, driven by slash commands (added in spec 003).

## Layout
Each piece of work gets `specs/NNN-<name>/` with:
- `requirements.md`: problem, user stories, numbered acceptance criteria (R1, R2, ...) in Given/When/Then or EARS form, scope (in/out), open questions and assumptions.
- `design.md`: approach, code touched (`file:line`), rejected alternatives, data and compatibility impact, risks.
- `tasks.md`: ordered checklist. Each task names the criteria it serves and the test that proves it.

All three files end with a **Change log** section.

## Gates
- Spec 004 (TICKET-142): three separate approvals, requirements, then design, then tasks.
- Small specs (001-003): all three files reviewed in one go. The spec says so at the top.

## Traceability
- Every acceptance criterion maps to at least one automated test; the test name or a comment cites its ID.
- Commit messages cite spec and task, e.g. `spec 005 T3: ...`.

## Source of truth
If implementing shows a spec is wrong or incomplete, stop, update the spec, log the change with the reason, then continue. Code and spec never drift silently.

## Principles
1. Preserve existing behaviour exactly, bugs included. Record bugs, fix only when the owner agrees.
2. Staff must not notice any change except the new feature.
3. Real `data/` is never written except through tests on temp copies.
4. Golden files change only for an intended behaviour change; the commit cites the criterion.
5. Keep C changes minimal and explainable; no reformatting of untouched code.
6. Never push, force-push, change remotes or open PRs without asking. Never open a PR against upstream.
7. Ambiguities get a recorded call, in the spec or in `docs/DECISIONS.md`.
8. Verify before claiming: run it and show the output.
