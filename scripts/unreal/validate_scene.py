"""Compare imported actor bounds and test routes with Unreal collision sweeps."""

import gzip
import json
from pathlib import Path

import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parents[1]
with gzip.open(
    ROOT / "assets/unreal-export/scene.json.gz", "rt", encoding="utf-8"
) as stream:
    data = json.load(stream)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if world is None:
    raise RuntimeError("Stop Play before running editor validation")
actors = {
    actor.get_actor_label(): actor
    for actor in unreal.get_editor_subsystem(
        unreal.EditorActorSubsystem
    ).get_all_level_actors()
}
by_id = {
    str(tag).removeprefix("BlenderID:"): actor
    for actor in actors.values()
    for tag in actor.tags
    if str(tag).startswith("BlenderID:")
}
errors = []
max_error_cm = 0
for record in data["objects"]:
    actor = by_id.get(record["source_id"]) or actors.get(record["name"])
    if actor is None:
        errors.append("Missing actor: " + record["name"])
        continue
    centre, extent = actor.get_actor_bounds(False)
    for actual, expected in zip((centre.x, centre.y, centre.z), record["location_cm"]):
        max_error_cm = max(max_error_cm, abs(actual - expected))
    for actual, expected in zip(
        (extent.x * 2, extent.y * 2, extent.z * 2), record["bounds_size_cm"]
    ):
        max_error_cm = max(max_error_cm, abs(actual - expected))
channel = unreal.TraceTypeQuery.ECC_VISIBILITY
draw = unreal.DrawDebugTrace.NONE
routes = []
for name, points in data["routes"].items():
    blocked = []
    unsupported = []
    for index in range(len(points) - 1):
        first, second = points[index : index + 2]
        start = unreal.Vector(first[0] * 100, first[1] * 100, 89)
        end = unreal.Vector(second[0] * 100, second[1] * 100, 89)
        hit = unreal.SystemLibrary.capsule_trace_single(
            world, start, end, 25, 86, channel, False, [], draw
        )
        if hit:
            blocked.append({"segment": index, "hit": str(hit)})
        distance = ((second[0] - first[0]) ** 2 + (second[1] - first[1]) ** 2) ** 0.5
        samples = max(1, int(distance / 0.05) + 1)
        for sample in range(samples + 1):
            t = sample / samples
            x = (first[0] * (1 - t) + second[0] * t) * 100
            y = (first[1] * (1 - t) + second[1] * t) * 100
            floor = unreal.SystemLibrary.line_trace_single(
                world,
                unreal.Vector(x, y, 10),
                unreal.Vector(x, y, -10),
                channel,
                False,
                [],
                draw,
            )
            if floor is None:
                unsupported.append([round(x, 2), round(y, 2)])
    routes.append(
        {
            "name": name,
            "blocked": blocked,
            "unsupported_floor_samples": unsupported,
            "passed": not blocked and not unsupported,
        }
    )
wall_test = unreal.SystemLibrary.line_trace_single(
    world,
    unreal.Vector(200, 200, 120),
    unreal.Vector(-100, 200, 120),
    channel,
    False,
    [],
    draw,
)
pawn_class = unreal.load_class(
    None, "/Game/OakVille/Blueprints/BP_OakVilleWalker.BP_OakVilleWalker_C"
)
pawn = unreal.get_default_object(pawn_class)
capsule = pawn.get_editor_property("capsule_component")
report = {
    "engine_version": unreal.SystemLibrary.get_engine_version(),
    "mesh_count_expected": len(data["objects"]),
    "actor_bounds_max_error_cm": round(max_error_cm, 5),
    "errors": errors,
    "routes": routes,
    "wall_blocks_trace": wall_test is not None,
    "capsule_radius_cm": capsule.get_unscaled_capsule_radius(),
    "capsule_half_height_cm": capsule.get_unscaled_capsule_half_height(),
    "eye_above_capsule_centre_cm": pawn.get_editor_property("base_eye_height"),
    "walk_speed_cm_s": pawn.get_editor_property(
        "character_movement"
    ).get_editor_property("walking_speed"),
}
report["passed"] = (
    not errors
    and max_error_cm < 0.02
    and all(route["passed"] for route in routes)
    and report["wall_blocks_trace"]
)
(ROOT / "docs/unreal/scene-validation.json").write_text(
    json.dumps(report, indent=2), encoding="utf-8"
)
print(
    json.dumps(
        {key: value for key, value in report.items() if key != "routes"}, indent=2
    )
)
if not report["passed"]:
    raise RuntimeError(
        "Unreal validation failed; inspect docs/unreal/scene-validation.json"
    )
