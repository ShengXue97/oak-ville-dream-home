# Service fittings and kitchen approach

Delivery status: Blender, its export and the Unreal map are synchronized at
0.10.1, including the corrected main-bedroom hinge and inward swing.

The dimensioned plan shows one labelled A/C ledge, modelled at plan X
8.625–11.100 m and Y 6.400–7.650 m. It sits outside the ensuite beside the
service-yard area. No second ledge at the main bedroom or kitchen has been
inferred. The existing 880 × 380 × 740 mm condenser remains there, now with
120 mm supports, outward-facing grille and a service panel. This represents
an indicative multi-split installation; the capacity, number of actual outdoor
units and manufacturer clearances must be chosen during the mechanical design.

Four proposed indoor units are in `Fixed_Joinery`, each grouped under a named
`<Room>_Aircon_Assembly` empty. Body dimensions are 1000 × 230 × 280 mm for
living, 820 × 230 × 280 mm for Bedrooms 2/3, and 900 × 230 × 280 mm for the main
bedroom. They have separate face panels, outlet recesses, flaps, intake slots,
display panels and short pipe-cover stubs. Mounting centres are 2.28–2.30 m.
Full refrigerant/drain runs, gradients, wall penetrations, electrical provision
and cooling loads are not designed. Geometry is editable and manufacturer-neutral.

Both bathroom openings already existed with clear glass only. Visible frames,
mullions and latches now make them legible as closed windows. The original
provisional opening sizes remain 700 × 550 mm (common bath) and 800 × 550 mm
(ensuite), with sill 1.80 m. Frosted panes use the shared
`Frosted_Privacy_Glass` material: a matte privacy-glass visual approximation,
not an optical scattering simulation. Top-hung operation is proposed metadata;
the windows are currently static and closed. Exact fitting/opening style and
heights require confirmation against the actual supplied window schedule.

The dining table next to the fridge was treated as the kitchen obstruction.
The complete table/chair set and pendant move 200 mm west and 150 mm north,
without reducing their dimensions. The tabletop's southern edge moves from
plan Y 5.70 m to 5.55 m, increasing its distance to the kitchen datum at Y 6.40 m
from 700 to 850 mm. This is a measured tabletop-to-datum distance, not the
minimum width of every possible route. All 11 modelled capsule routes are
checked separately, including the dining-to-kitchen approach around the chairs.
The low coffee table by the sofa is unchanged pending clarification.

Reproduce with `scripts/complete_services.py` (`apply()`), included in stage 5.
For live edits run `refresh_proxies()` and `scripts/refresh_furniture_colliders.py`
afterward, refresh designer schedules, prepare new Blender IDs and save.
Run `python scripts/unreal/update_from_blender.py`, then
`python scripts/unreal/remote.py scripts/unreal/sync_service_materials.py` for
the intentional clear-to-frosted role change on the two existing panes.
Render `scripts/render_services_previews.py` with background Blender for four
inspection images in `renders/services/`.

Architectural dimensions, door swings and Unreal's lighting profile are retained.
Small trim carries no gameplay collision; A/C bodies, window frames/panes and
condenser feet have solid geometry and inspectable Blender collision proxies.

Validation: `docs/validation/services-validation.json` checks all four unit
heights, condenser containment, frosted pane assignments and the 850 mm
table-to-kitchen-datum distance. `services-routes.json` and saved-file reopening
verify the 11 intended routes, furniture/swing checks and written plan datums.
