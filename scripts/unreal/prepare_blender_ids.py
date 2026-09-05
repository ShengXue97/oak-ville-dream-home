"""Run in Blender before saving new/duplicated objects for Unreal sync.

Existing unique IDs survive renames. Duplicates receive new UUIDs. This modifies
custom properties only; save Blender yourself after reviewing the changes.
"""

import uuid
import bpy

seen = set()
changed = []
for obj in sorted(bpy.data.scenes["Oak_Ville"].objects, key=lambda item: item.name):
    if obj.type != "MESH":
        continue
    source_id = obj.get("oakville_source_id")
    if not source_id or source_id in seen:
        source_id = str(uuid.uuid4())
        obj["oakville_source_id"] = source_id
        changed.append(obj.name)
    seen.add(source_id)
print("Assigned new Unreal IDs:", changed)
