"""Copy Epic's installed First Person template dependencies into this project.

Preserve their /Game mount paths so native Blueprint references remain valid.
Existing destination files are never overwritten. No template maps are copied.
"""

import argparse
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument(
    "--engine", type=Path, default=Path("C:/Program Files/Epic Games/UE_5.8")
)
args = parser.parse_args()
content = ROOT / "unreal/OakVille/Content"
sources = {
    "FirstPerson/Blueprints": args.engine
    / "Templates/TP_FirstPersonBP/Content/FirstPerson/Blueprints",
    "FirstPerson/Anims": args.engine
    / "Templates/TP_FirstPersonBP/Content/FirstPerson/Anims",
    "Input": args.engine / "Templates/TemplateResources/High/Input/Content",
    "Characters": args.engine / "Templates/TemplateResources/High/Characters/Content",
}
copied = 0
for folder, source in sources.items():
    if not source.is_dir():
        raise FileNotFoundError(source)
    for path in source.rglob("*"):
        if not path.is_file():
            continue
        destination = content / folder / path.relative_to(source)
        if not destination.exists():
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, destination)
            copied += 1
print(f"Copied {copied} template assets without overwriting existing content")
