"""Milestone 3: human-sized editable furnishings, storage and sanitaryware.

All dimensions are proposed furniture sizes, not measurements from the tour.
Rounded edges remain editable bevel modifiers. Components stay separate.
"""

import csv


def round_object(
    name, x, plan_y, z, radius, depth, material_role, collection_name="Furniture"
):
    bpy.ops.mesh.primitive_cylinder_add(
        vertices=48, radius=radius, depth=depth, location=(x, -plan_y, z)
    )
    obj = bpy.context.object
    obj.name = name
    for current_collection in list(obj.users_collection):
        current_collection.objects.unlink(obj)
    COLS[collection_name].objects.link(obj)
    obj.data.materials.append(bpy.data.materials[material_role])
    bevel = obj.modifiers.new("Editable rounded rim", "BEVEL")
    bevel.width = min(0.025, depth / 3)
    bevel.segments = 3
    obj.modifiers.new("Weighted normals", "WEIGHTED_NORMAL")
    obj["collision_source"] = True
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def soft_shape(name, x, plan_y, z, size, material_role, collection_name="Decor"):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=24, ring_count=12, radius=1, location=(x, -plan_y, z)
    )
    obj = bpy.context.object
    obj.name = name
    obj.scale = tuple(value / 2 for value in size)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for current_collection in list(obj.users_collection):
        current_collection.objects.unlink(obj)
    COLS[collection_name].objects.link(obj)
    obj.data.materials.append(bpy.data.materials[material_role])
    obj["collision_source"] = collection_name != "Decor"
    for polygon in obj.data.polygons:
        polygon.use_smooth = True
    return obj


def cabinet(name, x, plan_y, width, depth, height, bottom=0.10, fronts="south"):
    """Casework with separate plinth, carcass and individually editable fronts."""
    cub(
        name + "_Carcass",
        x,
        plan_y,
        bottom + height / 2,
        width,
        depth,
        height,
        "Fixed_Joinery",
        "Oak_Joinery",
        0.012,
    )
    if bottom <= 0.20:
        cub(
            name + "_Recessed_Plinth",
            x,
            plan_y,
            bottom / 2,
            width - 0.08,
            depth - 0.06,
            bottom,
            "Fixed_Joinery",
            "Oak_Joinery",
            0.008,
        )
    if fronts in {"south", "north"}:
        count = max(1, round(width / 0.50))
        direction = 1 if fronts == "south" else -1
        for index in range(count):
            front_x = x - width / 2 + (index + 0.5) * width / count
            cub(
                name + f"_Front_{index + 1:02d}",
                front_x,
                plan_y + direction * (depth / 2 + 0.011),
                bottom + height / 2,
                width / count - 0.006,
                0.022,
                height - 0.008,
                "Fixed_Joinery",
                "Cabinet_Front",
                0.005,
            )
    else:
        count = max(1, round(depth / 0.50))
        direction = 1 if fronts == "east" else -1
        for index in range(count):
            front_y = plan_y - depth / 2 + (index + 0.5) * depth / count
            cub(
                name + f"_Front_{index + 1:02d}",
                x + direction * (width / 2 + 0.011),
                front_y,
                bottom + height / 2,
                0.022,
                depth / count - 0.006,
                height - 0.008,
                "Fixed_Joinery",
                "Cabinet_Front",
                0.005,
            )


