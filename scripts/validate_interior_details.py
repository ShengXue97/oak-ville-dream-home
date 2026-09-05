"""Check actual mesh bounds for attached hardware and dining-chair clearance."""

import json
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]
bpy.context.view_layer.update()


def bounds(obj, local=False):
    points = [Vector(point) for point in obj.bound_box]
    if not local:
        points = [obj.matrix_world @ point for point in points]
    return [(min(p[i] for p in points), max(p[i] for p in points)) for i in range(3)]


def separation(first, second):
    return (
        sum(max(0, a[0] - b[1], b[0] - a[1]) ** 2 for a, b in zip(first, second)) ** 0.5
    )


hardware = []
for obj in bpy.context.scene.objects:
    if obj.get("hardware_part") != "Rose":
        continue
    leaf = bpy.data.objects[obj["attached_to_leaf"]]

    # Compare mesh vertices in hinge coordinates: parent transforms cancel.
    def hinge_bounds(part):
        points = [part.matrix_local @ Vector(p) for p in part.bound_box]
        return [
            (min(p[i] for p in points), max(p[i] for p in points)) for i in range(3)
        ]

    prefix = obj.name.removesuffix("Rose")
    spindle = bpy.data.objects[prefix + "Spindle"]
    lever = bpy.data.objects[prefix + "Lever"]
    gaps = [
        separation(hinge_bounds(a), hinge_bounds(b))
        for a, b in ((leaf, obj), (obj, spindle), (spindle, lever))
    ]
    hardware.append(
        {
            "mount": obj.name,
            "connection_gaps_m": gaps,
            "same_hinge": all(
                part.parent == leaf.parent for part in (obj, spindle, lever)
            ),
        }
    )

plants = [
    obj
    for obj in bpy.context.scene.objects
    if obj.name.startswith("Dining_Plant_") and obj.type == "MESH"
]
chairs = [
    obj
    for obj in bpy.context.scene.objects
    if obj.name.startswith("Dining_Chair_") and obj.type == "MESH"
]
clearances = [
    (separation(bounds(plant), bounds(chair)), plant.name, chair.name)
    for plant in plants
    for chair in chairs
]
closest = min(clearances)
all_plants = [
    obj
    for obj in bpy.context.scene.objects
    if obj.type == "MESH" and obj.name.startswith(("Dining_Plant_", "Living_Plant_"))
]
obstacles = [
    obj
    for obj in bpy.context.scene.objects
    if obj.type == "MESH"
    and obj.get("collision_source")
    and obj not in all_plants
    and not obj.name.startswith("COL_")
]
overlaps = []
for plant in all_plants:
    for obstacle in obstacles:
        depths = [
            min(a[1], b[1]) - max(a[0], b[0])
            for a, b in zip(bounds(plant), bounds(obstacle))
        ]
        if min(depths) > 0.001:
            overlaps.append([plant.name, obstacle.name])
hardware_wall_contacts = []
architecture = [
    obj
    for obj in bpy.context.scene.objects
    if obj.type == "MESH"
    and any(c.name == "Architecture" for c in obj.users_collection)
]
for handle in bpy.context.scene.objects:
    if not handle.get("hardware_part"):
        continue
    for wall in architecture:
        depths = [
            min(a[1], b[1]) - max(a[0], b[0])
            for a, b in zip(bounds(handle), bounds(wall))
        ]
        if min(depths) > 0.001:
            hardware_wall_contacts.append([handle.name, wall.name])
report = {
    "hardware_mounts_checked": len(hardware),
    "hardware_wall_contacts_at_open_stop": hardware_wall_contacts,
    "hardware": hardware,
    "hardware_attached": len(hardware) == 16
    and all(
        row["same_hinge"] and max(row["connection_gaps_m"]) < 0.0001 for row in hardware
    ),
    "dining_plant_to_chair_conservative_gap_m": round(closest[0], 4),
    "closest_objects": list(closest[1:]),
    "plant_clear_of_chairs": closest[0] >= 0.10,
    "plant_obstacle_overlaps": overlaps,
    "method": "Conservative world-axis mesh bounding boxes for every dining plant/chair component; mounted hardware checked in hinge coordinates. Static chair layout only, not chair pull-out simulation.",
}
report["passed"] = (
    report["hardware_attached"]
    and report["plant_clear_of_chairs"]
    and not overlaps
    and not hardware_wall_contacts
)
(ROOT / "docs/validation/interior-detail-validation.json").write_text(
    json.dumps(report, indent=2), encoding="utf-8"
)
print(
    json.dumps(
        {key: value for key, value in report.items() if key != "hardware"}, indent=2
    )
)
if not report["passed"]:
    raise RuntimeError("Interior detail validation failed")
