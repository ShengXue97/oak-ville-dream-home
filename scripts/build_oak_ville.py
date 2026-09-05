"""Oak Ville: staged, additive live construction. Run with Blender Python.
CLI: blender --background --python scripts/build_oak_ville.py -- --stage 5
Live: runpy.run_path(path)['build'](stage). Never reload an existing scene.
Coordinates in design data: x right, v down on plan, z up. All metres.
"""

import bpy, math, json, sys
from pathlib import Path
from mathutils import Vector, Quaternion

ROOT = Path(__file__).resolve().parents[1]
for folder in (
    "docs/validation",
    "docs/schedules",
    "docs/drawings",
    "assets/styles",
    ".cache",
):
    (ROOT / folder).mkdir(parents=True, exist_ok=True)
BUILD_OUTPUT = ROOT / "oak-ville.blend"
H = 2.60
COLS = {}
ROOMS = {
    "Living": (0, 3.375, 0, 4.45),
    "Bedroom_3": (3.375, 6.375, 0, 3.35),
    "Bedroom_2": (6.375, 9.375, 0, 3.35),
    "Main_Bedroom": (9.375, 12.675, 0, 4.45),
    "Bedroom_Corridor": (3.375, 9.375, 3.35, 4.45),
    "Shelter": (0, 1.75, 4.45, 7.25),
    "Dining": (1.75, 6.375, 4.45, 6.4),
    "Entry": (1.75, 3.5, 6.4, 7.25),
    "Kitchen": (3.5, 5.775, 6.4, 8.95),
    "Service_Yard": (5.775, 7.15, 6.4, 8.95),
    "Utility_Strip": (7.15, 7.75, 6.4, 8.95),
    "Common_Bath": (6.375, 8.625, 4.45, 6.4),
    "Ensuite": (8.625, 11.1, 4.45, 6.4),
    "AC_Ledge": (8.625, 11.1, 6.4, 7.65),
}
CHAINS = {
    "upper": [3375, 3000, 3000, 3300],
    "left": [4450, 2800, 1700],
    "right": [4450, 1950, 1250],
    "lower": [1750, 1750, 2275, 1375, 3950],
}
DOORS = [
    ("Entry", "h", 7.25, 2.15, 3.25, 0.20, 90),
    ("Shelter", "v", 1.75, 5.20, 6.05, 0.25, -90),
    ("Bedroom_3", "h", 3.35, 5.40, 6.30, 0.10, 90),
    ("Bedroom_2", "h", 3.35, 6.45, 7.35, 0.10, 86),
    ("Main_Bedroom", "v", 9.375, 3.45, 4.35, 0.10, 90),
    ("Common_Bath", "h", 4.45, 6.75, 7.55, 0.10, -90),
    ("Ensuite", "h", 4.45, 9.55, 10.35, 0.15, -90),
    ("Service_Yard", "v", 5.775, 7.20, 8.05, 0.10, -90),
]


def collection(name, parent=None):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        (parent or bpy.context.scene.collection).children.link(c)
    COLS[name] = c
    return c


def material(name, color, rough=0.65):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.diffuse_color = (*color, 1)
    m.use_nodes = True
    p = m.node_tree.nodes.get("Principled BSDF")
    p.inputs["Base Color"].default_value = (*color, 1)
    p.inputs["Roughness"].default_value = rough
    return m


def box(name, bounds, coll="Architecture", mat="Wall_Paint", bevel=0, solid=True):
    x0, x1, v0, v1, z0, z1 = bounds
    verts = [(x, -v, z) for z in (z0, z1) for v in (v0, v1) for x in (x0, x1)]
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(
        verts,
        [],
        [
            (1, 3, 2, 0),
            (6, 7, 5, 4),
            (4, 5, 1, 0),
            (3, 7, 6, 2),
            (2, 6, 4, 0),
            (5, 7, 3, 1),
        ],
    )
    mesh.update()
    o = bpy.data.objects.new(name, mesh)
    COLS[coll].objects.link(o)
    # Keep geometry local to a sensible centre origin.
    center = Vector(((x0 + x1) / 2, -(v0 + v1) / 2, (z0 + z1) / 2))
    for vert in mesh.vertices:
        vert.co -= center
    o.location = center
    if mat:
        o.data.materials.append(bpy.data.materials[mat])
    if bevel:
        mod = o.modifiers.new("Editable softened edges", "BEVEL")
        mod.width = bevel
        mod.segments = 3
        o.modifiers.new("Weighted corner normals", "WEIGHTED_NORMAL")
    o["collision_source"] = solid
    o["design_bounds"] = list(bounds)
    return o


