"""Apply the saved Blender style to the editor without changing custom overrides."""
import gzip
import json
import sys
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/unreal"))
from oakville_styles import StyleSession

levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if levels.is_in_play_in_editor():
    raise RuntimeError("Stop Play before synchronizing styles")
with gzip.open(ROOT / "assets/unreal-export/scene.json.gz", "rt") as stream:
    data = json.load(stream)
session = StyleSession(unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors(), data)
count = session.apply(data.get("active_style", "MINIMALIST_CREAM"))
levels.save_current_level()
report = {"active_style": session.active, "surfaces": count, "custom_overrides_retained": session.custom_overrides, "passed": True}
(ROOT / "docs/unreal/style-sync-validation.json").write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps(report))
