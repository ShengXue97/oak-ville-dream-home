"""Inspect installed Unreal APIs and leave the visible editor ready for import."""

import json
from pathlib import Path

import unreal

ROOT = Path(unreal.Paths.project_dir()).resolve().parents[1]
output = ROOT / ".cache/unreal"
output.mkdir(parents=True, exist_ok=True)
names = [
    "GeometryScript_MeshEdits",
    "GeometryScriptSimpleMeshBuffers",
    "GeometryScript_NewAssetUtils",
    "GeometryScriptCreateNewStaticMeshAssetOptions",
    "ArchVisCharacter",
    "EditorActorSubsystem",
    "StaticMeshEditorSubsystem",
    "BlueprintEditorLibrary",
]
details = {}
for name in names:
    cls = getattr(unreal, name, None)
    details[name] = {
        "doc": str(getattr(cls, "__doc__", "")),
        "members": dir(cls) if cls else [],
    }
(output / "api-inspection.json").write_text(
    json.dumps(details, indent=2), encoding="utf-8"
)
unreal.log("OAK_VILLE_BOOTSTRAP_READY")
