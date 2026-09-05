"""Check that a sync will target the saved Oak Ville editor map safely."""

import unreal

levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if levels.is_in_play_in_editor():
    raise RuntimeError("Stop Play, then run the update again. Nothing has changed.")
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if world is None or world.get_path_name() != "/Game/OakVille/Maps/OakVille.OakVille":
    raise RuntimeError("Open the OakVille map before updating")
dirty = list(unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages())
dirty += list(unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages())
if dirty:
    raise RuntimeError(
        "Save your Unreal edits before updating: "
        + ", ".join(p.get_name() for p in dirty)
    )
print("OakVille is open, saved, and outside Play mode")
