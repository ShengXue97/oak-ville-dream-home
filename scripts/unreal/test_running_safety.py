"""Inject movement faults in an owned Play session; never use during navigation."""

import json
import gzip
from pathlib import Path

import unreal
import oakville_runtime as runtime

state = runtime.STATE
if state is None or state.creative:
    raise RuntimeError("An owned human-mode Play session is required")
pawn, movement = state.pawn, state.movement
original = pawn.get_actor_location()
original_down = state.down
report = {}

try:
    for key in ("LeftShift", "RightShift"):
        state.down = lambda name: name == key
        state.update_walk_speed()
        start = unreal.Vector(440, 240, 88)
        pawn.set_actor_location(start, False, True)
        state.previous_position = start
        state.last_safe = start
        # Deliberately bypass the native sweep through Bedroom 3's west wall.
        pawn.set_actor_location(unreal.Vector(300, 240, 88), False, True)
        state.validate_human_displacement()
        report[key + "_crossing_rejected"] = (
            (pawn.get_actor_location() - start).length() < 0.1
            and pawn.get_actor_enable_collision()
            and movement.get_editor_property("max_walk_speed") == 320.0
        )
    state.down = lambda name: False
    state.update_walk_speed()
    report["release_restores_walk"] = (
        movement.get_editor_property("max_walk_speed") == 180.0
    )
    # The safeguard must accept every planned corridor/doorway segment, not
    # merely reject walls. Furniture is checked by the separate scene validator.
    root = Path(__file__).resolve().parents[2]
    with gzip.open(root / "assets/unreal-export/scene.json.gz", "rt") as stream:
        routes = json.load(stream)["routes"]
    route_failures = []
    for route_name, points in routes.items():
        for first, second in zip(points, points[1:]):
            state.previous_position = unreal.Vector(first[0] * 100, first[1] * 100, 88)
            end = unreal.Vector(second[0] * 100, second[1] * 100, 88)
            pawn.set_actor_location(end, False, True)
            state.validate_human_displacement()
            if (pawn.get_actor_location() - end).length() > 0.1:
                route_failures.append(route_name)
    report["all_eleven_routes_accepted"] = len(routes) == 11 and not route_failures
    movement.set_movement_mode(unreal.MovementMode.MOVE_FLYING)
    state.ensure_human_collision()
    report["unexpected_flight_recovered"] = (
        movement.get_editor_property("movement_mode")
        == unreal.MovementMode.MOVE_FALLING
    )
    movement.set_updated_component(None)
    state.ensure_human_collision()
    report["detached_movement_recovered"] = movement.get_editor_property(
        "updated_component"
    ) == pawn.get_editor_property("capsule_component")
    state.set_creative(True)
    outside = unreal.Vector(-100, 240, 180)
    pawn.set_actor_location(outside, False, True)
    state.validate_human_displacement()
    report["explicit_creative_still_works"] = (
        pawn.get_actor_location() - outside
    ).length() < 0.1
    state.set_creative(False)
    report["return_from_creative_safe"] = (
        pawn.get_actor_enable_collision()
        and (pawn.get_actor_location() - state.last_safe).length() < 0.1
    )
finally:
    state.down = original_down
    state.update_walk_speed()
    pawn.set_actor_location(original, False, True)
    movement.stop_movement_immediately()
    state.last_safe = original
    state.previous_position = original

report["passed"] = all(report.values())
(
    Path(__file__).resolve().parents[2] / "docs/unreal/running-safety-validation.json"
).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
print(json.dumps(report))
if not report["passed"]:
    raise RuntimeError("Running safety regression failed")
