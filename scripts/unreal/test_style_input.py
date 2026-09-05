"""Exercise T press/hold/release in an owned Play session using its real handler.

This injects key state at the existing input adapter, not physical OS input.
"""
import json
from pathlib import Path
import unreal
import oakville_runtime as runtime

ROOT = Path(__file__).resolve().parents[2]
state = runtime.STATE
if state is None or state.styles is None:
    raise RuntimeError("Start an owned Play session with style assets installed")
original_down = state.down
original_style = state.styles.active
initial_materials = [(c, c.get_material(0)) for c, _ in state.styles.bindings]
capsule = state.pawn.capsule_component
movement = state.movement
try:
    state.down = lambda key: False
    state.tick(0.016)
    state.down = lambda key: key == 'T'
    state.tick(0.016)
    assert state.styles.active != original_style
    for _ in range(10):
        state.tick(0.016)
    assert state.styles.active != original_style, 'Held T repeated the switch'
    state.down = lambda key: False
    state.tick(0.016)
    state.down = lambda key: key == 'T'
    state.tick(0.016)
    assert state.styles.active == original_style
    assert all(c.get_material(0) == m for c, m in initial_materials)
    for key in ('LeftShift', 'RightShift', None):
        state.down = lambda name, key=key: name == key
        state.tick(0.016)
        assert abs(movement.max_walk_speed - (320 if key else 180)) < 0.01
    assert state.pawn.capsule_component == capsule
    assert state.movement == movement
    assert state.pawn.get_actor_enable_collision()
    assert not state.creative
    report = {'passed': True, 'press_hold_release_round_trip': True,
              'materials_restored': len(initial_materials), 'both_shift_keys_and_release': True,
              'capsule_movement_collision_preserved': True, 'physical_keyboard_simulated': False}
    (ROOT / 'docs/unreal/style-input-validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report))
finally:
    state.down = original_down
    state.keys.pop('T', None)
    state.styles.apply(original_style)
    state.update_walk_speed()
