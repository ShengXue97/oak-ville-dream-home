"""Build editable Unreal assets in small batches in the visible editor.

Geometry Script writes regular Static Mesh assets from the Blender export.
The input's centimetre coordinates are explicit, avoiding FBX axis ambiguity.
Rerunning resumes missing assets; it never replaces an existing mesh asset.
"""

import gzip
import json
import re
import time
from pathlib import Path

import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parents[1]
REPORT = ROOT / "docs/unreal/import-progress.json"
with gzip.open(
    ROOT / "assets/unreal-export/scene.json.gz", "rt", encoding="utf-8"
) as stream:
    DATA = json.load(stream)
ASSETS = unreal.AssetToolsHelpers.get_asset_tools()
ACTORS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
LEVELS = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
MAP = "/Game/OakVille/Maps/OakVille"


def safe_name(name):
    return re.sub(r"[^a-zA-Z0-9_]", "_", name)


def expression(material, cls, x, y, **properties):
    node = unreal.MaterialEditingLibrary.create_material_expression(material, cls, x, y)
    for key, value in properties.items():
        node.set_editor_property(key, value)
    return node


def master_material(name, translucent=False, wood=False):
    path = "/Game/OakVille/Materials/" + name
    existing = unreal.load_asset(path)
    if existing:
        return existing
    material = ASSETS.create_asset(
        name, "/Game/OakVille/Materials", unreal.Material, unreal.MaterialFactoryNew()
    )
    editor = unreal.MaterialEditingLibrary
    colour = expression(
        material,
        unreal.MaterialExpressionVectorParameter,
        -600,
        -200,
        parameter_name="Colour",
        default_value=unreal.LinearColor(0.7, 0.65, 0.55, 1),
    )
    roughness = expression(
        material,
        unreal.MaterialExpressionScalarParameter,
        -300,
        100,
        parameter_name="Roughness",
        default_value=0.6,
    )
    metallic = expression(
        material,
        unreal.MaterialExpressionScalarParameter,
        -300,
        200,
        parameter_name="Metallic",
        default_value=0.0,
    )
    editor.connect_material_property(colour, "", unreal.MaterialProperty.MP_BASE_COLOR)
    editor.connect_material_property(
        roughness, "", unreal.MaterialProperty.MP_ROUGHNESS
    )
    editor.connect_material_property(metallic, "", unreal.MaterialProperty.MP_METALLIC)
    if wood:
        position = expression(
            material, unreal.MaterialExpressionWorldPosition, -1200, -500
        )
        mask = expression(
            material,
            unreal.MaterialExpressionComponentMask,
            -1000,
            -500,
            r=True,
            g=False,
            b=False,
        )
        multiply = expression(
            material, unreal.MaterialExpressionMultiply, -800, -500, const_b=1.7
        )
        wave = expression(material, unreal.MaterialExpressionSine, -600, -500)
        contrast = expression(
            material, unreal.MaterialExpressionMultiply, -400, -500, const_b=0.045
        )
        offset = expression(
            material, unreal.MaterialExpressionAdd, -200, -500, const_b=0.94
        )
        tint = expression(material, unreal.MaterialExpressionMultiply, 0, -200)
        for a, a_pin, b, b_pin in (
            (position, "", mask, ""),
            (mask, "", multiply, "A"),
            (multiply, "", wave, ""),
            (wave, "", contrast, "A"),
            (contrast, "", offset, "A"),
            (offset, "", tint, "A"),
            (colour, "", tint, "B"),
        ):
            if not editor.connect_material_expressions(a, a_pin, b, b_pin):
                raise RuntimeError(f"Material connection failed: {a} -> {b}")
        editor.connect_material_property(
            tint, "", unreal.MaterialProperty.MP_BASE_COLOR
        )
    if translucent:
        material.set_editor_property("blend_mode", unreal.BlendMode.BLEND_TRANSLUCENT)
        material.set_editor_property("two_sided", True)
        opacity = expression(
            material,
            unreal.MaterialExpressionScalarParameter,
            -300,
            300,
            parameter_name="Opacity",
            default_value=0.12,
        )
        editor.connect_material_property(
            opacity, "", unreal.MaterialProperty.MP_OPACITY
        )
    editor.recompile_material(material)
    unreal.EditorAssetLibrary.save_loaded_asset(material)
    return material


