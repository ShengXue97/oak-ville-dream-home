"""Use Epic's native First Person Blueprint input and CharacterMovement."""

import unreal

levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if levels.is_in_play_in_editor():
    raise RuntimeError("Stop Play before switching the controller")
registry = unreal.AssetRegistryHelpers.get_asset_registry()
registry.scan_paths_synchronous(
    ["/Game/FirstPerson", "/Game/Input", "/Game/Characters"], force_rescan=True
)
base = "/Game/FirstPerson/Blueprints/"
pawn_bp = unreal.load_asset(base + "BP_FirstPersonCharacter")
controller_bp = unreal.load_asset(base + "BP_FirstPersonPlayerController")
for bp in (pawn_bp, controller_bp):
    unreal.BlueprintEditorLibrary.compile_blueprint(bp)
pawn_class = unreal.load_class(
    None, base + "BP_FirstPersonCharacter.BP_FirstPersonCharacter_C"
)
controller_class = unreal.load_class(
    None, base + "BP_FirstPersonPlayerController.BP_FirstPersonPlayerController_C"
)
pawn = unreal.get_default_object(pawn_class)
pawn.get_editor_property("capsule_component").set_capsule_size(25, 86)
pawn.set_editor_property("base_eye_height", 72.0)
pawn.set_editor_property("jump_max_count", 1)
pawn.set_editor_property("jump_max_hold_time", 0.0)
movement = pawn.get_editor_property("character_movement")
for key, value in {
    "gravity_scale": 1.0,
    "jump_z_velocity": 260.0,
    "air_control": 0.15,
    "max_walk_speed": 180.0,
    "max_acceleration": 1000.0,
    "ground_friction": 8.0,
    "braking_deceleration_walking": 1200.0,
    "max_step_height": 18.0,
    "max_fly_speed": 250.0,
}.items():
    movement.set_editor_property(key, value)
movement.set_editor_property(
    "default_land_movement_mode", unreal.MovementMode.MOVE_WALKING
)
subobjects = unreal.get_engine_subsystem(unreal.SubobjectDataSubsystem)
for handle in subobjects.k2_gather_subobject_data_for_blueprint(pawn_bp):
    data = unreal.SubobjectDataBlueprintFunctionLibrary.get_data(handle)
    obj = unreal.SubobjectDataBlueprintFunctionLibrary.get_object(data)
    if isinstance(obj, unreal.CameraComponent):
        obj.set_field_of_view(65.0)
        obj.set_editor_property("use_pawn_control_rotation", True)
    if isinstance(obj, unreal.SkeletalMeshComponent):
        obj.set_visibility(False, True)
        obj.set_hidden_in_game(True, True)
        obj.set_cast_shadow(False)
unreal.BlueprintEditorLibrary.compile_blueprint(pawn_bp)
unreal.EditorAssetLibrary.save_loaded_asset(pawn_bp, only_if_is_dirty=False)
unreal.EditorAssetLibrary.save_loaded_asset(controller_bp, only_if_is_dirty=False)
mode_bp = unreal.load_asset("/Game/OakVille/Blueprints/BP_OakVilleGameMode")
unreal.BlueprintEditorLibrary.compile_blueprint(mode_bp)
mode_class = unreal.load_class(
    None, "/Game/OakVille/Blueprints/BP_OakVilleGameMode.BP_OakVilleGameMode_C"
)
mode = unreal.get_default_object(mode_class)
mode.set_editor_property("default_pawn_class", pawn_class)
mode.set_editor_property("player_controller_class", controller_class)
unreal.BlueprintEditorLibrary.compile_blueprint(mode_bp)
unreal.EditorAssetLibrary.save_loaded_asset(mode_bp, only_if_is_dirty=False)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
for actor in actors.get_all_level_actors():
    if isinstance(actor, unreal.PlayerStart):
        actor.set_actor_location(unreal.Vector(270, 655, 88), False, False)
        actor.set_actor_rotation(unreal.Rotator(pitch=0, yaw=-60, roll=0), False)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
world.get_world_settings().set_editor_property("default_game_mode", mode_class)
levels.save_current_level()
print("Epic First Person character and controller configured")
