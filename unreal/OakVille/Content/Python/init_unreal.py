"""Automatically enable Oak Ville editor Play controls when this project opens."""

import sys
from pathlib import Path

scripts = Path(__file__).resolve().parents[4] / "scripts/unreal"
if str(scripts) not in sys.path:
    sys.path.insert(0, str(scripts))
import oakville_runtime

oakville_runtime.install()