def bed(room, x, plan_y, width=1.5, length=2.0):
    cub(
        room + "_Bed_Base",
        x,
        plan_y,
        0.22,
        width + 0.08,
        length + 0.10,
        0.32,
        "Furniture",
        "Oak_Joinery",
        0.065,
    )
    cub(
        room + "_Mattress",
        x,
        plan_y,
        0.48,
        width,
        length,
        0.25,
        "Furniture",
        "Fabric_Main",
        0.095,
    )
    cub(
        room + "_Upholstered_Headboard",
        x,
        plan_y - length / 2 - 0.06,
        0.70,
        width + 0.16,
        0.10,
        1.10,
        "Furniture",
        "Fabric_Oatmeal",
        0.045,
    )
    cub(
        room + "_Duvet",
        x,
        plan_y + 0.20,
        0.635,
        width + 0.015,
        length - 0.45,
        0.12,
        "Furniture",
        "Fabric_Main",
        0.055,
    )
    pillow_count = 2 if width >= 1.35 else 1
    for index in range(pillow_count):
        pillow_x = x + (index - (pillow_count - 1) / 2) * 0.65
        cub(
            room + f"_Pillow_{index + 1}",
            pillow_x,
            plan_y - 0.67,
            0.68,
            0.59,
            0.39,
            0.15,
            "Decor",
            "Porcelain",
            0.07,
            False,
        )
    cub(
        room + "_Folded_Throw",
        x,
        plan_y + 0.65,
        0.705,
        width + 0.025,
        0.43,
        0.045,
        "Decor",
        "Fabric_Oatmeal",
        0.02,
        False,
    )


def dining_chair(name, x, plan_y, back_direction):
    cub(
        name + "_Seat",
        x,
        plan_y,
        0.46,
        0.47,
        0.48,
        0.10,
        "Furniture",
        "Fabric_Main",
        0.045,
    )
    cub(
        name + "_Back",
        x + back_direction * 0.20,
        plan_y,
        0.71,
        0.08,
        0.46,
        0.45,
        "Furniture",
        "Fabric_Main",
        0.035,
    )
    for offset_x in (-0.17, 0.17):
        for offset_y in (-0.18, 0.18):
            cub(
                name + "_Leg",
                x + offset_x,
                plan_y + offset_y,
                0.21,
                0.04,
                0.04,
                0.42,
                "Furniture",
                "Oak_Joinery",
                0.008,
            )


# Living room: generously upholstered sofa, oak media console and layered rug.
cub(
    "Living_Sofa_Platform",
    0.68,
    1.95,
    0.23,
    0.97,
    2.30,
    0.28,
    "Furniture",
    "Fabric_Oatmeal",
    0.08,
)
cub(
    "Living_Sofa_Back",
    0.27,
    1.95,
    0.63,
    0.22,
    2.30,
    0.66,
    "Furniture",
    "Fabric_Main",
    0.09,
)
for plan_y in (0.83, 3.07):
    cub(
        "Living_Sofa_Arm",
        0.70,
        plan_y,
        0.54,
        0.94,
        0.20,
        0.48,
        "Furniture",
        "Fabric_Main",
        0.08,
    )
for index, plan_y in enumerate((1.23, 1.95, 2.67)):
    cub(
        f"Living_Sofa_Seat_{index}",
        0.72,
        plan_y,
        0.47,
        0.79,
        0.69,
        0.22,
        "Furniture",
        "Fabric_Main",
        0.09,
    )
    cub(
        f"Living_Sofa_Back_Cushion_{index}",
        0.43,
        plan_y,
        0.78,
        0.26,
        0.65,
        0.43,
        "Furniture",
        "Fabric_Main",
        0.10,
    )
cub(
    "Living_Rug",
    1.75,
    1.95,
    0.015,
    2.45,
    2.80,
    0.025,
    "Decor",
    "Fabric_Oatmeal",
    0.012,
    False,
)
round_object("Living_Coffee_Table_Top", 1.72, 1.85, 0.37, 0.38, 0.07, "Countertop")
round_object("Living_Coffee_Table_Base", 1.72, 1.85, 0.17, 0.23, 0.32, "Oak_Joinery")
round_object("Living_Side_Table", 0.70, 3.65, 0.43, 0.25, 0.06, "Oak_Joinery")
round_object("Living_Side_Table_Base", 0.70, 3.65, 0.22, 0.16, 0.42, "Oak_Joinery")
cabinet("Living_Media_Console", 3.09, 1.85, 0.36, 2.05, 0.36, 0.16, "west")
cub(
    "Living_TV",
    3.30,
    1.85,
    1.24,
    0.055,
    1.22,
    0.70,
    "Fixed_Joinery",
    "Appliance",
    0.018,
)

