## Editable Blender model — v0.5.0

Open [oak-ville.blend](oak-ville.blend). The warm cream-and-oak model, scripts, packed references and designer schedules are complete. Start with the [validation report](docs/VALIDATION_REPORT.md), [designer handoff](docs/DESIGNER_HANDOFF.md), [walkthrough guide](docs/WALKTHROUGH.md) and [restyling guide](docs/RESTYLING.md). Local previews are in [renders/index.html](renders/index.html); reproduce them with `scripts/render_previews.py` and `scripts/preview_gallery.py`.

The model is a dimensioned design reference with documented assumptions, not surveyed fabrication drawings. Collision meshes are supplied for later engine integration; Blender Walk Navigation itself does not block walls/furniture. Use Solid shading for responsive movement.

Primary style update: USER_PRIMARY_STYLE_REFERENCE.png and STYLE_DIRECTION.md now control the aesthetic.

# Start here

Read START_HERE_BLENDER_PROMPT.md for the complete updated brief. Initial style: contemporary warm-white and cream minimalism. The dark reference set was rejected and is excluded.

# Corrected BTO Blender reference pack

This pack supersedes the earlier cropped screenshots. 125 complete viewer captures across nine camera stations, with the minimap open in every screenshot. Room filenames identify the camera location; walkway copies identify connections. Some angles overlap intentionally. Contact sheets are previews; use rooms/ for full-size images.

Open index.html for the gallery and WALKWAY_INDEX.md for circulation references. The full browser captures are retained in full-screen/ for checking framing.

## Reconstruction brief for the next AI
Use OAK_VILLE_DIMENSIONED_PLAN.jpg as the primary geometry source. OAK_VILLE_PRIMARY_FLOOR_PLAN.png is the earlier supplementary layout. The HDB show flat is similar, not verified identical. Keep room adjacency, entrance, household shelter, service yard, both bathrooms, and the complete shared corridor. Do not let furniture occupy or erase the walkways. Apply the requested new interior style to finishes and furniture after establishing the architecture.

The plan states approximately 90 sqm including 86 sqm internal area and the air-con ledge; the newly added detailed plan supplies dimension chains. Screenshots are wide-angle panorama views, not calibrated measurements. Do not infer precise dimensions from furniture or mirrors. Distinguish reflected rooms from actual openings. Keep assumptions explicit and verify dimensions against a dimensioned plan before a precise model.

R01 entrance; R02 living; R03 dining and corridor junction; R04 kitchen; R05 left bedroom (kid room); R06 middle bedroom (nursery); R07 main bedroom; R08 ensuite; R09 common bathroom. Left and middle refer to the supplied plan orientation, not compass directions. Sequence numbers are view IDs, not measured camera bearings.

W01-W10 have visual references; W11 household shelter access is plan-only. Service yard coverage is partial from the kitchen. No independent household shelter or air-con ledge photos are supplied. Corridor coverage is from the dining junction and room thresholds, not an invented central camera station.

Source: https://assets.hdb.gov.sg/residential/buying-a-flat/finding-a-flat/my-nice-home-gallery/eamnh/4room.html
Captured 5 September 2026. Existing style: Japandi. Do not copy its finishes unless requested.