def create_materials():
    masters = {
        "surface": master_material("M_Surface"),
        "wood": master_material("M_Oak", wood=True),
        "glass": master_material("M_Translucent", translucent=True),
    }
    result = {}
    for role, settings in DATA["materials"].items():
        base_role = settings.get("base_role", role)
        name = "MI_" + safe_name(role)
        path = "/Game/OakVille/Materials/" + name
        instance = unreal.load_asset(path)
        if not instance:
            instance = ASSETS.create_asset(
                name,
                "/Game/OakVille/Materials",
                unreal.MaterialInstanceConstant,
                unreal.MaterialInstanceConstantFactoryNew(),
            )
            kind = (
                "glass"
                if base_role in {"Glass", "Sheer_Linen"}
                else (
                    "wood"
                    if base_role
                    in {
                        "Oak_Joinery",
                        "Floor_Main",
                        "Accent_Honey_Oak",
                        "Accent_Natural_Oak_Floor",
                    }
                    else "surface"
                )
            )
            editor = unreal.MaterialEditingLibrary
            editor.set_material_instance_parent(instance, masters[kind])
            editor.set_material_instance_vector_parameter_value(
                instance, "Colour", unreal.LinearColor(*settings["colour"])
            )
            editor.set_material_instance_scalar_parameter_value(
                instance, "Roughness", settings["roughness"]
            )
            editor.set_material_instance_scalar_parameter_value(
                instance, "Metallic", settings["metallic"]
            )
            if kind == "glass":
                editor.set_material_instance_scalar_parameter_value(
                    instance, "Opacity", 0.12 if role == "Glass" else 0.48
                )
            unreal.EditorAssetLibrary.save_loaded_asset(instance)
        result[role] = instance
    return result


def create_mesh(record):
    name = "SM_" + safe_name(record["name"])
    path = "/Game/OakVille/Meshes/" + record["group"] + "/" + name
    mesh = unreal.load_asset(path)
    if mesh:
        return mesh
    buffers = unreal.GeometryScriptSimpleMeshBuffers()
    buffers.vertices = [unreal.Vector(*value) for value in record["vertices"]]
    buffers.normals = [unreal.Vector(*value) for value in record["normals"]]
    buffers.triangles = [unreal.IntVector(*value) for value in record["triangles"]]
    buffers.uv0 = [
        unreal.Vector2D(value[0] / 100, value[1] / 100) for value in record["vertices"]
    ]
    if record.get("uv0"):
        buffers.uv0 = [unreal.Vector2D(*uv) for uv in record["uv0"]]
    dynamic = unreal.DynamicMesh()
    unreal.GeometryScript_MeshEdits.append_buffers_to_mesh(dynamic, buffers)
    options = unreal.GeometryScriptCreateNewStaticMeshAssetOptions()
    options.enable_recompute_normals = False
    options.enable_recompute_tangents = True
    options.enable_collision = record["solid"]
    options.collision_mode = unreal.CollisionTraceFlag.CTF_USE_COMPLEX_AS_SIMPLE
    options.enable_nanite = False
    mesh, outcome = (
        unreal.GeometryScript_NewAssetUtils.create_new_static_mesh_asset_from_mesh(
            dynamic, path, options
        )
    )
    if not mesh:
        raise RuntimeError(f"Mesh creation failed: {record['name']}: {outcome}")
    mesh.set_material(0, MATERIALS[record["material"]])
    unreal.EditorAssetLibrary.set_metadata_tag(mesh, "BlenderObject", record["name"])
    unreal.EditorAssetLibrary.set_metadata_tag(
        mesh, "SourceVersion", DATA["source_version"]
    )
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)
    return mesh


