# Updating the walkthrough

`oak-ville.blend` is the geometry source. Unreal owns its lighting, walkthrough
settings and editable material instances. Keep both applications in this repo.

1. Edit and save `oak-ville.blend`. For new or duplicated objects, first run
   `scripts/unreal/prepare_blender_ids.py` in Blender's Text Editor, then save.
   Existing objects already carry IDs. Renaming them does not change those IDs.
2. Open `unreal/OakVille/OakVille.uproject`, open the OakVille map, stop Play,
   and save any Unreal edits.
3. From the repository terminal run:

   ```powershell
   python scripts/unreal/update_from_blender.py
   ```

The command exports the saved Blender file, updates the open Unreal session in
small batches, saves the map and meshes, then checks imported dimensions and all
11 planned routes. It does not move window focus. No Unreal MCP is required;
the project uses Epic's Python Remote Execution plugin over localhost.

The default executable locations match this machine. Use `--blender` and
`--engine` to supply different installation paths. Python must be available.

## What the update preserves

- Existing mesh assets and actor references; geometry is updated in place.
- Unreal component material overrides and existing role material instances.
- Unreal lighting, cameras, Blueprint settings, actor rotation and scale.
- Manual actor translation offsets relative to the last Blender position.
- User-created Unreal objects. Removed Blender objects are listed in
  `docs/unreal/sync-validation.json` for review, never silently deleted.

Existing object IDs must remain unique. The exporter rejects missing/duplicate
IDs before publishing a new export. When duplicating objects, run the ID helper
before the next export. Objects with custom Unreal labels are matched by ID.

Geometry is baked around each source object's world bounds centre. Blender
parent hierarchies are recorded as metadata, not reproduced as Unreal parenting.
Do not use this sync for animated/deforming assets. Meshes currently use their
first Blender material slot; full Blender node graphs do not transfer. Use the
shared `MI_*` instances in Unreal to change the interior palette. Blender
material reassignment on existing objects is not applied automatically.

## Review and safety

Preflight refuses Play mode, the wrong map, or unsaved Unreal edits. If Play
starts during a sync, it pauses until Play stops. The runner times out after ten
minutes without cancelling the editor callback; inspect progress before retrying.
Save Blender yourself: background export cannot see unsaved Blender edits.

`scene-validation.json` compares geometry to the saved Blender export and tests
the named routes. Intentional Unreal offsets/rotation/scale can fail the strict
dimension comparison; inspect rather than undoing those edits automatically.
Furniture collision is a conservative convex approximation; spaces beneath
joined furniture meshes are not necessarily traversable. Architecture and
room dimensions must remain governed by the dimensioned reference plan.

The standalone Windows build is pending installation of the Windows SDK;
the current delivery is the editable Unreal editor project. Doors are separate
static meshes in their exported open positions, not yet interactive doors.
