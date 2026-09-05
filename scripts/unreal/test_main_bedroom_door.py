"""Check main-bedroom E interaction over actual frames in an owned Play session."""

import json
import time
from pathlib import Path

import unreal
import oakville_runtime as runtime

ROOT = Path(unreal.Paths.project_dir()).resolve().parents[1]
state = runtime.STATE
if state is None:
    raise RuntimeError("Start a dedicated test Play session first")
door = next(d for d in state.doors if d.name == "Main_Bedroom_Door_Hinge")
pawn, controller = state.pawn, state.controller
old_down = state.down
old_position = pawn.get_actor_location()
old_rotation = controller.get_control_rotation()
keys = set()
state.down = lambda key: key in keys
state.keys["E"] = False
report = {}
phase = "aim_open"
started = time.monotonic()
pawn.set_actor_location(unreal.Vector(885, 390, 88), False, True)
state.movement.stop_movement_immediately()


def aim():
    eye = pawn.get_actor_location() + unreal.Vector(0, 0, 72)
    controller.set_control_rotation(
        unreal.MathLibrary.make_rot_from_x(door.leaf.get_actor_location() - eye)
    )


def finish():
    state.down = old_down
    state.keys["E"] = False
    door.current = door.target = door.closed_angle
    door.apply(door.current)
    pawn.set_actor_location(old_position, False, True)
    controller.set_control_rotation(old_rotation)
    state.movement.stop_movement_immediately()
    unreal.unregister_slate_post_tick_callback(handle)
    report["passed"] = all(report.values())
    (ROOT / "docs/unreal/main-bedroom-door-validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report))


def tick(delta):
    global phase, started
    elapsed = time.monotonic() - started
    if phase == "aim_open" and elapsed > 0.5:
        report["targets_main_door"] = state.aimed_door() is door
        keys.add("E")
        phase, started = "open", time.monotonic()
    elif phase == "open":
        if elapsed > 0.2:
            keys.discard("E")
        if elapsed < 3:
            return
        report["e_opens_door"] = abs(door.current - door.open_angle) < 0.1
        centre, extent = door.leaf.get_actor_bounds(False)
        report["hinge_at_bedroom2_side"] = abs(door.hinge.y - 348) < 0.1
        report["opens_into_main_bedroom"] = centre.x > door.hinge.x + 30
        report["clears_ensuite_approach"] = centre.y + extent.y < 375
        aim()
        phase, started = "aim_close", time.monotonic()
    elif phase == "aim_close" and elapsed > 0.5:
        keys.add("E")
        phase, started = "close", time.monotonic()
    elif phase == "close":
        if elapsed > 0.2:
            keys.discard("E")
        if elapsed < 3:
            return
        report["e_closes_door"] = abs(door.current - door.closed_angle) < 0.1
        finish()


aim()
handle = unreal.register_slate_post_tick_callback(tick)
