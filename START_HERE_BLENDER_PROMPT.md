# Build my Oak Ville BTO in Blender - warm white and cream minimalism

Create an editable, fully furnished .blend model of my actual Oak Ville Singapore 4-room BTO, at real-world scale, suitable for later first-person walking simulation. Deliver the model, packed assets, preview renders and a short validation report. The initial interior must be contemporary warm minimalist: warm white and cream. The attached HDB tour is Japandi and is a spatial reference only.

## Source priority
1. OAK_VILLE_DIMENSIONED_PLAN.jpg controls dimensions, wall positions and openings. It is a photographed plan with perspective distortion: use written dimension values and their extension-line endpoints, not uncorrected image pixels.
2. OAK_VILLE_PRIMARY_FLOOR_PLAN.png clarifies layout and room labels. Retain it as a secondary plan; the newly dimensioned plan is authoritative where they differ.
3. rooms/ and walkways/ document a similar HDB show flat, not the actual unit. Use them to understand volumes, connections and plausible fittings, never to override the dimensioned Oak Ville plan.
4. USER_PRIMARY_STYLE_REFERENCE.png is the primary aesthetic reference, supplied by the user. Follow its recurring warm cream, pale oak, soft upholstered, layered contemporary-minimalist interiors. Ignore unrelated sponsored tiles, distressed unfinished rooms, dark leather furniture and dark-grey interiors within the Pinterest search screenshot. The screenshot is a mood reference, not a single coherent plan or proof of buildable dimensions.
5. cream-minimalist-references/ is supplementary only. The user screenshot overrides it wherever they differ. Never copy another project's layout, wall removals or room sizes.

## Scale and geometry
Use metres, 1 Blender unit = 1 metre, unit scale 1. Convert the plan's millimetres to metres. Do not make a generic apartment or scale the flat until it merely looks right. Its spaces must feel the size of this real Singapore 4-room BTO when viewed by a person at normal eye height.

Visible dimension chains to verify directly against the photo before modelling:
- Upper chain: 3375 + 3000 + 3000 + 3300 = 12675 mm.
- Left chain: 4450 + 2800 + 1700 = 8950 mm.
- Right chain: 4450 + 1950 + 1250 = 7650 mm.
- Lower chain: 1750 + 1750 + 2275 + 1375 + 3950 = 11100 mm.
These describe the marked reference spans; do not treat them automatically as clear internal room widths. Match each dimension's extension lines and distinguish wall faces from centre lines. The overall outline is stepped, not a rectangle. Do not compute the flat area by multiplying the largest spans.

The earlier plan lists about 90 sqm inclusive of 86 sqm internal floor area and air-con ledge. Use this as a plausibility check with a documented area convention, not a reason to distort the written dimensions. Record any disagreement rather than forcing a fit. The two plans may be different drawing variants; identify differences explicitly.

Build all three bedrooms, living/dining, kitchen, service yard, household shelter, both bathrooms, air-con ledge, entry and ALL corridors/doorway connections. Map screenshot left bedroom to Bedroom 3 and middle/nursery to Bedroom 2. Respect thick structural walls and shelter geometry. Preserve the actual corridor even if less photogenic than an open-plan show flat.

Ceiling heights, sill heights and any illegible dimensions must be marked as assumptions, not measured facts. If missing, use an adjustable provisional 2.60 m finished ceiling height for the initial model, with beams/soffits separate and flagged for verification. Derive wall thicknesses and doorway spans from plan evidence where possible, and list estimates. Do not claim survey or construction accuracy.

## Human-scale walkthrough readiness
Provide an adjustable 1.70 m human reference and eye camera at 1.60 m above finished floor; these are simulation defaults, not measurements of the owner. Add a 1 m calibration cube/ruler. Use a natural first-person field of view around 65 degrees horizontal, adjustable, and clearly distinguish it from wide-angle presentation cameras. Do not widen corridors or shrink furniture to fake spaciousness.

Use realistically dimensioned furniture, sanitaryware, counters, beds and appliances. Document key sizes. Place the first-person start at the entry. Create named route curves W01 entry-dining, W02 dining-living, W03 dining-kitchen, W04 bedroom corridor, W05 Bedroom 3, W06 Bedroom 2, W07 main bedroom, W08 common bath, W09 ensuite and W10 service yard. Include W11 shelter access from the plan even though no tour interior is available.