# Compact four-seat dining setting; an unobstructed corridor remains above it.
cub(
    "Dining_Oval_Table",
    4.65,
    5.05,
    0.755,
    0.85,
    1.30,
    0.055,
    "Furniture",
    "Oak_Joinery",
    0.22,
)
for plan_y in (4.68, 5.42):
    cub(
        "Dining_Table_Pedestal",
        4.65,
        plan_y,
        0.37,
        0.42,
        0.13,
        0.72,
        "Furniture",
        "Oak_Joinery",
        0.045,
    )
for index, plan_y in enumerate((4.73, 5.37)):
    dining_chair(f"Dining_Chair_West_{index}", 3.93, plan_y, -1)
    dining_chair(f"Dining_Chair_East_{index}", 5.37, plan_y, 1)
cabinet("Entry_Shoe_Storage", 1.99, 6.70, 0.22, 0.57, 1.02, 0.08, "east")

# Bedroom 3 is the tour's left bedroom; Bedroom 2 is its middle/nursery room.
bed("Bedroom_3", 5.60, 1.20, 0.90, 1.90)
cabinet("Bedroom_3_Wardrobe", 3.78, 1.30, 0.55, 1.65, 2.23, 0.10, "east")
cub(
    "Bedroom_3_Desk",
    4.32,
    3.04,
    0.745,
    1.40,
    0.45,
    0.055,
    "Furniture",
    "Oak_Joinery",
    0.025,
)
for x in (3.72, 4.92):
    cub(
        "Bedroom_3_Desk_Leg",
        x,
        3.04,
        0.36,
        0.055,
        0.38,
        0.72,
        "Furniture",
        "Oak_Joinery",
        0.01,
    )
round_object("Bedroom_3_Desk_Stool", 4.32, 3.04, 0.46, 0.22, 0.08, "Fabric_Main")
round_object("Bedroom_3_Stool_Base", 4.32, 3.04, 0.23, 0.12, 0.44, "Oak_Joinery")
bed("Bedroom_2", 8.20, 1.37, 1.20, 2.00)
cabinet("Bedroom_2_Wardrobe", 6.76, 1.30, 0.55, 1.65, 2.23, 0.10, "east")
cabinet("Bedroom_2_Low_Storage", 8.30, 3.02, 1.60, 0.46, 0.73, 0.10, "north")
round_object("Bedroom_2_Bedside", 9.00, 0.85, 0.47, 0.22, 0.07, "Oak_Joinery")
round_object("Bedroom_2_Bedside_Base", 9.00, 0.85, 0.24, 0.13, 0.44, "Oak_Joinery")
bed("Main_Bedroom", 11.30, 1.35, 1.60, 2.00)
cabinet("Main_Bedroom_Wardrobe", 12.23, 3.40, 0.60, 1.55, 2.23, 0.10, "west")
for x in (10.24, 12.34):
    round_object("Main_Bedroom_Bedside", x, 0.75, 0.48, 0.20, 0.07, "Oak_Joinery")
    round_object("Main_Bedroom_Bedside_Base", x, 0.75, 0.24, 0.13, 0.44, "Oak_Joinery")
cub(
    "Main_Bedroom_Rug",
    11.25,
    1.75,
    0.016,
    2.30,
    2.70,
    0.024,
    "Decor",
    "Fabric_Oatmeal",
    0.01,
    False,
)

