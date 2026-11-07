# Cross-cutting decisions

Spec-specific decisions live in each spec. Format: decision, reasoning, status.

## D1. Fleet flag stored as customer type `F` (proposed, confirm at spec 004 design gate)
No file-format change. An old binary writes the `%c` back unchanged, so rolling back to `dealerdesk.old` is safe. Cost: a customer cannot be both Trade and Fleet.

## D8. Existing bugs are recorded, not fixed
Behaviour is preserved, bugs included (B-IDs in CODEMAP). Fixing is a separate decision for the user.

## D9. Harness uses the Python standard library only
No pip step in CI. Raw ANSI bytes are kept in goldens and the date is masked.

## D10. clang runs in CI only
It is not installed locally. Installing it is the user's call.

## D11. Default branch stays `master`
That is what upstream uses. Keeps the history comparable.
