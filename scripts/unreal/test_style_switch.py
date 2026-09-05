"""Check saved-map style restoration and preservation without moving the camera."""
import gzip
import json
import sys
from pathlib import Path
import unreal

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts/unreal"))
from oakville_styles import StyleSession, MINIMALIST, TROPICAL

levels = unreal.get_editor_subsystem(unreal.LevelEditorSubsystem)
if levels.is_in_play_in_editor():
    raise RuntimeError("Run editor style checks outside Play")
with gzip.open(ROOT / "assets/unreal-export/scene.json.gz", "rt") as stream:
    data = json.load(stream)
actors = unreal.get_editor_subsystem(unreal.EditorActorSubsystem).get_all_level_actors()
session = StyleSession(actors, data)
components = [(a, a.get_component_by_class(unreal.StaticMeshComponent)) for a in actors]
components = [(a, c) for a, c in components if c]
baseline = [(c, c.get_material(0)) for _, c in components]
invariants = [(a, str(a.get_actor_transform()), c.static_mesh,
               c.get_collision_enabled(), c.get_collision_profile_name(),
               a.get_actor_enable_collision()) for a, c in components]
try:
    session.apply(MINIMALIST)
    minimalist = [c.get_material(0) for _, c in components]
    session.apply(TROPICAL)
    tropical = [c.get_material(0) for _, c in components]
    changed = sum(a != b for a, b in zip(minimalist, tropical))
    assert changed > 300
    session.apply(MINIMALIST)
    assert [c.get_material(0) for _, c in components] == minimalist
    session.apply(TROPICAL)
    assert [c.get_material(0) for _, c in components] == tropical
    for a, transform, mesh, enabled, profile, collision in invariants:
        c = a.get_component_by_class(unreal.StaticMeshComponent)
        assert str(a.get_actor_transform()) == transform
        assert c.static_mesh == mesh
        assert c.get_collision_enabled() == enabled
        assert c.get_collision_profile_name() == profile
        assert a.get_actor_enable_collision() == collision
    # A deliberately unrelated override is kept in both directions.
    component = session.bindings[0][0]
    original = component.get_material(0)
    custom = unreal.load_asset('/Game/OakVille/Materials/MI_Appliance')
    component.set_material(0, custom)
    protected = StyleSession(actors, data)
    protected.apply(MINIMALIST)
    assert component.get_material(0) == custom
    protected.apply(TROPICAL)
    assert component.get_material(0) == custom
    component.set_material(0, original)
    report = {"passed": True, "changed_surfaces": changed,
              "both_round_trips_exact": True, "transforms_meshes_collision_unchanged": True,
              "unrelated_override_preserved": True}
    (ROOT / 'docs/unreal/style-switch-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
finally:
    for component, material in baseline:
        component.set_material(0, material)
    levels.save_current_level()