# L-shaped kitchen: realistic 600 mm counter depth, 900 mm working height.
cabinet("Kitchen_West_Base", 3.92, 7.60, 0.60, 2.05, 0.76, 0.10, "east")
cub(
    "Kitchen_West_Counter",
    3.92,
    7.60,
    0.89,
    0.64,
    2.07,
    0.04,
    "Fixed_Joinery",
    "Countertop",
    0.009,
)
cabinet("Kitchen_Back_Base", 4.94, 8.49, 1.36, 0.62, 0.76, 0.10, "north")
cub(
    "Kitchen_Back_Counter",
    4.94,
    8.49,
    0.89,
    1.39,
    0.65,
    0.04,
    "Fixed_Joinery",
    "Countertop",
    0.009,
)
cabinet("Kitchen_West_Upper", 3.82, 7.61, 0.36, 1.94, 0.67, 1.68, "east")
cub(
    "Kitchen_Backsplash",
    3.615,
    7.60,
    1.26,
    0.018,
    2.02,
    0.72,
    "Fixed_Joinery",
    "Wet_Tile",
    0.003,
)
cub(
    "Kitchen_Induction_Hob",
    3.94,
    7.24,
    0.922,
    0.49,
    0.59,
    0.022,
    "Fixed_Joinery",
    "Appliance",
    0.012,
)
for plan_y in (7.09, 7.39):
    round_object(
        "Kitchen_Hob_Ring",
        3.94,
        plan_y,
        0.936,
        0.10,
        0.003,
        "Metal_Champagne",
        "Fixed_Joinery",
    )
cub(
    "Kitchen_Sink_Rim",
    4.93,
    8.45,
    0.92,
    0.60,
    0.43,
    0.025,
    "Fixed_Joinery",
    "Metal_Champagne",
    0.035,
)
cub(
    "Kitchen_Sink_Bowl",
    4.93,
    8.45,
    0.936,
    0.52,
    0.35,
    0.023,
    "Fixed_Joinery",
    "Appliance",
    0.04,
)
cub(
    "Kitchen_Tap_Stem",
    4.93,
    8.69,
    1.10,
    0.025,
    0.025,
    0.36,
    "Fixed_Joinery",
    "Metal_Champagne",
    0.01,
)
cub(
    "Kitchen_Tap_Spout",
    4.93,
    8.58,
    1.27,
    0.025,
    0.24,
    0.025,
    "Fixed_Joinery",
    "Metal_Champagne",
    0.009,
)
cub(
    "Kitchen_Fridge",
    5.30,
    6.84,
    0.93,
    0.64,
    0.66,
    1.86,
    "Fixed_Joinery",
    "Cabinet_Front",
    0.025,
)
cub(
    "Kitchen_Fridge_Handle",
    5.12,
    7.187,
    1.16,
    0.027,
    0.04,
    0.46,
    "Fixed_Joinery",
    "Metal_Champagne",
    0.01,
)

# Wet rooms retain the cream/ivory palette and separate fixtures.
for room, toilet_x, vanity_x, shower_x in [
    ("Common_Bath", 6.94, 8.28, 8.13),
    ("Ensuite", 9.08, 10.73, 10.61),
]:
    cub(
        room + "_WC_Cistern",
        toilet_x,
        6.19,
        0.56,
        0.39,
        0.19,
        0.74,
        "Fixed_Joinery",
        "Porcelain",
        0.05,
    )
    soft_shape(
        room + "_WC_Pan",
        toilet_x,
        5.93,
        0.31,
        (0.39, 0.62, 0.48),
        "Porcelain",
        "Fixed_Joinery",
    )
    soft_shape(
        room + "_WC_Seat",
        toilet_x,
        5.90,
        0.45,
        (0.38, 0.52, 0.075),
        "Porcelain",
        "Fixed_Joinery",
    )
    cabinet(room + "_Vanity", vanity_x, 4.93, 0.42, 0.64, 0.50, 0.32, "west")
    cub(
        room + "_Vanity_Top",
        vanity_x,
        4.93,
        0.86,
        0.45,
        0.66,
        0.06,
        "Fixed_Joinery",
        "Countertop",
        0.025,
    )
    soft_shape(
        room + "_Basin",
        vanity_x - 0.02,
        4.93,
        0.91,
        (0.37, 0.46, 0.10),
        "Porcelain",
        "Fixed_Joinery",
    )
    cub(
        room + "_Mirror",
        vanity_x + 0.20,
        4.93,
        1.52,
        0.025,
        0.61,
        0.86,
        "Fixed_Joinery",
        "Glass",
        0.07,
    )
    cub(
        room + "_Shower_Zone",
        shower_x,
        5.91,
        0.011,
        0.85,
        0.85,
        0.02,
        "Decor",
        "Wet_Tile",
        0.01,
        False,
    )
    cub(
        room + "_Shower_Stem",
        shower_x,
        6.29,
        1.46,
        0.025,
        0.025,
        1.22,
        "Fixed_Joinery",
        "Metal_Champagne",
        0.01,
    )
    round_object(
        room + "_Shower_Head",
        shower_x,
        6.13,
        2.09,
        0.115,
        0.025,
        "Metal_Champagne",
        "Fixed_Joinery",
    )
    cub(
        room + "_Shower_Glass",
        shower_x - 0.42,
        6.06,
        1.01,
        0.012,
        0.48,
        2.02,
        "Fixed_Joinery",
        "Glass",
        0.003,
    )
    cub(
        room + "_Drain",
        shower_x,
        6.12,
        0.025,
        0.10,
        0.10,
        0.008,
        "Decor",
        "Metal_Champagne",
        0.003,
        False,
    )

