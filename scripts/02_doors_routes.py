"""Milestone 2: editable doors, windows and explicit connected route curves.

Executed in build_oak_ville.py's namespace. Door pivots store open/closed
angles; the default state is open for circulation inspection.
"""

import csv


def create_route(name, points):
    curve = bpy.data.curves.new(name, "CURVE")
    curve.dimensions = "3D"
    curve.bevel_depth = 0.012
    curve.bevel_resolution = 2
    spline = curve.splines.new("POLY")
    spline.points.add(len(points) - 1)
    for point, (x, plan_y) in zip(spline.points, points):
        point.co = (x, -plan_y, 0.035, 1)
    obj = bpy.data.objects.new(name, curve)
    COLS["Walkthrough"].objects.link(obj)
    obj.hide_render = True
    obj["route_points_plan_m"] = json.dumps(points)
    obj["capsule_diameter_m"] = 0.50
    obj["capsule_height_m"] = 1.70
    obj.data.materials.append(bpy.data.materials["Annotation"])
    return obj


door_schedule = []
for room, axis, fixed, start, end, thickness, angle in DOORS:
    if room == "Shelter":
        angle = 90  # Opens out of the protected shelter, as shown on the plan.
    pivot = bpy.data.objects.new(room + "_Door_Hinge", None)
    COLS["Doors_Windows"].objects.link(pivot)
    pivot.location = (
        (start + 0.03, -fixed, 0) if axis == "h" else (fixed, -(start + 0.03), 0)
    )
    pivot.empty_display_size = 0.12
    pivot["closed_angle_degrees"] = 0.0
    pivot["open_angle_degrees"] = float(angle)
    pivot["door_state"] = "OPEN"
    pivot["opening_width_estimated_m"] = end - start
    leaf_width = end - start - 0.065
    if axis == "h":
        leaf_bounds = (0, leaf_width, -0.022, 0.022, 0.012, 2.105)
    else:
        leaf_bounds = (-0.022, 0.022, 0, leaf_width, 0.012, 2.105)
    leaf = box(
        room + "_Door_Leaf", leaf_bounds, "Doors_Windows", "Cabinet_Front", 0.006
    )
    leaf.parent = pivot
    pivot.rotation_euler.z = math.radians(angle)
    leaf["hinged_component"] = True
    # Frame members only: no invisible box spanning the doorway.
    for location in (start + 0.015, end - 0.015):
        if axis == "h":
            bounds = (
                location - 0.015,
                location + 0.015,
                fixed - thickness / 2 - 0.012,
                fixed + thickness / 2 + 0.012,
                0,
                2.15,
            )
        else:
            bounds = (
                fixed - thickness / 2 - 0.012,
                fixed + thickness / 2 + 0.012,
                location - 0.015,
                location + 0.015,
                0,
                2.15,
            )
        box(room + "_Door_Jamb", bounds, "Doors_Windows", "Oak_Joinery", 0.003)
    if axis == "h":
        bounds = (
            start,
            end,
            fixed - thickness / 2 - 0.012,
            fixed + thickness / 2 + 0.012,
            2.12,
            2.15,
        )
    else:
        bounds = (
            fixed - thickness / 2 - 0.012,
            fixed + thickness / 2 + 0.012,
            start,
            end,
            2.12,
            2.15,
        )
    box(room + "_Door_Frame_Head", bounds, "Doors_Windows", "Oak_Joinery", 0.003)
    # Handle coordinates are local to the hinge, so they follow the leaf.
    handle = cub(
        room + "_Door_Handle",
        leaf_width - 0.10 if axis == "h" else 0.055,
        -0.055 if axis == "h" else leaf_width - 0.10,
        1.02,
        0.11 if axis == "h" else 0.025,
        0.025 if axis == "h" else 0.11,
        0.025,
        "Doors_Windows",
        "Metal_Champagne",
        0.009,
        False,
    )
    handle.parent = pivot
    door_schedule.append(
        {
            "room": room,
            "opening_m": round(end - start, 3),
            "between_frames_m": round(end - start - 0.06, 3),
            "clear_head_m": 2.12,
            "open_degrees": angle,
            "evidence": "Estimated from photograph; site measure required",
        }
    )

