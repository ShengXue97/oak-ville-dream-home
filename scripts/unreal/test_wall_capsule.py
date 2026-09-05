"""Sweep the actual Play character capsule against each wall from both sides.

Run only in a dedicated test session: the player is temporarily repositioned.
Other actors are ignored during each isolated wall test and restored afterward.
"""

import gzip
import json
from pathlib import Path

import unreal
import oakville_runtime as runtime

ROOT = Path(__file__).resolve().parents[2]
state = runtime.STATE
if state is None or state.creative:
    raise RuntimeError("Start a dedicated human-mode test Play session")
pawn, capsule = state.pawn, state.pawn.get_editor_property("capsule_component")
actors = unreal.GameplayStatics.get_all_actors_of_class(
    state.world, unreal.StaticMeshActor
)
by_id = {
    str(tag).removeprefix("BlenderID:"): actor
    for actor in actors
    for tag in actor.tags
    if str(tag).startswith("BlenderID:")
}
with gzip.open(
    ROOT / "assets/unreal-export/scene.json.gz", "rt", encoding="utf-8"
) as stream:
    data = json.load(stream)
original = pawn.get_actor_location()
results = []
try:
    for actor in actors:
        capsule.ignore_actor_when_moving(actor, True)
    for record in data["objects"]:
        size = record["bounds_size_cm"]
        if (
            record["group"] != "Architecture"
            or not record["solid"]
            or min(size[:2]) > 40
            or size[2] < 160
        ):
            continue
        centre = record["location_cm"]
        if centre[2] - size[2] / 2 > 60:
            continue
        target = by_id[record["source_id"]]
        capsule.ignore_actor_when_moving(target, False)
        axis = 0 if size[0] < size[1] else 1
        for side in (-1, 1):
            start = list(centre)
            end = list(centre)
            start[2] = end[2] = 120
            start[axis] += side * (size[axis] / 2 + 40)
            end[axis] -= side * (size[axis] / 2 + 40)
            pawn.set_actor_location(unreal.Vector(*start), False, True)
            pawn.set_actor_location(unreal.Vector(*end), True, False)
            actual = pawn.get_actor_location()
            distance = side * (getattr(actual, "xyz"[axis]) - centre[axis])
            results.append(
                {
                    "wall": record["name"],
                    "side": side,
                    "standoff_cm": round(distance - size[axis] / 2, 3),
                    "passed": distance >= size[axis] / 2 + 24.9,
                }
            )
        capsule.ignore_actor_when_moving(target, True)
finally:
    for actor in actors:
        capsule.ignore_actor_when_moving(actor, False)
    pawn.set_actor_location(original, False, True)
    state.movement.stop_movement_immediately()
report = {
    "method": "Actual Character root capsule swept on Pawn channel in Play, each wall isolated, both directions",
    "checks": results,
    "passed": bool(results) and all(r["passed"] for r in results),
}
(ROOT / "docs/unreal/wall-capsule-validation.json").write_text(
    json.dumps(report, indent=2), encoding="utf-8"
)
print(
    json.dumps(
        {
            "checks": len(results),
            "failed": [r for r in results if not r["passed"]],
            "passed": report["passed"],
        }
    )
)
