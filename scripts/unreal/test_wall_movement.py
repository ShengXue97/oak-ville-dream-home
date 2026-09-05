"""Exercise native CharacterMovement against thin and external walls in Play.

Use only in an owned test session. Ignore furnishings temporarily to isolate
walls; drive native movement input over real game frames, then restore state.
"""

import json
import time
from pathlib import Path
import unreal
import oakville_runtime as runtime

ROOT = Path(__file__).resolve().parents[2]

state = runtime.STATE
if state is None or state.creative:
    raise RuntimeError("Start a dedicated human-mode test session")
pawn, movement = state.pawn, state.movement
capsule = pawn.get_editor_property("capsule_component")
original = pawn.get_actor_location()
actors = unreal.GameplayStatics.get_all_actors_of_class(
    state.world, unreal.StaticMeshActor
)
ignored = [
    a
    for a in actors
    if str(a.get_folder_path()) in {"Furniture", "Fixed_Joinery", "Decor"}
]
for actor in ignored:
    capsule.ignore_actor_when_moving(actor, True)
original_down = state.down
cases = [
    ("external", (100, 400, 88), (-1, 0, 0), 35, -1),
    ("thin_west", (440, 240, 88), (-1, 0, 0), 367.5, -1),
    ("thin_east", (550, 220, 88), (1, 0, 0), 607.5, 1),
]
cases = [
    (name, start, direction, limit, sign, speed)
    for speed in (180, 320)
    for name, start, direction, limit, sign in cases
]
index = 0
started = 0
results = []
max_delta = 0


def begin():
    global started
    name, start, direction, limit, sign, speed = cases[index]
    pawn.set_actor_location(unreal.Vector(*start), False, True)
    state.previous_position = pawn.get_actor_location()
    movement.stop_movement_immediately()
    state.down = lambda key: speed == 320 and key == "LeftShift"
    started = time.monotonic()


def finish():
    unreal.unregister_slate_post_tick_callback(handle)
    for actor in ignored:
        capsule.ignore_actor_when_moving(actor, False)
    state.down = original_down
    state.update_walk_speed()
    pawn.set_actor_location(original, False, True)
    movement.stop_movement_immediately()
    state.last_safe = original
    state.previous_position = original
    report = {
        "cases": results,
        "max_frame_delta_s": max_delta,
        "passed": bool(results) and all(r["passed"] for r in results),
    }
    (ROOT / "docs/unreal/wall-movement-validation.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )
    print(json.dumps(report))


def tick(delta):
    global index, max_delta
    max_delta = max(max_delta, delta)
    name, start, direction, limit, sign, speed = cases[index]
    pawn.add_movement_input(unreal.Vector(*direction), 1, True)
    if time.monotonic() - started < 2:
        return
    x = pawn.get_actor_location().x
    results.append(
        {
            "wall": name,
            "speed_cm_s": speed,
            "x_cm": round(x, 3),
            "passed": sign * (x - limit) <= 0.1 and abs(x - start[0]) > 10,
        }
    )
    index += 1
    if index == len(cases):
        finish()
    else:
        begin()


begin()
handle = unreal.register_slate_post_tick_callback(tick)
