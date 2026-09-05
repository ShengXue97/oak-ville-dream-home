"""Apply the editable Unreal lighting translation of the Blender style.

Run deliberately after editing assets/unreal/lighting-profile.json. Ordinary
geometry sync retains these settings. Blender watts and Unreal lumens are not
interchangeable; this profile is a visual calibration, not a lighting survey.
"""

import json
from pathlib import Path

import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parents[1]
PROFILE = json.loads((ROOT / "assets/unreal/lighting-profile.json").read_text())
LEVELS = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
ACTORS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)


def apply():
    if LEVELS.is_in_play_in_editor():
        raise RuntimeError("Stop Play before tuning lighting")
    actors = ACTORS.get_all_level_actors()
    volume = next(a for a in actors if a.get_actor_label() == "Exposure_Control")
    rows = []
    for actor in actors:
        name = actor.get_actor_label()
        light = actor.get_component_by_class(unreal.RectLightComponent)
        if light:
            if "Daylight" in name:
                role = "window"
            elif "Under_Cabinet" in name:
                role = "task"
            elif "Cove" in name:
                role = "cove"
            else:
                role = "ceiling"
            values = PROFILE["lights"][role]
            lumens = PROFILE["overrides_lumens"].get(name, values["lumens"])
            light.set_editor_property("use_temperature", False)
            light.set_light_color(unreal.LinearColor(*values["colour_linear"], 1))
            light.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
            light.set_intensity(lumens)
            light.set_editor_property("attenuation_radius", values["radius_cm"])
            light.set_editor_property("cast_shadows", True)
            light.set_editor_property("indirect_lighting_intensity", 1.0)
            rows.append({"name": name, "role": role, "lumens": lumens})
        sun = actor.get_component_by_class(unreal.DirectionalLightComponent)
        if sun:
            sun.set_light_color(unreal.LinearColor(1, 1, 1, 1))
            sun.set_editor_property("use_temperature", False)
            sun.set_intensity(PROFILE["sun"]["lux"])
            sun.set_editor_property(
                "light_source_angle", PROFILE["sun"]["source_angle_degrees"]
            )
        sky = actor.get_component_by_class(unreal.SkyLightComponent)
        if sky:
            sky.set_intensity(PROFILE["sky_intensity"])
            sky.set_editor_property("real_time_capture", True)
            sky.recapture_sky()
    volume.set_editor_property("unbound", True)
    settings = volume.get_editor_property("settings")
    for key, value in PROFILE["post_process"].items():
        settings.set_editor_property("override_" + key, True)
        settings.set_editor_property(key, value)
    for key, value in {
        "auto_exposure_method": unreal.AutoExposureMethod.AEM_HISTOGRAM,
        "dynamic_global_illumination_method": unreal.DynamicGlobalIlluminationMethod.LUMEN,
        "reflection_method": unreal.ReflectionMethod.LUMEN,
    }.items():
        settings.set_editor_property("override_" + key, True)
        settings.set_editor_property(key, value)
    volume.set_editor_property("settings", settings)
    LEVELS.save_current_level()
    report = {"profile": PROFILE, "lights": rows, "rect_light_count": len(rows)}
    (ROOT / "docs/unreal/lighting-validation.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(
        f"Applied {PROFILE['name']} to {len(rows)} area lights, sun, sky and exposure"
    )


if __name__ == "__main__":
    apply()
