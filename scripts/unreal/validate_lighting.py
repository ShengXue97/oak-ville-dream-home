"""Check saved lighting settings, material assignments and retained architecture collision."""

import json
from pathlib import Path

import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parents[1]
profile = json.loads((ROOT / "assets/unreal/lighting-profile.json").read_text())
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
volume = next(a for a in actors if a.get_actor_label() == "Exposure_Control")
settings = volume.get_editor_property("settings")
errors = []
for key, expected in profile["post_process"].items():
    actual = settings.get_editor_property(key)
    if (
        not settings.get_editor_property("override_" + key)
        or abs(actual - expected) > 0.001
    ):
        errors.append(f"Post process mismatch: {key}: {actual}")
walls = 0
meshes = 0
for actor in actors:
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    if not component or not component.static_mesh:
        continue
    if not any(str(t).startswith("BlenderID:") for t in actor.tags):
        continue
    meshes += 1
    if component.get_material(0) is None:
        errors.append(f"Missing material: {actor.get_actor_label()}")
    if str(actor.get_folder_path()) == "Architecture":
        walls += 1
        if (
            not actor.get_actor_enable_collision()
            or component.get_collision_response_to_channel(
                unreal.CollisionChannel.ECC_PAWN
            )
            != unreal.CollisionResponseType.ECR_BLOCK
        ):
            errors.append(f"Architecture collision disabled: {actor.get_actor_label()}")
        if (
            unreal.get_editor_subsystem(
                unreal.StaticMeshEditorSubsystem
            ).get_simple_collision_count(component.static_mesh)
            == 0
        ):
            errors.append(f"Missing collision shape: {actor.get_actor_label()}")
report = {
    "post_process_values_match": not errors,
    "managed_meshes": meshes,
    "architecture_bodies_checked": walls,
    "errors": errors,
    "passed": not errors,
}
(ROOT / "docs/unreal/lighting-integrity-validation.json").write_text(
    json.dumps(report, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(report))
if errors:
    raise RuntimeError("Lighting validation failed")