def blueprint(name, parent):
    path = "/Game/OakVille/Blueprints/" + name
    asset = unreal.load_asset(path)
    if asset:
        return asset
    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", parent)
    return ASSETS.create_asset(
        name, "/Game/OakVille/Blueprints", unreal.Blueprint, factory
    )


def finish_walkthrough():
    pawn_bp = blueprint("BP_OakVilleWalker", unreal.ArchVisCharacter)
    pawn_class = unreal.load_class(None, pawn_bp.get_path_name() + "_C")
    pawn = unreal.get_default_object(pawn_class)
    pawn.get_editor_property("capsule_component").set_capsule_size(25, 86)
    pawn.set_editor_property("base_eye_height", 74.0)
    pawn.set_editor_property("mouse_sensitivity_scale_yaw", 0.65)
    pawn.set_editor_property("mouse_sensitivity_scale_pitch", 0.65)
    movement = pawn.get_editor_property("character_movement")
    movement.set_editor_property("walking_speed", 120.0)
    movement.set_editor_property("walking_acceleration", 600.0)
    movement.set_editor_property("walking_friction", 8.0)
    movement.set_editor_property("max_step_height", 8.0)
    unreal.EditorAssetLibrary.save_loaded_asset(pawn_bp)
    camera_bp = blueprint("BP_OakVilleCamera", unreal.PlayerCameraManager)
    camera_class = unreal.load_class(None, camera_bp.get_path_name() + "_C")
    unreal.get_default_object(camera_class).set_editor_property("default_fov", 65.0)
    unreal.EditorAssetLibrary.save_loaded_asset(camera_bp)
    controller_bp = blueprint("BP_OakVilleController", unreal.PlayerController)
    controller_class = unreal.load_class(None, controller_bp.get_path_name() + "_C")
    unreal.get_default_object(controller_class).set_editor_property(
        "player_camera_manager_class", camera_class
    )
    unreal.EditorAssetLibrary.save_loaded_asset(controller_bp)
    mode_bp = blueprint("BP_OakVilleGameMode", unreal.GameModeBase)
    mode_class = unreal.load_class(None, mode_bp.get_path_name() + "_C")
    mode = unreal.get_default_object(mode_class)
    mode.set_editor_property("default_pawn_class", pawn_class)
    mode.set_editor_property("player_controller_class", controller_class)
    unreal.EditorAssetLibrary.save_loaded_asset(mode_bp)
    world = unreal.get_editor_subsystem(unreal.UnrealEditorSubsystem).get_editor_world()
    world.get_world_settings().set_editor_property("default_game_mode", mode_class)
    start = next(
        (
            actor
            for actor in ACTORS.get_all_level_actors()
            if actor.get_actor_label() == "Walk_Start_172cm_Eye160cm"
        ),
        None,
    ) or ACTORS.spawn_actor_from_class(
        unreal.PlayerStart, unreal.Vector(270, 705, 88), unreal.Rotator(0, -90, 0)
    )
    start.set_actor_label("Walk_Start_172cm_Eye160cm")
    start.set_folder_path("Walkthrough")
    for record in DATA["lights"]:
        light_class = (
            unreal.DirectionalLight if record["type"] == "SUN" else unreal.RectLight
        )
        direction = unreal.Vector(*record.get("direction", [0, 0, -1]))
        rotation = unreal.MathLibrary.make_rot_from_x(direction)
        actor = ACTORS.spawn_actor_from_class(
            light_class, unreal.Vector(*record["location_cm"]), rotation
        )
        actor.set_actor_label(record["name"])
        actor.set_folder_path("Lighting")
        component = actor.get_component_by_class(unreal.LightComponent)
        component.set_mobility(unreal.ComponentMobility.MOVABLE)
        component.set_light_color(unreal.LinearColor(*record["colour"], 1))
        if record["type"] == "SUN":
            component.set_intensity(15000)
        else:
            component.set_editor_property("intensity_units", unreal.LightUnits.LUMENS)
            component.set_intensity(max(150, min(record["energy"] * 8, 2200)))
            component.set_editor_property("source_width", max(10, record["size"] * 100))
            component.set_editor_property(
                "source_height", max(10, record["size"] * 100)
            )
            component.set_editor_property("attenuation_radius", 500)
    sky = ACTORS.spawn_actor_from_class(unreal.SkyLight, unreal.Vector(600, 400, 400))
    sky.set_folder_path("Lighting")
    sky.get_component_by_class(unreal.SkyLightComponent).set_mobility(
        unreal.ComponentMobility.MOVABLE
    )
    ACTORS.spawn_actor_from_class(
        unreal.SkyAtmosphere, unreal.Vector(0, 0, 0)
    ).set_folder_path("Lighting")
    LEVELS.save_current_level()
    unreal.EditorLevelLibrary.set_level_viewport_camera_info(
        unreal.Vector(270, 705, 160), unreal.Rotator(0, -90, 0)
    )


