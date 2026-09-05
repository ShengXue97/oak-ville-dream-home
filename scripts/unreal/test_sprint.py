"""Check hold/release speed changes on the native character in test Play."""

import json
from pathlib import Path

import unreal
import oakville_runtime as runtime

state = runtime.STATE
if state is None or state.creative:
    raise RuntimeError("Start a dedicated human-mode test Play session first")

original_down = state.down
report = {}
try:
    for label, keys, expected in (
        ("walk", set(), 180.0),
        ("left_shift_run", {"LeftShift"}, 320.0),
        ("release_returns_to_walk", set(), 180.0),
        ("right_shift_run", {"RightShift"}, 320.0),
    ):
        state.down = lambda name: name in keys
        state.update_walk_speed()
        actual = state.movement.get_editor_property("max_walk_speed")
        report[label] = {"speed_cm_s": actual, "passed": actual == expected}
    report["native_character"] = isinstance(state.pawn, unreal.Character)
    report["gravity_scale"] = state.movement.get_editor_property("gravity_scale")
    report["passed"] = (
        all(
            report[key]["passed"]
            for key in (
                "walk",
                "left_shift_run",
                "release_returns_to_walk",
                "right_shift_run",
            )
        )
        and report["native_character"]
        and report["gravity_scale"] == 1.0
    )
finally:
    state.down = original_down
    state.update_walk_speed()

root = Path(__file__).resolve().parents[2]
(root / "docs/unreal/sprint-validation.json").write_text(
    json.dumps(report, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(report))
if not report["passed"]:
    raise RuntimeError("Sprint validation failed")