Provide separate simplified collision meshes for architecture and furniture; do not include invisible blockers across doors. Keep door leaves separate with hinge pivots and open/closed states. Check a provisional human capsule 0.50 m diameter and 1.70 m tall along accessible routes, with doors opened. Record actual narrow points, overhead obstacles and collisions. This is a simulation test, not certification of building/accessibility compliance. Do not promise game-engine collision merely because Blender viewport walk navigation works. Include instructions for later engine export and which collections to use as collision geometry.

## Aesthetic - warm white and cream contemporary minimalism
The user explicitly rejected the earlier dark timber/grey reference set and dislikes cold white/light-grey interiors. Use creamy warm whites, ivory, oatmeal and soft sand, matte or softly satin surfaces, simple flush cabinetry, restrained rounded furniture, subtle textiles and uncluttered surfaces. Use pale natural oak more generously in selected flooring, joinery, side tables and dining furniture, balanced with cream surfaces. Layer linen-like curtains, tactile cream upholstery and soft oatmeal rugs. Prefer rounded or softly rectangular sofas and low tables, restrained styling and a few plants. Aim for the comfortable, layered feeling in the user screenshot rather than an almost-empty all-white room. Lighting should feel welcoming and warm without turning every surface yellow. Suggested adjustable artificial-light range: 2700-3000 K, balanced with daylight.

Use the same palette and material family in every room, including both bathrooms and service yard. Use a consistent pale-oak or warm-ivory main floor scheme, warm-white walls, cream cabinetry and upholstery, and light neutral counters with quiet texture. Choose one main floor family for coherence; use suitable warm-ivory tile materials in wet rooms. Soft cove lighting, sheer curtains, simple recessed shelves and restrained rounded details may add depth. Minimise dark hardware and black accents except unavoidable appliances/screens. Avoid grey concrete, dark wood floors, rustic cabinetry, heavy marble veining, excessive decorative slat walls, dominant rattan themes and excessive ornaments. Do not reproduce the Japandi show-flat styling.

The user-supplied Pinterest screenshot is the primary style direction: warm organic contemporary minimalism. This descriptive label must not shift the design back to the original Japandi show flat. Selected light-oak vertical details are acceptable where useful, but avoid repeating them everywhere. The Weiken 229A Tengah Drive photographs are supplementary references for simple cabinetry and HDB-scale execution, not the controlling mood. Some photographed surfaces read cool from exposure/daylight: the user's warm-white/cream direction overrides that colour cast. Carry the palette into any unpictured room. Bathroom reference is for simple forms; use warm ivory materials rather than copying cooler grey veining. Keep structural openings rectangular unless the actual plan establishes otherwise; aesthetic references are not permission to change architecture.

## Make future interior restyling easy
Keep building geometry independent of the current style. Organise named collections: Architecture, Doors_Windows, Fixed_Joinery, Furniture, Lighting, Decor, Collision, Walkthrough, Reference_Plans. Within each, name by room and function. Do not merge the whole flat into one mesh. Keep individual furniture and removable finishes separate. Use shared, clearly named material roles such as Wall_Paint, Floor_Main, Cabinet_Front, Countertop and Fabric_Main. Make palette, roughness and lighting changes possible in one shared material or control location.

Keep MINIMALIST_CREAM as the active style collection/preset. Provide a documented process to duplicate it and swap furniture, materials and lights while preserving dimensions, architecture and circulation. Avoid destructive joins and baked-in decorative geometry. Keep modifiers editable where practical; use real dimensions and sensible origins. Pack textures into the .blend and use relative paths for any external assets. Include asset attribution/licences where applicable. Reference photographs are reference-only and must not be projected as room textures.

## Acceptance checks and deliverables
Before delivery, reopen the .blend and confirm packed assets work. Supply a dimensioned orthographic top view matching the Oak Ville plan, a table of plan values versus model values, room/area checks, estimated dimensions, and screenshots at human eye level for each room and walkway. Report missing evidence honestly. Verify furniture fits, doors swing, floors connect and the human capsule can traverse the intended routes. Keep the flat enclosed with real walls/ceilings for walking; provide a separate cutaway view for inspection.

Deliver the editable .blend, preview images, short walkthrough/export instructions and a readable assumptions/validation report. The default opened scene must show the warm cream minimalist design. Do not claim physical dimensions or walkthrough tests are verified unless actually checked.
