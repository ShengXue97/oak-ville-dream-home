"""Layer editable accent roles onto existing furnishings without changing geometry."""

import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]


def linear_colour(hex_colour):
    channels = [int(hex_colour[i : i + 2], 16) / 255 for i in (0, 2, 4)]
    return [
        v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in channels
    ] + [1.0]


def apply():
    if bpy.context.mode != "OBJECT":
        raise RuntimeError("Exit Edit Mode before applying the style preset")
    preset = json.loads((ROOT / "assets/styles/minimalist-accents.json").read_text())
    for name, settings in preset["roles"].items():
        material = bpy.data.materials.get(name)
        if material is None:
            material = bpy.data.materials[settings["source"]].copy()
            material.name = name
        colour = linear_colour(settings["hex"])
        material.diffuse_color = colour
        shader = material.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Base Color"].default_value = colour
        shader.inputs["Roughness"].default_value = settings["roughness"]
        for node in material.node_tree.nodes:
            if node.type == "TEX_BRICK":
                node.inputs["Color1"].default_value = colour
                node.inputs["Color2"].default_value = [v * 0.87 for v in colour[:3]] + [
                    1
                ]
            if node.type == "VALTORGB":
                for index, element in enumerate(node.color_ramp.elements):
                    factor = 0.8 if index == 0 else 1.0
                    element.color = [value * factor for value in colour[:3]] + [1]
        material["style_role"] = name

    assignments = {}

    def assign(name, role):
        obj = bpy.data.objects.get(name)
        if obj is None:
            raise ValueError("Missing intended accent surface: " + name)
        previous = obj.get("accent_previous_role") or obj.data.materials[0].name
        obj["accent_previous_role"] = previous
        obj.data.materials[0] = bpy.data.materials[role]
        assignments[name] = {"previous": previous, "target": role}

    exact = {
        "Living_Sofa_Back_Cushion_0": "Fabric_Main",
        "Living_Sofa_Back_Cushion_2": "Fabric_Main",
        "Living_Rug": "Accent_Flax_Linen",
        "Living_Art_Frame": "Accent_Honey_Oak",
        "Living_Coffee_Table_Top": "Accent_Warm_Stone",
        "Dining_Plant_Pot": "Accent_Olive_Ceramic",
        "Bedroom_3_Folded_Throw": "Accent_Sage_Linen",
        "Bedroom_3_Upholstered_Headboard": "Accent_Flax_Linen",
        "Bedroom_2_Folded_Throw": "Accent_Clay_Linen",
        "Bedroom_2_Upholstered_Headboard": "Accent_Flax_Linen",
        "Main_Bedroom_Folded_Throw": "Accent_Sage_Linen",
        "Main_Bedroom_Upholstered_Headboard": "Accent_Flax_Linen",
        "Main_Bedroom_Rug": "Accent_Flax_Linen",
        "Common_Bath_Vanity_Front_01": "Accent_Honey_Oak",
        "Ensuite_Vanity_Front_01": "Accent_Honey_Oak",
    }
    for name, role in exact.items():
        assign(name, role)
    for obj in bpy.context.scene.objects:
        name = obj.name
        if obj.type != "MESH" or name.startswith("COL_"):
            continue
        if (
            name.endswith("_Floor")
            and obj.data.materials
            and obj.data.materials[0].name in {"Floor_Main", "Accent_Natural_Oak_Floor"}
        ):
            assign(name, "Accent_Natural_Oak_Floor")
        if name.startswith(("Dining_Oval_Table", "Dining_Table_Pedestal")):
            assign(name, "Accent_Honey_Oak")
        elif (
            name.startswith("Dining_Chair")
            and "_Detail_" not in name
            and name.endswith(("_Seat", "_Back"))
        ):
            assign(name, "Accent_Flax_Linen")
        elif name.startswith("Dining_Chair") and name.endswith("_Detail_Bent_Oak_Back"):
            assign(name, "Oak_Joinery")
        elif name.startswith("Living_Table_Book") and name.endswith(
            ("Top_Cover", "Lower_Cover")
        ):
            role = "Accent_Clay_Linen" if ".001" in name else "Accent_Sage_Linen"
            assign(name, role)
    report = {"preset": preset, "assignments": assignments, "geometry_changed": False}
    (ROOT / "assets/styles/accent-assignments.json").write_text(
        json.dumps(report, indent=2) + "\n"
    )
    block = bpy.data.texts.get("MINIMALIST_ACCENTS.json") or bpy.data.texts.new(
        "MINIMALIST_ACCENTS.json"
    )
    block.clear()
    block.write(json.dumps(report, indent=2))
    return report


if __name__ == "__main__":
    apply()
