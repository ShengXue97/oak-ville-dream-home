"""Update managed geometry while retaining Unreal materials and manual offsets.

Persistent Blender UUIDs identify objects across renames. Removed objects are
reported for review. Nothing absent from Blender is silently deleted. Existing
Unreal lights, Blueprint settings and component material overrides are retained.
"""

import hashlib
import importlib.util
import json
from pathlib import Path

import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "oakville_import", ROOT / "scripts/unreal/import_scene.py"
)
importer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(importer)
DATA = importer.DATA
if unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor():
    raise RuntimeError("Stop Play before syncing; no scene changes have been made")
importer.MATERIALS = importer.create_materials()
ACTORS = unreal.get_editor_subsystem(unreal.EditorActorSubsystem)
EXISTING = {actor.get_actor_label(): actor for actor in ACTORS.get_all_level_actors()}
BY_ID = {
    str(tag).removeprefix("BlenderID:"): actor
    for actor in EXISTING.values()
    for tag in actor.tags
    if str(tag).startswith("BlenderID:")
}
REPORT = {
    "updated": [],
    "unchanged": [],
    "added": [],
    "removed_or_renamed_review": [],
    "errors": [],
}
INDEX = 0
BUSY = False


def update_record(record):
    signature = hashlib.sha256(
        json.dumps(
            {
                "revision": DATA["geometry_revision"],
                "vertices": record["vertices"],
                "normals": record["normals"],
                "triangles": record["triangles"],
            },
            separators=(",", ":"),
        ).encode()
    ).hexdigest()
    name = record["name"]
    actor = BY_ID.get(record["source_id"]) or EXISTING.get(name)
    if not actor:
        mesh = importer.create_mesh(record)
        actor = ACTORS.spawn_actor_from_class(
            unreal.StaticMeshActor, unreal.Vector(*record["location_cm"])
        )
        actor.set_actor_label(name)
        actor.set_folder_path(record["group"])
        actor.tags = [unreal.Name("OakVille"), unreal.Name("Blender:" + name)]
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        component.set_static_mesh(mesh)
        component.set_collision_profile_name(
            "BlockAll" if record["solid"] else "NoCollision"
        )
        REPORT["added"].append(name)
    else:
        component = actor.get_component_by_class(unreal.StaticMeshComponent)
        mesh = component.static_mesh
    source_tag = unreal.Name("BlenderID:" + record["source_id"])
    if source_tag not in actor.tags:
        actor.tags = list(actor.tags) + [source_tag]
    old_name = unreal.EditorAssetLibrary.get_metadata_tag(mesh, "BlenderObject")
    if actor.get_actor_label() == old_name:
        actor.set_actor_label(name)
    unreal.EditorAssetLibrary.set_metadata_tag(mesh, "BlenderObject", name)
    unreal.EditorAssetLibrary.set_metadata_tag(mesh, "BlenderID", record["source_id"])
    previous_hash = unreal.EditorAssetLibrary.get_metadata_tag(mesh, "GeometryHash")
    previous_position = unreal.EditorAssetLibrary.get_metadata_tag(
        mesh, "BlenderCentreCm"
    )
    if signature != previous_hash:
        buffers = unreal.GeometryScriptSimpleMeshBuffers()
        buffers.vertices = [unreal.Vector(*value) for value in record["vertices"]]
        buffers.normals = [unreal.Vector(*value) for value in record["normals"]]
        buffers.triangles = [unreal.IntVector(*value) for value in record["triangles"]]
        uvs = []
        for value, normal in zip(record["vertices"], record["normals"]):
            axis = max(range(3), key=lambda index: abs(normal[index]))
            axes = [index for index in range(3) if index != axis]
            uvs.append(unreal.Vector2D(value[axes[0]] / 100, value[axes[1]] / 100))
        buffers.uv0 = uvs
        dynamic = unreal.DynamicMesh()
        unreal.GeometryScript_MeshEdits.append_buffers_to_mesh(dynamic, buffers)
        options = unreal.GeometryScriptCopyMeshToAssetOptions()
        options.enable_recompute_normals = False
        options.enable_recompute_tangents = True
        options.replace_materials = False
        unreal.GeometryScript_AssetUtils.copy_mesh_to_static_mesh(
            dynamic, mesh, options, unreal.GeometryScriptMeshWriteLOD()
        )
        unreal.EditorAssetLibrary.set_metadata_tag(mesh, "GeometryHash", signature)
        REPORT["updated"].append(name)
    else:
        REPORT["unchanged"].append(name)
    if previous_position:
        old = unreal.Vector(*json.loads(previous_position))
        offset = actor.get_actor_location() - old
        actor.set_actor_location(
            unreal.Vector(*record["location_cm"]) + offset, False, False
        )
    collision_kind = (
        "NDOP26"
        if record["group"] in {"Furniture", "Decor", "Doors_Windows"}
        else "BOX"
    )
    previous_collision = unreal.EditorAssetLibrary.get_metadata_tag(
        mesh, "CollisionKind"
    )
    if record["solid"] and (
        signature != previous_hash
        or previous_collision != collision_kind
        or unreal.get_editor_subsystem(
            unreal.StaticMeshEditorSubsystem
        ).get_simple_collision_count(mesh)
        == 0
    ):
        mesh_editor = unreal.get_editor_subsystem(unreal.StaticMeshEditorSubsystem)
        mesh_editor.remove_collisions(mesh)
        mesh.get_editor_property("body_setup").set_editor_property(
            "collision_trace_flag", unreal.CollisionTraceFlag.CTF_USE_SIMPLE_AND_COMPLEX
        )
        mesh_editor.add_simple_collisions(
            mesh, getattr(unreal.ScriptingCollisionShapeType, collision_kind)
        )
        unreal.EditorAssetLibrary.set_metadata_tag(
            mesh, "CollisionKind", collision_kind
        )
    component.set_collision_profile_name(
        "BlockAll" if record["solid"] else "NoCollision"
    )
    unreal.EditorAssetLibrary.set_metadata_tag(
        mesh, "BlenderCentreCm", json.dumps(record["location_cm"])
    )
    unreal.EditorAssetLibrary.set_metadata_tag(
        mesh, "SourceVersion", DATA["source_version"]
    )
    unreal.EditorAssetLibrary.save_loaded_asset(mesh)


