"""Export the saved Blender model, incrementally sync Unreal, and validate.

Usage from the repository: python scripts/unreal/update_from_blender.py
Requires the OakVille map open and saved in Unreal, outside Play mode.
This command neither launches nor focuses an application.
"""

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--blender",
        type=Path,
        default=Path("C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"),
    )
    parser.add_argument(
        "--engine", type=Path, default=Path("C:/Program Files/Epic Games/UE_5.8")
    )
    args = parser.parse_args()
    if not args.blender.is_file():
        parser.error("Blender executable not found; provide --blender")

    def remote(script):
        subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts/unreal/remote.py"),
                str(ROOT / "scripts/unreal" / script),
                "--engine",
                str(args.engine),
            ],
            cwd=ROOT,
            check=True,
        )

    remote("preflight.py")
    subprocess.run(
        [
            str(args.blender),
            "--background",
            "--python-exit-code",
            "1",
            str(ROOT / "oak-ville.blend"),
            "--python",
            str(ROOT / "scripts/unreal/export_blender_scene.py"),
        ],
        cwd=ROOT,
        check=True,
    )
    report_path = ROOT / "docs/unreal/sync-validation.json"
    previous = report_path.stat().st_mtime_ns if report_path.exists() else 0
    remote("sync_scene.py")
    deadline = time.monotonic() + 600
    while time.monotonic() < deadline:
        if report_path.exists() and report_path.stat().st_mtime_ns != previous:
            try:
                report = json.loads(report_path.read_text())
            except json.JSONDecodeError:
                time.sleep(0.5)
                continue
            if report.get("errors"):
                raise RuntimeError("Sync failed; see docs/unreal/sync-validation.json")
            if report.get("complete"):
                print(
                    f"Geometry: {len(report['updated'])} changed, {len(report['added'])} added, {len(report['unchanged'])} unchanged"
                )
                remote("validate_scene.py")
                if (ROOT / "assets/styles/accent-assignments.json").is_file():
                    remote("sync_accent_materials.py")
                print(
                    "Update complete. Unreal lighting and material overrides were retained."
                )
                return
        time.sleep(1)
    raise TimeoutError(
        "Sync has not finished. It pauses during Play. Check the editor and sync-progress.json before retrying."
    )


if __name__ == "__main__":
    main()
