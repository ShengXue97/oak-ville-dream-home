# Oak Ville: modern tropical luxury handover

Implementation update: v0.11.0 adds a reversible finish selector in Blender and
Unreal Play (T). See [the switch guide](STYLE_SWITCH.md) and
[sampled reference review](tropical-modern/REFERENCE_ANALYSIS.md). The original
handover below records the earlier planning state; replacement furniture and
full-tour reference coverage remain outside this first finish-switch release.

Date: 2026-09-05
Baseline application version: **0.10.3**
Baseline implementation commit: **5689766** (`fix: refine minimalist material balance and artwork`)
Workspace: `C:\Users\Admin\Documents\coding-projects\oak-ville-dream-home`

## 1. Immediate objective

Develop a **second interior design option** for the existing Singapore BTO flat,
inspired by the user's selected modern tropical luxury home tour. Preserve the
current minimalist option and the dimensioned apartment. This document hands
over the research and implementation plan; it does not implement the new style.

The user selected the first reference from the tropical shortlist:

- Title: **Walk through a Tropical-lux home in the east of Singapore**.
- Designer/channel attribution from the search result: **i.Poise Design**.
- URL: https://www.youtube.com/watch?v=EcJ51c-ZILI
- Selection: explicit user approval of this reference as the intended direction.
- Reference status: video located, but **not yet watched frame by frame, downloaded,
  or captured into local screenshots** during this task.
- The property's exact type, layout, furnishings and finishes must be verified
  from the video before being described as observed facts. Do not call it a BTO
  without evidence.

The user's immediate follow-up was how screenshots would be obtained from a
video. Explain actual available access, capture representative frames if possible,
and ask for a video file or selected screenshots only if access is unavailable.
Do not claim a video has been viewed merely because its search description was read.

## 2. Scope and user decisions

### Accepted direction

- Singapore BTO context, with all existing rooms and walkways retained.
- Modern tropical luxury as an additional option, based on the selected video.
- Blender remains the source for model geometry, furniture and door pivots.
- Unreal remains the interactive desktop walkthrough and must reflect Blender edits.
- Keep interiors easy for a human designer to inspect and change later.
- Code must be clearly named, properly indented and readable.
- Preserve the current minimalist version for comparison and restoration.

### Preferences learned from previous iterations

- The user wants coherent material and colour variation, not random colours on
  separate parts of the sofa. The current sofa is consistently cream.
- Furniture should have convincing construction, texture and shape, including
  fixtures such as sinks and toilets. Primitive placeholders were rejected.
- Natural-looking plants must not intersect furniture or obstruct routes.
- Artwork should look finished and considered. The former oval reliefs have
  already been replaced with an original landscape print.
- Lighting should preserve material colour and window detail. A pervasive yellow
  tint, clipped window highlights, and excessively dull interiors were rejected.
- Respond efficiently; avoid redundant tests after appropriate checks pass.
- Keep Unreal on monitor 2. The user uses the PC on monitor 1.
- Do not interrupt navigation, steal input, or reload over unsaved edits.

### Shelved work

The 21-storey HDB block idea is explicitly shelved. Do not start floor repetition,
corridors, lifts, a ground floor, a roof, or a block-instancing refactor as part of
this style task. The earlier recommendation was to model reusable parts in Blender
and assemble floors in Unreal, but this is not the active objective.

## 3. Baseline deliverables and source hierarchy

| Item | Repository location / authority |
| --- | --- |
| Main editable model | `oak-ville.blend` |
| Unreal project | `unreal/OakVille/OakVille.uproject` |
| Unreal main map | `/Game/OakVille/Maps/OakVille` |
| Real-world geometry | `references/original/OAK_VILLE_DIMENSIONED_PLAN.jpg` |
| Original style direction | Locate and read `START_HERE_BLENDER_PROMPT.md`, `STYLE_DIRECTION.md`, and `USER_PRIMARY_STYLE_REFERENCE.png` under the organised references tree |
| Current palette | `assets/styles/minimalist-accents.json`, `palette-editable.json` |
| Current assignments | `assets/styles/accent-assignments.json` |
| Current print | `assets/artwork/mineral-landscape.png`, packed in Blender |
| Lighting profile | `assets/unreal/lighting-profile.json` |
| Designer guidance | `docs/DESIGNER_HANDOFF.md` |
| Style workflow | `docs/RESTYLING.md`, `docs/MINIMALIST_MATERIALS.md` |
| Unreal update guide | `docs/unreal/UPDATE_FROM_BLENDER.md` |
| Walkthrough and limitations | `docs/unreal/README.md` |
| Model drawings / schedules | `docs/drawings/`, `docs/schedules/` |
| Source validation | `docs/validation/` |
| Unreal validation | `docs/unreal/` |

