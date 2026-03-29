"""Original code (Codex, 5a1304e, Mar 18): Path.home() hardcoded, no guards.

This is what Codex first wrote. Data dir is resolved at import time via
Path.home(). No single-instance mechanism, no USERPROFILE fallback.

Codex then added _is_already_running() and _SHOW_SIGNAL in ae49aa8 (see
broken_app.py) to prevent the "disappeared window" bug on relaunch, but
never fixed the root cause (wrong directory).
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path

# Original: Path.home() at import time, no env var fallback
_DATA_DIR = Path.home() / ".cuagent-win"
_HISTORY_PATH = _DATA_DIR / "history.json"
_SETTINGS_PATH = _DATA_DIR / "settings.json"
# No _SHOW_SIGNAL, no _is_already_running — those were added later


def launch_app() -> None:
    """Original launch_app: no single-instance check, no path sync."""
    _DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not _HISTORY_PATH.exists():
        sample = [{"task": "test task", "timestamp": time.time(), "success": True}]
        _HISTORY_PATH.write_text(json.dumps(sample))

    print(f"Path.home()    = {Path.home()}")
    print(f"USERPROFILE    = {os.environ.get('USERPROFILE', '(not set)')}")
    print(f"_DATA_DIR      = {_DATA_DIR}")
    print(f"History exists = {_HISTORY_PATH.exists()}")
    print()
    print("On Windows scheduled task, Path.home() may differ from USERPROFILE.")
    print("If they differ, history written by the interactive user is invisible")
    print("to the scheduled-task launch and vice versa.")


if __name__ == "__main__":
    launch_app()
