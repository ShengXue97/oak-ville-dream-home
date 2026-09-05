"""Repair the initial oak shader's missing input without replacing instances."""

import unreal

if unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor():
    raise RuntimeError("Stop Play before repairing the material")
material = unreal.load_asset("/Game/OakVille/Materials/M_Oak")
editor = unreal.MaterialEditingLibrary
# Existing instances and their colour/roughness overrides stay intact.
editor.delete_all_material_expressions(material)
colour = editor.create_material_expression(
    material, unreal.MaterialExpressionVectorParameter, -500, 0
)
colour.set_editor_property("parameter_name", "Colour")
roughness = editor.create_material_expression(
    material, unreal.MaterialExpressionScalarParameter, -500, 160
)
roughness.set_editor_property("parameter_name", "Roughness")
roughness.set_editor_property("default_value", 0.6)
uv = editor.create_material_expression(
    material, unreal.MaterialExpressionTextureCoordinate, -1000, -200
)
mask = editor.create_material_expression(
    material, unreal.MaterialExpressionComponentMask, -800, -200
)
mask.set_editor_property("r", True)
mask.set_editor_property("g", False)
wave = editor.create_material_expression(
    material, unreal.MaterialExpressionSine, -600, -200
)
wave.set_editor_property("period", 0.02)
contrast = editor.create_material_expression(
    material, unreal.MaterialExpressionMultiply, -400, -200
)
contrast.set_editor_property("const_b", 0.025)
offset = editor.create_material_expression(
    material, unreal.MaterialExpressionAdd, -200, -200
)
offset.set_editor_property("const_b", 0.975)
tint = editor.create_material_expression(
    material, unreal.MaterialExpressionMultiply, 0, 0
)
for source, target, pin in (
    (uv, mask, ""),
    (mask, wave, ""),
    (wave, contrast, "A"),
    (contrast, offset, "A"),
    (offset, tint, "A"),
    (colour, tint, "B"),
):
    if not editor.connect_material_expressions(source, "", target, pin):
        raise RuntimeError(f"Unable to connect {source} to {target}")
editor.connect_material_property(tint, "", unreal.MaterialProperty.MP_BASE_COLOR)
editor.connect_material_property(roughness, "", unreal.MaterialProperty.MP_ROUGHNESS)
editor.recompile_material(material)
unreal.EditorAssetLibrary.save_loaded_asset(material)
print("Oak graph repaired; all connections succeeded")