The written dimensioned plan controls geometry. Japandi tour images establish
spaces and connections only. The new tropical video controls aesthetic reference
only. Do not transplant its room sizes, remove a bedroom, or widen this flat to
reproduce a camera shot.

Blender uses metres: X increases right across the plan, Y is negative down the
plan, and finished floor is Z=0. Unreal uses centimetres. Existing scripts perform
the conversion; do not add another scale conversion.

Written dimension chains retained in the model:

| Chain | Segments, mm | Total, mm |
| --- | --- | --- |
| Upper | 3375 + 3000 + 3000 + 3300 | 12675 |
| Left | 4450 + 2800 + 1700 | 8950 |
| Right | 4450 + 1950 + 1250 | 7650 |
| Lower | 1750 + 1750 + 2275 + 1375 + 3950 | 11100 |

These are provisional structural/partition reference datums, not all clear
finished internal dimensions. Ceiling height, several wall/opening dimensions,
services and window details are assumptions documented in `DESIGNER_HANDOFF.md`.
The model supports design coordination; it is not a surveyed fabrication model.

## 4. Reference capture plan

1. Check the actual video-access tools available in the new session. Browser
   access does not automatically guarantee video playback or frame extraction.
2. Watch the tour in sequence if accessible. Note which rooms and details are
   actually shown, and record the exact timestamp of each selected frame.
3. Capture sharp, representative frames: living overview, opposite living view,
   dining, kitchen, bedroom, bathroom, and material/furniture close-ups when shown.
   Do not invent views of rooms absent from the video.
4. Prefer frames without transitions, motion blur or player controls. Keep an
   uncropped reference when useful and record any crops. Avoid treating wide-angle
   camera distortion as evidence of room dimensions.
5. Produce an annotated contact sheet and a short room/material inventory before
   modelling. Tie each important design inference to a frame or label it proposed.
6. If direct capture is blocked, request the video file or user-selected screenshots.
   Do not bypass access restrictions or claim that screenshots exist in advance.

Proposed folders (not created by this documentation task):

```text
references/tropical-modern/ipose-video/
    README.md
    source.json
    frames/
        00m00s_living-overview.jpg
    contact-sheet.jpg
docs/tropical-modern/
    REFERENCE_ANALYSIS.md
    DESIGN_DECISIONS.md
```

The filename above is a format example, not an actual timestamp. The manifest
should record URL, title, attribution, capture date, timestamps, room labels,
observations and confidence. These are third-party design references, not reusable
surface textures. Do not bundle the full video or bulk-upload extracted media to
the remote repository without checking the intended scope and reuse permissions.
Keep attribution alongside any retained reference frames.

## 5. Provisional design hypothesis, pending video review

The earlier suggested palette was deeper timber, pale stone, ivory upholstery,
selective woven details, deep green accents and carefully placed plants. This is
an assistant proposal, **not a verified description of the selected video**.

Use the capture review to establish:

- Timber species appearance, tone, grain direction and proportion of timber surfaces.
- Stone colour, pattern scale and finish; distinguish honed from glossy surfaces.
- Upholstery colours, fabric texture, sofa shape and furniture leg/frame detailing.
- Amount and type of woven material; avoid applying rattan indiscriminately.
- Plant species appearance, scale, placement and relationship to circulation.
- Lighting distribution and daylight character, rather than just warm colour values.
- Artwork, curtains, hardware and cabinet detailing that make the design coherent.

Translate those observations into room-by-room proposals sized to this flat.
Luxury should be expressed through proportion, detailing and material quality;
do not assume it means gold trim, polished marble everywhere or yellow lighting.

## 6. Style separation: required implementation work

Do not simply recolour the current global materials and overwrite the only option.
The existing tools support partial style duplication, but a complete two-style
Blender-to-Unreal workflow has **not** been implemented or validated.

Current collection organisation separates architecture, doors/windows, furniture,
joinery, lighting, decor, collision and walkthrough data. `MINIMALIST_CREAM` groups
the current interior. `scripts/style_controls.py` exposes `duplicate_style`, but
shared wall/floor roles and export identity require additional handling.

Recommended implementation sequence:

