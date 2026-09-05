"""Refresh changed preview cameras, schedules and the dimensioned SVG in Blender."""

import csv
import json
import math
import runpy
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
views = {
    "PREVIEW_Entry": ((2.7, 6.55, 1.6), (3.2, 5.68, 1.6)),
    "PREVIEW_Bedroom_3": ((5.8, 3.05, 1.6), (4.95, 1.2, 1.05)),
    "PREVIEW_Service_Yard": ((6.4, 7.65, 1.6), (6.5, 8.5, 1.1)),
}
for route in bpy.data.scenes["Oak_Ville"].objects:
    if route.get("route_points_plan_m"):
        points = json.loads(route["route_points_plan_m"])
        first, second = points[:2]
        if route.name.startswith(("W03", "W11")):
            first, second = points[1], points[-1]
        views["EYE_" + route.name] = ((*first, 1.6), (*second, 1.6))
for name, (position, target) in views.items():
    obj = bpy.data.objects.get(name)
    if obj:
        obj.location = (position[0], -position[1], position[2])
        direction = Vector((target[0], -target[1], target[2])) - obj.location
        obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
namespace = runpy.run_path(str(ROOT / "scripts/build_oak_ville.py"))[
    "build"
].__globals__
exec((ROOT / "scripts/validate_model.py").read_text(), namespace)
exec((ROOT / "scripts/designer_documents.py").read_text(), namespace)
namespace["write_designer_documents"]()
specs = json.loads((ROOT / "assets/architecture/door-layout.json").read_text())
with (ROOT / "docs/schedules/door-schedule.csv").open("w", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(
        [
            "room",
            "opening_m",
            "between_frames_m",
            "clear_head_m",
            "open_degrees",
            "hinge_end",
            "evidence",
        ]
    )
    for room, spec in specs.items():
        width = spec["end_m"] - spec["start_m"]
        writer.writerow(
            [
                room,
                round(width, 3),
                round(width - 0.06, 3),
                2.12,
                spec["open_angle_blender"],
                spec["hinge_end"],
                spec["direction"],
            ]
        )
with (ROOT / "docs/schedules/camera-schedule.csv").open("w", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(
        ["camera", "x_m", "plan_y_m", "eye_z_m", "horizontal_fov_deg", "purpose"]
    )
    for obj in sorted(bpy.data.scenes["Oak_Ville"].objects, key=lambda item: item.name):
        if obj.type == "CAMERA":
            writer.writerow(
                [
                    obj.name,
                    round(obj.location.x, 3),
                    round(-obj.location.y, 3),
                    round(obj.location.z, 3),
                    round(math.degrees(obj.data.angle_x), 2),
                    (
                        "Orthographic inspection"
                        if obj.data.type == "ORTHO"
                        else "Human eye-level"
                    ),
                ]
            )
