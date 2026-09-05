"""Keep the engine-specific lighting calibration with the editable Blender source."""

from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
profile = ROOT / "assets/unreal/lighting-profile.json"
block = bpy.data.texts.get("UNREAL_LIGHTING_PROFILE.json") or bpy.data.texts.new(
    "UNREAL_LIGHTING_PROFILE.json"
)
block.clear()
block.write(profile.read_text(encoding="utf-8"))
bpy.context.scene["unreal_lighting_profile"] = "//assets/unreal/lighting-profile.json"
bpy.context.scene["unreal_lighting_note"] = (
    "Engine-specific visual calibration; Blender lighting remains the style reference. "
    "Run scripts/unreal/tune_lighting.py deliberately; geometry sync preserves it."
)