1. Add an explicit active-style identifier and a manifest for each option.
2. Keep architecture and plan datums shared. Separate replaceable tropical
   furniture, joinery and decor from the existing minimalist collections.
3. Give tropical materials independent datablocks and stable role names. Include
   wall/floor assignments in style switching, since those objects may be shared.
4. Inspect UUID handling before duplicating objects. Independent design objects
   need unique export IDs; hidden alternatives must not leak into the active export.
5. Make viewport, render, export and collision selection agree on the active style.
6. Keep one selected style active in Unreal initially, unless a separate option map
   is deliberately implemented. In-game style switching is not currently promised.
7. Test a round trip: minimalist -> tropical -> minimalist. Geometry, material
   assignments, artwork, visibility and collision must restore correctly.

Critical pipeline trap: `scripts/unreal/update_from_blender.py` currently runs
`sync_accent_materials.py` whenever `accent-assignments.json` exists. This migration
is minimalist-specific. Make it style-aware before tropical sync, or it may
reapply minimalist roles to the new option.

Preserve stable IDs for edits to an existing object, and preserve unrelated Unreal
material overrides and lighting. Inspect asset deletion rules before switching
styles so an inactive option is not permanently lost during incremental sync.
Do not run the full procedural builder over a manually edited scene merely to restyle it.

## 7. Existing scripts and important technical lessons

| Script | Role |
| --- | --- |
| `scripts/style_controls.py` | Palette editing / partial style duplication |
| `scripts/minimalist_accents.py` | Current coordinated materials |
| `scripts/refine_artwork.py` | Packed landscape print and artwork geometry |
| `scripts/furniture_overhaul.py` | Detailed furniture family construction |
| `scripts/fixture_details.py` | Detailed fixtures |
| `scripts/refresh_furniture_colliders.py` | Refresh furniture collision proxies |
| `scripts/refresh_designer_handoff.py` | Refresh designer documentation |
| `scripts/unreal/export_blender_scene.py` | Saved-source mesh/material export |
| `scripts/unreal/sync_scene.py` | Incremental Unreal update |
| `scripts/unreal/sync_accent_materials.py` | Current intentional role migration / art texture |
| `scripts/unreal/update_from_blender.py` | Normal export, sync and validation command |
| `scripts/unreal/oakville_runtime.py` | Editor Play interaction and movement support |

Known installed baseline: Blender 5.2.1 and Unreal 5.8.2. Recheck executables and
live integrations at the start of implementation rather than assuming they remain
available. Use Blender MCP if available for live changes. Unreal Python remote
scripts are the existing integration; another MCP installation is not a prerequisite.

Normal update, from the repository root, after saving Blender and leaving Unreal
outside Play with its map saved:

```powershell
python scripts/unreal/update_from_blender.py
```

Do not execute this as a tropical-style deployment until the style-selection
changes above are in place. Do not overlap Unreal remote calls; wait for each
asynchronous import/sync to complete before validation or another mutation.

Blender procedural shader graphs do not transfer directly to Unreal. Recreate
roles with Unreal material instances and bake/export textures where appropriate.
The existing art export preserves loop UVs; the Unreal artwork master is matte and
two-sided. The missing painting issue was resolved and the user confirmed seeing
it in both applications. Keep that fix when adding a new option.

There was also accidental multi-object Edit Mode geometry drift during user
navigation. It was restored with user confirmation in v0.10.3. Run object/data
mutations in Object Mode and check actual mesh dimensions, not just object scale.
Do not restore an old model over new user edits without identifying their intent.

## 8. Movement, collision and circulation constraints

- User height is **1.72 m** (the original `1.72cm` message was interpreted accordingly).
- Desktop walkthrough, not VR. Human mode is default.
- Native Unreal CharacterMovement / First Person input underpin movement.
- Walk 180 cm/s; hold either Shift to run at 320 cm/s; release restores walking.
- Space jumps; gravity scale 1. Capsule radius 25 cm, half-height 86 cm.
- Approximate standing eye height 160 cm; horizontal field of view 65 degrees.
- E operates interior doors. Front door remains closed and locked.
- G toggles creative flight; no custom F-key controls. Creative mode may bypass
  collision intentionally; human mode must not.
- Spawn faces into the flat with level pitch. Respect the plan's door handedness,
  especially the corrected inward-opening main-bedroom door.

The prior Shift fault was camera displacement/component reconstruction, not a
reason to disable collision. The dedicated capsule-centred camera and runtime
speed assignment fix were user-confirmed. Do not reintroduce editor property
notifications on Shift or attach the camera back to the displaced template mesh.

