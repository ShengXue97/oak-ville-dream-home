"""Detailed, editable cream-and-oak furniture within the approved layout.

Geometry is authored here, not fetched from external asset libraries. Existing
object IDs and transforms survive replacement. Small construction details are
separate, named meshes with shared material roles and no gameplay collision.
Run apply('seating'), apply('bedrooms') or apply('fixtures') for live milestones;
apply() rebuilds every family deterministically.
"""

import json
import math
import uuid
from pathlib import Path

import bmesh
import bpy
from mathutils import Matrix, Vector

ROOT = Path(__file__).resolve().parents[1]
REVISION = "crafted-minimalist-1"


def source_objects():
    return [
        o
        for o in bpy.data.objects
        if o.type == "MESH"
        and "_Detail_" not in o.name
        and any(
            c.name in {"Furniture", "Fixed_Joinery", "Decor"}
            for c in o.users_collection
        )
    ]


def ensure_materials():
    if "Metal_Brushed_Steel" not in bpy.data.materials:
        steel = bpy.data.materials["Metal_Champagne"].copy()
        steel.name = "Metal_Brushed_Steel"
        steel.diffuse_color = (0.43, 0.46, 0.47, 1)
        shader = steel.node_tree.nodes.get("Principled BSDF")
        shader.inputs["Base Color"].default_value = (0.43, 0.46, 0.47, 1)
        shader.inputs["Metallic"].default_value = 0.9
        shader.inputs["Roughness"].default_value = 0.30


def signed_power(value, exponent):
    return math.copysign(abs(value) ** exponent, value)


def loop(radius=0.5, z=0.0, exponent=1.0, count=48):
    return [
        (
            radius * signed_power(math.cos(i * math.tau / count), exponent),
            radius * signed_power(math.sin(i * math.tau / count), exponent),
            z,
        )
        for i in range(count)
    ]


def profile_mesh(profile, exponent=1.0, count=48, closed=False):
    """Closed solid of oval/rounded-square rings; closed=True makes a rim."""
    vertices = [
        point for radius, z in profile for point in loop(radius, z, exponent, count)
    ]
    faces = []
    ring_pairs = len(profile) if closed else len(profile) - 1
    for ring in range(ring_pairs):
        next_ring = (ring + 1) % len(profile)
        for i in range(count):
            j = (i + 1) % count
            faces.append(
                (
                    ring * count + i,
                    ring * count + j,
                    next_ring * count + j,
                    next_ring * count + i,
                )
            )
    if not closed:
        for ring in (0, len(profile) - 1):
            centre = len(vertices)
            vertices.append((0, 0, profile[ring][1]))
            for i in range(count):
                faces.append((centre, ring * count + i, ring * count + (i + 1) % count))
    return vertices, faces


def mesh_data(name, vertices, faces, smooth=True):
    mesh = bpy.data.meshes.new(name + "_EditableMesh")
    mesh.from_pydata(vertices, [], faces)
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    mesh.update()
    for polygon in mesh.polygons:
        polygon.use_smooth = smooth
    return mesh


def envelope(obj):
    if "overhaul_original_bounds" not in obj:
        low = [min(point[axis] for point in obj.bound_box) for axis in range(3)]
        high = [max(point[axis] for point in obj.bound_box) for axis in range(3)]
        obj["overhaul_original_bounds"] = json.dumps([low, high])
    low, high = json.loads(obj["overhaul_original_bounds"])
    return Vector([(a + b) / 2 for a, b in zip(low, high)]), Vector(
        [b - a for a, b in zip(low, high)]
    )


def replace(obj, geometry, role=None):
    centre, size = envelope(obj)
    vertices, faces = geometry
    vertices = [
        centre + Vector([point[i] * size[i] for i in range(3)]) for point in vertices
    ]
    material = bpy.data.materials[role] if role else obj.data.materials[0]
    old = obj.data
    obj.data = mesh_data(obj.name, vertices, faces)
    obj.data.materials.append(material)
    obj.modifiers.clear()
    obj["furniture_revision"] = REVISION
    if old.users == 0:
        bpy.data.meshes.remove(old)
    return obj


