# Changelog

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