def cub(
    name,
    x,
    v,
    z,
    sx,
    sy,
    sz,
    coll="Furniture",
    mat="Fabric_Main",
    bevel=0.025,
    solid=True,
):
    return box(
        name,
        (x - sx / 2, x + sx / 2, v - sy / 2, v + sy / 2, z - sz / 2, z + sz / 2),
        coll,
        mat,
        bevel,
        solid,
    )


def wall(name, axis, fixed, start, end, t=0.10, openings=()):
    # Openings: (start,end,sill,head). Segments leave genuine apertures.
    cuts = sorted(openings)
    pos = start
    for i, (a, b, sill, head) in enumerate(cuts + [(end, end, 0, H)]):

        def segment(s, e, z0, z1, suffix):
            if e - s < 0.001 or z1 - z0 < 0.001:
                return
            bounds = (
                (s, e, fixed - t / 2, fixed + t / 2, z0, z1)
                if axis == "h"
                else (fixed - t / 2, fixed + t / 2, s, e, z0, z1)
            )
            o = box(name + "_" + suffix, bounds)
            o["wall_thickness_estimate_m"] = t

        segment(pos, a, 0, H, f"{i}_pier")
        if b > a:
            segment(a, b, 0, sill, f"{i}_sill")
            segment(a, b, head, H, f"{i}_header")
        pos = b


def camera(name, xyz, target, coll="Walkthrough", fov=65, ortho=None):
    d = bpy.data.cameras.new(name)
    o = bpy.data.objects.new(name, d)
    COLS[coll].objects.link(o)
    o.location = (xyz[0], -xyz[1], xyz[2])
    dest = Vector((target[0], -target[1], target[2]))
    o.rotation_euler = (dest - o.location).to_track_quat("-Z", "Y").to_euler()
    d.sensor_fit = "HORIZONTAL"
    d.angle = math.radians(fov)
    d.clip_start = 0.05
    d.clip_end = 200
    if ortho:
        d.type = "ORTHO"
        d.ortho_scale = ortho
    return o


def label(name, text, x, v, z, size=0.18):
    d = bpy.data.curves.new(name, "FONT")
    d.body = text
    d.size = size
    d.align_x = "CENTER"
    o = bpy.data.objects.new(name, d)
    COLS["Plan_Annotations"].objects.link(o)
    o.location = (x, -v, z)
    d.materials.append(bpy.data.materials["Annotation"])
    return o


def refresh(stage):
    bpy.context.view_layer.update()
    for win in bpy.context.window_manager.windows:
        for area in win.screen.areas:
            if area.type == "VIEW_3D":
                s = area.spaces.active
                s.clip_end = 200
                s.overlay.show_extras = False
                s.shading.type = "SOLID" if stage < 4 else "MATERIAL"
                s.shading.color_type = "MATERIAL"
                if stage <= 2:
                    s.region_3d.view_location = (6.3, -4.4, 0)
                    s.region_3d.view_distance = 16
                    s.region_3d.view_rotation = Quaternion((1, 0, 0, 0))
                    s.region_3d.view_perspective = "ORTHO"
                area.tag_redraw()


def save(stage):
    s = bpy.context.scene
    s["milestone"] = stage
    s["ceiling_height_assumed_m"] = H
    s["project_version"] = (
        (ROOT / "VERSION").read_text().strip()
        if stage == 5
        else ["0.0.0", "0.1.0", "0.2.0", "0.3.0", "0.4.0"][stage]
    )
    bpy.ops.file.pack_all()
    if not bpy.data.filepath:
        bpy.ops.wm.save_as_mainfile(
            filepath=str(BUILD_OUTPUT), check_existing=False, compress=True
        )
    bpy.ops.file.make_paths_relative()
    refresh(stage)
    bpy.ops.wm.save_as_mainfile(
        filepath=str(BUILD_OUTPUT), check_existing=False, compress=True
    )


