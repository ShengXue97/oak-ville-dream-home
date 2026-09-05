# Changelog

## 0.10.3 - Coordinated minimalist materials and refined artwork

- Follow the user's Singapore BTO examples with a warmer natural-oak floor family, honey-oak dining furniture, flax textiles and restrained sage, clay and olive accents. Keep the sofa consistently cream.
- Replace the two oval art reliefs with a packed original landscape print inside the existing frames. Preserve image UVs through Blender-to-Unreal export and import the print texture into Unreal.
- Keep material roles editable in a JSON palette and apply intentional changes during the standard sync while preserving unrelated custom material overrides.
- Recover accidental multi-object Edit Mode mesh changes from the previously validated Blender model, as confirmed by the user; preserve the accidental session in a local recovery copy.
- Reopen the saved Blender source and validate dimensions, all 11 routes and furniture/door clearances. Existing walls, collision settings, lighting and player controls remain unchanged.

## 0.10.2 - Fix Shift-triggered camera displacement

- Use runtime speed assignment instead of editor change notifications to prevent Blueprint component reconstruction on Shift transitions. User confirmed the fix in Play.
- Replace the mesh-attached template viewpoint with a dedicated capsule-centred walkthrough camera. The old live camera was approximately 75 cm sideways from the collision capsule, allowing the view to enter walls while the player body stayed blocked.
- Keep either Shift as hold-to-run (320 cm/s), returning to 180 cm/s on release; only G explicitly enables creative flight.
- Recover an unexpected human flight mode or detached CharacterMovement collision component, in addition to disabled capsule collision.
- Independently sweep human displacement against architecture before accepting a new safe position. Reject wall crossings, stop movement and log the event; preserve native movement, jumping, furniture collision and moving doors.
- Add camera alignment, fault-injection and route regression checks. Tests exercise the Shift handler over actual frames; physical keyboard input is not simulated.
- Runtime-only patch: the dimensioned Blender geometry and existing Unreal mesh assets remain unchanged at source-model version 0.10.1.

## 0.10.1 - Correct main-bedroom door swing

- Correct the main-bedroom hinge to the Bedroom 2-side jamb and open into the bedroom rather than the corridor, preserving the opening dimensions and ensuite approach.
- Apply the correction in Blender and export the same signed angle for Unreal's E interaction.
- Synchronize the pending 0.10.0 windows, air conditioning and dining layout into Unreal, retaining calibrated lighting and applying the frosted-pane material change.

## 0.10.0 - Bathroom window fittings, air conditioning and kitchen access

- Completed both provisional bathroom window openings with frames, centre mullions, frosted privacy panes and latches, shown closed.
- Added four separately editable indoor A/C assemblies for living and all bedrooms, with outlet flaps, intake slots and local pipe-cover stubs. Detailed the existing outdoor condenser with supports, an outward grille and a service panel.
- Retained the one A/C ledge labelled on the supplied plan. Equipment sizes/positions are indicative; system capacity and complete pipe/drain routing remain unselected.
- Moved the dining set 200 mm west and 150 mm north to improve the kitchen approach, retaining its full dimensions and moving attached details with it.
- Added reproducible service builders, live collision-proxy updates, preview renders and documented installation assumptions. Ordinary Unreal sync retains the neutral-lighting calibration.

## 0.9.2 - Neutral daylight and controlled window highlights

- Rebalanced 19 Unreal area lights by purpose and room instead of assigning the same intensity to windows, ceilings and task lights. Neutral ceiling fill preserves cream finishes without the previous yellow cast.
- Reduced the direct sun from 2500 to 300 lux for this interior preview, widened its source angle, softened highlight contrast and reduced bloom. Fixed exposure prevents brightness pumping while walking.
- Added an editable lighting profile, embedded a copy in the Blender source, and retained it across normal geometry sync. Blender geometry, materials and lighting remain the source style reference.
- Added repeatable dining, kitchen, corridor and window-facing captures, plus saved-setting/material/collision integrity checks. Unreal shading remains an approximation of Blender's procedural materials and colour transform.

## 0.9.1 - Harden human collision and refresh imported physics

- Explicitly restore disabled actor/capsule collision and wall blocking in human mode, returning to the last safe position. Unloading the editor helper now exits noclip safely.
- Keep a visible HUMAN/collision ON or CREATIVE/collision OFF indicator so the current mode is unambiguous.
- Rebind placed mesh components after geometry/collision rebuilds while preserving material overrides. Refreshed 102 existing architectural physics bodies without changing geometry.
- Added actual Pawn-channel capsule tests against 49 wall segments from both sides, native walking/running wall-contact tests over game frames, and injected collision-fault recovery checks.
- The reported intermittent wall passage was not reproduced in the isolated tests; these changes address identified recovery/refresh gaps, not a proven root cause. An exact location/action sequence is still needed if the symptom recurs.

