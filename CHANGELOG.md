# Changelog

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
