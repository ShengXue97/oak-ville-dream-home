"""Editable attached door hardware and lightweight botanical detail.

All coordinates are metres. Plant locations are proposed decor positions.
Geometry is deterministic, with no external asset or texture dependency.
"""

import math
import random

import bmesh
import bpy
from mathutils import Vector


def mesh_object(name, vertices, faces, collection, material):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    bm = bmesh.new()
    bm.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(bm, faces=list(bm.faces))
    bm.to_mesh(mesh)
    bm.free()
    obj = bpy.data.objects.new(name, mesh)
    bpy.data.collections[collection].objects.link(obj)
    obj.data.materials.append(bpy.data.materials[material])
    obj["collision_source"] = False
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    return obj


def tube(name, points, radii, collection, material, parent=None, sides=12):
    """Create a capped tube with smoothly varying radius along a polyline."""
    points = [Vector(point) for point in points]
    vertices = []
    for index, point in enumerate(points):
        tangent = points[min(index + 1, len(points) - 1)] - points[max(0, index - 1)]
        tangent.normalize()
        guide = Vector((0, 0, 1)) if abs(tangent.z) < 0.95 else Vector((1, 0, 0))
        side = tangent.cross(guide).normalized()
        up = tangent.cross(side).normalized()
        for step in range(sides):
            angle = 2 * math.pi * step / sides
            vertices.append(
                point + radii[index] * (side * math.cos(angle) + up * math.sin(angle))
            )
    faces = [tuple(reversed(range(sides)))]
    for ring in range(len(points) - 1):
        for step in range(sides):
            a = ring * sides + step
            b = ring * sides + (step + 1) % sides
            faces.append((a, b, b + sides, a + sides))
    faces.append(tuple(range((len(points) - 1) * sides, len(points) * sides)))
    obj = mesh_object(name, vertices, faces, collection, material)
    obj.parent = parent
    return obj


def build_door_hardware(room, axis, width, pivot):
    """Attach two rose/spindle/lever sets to the 44 mm door leaf."""
    along = Vector((1, 0, 0)) if axis == "h" else Vector((0, -1, 0))
    normal = Vector((0, 1, 0)) if axis == "h" else Vector((1, 0, 0))
    centre = along * (width - 0.075) + Vector((0, 0, 1.02))
    for sign, side in ((1, "Front"), (-1, "Back")):
        outward = normal * sign
        for part, points, radius in (
            ("Rose", [centre + outward * 0.021, centre + outward * 0.029], 0.025),
            ("Spindle", [centre + outward * 0.027, centre + outward * 0.066], 0.010),
            (
                "Lever",
                [centre + outward * 0.063, centre - along * 0.10 + outward * 0.063],
                0.011,
            ),
        ):
            obj = tube(
                f"{room}_Door_Handle_{side}_{part}",
                points,
                [radius, radius],
                "Doors_Windows",
                "Metal_Champagne",
                pivot,
                24,
            )
            obj["hardware_part"] = part
            obj["attached_to_leaf"] = room + "_Door_Leaf"
            bevel = obj.modifiers.new("Soft hardware edges", "BEVEL")
            bevel.width = 0.0015
            bevel.segments = 2


def plant_materials():
    roles = {
        "Plant_Leaf_Deep": (0.055, 0.105, 0.025),
        "Plant_Leaf_Mid": (0.090, 0.155, 0.040),
        "Plant_Leaf_Young": (0.145, 0.210, 0.060),
        "Plant_Bark": (0.100, 0.068, 0.032),
        "Plant_Soil": (0.032, 0.020, 0.012),
    }
    for name, colour in roles.items():
        if name in bpy.data.materials:
            continue
        material = bpy.data.materials.new(name)
        material.diffuse_color = (*colour, 1)
        material.use_nodes = True
        nodes = material.node_tree.nodes
        links = material.node_tree.links
        shader = nodes.get("Principled BSDF")
        shader.inputs["Base Color"].default_value = (*colour, 1)
        shader.inputs["Roughness"].default_value = 0.43 if "Leaf" in name else 0.85
        noise = nodes.new("ShaderNodeTexNoise")
        noise.inputs["Scale"].default_value = 85
        bump = nodes.new("ShaderNodeBump")
        bump.inputs["Strength"].default_value = 0.12
        bump.inputs["Distance"].default_value = 0.0004
        links.new(noise.outputs["Fac"], bump.inputs["Height"])
        links.new(bump.outputs["Normal"], shader.inputs["Normal"])