cub(
    "Service_Yard_Washer",
    6.49,
    8.49,
    0.44,
    0.60,
    0.62,
    0.88,
    "Fixed_Joinery",
    "Porcelain",
    0.035,
)
washer_door = round_object(
    "Service_Yard_Washer_Door",
    6.49,
    8.165,
    0.47,
    0.205,
    0.025,
    "Appliance",
    "Fixed_Joinery",
)
washer_door.rotation_euler.x = math.pi / 2
cabinet("Service_Yard_Upper_Storage", 6.49, 8.59, 0.94, 0.38, 0.57, 1.73, "north")
for height in (0.40, 0.95, 1.50, 2.05):
    cub(
        "Shelter_Freestanding_Shelf",
        0.48,
        6.70,
        height,
        0.66,
        0.45,
        0.035,
        "Furniture",
        "Oak_Joinery",
        0.006,
    )
for x in (0.19, 0.77):
    cub(
        "Shelter_Shelf_Upright",
        x,
        6.70,
        1.08,
        0.04,
        0.43,
        2.16,
        "Furniture",
        "Cabinet_Front",
        0.005,
    )
cub(
    "AC_Ledge_Condenser_Indicative",
    9.90,
    7.01,
    0.49,
    0.88,
    0.38,
    0.74,
    "Fixed_Joinery",
    "Porcelain",
    0.025,
)

# Schedule actual mesh bounds after dependency evaluation, not nominal strings.
bpy.context.view_layer.update()
with (ROOT / "docs/schedules/furniture-component-schedule.csv").open(
    "w", newline=""
) as stream:
    writer = csv.writer(stream)
    writer.writerow(
        ["component", "width_m", "depth_m", "height_m", "x_m", "plan_y_m", "z_m"]
    )
    for obj in sorted(bpy.context.scene.objects, key=lambda item: item.name):
        if obj.type == "MESH" and any(
            c.name in {"Furniture", "Fixed_Joinery"} for c in obj.users_collection
        ):
            writer.writerow(
                [
                    obj.name,
                    *[round(value, 4) for value in obj.dimensions],
                    round(obj.location.x, 4),
                    round(-obj.location.y, 4),
                    round(obj.location.z, 4),
                ]
            )
exec((ROOT / "scripts/validate_model.py").read_text(), globals())
validate_routes("furnished-routes")

# Frame a useful overview once for this milestone.
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == "VIEW_3D":
            view = area.spaces.active.region_3d
            view.view_location = (6.3, -4.4, 0.3)
            view.view_distance = 16
            view.view_rotation = Quaternion((1, 0, 0, 0))
            view.view_perspective = "ORTHO"
