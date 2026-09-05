"""Apply intentional Blender accent roles, preserving unrelated Unreal overrides."""

import json
from pathlib import Path

import unreal

ROOT = Path(__file__).resolve().parents[2]
export = json.loads((ROOT / "assets/unreal-export/manifest.json").read_text())
if export.get("active_style", "MINIMALIST_CREAM") != "MINIMALIST_CREAM":
    raise RuntimeError(
        "Minimalist accent migration cannot run on a tropical export; use sync_styles.py"
    )
levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if levels.is_in_play_in_editor():
    raise RuntimeError("Stop Play before updating accent materials")
task = unreal.AssetImportTask()
task.filename = str(ROOT / "assets/artwork/mineral-landscape.png")
task.destination_path = "/Game/OakVille/Art"
task.destination_name = "T_MineralLandscape"
task.automated = True
task.save = True
task.replace_existing = True
unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
texture = unreal.load_asset("/Game/OakVille/Art/T_MineralLandscape")
art = unreal.load_asset("/Game/OakVille/Materials/M_Artwork")
if art is None:
    art = unreal.AssetToolsHelpers.get_asset_tools().create_asset(
        "M_Artwork",
        "/Game/OakVille/Materials",
        unreal.Material,
        unreal.MaterialFactoryNew(),
    )
    editor = unreal.MaterialEditingLibrary
    sample = editor.create_material_expression(
        art, unreal.MaterialExpressionTextureSample, -300, 0
    )
    sample.set_editor_property("texture", texture)
    editor.connect_material_property(
        sample, "RGB", unreal.MaterialProperty.MP_BASE_COLOR
    )
    roughness = editor.create_material_expression(
        art, unreal.MaterialExpressionConstant, -300, 200
    )
    roughness.set_editor_property("r", 0.95)
    editor.connect_material_property(
        roughness, "", unreal.MaterialProperty.MP_ROUGHNESS
    )
    editor.recompile_material(art)
    unreal.EditorAssetLibrary.save_loaded_asset(art)
instance = unreal.load_asset("/Game/OakVille/Materials/MI_Art_Mineral_Landscape")
art.set_editor_property("two_sided", True)
unreal.MaterialEditingLibrary.recompile_material(art)
unreal.EditorAssetLibrary.save_loaded_asset(art)
if instance is None:
    raise RuntimeError("Sync the Blender geometry before applying the artwork")
unreal.MaterialEditingLibrary.set_material_instance_parent(instance, art)
unreal.EditorAssetLibrary.save_loaded_asset(instance)
assignments = json.loads((ROOT / "assets/styles/accent-assignments.json").read_text())[
    "assignments"
]
actors = {
    a.get_actor_label(): a
    for a in unreal.get_editor_subsystem(
        unreal.EditorActorSubsystem
    ).get_all_level_actors()
}
report = {"applied": [], "custom_overrides_retained": [], "errors": []}
for name, roles in assignments.items():
    actor = actors.get(name)
    material = unreal.load_asset("/Game/OakVille/Materials/MI_" + roles["target"])
    if actor is None or material is None:
        report["errors"].append(name)
        continue
    component = actor.get_component_by_class(unreal.StaticMeshComponent)
    current = component.get_material(0)
    if (
        name.endswith("_Detail_Bent_Oak_Back")
        and roles["target"] == "Oak_Joinery"
        and current
        and current.get_name() == "MI_Accent_Flax_Linen"
    ):
        component.set_material(0, material)
        current = material
    if current and current.get_name() not in {
        "MI_" + roles["previous"],
        "MI_" + roles["target"],
    }:
        report["custom_overrides_retained"].append(name)
        continue
    component.set_material(0, material)
    if component.get_material(0) != material:
        report["errors"].append(name)
    report["applied"].append(name)
levels.save_current_level()
report["passed"] = not report["errors"]
(ROOT / "docs/unreal/accent-material-validation.json").write_text(
    json.dumps(report, indent=2) + "\n"
)
print(json.dumps(report))
if not report["passed"]:
    raise RuntimeError("Accent material assignment failed")
