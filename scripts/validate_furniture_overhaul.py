"""Check detailed meshes, their editable attachments and actual sink depth."""

import json
from pathlib import Path

import bmesh
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
scene = bpy.data.scenes["Oak_Ville"]
bpy.context.window.scene = scene
bpy.context.view_layer.update()
objects = [o for o in scene.objects if o.get("furniture_revision")]
invalid = []
attachments = []
triangles = 0
for obj in objects:
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    if (
        any(not edge.is_manifold for edge in mesh.edges)
        or mesh.calc_volume(signed=True) <= 0
    ):
        invalid.append(obj.name)
    mesh.free()
    evaluated = obj.evaluated_get(bpy.context.evaluated_depsgraph_get())
    evaluated_mesh = evaluated.to_mesh()
    evaluated_mesh.calc_loop_triangles()
    triangles += len(evaluated_mesh.loop_triangles)
    evaluated.to_mesh_clear()
    if obj.get("assembly_source") and (
        not obj.parent or obj.parent.name != obj["assembly_source"]
    ):
        attachments.append(obj.name)
hit, location, normal, index, obj, matrix = scene.ray_cast(
    bpy.context.evaluated_depsgraph_get(),
    Vector((4.93, -8.45, 1.8)),
    Vector((0, 0, -1)),
)
depth = 0.93 - location.z if hit else 0
report = {
    "revision": scene["furniture_revision"],
    "detailed_components": len(objects),
    "separate_attached_details": sum(bool(o.get("assembly_source")) for o in objects),
    "evaluated_detail_triangles": triangles,
    "invalid_closed_meshes": invalid,
    "unparented_details": attachments,
    "sink_centre_hit": obj.name if hit else None,
    "sink_recess_m": round(depth, 4),
    "source_roles": sorted({m.name for o in objects for m in o.data.materials}),
    "passed": not invalid and not attachments and depth > 0.12 and triangles < 300000,
    "scope": "Mesh integrity, editable attachment and sink recess; full plan, door and route checks are separate reports.",
}
(ROOT / "docs/validation/furniture-overhaul.json").write_text(
    json.dumps(report, indent=2), encoding="utf-8"
)
print(json.dumps(report, indent=2))
if not report["passed"]:
    raise RuntimeError("Furniture overhaul validation failed")