def architecture():
    old = bpy.context.scene
    s = bpy.data.scenes.new("Oak_Ville")
    bpy.context.window.scene = s
    s["preserved_startup_scene"] = old.name
    s.unit_settings.system = "METRIC"
    s.unit_settings.scale_length = 1
    s.unit_settings.length_unit = "METERS"
    style = collection("MINIMALIST_CREAM")
    for n in [
        "Architecture",
        "Doors_Windows",
        "Collision",
        "Walkthrough",
        "Reference_Plans",
        "Plan_Annotations",
    ]:
        collection(n)
    for n in ["Fixed_Joinery", "Furniture", "Lighting", "Decor"]:
        collection(n, style)
    collection("Ceilings", COLS["Architecture"])
    collection("Beams_Soffits", COLS["Architecture"])
    colors = {
        "Wall_Paint": (0.80, 0.75, 0.65),
        "Floor_Main": (0.58, 0.40, 0.23),
        "Wet_Tile": (0.72, 0.65, 0.52),
        "Cabinet_Front": (0.77, 0.70, 0.58),
        "Countertop": (0.82, 0.76, 0.66),
        "Fabric_Main": (0.78, 0.70, 0.58),
        "Oak_Joinery": (0.58, 0.40, 0.23),
        "Fabric_Oatmeal": (0.55, 0.44, 0.32),
        "Porcelain": (0.88, 0.84, 0.74),
        "Metal_Champagne": (0.5, 0.4, 0.25),
        "Appliance": (0.12, 0.13, 0.13),
        "Glass": (0.66, 0.79, 0.80),
        "Foliage": (0.18, 0.27, 0.10),
        "Annotation": (0.07, 0.12, 0.14),
    }
    for n, c in colors.items():
        material(n, c)
    for room, (x0, x1, v0, v1) in ROOMS.items():
        wet = room in [
            "Kitchen",
            "Service_Yard",
            "Utility_Strip",
            "Common_Bath",
            "Ensuite",
            "AC_Ledge",
        ]
        o = box(
            room + "_Floor",
            (x0, x1, v0, v1, -0.16, 0),
            mat="Wet_Tile" if wet else "Floor_Main",
        )
        o["reference_area_includes_walls"] = True
        if room != "AC_Ledge":
            box(room + "_Ceiling", (x0, x1, v0, v1, H, H + 0.14), "Ceilings")
        label(
            room + "_Label", room.replace("_", " "), (x0 + x1) / 2, (v0 + v1) / 2, 0.02
        )
    # Structural perimeter, thick shelter, partitions. Positions tied to chain datums.
    for n, a, f, st, en, t, op in [
        (
            "Facade_North",
            "h",
            0,
            0,
            12.675,
            0.20,
            [
                (0.4, 3.15, 0.85, 2.35),
                (3.60, 5.85, 0.85, 2.35),
                (6.70, 9.12, 0.85, 2.35),
                (9.62, 12.35, 0.85, 2.35),
            ],
        ),
        ("Living_West", "v", 0, 0, 4.45, 0.20, []),
        ("Main_East", "v", 12.675, 0, 4.45, 0.25, [(1.4, 3.1, 0.85, 2.35)]),
        ("Main_South", "h", 4.45, 9.375, 12.675, 0.15, [(9.55, 10.35, 0, 2.15)]),
        ("Bedroom3_West", "v", 3.375, 0, 3.35, 0.10, []),
        ("Bedroom3_East", "v", 6.375, 0, 3.35, 0.10, []),
        ("Bedroom2_East", "v", 9.375, 0, 4.45, 0.10, [(3.45, 4.35, 0, 2.15)]),
        ("Bedroom3_South", "h", 3.35, 3.375, 6.375, 0.10, [(5.40, 6.30, 0, 2.15)]),
        ("Bedroom2_South", "h", 3.35, 6.375, 9.375, 0.10, [(6.45, 7.35, 0, 2.15)]),
        ("Shelter_North", "h", 4.45, 0, 1.75, 0.25, []),
        ("Shelter_West", "v", 0, 4.45, 7.25, 0.25, []),
        ("Shelter_East", "v", 1.75, 4.45, 7.25, 0.25, [(5.20, 6.05, 0, 2.15)]),
        ("Shelter_South", "h", 7.25, 0, 1.75, 0.25, []),
        ("Entry_South", "h", 7.25, 1.75, 3.5, 0.20, [(2.15, 3.25, 0, 2.15)]),
        ("Kitchen_West", "v", 3.5, 6.4, 8.95, 0.20, []),
        ("Kitchen_Yard_South", "h", 8.95, 3.5, 7.75, 0.25, []),
        ("Yard_East", "v", 7.75, 6.4, 8.95, 0.15, [(6.65, 8.65, 1.1, 2.40)]),
        ("Yard_Utility", "v", 7.15, 6.4, 8.95, 0.08, [(6.65, 8.65, 0.9, 2.40)]),
        ("Kitchen_Yard", "v", 5.775, 6.4, 8.95, 0.10, [(7.20, 8.05, 0, 2.15)]),
        ("Bath_Common_West", "v", 6.375, 4.45, 6.4, 0.30, []),
        ("Baths_North", "h", 4.45, 6.375, 9.375, 0.10, [(6.75, 7.55, 0, 2.15)]),
        ("Baths_Divider", "v", 8.625, 4.45, 6.4, 0.10, []),
        ("Ensuite_East", "v", 11.1, 4.45, 6.4, 0.25, []),
        (
            "Baths_South",
            "h",
            6.4,
            6.375,
            11.1,
            0.12,
            [(6.85, 7.55, 1.8, 2.35), (9.5, 10.3, 1.8, 2.35)],
        ),
        ("Ledge_West", "v", 8.625, 6.4, 7.65, 0.10, []),
        ("Ledge_East", "v", 11.1, 6.4, 7.65, 0.10, []),
    ]:
        wall(n, a, f, st, en, t, op)
    # Ledge is exterior, with provisional parapet rather than an interior room.
    box("Ledge_South_Parapet", (8.575, 11.15, 7.60, 7.70, 0, 1.1))
    box("Yard_North_Closure", (5.775, 6.375, 6.34, 6.46, 0, H))
    box(
        "Kitchen_Open_Portal_Soffit",
        (3.60, 6.225, 6.32, 6.48, 2.35, 2.60),
        "Beams_Soffits",
    )
    for x in (0, 6.375, 12.675):
        cub(
            "Facade_Column_" + str(x),
            x,
            0.15,
            1.3,
            0.30,
            0.55,
            2.6,
            "Architecture",
            "Wall_Paint",
            0,
        )
    # Reference station empties make written chains independently measurable.
    for chain, values in CHAINS.items():
        acc = 0
        for i in range(len(values) + 1):
            x, v = (
                (acc, -0.75)
                if chain == "upper"
                else (
                    (-0.65, acc)
                    if chain == "left"
                    else ((13.25, acc) if chain == "right" else (acc, 9.60))
                )
            )
            o = bpy.data.objects.new("DIM_" + chain + "_" + str(i), None)
            COLS["Reference_Plans"].objects.link(o)
            o.location = (x, -v, 0)
            o.empty_display_size = 0.07
            if i < len(values):
                acc += values[i] / 1000
    for filename in [
        "OAK_VILLE_DIMENSIONED_PLAN.jpg",
        "OAK_VILLE_PRIMARY_FLOOR_PLAN.png",
        "USER_PRIMARY_STYLE_REFERENCE.png",
    ]:
        img = bpy.data.images.load(
            str(ROOT / "references/original" / filename), check_existing=True
        )
        img.pack()
        img.filepath = str(ROOT / "references/original" / filename)
        o = bpy.data.objects.new("REF_" + filename, None)
        COLS["Reference_Plans"].objects.link(o)
        o.empty_display_type = "IMAGE"
        o.data = img
        o.hide_render = True
        o.hide_set(True)
    top = camera("PLAN_Orthographic", (6.3, 4.4, 20), (6.3, 4.4, 0), ortho=16.0)
    s.camera = top
    cut = s.view_layers[0]
    cut.name = "Inspection_Cutaway"
    cut.layer_collection.children["Architecture"].children["Ceilings"].exclude = True
    walk = s.view_layers.new("Enclosed_Walkthrough")
    walk.layer_collection.children["Plan_Annotations"].exclude = True
    for layer in [cut, walk]:
        layer.layer_collection.children["Reference_Plans"].exclude = True
    bpy.context.window.view_layer = cut
    s.render.engine = "CYCLES"
    s.cycles.samples = 24
    s.cycles.use_denoising = True
    s.render.resolution_x = 1280
    s.render.resolution_y = 900
    s.render.resolution_percentage = 100
    s.world = bpy.data.worlds.new("Oak_Ville_Daylight")
    s.world.use_nodes = True
    s.world.node_tree.nodes["Background"].inputs[0].default_value = (0.8, 0.86, 1, 1)
    s.world.node_tree.nodes["Background"].inputs[1].default_value = 0.4
    validate_dimensions()


