# Oak Ville desktop walkthrough

Open `unreal/OakVille/OakVille.uproject` in Unreal 5.8.2 on monitor 2.
The default map is `Content/OakVille/Maps/OakVille`. Click Play, then click
the viewport to capture the mouse. Escape stops Play.

| Control | Behaviour |
| --- | --- |
| WASD / mouse | Walk / look using Epic's First Person Blueprint input |
| Hold Shift | Run; release to return to walking (either Shift key) |
| Space | Jump in human mode; ascend in creative mode |
| E | Open or close the nearby door you are looking at |
| G | Toggle human walking and creative flight without collision |
| Left Ctrl | Descend in creative mode |

Human mode is the default. Returning from creative mode places you at the last
grounded position to avoid spawning inside furniture. The front door stays
closed and locked. Interior doors start closed and rotate with their handles;
the animation stops if its leaf would intersect the player's capsule.
No custom controls use function keys. Unreal's own Shift+F1 mouse-release
shortcut remains available.

The capsule is 172 cm tall and 50 cm across. Assumed eye height is about 160 cm,
horizontal field of view 65 degrees, walking speed 180 cm/s, running speed
320 cm/s while Shift is held, gravity scale 1,
jump velocity 260 cm/s and maximum step height 18 cm. The entry start faces
into the flat with zero pitch. Native movement settings are in the copied
`/Game/FirstPerson/Blueprints/BP_FirstPersonCharacter` and
`BP_FirstPersonPlayerController`, selected by `BP_OakVilleGameMode`.

E/G interaction, Shift running and camera setup currently run through editor Python in
`scripts/unreal/oakville_runtime.py`, loaded by `Content/Python/init_unreal.py`.
This is an **editor Play walkthrough**. Packaging needs the missing Windows
SDK/C++ toolchain and a Blueprint/C++ port of the editor-only interactions.
Native movement uses Epic's standard CharacterMovement and Enhanced Input.

For geometry changes follow [Update from Blender](UPDATE_FROM_BLENDER.md).
Blender is authoritative for room geometry, furniture and door pivots. Unreal
owns its lighting and role material instances. Full Blender node graphs do not
transfer. The dimensioned plan and documented assumptions take precedence over
perspective tour screenshots; this is not a surveyed fabrication model.

## Reproduction and checks

The committed template assets come from the installed Epic UE 5.8 templates:
`TP_FirstPersonBP` and `TemplateResources/High/{Input,Characters}`. Their mount
paths are retained so Blueprint references resolve. To restore missing template
files run `python scripts/unreal/install_template_assets.py`; it never overwrites
existing files. The template character's visible mannequin is disabled.

For a fresh scene import run `import_scene.py`, then `sync_scene.py`,
`repair_oak_material.py`, `tune_lighting.py`, `setup_standard_controller.py`,
and `install_play_controls.py` using `python scripts/unreal/remote.py SCRIPT`.
Wait for each import/sync to finish before the next command. Regular geometry
updates use only `update_from_blender.py` and preserve lighting/material edits.

- `scene-validation.json`: 576 bounds, 11 capsule routes and supporting floors.
- `play-controls-validation.json`: actual spawned native character, grounded
  start, jump/landing, E targeting/opening, locked entry and G mode changes.
- `sync-preservation-test.json`: rename/update retention of overrides and offsets.
- `../validation/bedroom3-clearances.json`: corrected single-bed circulation.
- `scripts/unreal/capture_offscreen.py`: previews without changing window focus.

Furniture collision uses conservative convex hulls. The designated accessible
bedside and foot route are checked; wall-side slivers are not walking routes.
Bath and yard folding-door symbols remain single-leaf swing proxies, documented
in `assets/architecture/door-layout.json`; their detailed folding mechanisms
still need modelling. Doors and windows require site confirmation before build.
