# Coordinated material variation

The user's Singapore BTO references guide the material balance: cream walls,
natural timber furniture and joinery, coherent upholstery, layered textiles and
restrained accents. They do not replace the dimensioned Oak Ville floor plan.

The sofa remains consistently cream. Variation comes from honey-oak dining and
vanity fronts, flax rugs and headboards, muted sage or clay folded bed throws,
coordinated chair upholstery and a deep olive ceramic planter. A warmer natural-oak
floor family provides broad material contrast against cream walls. Architecture
and calibrated lighting retain their established roles.

Edit `assets/styles/minimalist-accents.json` and run
`scripts/minimalist_accents.py` in Blender Object Mode. Role materials are copied
from existing textured shaders so grain and fabric detail remain editable.
`scripts/refine_artwork.py` installs the packed print within the existing frames.
The artwork is a matte print, not a light source.

The print is stored at `assets/artwork/mineral-landscape.png`. It was created with
the built-in image-generation tool for this project. The prompt requested an
original gallery-quality abstract landscape on textured ivory paper, layered
mineral pigment, pale limestone and sand, olive-grey and restrained sienna,
fine charcoal lines, negative space and dry-brush washes, with no frame, text
or signature. It is not a photograph or third-party artwork reproduction.

After saving Blender, use `scripts/unreal/update_from_blender.py`, which also runs
`scripts/unreal/sync_accent_materials.py`. The explicit material migration
retains unrelated custom overrides. UVs for the two artwork meshes travel with
the export; ordinary mesh UV generation is unchanged.

Reproduce preview images with `scripts/render_accent_previews.py` using the saved
model in background Blender. Generated previews live in `renders/accents/`.
