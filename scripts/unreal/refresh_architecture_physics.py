"""Rebind placed architecture to its saved collision without changing geometry."""

import json
from pathlib import Path

import unreal

levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if levels.is_in_play_in_editor():
    raise RuntimeError("Stop Play before refreshing placed physics bodies")
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
names = []
for actor in actors:
    if str(actor.get_folder_path()) not in {
        "Architecture",
        "Ceilings",
        "Beams_Soffits",
    }:
        continue
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    if not component or not component.static_mesh:
        continue
    mesh = component.static_mesh
    overrides = list(component.get_editor_property("override_materials"))
    component.set_static_mesh(None)
    component.set_static_mesh(mesh)
    component.set_editor_property("override_materials", overrides)
    component.set_collision_profile_name("BlockAll")
    actor.set_actor_enable_collision(True)
    names.append(actor.get_actor_label())
levels.save_current_level()
root = Path(__file__).resolve().parents[2]
(root / "docs/unreal/physics-refresh.json").write_text(
    json.dumps({"rebound": names, "geometry_changed": False}, indent=2),
    encoding="utf-8",
)
print("Refreshed", len(names), "placed architectural physics bodies")
