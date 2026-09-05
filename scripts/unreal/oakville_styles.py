"""Material-only style switching shared by editor sync and Play controls."""

import re
import unreal

MINIMALIST = "MINIMALIST_CREAM"
TROPICAL = "TROPICAL_MODERN"
LABELS = {MINIMALIST: "Minimalist", TROPICAL: "Tropical modern"}


def asset_path(role):
    return "/Game/OakVille/Materials/MI_" + re.sub(r"[^a-zA-Z0-9_]", "_", role)


class StyleSession:
    def __init__(self, actors, data):
        self.active = data.get("active_style", MINIMALIST)
        self.bindings = []
        self.custom_overrides = []
        self.errors = []
        by_id = {
            str(tag).removeprefix("BlenderID:"): actor
            for actor in actors for tag in actor.tags
            if str(tag).startswith("BlenderID:")
        }
        cache = {}
        for record in data["objects"]:
            roles = record.get("style_materials")
            if not roles or roles[MINIMALIST] == roles[TROPICAL]:
                continue
            actor = by_id.get(record["source_id"])
            component = actor.get_component_by_class(unreal.StaticMeshComponent) if actor else None
            if component is None:
                self.errors.append(record["name"] + ": missing component")
                continue
            variants = {}
            for style, role in roles.items():
                if role not in cache:
                    cache[role] = unreal.load_asset(asset_path(role))
                variants[style] = cache[role]
            if not all(variants.values()):
                self.errors.append(record["name"] + ": missing style material")
                continue
            current = component.get_material(0)
            if current not in variants.values():
                self.custom_overrides.append(record["name"])
                continue
            self.bindings.append((component, variants))
        if self.errors:
            raise RuntimeError("Style preflight failed: " + "; ".join(self.errors[:10]))

    def apply(self, style):
        if style not in LABELS:
            raise ValueError("Unknown style: " + str(style))
        # Material slots only: no mesh reconstruction, transforms or collision edits.
        previous = [(component, component.get_material(0)) for component, _ in self.bindings]
        try:
            for component, variants in self.bindings:
                component.set_material(0, variants[style])
                if component.get_material(0) != variants[style]:
                    raise RuntimeError("Style assignment did not stick")
        except Exception:
            for component, material in previous:
                component.set_material(0, material)
            raise
        self.active = style
        return len(self.bindings)

    def toggle(self):
        return self.apply(TROPICAL if self.active == MINIMALIST else MINIMALIST)