def leaf(name, base, angle, length, width, rise, material):
    """Pointed, cambered leaf with a closed sub-millimetre cross-section."""
    base = Vector(base)
    forward = Vector((math.cos(angle), math.sin(angle), 0))
    side = Vector((-math.sin(angle), math.cos(angle), 0))
    vertices = [base]
    rings, sides = 11, 8
    midrib = [base]
    for ring in range(1, rings):
        t = ring / rings
        centre = base + forward * (length * t)
        centre.z += rise * t + 0.024 * math.sin(math.pi * t) - 0.032 * t * t
        midrib.append(centre.copy())
        half_width = width * 0.5 * math.sin(math.pi * t) ** 0.8
        for step in range(sides):
            phase = 2 * math.pi * step / sides
            offset = side * (half_width * math.cos(phase))
            offset.z = -0.008 * abs(math.cos(phase)) * math.sin(
                math.pi * t
            ) + 0.0007 * math.sin(phase)
            vertices.append(centre + offset)
    tip = base + forward * length + Vector((0, 0, rise - 0.032))
    tip_index = len(vertices)
    vertices.append(tip)
    midrib.append(tip)
    faces = [(0, 1 + step, 1 + (step + 1) % sides) for step in range(sides)]
    for ring in range(rings - 2):
        for step in range(sides):
            a = 1 + ring * sides + step
            b = 1 + ring * sides + (step + 1) % sides
            faces.append((a, b, b + sides, a + sides))
    last = 1 + (rings - 2) * sides
    faces.extend(
        (last + step, tip_index, last + (step + 1) % sides) for step in range(sides)
    )
    obj = mesh_object(name, vertices, faces, "Decor", material)
    obj["detail_type"] = "Thin curved leaf"
    vein_points = [point + Vector((0, 0, 0.0008)) for point in midrib[:-1]]
    tube(
        name + "_Midrib",
        vein_points,
        [0.001 * (1 - i / len(vein_points)) + 0.00015 for i in range(len(vein_points))],
        "Decor",
        "Plant_Leaf_Young",
        sides=6,
    )


def build_plants(namespace):
    plant_materials()
    for room, x, plan_y in (("Living", 2.77, 0.64), ("Dining", 5.88, 6.05)):
        pot = bpy.data.objects.get(room + "_Plant_Pot")
        if pot is None:
            pot = namespace["round_object"](
                room + "_Plant_Pot", x, plan_y, 0.21, 0.16, 0.39, "Countertop", "Decor"
            )
        pot.location = (x, -plan_y, 0.21)
        proxy = bpy.data.objects.get("COL_" + pot.name)
        if proxy:
            proxy.location = pot.location
        origin = Vector((x, -plan_y, 0))
        tube(
            room + "_Plant_Soil",
            [origin + Vector((0, 0, 0.403)), origin + Vector((0, 0, 0.409))],
            [0.142, 0.142],
            "Decor",
            "Plant_Soil",
            sides=48,
        )
        trunk = [
            origin
            + Vector(
                (0.018 * math.sin(i * 0.5), 0.012 * math.sin(i * 0.8), 0.40 + i * 0.105)
            )
            for i in range(10)
        ]
        tube(
            room + "_Plant_Trunk",
            trunk,
            [0.011 - i * 0.0008 for i in range(10)],
            "Decor",
            "Plant_Bark",
        )
        rng = random.Random(72 if room == "Dining" else 41)
        for index in range(22):
            level = 2 + index // 3
            angle = index * 2.39996 + rng.uniform(-0.18, 0.18)
            base = trunk[level]
            reach = rng.uniform(0.035, 0.095)
            end = base + Vector(
                (
                    reach * math.cos(angle),
                    reach * math.sin(angle),
                    rng.uniform(0.018, 0.045),
                )
            )
            tube(
                f"{room}_Plant_Branch_{index:02d}",
                [base, end],
                [0.0025, 0.0012],
                "Decor",
                "Plant_Bark",
                sides=8,
            )
            material = ("Plant_Leaf_Deep", "Plant_Leaf_Mid", "Plant_Leaf_Young")[
                index % 3
            ]
            leaf(
                f"{room}_Plant_Leaf_{index:02d}",
                end,
                angle,
                rng.uniform(0.14, 0.22),
                rng.uniform(0.055, 0.085),
                rng.uniform(-0.025, 0.065),
                material,
            )


def apply_live_fixes(namespace):
    """Replace only the original generated handles and plant foliage."""
    for obj in list(bpy.context.scene.objects):
        old_handle = obj.name.endswith("_Door_Handle") or bool(obj.get("hardware_part"))
        old_foliage = any(
            obj.name.startswith(room + suffix)
            for room in ("Dining", "Living")
            for suffix in ("_Leaf", "_Plant_")
        ) and not obj.name.endswith("_Plant_Pot")
        if old_handle or old_foliage:
            bpy.data.objects.remove(obj, do_unlink=True)
    for room, axis, fixed, start, end, thickness, angle in namespace["DOORS"]:
        build_door_hardware(
            room, axis, end - start - 0.065, bpy.data.objects[room + "_Door_Hinge"]
        )
    build_plants(namespace)
    import runpy

    runpy.run_path(str(namespace["ROOT"] / "scripts/door_plan.py"))["apply"]()
    bpy.context.view_layer.update()
