# Wall-collision investigation and hardening

The reported intermittent wall passage was not reproduced in the current
saved scene. This is not evidence that the report was mistaken: the previous
route validator used visibility traces and only one wall-blocking probe, which
was insufficient coverage for a player-collision regression.

The new tests exercise the actual character capsule on its Pawn channel in
Play. All 49 substantial vertical wall segments blocked in both directions
(98 checks). Native CharacterMovement then drove the character against an
external wall and two thin partitions at 180 and 320 cm/s over real frames.
All six cases stopped on the near side; observed frame intervals reached
125 ms. Furniture was temporarily ignored to isolate wall contact, then restored.
This does not cover every corner, opening, jump or possible input sequence.

Two defensive corrections address gaps found during inspection:

- Human mode now explicitly restores actor/capsule collision and WorldStatic/
  WorldDynamic blocking if another operation disables them, returning to the
  last safe location. Unloading the helper exits creative noclip safely.
- Sync rebinds placed components after mesh/collision rebuilding to refresh
  their registered physics bodies. Material overrides are retained. Existing
  architecture was rebound once without modifying mesh geometry.

A persistent HUMAN/collision ON or CREATIVE/collision OFF message makes the
active state visible. G still deliberately enables flight through geometry.

`wall-capsule-validation.json`, `wall-movement-validation.json` and
`collision-recovery-validation.json` record the tests. Their corresponding
`scripts/unreal/test_*.py` scripts require a dedicated test Play session: they
move the test pawn and must not be run during the owner's walkthrough.

The precise root cause remains unconfirmed. If the symptom returns, record the
room/wall, movement direction, whether Shift or Space was held, and the mode
indicator. Preserve that Play session for read-only inspection before stopping
it so the transient collision state can be captured.
