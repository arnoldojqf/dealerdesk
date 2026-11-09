---
description: Independent check of a spec's implementation and tests against every acceptance criterion
argument-hint: <spec number or folder name>
---

Verify the spec `$ARGUMENTS` with a fresh-context reviewer.

1. Resolve the folder under `specs/`.
2. Launch the `spec-reviewer` subagent (Agent tool, subagent_type `spec-reviewer`).
   Pass only the spec folder path. Do not describe the implementation or say what
   you expect; the reviewer must form its own view.
3. Show the reviewer's table and findings to the owner unchanged, then add your
   own short summary: gaps, overclaims, drift.
4. Do not edit anything in this command. Offer to fix each gap (or to record it
   with a reason in the spec's Change log) and wait for the owner's decision.
5. If asked, save the report as `specs/NNN-<name>/verify-report.md`.