def tick(delta_time):
    global INDEX, BUSY
    if BUSY:
        return
    BUSY = True
    try:
        if unreal.get_editor_subsystem(
            unreal.LevelEditorSubsystem
        ).is_in_play_in_editor():
            return
        for _ in range(4):
            if INDEX == len(DATA["objects"]):
                unreal.unregister_slate_post_tick_callback(HANDLE)
                source_names = {record["source_id"] for record in DATA["objects"]}
                REPORT["removed_or_renamed_review"] = [
                    source_id for source_id in BY_ID if source_id not in source_names
                ]
                unreal.get_editor_subsystem(
                    unreal.LevelEditorSubsystem
                ).save_current_level()
                REPORT["complete"] = True
                unreal._oakville_sync_running = False
                (ROOT / "docs/unreal/sync-validation.json").write_text(
                    json.dumps(REPORT, indent=2)
                )
                return
            update_record(DATA["objects"][INDEX])
            INDEX += 1
        (ROOT / "docs/unreal/sync-progress.json").write_text(
            json.dumps({"objects": INDEX, "total": len(DATA["objects"])})
        )
    except Exception:
        import traceback

        REPORT["errors"].append(traceback.format_exc())
        (ROOT / "docs/unreal/sync-validation.json").write_text(
            json.dumps(REPORT, indent=2)
        )
        unreal.unregister_slate_post_tick_callback(HANDLE)
        unreal._oakville_sync_running = False
        unreal.log_error(REPORT["errors"][-1])
    finally:
        BUSY = False


if __name__ == "__main__":
    if getattr(unreal, "_oakville_sync_running", False):
        raise RuntimeError("A sync is already running; wait for it to finish")
    unreal._oakville_sync_running = True
    HANDLE = unreal.register_slate_post_tick_callback(tick)
