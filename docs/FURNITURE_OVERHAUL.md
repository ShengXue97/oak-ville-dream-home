# Furniture and fixture overhaul

The warm cream-and-oak scheme and dimensioned architecture remain the basis.
This revision refines the proposed furniture throughout the flat instead of
substituting larger showroom pieces. All geometry is authored procedurally in
this repository; there are no downloaded asset licences or external textures.

| Family | Refinement |
| --- | --- |
| Dining chairs | Curved upholstered shells, bent-oak backs, sewn seat edges and tapered legs |
| Tables, desk and stools | Shaped oval tops, chamfered undersides, sculpted supports and rim details |
| Sofa | Fuller cushions, separate sewn welts and recessed timber base |
| Beds | Draped duvet surfaces, folded textiles, pillow/mattress piping, headboard seams and base reveals |
| Wardrobes, cabinets, vanities and shelves | Separate satin pulls, shelving fixings and edge details |
| Kitchen | Recessed stainless sink, real counter opening, basket drain, overflow and refined tap/hob details |
| Bathrooms | Hollow bowls, open ring seats, raised lids, cistern joints, flush buttons, basin drains, framed mirrors and connected shower arms |
| Appliances | Refrigerator divisions/vent, washer panel/dial/drawer/door rims, TV bezel and condenser vents |
| Decor | Hollow ceramic planters, bound rugs and separate book covers/page edges |

The geometry remains proposed, not a selected manufacturer's product or
fabrication drawing. Internal appliance machinery, concealed plumbing,
upholstery fabrication and cabinet-opening mechanisms are not modelled.
Bathroom/yard door folding mechanisms remain the earlier documented proxies.

## Editing and reproduction

`scripts/furniture_overhaul.py` contains readable family builders and reusable
mesh helpers. The final build stage calls `apply()` after the basic furniture
and vanity builders. `apply('seating')`, `apply('bedrooms')`, `apply('joinery')`,
`apply('fixtures')`, `apply('appliances')` and `apply('decor')` support incremental
work in the open Blender session. Repeating a family replaces its own meshes
without creating duplicate details. The original layout envelopes are stored
on the source objects; the existing persistent export IDs are retained.

New `_Detail_` parts are separately editable and parented to their source part,
so handles, piping and trim follow that part when it moves. Materials use the
existing role system plus `Metal_Brushed_Steel`. Edit the shared roles to restyle
the flat. Refined meshes are editable directly; the chair edge bevel remains
a modifier. Re-running a builder replaces manual edits to its generated mesh.

After manual live refinement, `scripts/refresh_furniture_colliders.py` updates
the inspection proxies. Small trim, stitching, drain and control parts have no
gameplay collision; the primary furniture bodies provide collision. Regenerated
models create their proxies automatically. The saved model includes all details.

Use the normal Blender-to-Unreal update command. For an existing pre-overhaul
Unreal map, run `scripts/unreal/sync_furniture_materials.py` once after sync to
change the sink's old material and the pillows' former porcelain role. This
migration retains distinct custom Unreal materials. Fresh imports receive the
correct roles directly; subsequent regular syncs continue preserving overrides.

## Review evidence

- `validation/furniture-overhaul.json`: closed meshes, parented details, triangle
  budget and ray-measured sink recess.
- `validation/reopened-file-validation.json`: saved-file plan datums, door
  swings, routes, packed references and collision-source mesh integrity.
- `validation/bedroom3-clearances.json`: 615 mm at the bed foot and approximately
  1017 mm beside the bed, now measured to the wardrobe pulls.
- `validation/reproduction-validation.json`: comparison against a fresh build.
- `unreal/scene-validation.json`: imported bounds and engine collision routes.

Run `scripts/render_furniture_previews.py` in background Blender with the saved
model to reproduce the sofa, dining, bed, sink, toilet, vanity and washer reviews
under `renders/furniture/`. These outputs are ignored by Git. They are visual
reviews of proposed furnishings, not evidence of site measurements or hardware
performance. The earlier accidental scale operation was recovered only after
backing up the detailed scene and checking the transform difference against the
verified committed v0.8.0 model. Room dimensions were restored before export.
