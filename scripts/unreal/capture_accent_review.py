"""Capture the material update without moving the user's editor viewport."""

import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "accent_capture", Path(__file__).with_name("capture_lighting_review.py")
)
capture = importlib.util.module_from_spec(spec)
spec.loader.exec_module(capture)
capture.VIEWS = [
    ("living_art", (245, 320, 160), (60, 185, 120)),
    ("dining", (580, 610, 150), (445, 490, 110)),
]
capture.run("accents")
