"""User-invoked viewport quality controls; does not move the view or save."""

import bpy


def set_preview(quality="FAST"):
    if quality not in {"FAST", "MATERIALS", "LIGHTING"}:
        raise ValueError("Choose FAST, MATERIALS or LIGHTING")
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type != "VIEW_3D":
                continue
            shading = area.spaces.active.shading
            shading.type = "SOLID" if quality == "FAST" else "MATERIAL"
            shading.color_type = "MATERIAL"
            shading.use_scene_lights = quality == "LIGHTING"
            shading.use_scene_world = quality == "LIGHTING"
            area.tag_redraw()
