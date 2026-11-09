---
description: Draft the next spec (requirements, design, tasks) in stages, pausing for approval at each gate
argument-hint: <short-name> [bundled]
---

Create a new spec named `$ARGUMENTS` following `specs/README.md` (read it first;
it is the source of truth for layout, gates, traceability and principles).

1. Find the next number: look at the folders in `specs/` and use the next `NNN`.
   Create `specs/NNN-<name>/`. Read `docs/CODEMAP.md`, `docs/DECISIONS.md` and the
   code the work will touch before writing anything.
2. If the problem is not clear from the request, ask. Do not invent it.
3. Draft `requirements.md`: problem, user stories, numbered acceptance criteria
   (R1, R2, ...) written so each can be tested (Given/When/Then or EARS), scope
   (in and out), open questions, assumptions (every ambiguity becomes one), and a
   Change log section. Status `draft`.
4. STOP and ask for approval of the requirements. Do not write design.md yet,
   unless the user said `bundled`, in which case draft all three files and stop once.
5. After approval: draft `design.md`: approach, code touched with `file:line`
   references (verify each by reading the file), rejected alternatives with
   reasons, data and compatibility impact, risks, Change log. STOP for approval.
6. After approval: draft `tasks.md`: ordered small tasks, each naming the
   criteria it serves and the test that proves it, tests first; a traceability
   table mapping every criterion to a test; Change log. STOP for approval.
7. Add the spec to the index in `docs/PLAN.md`. Commit each approved stage as
   `spec NNN: ...`. Write no code and make no change to `tests/golden/`.