## 0.9.0 - Detailed furniture and fixtures throughout the flat

- Refined 294 furniture/detail components across seating, tables, beds, storage, kitchen, bathrooms, appliances and decor. Added curved chair shells, bent oak, sewn upholstery, draped bedding, shaped table profiles, cabinet hardware, hollow bowls and detailed appliance fronts.
- Added a genuinely recessed kitchen sink and countertop opening, basket drain, raised toilet lids, ring seats, connected shower arms and a shared brushed-steel material role.
- Retained room geometry and the corrected bedroom layout. New details are separately editable, parented to their source parts and use shared material roles; tiny trim does not add gameplay collision.
- Added deterministic family builders, collision-proxy refresh, seven detail preview views, mesh/attachment/recess checks and a targeted Unreal material migration that preserves custom overrides.
- Recovered an accidental uniform scale only after backing up the detailed scene and auditing against the verified committed model. Rechecked written plan datums, all planned routes and saved-file integrity before export.
- Updated designer schedules and documentation. Furniture remains proposed geometry, with manufacturer dimensions, concealed construction and moving cabinet mechanisms requiring further design.

## 0.8.0 - Faster walking and hold-to-run

- Increased normal walking from 120 to 180 cm/s. Hold either Shift key to run at 320 cm/s; releasing it restores walking speed.
- Retained native CharacterMovement, gravity, jump and collision. Shift running applies to human mode; creative flight keeps its existing speed.
- Updated the reproducible Blueprint setup, editor runtime, on-screen controls and instructions. Verified both Shift keys and release behaviour on the live native character; gravity remained at scale 1.
- Running, like E/G interaction, currently uses the editor Play Python integration and needs a packaged gameplay implementation for standalone delivery.

## 0.7.0 - Human walking, working doors and bedroom circulation

- Switched to Epic's standard First Person Blueprint character/controller with native grounded movement, gravity and jump. Start inside the entry with horizontal view, 172 cm capsule and assumed 160 cm eye height.
- Added E-operated interior doors and G creative/human mode toggle without function-key bindings. Entry stays closed and locked. Handles follow their leaves; moving leaves stop at the player capsule.
- Corrected hinge sides and swing directions from the plan in Blender and the shared export. Bath/yard folding symbols remain documented single-leaf proxies.
- Corrected Bedroom 3 in the editable Blender source: 900 × 1900 mm single bed, west wardrobe, foot-end desk and tucked stool. Checked 615 mm foot clearance, 1033 mm accessible-side clearance and no bed/stool overlap; room walls are unchanged.
- Restored an accidental whole-scene scale operation with owner approval. Updated reference drawing, schedules, cameras and regeneration scripts. Reproduction comparison tolerates only 0.011 mm numeric rounding differences.
- Validated native character spawn, grounded start, jump/landing, E opening, locked front door and G transitions in Play. Rechecked Blender dimensions and planned routes and Unreal mesh bounds/collision routes.
- Geometry changes remain Blender-first; export records actual door pose, and incremental sync preserves Unreal overrides and lighting.
- Limitations: E/G currently run through editor Python, not packaged gameplay. Windows SDK/C++ tools and a packaged interaction implementation remain required for a standalone build. Unlabelled plan depths and joinery details remain provisional.

## 0.6.0 - Editable Unreal walkthrough and Blender updates

- Added the Unreal 5.8.2 editor project under `unreal/OakVille`, with centimetre-scale meshes, a 172 cm character capsule, 160 cm eye height, 65 degree field of view and desktop walking controls.
- Added an incremental Blender export/update command, persistent object IDs, geometry hashes, safe Play/unsaved-map preflight checks and non-destructive removal reporting.
- Verified rename and geometry updates preserve Unreal material overrides, actor references and manual translation offsets. An unchanged sync skipped all 576 geometry rebuilds.
- Corrected triangle facing, repaired the shared oak shader, enabled Lumen explicitly and added sky/sun and exposure controls. Furniture/door collision uses tighter convex bounds; architecture uses simple boxes.
- Validated all 576 imported bounds within 0.00005 cm of the Blender export and all 11 planned capsule routes with supporting floors. Reopened Blender and passed its dimension, route and packed-reference checks.
- Geometry, furniture, role material instances and lighting remain separately editable. Scripts are formatted and documented in `docs/unreal/UPDATE_FROM_BLENDER.md`.
- Limitations: Windows SDK is missing, so no standalone executable is delivered yet. Doors are static in their exported open state. Materials approximate the Blender design; full node graphs and multiple material slots are not transferred. Conservative furniture collision does not certify every possible approach or seating interaction.