def detail(base, suffix, geometry, role, size=(1, 1, 1), offset=(0, 0, 0)):
    """Size and offset use the source's original local bounding-box units."""
    name = base.name + "_Detail_" + suffix
    obj = bpy.data.objects.get(name)
    centre, extent = envelope(base)
    vertices, faces = geometry
    vertices = [
        centre + Vector([(p[i] * size[i] + offset[i]) * extent[i] for i in range(3)])
        for p in vertices
    ]
    mesh = mesh_data(name, vertices, faces)
    if obj is None:
        obj = bpy.data.objects.new(name, mesh)
        base.users_collection[0].objects.link(obj)
    else:
        old = obj.data
        obj.data = mesh
        if old.users == 0:
            bpy.data.meshes.remove(old)
    obj.parent = base
    obj.matrix_parent_inverse = Matrix.Identity(4)
    obj.matrix_world = base.matrix_world.copy()
    obj.data.materials.append(bpy.data.materials[role])
    obj["collision_source"] = False
    obj["furniture_revision"] = REVISION
    obj["assembly_source"] = base.name
    obj["oakville_source_id"] = str(uuid.uuid5(uuid.NAMESPACE_URL, "oak-ville/" + name))
    obj["evidence_status"] = (
        "Proposed furniture construction detail; confirm selected product"
    )
    return obj


def box_mesh():
    vertices = [
        (x, y, z) for z in (-0.5, 0.5) for y in (-0.5, 0.5) for x in (-0.5, 0.5)
    ]
    return vertices, [
        (0, 1, 3, 2),
        (4, 6, 7, 5),
        (0, 4, 5, 1),
        (2, 3, 7, 6),
        (0, 2, 6, 4),
        (1, 5, 7, 3),
    ]


def tube_detail(base, suffix, points, radius, role):
    centre, size = envelope(base)
    inverse = base.matrix_world.inverted()
    vertices = []
    for i, point in enumerate(points):
        tangent = (
            points[min(i + 1, len(points) - 1)] - points[max(0, i - 1)]
        ).normalized()
        guide = Vector((1, 0, 0)) if abs(tangent.x) < 0.9 else Vector((0, 1, 0))
        side = tangent.cross(guide).normalized()
        up = tangent.cross(side).normalized()
        for j in range(16):
            local = (
                inverse
                @ (
                    point
                    + radius
                    * (
                        side * math.cos(j * math.tau / 16)
                        + up * math.sin(j * math.tau / 16)
                    )
                )
                - centre
            )
            vertices.append([local[k] / size[k] for k in range(3)])
    faces = [
        tuple(reversed(range(16))),
        tuple((len(points) - 1) * 16 + i for i in range(16)),
    ]
    faces.extend(
        (
            r * 16 + i,
            r * 16 + (i + 1) % 16,
            (r + 1) * 16 + (i + 1) % 16,
            (r + 1) * 16 + i,
        )
        for r in range(len(points) - 1)
        for i in range(16)
    )
    return detail(base, suffix, (vertices, faces), role)


def piping(base, suffix, z, role="Fabric_Oatmeal", exponent=0.32, radius=0.475, axis=2):
    """A narrow closed sewn welt, kept inside the source envelope."""
    centre, size = envelope(base)
    axes = [i for i in range(3) if i != axis]
    path = loop(radius, 0, exponent, 64)
    points = []
    for p in path:
        q = [0.0, 0.0, 0.0]
        q[axes[0]], q[axes[1]], q[axis] = p[0], p[1], z
        points.append(q)
    vertices, faces = [], []
    for index, point in enumerate(points):
        tangent = Vector(points[(index + 1) % len(points)]) - Vector(points[index - 1])
        tangent = Vector([tangent[i] * size[i] for i in range(3)]).normalized()
        normal = Vector([1 if i == axis else 0 for i in range(3)])
        side = tangent.cross(normal).normalized()
        for j in range(6):
            shift = 0.0015 * (
                normal * math.cos(j * math.tau / 6) + side * math.sin(j * math.tau / 6)
            )
            vertices.append([point[i] + shift[i] / size[i] for i in range(3)])
    for i in range(len(points)):
        for j in range(6):
            faces.append(
                (
                    i * 6 + j,
                    i * 6 + (j + 1) % 6,
                    ((i + 1) % len(points)) * 6 + (j + 1) % 6,
                    ((i + 1) % len(points)) * 6 + j,
                )
            )
    return detail(base, suffix, (vertices, faces), role)


