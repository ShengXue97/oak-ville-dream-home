"""Persist an eye-level camera attached to the capsule, independent of animation."""

import unreal

if unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor():
    raise RuntimeError("Stop Play before repairing the saved camera hierarchy")

blueprint = unreal.load_asset("/Game/FirstPerson/Blueprints/BP_FirstPersonCharacter")
subsystem = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
library = unreal.SubobjectDataBlueprintFunctionLibrary
handles = subsystem.k2_gather_subobject_data_for_blueprint(blueprint)
objects = [(handle, library.get_object(library.get_data(handle))) for handle in handles]
capsule_handle = next(
    h for h, obj in objects if isinstance(obj, unreal.CapsuleComponent)
)
# Use a dedicated camera so template mesh/socket initialization cannot reclaim it.
camera = next(
    (
        obj
        for _, obj in objects
        if obj.get_name().startswith("WalkthroughCamera")
        or obj.get_name() == "Camera_GEN_VARIABLE"
    ),
    None,
)
if camera is not None and camera.get_name() == "Camera_GEN_VARIABLE":
    subsystem.rename_subobject(
        next(h for h, obj in objects if obj == camera), "WalkthroughCamera"
    )
if camera is None:
    params = unreal.AddNewSubobjectParams()
    params.set_editor_property("blueprint_context", blueprint)
    params.set_editor_property("parent_handle", capsule_handle)
    params.set_editor_property("new_class", unreal.CameraComponent)
    handle, failure = subsystem.add_new_subobject(params)
    if str(failure):
        raise RuntimeError(str(failure))
    subsystem.rename_subobject(handle, "WalkthroughCamera")
    camera = library.get_object(library.get_data(handle))
for _, old_camera in objects:
    if isinstance(old_camera, unreal.CameraComponent) and old_camera != camera:
        old_camera.set_editor_property("auto_activate", False)
camera.set_editor_property("relative_location", unreal.Vector(0, 0, 72))
camera.set_editor_property("relative_rotation", unreal.Rotator(0, 0, 0))
camera.set_editor_property("use_pawn_control_rotation", True)
camera.set_editor_property("auto_activate", True)
camera.set_field_of_view(65.0)

unreal.BlueprintEditorLibrary.compile_blueprint(blueprint)
unreal.EditorAssetLibrary.save_loaded_asset(blueprint, only_if_is_dirty=False)
print("Saved capsule-attached camera at 72 cm above the character origin")
