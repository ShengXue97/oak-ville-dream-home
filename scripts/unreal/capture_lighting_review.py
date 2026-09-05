"""Capture repeatable lighting comparisons without moving the user's viewport."""

from pathlib import Path

import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parents[1]
VIEWS = [
    ("dining", (290, 645, 160), (440, 540, 125)),
    ("living_window", (255, 330, 160), (155, 50, 140)),
    ("bedroom_window", (580, 305, 160), (495, 120, 105)),
    ("corridor", (670, 395, 160), (960, 395, 140)),
    ("dining_kitchen", (270, 430, 160), (460, 630, 135)),
]


def run(label):
    """Write matched views under renders/unreal/lighting/<label>."""
    global CAPTURE, COMPONENT, TARGET, HANDLE, FRAME, INDEX, OUTPUT
    levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
    if levels.is_in_play_in_editor():
        raise RuntimeError("Stop Play before capturing lighting")
    actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    OUTPUT = ROOT / "renders/unreal/lighting" / label
    OUTPUT.mkdir(parents=True, exist_ok=True)
    CAPTURE = actors.spawn_actor_from_class(unreal.SceneCapture2D, unreal.Vector())
    COMPONENT = CAPTURE.get_component_by_class(unreal.SceneCaptureComponent2D)
    TARGET = unreal.RenderingLibrary.create_render_target2d(
        world, 1280, 720, unreal.TextureRenderTargetFormat.RTF_RGBA8
    )
    COMPONENT.set_editor_property("texture_target", TARGET)
    COMPONENT.set_editor_property(
        "capture_source", unreal.SceneCaptureSource.SCS_FINAL_COLOR_LDR
    )
    COMPONENT.set_editor_property("fov_angle", 65.0)
    COMPONENT.set_editor_property("capture_every_frame", False)
    COMPONENT.set_editor_property("always_persist_rendering_state", True)
    # Explicitly match the level volume; captures can otherwise use different
    # exposure/GI defaults from the player camera on some engine versions.
    volume = next(
        a
        for a in actors.get_all_level_actors()
        if a.get_actor_label() == "Exposure_Control"
    )
    COMPONENT.set_editor_property(
        "post_process_settings", volume.get_editor_property("settings")
    )
    COMPONENT.set_editor_property("post_process_blend_weight", 1.0)
    FRAME, INDEX = 0, 0
    set_view()
    HANDLE = unreal.register_slate_post_tick_callback(tick)


def set_view():
    _, position, target = VIEWS[INDEX]
    position = unreal.Vector(*position)
    CAPTURE.set_actor_location(position, False, False)
    CAPTURE.set_actor_rotation(
        unreal.MathLibrary.make_rot_from_x(unreal.Vector(*target) - position), False
    )


def tick(delta):
    global FRAME, INDEX
    COMPONENT.capture_scene()
    FRAME += 1
    if FRAME < 60:
        return
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    unreal.RenderingLibrary.export_render_target(
        world, TARGET, str(OUTPUT), VIEWS[INDEX][0] + ".png"
    )
    INDEX += 1
    FRAME = 0
    if INDEX < len(VIEWS):
        set_view()
        return
    unreal.unregister_slate_post_tick_callback(HANDLE)
    unreal.get_editor_subsystem(unreal.EditorActorSubsystem).destroy_actor(CAPTURE)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
    print(f"Lighting previews saved: {OUTPUT}")


if __name__ == "__main__":
    run("review")
