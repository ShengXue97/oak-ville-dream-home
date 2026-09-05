"""Milestone 5: inspectable collision proxies and human-scale deliverables.

This prepares navigation/export data; Blender walk mode is not a physics
engine. The geometry checks are run separately and reported with limitations.
"""

import csv
import runpy

exec((ROOT / "scripts/validate_model.py").read_text(), globals())
fixture_helpers = runpy.run_path(str(ROOT / "scripts/fixture_details.py"))
fixture_helpers["refine_basins"](globals())
runpy.run_path(str(ROOT / "scripts/furniture_overhaul.py"))["apply"]()
runpy.run_path(str(ROOT / "scripts/complete_services.py"))["apply"]()
runpy.run_path(str(ROOT / "scripts/validate_services.py"))

# More centred yard approach avoids skimming the washer's projecting door.
for name in ("W03_dining-kitchen",):
    route = bpy.data.objects[name]
    points = json.loads(route["route_points_plan_m"])
    points = [
        [x, 7.625 if abs(plan_y - 7.7) < 0.001 else plan_y] for x, plan_y in points
    ]
    route["route_points_plan_m"] = json.dumps(points)
    for point, (x, plan_y) in zip(route.data.splines[0].points, points):
        point.co = (x, -plan_y, 0.035, 1)

collection("Collision_Architecture", COLS["Collision"])
collection("Collision_Furniture", COLS["Collision"])
collection("Collision_Doors", COLS["Collision"])
collection("Calibration", COLS["Walkthrough"])

# Simplified collision boxes retain each source's local origin and transform.
# Door proxies follow the original hinge so opened doors have opened colliders.
collision_records = []
bpy.context.view_layer.update()
for source in list(bpy.context.scene.objects):
    if source.type != "MESH" or not source.get("collision_source", False):
        continue
    if any(c.name.startswith("Collision") for c in source.users_collection):
        continue
    role = "Collision_Furniture"
    if any(
        c.name in {"Architecture", "Ceilings", "Beams_Soffits", "Doors_Windows"}
        for c in source.users_collection
    ):
        role = "Collision_Architecture"
    if source.get("hinged_component"):
        role = "Collision_Doors"
    corners = list(source.bound_box)
    low = [min(point[axis] for point in corners) for axis in range(3)]
    high = [max(point[axis] for point in corners) for axis in range(3)]
    vertices = [
        (x, y, z)
        for z in (low[2], high[2])
        for y in (low[1], high[1])
        for x in (low[0], high[0])
    ]
    mesh = bpy.data.meshes.new("COL_" + source.name)
    mesh.from_pydata(
        vertices,
        [],
        [
            (0, 1, 3, 2),
            (4, 6, 7, 5),
            (0, 4, 5, 1),
            (2, 3, 7, 6),
            (0, 2, 6, 4),
            (1, 5, 7, 3),
        ],
    )
    mesh.flip_normals()
    proxy = bpy.data.objects.new("COL_" + source.name, mesh)
    COLS[role].objects.link(proxy)
    proxy.parent = source.parent
    proxy.matrix_world = source.matrix_world.copy()
    proxy.display_type = "WIRE"
    proxy.hide_render = True
    proxy["source_object"] = source.name
    proxy["collision_source"] = False
    collision_records.append({"proxy": proxy.name, "source": source.name, "role": role})
for layer in bpy.context.scene.view_layers:
    layer.layer_collection.children["Collision"].exclude = True
(ROOT / "docs/validation/collision-manifest.json").write_text(
    json.dumps(collision_records, indent=2)
)

