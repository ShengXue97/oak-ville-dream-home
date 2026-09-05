# Unreal lighting calibration

The warm cream-and-oak Blender model is the visual reference. Unreal uses a
separate, explicit renderer calibration in `assets/unreal/lighting-profile.json`.
The previous profile gave all 19 area lights 350 lumens and a 280 cm range;
ceiling warmth dominated the interior while the 2500 lux sun produced strong
white patches on bedding near windows.

The current profile separates broad neutral window light, near-neutral ceiling
fill, restrained warm cove light and local task light. Ceiling powers vary by
room. The direct sun is reduced to 300 lux with a 5-degree source angle, as an
art-directed soft-daylight preview. These values are not a physical daylight
survey or a luminaire specification for construction. Source names retain their
original Blender labels for stable identity; a `2900K` suffix does not describe
the calibrated Unreal RGB colour.

Exposure is fixed at legacy luminance 12 (not EV100), white balance at 6500 K,
bloom at 0.025, with lens flare and vignette disabled. Local highlight contrast
is 0.75 and shadow contrast 0.85; material saturation is not globally removed.
This follows the controls described in [Epic's exposure documentation](https://dev.epicgames.com/documentation/unreal-engine/auto-exposure-in-unreal-engine).

## Apply and reproduce

1. Save edits and stop Play in the OakVille map.
2. Edit `assets/unreal/lighting-profile.json` if a new calibration is needed.
3. Run `python scripts/unreal/remote.py scripts/unreal/tune_lighting.py`.
4. Run `python scripts/unreal/remote.py scripts/unreal/validate_lighting.py`.
5. For matched captures, run
   `python scripts/unreal/remote.py scripts/unreal/capture_lighting_review.py`.
   Wait for completion before starting another capture or changing the lights.

Captures appear in `renders/unreal/lighting/<label>/`, which is ignored because
it is reproducible. The saved before/final comparisons use identical cameras.
The script captures dining, living window, Bedroom 3 window, corridor and a
dining/kitchen view without moving the editor viewport or taking desktop focus.
Scene captures have separate temporal history and can show more grain than a
settled player viewport. Judge the saved level in Play as well.

`scripts/embed_unreal_lighting_profile.py` embeds the profile as a Blender text
block and records its relative path. The build includes this step. It does not
change Blender lights: the renderer-specific translation belongs in Unreal.
Ordinary `update_from_blender.py` geometry updates preserve these light settings,
material overrides, and exposure. E doors, G creative mode, Shift running and
collision configuration are unaffected by this lighting pass.

Current Unreal furniture contains the curved table supports and separate chair
back details from the Blender overhaul. The submitted Unreal screenshot showed
the earlier furniture shapes. Fresh captures verify the current geometry.

Unreal's role-based procedural shaders and tone mapping do not exactly reproduce
Blender's node graphs/AgX. Wood grain remains a simplified shader; exterior
scenery is not modelled. The flat's measured geometry is unchanged.

## Validation evidence

Five final views were inspected. The four matching before/final views are
measured by `measure_lighting_previews.py` (Pillow required), with results in
`lighting-image-comparison.json`. Near-white pixels (all RGB channels >=250)
fell from 3.261% to 0% in Bedroom 3, and from 1.568% to 0% in the living-window
view. Whole-image colour differences include materials and are not a universal
quality score. Dining shadows are visibly more readable, while cream and oak
retain their intended warmth.

The saved `.blend` passed reopening, dimensions, furniture/swing and 11-route
checks. A complete export/sync retained all 773 meshes with zero geometry
changes. Lighting integrity checks confirmed assigned materials and 88
architectural collision bodies; this pass does not establish the cause of the
previous intermittent collision report.
