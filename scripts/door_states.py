"""Set all model door pivots OPEN or CLOSED; does not save automatically.

In Blender's Python Console:
    import runpy
    controls = runpy.run_path(bpy.path.abspath('//scripts/door_states.py'))
    controls['set_doors']('CLOSED')
"""

import math
import bpy


def set_doors(state="OPEN"):
    if state not in {"OPEN", "CLOSED"}:
        raise ValueError("Door state must be OPEN or CLOSED")
    for obj in bpy.context.scene.objects:
        if "open_angle_degrees" not in obj:
            continue
        key = "open_angle_degrees" if state == "OPEN" else "closed_angle_degrees"
        obj.rotation_euler.z = math.radians(obj[key])
        obj["door_state"] = state
    bpy.context.view_layer.update()
