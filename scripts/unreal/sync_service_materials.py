"""Apply the intentional clear-to-frosted bathroom glazing change after sync."""

import unreal

levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if levels.is_in_play_in_editor():
    raise RuntimeError("Stop Play before changing bathroom glazing")
material = unreal.load_asset("/Game/OakVille/Materials/MI_Frosted_Privacy_Glass")
if not material:
    raise RuntimeError("Sync Blender geometry first")
changed = []
for actor in unreal.get_editor_subsystem(
    unreal.EditorActorSubsystem
).get_all_level_actors():
    if actor.get_actor_label() not in {
        "Common_Bath_Vent_Window",
        "Ensuite_Vent_Window",
    }:
        continue
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    old = component.get_material(0)
    if old and old.get_name() not in {"MI_Glass", "MI_Frosted_Privacy_Glass"}:
        unreal.log_warning(
            f"Preserved custom window material on {actor.get_actor_label()}"
        )
        continue
    component.set_material(0, material)
    changed.append(actor.get_actor_label())
levels.save_current_level()
print("Frosted bathroom panes: " + ", ".join(changed))
