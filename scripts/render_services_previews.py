"""Render service fittings from the saved Blender file without modifying it."""

from pathlib import Path
import sys

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
VIEWS = {
    "bathroom_window": ((7.65, -5.35, 1.6), (7.2, -6.4, 1.98)),
    "bedroom_aircon": ((5.1, -1.45, 1.6), (4.55, -3.175, 2.17)),
    "condenser": ((9.35, -7.52, 1.35), (9.9, -7.01, 0.48)),
    "kitchen_approach": ((3.0, -5.9, 1.6), (4.7, -6.7, 0.90)),
}
scene = bpy.data.scenes["Oak_Ville"]
bpy.context.window.scene = scene
scene.render.engine = "CYCLES"
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.cycles.denoiser = "OPENIMAGEDENOISE"
scene.cycles.denoising_use_gpu = False
scene.render.resolution_x = 960
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
for layer in scene.view_layers:
    layer.use = layer.name == "Enclosed_Walkthrough"
output = ROOT / "renders/services"
output.mkdir(parents=True, exist_ok=True)
for name, (eye, target) in VIEWS.items():
    requested = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    if requested and name not in requested:
        continue
    data = bpy.data.cameras.new("REVIEW_" + name)
    camera = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(camera)
    camera.location = Vector(eye)
    camera.rotation_euler = (
        (Vector(target) - camera.location).to_track_quat("-Z", "Y").to_euler()
    )
    data.lens = 30
    data.clip_start = 0.01
    scene.camera = camera
    scene.render.filepath = str(output / (name + ".png"))
    bpy.ops.render.render(write_still=True)
    print("SERVICES_PREVIEW_COMPLETE", name, flush=True)
