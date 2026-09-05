"""Milestone 4: reusable cream/oak palette, procedural textures and lighting.

No external texture files are required. The palette JSON is a convenient
control point; shared material names are the stable interface for restyling.
"""

import random
import ast

# Load shared geometry helpers without recreating the furniture milestone.
helper_tree = ast.parse((ROOT / "scripts/03_furnish.py").read_text())
helper_functions = [
    node
    for node in helper_tree.body
    if isinstance(node, ast.FunctionDef) and node.name in {"round_object", "soft_shape"}
]
exec(
    compile(
        ast.Module(body=helper_functions, type_ignores=[]),
        "furniture_geometry_helpers",
        "exec",
    ),
    globals(),
)

random.seed(41)


def textured_role(name, color_a, color_b, scale, stretch=(1, 1, 1), bump=0.0005):
    material_data = bpy.data.materials[name]
    nodes = material_data.node_tree.nodes
    links = material_data.node_tree.links
    shader = nodes.get("Principled BSDF")
    coordinates = nodes.new("ShaderNodeTexCoord")
    coordinates.label = "Local generated coordinates; no external image dependency"
    mapping = nodes.new("ShaderNodeVectorMath")
    mapping.operation = "MULTIPLY"
    mapping.inputs[1].default_value = stretch
    links.new(coordinates.outputs["Generated"], mapping.inputs[0])
    noise = nodes.new("ShaderNodeTexNoise")
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = 2
    links.new(mapping.outputs["Vector"], noise.inputs["Vector"])
    ramp = nodes.new("ShaderNodeValToRGB")
    ramp.name = "EDIT_PALETTE"
    ramp.color_ramp.elements[0].position = 0.20
    ramp.color_ramp.elements[0].color = (*color_a, 1)
    ramp.color_ramp.elements[1].position = 0.80
    ramp.color_ramp.elements[1].color = (*color_b, 1)
    links.new(noise.outputs["Fac"], ramp.inputs["Fac"])
    links.new(ramp.outputs["Color"], shader.inputs["Base Color"])
    relief = nodes.new("ShaderNodeBump")
    relief.inputs["Strength"].default_value = 0.20
    relief.inputs["Distance"].default_value = bump
    links.new(noise.outputs["Fac"], relief.inputs["Height"])
    links.new(relief.outputs["Normal"], shader.inputs["Normal"])
    coordinates.location = (-650, 0)
    mapping.location = (-460, 0)
    noise.location = (-260, 0)
    ramp.location = (-40, 100)
    relief.location = (-40, -180)
    shader.location = (230, 80)
    return material_data


textured_role(
    "Oak_Joinery", (0.52, 0.37, 0.23), (0.69, 0.54, 0.37), 3.0, (1, 35, 2), 0.0008
)
textured_role(
    "Floor_Main", (0.58, 0.43, 0.29), (0.71, 0.56, 0.40), 3.0, (1, 60, 2), 0.0006
)
textured_role("Fabric_Main", (0.68, 0.61, 0.50), (0.85, 0.78, 0.65), 110, bump=0.0009)
textured_role(
    "Fabric_Oatmeal", (0.48, 0.39, 0.29), (0.67, 0.56, 0.43), 140, bump=0.0011
)
textured_role("Countertop", (0.73, 0.68, 0.59), (0.87, 0.82, 0.73), 90, bump=0.0003)
textured_role("Wet_Tile", (0.66, 0.60, 0.49), (0.78, 0.72, 0.61), 75, bump=0.0004)
material("Wall_Paint", (0.83, 0.78, 0.69), 0.82)
material("Cabinet_Front", (0.81, 0.75, 0.64), 0.48)
material("Sheer_Linen", (0.87, 0.82, 0.73), 0.90)
material("Mirror", (0.90, 0.90, 0.88), 0.035)
bpy.data.materials["Mirror"].node_tree.nodes["Principled BSDF"].inputs[
    "Metallic"
].default_value = 1
bpy.data.materials["Metal_Champagne"].node_tree.nodes["Principled BSDF"].inputs[
    "Metallic"
].default_value = 0.75
glass_shader = bpy.data.materials["Glass"].node_tree.nodes["Principled BSDF"]
glass_shader.inputs["Base Color"].default_value = (0.96, 0.97, 0.96, 1)
glass_shader.inputs["Transmission Weight"].default_value = 1.0
glass_shader.inputs["Roughness"].default_value = 0.07
glass_shader.inputs["IOR"].default_value = 1.45
linen_shader = bpy.data.materials["Sheer_Linen"].node_tree.nodes["Principled BSDF"]
linen_shader.inputs["Transmission Weight"].default_value = 0.28
for obj in bpy.context.scene.objects:
    if obj.name.endswith("_Mirror"):
        obj.data.materials.clear()
        obj.data.materials.append(bpy.data.materials["Mirror"])

