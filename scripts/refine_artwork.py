"""Replace the oval reliefs with packed, UV-mapped original landscape prints."""

from pathlib import Path
import json
import bpy

ROOT = Path(__file__).resolve().parents[1]


def apply():
    if bpy.context.mode != "OBJECT":
        raise RuntimeError("Exit Edit Mode before replacing artwork surfaces")
    image = bpy.data.images.load(
        str(ROOT / "assets/artwork/mineral-landscape.png"), check_existing=True
    )
    image.filepath = "//assets/artwork/mineral-landscape.png"
    image.pack()
    material = bpy.data.materials.get(
        "Art_Mineral_Landscape"
    ) or bpy.data.materials.new("Art_Mineral_Landscape")
    material.use_nodes = True
    nodes = material.node_tree.nodes
    shader = nodes.get("Principled BSDF")
    shader.inputs["Roughness"].default_value = 0.95
    texture = nodes.get("Landscape_Print") or nodes.new("ShaderNodeTexImage")
    texture.name = "Landscape_Print"
    texture.image = image
    material.node_tree.links.new(texture.outputs["Color"], shader.inputs["Base Color"])
    for room in ("Living", "Bedroom_3"):
        field = bpy.data.objects[room + "_Art_Cream_Field"]
        obj = bpy.data.objects[room + "_Art_Relief"]
        # Retain the existing object's stable ID and frame; replace only its art surface.
        mesh = bpy.data.meshes.new(room + "_Landscape_Print")
        width, height = 0.60, 0.75
        mesh.from_pydata(
            [
                (0, width / 2, -height / 2),
                (0, -width / 2, -height / 2),
                (0, -width / 2, height / 2),
                (0, width / 2, height / 2),
            ],
            [],
            [(0, 1, 2, 3)],
        )
        mesh.materials.append(material)
        uv = mesh.uv_layers.new(name="Print_UV")
        for loop, coordinate in zip(uv.data, [(0, 0), (1, 0), (1, 1), (0, 1)]):
            loop.uv = coordinate
        obj.data = mesh
        obj.location = (field.location.x + 0.008, field.location.y, field.location.z)
        obj.modifiers.clear()
        obj["collision_source"] = False
        obj["artwork_asset"] = "//assets/artwork/mineral-landscape.png"
    path = ROOT / "assets/styles/accent-assignments.json"
    report = json.loads(path.read_text())
    for room in ("Living", "Bedroom_3"):
        report["assignments"][room + "_Art_Relief"] = {
            "previous": "Fabric_Oatmeal",
            "target": "Art_Mineral_Landscape",
        }
    report["geometry_changed"] = (
        "Two non-colliding art surfaces replaced within existing frames"
    )
    path.write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    apply()
