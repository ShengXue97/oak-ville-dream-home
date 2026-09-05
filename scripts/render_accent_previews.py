"""Render two colour reviews from the saved Blender source, without saving it."""

from pathlib import Path
import bpy

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.data.scenes["Oak_Ville"]
bpy.context.window.scene = scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 20
scene.cycles.use_denoising = True
scene.cycles.denoising_use_gpu = False
scene.render.resolution_x = 960
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
for layer in scene.view_layers:
    layer.use = layer.name == "Enclosed_Walkthrough"
output = ROOT / "renders/accents"
output.mkdir(parents=True, exist_ok=True)
for name in ("PREVIEW_Living_Eye", "PREVIEW_Main_Bedroom"):
    scene.camera = bpy.data.objects[name]
    scene.render.filepath = str(output / (name + ".png"))
    bpy.ops.render.render(write_still=True)
