# Oak Ville — editable design reference

The dimensioned photograph controls this model. The coloured secondary plan confirms topology; the tour confirms room connections only. The active interior direction is warm cream, pale oak and layered minimalist upholstery.

## Evidence and coordinate convention

One Blender unit = one metre. X increases right across the plan; Y is negative down the plan; Z is above finished floor. Finished floor is Z=0. Written chains are converted directly from millimetres. Their stations are retained as `DIM_*` reference empties.

| Chain | Written segments (mm) | Total (mm) | Interpretation |
|---|---|---:|---|
| Upper | 3375 / 3000 / 3000 / 3300 | 12675 | Outer left reference, three bedroom partition references, outer right reference |
| Left | 4450 / 2800 / 1700 | 8950 | North reference, shelter north, shelter/entry south, kitchen south |
| Right | 4450 / 1950 / 1250 | 7650 | North reference, bath north, bath south, ledge south |
| Lower | 1750 / 1750 / 2275 / 1375 / 3950 | 11100 | Left reference, shelter east, kitchen west, kitchen/yard divider, yard/utility divider, bath/ledge east |

The photograph's extension lines indicate these structural/partition references, but are too coarse to resolve every finish face versus centre line. The model uses a **provisional wall-centre datum convention**, with thickness extending either side. This is not a claim that the dimensions are clear internal widths. Interior finished-face dimensions are derived separately. No unrectified pixel measurement controls a written span.

## Assumptions requiring site verification

| Item | Model assumption | Required verification |
|---|---|---|
| Finished ceiling | 2600 mm | Measure every room and beam underside |
| Typical partitions | 100 mm | Confirm finished thickness and wall construction |
| External walls | 150–250 mm | Confirm inside/outside faces, columns and facade |
| Shelter walls | 250 mm | Verify protected shelter envelope and actual door specification |
| Common bath west pier | 300 mm | Verify structural pier thickness |
| Bedroom 2/3 south boundary | 3350 mm below north datum | Undimensioned depth inferred from topology and photo; verify |
| Bath divider | X=8625 mm | Inferred; no written subdimension |
| Yard outer edge | X=7750 mm | Inferred utility strip width of 600 mm |
| Door openings | 800–1100 mm; head 2150 mm | Measure jambs, frame deductions, handedness and swings |
| Main facade windows | sill 850 / head 2350 mm | Verify width, panels and sill/head heights |
| Bath windows | sill 1800 / head 2350 mm | Verify ventilation/window positions |
| Kitchen open portal | underside 2350 mm | Verify beam and actual opening |
| Wet-room levels | Flush at Z=0 | Verify drops, thresholds, drainage and waterproofing |
| Services | Indicative fixtures only | Obtain plumbing, electrical, AC, sprinkler/ventilation information |

## Area and drawing-variant reconciliation

`validation/dimension-validation.json` lists all chain errors and non-overlapping floor-patch areas. These patches include wall reference footprints: internal reference area **91.8612 m²**, ledge **3.09375 m²**, combined **94.955 m²**. They are not the net usable area. The older plan quotes 86 m² internal and about 90 m² including ledge. Final 25 mm grid sampling gives **83.440 m² internal floor excluding wall footprints**, or **86.171 m² including the ledge**. This is a different area convention, not a statutory measurement; see `VALIDATION_REPORT.md` and `schedules/room-area-schedule.csv`.

Both drawings have the same basic rooms and access topology. The secondary plan shows furnished kitchen cabinets and a service-yard utility band more clearly; the photograph controls the kitchen west datum and lower chain. The secondary illustration is not dimensioned, so quantitative differences cannot be proven. The discrepancy in area remains unresolved pending original undistorted drawings/site measurements. No room has been resized to fit the headline area.

## Use by an interior designer

Use the room/object schedules and orthographic drawing as coordination references. Measure final finished faces on site before ordering joinery, glazing, doors or countertops. Keep structural walls, shelter geometry and facade separate from proposed finishes. This model does not establish permission to remove walls or alter the shelter. Produce detailed shop drawings, service layouts and specifications from confirmed measurements.

Architecture, Doors_Windows, Fixed_Joinery, Furniture, Lighting, Decor, Collision, Walkthrough and Reference_Plans are separate collections. Furniture is individually editable. `MINIMALIST_CREAM` groups the current joinery, furniture, lighting and decor. Shared material roles make the palette replaceable without editing architecture meshes.

## Availability

Blender 5.2.1 LTS and the interactive Blender MCP bridge were tested successfully. Git LFS is installed and configured locally for `.blend`. No external asset download is needed. All construction runs in the visible session, with additive stages; reopening the saved file for final verification will use a separate read-only background process to avoid discarding live edits.