# World-coordinate plank joints retain a consistent module across room patches.
floor_material = bpy.data.materials["Floor_Main"]
nodes = floor_material.node_tree.nodes
links = floor_material.node_tree.links
geometry = nodes.new("ShaderNodeNewGeometry")
brick = nodes.new("ShaderNodeTexBrick")
brick.name = "Oak_Planks_1200x180mm"
brick.inputs["Scale"].default_value = 1.0
brick.inputs["Brick Width"].default_value = 1.20
brick.inputs["Row Height"].default_value = 0.18
brick.inputs["Mortar Size"].default_value = 0.001
brick.inputs["Mortar Smooth"].default_value = 0.001
brick.inputs["Color1"].default_value = (0.64, 0.49, 0.33, 1)
brick.inputs["Color2"].default_value = (0.73, 0.59, 0.43, 1)
brick.inputs["Mortar"].default_value = (0.41, 0.31, 0.20, 1)
links.new(geometry.outputs["Position"], brick.inputs["Vector"])
mix = nodes.new("ShaderNodeMixRGB")
mix.blend_type = "MULTIPLY"
mix.inputs[0].default_value = 0.18
links.new(brick.outputs["Color"], mix.inputs[1])
links.new(nodes["EDIT_PALETTE"].outputs["Color"], mix.inputs[2])
links.new(mix.outputs[0], nodes["Principled BSDF"].inputs["Base Color"])


def curtain(room, start, end, plan_y=0.19):
    """Sinusoidal drape with editable thickness, kept away from window jambs."""
    vertices = []
    faces = []
    segments = 72
    for height in (0.07, 2.43):
        for index in range(segments + 1):
            fraction = index / segments
            x = start + (end - start) * fraction
            depth = plan_y + 0.043 * math.sin(fraction * math.pi * 16)
            vertices.append((x, -depth, height))
    for index in range(segments):
        faces.append((index, index + 1, index + segments + 2, index + segments + 1))
    mesh = bpy.data.meshes.new(room + "_Linen_Drape")
    mesh.from_pydata(vertices, [], faces)
    obj = bpy.data.objects.new(room + "_Linen_Drape", mesh)
    COLS["Decor"].objects.link(obj)
    obj.data.materials.append(bpy.data.materials["Sheer_Linen"])
    modifier = obj.modifiers.new("Editable fabric thickness", "SOLIDIFY")
    modifier.thickness = 0.001
    for polygon in mesh.polygons:
        polygon.use_smooth = True


for room, left, right in [
    ("Living", 0.40, 3.15),
    ("Bedroom_3", 3.60, 5.85),
    ("Bedroom_2", 6.70, 9.12),
    ("Main_Bedroom", 9.62, 12.35),
]:
    curtain(room + "_Left", left, left + 0.46)
    curtain(room + "_Right", right - 0.46, right)
    cub(
        room + "_Curtain_Track",
        (left + right) / 2,
        0.17,
        2.46,
        right - left + 0.10,
        0.045,
        0.035,
        "Decor",
        "Cabinet_Front",
        0.008,
        False,
    )


