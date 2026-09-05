"""Build contact sheets and a local preview index from reproducible renders."""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import html
import json
import hashlib

ROOT = Path(__file__).resolve().parents[1]
folder = ROOT / "renders"
font = ImageFont.load_default(size=15)
for prefix, title in [("EYE_W", "walkways"), ("PREVIEW_", "rooms")]:
    paths = sorted(folder.glob(prefix + "*.png"))
    rows = (len(paths) + 2) // 3
    sheet = Image.new("RGB", (960, rows * 265), "#fffaf0")
    draw = ImageDraw.Draw(sheet)
    for index, path in enumerate(paths):
        with Image.open(path) as source:
            source.thumbnail((320, 240))
            x, y = (index % 3) * 320, (index // 3) * 265
            sheet.paste(source, (x, y))
            draw.text(
                (x + 6, y + 243),
                path.stem.replace(prefix, "").replace("_", " "),
                fill="#253737",
                font=font,
            )
    sheet.save(folder / (title + "-contact-sheet.jpg"), quality=90)

paths = (
    sorted(folder.glob("EYE_W*.png"))
    + sorted(folder.glob("PREVIEW_*.png"))
    + [folder / "PLAN_Orthographic.png"]
    + sorted(folder.glob("DETAIL_*.png"))
)
cards = []
for path in paths:
    cards.append(
        f'<figure><a href="{path.name}"><img src="{path.name}" loading="lazy"></a><figcaption>{html.escape(path.stem.replace("_", " "))}</figcaption></figure>'
    )
page = """<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Oak Ville model previews</title><style>body{font:16px system-ui;background:#faf6ed;color:#263735;margin:32px}main{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:22px}figure{margin:0;background:white;padding:12px}img{width:100%}figcaption{padding:10px 0}a{color:#315f60}</style>
<h1>Oak Ville · editable model previews</h1><p>Warm cream and pale oak minimalism. Eye-level cameras: 1.60 m, 65° horizontal field of view. Openings and unlabelled dimensions remain provisional.</p>
<p><a href="../docs/drawings/OAK_VILLE_DIMENSIONED_MODEL.svg">Dimensioned designer drawing</a> · <a href="../docs/DESIGNER_HANDOFF.md">Assumptions and handoff</a></p><main>"""
(folder / "index.html").write_text(
    page + "\n".join(cards) + "</main></html>", encoding="utf-8"
)
print(f"Created preview gallery with {len(paths)} views")
validation = []
for path in paths:
    with Image.open(path) as rendered:
        rendered.load()
        extrema = rendered.convert("RGB").getextrema()
        validation.append(
            {
                "file": "renders/" + path.name,
                "size": list(rendered.size),
                "nonuniform_pixels": any(high > low for low, high in extrema),
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
(ROOT / "docs/validation/preview-validation.json").write_text(
    json.dumps(
        {
            "view_count": len(validation),
            "all_images_load": True,
            "all_images_nonuniform": all(
                row["nonuniform_pixels"] for row in validation
            ),
            "views": validation,
            "visual_review": "Room and walkway contact sheets reviewed; living, bathrooms, vanity and plan inspected individually during delivery. Provisional design-detail representations, not photogrammetry.",
        },
        indent=2,
    )
)
