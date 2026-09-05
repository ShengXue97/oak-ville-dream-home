"""Render an interior preview without taking focus or moving the editor camera."""

from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parents[1]
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if levels.is_in_play_in_editor():
    raise RuntimeError("Stop Play before capturing")
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
capture = actors.spawn_actor_from_class(
    unreal.SceneCapture2D,
    unreal.Vector(280, 330, 160),
    unreal.Rotator(pitch=-12, yaw=-145, roll=0),
)
component = capture.get_component_by_class(unreal.SceneCaptureComponent2D)
target = unreal.RenderingLibrary.create_render_target2d(
    world, 1280, 720, unreal.TextureRenderTargetFormat.RTF_RGBA8
)
component.set_editor_property("texture_target", target)
component.set_editor_property(
    "capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR
)
component.set_editor_property("fov_angle", 65.0)
component.set_editor_property("capture_every_frame", False)
component.set_editor_property("always_persist_rendering_state", True)
settings = component.get_editor_property("post_process_settings")
settings.set_editor_property("override_dynamic_global_illumination_method", True)
settings.set_editor_property(
    "dynamic_global_illumination_method", unreal.DynamicGlobalIlluminationMethod.LUMEN
)
settings.set_editor_property("override_reflection_method", True)
settings.set_editor_property("reflection_method", unreal.ReflectionMethod.LUMEN)
component.set_editor_property("post_process_settings", settings)
component.capture_scene()
count = 0


def finish(delta):
    global count
    count += 1
    component.capture_scene()
    if count not in {24, 48, 72}:
        return
    output = ROOT / "renders/unreal"
    output.mkdir(parents=True, exist_ok=True)
    unreal.RenderingLibrary.export_render_target(
        world,
        target,
        str(output),
        {
            24: "living-offscreen.png",
            48: "corridor-offscreen.png",
            72: "bedroom3-offscreen.png",
        }[count],
    )
    if count == 24:
        capture.set_actor_location(unreal.Vector(670, 395, 160), False, False)
        capture.set_actor_rotation(unreal.Rotator(pitch=-8, yaw=0, roll=0), False)
        return
    if count == 48:
        position = unreal.Vector(580, 305, 160)
        capture.set_actor_location(position, False, False)
        capture.set_actor_rotation(
            unreal.MathLibrary.make_rot_from_x(unreal.Vector(495, 120, 105) - position),
            False,
        )
        return
    unreal.unregister_slate_post_tick_callback(handle)
    actors.destroy_actor(capture)
    levels.save_current_level()
    print("Saved living, corridor and Bedroom 3 previews")


handle = unreal.register_slate_post_tick_callback(finish)