def area_light(name, position, target, power, size, kelvin=2900):
    data = bpy.data.lights.new(name, "AREA")
    data.energy = power
    data.shape = "DISK"
    data.size = size
    # A Blackbody node supplies an inspectable temperature-to-colour conversion.
    temperature_material = bpy.data.materials.get("Light_Temperature_Reference")
    if temperature_material is None:
        temperature_material = material("Light_Temperature_Reference", (1, 1, 1))
        blackbody = temperature_material.node_tree.nodes.new("ShaderNodeBlackbody")
        blackbody.name = "Artificial_Light_2900K"
        blackbody.inputs[0].default_value = 2900
    # Blender light colour is scene-linear; restrained warm tint balances daylight.
    data.color = (1.0, 0.78, 0.55) if kelvin < 4000 else (0.82, 0.90, 1.0)
    data["design_temperature_kelvin"] = kelvin
    data["temperature_note"] = (
        "Approximate warm/cool tint, adjustable; not a photometric fixture specification"
    )
    obj = bpy.data.objects.new(name, data)
    COLS["Lighting"].objects.link(obj)
    obj.location = (position[0], -position[1], position[2])
    direction = Vector((target[0], -target[1], target[2])) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()
    # The daylight emitter is a lighting aid, not a physical disk outside the flat.
    obj.visible_camera = False
    obj.visible_glossy = False
    obj.visible_transmission = False
    return obj


# Room lights are easy to replace with a designer's actual lighting specification.
light_positions = {
    "Living": (1.70, 2.00, 160),
    "Dining": (4.65, 5.05, 110),
    "Entry": (2.65, 6.55, 55),
    "Bedroom_3": (4.85, 1.70, 95),
    "Bedroom_2": (7.90, 1.70, 95),
    "Main_Bedroom": (11.00, 2.20, 130),
    "Common_Bath": (7.50, 5.40, 65),
    "Ensuite": (9.90, 5.40, 65),
    "Kitchen": (4.72, 7.58, 85),
    "Service_Yard": (6.45, 7.55, 65),
    "Shelter": (0.85, 5.60, 45),
    "Bedroom_Corridor": (7.70, 3.90, 75),
}
for room, (x, plan_y, power) in light_positions.items():
    area_light(room + "_Ceiling_2900K", (x, plan_y, 2.52), (x, plan_y, 0), power, 0.70)
    cub(
        room + "_Ceiling_Diffuser",
        x,
        plan_y,
        2.565,
        0.36,
        0.36,
        0.025,
        "Lighting",
        "Porcelain",
        0.06,
        False,
    )
for room, x, width in [
    ("Living", 1.75, 2.4),
    ("Bedroom_3", 4.70, 2.0),
    ("Bedroom_2", 7.85, 2.1),
    ("Main_Bedroom", 10.95, 2.3),
]:
    area_light(
        room + "_Daylight_6500K", (x, -0.45, 1.80), (x, 2.4, 0.8), 420, width, 6500
    )
area_light(
    "Kitchen_Under_Cabinet_2900K", (4.03, 7.60, 1.64), (4.15, 7.60, 0.90), 25, 1.1
)
area_light("Living_Cove_Wash_2900K", (0.26, 2.0, 2.37), (0.13, 2.0, 2.57), 50, 1.6)
cub(
    "Living_Removable_Cove_Trim",
    0.24,
    2.0,
    2.37,
    0.14,
    3.65,
    0.07,
    "Fixed_Joinery",
    "Wall_Paint",
    0.01,
)
area_light("Yard_Daylight_6500K", (8.10, 7.6, 1.8), (6.4, 7.6, 1), 160, 1.5, 6500)

