"""Record matched preview brightness and near-white clipping, without editing images."""

import json
from pathlib import Path

from PIL import Image, ImageStat

ROOT = Path(__file__).resolve().parents[2]
rows = {}
for view in ("dining", "living_window", "bedroom_window", "corridor"):
    rows[view] = {}
    for stage in ("before", "final"):
        path = ROOT / "renders/unreal/lighting" / stage / f"{view}.png"
        with Image.open(path).convert("RGB") as image:
            mean = ImageStat.Stat(image).mean
            clipped = sum(min(pixel) >= 250 for pixel in image.get_flattened_data())
            rows[view][stage] = {
                "mean_rgb_8bit": [round(value, 2) for value in mean],
                "near_white_pixel_percent": round(
                    100 * clipped / (image.width * image.height), 3
                ),
            }
report = {
    "note": "Whole-image measurements, not a perceptual quality score. Near-white means all RGB channels >=250/255. Both stages use identical capture cameras.",
    "views": rows,
}
(ROOT / "docs/unreal/lighting-image-comparison.json").write_text(
    json.dumps(report, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(report, indent=2))
