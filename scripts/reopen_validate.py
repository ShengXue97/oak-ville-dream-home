"""Read-only validation after Blender opens the saved .blend independently.

Writes reports but never saves or modifies the deliverable on disk.
"""

import bpy
import json
import runpy
import bmesh
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
bpy.context.window.scene = bpy.data.scenes["Oak_Ville"]
namespace = runpy.run_path(str(ROOT / "scripts/build_oak_ville.py"))
namespace = namespace["build"].__globals__
exec((ROOT / "scripts/validate_model.py").read_text(), namespace)
routes = namespace["validate_routes"]("reopened-routes")
fit = namespace["validate_furniture_and_swings"]()
exec((ROOT / "scripts/designer_documents.py").read_text(), namespace)
dimensions = namespace["write_designer_documents"]()
images = [
    {
        "name": image.name,
        "path": image.filepath,
        "packed": bool(image.packed_file),
        "loaded_pixels": len(image.pixels) > 0,
    }
    for image in bpy.data.images
    if image.source == "FILE"
]
scene = bpy.context.scene
invalid_closed_meshes = []
negative_volume_meshes = []
for obj in scene.objects:
    if obj.type != "MESH" or not (
        obj.get("collision_source") or "source_object" in obj
    ):
        continue
    mesh = bmesh.new()
    mesh.from_mesh(obj.data)
    if not all(edge.is_manifold for edge in mesh.edges):
        invalid_closed_meshes.append(obj.name)
    elif mesh.calc_volume(signed=True) < -0.00000001:
        negative_volume_meshes.append(obj.name)
    mesh.free()
report = {
    "opened_file": Path(bpy.data.filepath).name,
    "blender_version": bpy.app.version_string,
    "project_version": scene.get("project_version"),
    "metres_per_unit": scene.unit_settings.scale_length,
    "default_scene": scene.name,
    "camera": scene.camera.name,
    "routes_pass": routes["all_pass"],
    "furniture_and_swings_pass": fit["all_pass"],
    "mesh_dimensions_pass": dimensions["all_mesh_datums_pass"],
    "images": images,
    "packed_references_pass": len(images) >= 3
    and all(image["packed"] and image["loaded_pixels"] for image in images),
    "missing_libraries": [
        library.filepath
        for library in bpy.data.libraries
        if not Path(bpy.path.abspath(library.filepath)).exists()
    ],
    "ceiling_objects": len(bpy.data.collections["Ceilings"].objects),
    "route_count": len(routes["routes"]),
    "collision_proxy_count": len(bpy.data.collections["Collision"].all_objects),
    "file_size_bytes": Path(bpy.data.filepath).stat().st_size,
    "read_only": True,
    "nonmanifold_collision_sources": invalid_closed_meshes,
    "inward_closed_meshes": negative_volume_meshes,
}
report["all_pass"] = (
    all(
        report[key]
        for key in (
            "routes_pass",
            "furniture_and_swings_pass",
            "mesh_dimensions_pass",
            "packed_references_pass",
        )
    )
    and not report["missing_libraries"]
    and not invalid_closed_meshes
    and not negative_volume_meshes
)
(ROOT / "docs/validation/reopened-file-validation.json").write_text(
    json.dumps(report, indent=2)
)
print(json.dumps(report, indent=2), flush=True)
if not report["all_pass"]:
    raise RuntimeError(
        "Saved-file validation failed; inspect docs/validation/reopened-file-validation.json"
    )