def plush(base, exponent=0.35, wrinkles=False):
    geometry = profile_mesh(
        [
            (0.03, -0.5),
            (0.38, -0.47),
            (0.47, -0.32),
            (0.5, -0.08),
            (0.5, 0.12),
            (0.47, 0.35),
            (0.38, 0.47),
            (0.03, 0.5),
        ],
        exponent,
        64,
    )
    if wrinkles:
        vertices, faces = geometry
        vertices = [
            (
                x,
                y,
                (
                    z
                    + 0.016
                    * math.sin(26 * x + 4 * y)
                    * math.cos(19 * y)
                    * (1 - abs(2 * x))
                    if z > 0.1
                    else z
                ),
            )
            for x, y, z in vertices
        ]
        geometry = vertices, faces
    return replace(base, geometry)


def cloth(base, folded=False):
    """A closed thin textile with draped edges and shallow, deterministic folds."""
    nx, ny = 32, 40
    vertices = []
    for side in (0, 1):
        for j in range(ny + 1):
            for i in range(nx + 1):
                x = i / nx - 0.5
                y = j / ny - 0.5
                edge = max(0, (abs(x) - 0.36) / 0.14)
                foot = max(0, (y - 0.35) / 0.15)
                z = (
                    0.25
                    + 0.075 * math.sin(19 * x + 4 * y)
                    + 0.045 * math.cos(25 * y - 6 * x)
                )
                z -= (0.20 if folded else 0.65) * edge**2 + 0.12 * foot**2
                z = max(-0.39, z) - side * (0.28 if folded else 0.065)
                vertices.append((x * (1 - 0.025 * (2 * y) ** 8), y, z))
    stride = (nx + 1) * (ny + 1)
    faces = []
    for side in range(2):
        for j in range(ny):
            for i in range(nx):
                a = side * stride + j * (nx + 1) + i
                faces.append((a, a + 1, a + nx + 2, a + nx + 1))
    border = list(range(nx + 1)) + [j * (nx + 1) + nx for j in range(1, ny + 1)]
    border += list(range(ny * (nx + 1) + nx - 1, ny * (nx + 1) - 1, -1))
    border += [j * (nx + 1) for j in range(ny - 1, 0, -1)]
    faces.extend(
        (a, b, b + stride, a + stride) for a, b in zip(border, border[1:] + border[:1])
    )
    return replace(base, (vertices, faces))


