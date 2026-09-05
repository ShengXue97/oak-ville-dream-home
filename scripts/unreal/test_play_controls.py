"""Validate live Play pawn, jump, doors and creative toggle without OS input.

Run only in a dedicated test Play session. This moves the test player and drives
the same key-edge handler used by E and G, then restores the entry start.
Jump is invoked through the native Character API to test gravity and landing;
this does not simulate the operating system Space key or test its input binding.
"""

import json
import time
from pathlib import Path
import unreal
import oakville_runtime as runtime

ROOT = Path(__file__).resolve().parents[2]
state = runtime.STATE
if state is None:
    raise RuntimeError("Start the test Play session first")
pawn = state.pawn
controller = state.controller
movement = state.movement
controller.set_ignore_move_input(True)
controller.set_ignore_look_input(True)
report = {
    "spawned_character": pawn.get_class().get_name() == "BP_FirstPersonCharacter_C",
    "initial_human_mode": not state.creative,
    "level_start_pitch": abs(state.initial_pitch) < 0.01,
    "gravity_scale": movement.get_editor_property("gravity_scale"),
}
original_down = state.down
test_keys = set()
state.down = lambda key: key in test_keys
start_z = pawn.get_actor_location().z
peak_z = start_z
phase = "jump"
started = time.monotonic()
test_keys.add("SpaceBar")
pawn.jump()


def finish():
    controller.set_ignore_move_input(False)
    controller.set_ignore_look_input(False)
    state.down = original_down
    test_keys.clear()
    if state.creative:
        state.set_creative(False)
    pawn.set_actor_location(unreal.Vector(270, 655, 88), False, True)
    pawn.set_actor_rotation(unreal.Rotator(pitch=0, yaw=-60, roll=0), False)
    controller.set_control_rotation(unreal.Rotator(pitch=0, yaw=-60, roll=0))
    movement.stop_movement_immediately()
    for door in state.doors:
        door.current = door.target = door.closed_angle
        door.apply(door.current)
    unreal.unregister_slate_post_tick_callback(handle)
    report["passed"] = all(
        value for key, value in report.items() if isinstance(value, bool)
    )
    (ROOT / "docs/unreal/play-controls-validation.json").write_text(
        json.dumps(report, indent=2)
    )
    print(json.dumps(report))


def test_tick(delta):
    global phase, started, peak_z
    elapsed = time.monotonic() - started
    try:
        if phase == "jump":
            peak_z = max(peak_z, pawn.get_actor_location().z)
            if elapsed > 0.25:
                test_keys.discard("SpaceBar")
            if elapsed < 2.5:
                return
            report["jump_rise_cm"] = round(peak_z - start_z, 2)
            report["jump_lifted_character"] = peak_z - start_z > 15
            report["landed_on_floor"] = (
                movement.is_moving_on_ground()
                and abs(pawn.get_actor_location().z - start_z) < 3
            )
            front = next(d for d in state.doors if d.locked)
            report["front_door_rejects_toggle"] = (
                not front.toggle() and front.target == front.closed_angle
            )
            door = next(d for d in state.doors if d.name == "Bedroom_3_Door_Hinge")
            centre = door.leaf.get_actor_location()
            pawn.set_actor_location(
                unreal.Vector(centre.x, centre.y + 90, 88), False, True
            )
            pawn.set_actor_rotation(unreal.Rotator(pitch=0, yaw=-90, roll=0), False)
            controller.set_control_rotation(unreal.Rotator(pitch=0, yaw=-90, roll=0))
            phase, started = "door_aim", time.monotonic()
        elif phase == "door_aim" and elapsed > 0.4:
            report["nearby_door_targeted"] = state.aimed_door() is not None
            report["targeted_door"] = (
                state.aimed_door().name if state.aimed_door() else None
            )
            test_keys.add("E")
            phase, started = "door_open", time.monotonic()
        elif phase == "door_open":
            if elapsed > 0.25:
                test_keys.discard("E")
            door = next(d for d in state.doors if d.name == "Bedroom_3_Door_Hinge")
            if elapsed < 8 and abs(door.current - door.open_angle) > 0.1:
                return
            report["door_angle_after_e"] = door.current
            report["door_target_after_e"] = door.target
            report["e_opens_interior_door"] = abs(door.current - door.open_angle) < 0.1
            test_keys.add("G")
            phase, started = "creative", time.monotonic()
        elif phase == "creative" and elapsed > 0.3:
            report["g_enables_flight"] = (
                state.creative
                and movement.get_editor_property("movement_mode")
                == unreal.MovementMode.MOVE_FLYING
            )
            test_keys.discard("G")
            phase, started = "release", time.monotonic()
        elif phase == "release" and elapsed > 0.3:
            test_keys.add("G")
            phase, started = "human", time.monotonic()
        elif phase == "human" and elapsed > 0.6:
            report["g_restores_human"] = (
                not state.creative and movement.is_moving_on_ground()
            )
            finish()
    except Exception:
        import traceback

        report["error"] = traceback.format_exc()
        report["test_completed"] = False
        finish()


handle = unreal.register_slate_post_tick_callback(test_tick)
