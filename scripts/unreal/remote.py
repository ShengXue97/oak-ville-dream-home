"""Run a project script in the open Unreal editor via Epic's localhost bridge."""

import argparse
import importlib.util
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
parser = argparse.ArgumentParser()
parser.add_argument("script", type=Path)
parser.add_argument(
    "--engine", type=Path, default=Path("C:/Program Files/Epic Games/UE_5.8")
)
args = parser.parse_args()
bridge_path = (
    args.engine
    / "Engine/Plugins/Experimental/PythonScriptPlugin/Content/Python/remote_execution.py"
)
spec = importlib.util.spec_from_file_location("epic_remote_execution", bridge_path)
bridge = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bridge)
session = bridge.RemoteExecution()
session.start()
try:
    deadline = time.monotonic() + 10
    while time.monotonic() < deadline:
        nodes = [
            node
            for node in session.remote_nodes
            if node.get("project_name") == "OakVille"
        ]
        if nodes:
            break
        time.sleep(0.2)
    if len(nodes) != 1:
        raise RuntimeError(
            f"Expected one OakVille editor, discovered: {session.remote_nodes}"
        )
    session.open_command_connection(nodes[0]["node_id"])
    script = args.script.resolve()
    if not script.is_relative_to(ROOT):
        raise ValueError("Only scripts inside the project may be executed")
    result = session.run_command(str(script), raise_on_failure=False)
    print(json.dumps(result, indent=2))
    if not result.get("success"):
        raise SystemExit(1)
finally:
    session.stop()
