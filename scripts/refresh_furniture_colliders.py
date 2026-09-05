"""Refresh existing inspection proxies after an in-place furniture refinement."""

import bpy
from mathutils import Vector


def refresh():
    count = 0
    for proxy in bpy.data.objects:
        source = bpy.data.objects.get(proxy.get("source_object", ""))
        if source is None or not source.get("furniture_revision"):
            continue
        low = [min(v[axis] for v in source.bound_box) for axis in range(3)]
        high = [max(v[axis] for v in source.bound_box) for axis in range(3)]
        corners = [
            (x, y, z)
            for z in (low[2], high[2])
            for y in (low[1], high[1])
            for x in (low[0], high[0])
        ]
        for vertex, point in zip(proxy.data.vertices, corners):
            vertex.co = Vector(point)
        proxy.matrix_world = source.matrix_world.copy()
        count += 1
    bpy.context.view_layer.update()
    return {"refreshed_proxies": count}


if __name__ == "__main__":
    print(refresh())