Keep Bedroom 3's corrected bed access, the dining-to-kitchen route, and all door
sweeps clear. Rebuild appropriate collision after furniture shape/placement changes.
Decorative trim should not produce unnecessary blocking volumes. Plants must clear
chairs; bedside tables must not overlap beds. Evaluate both appearance and capsule
access, not just a top-down visual gap.

The walkthrough currently relies on editor Python for E/G, running and camera setup.
It is not a packaged game. A standalone build requires porting those interactions
to Blueprint/C++ and rechecking the installed packaging toolchain. Bath/yard folding
doors remain documented swing proxies rather than complete folding mechanisms.

## 9. Validation and visual review

The latest completed baseline verification reported 868 exported meshes,
224752 triangles, 19 lights, 8 doors and 361 Blender collision proxies. These are
baseline counts, not acceptance targets for the new style. Some older documents
still contain earlier counts; use report contents and version context.

Baseline dimensions, all 11 routes, furniture/door checks, reopened Blender file
and Unreal bounds/collision checks passed. They must be regenerated for changed
geometry; an old passing JSON file is not proof of a new option.

For each completed tropical milestone:

1. Save the visible Blender session without discarding user edits; pack required
   textures and use relative paths.
2. Check dimensions and room topology. Refresh furniture collision and designer
   schedules when the furnishing footprint changes.
3. Reopen the saved file separately for verification without replacing the user's
   interactive session. Check missing textures, mesh integrity and active-style export.
4. Sync Unreal outside Play, wait for completion and inspect material assignment,
   bounds and collision reports.
5. Review matching human-eye views of living, dining, kitchen, bedrooms, bathrooms
   and window-facing areas. Reject missing/checkered textures, clipped highlights,
   yellow casts, floating fittings and furniture intersections.
6. Exercise E doors, locked entry, normal walking, Shift press/release near walls,
   jump/landing and G return to human mode if relevant code or collision changed.
7. Verify the minimalist option still restores correctly before committing the
   first release that adds tropical style support.

Existing useful evidence: `docs/validation/reopened-file-validation.json`,
`reopened-routes.json`, `material-visual-review.json`, and
`docs/unreal/scene-validation.json`. Inspect script entry points before executing
checks; some require Blender or Unreal rather than ordinary Python.

## 10. Milestones, files and delivery

Suggested milestones:

1. Reference frames, contact sheet and verified design analysis.
2. Reversible style selection and a living/dining pilot for visual review.
3. Remaining room furniture, joinery, fixtures and decor.
4. Unreal material/lighting matching and full walkthrough validation.

Keep source scripts in `scripts/`, reusable assets in `assets/`, review renders in
`renders/`, and decision/validation records in `docs/`. Clearly separate source
references from generated assets. Keep temporary captures and caches ignored.
Do not remove existing reference files or unrelated work while organising folders.

At handover preparation, Git was clean on `master`, aligned with `origin/master`.
The prior v0.10.3 delivery uploaded 881 LFS objects successfully. This is historical
evidence; check current status again before the next change.

Repository instructions require committing and pushing every completed validated
change to `origin/master`. Preserve unrelated edits; no force pushes, history
rewrites, tags or releases. Keep main Blender and Unreal binaries tracked by LFS.
Audit LFS for current project objects rather than automatically uploading all history.

Documentation-only handover: no application version bump. A new functioning second
style is a MINOR capability (normally 0.11.0 if 0.10.3 is still current); fixes and
polish are PATCH. Inspect pending changes/version history before choosing a number.
Ask before a MAJOR bump. Include corresponding changelog and version changes in
implementation commits, using conventional subjects with detailed validation bodies.

## 11. First actions for the next session

1. Read this document, root `AGENTS.md`, the original project prompts and the linked
   designer/restyling/update guides. Inspect Git and live application state.
2. Check video access and capture representative frames from the selected tour.
3. Produce a concise, source-grounded material/furniture analysis, marking proposals
   separately from observed details and identifying any missing room references.
4. Inspect style duplication, UUID/export filters, material migration and deletion
   handling. Establish reversible options before editing the current design.
5. Build the tropical living/dining pilot in Blender and sync the corresponding
   option to Unreal, preserving the dimensioned shell and existing minimalist style.

No tropical geometry, textures, video frames or new Unreal option have been created
by this handover task. No HDB block work is authorised by this document.
