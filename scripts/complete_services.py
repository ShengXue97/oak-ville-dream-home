"""Editable bathroom windows, indicative air conditioning and dining clearance.

All dimensions are metres. Plan coordinates use positive Y down the drawing;
Blender uses negative Y. Equipment is proposed, not manufacturer-selected.
"""

import json
import math
import uuid
from pathlib import Path

import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
REVISION = "services-1"


def box(
    name, position, size, material, group="Fixed_Joinery", bevel=0.008, solid=False
):
    obj = bpy.data.objects.get(name)
    if obj is not None:
        obj.parent = None
        obj.rotation_euler = (0, 0, 0)
    if obj is None:
        bpy.ops.mesh.primitive_cube_add(size=1)
        obj = bpy.context.object
        obj.name = name
        for collection in list(obj.users_collection):
            collection.objects.unlink(obj)
        bpy.data.collections[group].objects.link(obj)
    obj.location = (position[0], -position[1], position[2])
    obj.dimensions = size
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    if bevel and not obj.modifiers.get("Soft manufactured edges"):
        modifier = obj.modifiers.new("Soft manufactured edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
    obj.data.materials.clear()
    obj.data.materials.append(bpy.data.materials[material])
    obj["collision_source"] = solid
    obj["service_revision"] = REVISION
    obj["oakville_source_id"] = obj.get("oakville_source_id") or str(
        uuid.uuid5(uuid.NAMESPACE_URL, "oakville/services/" + name)
    )
    obj["evidence_status"] = (
        "Proposed equipment/fittings; verify installation and manufacturer dimensions on site"
    )
    return obj


def attach(child, parent):
    world = child.matrix_world.copy()
    child.parent = parent
    child.matrix_world = world


def windows():
    material = bpy.data.materials.get("Frosted_Privacy_Glass")
    if material is None:
        material = bpy.data.materials["Porcelain"].copy()
        material.name = "Frosted_Privacy_Glass"
        material.diffuse_color = (0.64, 0.73, 0.72, 1)
        shader = material.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Base Color"].default_value = material.diffuse_color
        shader.inputs["Roughness"].default_value = 0.65
    for room, left, right in [("Common_Bath", 6.85, 7.55), ("Ensuite", 9.5, 10.3)]:
        width = right - left
        centre = (left + right) / 2
        pane = bpy.data.objects[room + "_Vent_Window"]
        pane.location = (centre, -6.40, 2.075)
        pane.dimensions = (width - 0.08, 0.014, 0.47)
        pane.data.materials.clear()
        pane.data.materials.append(material)
        pane["collision_source"] = True
        pane["service_revision"] = REVISION
        pane["evidence_status"] = (
            "Existing provisional opening; proposed frosted top-hung window, shown closed"
        )
        for side, x in [
            ("Left", left + 0.02),
            ("Right", right - 0.02),
            ("Centre", centre),
        ]:
            box(
                room + "_Window_Frame_" + side,
                (x, 6.40, 2.075),
                (0.04, 0.075, 0.47),
                "Cabinet_Front",
                "Doors_Windows",
                0.003,
                True,
            )
        for side, z in [("Sill", 1.82), ("Head", 2.33)]:
            box(
                room + "_Window_Frame_" + side,
                (centre, 6.40, z),
                (width, 0.075, 0.04),
                "Cabinet_Front",
                "Doors_Windows",
                0.003,
                True,
            )
        for index, x in enumerate((left + width * 0.25, left + width * 0.75)):
            box(
                room + f"_Window_Latch_{index}",
                (x, 6.345, 1.865),
                (0.075, 0.023, 0.016),
                "Metal_Brushed_Steel",
                "Doors_Windows",
                0.004,
            )


def indoor_units():
    # Local +Y is the discharge face. Wall positions are deliberately separate
    # from cabinetry, window heads and door clearances.
    settings = [
        ("Living", (0.215, 2.0, 2.28), -math.pi / 2, 1.0),
        ("Bedroom_3", (4.55, 3.175, 2.30), 0, 0.82),
        ("Bedroom_2", (8.25, 3.175, 2.30), 0, 0.82),
        ("Main_Bedroom", (11.20, 4.255, 2.30), 0, 0.90),
    ]
    for room, position, angle, width in settings:
        origin = Vector((position[0], -position[1], position[2]))
        rotation = Matrix.Rotation(angle, 4, "Z")
        root = bpy.data.objects.get(room + "_Aircon_Assembly")
        if root is None:
            root = bpy.data.objects.new(room + "_Aircon_Assembly", None)
            bpy.data.collections["Fixed_Joinery"].objects.link(root)
        root.matrix_world = Matrix.Identity(4)
        components = [
            ("Body", (0, 0, 0), (width, 0.23, 0.28), "Porcelain", 0.032, True),
            (
                "Front_Panel",
                (0, 0.119, 0.018),
                (width - 0.025, 0.018, 0.205),
                "Cabinet_Front",
                0.008,
                False,
            ),
            (
                "Outlet_Recess",
                (0, 0.119, -0.105),
                (width - 0.12, 0.016, 0.045),
                "Appliance",
                0.004,
                False,
            ),
            (
                "Discharge_Flap",
                (0, 0.146, -0.125),
                (width - 0.11, 0.07, 0.012),
                "Porcelain",
                0.004,
                False,
            ),
            (
                "Status_Display",
                (width * 0.32, 0.133, -0.01),
                (0.034, 0.006, 0.012),
                "Appliance",
                0.002,
                False,
            ),
            (
                "Pipe_Cover_Stub",
                (width / 2 + 0.055, -0.08, 0),
                (0.11, 0.055, 0.065),
                "Cabinet_Front",
                0.008,
                False,
            ),
        ]
        for index in range(9):
            components.append(
                (
                    f"Intake_Slot_{index:02}",
                    (-width * 0.35 + index * width * 0.0875, -0.025, 0.141),
                    (0.033, 0.14, 0.004),
                    "Appliance",
                    0.001,
                    False,
                )
            )
        for suffix, offset, size, material, bevel, solid in components:
            name = room + "_Aircon_" + suffix
            obj = bpy.data.objects.get(name)
            if obj:
                obj.parent = None
                obj.rotation_euler = (0, 0, 0)
            local = Vector(offset)
            world = origin + rotation.to_3x3() @ local
            obj = box(
                name,
                (world.x, -world.y, world.z),
                size,
                material,
                bevel=bevel,
                solid=solid,
            )
            obj.rotation_euler.z = angle
            bpy.context.view_layer.update()
            attach(obj, root)
        root["nominal_width_m"] = width
        root["installation_note"] = (
            "Indicative wall unit; capacity, service clearance and full pipe/drain routes to be designed"
        )


def condenser_details():
    body = bpy.data.objects["AC_Ledge_Condenser_Indicative"]
    for index, x in enumerate((9.60, 10.20)):
        foot = box(
            f"AC_Ledge_Condenser_Foot_{index}",
            (x, 7.01, 0.06),
            (0.09, 0.48, 0.12),
            "Metal_Brushed_Steel",
            bevel=0.008,
            solid=True,
        )
        attach(foot, body)
    # Layered fan grille on the outward-facing side, made from ordinary meshes.
    for index in range(17):
        x = 9.60 + index * 0.023
        dx = x - 9.784
        height = 2 * math.sqrt(max(0.0, 0.235**2 - dx**2))
        bar = box(
            f"AC_Ledge_Fan_Grille_{index:02}",
            (x, 7.208, 0.52),
            (0.008, 0.017, height),
            "Metal_Brushed_Steel",
            bevel=0.002,
        )
        attach(bar, body)
    plate = box(
        "AC_Ledge_Fan_Recess",
        (9.784, 7.204, 0.52),
        (0.49, 0.005, 0.50),
        "Appliance",
        bevel=0.06,
    )
    attach(plate, body)
    panel = box(
        "AC_Ledge_Condenser_Service_Panel",
        (10.19, 7.205, 0.49),
        (0.20, 0.012, 0.59),
        "Cabinet_Front",
        bevel=0.008,
    )
    attach(panel, body)
    body["installation_note"] = (
        "One indicative multi-split outdoor unit on the only labelled A/C ledge. No additional master/kitchen ledge inferred. Manufacturer/system capacity not selected."
    )


def clear_dining_route():
    # Translate, never shrink, the table/chairs. Their descendants follow once.
    names = ("Dining_Oval_Table", "Dining_Table_", "Dining_Chair_", "Dining_Pendant_")
    delta = Vector((-0.20, 0.15, 0))
    for obj in bpy.context.scene.objects:
        if (
            obj.parent is None
            and obj.name.startswith(names)
            and not obj.get("kitchen_clearance_revision")
        ):
            obj.location += delta
            obj["kitchen_clearance_revision"] = REVISION
    bpy.context.view_layer.update()


def apply():
    windows()
    indoor_units()
    condenser_details()
    clear_dining_route()
    bpy.context.view_layer.update()
    bpy.ops.object.select_all(action="DESELECT")
    return {
        "bathroom_windows": 2,
        "indoor_aircon_units": 4,
        "outdoor_units": 1,
        "dining_translation_m": [-0.20, -0.15, 0],
    }


def refresh_proxies():
    """Add/update inspection proxies in an existing live scene after apply()."""
    import bmesh

    count = 0
    for source in list(bpy.context.scene.objects):
        if not source.get("service_revision") or not source.get("collision_source"):
            continue
        name = "COL_" + source.name
        proxy = bpy.data.objects.get(name)
        if proxy is None:
            mesh = bpy.data.meshes.new(name)
            mesh.from_pydata(
                [tuple(v) for v in source.bound_box],
                [],
                [
                    (0, 1, 2, 3),
                    (4, 7, 6, 5),
                    (0, 4, 5, 1),
                    (1, 5, 6, 2),
                    (2, 6, 7, 3),
                    (3, 7, 4, 0),
                ],
            )
            bm = bmesh.new()
            bm.from_mesh(mesh)
            bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
            bm.to_mesh(mesh)
            bm.free()
            proxy = bpy.data.objects.new(name, mesh)
            role = (
                "Collision_Architecture" if "Window" in name else "Collision_Furniture"
            )
            bpy.data.collections[role].objects.link(proxy)
        else:
            # Service solids are eight-vertex boxes; copy their unmodified cage
            # so repeated edits cannot leave an old proxy size behind.
            proxy.data = source.data.copy()
        proxy.parent = source.parent
        proxy.matrix_world = source.matrix_world.copy()
        proxy.hide_render = True
        proxy.display_type = "WIRE"
        proxy["source_object"] = source.name
        proxy["collision_source"] = False
        count += 1
    records = [
        {
            "proxy": obj.name,
            "source": obj["source_object"],
            "role": obj.users_collection[0].name,
        }
        for obj in bpy.context.scene.objects
        if "source_object" in obj and obj.name.startswith("COL_")
    ]
    (ROOT / "docs/validation/collision-manifest.json").write_text(
        json.dumps(sorted(records, key=lambda row: row["proxy"]), indent=2),
        encoding="utf-8",
    )
    return count


if __name__ == "__main__":
    print(apply())
