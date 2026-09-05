"""Inject disabled-collision faults in an owned Play session and verify recovery.

The final check unloads the helper in creative mode. End this test Play session
and run install_play_controls.py afterward before starting another session.
"""

import json
from pathlib import Path

import unreal
import oakville_runtime as runtime

state = runtime.STATE
if state is None:
    raise RuntimeError("Start a dedicated test Play session first")
pawn = state.pawn
capsule = pawn.get_editor_property("capsule_component")
report = {}
pawn.set_actor_enable_collision(False)
state.ensure_human_collision()
report["actor_collision_recovered"] = pawn.get_actor_enable_collision()
capsule.set_collision_enabled(unreal.CollisionEnabled.NO_COLLISION)
state.ensure_human_collision()
report["capsule_collision_recovered"] = (
    capsule.get_collision_enabled() == unreal.CollisionEnabled.QUERY_AND_PHYSICS
)
capsule.set_collision_response_to_channel(
    unreal.CollisionChannel.ECC_WORLD_STATIC, unreal.CollisionResponseType.ECR_IGNORE
)
state.ensure_human_collision()
report["wall_response_recovered"] = (
    capsule.get_collision_response_to_channel(unreal.CollisionChannel.ECC_WORLD_STATIC)
    == unreal.CollisionResponseType.ECR_BLOCK
)
state.set_creative(True)
report["creative_still_allows_noclip"] = not pawn.get_actor_enable_collision()
runtime.uninstall()
report["unload_restores_collision"] = (
    pawn.get_actor_enable_collision() and not state.creative
)
report["passed"] = all(report.values())
root = Path(__file__).resolve().parents[2]
(root / "docs/unreal/collision-recovery-validation.json").write_text(
    json.dumps(report, indent=2), encoding="utf-8"
)
print(json.dumps(report))
if not report["passed"]:
    raise RuntimeError("Human collision recovery failed")
