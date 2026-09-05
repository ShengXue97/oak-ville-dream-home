"""Matching eye-level material comparisons; never saves the source model."""
from pathlib import Path
import sys
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from style_switch import set_style, STYLES

scene = bpy.data.scenes["Oak_Ville"]
bpy.context.window.scene = scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 16
scene.cycles.use_denoising = True
scene.cycles.denoising_use_gpu = False
scene.render.resolution_x = 960
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
for layer in scene.view_layers:
    layer.use = layer.name == "Enclosed_Walkthrough"
output = ROOT / "renders/styles"
output.mkdir(parents=True, exist_ok=True)
for style in STYLES:
    set_style(style)
    for name in ("PREVIEW_Living_Eye", "PREVIEW_Main_Bedroom"):
        scene.camera = bpy.data.objects[name]
        scene.render.filepath = str(output / (style + "__" + name + ".png"))
        bpy.ops.render.render(write_still=True)