def seating():
    originals = source_objects()
    for obj in originals:
        name = obj.name
        if name.startswith("Living_Sofa"):
            plush(obj, 0.26, wrinkles="Cushion" in name or "_Seat_" in name)
            if "_Seat_" in name:
                piping(obj, "Upper_Welt", 0.22)
            elif "Back_Cushion" in name:
                piping(obj, "Face_Welt", 0.40, axis=0)
            elif "Platform" in name:
                detail(
                    obj,
                    "Recessed_Oak_Base",
                    box_mesh(),
                    "Oak_Joinery",
                    (0.90, 0.94, 0.15),
                    (0, 0, -0.42),
                )
        if name.startswith("Dining_Chair"):
            if name.endswith("_Seat"):
                plush(obj, 0.40)
                piping(obj, "Seat_Welt", 0.10)
                detail(
                    obj,
                    "Oak_Seat_Rail",
                    profile_mesh([(0.46, -0.5), (0.5, -0.2), (0.48, 0.5)], 0.30),
                    "Oak_Joinery",
                    (0.90, 0.94, 0.25),
                    (0, 0, -0.52),
                )
            elif name.endswith("_Back"):
                vertices, faces = box_mesh()
                # Curved upholstered shell, sampled across its width and height.
                vertices = []
                for side in (-1, 1):
                    for z in range(9):
                        for y in range(25):
                            yy = y / 24 - 0.5
                            zz = z / 8 - 0.5
                            xx = 0.22 * (2 * yy) ** 2 + 0.22 * side + 0.05 * zz
                            vertices.append((xx, yy, zz * (1 - 0.06 * (2 * yy) ** 2)))
                faces = []
                stride = 9 * 25
                for side in range(2):
                    for z in range(8):
                        for y in range(24):
                            a = side * stride + z * 25 + y
                            faces.append((a, a + 1, a + 26, a + 25))
                border = (
                    list(range(25))
                    + [z * 25 + 24 for z in range(1, 9)]
                    + list(range(8 * 25 + 23, 8 * 25 - 1, -1))
                    + [z * 25 for z in range(7, 0, -1)]
                )
                faces.extend(
                    (a, b, b + stride, a + stride)
                    for a, b in zip(border, border[1:] + border[:1])
                )
                replace(obj, (vertices, faces))
                bevel = obj.modifiers.new("Soft upholstered shell edge", "BEVEL")
                bevel.width = 0.006
                bevel.segments = 3
                normal = -1 if "_West_" in name else 1
                detail(
                    obj,
                    "Bent_Oak_Back",
                    (vertices, faces),
                    "Oak_Joinery",
                    (0.18, 0.98, 0.96),
                    (normal * 0.34, 0, 0),
                )
            elif "_Leg" in name:
                replace(
                    obj,
                    profile_mesh(
                        [(0.30, -0.5), (0.32, -0.43), (0.47, 0.43), (0.5, 0.5)], 0.5, 24
                    ),
                )
    for name in ("Dining_Oval_Table", "Bedroom_3_Desk"):
        obj = bpy.data.objects[name]
        replace(
            obj,
            profile_mesh(
                [(0.46, -0.5), (0.495, -0.18), (0.5, 0.23), (0.48, 0.5)],
                0.58 if name.startswith("Dining") else 0.16,
                64,
            ),
        )
        detail(
            obj,
            "Underside_Apron",
            profile_mesh([(0.45, -0.5), (0.49, 0.5)], 0.5),
            "Oak_Joinery",
            (0.85, 0.87, 1.25),
            (0, 0, -1.0),
        )
    for obj in originals:
        if "Dining_Table_Pedestal" in obj.name:
            replace(
                obj,
                profile_mesh(
                    [
                        (0.5, -0.5),
                        (0.48, -0.43),
                        (0.29, -0.28),
                        (0.24, 0.12),
                        (0.40, 0.40),
                        (0.48, 0.5),
                    ],
                    0.55,
                    48,
                ),
            )
        if any(
            word in obj.name
            for word in (
                "Coffee_Table",
                "Side_Table",
                "Bedside",
                "Stool_Base",
                "Desk_Stool",
            )
        ):
            if obj.type != "MESH":
                continue
            is_base = "Base" in obj.name
            profile = (
                [
                    (0.48, -0.5),
                    (0.5, -0.44),
                    (0.36, -0.35),
                    (0.29, 0.25),
                    (0.40, 0.43),
                    (0.46, 0.5),
                ]
                if is_base
                else [(0.46, -0.5), (0.50, -0.1), (0.50, 0.20), (0.47, 0.5)]
            )
            replace(obj, profile_mesh(profile, 1, 64))
            if not is_base:
                piping(obj, "Inlaid_Edge", 0.15, "Oak_Joinery", 1, 0.483)


def bedrooms():
    for obj in source_objects():
        if obj.type != "MESH" or "_Detail_" in obj.name:
            continue
        name = obj.name
        if any(
            part in name
            for part in ("_Mattress", "_Duvet", "_Pillow_", "_Folded_Throw")
        ):
            if "_Pillow_" in name:
                obj.data.materials.clear()
                obj.data.materials.append(bpy.data.materials["Fabric_Main"])
            if "_Duvet" in name or "_Folded_Throw" in name:
                folded = "_Folded_Throw" in name
                cloth(obj, folded)
                if folded:
                    obj.location.z = 0.674
                # Remove only our superseded draft welt: a fixed-height ring
                # would float above the new draped edge. It was never exported.
                old = bpy.data.objects.get(name + "_Detail_Sewn_Edge")
                if old and old.get("furniture_revision") == REVISION:
                    bpy.data.objects.remove(old, do_unlink=True)
            else:
                plush(obj, 0.32, wrinkles=True)
                piping(obj, "Sewn_Edge", 0, "Fabric_Oatmeal", 0.32, 0.493)
            if "_Mattress" in name:
                piping(obj, "Upper_Piping", 0.34, "Fabric_Main", 0.32, 0.465)
                piping(obj, "Lower_Piping", -0.34, "Fabric_Main", 0.32, 0.465)
        if "_Upholstered_Headboard" in name:
            replace(
                obj,
                profile_mesh(
                    [(0.46, -0.5), (0.5, -0.4), (0.5, 0.4), (0.46, 0.5)], 0.22, 64
                ),
            )
            centre, size = envelope(obj)
            count = 3 if size.x > 1.4 else 2
            for i in range(1, count):
                detail(
                    obj,
                    f"Panel_Seam_{i}",
                    box_mesh(),
                    "Fabric_Main",
                    (0.002 / size.x, 0.025, 0.86),
                    (i / count - 0.5, -0.501, 0),
                )
        if name.endswith("_Bed_Base"):
            replace(
                obj,
                profile_mesh(
                    [
                        (0.46, -0.5),
                        (0.47, -0.25),
                        (0.5, -0.18),
                        (0.5, 0.46),
                        (0.48, 0.5),
                    ],
                    0.16,
                    64,
                ),
            )
            piping(obj, "Upper_Shadow_Reveal", 0.28, "Fabric_Oatmeal", 0.16, 0.493)
            detail(
                obj,
                "Recessed_Foot",
                box_mesh(),
                "Oak_Joinery",
                (0.83, 0.86, 0.15),
                (0, 0, -0.52),
            )
        if "_Desk_Leg" in name:
            replace(
                obj, profile_mesh([(0.34, -0.5), (0.35, -0.46), (0.5, 0.5)], 0.2, 32)
            )
        if "_Rug" in name:
            piping(obj, "Bound_Edge", 0.1, "Fabric_Main", 0.16, 0.493)


