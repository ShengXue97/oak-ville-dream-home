# Changing the interior style

The building shell and dimensions are in `Architecture`; openings and hinged leaves are in `Doors_Windows`. Current furniture, joinery, lighting and decor are grouped beneath `MINIMALIST_CREAM`. They are not merged into the building.

For a palette change, edit the shared role in Material Properties or the Shader Editor: `Wall_Paint`, `Floor_Main`, `Oak_Joinery`, `Cabinet_Front`, `Countertop`, `Fabric_Main`, `Fabric_Oatmeal`, `Wet_Tile`, `Sheer_Linen`. Textured materials use the clearly named `EDIT_PALETTE` Color Ramp. Oak flooring also has the `Oak_Planks_1200x180mm` Brick node; edit its two plank colours for a floor colour change. Roughness remains on the Principled shader. No reference photo is used as a surface texture.

`assets/styles/palette-editable.json` is exported from the actual material nodes. Duplicate it, adjust values, and call `apply_palette` in `scripts/style_controls.py` from Blender's Python Console. Colours are scene-linear RGBA. This affects shared materials throughout the flat and does not change geometry. The floor's Brick node remains directly editable in the Shader Editor.

For an alternative furnishing scheme, call `duplicate_style('DESIGN_OPTION_B')`. It creates independent mesh/light data beneath a new, initially hidden collection. Switch the original and alternative collections' viewport and render visibility together. Make a material single-user before changing only one option's material. Walls keep their shared roles; use a separate saved `.blend` for comparing whole-flat wall/floor palettes.

Keep door apertures and collision routes visible while designing. After changes, regenerate the component schedule/collision proxies and rerun the validation scripts. The supplied collisions describe the delivered layout and do not automatically update after furniture moves. Do not run the full builder over a manually edited scene to restyle it.

Light objects have purpose/room names and a `design_temperature_kelvin` property. The initial 2900 K artificial and 6500 K daylight labels describe approximate tints, not measured photometric fixtures. Adjust Color, Power and Size in Light Properties; obtain actual fixture specifications for construction drawings. Emissive appearance and real-world lux calculations are not established by this model.
