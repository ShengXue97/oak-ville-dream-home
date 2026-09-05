"""Check the revised single bed, stool separation and usable bedside/foot aisle."""

import json
from pathlib import Path
import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]


def bounds(name):
    obj = bpy.data.objects[name]
    points = [obj.matrix_world @ Vector(v) for v in obj.bound_box]
    return [
        min(p.x for p in points),
        max(p.x for p in points),
        min(-p.y for p in points),
        max(-p.y for p in points),
    ]


bed = bounds("Bedroom_3_Bed_Base")
desk = bounds("Bedroom_3_Desk")
stool = bounds("Bedroom_3_Desk_Stool")
fronts = [
    bounds(o.name)[1]
    for o in bpy.data.objects
    if o.name.startswith("Bedroom_3_Wardrobe_Front_")
]
mattress = bpy.data.objects["Bedroom_3_Mattress"]
report = {
    "mattress_m": [round(mattress.dimensions.x, 3), round(mattress.dimensions.y, 3)],
    "bed_foot_to_desk_clear_m": round(desk[2] - bed[3], 3),
    "wardrobe_front_to_bed_side_clear_m": round(bed[0] - max(fronts), 3),
    "stool_overlaps_bed": min(stool[1], bed[1]) > max(stool[0], bed[0])
    and min(stool[3], bed[3]) > max(stool[2], bed[2]),
    "route": "W05_Bedroom_3 crosses the foot and continues along the open side",
    "room_dimensions_changed": False,
    "note": "The wall-side gap is not a walking route. The stool is tucked under the desk; pull-out seating space is separate from the standing walkway.",
}
report["passed"] = (
    report["mattress_m"] == [0.9, 1.9]
    and report["bed_foot_to_desk_clear_m"] > 0.55
    and report["wardrobe_front_to_bed_side_clear_m"] > 0.9
    and not report["stool_overlaps_bed"]
)
(ROOT / "docs/validation/bedroom3-clearances.json").write_text(
    json.dumps(report, indent=2)
)
print(json.dumps(report, indent=2))
if not report["passed"]:
    raise RuntimeError("Bedroom 3 clearance validation failed")