# Restrained pendant above dining; underside stays above 1.95 m.
round_object(
    "Dining_Pendant_Shade", 4.65, 5.05, 2.09, 0.26, 0.22, "Sheer_Linen", "Lighting"
)
cub(
    "Dining_Pendant_Cord",
    4.65,
    5.05,
    2.38,
    0.012,
    0.012,
    0.35,
    "Lighting",
    "Metal_Champagne",
    0.004,
    False,
)

# Small amount of styling: plants, books and tonal artwork.
for room, x, plan_y in [("Living", 2.77, 0.64), ("Dining", 5.76, 4.77)]:
    round_object(
        room + "_Plant_Pot", x, plan_y, 0.21, 0.16, 0.39, "Countertop", "Decor"
    )
    for index in range(9):
        angle = index * 2.4
        height = 0.63 + index * 0.055
        cub(
            room + "_Plant_Stem",
            x,
            plan_y,
            height / 2 + 0.20,
            0.012,
            0.012,
            height,
            "Decor",
            "Oak_Joinery",
            0.003,
            False,
        )
        leaf = soft_shape(
            room + "_Leaf",
            x + 0.15 * math.cos(angle),
            plan_y + 0.15 * math.sin(angle),
            height + 0.10,
            (0.24, 0.12, 0.055),
            "Foliage",
        )
        leaf.rotation_euler = (0.4, 0.4, angle)
for index in range(3):
    cub(
        "Living_Table_Book",
        1.70,
        1.85,
        0.422 + 0.024 * index,
        0.28 - index * 0.025,
        0.20,
        0.023,
        "Decor",
        "Cabinet_Front",
        0.008,
        False,
    )
for room, x, plan_y in [("Bedroom_3", 3.445, 1.5), ("Living", 0.125, 2.0)]:
    cub(
        room + "_Art_Frame",
        x,
        plan_y,
        1.62,
        0.032,
        0.78,
        0.88,
        "Decor",
        "Oak_Joinery",
        0.008,
        False,
    )
    cub(
        room + "_Art_Cream_Field",
        x + 0.02,
        plan_y,
        1.62,
        0.01,
        0.72,
        0.82,
        "Decor",
        "Countertop",
        0.01,
        False,
    )
    soft_shape(
        room + "_Art_Relief",
        x + 0.033,
        plan_y + 0.08,
        1.63,
        (0.02, 0.33, 0.51),
        "Fabric_Oatmeal",
    )

# Save a compact preset describing stable role names and intended temperatures.
preset = {
    "name": "MINIMALIST_CREAM",
    "description": "Warm cream and pale oak contemporary minimalism",
    "material_roles": {
        name: list(bpy.data.materials[name].diffuse_color)
        for name in [
            "Wall_Paint",
            "Floor_Main",
            "Cabinet_Front",
            "Countertop",
            "Fabric_Main",
            "Fabric_Oatmeal",
            "Oak_Joinery",
            "Wet_Tile",
        ]
    },
    "artificial_light_design_kelvin": 2900,
    "daylight_design_kelvin": 6500,
    "texture_dependency": "Procedural nodes only; edit EDIT_PALETTE ramps for textured materials",
}
(ROOT / "assets/MINIMALIST_CREAM.json").write_text(json.dumps(preset, indent=2))

living_camera = camera(
    "PREVIEW_Living_Eye", (2.65, 4.05, 1.60), (1.45, 1.50, 1.10), fov=65
)
scene = bpy.context.scene
scene.camera = living_camera
scene.view_settings.view_transform = "AgX"
scene.view_settings.exposure = 0.0
scene.cycles.samples = 24
scene.cycles.preview_samples = 8
bpy.context.window.view_layer = scene.view_layers["Enclosed_Walkthrough"]
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == "VIEW_3D":
            space = area.spaces.active
            space.region_3d.view_perspective = "CAMERA"
            space.overlay.show_overlays = False
            space.shading.type = "MATERIAL"
            space.shading.use_scene_lights = True
            space.shading.use_scene_world = True

exec((ROOT / "scripts/validate_model.py").read_text(), globals())
validate_routes("styled-routes")