def validate_dimensions():
    out = {}
    for chain, vals in CHAINS.items():
        rows = []
        for i, mm in enumerate(vals):
            a = bpy.data.objects["DIM_" + chain + "_" + str(i)].location
            b = bpy.data.objects["DIM_" + chain + "_" + str(i + 1)].location
            actual = (b - a).length * 1000
            rows.append(
                {
                    "plan_mm": mm,
                    "model_mm": round(actual, 3),
                    "error_mm": round(actual - mm, 4),
                }
            )
        out[chain] = {
            "segments": rows,
            "total_mm": sum(vals),
            "pass": all(abs(r["error_mm"]) < 0.01 for r in rows),
        }
    out["area_convention"] = (
        "Non-overlapping reference floor patches, inclusive of walls; not clear/net floor area."
    )
    out["reference_areas_m2"] = {
        r: round((b - a) * (d - c), 4) for r, (a, b, c, d) in ROOMS.items()
    }
    out["internal_reference_m2"] = round(
        sum((b - a) * (d - c) for r, (a, b, c, d) in ROOMS.items() if r != "AC_Ledge"),
        4,
    )
    out["includes_ledge_m2"] = round(sum(out["reference_areas_m2"].values()), 4)
    (ROOT / "docs/validation/dimension-validation.json").write_text(
        json.dumps(out, indent=2)
    )
    return out


