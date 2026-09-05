"""Capture the editor viewport without moving the system mouse or focus."""

from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parents[1]
output = ROOT / "renders/unreal"
output.mkdir(parents=True, exist_ok=True)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
if unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor():
    raise RuntimeError("Stop Play before capturing editor previews")
camera = next(
    (
        a
        for a in actors.get_all_level_actors()
        if a.get_actor_label() == "Preview_Entry"
    ),
    None,
)
if camera is None:
    camera = actors.spawn_actor_from_class(
        unreal.CameraActor,
        unreal.Vector(270, 705, 160),
        unreal.Rotator(pitch=0, yaw=-90, roll=0),
    )
    camera.set_actor_label("Preview_Entry")
    camera.set_folder_path("Walkthrough")
camera.get_component_by_class(unreal.CameraComponent).set_field_of_view(65)
camera.set_actor_location(unreal.Vector(150, 330, 160), False, False)
camera.set_actor_rotation(unreal.Rotator(pitch=0, yaw=-65, roll=0), False)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.AutomationLibrary.take_high_res_screenshot(
    1280, 720, str(output / "living-preview.png"), camera=camera, delay=0.0
)
