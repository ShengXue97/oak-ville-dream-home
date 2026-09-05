"""Reversible finish options. Run in Blender to add the Oak Ville sidebar.

The original materials remain untouched. Both options share the same detailed
geometry, UVs, object IDs, lights and collision proxies. No automatic saves.
"""

import json
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
MINIMALIST = "MINIMALIST_CREAM"
TROPICAL = "TROPICAL_MODERN"
STYLES = {MINIMALIST: "Minimalist", TROPICAL: "Tropical modern"}
SLOTS = "oakville_style_slots"


def colour(hex_value):
    values = [int(hex_value[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in values] + [1]


def prepare():
    """Create independent roles once; repeated runs retain designer edits."""
    if bpy.context.mode != "OBJECT":
        raise RuntimeError("Exit Edit Mode before preparing style options")
    preset = json.loads((ROOT / "assets/styles/TROPICAL_MODERN.json").read_text())
    for role, settings in preset["roles"].items():
        name = TROPICAL + "__" + role
        if name in bpy.data.materials:
            continue
        source = settings.get("source", role)
        material = bpy.data.materials[source].copy()
        material.name = name
        material.use_fake_user = True
        material["style_id"] = TROPICAL
        material["base_role"] = source
        tint = colour(settings["hex"])
        material.diffuse_color = tint
        shader = material.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Base Color"].default_value = tint
        shader.inputs["Roughness"].default_value = settings["roughness"]
        for node in material.node_tree.nodes:
            if node.type == "VALTORGB":
                for i, element in enumerate(node.color_ramp.elements):
                    factor = 0.85 if i == 0 else 1.0
                    element.color = [v * factor for v in tint[:3]] + [1]
            elif node.type == "TEX_BRICK":
                node.inputs["Color1"].default_value = tint
                node.inputs["Color2"].default_value = [v * 0.88 for v in tint[:3]] + [1]
    for obj in bpy.context.scene.objects:
        if obj.type != "MESH" or SLOTS in obj:
            continue
        original = [slot.material.name if slot.material else None for slot in obj.material_slots]
        if not original:
            continue
        tropical = [TROPICAL + "__" + role if role in preset["roles"] else role for role in original]
        obj[SLOTS] = json.dumps({MINIMALIST: original, TROPICAL: tropical})
        for role in original:
            if role:
                bpy.data.materials[role].use_fake_user = True
    if "active_style" not in bpy.context.scene:
        bpy.context.scene["active_style"] = MINIMALIST
    block = bpy.data.texts.get("TROPICAL_MODERN.json") or bpy.data.texts.new("TROPICAL_MODERN.json")
    block.clear()
    block.write(json.dumps(preset, indent=2))


def material_options(obj):
    """Read assignments by slot, including intentionally unchanged finishes."""
    return json.loads(obj[SLOTS]) if SLOTS in obj else {}


def set_style(style):
    if style not in STYLES:
        raise ValueError("Unknown style: " + str(style))
    if bpy.context.mode != "OBJECT":
        raise RuntimeError("Exit Edit Mode before switching styles")
    # Resolve everything before touching slots so missing assets fail atomically.
    changes = []
    for obj in bpy.context.scene.objects:
        options = material_options(obj)
        if not options:
            continue
        if len(obj.material_slots) != len(options[style]):
            raise RuntimeError("Material slots changed; review style mapping for " + obj.name)
        for index, role in enumerate(options[style]):
            slot = obj.material_slots[index]
            known = {roles[index] for roles in options.values()}
            current = slot.material.name if slot.material else None
            if current not in known:
                continue  # Preserve unrelated designer material assignments.
            material = bpy.data.materials.get(role) if role else None
            if role and material is None:
                raise RuntimeError("Missing style material: " + role)
            changes.append((slot, material))
    for slot, material in changes:
        slot.material = material
    bpy.context.scene["active_style"] = style
    bpy.context.view_layer.update()
    for screen in bpy.data.screens:
        for area in screen.areas:
            area.tag_redraw()
    return len(changes)


class OAKVILLE_OT_style(bpy.types.Operator):
    bl_idname = "oakville.set_style"
    bl_label = "Switch interior style"
    bl_options = {"REGISTER", "UNDO"}
    style: bpy.props.StringProperty()

    def execute(self, context):
        try:
            prepare()
            set_style(self.style)
        except (RuntimeError, ValueError) as error:
            self.report({"ERROR"}, str(error))
            return {"CANCELLED"}
        return {"FINISHED"}


class OAKVILLE_PT_style(bpy.types.Panel):
    bl_label = "Interior style"
    bl_idname = "OAKVILLE_PT_style"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Oak Ville"

    def draw(self, context):
        active = context.scene.get("active_style", MINIMALIST)
        row = self.layout.row(align=True)
        for style, label in STYLES.items():
            row.operator("oakville.set_style", text=label, depress=active == style).style = style
        self.layout.label(text="Shared layout • independent finishes")


def register():
    for cls in (OAKVILLE_OT_style, OAKVILLE_PT_style):
        old = getattr(bpy.types, cls.__name__, None)
        if old:
            bpy.utils.unregister_class(old)
        bpy.utils.register_class(cls)


if __name__ == "__main__":
    prepare()
    register()