def build(stage=1):
    if "Oak_Ville" not in bpy.data.scenes:
        architecture()
        save(1)
    else:
        if bpy.context.scene.name != "Oak_Ville":
            raise RuntimeError("Select Oak_Ville scene before additive build")
        for c in bpy.data.collections:
            COLS[c.name] = c
    for n, fn in [(2, doors_routes), (3, furnish), (4, finish), (5, walkthrough)]:
        if n <= stage and bpy.context.scene.get("milestone", 1) < n:
            fn()
            save(n)
    return {
        "stage": bpy.context.scene["milestone"],
        "objects": len(bpy.context.scene.objects),
        "file": bpy.data.filepath,
    }


# Later milestones are kept in separate scripts for review and reproduction.
def doors_routes():
    exec(
        compile(
            (ROOT / "scripts/02_doors_routes.py").read_text(),
            str(ROOT / "scripts/02_doors_routes.py"),
            "exec",
        ),
        globals(),
    )


def furnish():
    exec(
        compile(
            (ROOT / "scripts/03_furnish.py").read_text(),
            str(ROOT / "scripts/03_furnish.py"),
            "exec",
        ),
        globals(),
    )


def finish():
    exec(
        compile(
            (ROOT / "scripts/04_materials_lighting.py").read_text(),
            str(ROOT / "scripts/04_materials_lighting.py"),
            "exec",
        ),
        globals(),
    )


def walkthrough():
    exec(
        compile(
            (ROOT / "scripts/05_walkthrough.py").read_text(),
            str(ROOT / "scripts/05_walkthrough.py"),
            "exec",
        ),
        globals(),
    )


if __name__ == "__main__":
    args = sys.argv[sys.argv.index("--") + 1 :] if "--" in sys.argv else []
    stage = int(args[args.index("--stage") + 1]) if "--stage" in args else 5
    if "--output" in args:
        BUILD_OUTPUT = (ROOT / args[args.index("--output") + 1]).resolve()
        if not BUILD_OUTPUT.is_relative_to(ROOT):
            raise ValueError("Build output must remain inside this project")
    build(stage)
