# Oak Ville desktop walkthrough

Open `unreal/OakVille/OakVille.uproject` in Unreal 5.8.2. Keep it on monitor 2.
The default map is `Content/OakVille/Maps/OakVille`. Click Play to walk using
WASD and the mouse; Escape stops Play, and Shift+F1 releases the mouse.

The character is 172 cm tall with a 50 cm diameter capsule. Eye height starts
at 160 cm above floor, horizontal field of view is 65 degrees and walking speed
is 120 cm/s. The eye height is an assumption for a 172 cm owner, not a measurement.
Settings live in the `BP_OakVilleWalker` and `BP_OakVilleCamera` defaults.

For geometry changes, follow [Update from Blender](UPDATE_FROM_BLENDER.md).
For interior style changes, edit the shared `MI_*` material instances and keep
architecture separate from furniture and decor. Current materials are an Unreal
approximation of the cream/oak design, not a transfer of Blender shader graphs.

The source plan's written dimension spans remain authoritative; consult the
designer handoff and assumptions in the parent docs folder before actual building.
This is a design visualisation, not a surveyed fabrication model.

## Validation and reproduction

- `scene-validation.json`: imported bounds, 11 route sweeps and supporting floors.
- `sync-preservation-test.json`: rename, mesh update, material and offset retention.
- `sync-validation.json`: most recent incremental update result.
- `sdk-report.txt`: Windows SDK absent; standalone packaging remains pending.
- `scripts/unreal/import_scene.py`: first import into an open project with its
  configured plugins. Then run `sync_scene.py` to establish IDs and collision,
  `repair_oak_material.py` for the refined oak graph, and `tune_lighting.py`.
- `scripts/unreal/capture_offscreen.py`: interior preview without window focus.
  Output goes to ignored `renders/unreal/`. It uses an offscreen Lumen capture,
  so noise/performance differ from the interactive viewport.

Regular updates intentionally do not rerun lighting or material repair scripts.
Doors remain open static meshes; door interaction is not implemented. Furniture
colliders are conservative convex hull approximations. Planned routes pass, but
walking into furniture remains blocked and the capsule needs 25 cm clearance
around its centre. No room or furnishing was shrunk to make navigation easier.