def joinery():
    for obj in source_objects():
        if obj.type != "MESH" or "_Detail_" in obj.name:
            continue
        name = obj.name
        if "_Front_" in name:
            centre, size = envelope(obj)
            axis = 0 if size.x < size.y else 1
            root = name.split("_Front_")[0]
            carcass = bpy.data.objects.get(root + "_Carcass")
            normal = 1 if obj.location[axis] > carcass.location[axis] else -1
            extent = [0.05, 0.05, 0.05]
            offset = [0.0, 0.0, 0.0]
            extent[axis] = 0.016 / size[axis]
            extent[1 - axis] = 0.014 / size[1 - axis]
            extent[2] = min(0.36 / size.z, 0.5)
            offset[axis] = normal * (0.5 + 0.008 / size[axis])
            offset[1 - axis] = -0.30
            detail(
                obj,
                "Satin_Pull",
                profile_mesh(
                    [(0.4, -0.5), (0.5, -0.44), (0.5, 0.44), (0.4, 0.5)], 1, 16
                ),
                "Metal_Champagne",
                extent,
                offset,
            )
        if "Shelf_Upright" in name:
            for i in range(4):
                detail(
                    obj,
                    f"Shelf_Fixing_{i}",
                    box_mesh(),
                    "Metal_Champagne",
                    (0.7, 0.025, 0.006),
                    (0, -0.48, -0.31 + i * 0.254),
                )
        if "Freestanding_Shelf" in name:
            detail(
                obj,
                "Front_Lip",
                box_mesh(),
                "Oak_Joinery",
                (1, 0.025, 1.4),
                (0, 0.47, 0.18),
            )


