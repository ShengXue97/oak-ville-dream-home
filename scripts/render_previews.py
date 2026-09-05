"""Render saved-file previews without changing the live Blender session.

Example:
    blender --background oak-ville.blend --python scripts/render_previews.py \
        -- --camera PREVIEW_Living_Eye

Without --camera, render all PREVIEW_* and EYE_W* cameras plus the top view.
Outputs are reproducible and ignored by Git. No changes are saved to the blend.
"""

import bpy
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.data.scenes["Oak_Ville"]
bpy.context.window.scene = scene
args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
requested = args[args.index("--camera") + 1] if "--camera" in args else None
cameras = [
    obj
    for obj in scene.objects
    if obj.type == "CAMERA"
    and (
        obj.name == requested
        if requested
        else obj.name.startswith(("PREVIEW_", "EYE_W"))
        or obj.name == "PLAN_Orthographic"
    )
]
scene.render.engine = "CYCLES"
scene.cycles.samples = 24
scene.cycles.use_denoising = True
scene.render.image_settings.file_format = "PNG"
scene.render.resolution_x = 960
scene.render.resolution_y = 720
scene.render.resolution_percentage = 100
results = []
for camera_object in sorted(cameras, key=lambda obj: obj.name):
    started = time.time()
    top_view = camera_object.name == "PLAN_Orthographic"
    for layer in scene.view_layers:
        layer.use = layer.name == (
            "Inspection_Cutaway" if top_view else "Enclosed_Walkthrough"
        )
    scene.camera = camera_object
    scene.render.filepath = str(ROOT / "renders" / (camera_object.name + ".png"))
    bpy.ops.render.render(write_still=True)
    results.append(
        {
            "camera": camera_object.name,
            "path": "renders/" + camera_object.name + ".png",
            "seconds": round(time.time() - started, 2),
            "eye_height_m": camera_object.location.z,
            "layer": "Inspection_Cutaway" if top_view else "Enclosed_Walkthrough",
        }
    )
    (ROOT / "renders/render-progress.json").write_text(json.dumps(results, indent=2))
    print("OAK_RENDER_COMPLETE", camera_object.name, flush=True)