# Calibration group can be scaled as a whole without changing building units.
human = bpy.data.objects.new("Human_Reference_170cm_Adjustable", None)
COLS["Calibration"].objects.link(human)
human.location = (2.70, -7.05, 0)
human["height_m_at_scale_1"] = 1.70
human["adjust_height"] = "Set uniform scale to desired height / 1.70"
human["eye_height_default_m"] = 1.60
human["capsule_diameter_default_m"] = 0.50
for name, x, z, width, height in [
    ("Human_Torso", 0, 1.05, 0.42, 0.58),
    ("Human_Leg_L", -0.12, 0.38, 0.15, 0.76),
    ("Human_Leg_R", 0.12, 0.38, 0.15, 0.76),
    ("Human_Head", 0, 1.535, 0.22, 0.33),
]:
    part = cub(
        name,
        x,
        0,
        z,
        width,
        0.22,
        height,
        "Calibration",
        "Fabric_Oatmeal",
        0.025,
        False,
    )
    part.parent = human
    part.hide_render = True
calibration = cub(
    "Calibration_Exactly_1m_Cube",
    1.0,
    2.5,
    0.5,
    1,
    1,
    1,
    "Calibration",
    "Annotation",
    0,
    False,
)
calibration.hide_render = True
for layer in bpy.context.scene.view_layers:
    layer.layer_collection.children["Walkthrough"].children[
        "Calibration"
    ].exclude = True

# Eye-level camera positions are independent of the wider presentation camera.
room_cameras = {
    "Entry": ((2.70, 6.55, 1.60), (3.2, 5.68, 1.60)),
    "Dining": ((2.8, 4.0, 1.60), (4.65, 5.05, 1.15)),
    "Bedroom_3": ((5.80, 3.05, 1.60), (4.95, 1.2, 1.05)),
    "Bedroom_2": ((7.15, 2.55, 1.60), (8.20, 1.35, 1.10)),
    "Main_Bedroom": ((10.70, 2.90, 1.60), (11.30, 1.0, 1.15)),
    "Kitchen": ((4.70, 6.05, 1.60), (4.42, 8.50, 1.10)),
    "Common_Bath": ((7.15, 4.92, 1.60), (7.40, 6.05, 1.05)),
    "Ensuite": ((9.95, 4.95, 1.60), (9.62, 6.05, 1.05)),
    "Common_Bath_Vanity": ((7.35, 5.50, 1.60), (8.28, 4.93, 1.25)),
    "Ensuite_Vanity": ((9.78, 5.45, 1.60), (10.73, 4.93, 1.25)),
    "Service_Yard": ((6.40, 7.65, 1.60), (6.50, 8.50, 1.10)),
    "Shelter": ((1.00, 5.40, 1.60), (0.55, 6.75, 1.10)),
}
for room, (location, target) in room_cameras.items():
    camera("PREVIEW_" + room, location, target, fov=65)
for route in list(bpy.context.scene.objects):
    if not route.get("route_points_plan_m"):
        continue
    points = json.loads(route["route_points_plan_m"])
    first, second = points[:2]
    if route.name.startswith("W03"):
        first, second = points[1], points[-1]
    elif route.name.startswith("W11"):
        first, second = points[1], points[-1]
    name = "EYE_" + route.name
    eye = camera(name, (*first, 1.60), (*second, 1.60), fov=65)
    eye["route"] = route.name
camera("PRESENTATION_Axonometric", (17.5, 17.0, 15), (6.3, 4.4, 0), fov=50, ortho=18)

with (ROOT / "docs/schedules/camera-schedule.csv").open("w", newline="") as stream:
    writer = csv.writer(stream)
    writer.writerow(
        ["camera", "x_m", "plan_y_m", "eye_z_m", "horizontal_fov_deg", "purpose"]
    )
    for obj in sorted(bpy.context.scene.objects, key=lambda item: item.name):
        if obj.type == "CAMERA":
            writer.writerow(
                [
                    obj.name,
                    round(obj.location.x, 3),
                    round(-obj.location.y, 3),
                    round(obj.location.z, 3),
                    round(math.degrees(obj.data.angle_x), 2),
                    (
                        "Orthographic inspection"
                        if obj.data.type == "ORTHO"
                        else "Human eye-level"
                    ),
                ]
            )

