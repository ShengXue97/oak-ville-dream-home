"""Apply intentional overhaul role changes to existing, uncustomised surfaces.

Regular geometry sync preserves Unreal material overrides. This migration only
changes known old roles, retaining a designer's distinct custom material.
"""

import gzip
import json
from pathlib import Path

import unreal

ROOT = Path(__file__).resolve().parents[2]
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if levels.is_in_play_in_editor():
    raise RuntimeError("Stop Play before updating furniture material roles")
with gzip.open(
    ROOT / "assets/unreal-export/scene.json.gz", "rt", encoding="utf-8"
) as stream:
    data = json.load(stream)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
by_id = {
    str(tag).removeprefix("BlenderID:"): actor
    for actor in actors
    for tag in actor.tags
    if str(tag).startswith("BlenderID:")
}
report = {"applied": [], "custom_overrides_retained": []}
for record in data["objects"]:
    name = record["name"]
    if name in {"Kitchen_Sink_Rim", "Kitchen_Sink_Bowl"}:
        target = "Metal_Brushed_Steel"
        previous = {"MI_Metal_Champagne", "MI_Appliance", "MI_Metal_Brushed_Steel"}
    elif "_Pillow_" in name and "_Detail_" not in name:
        target = "Fabric_Main"
        previous = {"MI_Porcelain", "MI_Fabric_Main"}
    else:
        continue
    component = by_id[record["source_id"]].get_component_by_class(
        unreal.StaticMeshComponent
    )
    current = component.get_material(0)
    if current and current.get_name() not in previous:
        report["custom_overrides_retained"].append(name)
        continue
    material = unreal.load_asset("/Game/OakVille/Materials/MI_" + target)
    if not material:
        raise RuntimeError("Run geometry sync first to create " + target)
    component.set_material(0, material)
    report["applied"].append(name)
levels.save_current_level()
(ROOT / "docs/unreal/furniture-material-migration.json").write_text(
    json.dumps(report, indent=2), encoding="utf-8"
)
print(json.dumps(report))
