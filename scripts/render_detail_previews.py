"""Render close-ups of the repaired details in background Blender; never save."""

from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.data.scenes["Oak_Ville"]
bpy.context.window.scene = scene
for layer in scene.view_layers:
    layer.use = layer.name == "Enclosed_Walkthrough"
scene.render.engine = "CYCLES"
scene.cycles.samples = 32
scene.cycles.use_denoising = True
scene.cycles.denoiser = "OPENIMAGEDENOISE"
scene.cycles.denoising_use_gpu = False
scene.render.resolution_x = 1000
scene.render.resolution_y = 850
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = "PNG"

hinge = bpy.data.objects["Bedroom_2_Door_Hinge"]
lever = bpy.data.objects["Bedroom_2_Door_Handle_Back_Lever"]
target = lever.matrix_world @ (sum((Vector(v) for v in lever.bound_box), Vector()) / 8)
door_eye = target + hinge.matrix_world.to_3x3() @ Vector((-0.18, -0.55, 0.18))
views = [
    ("DETAIL_Attached_Door_Handle", door_eye, target),
    (
        "DETAIL_Dining_Plant_Clearance",
        Vector((4.88, -6.55, 1.65)),
        Vector((5.76, -5.84, 0.78)),
    ),
]
for name, eye, target in views:
    data = bpy.data.cameras.new(name)
    camera = bpy.data.objects.new(name, data)
    scene.collection.objects.link(camera)
    camera.location = eye
    camera.rotation_euler = (target - eye).to_track_quat("-Z", "Y").to_euler()
    data.lens = 48
    data.clip_start = 0.01
    scene.camera = camera
    scene.render.filepath = str(ROOT / "renders" / (name + ".png"))
    bpy.ops.render.render(write_still=True)
