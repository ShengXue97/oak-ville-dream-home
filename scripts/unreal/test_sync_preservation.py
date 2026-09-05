"""Exercise rename, geometry update and override preservation, then restore."""

import copy
import importlib.util
import json
from pathlib import Path
import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "sync_test", ROOT / "scripts/unreal/sync_scene.py"
)
sync = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sync)
record = next(
    r for r in sync.DATA["objects"] if r["group"] == "Decor" and not r["solid"]
)
actor = sync.BY_ID[record["source_id"]]
component = actor.get_component_by_class(unreal.StaticMeshComponent)
original_overrides = list(component.get_editor_property("override_materials"))
original_location = actor.get_actor_location()
original_label = actor.get_actor_label()
original_mesh = component.static_mesh
test_material = unreal.load_asset("/Game/OakVille/Materials/MI_Wall_Paint")
if test_material is None:
    raise RuntimeError("Test material is missing")
report = {}
try:
    component.set_material(0, test_material)
    offset = unreal.Vector(1, 2, 0)
    actor.set_actor_location(original_location + offset, False, False)
    changed = copy.deepcopy(record)
    changed["name"] += "_RenameTest"
    changed["location_cm"][0] += 3
    changed["vertices"] = [[v[0] * 1.01, v[1], v[2]] for v in changed["vertices"]]
    sync.update_record(changed)
    report["same_actor_and_mesh"] = component.static_mesh == original_mesh
    report["rename_followed_id"] = actor.get_actor_label() == changed["name"]
    report["material_override_retained"] = component.get_material(0) == test_material
    expected = original_location + offset + unreal.Vector(3, 0, 0)
    report["manual_offset_retained"] = (
        actor.get_actor_location() - expected
    ).length() < 0.001
    report["geometry_updated"] = changed["name"] in sync.REPORT["updated"]
finally:
    sync.update_record(record)
    actor.set_actor_location(original_location, False, False)
    actor.set_actor_label(original_label)
    component.set_editor_property("override_materials", original_overrides)
    unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).save_current_level()
report["passed"] = all(report.values())
(ROOT / "docs/unreal/sync-preservation-test.json").write_text(
    json.dumps(report, indent=2)
)
print(json.dumps(report))
if not report["passed"]:
    raise RuntimeError("Sync preservation test failed")
