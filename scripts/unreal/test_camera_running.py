"""Verify the live camera remains inside the capsule through Shift transitions.

Run in an owned Play session. Drives the runtime input handler without OS focus.
The asynchronous callback has its own module namespace when imported.
"""

import json
import time
from pathlib import Path

import unreal
import oakville_runtime as runtime

ROOT = Path(__file__).resolve().parents[2]
state = runtime.STATE
if state is None:
    raise RuntimeError("Start an owned Play session first")
pawn, controller = state.pawn, state.controller
camera = next(
    c for c in pawn.get_components_by_class(unreal.CameraComponent) if c.is_active()
)
original_down = state.down
original_rotation = controller.get_control_rotation()
original_capsule = pawn.get_editor_property("capsule_component")
original_movement = state.movement
cases = [
    (key, yaw)
    for key in (None, "LeftShift", None, "RightShift", None)
    for yaw in (0, 90, 180, 270)
]
index = 0
started = time.monotonic()
results = []


def begin():
    global started
    key, yaw = cases[index]
    state.down = lambda name: name == key
    controller.set_control_rotation(unreal.Rotator(pitch=0, yaw=yaw, roll=0))
    started = time.monotonic()


def tick(delta):
    global index
    if runtime.STATE is not state:
        # A user may stop Play during an automated check. Never retain a callback
        # that keeps querying components belonging to a destroyed Play world.
        unreal.unregister_slate_post_tick_callback(handle)
        return
    if time.monotonic() - started < 0.25:
        return
    offset = camera.get_world_location() - pawn.get_actor_location()
    horizontal = (offset.x**2 + offset.y**2) ** 0.5
    key, yaw = cases[index]
    results.append(
        {
            "key": key,
            "yaw": yaw,
            "horizontal_offset_cm": horizontal,
            "eye_offset_cm": offset.z,
            "passed": horizontal < 0.1
            and abs(offset.z - 72) < 0.1
            and camera.get_attach_parent() == pawn.capsule_component
            and camera.is_active()
            and pawn.get_editor_property("capsule_component") == original_capsule
            and pawn.get_editor_property("character_movement") == original_movement
            and pawn.get_actor_enable_collision(),
        }
    )
    index += 1
    if index < len(cases):
        begin()
        return
    state.down = original_down
    state.update_walk_speed()
    controller.set_control_rotation(original_rotation)
    unreal.unregister_slate_post_tick_callback(handle)
    report = {"cases": results, "passed": all(case["passed"] for case in results)}
    (ROOT / "docs/unreal/camera-running-validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report))


begin()
handle = unreal.register_slate_post_tick_callback(tick)