def fixtures():
    for room in ("Common_Bath", "Ensuite"):
        pan = bpy.data.objects[room + "_WC_Pan"]
        replace(
            pan,
            profile_mesh(
                [
                    (0.23, -0.50),
                    (0.30, -0.44),
                    (0.29, -0.20),
                    (0.43, 0.06),
                    (0.50, 0.20),
                    (0.49, 0.27),
                    (0.39, 0.27),
                    (0.33, 0.10),
                    (0.14, -0.11),
                    (0.035, -0.12),
                ],
                1,
                64,
            ),
        )
        seat = bpy.data.objects[room + "_WC_Seat"]
        replace(
            seat,
            profile_mesh(
                [
                    (0.48, -0.35),
                    (0.5, -0.15),
                    (0.5, 0.15),
                    (0.48, 0.35),
                    (0.35, 0.35),
                    (0.33, 0.15),
                    (0.33, -0.15),
                    (0.35, -0.35),
                ],
                1,
                64,
                True,
            ),
        )
        cistern = bpy.data.objects[room + "_WC_Cistern"]
        replace(
            cistern,
            profile_mesh(
                [(0.43, -0.5), (0.5, -0.42), (0.5, 0.44), (0.47, 0.5)], 0.25, 64
            ),
        )
        piping(cistern, "Lid_Joint", 0.43, "Porcelain", 0.25, 0.495)
        detail(
            cistern,
            "Dual_Flush",
            profile_mesh([(0.5, -0.5), (0.5, 0.5)], 1, 32),
            "Metal_Champagne",
            (0.18, 0.30, 0.008),
            (0, 0, 0.505),
        )
        detail(
            cistern,
            "Seat_Hinge",
            box_mesh(),
            "Metal_Champagne",
            (0.52, 0.12, 0.025),
            (0, 0.38, -0.15),
        )
        lid_vertices, lid_faces = profile_mesh(
            [(0.44, -0.5), (0.5, -0.15), (0.5, 0.15), (0.44, 0.5)], 0.75, 64
        )
        detail(
            cistern,
            "Raised_Lid",
            ([(x, z, y) for x, y, z in lid_vertices], lid_faces),
            "Porcelain",
            (0.92, 0.13, 0.62),
            (0, 0.57, 0.15),
        )
        basin = bpy.data.objects[room + "_Basin"]
        replace(
            basin,
            profile_mesh(
                [
                    (0.26, -0.5),
                    (0.36, -0.45),
                    (0.48, 0.05),
                    (0.5, 0.40),
                    (0.49, 0.50),
                    (0.455, 0.5),
                    (0.445, 0.28),
                    (0.35, -0.26),
                    (0.06, -0.30),
                ],
                0.75,
                64,
            ),
        )
        detail(
            basin,
            "Drain",
            profile_mesh([(0.5, -0.5), (0.5, 0.5)], 1, 32),
            "Metal_Champagne",
            (0.12, 0.10, 0.015),
            (0, 0, -0.27),
        )
        for suffix in ("Mixer_Stem", "Mixer_Spout", "Shower_Stem"):
            obj = bpy.data.objects[room + "_" + suffix]
            # Square-section mixers gain manufactured chamfers without excessive ornament.
            replace(
                obj,
                profile_mesh(
                    [(0.42, -0.5), (0.5, -0.45), (0.5, 0.45), (0.42, 0.5)], 0.5, 24
                ),
            )
        stem = bpy.data.objects[room + "_Mixer_Stem"]
        detail(
            stem,
            "Lever",
            box_mesh(),
            "Metal_Champagne",
            (2.5, 0.5, 0.04),
            (-0.6, 0, 0.50),
        )
        head = bpy.data.objects[room + "_Shower_Head"]
        replace(
            head,
            profile_mesh([(0.46, -0.5), (0.5, -0.25), (0.5, 0.25), (0.46, 0.5)], 1, 64),
        )
        shower_stem = bpy.data.objects[room + "_Shower_Stem"]
        centre, size = envelope(shower_stem)
        start = shower_stem.matrix_world @ (centre + Vector((0, 0, size.z * 0.5)))
        end = head.matrix_world.translation.copy()
        tube_detail(
            shower_stem,
            "Connected_Arm",
            [start, Vector((start.x, start.y, end.z)), end],
            0.012,
            "Metal_Champagne",
        )
        for i in range(16):
            angle = i * math.tau / 16
            detail(
                head,
                f"Spray_Nozzle_{i:02}",
                profile_mesh([(0.5, -0.5), (0.5, 0.5)], 1, 8),
                "Porcelain",
                (0.025, 0.025, 0.2),
                (0.35 * math.cos(angle), 0.35 * math.sin(angle), -0.48),
            )
        mirror = bpy.data.objects[room + "_Mirror"]
        piping(mirror, "Thin_Frame", -0.48, "Metal_Champagne", 0.25, 0.485, axis=0)
        drain = bpy.data.objects[room + "_Drain"]
        for i in range(5):
            detail(
                drain,
                f"Grate_Slot_{i}",
                box_mesh(),
                "Appliance",
                (0.7, 0.025, 0.08),
                (0, (i - 2) * 0.13, 0.51),
            )
    # The sink is now recessed into an actual opening rather than a dark slab.
    rim = bpy.data.objects["Kitchen_Sink_Rim"]
    replace(
        rim,
        profile_mesh(
            [(0.5, -0.5), (0.5, 0.5), (0.44, 0.5), (0.44, -0.5)], 0.30, 64, True
        ),
        "Metal_Brushed_Steel",
    )
    bowl = bpy.data.objects["Kitchen_Sink_Bowl"]
    # Change only the vertical bowl envelope; plan footprint stays fixed.
    centre, extent = envelope(bowl)
    low = list(centre - extent / 2)
    high = list(centre + extent / 2)
    low[2], high[2] = -0.19, -0.006
    bowl["overhaul_original_bounds"] = json.dumps([low, high])
    replace(
        bowl,
        profile_mesh(
            [
                (0.35, -0.5),
                (0.44, -0.45),
                (0.5, 0.5),
                (0.46, 0.5),
                (0.40, -0.35),
                (0.05, -0.37),
            ],
            0.30,
            64,
        ),
        "Metal_Brushed_Steel",
    )
    detail(
        bowl,
        "Basket_Drain",
        profile_mesh([(0.5, -0.5), (0.5, 0.5), (0.38, 0.5), (0.38, -0.5)], 1, 48, True),
        "Metal_Brushed_Steel",
        (0.13, 0.19, 0.02),
        (0, 0, -0.355),
    )
    detail(
        bowl,
        "Drain_Outlet",
        profile_mesh([(0.5, -0.5), (0.5, 0.5)], 1, 32),
        "Appliance",
        (0.095, 0.14, 0.008),
        (0, 0, -0.365),
    )
    detail(
        bowl,
        "Overflow",
        box_mesh(),
        "Appliance",
        (0.11, 0.008, 0.025),
        (0, -0.435, 0.25),
    )
    counter = bpy.data.objects["Kitchen_Back_Counter"]
    centre, extent = envelope(counter)
    # Four continuous loops make the through-opening manifold and editable.
    vertices = []
    for inner, z in ((False, -0.5), (False, 0.5), (True, 0.5), (True, -0.5)):
        for x, y, _ in loop(0.5, z, 0.20 if not inner else 0.30, 64):
            vertices.append(
                (
                    x if not inner else x * 0.56 / extent.x - 0.01 / extent.x,
                    y if not inner else y * 0.37 / extent.y + 0.04 / extent.y,
                    z,
                )
            )
    faces = [
        (
            r * 64 + i,
            r * 64 + (i + 1) % 64,
            ((r + 1) % 4) * 64 + (i + 1) % 64,
            ((r + 1) % 4) * 64 + i,
        )
        for r in range(4)
        for i in range(64)
    ]
    replace(counter, (vertices, faces))
    # Cabinet carcass top was solid; a matching opening keeps the basin visible.
    carcass = bpy.data.objects["Kitchen_Back_Base_Carcass"]
    replace(carcass, (vertices, faces))
    tap = bpy.data.objects["Kitchen_Tap_Stem"]
    replace(
        tap, profile_mesh([(0.42, -0.5), (0.5, -0.42), (0.5, 0.42), (0.42, 0.5)], 1, 32)
    )
    detail(
        tap,
        "Mixer_Handle",
        box_mesh(),
        "Metal_Champagne",
        (2.4, 0.6, 0.16),
        (0.6, 0, -0.27),
    )
    spout = bpy.data.objects["Kitchen_Tap_Spout"]
    replace(
        spout, profile_mesh([(0.4, -0.5), (0.5, -0.4), (0.5, 0.4), (0.4, 0.5)], 0.5, 32)
    )
    for obj in list(bpy.data.objects):
        if obj.name.startswith("Kitchen_Hob_Ring") and "_Detail_" not in obj.name:
            replace(
                obj,
                profile_mesh(
                    [(0.5, -0.5), (0.5, 0.5), (0.48, 0.5), (0.48, -0.5)], 1, 64, True
                ),
            )


