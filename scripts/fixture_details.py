"""Editable bowl geometry and mixer taps for the proposed vanity fixtures."""

import bpy
import bmesh
import math


def basin_mesh(name):
    """Closed, outward-facing oval bowl with a genuinely recessed interior."""
    profile = [
        (0.04, 0.00),
        (0.72, 0.00),
        (1.00, 0.055),
        (1.00, 0.095),
        (0.88, 0.095),
        (0.66, 0.035),
        (0.04, 0.035),
    ]
    segments = 48
    vertices = []
    for radius, height in profile:
        for index in range(segments):
            angle = 2 * math.pi * index / segments
            vertices.append(
                (
                    0.185 * radius * math.cos(angle),
                    0.230 * radius * math.sin(angle),
                    height,
                )
            )
    faces = []
    for ring in range(len(profile) - 1):
        for index in range(segments):
            next_index = (index + 1) % segments
            faces.append(
                (
                    ring * segments + index,
                    ring * segments + next_index,
                    (ring + 1) * segments + next_index,
                    (ring + 1) * segments + index,
                )
            )
    for ring, height in [(0, 0.00), (len(profile) - 1, 0.035)]:
        centre = len(vertices)
        vertices.append((0, 0, height))
        for index in range(segments):
            faces.append(
                (
                    centre,
                    ring * segments + index,
                    ring * segments + (index + 1) % segments,
                )
            )
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(vertices, [], faces)
    editable = bmesh.new()
    editable.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(editable, faces=list(editable.faces))
    editable.to_mesh(mesh)
    editable.free()
    for polygon in mesh.polygons:
        polygon.use_smooth = True
    return mesh


def refine_basins(namespace):
    """Replace only the named proposed basin meshes; do not touch architecture."""
    for room, vanity_x in [("Common_Bath", 8.28), ("Ensuite", 10.73)]:
        obj = bpy.data.objects[room + "_Basin"]
        obj.data = basin_mesh(room + "_Recessed_Basin")
        obj.data.materials.append(bpy.data.materials["Porcelain"])
        obj.location = (vanity_x - 0.02, -4.93, 0.895)
        obj["fixture_detail"] = (
            "Proposed hollow vessel basin; verify selected product dimensions"
        )
        for suffix, x, plan_y, z, width, depth, height in [
            ("Mixer_Stem", vanity_x + 0.17, 4.93, 1.04, 0.026, 0.026, 0.26),
            ("Mixer_Spout", vanity_x + 0.10, 4.93, 1.16, 0.16, 0.027, 0.027),
        ]:
            if room + "_" + suffix not in bpy.data.objects:
                namespace["cub"](
                    room + "_" + suffix,
                    x,
                    plan_y,
                    z,
                    width,
                    depth,
                    height,
                    "Fixed_Joinery",
                    "Metal_Champagne",
                    0.007,
                )
