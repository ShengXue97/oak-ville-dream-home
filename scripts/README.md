# Project scripts

Run commands from the project root. Blender supplies `bpy`; ordinary Python is sufficient for the preview gallery and folder validation. Code uses four-space indentation.

| Purpose | Scripts |
|---|---|
| Main build entry point | `build_oak_ville.py` |
| Ordered construction stages | `02_doors_routes.py`, `03_furnish.py`, `04_materials_lighting.py`, `05_walkthrough.py` |
| Build helpers and drawing/schedule export | `fixture_details.py`, `designer_documents.py` |
| Interactive controls | `door_states.py`, `style_controls.py`, `preview_controls.py` |
| Geometry and saved-file checks | `validate_model.py`, `reopen_validate.py`, `compare_reproduction.py` |
| Render and gallery generation | `render_previews.py`, `preview_gallery.py` |
| Folder and reference integrity | `validate_project_layout.py` |

The numbered stages and geometry validators use the main builder's namespace; they are not independent command-line entry points. See [the walkthrough guide](../docs/WALKTHROUGH.md) for supported commands. Reproduction test models belong in `.cache/`, never among original references.

Optional gallery dependency: Pillow (validated with 12.3.0). Black is an optional formatter, not a modelling dependency. No downloaded furniture or texture package is required.
