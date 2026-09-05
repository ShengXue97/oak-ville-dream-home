# Minimalist / tropical modern

In Unreal **Play**, press **T** once to switch styles. The on-screen label shows
the active option. Press T again to return. Holding the key does not cycle.
Switching takes effect in place without moving the player or reloading the map.
Leaving Play discards the comparison; the next session starts with the style
last saved in Blender and synchronized to Unreal.

In the current Blender session, open the 3D View sidebar with **N**, choose
**Oak Ville**, then click **Minimalist** or **Tropical modern**. After restarting
Blender, run the embedded `STYLE_SWITCH.py` text once to register the panel.
This does not require enabling automatic Python execution. Save normally to
retain the selected option. The delivered file starts in minimalist mode.

Run `python scripts/unreal/update_from_blender.py` after saving Blender to update
the saved Unreal default. The command exports both palettes and the selected
style. The original minimalist materials and independent `TROPICAL_MODERN__*`
materials remain available. The usual preflight requires a saved Unreal map
outside Play; the update preserves custom overrides and lighting.

The tropical option uses warm teak-like timber, sand limestone-like flooring,
ivory upholstery, olive textiles, cognac accents and darker bronze hardware.
These are editable design approximations, not specified commercial products.
Both options share the existing detailed furniture, plants, original landscape
artwork and apartment shell. No dimensions, furniture footprints, door pivots,
routes, collision proxies or lighting settings change with the selector.
This first release implements the finish comparison; replacement furniture and
botanical artwork remain future design work.

Edit the tropical materials directly in Blender's Shader Editor, or their
Unreal material instances. Their node trees are independent of the minimalist
originals. `assets/styles/TROPICAL_MODERN.json` defines their initial creation;
rerunning preparation preserves subsequent designer edits instead of resetting
them. Existing Unreal material instances likewise retain edits during sync.
Unreal's procedural surface approximation does not reproduce every Blender node.

Objects store their two material-slot lists in `oakville_style_slots`.
`scene['active_style']` stores the saved selection. New objects can be registered
by rerunning `style_switch.prepare()`; assign their intended original materials
first. If material slots are added or removed, explicitly review/update that
object's mapping before switching. Unknown material assignments are retained.
Object geometry is never duplicated for this finish option, so there is no
inactive alternative geometry to export or accidentally delete.

Validation: `docs/validation/style-switch.json`,
`docs/unreal/style-switch-validation.json`, and
`docs/unreal/style-input-validation.json`. The input check exercises the actual
T press/hold/release handler through its key-state adapter, not OS keystrokes.
Existing dimensions and route checks run during the normal export. Reproduce
matching Blender views with `scripts/render_style_previews.py` in background
Blender; generated images are under `renders/styles/`.

Like the existing E/G controls, the T shortcut uses **editor Python**. It is
available in the editor Play walkthrough; a packaged executable needs a native
Blueprint/C++ implementation.
