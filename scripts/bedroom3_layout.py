"""Correct Bedroom 3 furniture at true size; preserve object IDs and materials."""

import json
import bpy


def resize_mesh(obj, dimensions):
    size = [
        max(v.co[i] for v in obj.data.vertices)
        - min(v.co[i] for v in obj.data.vertices)
        for i in range(3)
    ]
    for vertex in obj.data.vertices:
        for axis in range(3):
            vertex.co[axis] *= dimensions[axis] / size[axis]
    obj.data.update()


def apply():
    specs = {
        "Bed_Base": ((5.60, 1.2, 0.22), (0.98, 2.0, 0.32)),
        "Mattress": ((5.60, 1.2, 0.48), (0.90, 1.90, 0.25)),
        "Upholstered_Headboard": ((5.60, 0.19, 0.70), (1.06, 0.10, 1.10)),
        "Duvet": ((5.60, 1.40, 0.635), (0.915, 1.45, 0.12)),
        "Pillow_1": ((5.60, 0.53, 0.68), (0.59, 0.39, 0.15)),
        "Folded_Throw": ((5.60, 1.85, 0.705), (0.925, 0.43, 0.045)),
        "Desk": ((4.32, 3.04, 0.745), (1.40, 0.45, 0.055)),
        "Desk_Leg": ((3.72, 3.04, 0.36), (0.055, 0.38, 0.72)),
        "Desk_Leg.001": ((4.92, 3.04, 0.36), (0.055, 0.38, 0.72)),
    }
    for suffix, (position, dimensions) in specs.items():
        obj = bpy.data.objects["Bedroom_3_" + suffix]
        obj.location = (position[0], -position[1], position[2])
        resize_mesh(obj, dimensions)
    for suffix in ("Wardrobe_Carcass", "Wardrobe_Recessed_Plinth"):
        bpy.data.objects["Bedroom_3_" + suffix].location.x = 3.78
    for obj in bpy.data.objects:
        if obj.name.startswith("Bedroom_3_Wardrobe_Front_"):
            obj.location.x = 4.066
    for suffix in ("Desk_Stool", "Stool_Base"):
        obj = bpy.data.objects["Bedroom_3_" + suffix]
        obj.location.x, obj.location.y = 4.32, -3.04
    bpy.context.view_layer.update()
    for proxy in bpy.data.objects:
        source_name = proxy.get("source_object", "")
        if source_name.startswith("Bedroom_3_") and source_name in bpy.data.objects:
            source = bpy.data.objects[source_name]
            dimensions = [
                max(v[i] for v in source.bound_box)
                - min(v[i] for v in source.bound_box)
                for i in range(3)
            ]
            resize_mesh(proxy, dimensions)
            proxy.matrix_world = source.matrix_world.copy()
    route = bpy.data.objects.get("W05_Bedroom_3")
    if route:
        points = [(5.85, 3.9), (5.85, 2.5), (4.7, 2.5), (4.7, 1.0)]
        route["route_points_plan_m"] = json.dumps(points)
        route.data.splines.clear()
        spline = route.data.splines.new("POLY")
        spline.points.add(len(points) - 1)
        for point, (x, y) in zip(spline.points, points):
            point.co = (x, -y, 0.035, 1)
    bpy.context.view_layer.update()


if __name__ == "__main__":
    apply()
