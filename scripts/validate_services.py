"""Check service counts, ledge containment and measurable kitchen clearance."""

import json
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[1]


def bounds(obj):
    corners = [obj.matrix_world @ Vector(point) for point in obj.bound_box]
    return [(min(p[i] for p in corners), max(p[i] for p in corners)) for i in range(3)]


units = [
    bpy.data.objects[room + "_Aircon_Body"]
    for room in ("Living", "Bedroom_3", "Bedroom_2", "Main_Bedroom")
]
unit_bounds = {obj.name: bounds(obj) for obj in units}
floor = bounds(bpy.data.objects["AC_Ledge_Floor"])
condenser = bounds(bpy.data.objects["AC_Ledge_Condenser_Indicative"])
contained = all(
    floor[i][0] <= condenser[i][0] <= condenser[i][1] <= floor[i][1] for i in (0, 1)
)
table = bounds(bpy.data.objects["Dining_Oval_Table"])
gap = 6.4 + table[1][0]
windows = [
    bpy.data.objects[room + "_Vent_Window"] for room in ("Common_Bath", "Ensuite")
]
frosted = all(o.active_material.name == "Frosted_Privacy_Glass" for o in windows)
report = {
    "indoor_units": unit_bounds,
    "indoor_units_above_2m": all(b[2][0] >= 2 for b in unit_bounds.values()),
    "condenser_within_labelled_ledge": contained,
    "bathroom_windows_frosted": frosted,
    "table_to_kitchen_datum_gap_m": round(gap, 4),
    "table_size_preserved_m": [
        round(v, 4) for v in bpy.data.objects["Dining_Oval_Table"].dimensions
    ],
}
report["passed"] = (
    report["indoor_units_above_2m"] and contained and frosted and gap >= 0.849
)
(ROOT / "docs/validation/services-validation.json").write_text(
    json.dumps(report, indent=2) + "\n", encoding="utf-8"
)
if not report["passed"]:
    raise RuntimeError(report)
print(json.dumps(report))
