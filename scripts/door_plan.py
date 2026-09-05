"""Apply audited hinge sides and opening directions without rebuilding rooms."""

import json
import math
from pathlib import Path
import bpy
from mathutils import Matrix

ROOT = Path(__file__).resolve().parents[1]


def apply():
    specs = json.loads((ROOT / "assets/architecture/door-layout.json").read_text())
    for room, spec in specs.items():
        pivot = bpy.data.objects.get(room + "_Door_Hinge")
        if pivot is None:
            continue
        along = (
            spec["end_m"] - 0.03
            if spec["hinge_end"] == "end"
            else spec["start_m"] + 0.03
        )
        pivot.location = (
            (along, -spec["fixed_m"], 0)
            if spec["axis"] == "h"
            else (spec["fixed_m"], -along, 0)
        )
        desired_flip = 180 if spec["hinge_end"] == "end" else 0
        for child in pivot.children:
            delta = desired_flip - child.get("plan_hinge_flip_degrees", 0)
            if delta:
                child.matrix_basis = (
                    Matrix.Rotation(math.radians(delta), 4, "Z") @ child.matrix_basis
                )
            child["plan_hinge_flip_degrees"] = desired_flip
        pivot["open_angle_degrees"] = spec["open_angle_blender"]
        pivot["plan_hinge_end"] = spec["hinge_end"]
        pivot["plan_swing_note"] = spec["direction"]
        if room == "Entry":
            pivot["door_state"] = "CLOSED"
            pivot.rotation_euler.z = 0
        if pivot.get("door_state") == "OPEN":
            pivot.rotation_euler.z = math.radians(spec["open_angle_blender"])
    routes = {
        "W01_entry-dining": [(2.7, 6.55), (2.7, 6.3), (3.0, 5.9), (3.0, 4.9)],
        "W10_service_yard": [(4.7, 7.7), (5.25, 7.7), (6.25, 7.7), (6.4, 7.65)],
    }
    for name, points in routes.items():
        route = bpy.data.objects.get(name)
        if route:
            route["route_points_plan_m"] = json.dumps(points)
            for point, (x, y) in zip(route.data.splines[0].points, points):
                point.co = (x, -y, 0.035, 1)
    bpy.context.view_layer.update()
    # Existing inspection collision proxies follow the corrected source pose.
    for proxy in bpy.data.objects:
        source_name = proxy.get("source_object")
        if source_name and "Door_" in source_name and source_name in bpy.data.objects:
            source = bpy.data.objects[source_name]
            proxy.matrix_world = source.matrix_world.copy()
    return specs


if __name__ == "__main__":
    apply()