# Editable glazing and mullions; facade walls already contain apertures.
for room, left, right in [
    ("Living", 0.4, 3.15),
    ("Bedroom_3", 3.60, 5.85),
    ("Bedroom_2", 6.70, 9.12),
    ("Main_Bedroom", 9.62, 12.35),
]:
    box(
        room + "_Window_Glass",
        (left, right, -0.012, 0.012, 0.85, 2.35),
        "Doors_Windows",
        "Glass",
    )
    for x in (left, (left + right) / 2, right):
        cub(
            room + "_Window_Mullion",
            x,
            0,
            1.6,
            0.035,
            0.07,
            1.5,
            "Doors_Windows",
            "Cabinet_Front",
            0.003,
        )
    for height in (0.86, 2.34):
        cub(
            room + "_Window_Rail",
            (left + right) / 2,
            0,
            height,
            right - left,
            0.07,
            0.035,
            "Doors_Windows",
            "Cabinet_Front",
            0.003,
        )
box(
    "Main_East_Window_Glass",
    (12.663, 12.687, 1.4, 3.1, 0.85, 2.35),
    "Doors_Windows",
    "Glass",
)
for room, left, right in [("Common_Bath", 6.85, 7.55), ("Ensuite", 9.5, 10.3)]:
    box(
        room + "_Vent_Window",
        (left, right, 6.388, 6.412, 1.8, 2.35),
        "Doors_Windows",
        "Glass",
    )
for plan_y in [6.7 + index * 0.10 for index in range(20)]:
    cub(
        "Yard_Vent_Louvre",
        7.75,
        plan_y,
        1.75,
        0.12,
        0.025,
        1.3,
        "Doors_Windows",
        "Cabinet_Front",
        0.003,
    )

ROUTES = {
    "W01_entry-dining": [(2.70, 7.05), (2.70, 6.5), (3.0, 5.9), (3.0, 4.9)],
    "W02_dining-living": [(3.0, 4.9), (2.7, 4.0), (2.45, 3.25), (2.45, 2.35)],
    "W03_dining-kitchen": [(3.0, 4.9), (3.0, 6.05), (4.70, 6.05), (4.70, 7.7)],
    "W04_bedroom_corridor": [
        (2.7, 4.0),
        (3.7, 3.9),
        (5.85, 3.9),
        (6.9, 3.9),
        (8.9, 3.9),
    ],
    "W05_Bedroom_3": [(5.85, 3.9), (5.85, 2.85), (5.85, 2.42)],
    "W06_Bedroom_2": [(6.90, 3.9), (6.90, 2.8), (7.15, 2.55)],
    "W07_main_bedroom": [(8.90, 3.9), (10.70, 3.9), (10.70, 2.9)],
    "W08_common_bath": [(7.15, 3.9), (7.15, 4.95), (7.55, 5.4)],
    "W09_ensuite": [(9.90, 3.9), (9.95, 4.9), (10.15, 5.25)],
    "W10_service_yard": [(4.70, 7.7), (5.25, 7.7), (6.25, 7.7), (6.5, 7.25)],
    "W11_shelter_access": [(3.0, 5.9), (2.25, 5.65), (1.3, 5.65), (0.9, 5.65)],
}
for name, points in ROUTES.items():
    create_route(name, points)

entry_camera = camera("FP_Entry_160cm_65deg", (2.70, 7.05, 1.60), (2.8, 4.9, 1.60))
entry_camera["purpose"] = "Human-scale entry start; horizontal field of view 65 degrees"
with (ROOT / "docs/door-schedule.csv").open("w", newline="") as stream:
    writer = csv.DictWriter(stream, fieldnames=door_schedule[0].keys())
    writer.writeheader()
    writer.writerows(door_schedule)

bpy.context.view_layer.update()
exec(
    compile(
        (ROOT / "scripts/validate_model.py").read_text(),
        str(ROOT / "scripts/validate_model.py"),
        "exec",
    ),
    globals(),
)
validate_routes("architecture-routes")