def appliances():
    fridge = bpy.data.objects["Kitchen_Fridge"]
    detail(
        fridge,
        "Door_Division",
        box_mesh(),
        "Appliance",
        (0.93, 0.008, 0.003),
        (0, -0.502, -0.13),
    )
    detail(
        fridge,
        "Lower_Vent",
        box_mesh(),
        "Appliance",
        (0.75, 0.008, 0.025),
        (0, -0.50, -0.45),
    )
    washer = bpy.data.objects["Service_Yard_Washer"]
    detail(
        washer,
        "Control_Panel",
        box_mesh(),
        "Cabinet_Front",
        (0.88, 0.012, 0.13),
        (0, 0.50, 0.33),
    )
    detail(
        washer,
        "Display",
        box_mesh(),
        "Appliance",
        (0.22, 0.014, 0.055),
        (0.20, 0.51, 0.33),
    )
    detail(
        washer,
        "Detergent_Drawer",
        box_mesh(),
        "Cabinet_Front",
        (0.32, 0.02, 0.09),
        (-0.27, 0.51, 0.33),
    )
    knob = detail(
        washer,
        "Program_Dial",
        profile_mesh([(0.5, -0.5), (0.5, 0.5)], 1, 32),
        "Metal_Champagne",
        (0.085, 0.085, 0.025),
        (0, 0, 0),
    )
    # Reorient the dial's local disc to the north-facing appliance front.
    centre, extent = envelope(washer)
    for v in knob.data.vertices:
        p = v.co - centre
        v.co = centre + Vector((p.x, extent.y * 0.525 + p.z, extent.z * 0.33 + p.y))
    knob.data.flip_normals()
    door = bpy.data.objects["Service_Yard_Washer_Door"]
    detail(
        door,
        "Machined_Rim",
        profile_mesh([(0.5, -0.5), (0.5, 0.5), (0.44, 0.5), (0.44, -0.5)], 1, 64, True),
        "Metal_Brushed_Steel",
        (0.98, 0.98, 1.2),
    )
    detail(
        door,
        "Rubber_Seal",
        profile_mesh(
            [(0.44, -0.5), (0.44, 0.5), (0.40, 0.5), (0.40, -0.5)], 1, 64, True
        ),
        "Appliance",
        (0.98, 0.98, 1.4),
    )
    tv = bpy.data.objects["Living_TV"]
    piping(tv, "Bezel", -0.49, "Appliance", 0.12, 0.489, axis=0)
    condenser = bpy.data.objects["AC_Ledge_Condenser_Indicative"]
    for i in range(12):
        detail(
            condenser,
            f"Vent_{i:02}",
            box_mesh(),
            "Appliance",
            (0.73, 0.006, 0.012),
            (0, 0.502, -0.30 + i * 0.05),
        )


