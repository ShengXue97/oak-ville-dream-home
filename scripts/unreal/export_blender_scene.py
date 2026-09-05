"""Export evaluated Blender meshes in centimetres for Unreal Geometry Script.

Run in background Blender with oak-ville.blend open. The Blender file is never
saved. Coordinates map (X, Y, Z) metres to (X, -Y, Z) centimetres. World-space
rotation is baked into local mesh vertices around each object's bounds centre.
Original transforms, role names and door hinge metadata remain in the manifest.
"""

import gzip
import json
import math
import runpy
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
# Validate the saved source against plan datums before publishing any export.
# Comparing Unreal only to the export would miss an accidental source scale.
runpy.run_path(str(ROOT / "scripts/reopen_validate.py"))
OUTPUT = ROOT / "assets/unreal-export"
OUTPUT.mkdir(parents=True, exist_ok=True)
scene = bpy.data.scenes["Oak_Ville"]
bpy.context.window.scene = scene
depsgraph = bpy.context.evaluated_depsgraph_get()


def unreal_point(point):
    return [round(point.x * 100, 5), round(-point.y * 100, 5), round(point.z * 100, 5)]


def material_settings(material):
    colour = list(material.diffuse_color)
    roughness, metallic = 0.6, 0.0
    if material.use_nodes:
        shader = next(
            (
                node
                for node in material.node_tree.nodes
                if node.type == "BSDF_PRINCIPLED"
            ),
            None,
        )
        if shader:
            colour = list(shader.inputs["Base Color"].default_value)
            roughness = shader.inputs["Roughness"].default_value
            metallic = shader.inputs["Metallic"].default_value
        ramps = [node for node in material.node_tree.nodes if node.type == "VALTORGB"]
        if ramps:
            colour = list(ramps[0].color_ramp.elements[-1].color)
        bricks = [node for node in material.node_tree.nodes if node.type == "TEX_BRICK"]
        if bricks:
            colour = list(bricks[0].inputs["Color1"].default_value)
    return {"colour": colour, "roughness": roughness, "metallic": metallic}


objects = []
seen_ids = set()
for obj in sorted(scene.objects, key=lambda item: item.name):
    collections = [collection.name for collection in obj.users_collection]
    if obj.type != "MESH" or obj.hide_render:
        continue
    if any(
        name.startswith("Collision")
        or name in {"Calibration", "Plan_Annotations", "Reference_Plans"}
        for name in collections
    ):
        continue
    source_id = obj.get("oakville_source_id")
    if not source_id or source_id in seen_ids:
        raise RuntimeError(
            "Missing or duplicate Unreal ID on "
            + obj.name
            + ". Run scripts/unreal/prepare_blender_ids.py in Blender, then save and retry."
        )
    seen_ids.add(source_id)
    evaluated = obj.evaluated_get(depsgraph)
    mesh = evaluated.to_mesh()
    mesh.calc_loop_triangles()
    world = [obj.matrix_world @ vertex.co for vertex in mesh.vertices]
    centre = Vector(
        [(min(p[i] for p in world) + max(p[i] for p in world)) / 2 for i in range(3)]
    )
    normal_matrix = obj.matrix_world.to_3x3().inverted().transposed()
    vertices, normals, triangles = [], [], []
    art_uvs = []
    # Split corners retain weighted/smooth normals and hard architectural edges.
    for triangle in mesh.loop_triangles:
        start = len(vertices)
        # Y reflection converts Blender's counterclockwise front faces to
        # Unreal's clockwise convention. Do not reverse the corners again.
        for loop_index in triangle.loops:
            loop = mesh.loops[loop_index]
            vertices.append(unreal_point(world[loop.vertex_index] - centre))
            normal = (
                normal_matrix @ mesh.corner_normals[loop_index].vector
            ).normalized()
            normals.append([normal.x, -normal.y, normal.z])
            if obj.get("artwork_asset") and mesh.uv_layers.active:
                uv = mesh.uv_layers.active.data[loop_index].uv
                art_uvs.append([float(uv.x), 1.0 - float(uv.y)])
        triangles.append([start, start + 1, start + 2])
    role = obj.data.materials[0].name if obj.data.materials else "Wall_Paint"
    group = next(
        (
            name
            for name in collections
            if name
            in {
                "Architecture",
                "Ceilings",
                "Beams_Soffits",
                "Doors_Windows",
                "Furniture",
                "Fixed_Joinery",
                "Decor",
                "Lighting",
            }
        ),
        "Furniture",
    )
    parent = obj.parent.name if obj.parent else None
    objects.append(
        {
            "name": obj.name,
            "source_id": source_id,
            "group": group,
            "material": role,
            "location_cm": unreal_point(centre),
            "bounds_size_cm": [
                round((max(p[i] for p in world) - min(p[i] for p in world)) * 100, 5)
                for i in range(3)
            ],
            "parent": parent,
            "solid": bool(obj.get("collision_source")),
            "vertices": vertices,
            "normals": normals,
            "triangles": triangles,
        }
    )
    evaluated.to_mesh_clear()
    if art_uvs:
        objects[-1]["uv0"] = art_uvs

lights = []
for obj in scene.objects:
    if obj.type == "LIGHT":
        lights.append(
            {
                "name": obj.name,
                "type": obj.data.type,
                "location_cm": unreal_point(obj.matrix_world.translation),
                "direction": unreal_point(
                    obj.matrix_world.to_3x3() @ Vector((0, 0, -1))
                ),
                "energy": obj.data.energy,
                "colour": list(obj.data.color),
                "size": getattr(obj.data, "size", 0.1),
            }
        )
doors = [
    {
        "name": obj.name,
        "location_cm": unreal_point(obj.matrix_world.translation),
        "open_angle": obj["open_angle_degrees"],
        "export_angle": math.degrees(obj.rotation_euler.z),
        "closed_angle": obj["closed_angle_degrees"],
    }
    for obj in scene.objects
    if "open_angle_degrees" in obj
]
manifest = {
    "source_version": scene["project_version"],
    "coordinate_mapping": "Blender (X,Y,Z) metres -> Unreal (X,-Y,Z) centimetres",
    "geometry_revision": 4,
    "objects": objects,
    "materials": {
        material.name: material_settings(material)
        for material in bpy.data.materials
        if material.name in {record["material"] for record in objects}
    },
    "lights": lights,
    "doors": doors,
    "routes": {
        obj.name: json.loads(obj["route_points_plan_m"])
        for obj in scene.objects
        if "route_points_plan_m" in obj
    },
}
with gzip.open(OUTPUT / "scene.json.gz", "wt", encoding="utf-8") as stream:
    json.dump(manifest, stream, separators=(",", ":"))
summary = {
    "source_version": manifest["source_version"],
    "mesh_objects": len(objects),
    "triangles": sum(len(obj["triangles"]) for obj in objects),
    "lights": len(lights),
    "doors": len(doors),
    "coordinate_mapping": manifest["coordinate_mapping"],
}
(OUTPUT / "manifest.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
