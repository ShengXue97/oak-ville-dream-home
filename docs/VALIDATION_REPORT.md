# Oak Ville validation and designer handoff

Version 0.5.0. The editable model is `../oak-ville.blend`. It was constructed through Blender MCP in the visible Blender 5.2.1 LTS session. Final saved-file checks run in an independent Blender process so the live session is not reloaded.

## What is verified

- Fifteen written dimension-chain segments match the model reference datums, with numerical error below 0.01 mm. Fourteen independent checks of actual architectural mesh datums also pass. This numerical precision does **not** establish the accuracy of estimated wall faces.
- All required spaces are present: living/dining, entry, three bedrooms, continuous bedroom corridor, kitchen, yard, utility band, both bathrooms, shelter and air-con ledge. The ensuite connects from the main bedroom; the shelter door opens off the entry/dining circulation. The shell is stepped and the enclosed view includes thirteen separate ceiling patches.
- Eleven W01–W11 routes pass a 0.50 m diameter, 1.70 m tall capsule check with doors open. Samples are at most 25 mm apart, with a 12.5 mm conservative allowance. Supporting floors connect at Z=0. Tilted fixtures use conservative world bounds; upright fixtures use oriented local bounds.
- Eight door leaves pass 91 angular samples from closed to open without detected wall/furniture penetration above the stated tolerance. Frames/leaf origins remain separate. Door handles, hinges, cabinet doors/drawers and appliance service clearances are not fully simulated.
- No furniture/architecture bounding-box penetration over 10 mm remains. Separate collision proxies are supplied for architecture, furniture and moving door leaves. They are hidden and excluded from the normal view layers.
- Source references are packed and readable after reopening. Surface textures are procedural, so there are no external texture dependencies or missing linked libraries.
- The entire model was regenerated from scripts in `.cache/reproduction-check.blend`. Comparison against the main file found no differences in object transforms/dimensions, collection memberships, material role assignments, vertex counts or route control points at 0.00001 m rounding. This test file is ignored by Git.

See `validation/reopened-file-validation.json`, `validation/reproduction-validation.json`, `validation/walkthrough-validation.json`, `validation/furniture-fit-and-door-swings.json`, `validation/dimension-validation.json` and `validation/mesh-dimensions-and-areas.json` in `docs/validation/` for machine-readable evidence.

## Dimensions and area limits

All written spans use the photographed plan. Thin extension lines cannot establish all finished-face/centre-line distinctions reliably; the model uses a documented provisional wall-centre datum interpretation. Bedroom 2/3 depth, bath divider, utility strip, wall thicknesses and openings remain estimates.

| Area convention | Model result |
|---|---:|
| Non-overlapping internal reference patches, including wall footprints | 91.8612 m² |
| Reference patches including ledge | 94.9550 m² |
| Sampled internal floor excluding wall footprints at Z=0.8 m | 83.440 m² |
| Sampled floor including ledge | 86.171 m² |
| Older plan quoted internal area | 86 m² |

The sampled floor method uses 25 mm cells, includes doorway floors, excludes wall footprints and does not subtract furniture. These conventions are not statutory area measurements. The remaining 2.560 m² difference from the older plan's internal figure is unresolved; no scaling was used to force agreement.

| Useful provisional span | Model value |
|---|---:|
| Bedroom 2/3 reference width | 3.000 m |
| Bedroom 2/3 nominal clear width between 100 mm partitions | 2.900 m |
| Bedroom 2/3 nominal clear depth | 3.200 m |
| Main bedroom nominal clear width | 3.125 m |
| Bedroom corridor reference band | 1.100 m |
| Bedroom corridor nominal wall-face clearance | 1.000 m |
| Shelter nominal clear rectangle | 1.500 × 2.550 m |
| Common bath nominal clear rectangle | 2.050 × 1.840 m |
| Kitchen nominal clear width before cabinets | 2.125 m |
| Door clear height below frame head | 2.120 m |
| Provisional ceiling height | 2.600 m |

Columns, frames, finishes and furniture can reduce these nominal spans locally. The per-route report lists the limiting object and distance to the tested capsule. Its `centered_clear_diameter_m` is a route-centred clearance measure, **not** a measured full corridor width or accessibility rating. Kitchen circulation near the fridge remains compact; review the actual appliance and door clearances with the designer.

## Visual review and walkthrough scope

Room and connection images are in `../renders/index.html`, alongside a rendered orthographic plan. The dimensioned vector plan is `drawings/OAK_VILLE_DIMENSIONED_MODEL.svg`. Human-scale images use Z=1.60 m and 65° horizontal field of view; the presentation/plan cameras are explicitly separate. Bathrooms have additional vanity views because one natural-angle view cannot show all fittings in the compact space.

The model uses warm cream, pale oak, oatmeal and ivory throughout. Proposed fixtures are editable design-level representations, not manufacturer CAD or shop drawings. Plumbing, electrical circuits, waterproofing, material specifications, structural status and actual service constraints are not established. The shelter/yard/ledge have limited photographic evidence; their fitting proposals must not be mistaken for surveyed conditions.

Blender Walk Navigation does **not** consume these collision meshes as a character controller. It can move through walls and furniture. Use Solid shading for responsive navigation, and use the separate material/lighting modes when inspecting finishes. The model is prepared for a later engine walkthrough; engine collision and accessibility compliance have not been certified.

## Before fabrication

Resolve the assumptions in `DESIGNER_HANDOFF.md` with an undistorted issued drawing and on-site measurements. Confirm structural/shelter constraints, finished wall faces, ceiling/beam heights, every opening, floor drops, services and exact appliance/furniture specifications. Produce dimensioned elevations and shop drawings from those confirmed values. Keep proposed finishes and removable joinery separate from the fixed building shell when exploring design options.
