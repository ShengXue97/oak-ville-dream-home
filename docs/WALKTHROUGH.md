# Walkthrough and reproduction

Open `oak-ville.blend` in Blender 5.2. The scene is `Oak_Ville`, with `PREVIEW_Living_Eye` as the active presentation camera. Numpad 0 shows it. The live viewport was left in the user's Solid navigation mode for responsiveness; materials and lighting remain available. The original startup scene is preserved separately.

## First-person inspection

For responsive movement, leave Walk Navigation first, then press **Z → Solid** before starting it again. Inside Walk Navigation, Z has a different function (upright view correction). Material Preview with scene lights evaluates lighting, glass and shadows while moving and can feel much slower. Use materials/lighting for stationary inspection. `scripts/preview_controls.py` exposes `set_preview('FAST')`, `set_preview('MATERIALS')` (studio lighting) and `set_preview('LIGHTING')` (scene lights), without moving the current view.

1. Keep view layer `Enclosed_Walkthrough` selected. Ceilings are real geometry in this layer.
2. Select `FP_Entry_160cm_65deg` in the Outliner. Use Ctrl+Numpad 0 to make it active, then Numpad 0 for its view. The start is at the inside of the entry, Z=1.60 m.
3. Use View → Navigation → Walk Navigation (Shift+grave on the default keymap). WASD moves, mouse looks, wheel changes speed, Shift accelerates. Confirm with left click/Enter; Esc cancels. Configure gravity and view height to 1.60 m if using gravity mode.
4. Named W01–W11 curves show intended routes. `EYE_W*` cameras provide eye-level views of those connections; `PREVIEW_*` cameras cover rooms.
5. Camera horizontal field of view is 65°, not a wide-angle trick. `PRESENTATION_Axonometric` and `PLAN_Orthographic` are separate orthographic inspection cameras.

Blender navigation does not implement the supplied capsule/mesh physics. It can pass through furniture or walls. The JSON route tests are separate geometry checks, not proof of an engine's collision behaviour or accessibility compliance.

## Cutaway, dimensions and calibration

Switch to `Inspection_Cutaway` and choose `PLAN_Orthographic` for the plan. This layer excludes only ceilings and reference images; architectural walls remain. Enable overlays to see curves and helpers. `docs/drawings/OAK_VILLE_DIMENSIONED_MODEL.svg` is the annotated vector drawing for a designer.

Enable `Walkthrough → Calibration` in the view layer to inspect the 1.70 m human and exact 1 m cube. The human parent scales uniformly by desired height / 1.70. These are simulation defaults, not the owner's dimensions. Disable calibration again for navigation and renders.

## Doors and collision export

Doors default open. Each `*_Door_Hinge` stores closed/open angles and owns its leaf/handle. `scripts/door_states.py` sets all doors OPEN or CLOSED without saving. Do not merge leaves into architectural walls.

`Collision_Architecture` contains floor, wall, frame, ceiling and glazing boxes. `Collision_Furniture` contains conservative simplified furniture/fixture bounds. `Collision_Doors` contains hinge-parented moving leaf proxies. The parent `Collision` collection is excluded from both view layers and never rendered. Enable it deliberately for export/debugging; render geometry and collision geometry should be exported as separate sets.

For a later engine, export at scale 1 metre/unit (e.g. glTF after baking unsupported procedural materials, or FBX with unit settings verified). Add a capsule controller of diameter 0.50 m and height 1.70 m with eye offset 1.60 m. Map static architectural/furniture meshes to static colliders and door proxies to moving colliders. Re-run route/door tests in the target engine, including stairs/thresholds once measured. Procedural Blender materials require baking or recreation for glTF/game engines. No engine project or baked material export is included.

## Reproduce and validate

To reproduce without overwriting the main file, append `--output .cache/reproduction-check.blend` to the build command below. Then open `oak-ville.blend` in background with `--python scripts/compare_reproduction.py` to compare the model data. These checks do not reload the live session.

`python scripts/preview_gallery.py` creates contact sheets and `renders/index.html` from the images; it uses Pillow. The Python scripts use four-space indentation and have been formatted with Black. Black is an optional development tool; Pillow is needed only for generating the preview gallery. Temporary reproduction files belong in `.cache/`.

From this project folder, using the installed Blender executable:

```powershell
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background --python scripts/build_oak_ville.py -- --stage 5
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background oak-ville.blend --python scripts/reopen_validate.py
& 'C:/Program Files/Blender Foundation/Blender 5.2/blender.exe' --background oak-ville.blend --python scripts/render_previews.py
```

The first command builds from scratch and overwrites `oak-ville.blend`; run it only when you intend to regenerate the deliverable. It saves stages 1–5 and does not commit automatically. For live additive construction use `runpy.run_path(bpy.path.abspath('//scripts/build_oak_ville.py'))['build'](stage)` in the active Oak_Ville scene. Completed stages are skipped to protect manual work; this is not a live parametric regeneration engine.

After moving furniture, regenerate collision proxies from the current layout before engine export. The supplied validation reports describe the saved deliverable, not later edits. Render outputs are ignored in Git but remain locally in `renders/`; all scripts and the main `.blend` are versioned. Git LFS stores `.blend` binaries.
