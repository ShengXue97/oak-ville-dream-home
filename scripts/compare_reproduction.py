"""Compare the delivered file with a freshly regenerated test file, read-only."""

import bpy
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def scene_record():
    scene = bpy.data.scenes["Oak_Ville"]
    bpy.context.window.scene = scene
    bpy.context.window.view_layer = scene.view_layers["Inspection_Cutaway"]
    scene.view_layers["Inspection_Cutaway"].layer_collection.children[
        "Collision"
    ].exclude = False
    bpy.context.view_layer.update()
    record = {}
    for obj in scene.objects:
        item = {
            "type": obj.type,
            "matrix": [round(value, 5) for row in obj.matrix_world for value in row],
            "dimensions": [round(value, 5) for value in obj.dimensions],
            "collections": sorted(
                collection.name for collection in obj.users_collection
            ),
        }
        if obj.type == "MESH":
            item["vertices"] = len(obj.data.vertices)
            item["materials"] = [material.name for material in obj.data.materials]
        if obj.get("route_points_plan_m"):
            item["route"] = json.loads(obj["route_points_plan_m"])
        record[obj.name] = item
    return record


delivered = scene_record()
bpy.ops.wm.open_mainfile(filepath=str(ROOT / ".cache/reproduction-check.blend"))
reproduced = scene_record()
differences = {
    name: {"delivered": delivered.get(name), "reproduced": reproduced.get(name)}
    for name in sorted(set(delivered) | set(reproduced))
    if delivered.get(name) != reproduced.get(name)
}
report = {
    "delivered_object_count": len(delivered),
    "reproduced_object_count": len(reproduced),
    "compared": "Object transforms, dimensions, types, collection memberships, mesh vertex counts, material role names and route control points at 0.00001m rounding",
    "differences": differences,
    "pass": not differences,
}
(ROOT / "docs/validation/reproduction-validation.json").write_text(
    json.dumps(report, indent=2)
)
print(json.dumps({"differences": list(differences), "pass": not differences}, indent=2))