def decor():
    for obj in source_objects():
        if obj.name.endswith("_Plant_Pot"):
            replace(
                obj,
                profile_mesh(
                    [
                        (0.35, -0.5),
                        (0.41, -0.46),
                        (0.48, 0.35),
                        (0.50, 0.45),
                        (0.48, 0.50),
                        (0.44, 0.50),
                        (0.44, 0.39),
                        (0.37, -0.39),
                    ],
                    1,
                    64,
                ),
            )
        if obj.name.startswith("Living_Table_Book"):
            detail(
                obj,
                "Top_Cover",
                box_mesh(),
                "Fabric_Oatmeal",
                (1.01, 1.01, 0.08),
                (0, 0, 0.46),
            )
            detail(
                obj,
                "Lower_Cover",
                box_mesh(),
                "Fabric_Oatmeal",
                (1.01, 1.01, 0.08),
                (0, 0, -0.46),
            )
            for i in range(4):
                detail(
                    obj,
                    f"Page_Edge_{i}",
                    box_mesh(),
                    "Countertop",
                    (0.95, 0.008, 0.007),
                    (0, 0.495, -0.25 + i * 0.16),
                )


def apply(family=None):
    bpy.context.view_layer.update()
    ensure_materials()
    families = {
        "seating": seating,
        "bedrooms": bedrooms,
        "joinery": joinery,
        "fixtures": fixtures,
        "appliances": appliances,
        "decor": decor,
    }
    for name, builder in families.items():
        if family is None or family == name:
            builder()
    bpy.context.view_layer.update()
    # Preserve existing physics envelopes. Added trims are decorative, not tiny
    # obstacles; replacement meshes stay inside their approved plan footprints.
    for obj in bpy.data.objects:
        if obj.get("furniture_revision") == REVISION and not obj.get(
            "oakville_source_id"
        ):
            obj["oakville_source_id"] = str(
                uuid.uuid5(uuid.NAMESPACE_URL, "oak-ville/" + obj.name)
            )
    bpy.context.scene["furniture_revision"] = REVISION
    return {
        "revision": REVISION,
        "detailed_objects": sum(
            o.get("furniture_revision") == REVISION for o in bpy.data.objects
        ),
    }


if __name__ == "__main__":
    print(apply())
