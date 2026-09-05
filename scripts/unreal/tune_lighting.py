"""Initial exposure and local-light tuning; run deliberately, not during sync."""

import unreal

if unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor():
    raise RuntimeError("Stop Play before tuning lighting")
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
if not any(
    a.get_component_by_class(unreal.DirectionalLightComponent)
    for a in actors.get_all_level_actors()
):
    daylight = actors.spawn_actor_from_class(
        unreal.DirectionalLight,
        unreal.Vector(0, 0, 500),
        unreal.Rotator(pitch=-35, yaw=60, roll=0),
    )
    daylight.set_actor_label("Daylight_Sun")
    daylight.set_folder_path("Lighting")
    daylight.get_component_by_class(unreal.DirectionalLightComponent).set_mobility(
        unreal.ComponentMobility.MOVABLE
    )
for actor in actors.get_all_level_actors():
    light = actor.get_component_by_class(unreal.RectLightComponent)
    if light:
        light.set_editor_property("attenuation_radius", 280.0)
        light.set_intensity(350.0)
    sun = actor.get_component_by_class(unreal.DirectionalLightComponent)
    if sun:
        sun.set_intensity(2500)
        sun.set_editor_property("atmosphere_sun_light", True)
    sky = actor.get_component_by_class(unreal.SkyLightComponent)
    if sky:
        sky.set_editor_property("real_time_capture", True)
        sky.recapture_sky()
volume = next(
    (
        actor
        for actor in actors.get_all_level_actors()
        if actor.get_actor_label() == "Exposure_Control"
    ),
    None,
)
if not volume:
    volume = actors.spawn_actor_from_class(
        unreal.PostProcessVolume, unreal.Vector(0, 0, 0)
    )
    volume.set_actor_label("Exposure_Control")
    volume.set_folder_path("Lighting")
volume.set_editor_property("unbound", True)
settings = volume.get_editor_property("settings")
settings.set_editor_property("override_dynamic_global_illumination_method", True)
settings.set_editor_property(
    "dynamic_global_illumination_method", unreal.DynamicGlobalIlluminationMethod.LUMEN
)
settings.set_editor_property("override_reflection_method", True)
settings.set_editor_property("reflection_method", unreal.ReflectionMethod.LUMEN)
settings.set_editor_property("override_auto_exposure_method", True)
settings.set_editor_property(
    "auto_exposure_method", unreal.AutoExposureMethod.AEM_HISTOGRAM
)
settings.set_editor_property("override_auto_exposure_min_brightness", True)
settings.set_editor_property("override_auto_exposure_max_brightness", True)
# This project uses the legacy luminance range, not EV100 values. Locking
# both limits to 32 reduces exposure by two stops relative to luminance 8.
settings.set_editor_property("auto_exposure_min_brightness", 32.0)
settings.set_editor_property("auto_exposure_max_brightness", 32.0)
settings.set_editor_property("override_auto_exposure_bias", True)
settings.set_editor_property("auto_exposure_bias", 0.0)
settings.set_editor_property("override_bloom_intensity", True)
settings.set_editor_property("bloom_intensity", 0.12)
settings.set_editor_property("override_motion_blur_amount", True)
settings.set_editor_property("motion_blur_amount", 0.0)
volume.set_editor_property("settings", settings)
unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
unreal.SystemLibrary.execute_console_command(world, "t.MaxFPS 60")
print("Lighting ranges and fixed exposure applied")
