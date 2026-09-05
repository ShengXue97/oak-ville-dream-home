"""Verify both style directions in the saved Blender file without saving it."""
import hashlib
import json
from pathlib import Path
import sys
import bpy

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import style_switch as styles


def geometry():
    result = {}
    for obj in bpy.context.scene.objects:
        record = {"matrix": [list(row) for row in obj.matrix_world],
                  "id": obj.get("oakville_source_id"),
                  "visibility": [obj.hide_viewport, obj.hide_render, obj.hide_get()],
                  "collision": bool(obj.get("collision_source"))}
        if obj.type == "MESH":
            record["vertices"] = [list(vertex.co) for vertex in obj.data.vertices]
            record["polygons"] = [list(poly.vertices) for poly in obj.data.polygons]
            record["uvs"] = [[list(loop.uv) for loop in layer.data] for layer in obj.data.uv_layers]
        if obj.type == "LIGHT":
            record["light"] = [list(obj.data.color), obj.data.energy]
        result[obj.name] = record
    return hashlib.sha256(json.dumps(result, sort_keys=True).encode()).hexdigest()


def materials():
    return {obj.name: [slot.material.name if slot.material else None for slot in obj.material_slots]
            for obj in bpy.context.scene.objects if obj.type == "MESH"}


original_style = bpy.context.scene.get("active_style", styles.MINIMALIST)
baseline_geometry = geometry()
styles.set_style(styles.MINIMALIST)
minimalist = materials()
styles.set_style(styles.TROPICAL)
tropical = materials()
assert geometry() == baseline_geometry, "Style switch changed geometry, UVs, visibility or lights"
changed = [name for name in minimalist if minimalist[name] != tropical[name]]
assert len(changed) > 300, "Whole-flat finish option is missing"
assert any("Floor" in name for name in changed)
assert any("Wall_Paint" in minimalist[name] for name in changed)
assert any("Sofa" in name for name in changed)
assert any("Kitchen" in name for name in changed)
assert any("Bath" in name for name in changed)
styles.set_style(styles.MINIMALIST)
assert materials() == minimalist, "Minimalist slots did not restore"
styles.set_style(styles.TROPICAL)
assert materials() == tropical, "Tropical slots did not restore"
# Re-preparing must not overwrite an edited alternative or create more copies.
count = len(bpy.data.materials)
styles.prepare()
assert len(bpy.data.materials) == count
assert materials() == tropical
styles.set_style(original_style)
assert geometry() == baseline_geometry
report = {"passed": True, "saved_style": original_style, "changed_surfaces": len(changed),
          "both_round_trips_exact": True, "geometry_uv_visibility_lighting_collision_unchanged": True,
          "idempotent_prepare": True, "geometry_sha256": baseline_geometry}
(ROOT / "docs/validation/style-switch.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
