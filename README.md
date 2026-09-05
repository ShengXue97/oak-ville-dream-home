# Oak Ville ? editable Blender project

Current project version: **0.8.0**. Open [oak-ville.blend](oak-ville.blend).

The [Unreal desktop walkthrough](unreal/OakVille/OakVille.uproject) lives in this repository. See the [Unreal guide](docs/unreal/README.md) and [Blender update workflow](docs/unreal/UPDATE_FROM_BLENDER.md).

| Folder | Contents |
|---|---|
| [references/original/](references/original/README.md) | Supplied plans, briefs, style photographs and tour screenshots, with the original gallery and manifest. |
| [scripts/](scripts/README.md) | Blender construction, editing, rendering and validation scripts. |
| [assets/styles/](assets/styles/) | Editable material palettes and style presets authored for this project. |
| [docs/](docs/README.md) | Designer handoff, restyling and walkthrough guides. |
| [docs/drawings/](docs/drawings/) | Generated dimensioned model drawing. |
| [docs/schedules/](docs/schedules/) | Generated room, furniture, door and camera CSV schedules. |
| [docs/validation/](docs/validation/) | Dimension, route, reproduction and file-integrity evidence. |
| [renders/](renders/index.html) | Generated model previews and contact sheets; reproducible and ignored by Git. |
| `.cache/` | Disposable reproduction files and tool caches; ignored by Git. |

Start with the [designer handoff](docs/DESIGNER_HANDOFF.md), [validation report](docs/VALIDATION_REPORT.md), [walkthrough guide](docs/WALKTHROUGH.md) and [restyling guide](docs/RESTYLING.md).

The [dimensioned plan](references/original/OAK_VILLE_DIMENSIONED_PLAN.jpg) controls geometry. The [primary style image](references/original/USER_PRIMARY_STYLE_REFERENCE.png) and [style direction](references/original/STYLE_DIRECTION.md) control the warm cream-and-oak minimalist interior. Tour images establish room connections. The [original brief](references/original/START_HERE_BLENDER_PROMPT.md) remains with the source pack.

The model is a dimensioned design reference with documented assumptions; site measurements are needed before fabrication. Architecture, furnishings and shared material roles remain separately editable. Use Solid shading for responsive navigation. Blender Walk Navigation does not block walls or furniture; supplied collision proxies support later engine integration.

See the walkthrough guide for reproduction commands. Keep the main model at the root, use relative paths, and pack required images. Git LFS tracks `.blend` files. VERSION and CHANGELOG.md describe the release history.
