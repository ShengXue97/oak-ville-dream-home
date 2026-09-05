"""Non-destructive style controls for a designer working in Blender.

No function saves automatically. A style copy preserves the architecture.
Review any changes in the viewport and save when satisfied.
"""

import bpy
import json
from pathlib import Path


def export_palette(path):
    roles = {}
    for material in bpy.data.materials:
        if not material.use_nodes or material.name == "Light_Temperature_Reference":
            continue
        shader = material.node_tree.nodes.get("Principled BSDF")
        if shader is None:
            continue
        roles[material.name] = {
            "base_color": list(shader.inputs["Base Color"].default_value),
            "roughness": shader.inputs["Roughness"].default_value,
            "ramps": {
                node.name: [list(element.color) for element in node.color_ramp.elements]
                for node in material.node_tree.nodes
                if node.type == "VALTORGB"
            },
        }
    Path(path).write_text(
        json.dumps({"preset": "MINIMALIST_CREAM", "roles": roles}, indent=2)
    )


def apply_palette(path):
    """Apply only explicitly supplied fields to matching shared material roles."""
    preset = json.loads(Path(path).read_text())
    for role, values in preset["roles"].items():
        material = bpy.data.materials.get(role)
        if material is None or not material.use_nodes:
            continue
        shader = material.node_tree.nodes.get("Principled BSDF")
        if "base_color" in values:
            shader.inputs["Base Color"].default_value = values["base_color"]
            material.diffuse_color = values["base_color"]
        if "roughness" in values:
            shader.inputs["Roughness"].default_value = values["roughness"]
        for node_name, colors in values.get("ramps", {}).items():
            node = material.node_tree.nodes.get(node_name)
            if node is not None:
                for element, color in zip(node.color_ramp.elements, colors):
                    element.color = color


def duplicate_style(name="DESIGN_OPTION_B"):
    """Duplicate decor/furniture/joinery/lights; leave the shell and doors intact.

    Each copied object gets unique geometry/light data. Materials stay shared
    until explicitly made single-user in the Material Properties panel.
    """
    if name in bpy.data.collections:
        raise ValueError(
            "Choose a new option name; an existing option will not be overwritten"
        )
    source = bpy.data.collections["MINIMALIST_CREAM"]
    target = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(target)
    object_map = {}

    def copy_collection(original, destination):
        for original_object in original.objects:
            copied = original_object.copy()
            if original_object.data:
                copied.data = original_object.data.copy()
            copied.name = name + "__" + original_object.name
            destination.objects.link(copied)
            object_map[original_object] = copied
        for child in original.children:
            copied_child = bpy.data.collections.new(name + "__" + child.name)
            destination.children.link(copied_child)
            copy_collection(child, copied_child)

    copy_collection(source, target)
    for original, copied in object_map.items():
        if original.parent in object_map:
            copied.parent = object_map[original.parent]
    # Hide the new option initially; the designer chooses when to switch.
    target.hide_render = True
    target.hide_viewport = True
    return target
