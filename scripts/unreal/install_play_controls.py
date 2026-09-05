"""Refresh the controls in the open editor; no restart or focus change needed."""

import importlib
import sys
from pathlib import Path
import unreal

if unreal.get_editor_subsystem(unreal.LevelEditorSubsystem).is_in_play_in_editor():
    raise RuntimeError("Stop Play before updating controls")
directory = str(Path(__file__).resolve().parent)
if directory not in sys.path:
    sys.path.insert(0, directory)
import oakville_runtime

oakville_runtime.uninstall()
importlib.reload(oakville_runtime)
oakville_runtime.install()