## 0.5.1 - Attached door hardware and botanical detail

- Replaced floating lever bars with connected mounting roses, spindles and levers on both sides of all eight doors; all parts remain parented to each door hinge.
- Replaced thick oval foliage with thin, curved pointed leaves, visible midribs, connected tapering branches, soil and varied greens on both plants.
- Moved the dining plant from (5.76, 4.77) m to (5.88, 6.05) m in plan coordinates to clear the chair backs. Architecture remains unchanged.
- Set the Bedroom 2 open stop to 86 degrees so its attached handle clears the adjacent partition; opening dimensions remain unchanged.
- Added reproducible detail construction and checks for handle attachment and plant-to-chair clearance, alongside existing saved-file and circulation validation.

## Unreleased — Project organisation

- Separated the supplied reference pack into `references/original/`, preserving source images and internal gallery links.
- Grouped generated drawings, schedules and validation evidence beneath `docs/`; moved editable palettes to `assets/styles/`.
- Updated reproduction scripts, documentation and packed Blender reference paths. Removed disposable backups, reproduction copies and tool caches; future temporary files use `.cache/`.
- Model version remains 0.5.0: this is project organisation and tooling, with no geometry or interior-design change.

## 0.5.0 — Walkthrough validation and designer handoff

- Added 345 separate collision proxies, adjustable 1.70 m human reference, exact 1 m cube, natural 65° eye cameras for all W01–W11 connections and room previews, plus orthographic inspection views.
- Added dimensioned SVG, room/area and camera schedules, packed in-file handoff text, style controls, fast-preview controls, reproduction and reopened-file validation scripts.
- Verified all 15 dimension-chain segments and 14 actual mesh datums, all 11 furnished routes, eight door sweeps, outward closed mesh normals and packed image loading. No linked assets are missing.
- Reproduced all five stages independently and compared the scene objects for transform/dimension/role/route differences. Added hollow editable vanity bowls and mixer taps during final fixture review.
- Documented 83.440 m² sampled internal floor excluding walls versus 91.8612 m² reference patches including walls, and the unresolved difference from the older plan's 86 m² figure.
- Kept the live user's Solid navigation view intact. Blender Walk mode has no wall/furniture capsule controller; collision proxies prepare later engine integration and are not interactive physics.

## 0.4.0 — Materials and lighting

- Added procedural pale-oak planks/grain, cream upholstery, oatmeal textiles, warm ivory wet finishes, curtains, tonal art and restrained greenery.
- Added named room lights, daylight aids and editable approximate temperature metadata. Hid daylight emitters from camera/transmission rays after render inspection.
- Added JSON palette export/application and non-destructive alternative-style duplication helpers.
- Saved and rendered the enclosed living view from a separate process while preserving the live session. Styled route validation passes. Textures are procedural; source images remain packed reference-only assets.

## 0.3.0 — Furnishings

- Furnished living/dining, all bedrooms, kitchen, both bathrooms, yard and shelter with separately editable components and shared material slots.
- Added component dimensions/locations schedule. Beds are 1200 × 2000 mm in Bedrooms 2/3 and 1600 × 2000 mm in the main bedroom; kitchen worktop is 900 mm high.
- Corrected wardrobe/column conflicts, entry storage swing conflict and vanity overhang without changing walls.
- All eleven furnished capsule routes pass. All eight door leaves sweep 0–90° at 1° steps without detected wall/furniture contact; no furniture/wall overlaps above 10 mm remain. Handles, drawer/wardrobe operation and final fabrication clearances still need detailed design.

## 0.2.0 — Doors and walkways

- Added eight independent hinged leaves with open/closed angle metadata, jambs, handles and glazing.
- Added all W01–W11 route curves and entry eye camera at 1.60 m with 65° horizontal field of view.
- Validated all routes through the unfurnished shell using a 0.50 × 1.70 m capsule against oriented bounds at 25 mm intervals with a 12.5 mm safety allowance. All pass with doors open.
- Routed main-bedroom access around its open door leaf. Door openings remain estimates pending site measurements.

## 0.1.0 — Dimensioned architecture

- Added metre-scale stepped shell, all room floor patches, thick shelter walls, separate ceilings and provisional soffit.
- Preserved the original startup scene; added live Inspection_Cutaway and Enclosed_Walkthrough layers.
- Packed three supplied reference images. Added reproducible staged Blender Python.
- Checked all 15 written chain segments: error below 0.01 mm in model datums. Actual photograph-to-wall-face interpretation remains provisional.
- Reference-patch internal area is 91.8612 m², not the secondary plan's quoted 86 m². Different conventions/variants and inferred endpoints require resolution; no scaling was used to force an area match.
