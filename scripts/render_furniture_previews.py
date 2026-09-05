"""Render close furniture reviews from the saved model without saving changes."""

import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.data.scenes["Oak_Ville"]
bpy.context.window.scene = scene
views = {
    "sofa": ((2.45, -3.20, 1.35), (0.62, -1.95, 0.57)),
    "dining": ((5.85, -6.00, 1.45), (4.60, -5.02, 0.57)),
    "bedroom": ((5.80, -3.05, 1.60), (5.0, -1.15, 0.70)),
    "kitchen_sink": ((4.96, -7.55, 1.58), (4.93, -8.45, 0.83)),
    "toilet": ((7.60, -5.22, 1.22), (6.94, -6.00, 0.42)),
    "vanity": ((7.48, -4.93, 1.48), (8.27, -4.93, 0.95)),
    "washer": ((6.45, -7.53, 1.12), (6.49, -8.48, 0.47)),
}
requested = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else list(views)
scene.render.engine = "CYCLES"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.cycles.denoiser = "OPENIMAGEDENOISE"
scene.cycles.denoising_use_gpu = False
scene.render.resolution_x = 1000
scene.render.resolution_y = 800
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"
for layer in scene.view_layers:
    layer.use = layer.name == "Enclosed_Walkthrough"
output = ROOT / "renders/furniture"
output.mkdir(parents=True, exist_ok=True)
for name in requested:
    eye, target = (Vector(point) for point in views[name])
    data = bpy.data.cameras.new("REVIEW_" + name)
    camera = bpy.data.objects.new(data.name, data)
    scene.collection.objects.link(camera)
    camera.location = eye
    camera.rotation_euler = (target - eye).to_track_quat("-Z", "Y").to_euler()
    data.lens = 38
    data.clip_start = 0.01
    scene.camera = camera
    scene.render.filepath = str(output / (name + ".png"))
    bpy.ops.render.render(write_still=True)
    print("FURNITURE_PREVIEW_COMPLETE", name, flush=True)