# Add dimensions as text/lines in the Blender plan view as well as the SVG.
for chain, values in CHAINS.items():
    accumulated = 0
    for index, millimetres in enumerate(values):
        length = millimetres / 1000
        if chain in {"upper", "lower"}:
            plan_y = -0.60 if chain == "upper" else 9.55
            text_obj = label(
                "PLAN_DIM_" + chain + str(index),
                str(millimetres),
                accumulated + length / 2,
                plan_y - 0.10,
                2.85,
                0.16,
            )
            cub(
                "PLAN_DIM_LINE_" + chain,
                accumulated + length / 2,
                plan_y,
                2.84,
                length,
                0.008,
                0.008,
                "Plan_Annotations",
                "Annotation",
                0,
                False,
            )
        else:
            x = -0.7 if chain == "left" else 13.30
            text_obj = label(
                "PLAN_DIM_" + chain + str(index),
                str(millimetres),
                x - 0.12,
                accumulated + length / 2,
                2.85,
                0.16,
            )
            text_obj.rotation_euler.z = math.pi / 2
            cub(
                "PLAN_DIM_LINE_" + chain,
                x,
                accumulated + length / 2,
                2.84,
                0.008,
                length,
                0.008,
                "Plan_Annotations",
                "Annotation",
                0,
                False,
            )
        accumulated += length
for obj in COLS["Plan_Annotations"].objects:
    if obj.type == "FONT" and obj.name.endswith("_Label"):
        obj.location.z = 2.85
label(
    "PLAN_Title",
    "OAK VILLE / MODEL DATUMS IN mm / VERIFY ASSUMED FACES ON SITE",
    6.30,
    -1.30,
    2.85,
    0.18,
)
bpy.data.objects["PLAN_Orthographic"].data.ortho_scale = 16.6

route_report = validate_routes()
fit_report = validate_furniture_and_swings()
exec((ROOT / "scripts/designer_documents.py").read_text(), globals())
dimension_report = write_designer_documents()
validate_dimensions()

# Embed the designer instructions in the blend, alongside the packed references.
for filename in [
    "DESIGNER_HANDOFF.md",
    "RESTYLING.md",
    "WALKTHROUGH.md",
    "VALIDATION_REPORT.md",
]:
    path = ROOT / "docs" / filename
    if path.exists():
        text_block = bpy.data.texts.get(filename) or bpy.data.texts.new(filename)
        text_block.clear()
        text_block.write(path.read_text(encoding="utf-8"))
for obj in bpy.context.scene.objects:
    if obj.type == "MESH" and any(
        c.name == "Architecture" for c in obj.users_collection
    ):
        obj["evidence_status"] = (
            "Written chain datums; thickness and unlabelled faces provisional. See DESIGNER_HANDOFF.md"
        )
    if obj.type == "MESH" and any(
        c.name in {"Furniture", "Fixed_Joinery"} for c in obj.users_collection
    ):
        obj["evidence_status"] = (
            "Proposed furniture/component dimensions; not surveyed or fabrication-ready"
        )

scene = bpy.context.scene
scene.camera = bpy.data.objects["PREVIEW_Living_Eye"]
bpy.context.window.view_layer = scene.view_layers["Enclosed_Walkthrough"]
for layer in scene.view_layers:
    layer.use = layer.name == "Enclosed_Walkthrough"
for window in bpy.context.window_manager.windows:
    for area in window.screen.areas:
        if area.type == "VIEW_3D":
            area.spaces.active.region_3d.view_perspective = "CAMERA"
            area.spaces.active.overlay.show_overlays = False

summary = {
    "routes_pass": route_report["all_pass"],
    "furniture_and_swings_pass": fit_report["all_pass"],
    "mesh_dimensions_pass": dimension_report["all_mesh_datums_pass"],
    "collision_proxies": len(collision_records),
    "scene_objects": len(scene.objects),
    "note": "Saved-file reopening and image review are recorded separately after this stage.",
}
(ROOT / "docs/validation/final-stage-validation.json").write_text(
    json.dumps(summary, indent=2)
)
runpy.run_path(str(ROOT / "scripts/refresh_designer_handoff.py"))
runpy.run_path(str(ROOT / "scripts/embed_unreal_lighting_profile.py"))