def initialize_import():
    global MATERIALS, EXISTING, INDEX, STARTED, ERROR, BUSY
    if unreal.EditorAssetLibrary.does_asset_exist(MAP):
        LEVELS.load_level(MAP)
    else:
        LEVELS.new_level(MAP)
    MATERIALS = create_materials()
    EXISTING = {
        actor.get_actor_label(): actor for actor in ACTORS.get_all_level_actors()
    }
    INDEX = 0
    STARTED = time.monotonic()
    ERROR = None
    BUSY = False


def import_tick(delta_time):
    global INDEX, ERROR, BUSY
    if BUSY:
        return
    BUSY = True
    try:
        for _ in range(6):
            if INDEX >= len(DATA["objects"]):
                unreal.unregister_slate_post_tick_callback(TICK_HANDLE)
                finish_walkthrough()
                REPORT.write_text(
                    json.dumps(
                        {
                            "status": "complete",
                            "objects": INDEX,
                            "seconds": round(time.monotonic() - STARTED, 1),
                        },
                        indent=2,
                    )
                )
                unreal.log("OAK_VILLE_IMPORT_COMPLETE")
                return
            record = DATA["objects"][INDEX]
            if record["name"] not in EXISTING:
                mesh = create_mesh(record)
                actor = ACTORS.spawn_actor_from_class(
                    unreal.StaticMeshActor, unreal.Vector(*record["location_cm"])
                )
                actor.set_actor_label(record["name"])
                actor.set_folder_path(record["group"])
                component = actor.get_component_by_class(unreal.StaticMeshComponent)
                component.set_static_mesh(mesh)
                component.set_collision_profile_name(
                    "BlockAll" if record["solid"] else "NoCollision"
                )
                component.set_mobility(unreal.ComponentMobility.STATIC)
                actor.tags = [
                    unreal.Name("OakVille"),
                    unreal.Name("Blender:" + record["name"]),
                ]
                EXISTING[record["name"]] = actor
            INDEX += 1
        REPORT.write_text(
            json.dumps(
                {
                    "status": "importing",
                    "objects": INDEX,
                    "total": len(DATA["objects"]),
                },
                indent=2,
            )
        )
        if INDEX % 60 == 0:
            LEVELS.save_current_level()
    except Exception as exc:
        import traceback

        ERROR = traceback.format_exc()
        REPORT.write_text(
            json.dumps({"status": "error", "objects": INDEX, "error": ERROR}, indent=2)
        )
        unreal.unregister_slate_post_tick_callback(TICK_HANDLE)
        unreal.log_error(ERROR)
    finally:
        BUSY = False


if __name__ == "__main__":
    initialize_import()
    unreal.EditorLevelLibrary.set_level_viewport_camera_info(
        unreal.Vector(1600, 1500, 1500), unreal.Rotator(-45, -140, 0)
    )
    TICK_HANDLE = unreal.register_slate_post_tick_callback(import_tick)
    unreal.log("OAK_VILLE_IMPORT_STARTED")
