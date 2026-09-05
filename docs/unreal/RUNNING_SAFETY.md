# Running safety (application 0.10.2)

Hold either Shift to run at 320 cm/s; release to walk at 180 cm/s. G is the only
project shortcut for creative flight. Human movement remains Epic's First Person
Character with CharacterMovement gravity, jump and capsule collision.

The live input mappings contain no Shift action that changes collision. A live
probe found the active template camera attached to the rotated FirstPersonMesh,
approximately 75 cm horizontally away from the capsule. This explains how the
view can enter walls while collision tests of the character body pass. The
reported physical-key sequence was not independently reproduced.

`fix_camera_rig.py` saves a separate WalkthroughCamera in the character Blueprint,
with the template camera inactive. The walkthrough camera is attached to the
capsule at (0, 0, 72) cm and follows native control rotation. Runtime initialization
and attachment checks keep the mesh/socket camera from becoming active again.
`setup_standard_controller.py` invokes this repair when rebuilding the controller.

The previous recovery check
could nevertheless accept an unexpected flying movement mode, a detached updated
component, or an unswept wall crossing as a new safe grounded position.

Human mode now repairs the first two conditions and independently sweeps each
displacement against architecture using the Pawn collision profile. It uses a
capsule inset by 2 cm to avoid ordinary floor/wall contact. A blocked displacement
returns to the previous accepted position and stops velocity before updating the
safe position. Output Log records the rejected positions and Shift state.

Furniture and moving doors use the native capsule collision; the additional sweep
ignores them to avoid rejecting normal step-ups and animated door movement. G
flight bypasses this safeguard, and returning to human restores the last safe
grounded position. This is a recovery layer, not a replacement movement controller.

Run tests only in a dedicated Play session because they reposition the pawn:

- `test_running_safety.py`: both Shift states, deliberate unswept wall crossings,
  route acceptance, unexpected flight, detached movement, and creative return.
- `test_wall_movement.py`: native movement at walking and running speeds against
  exterior and thin partition walls over actual game frames.
- `test_play_controls.py`: jump/landing, E interaction, locked entrance and G toggle.
- `test_camera_running.py`: 20 Shift/release and yaw combinations; the active eye
  must remain centred over the collision capsule with its 72 cm vertical offset.

Tests drive the runtime key-query handler and native movement APIs without taking
OS focus. They do not simulate the user's physical keyboard or prove that the
original intermittent input sequence has been reproduced. Results are in the
adjacent validation JSON files. No geometry or Blender material changes are needed
for this runtime-only patch; normal Blender-to-Unreal sync retains these controls.
