r"""Minimal repro: Path.home() resolves wrong dir on Windows non-interactive launch.

To reproduce the bug:
    1. Run normally: python broken_app.py
       Creates history at C:\Users\<you>\.cuagent-win\history.json  (correct)
    2. Run from a scheduled task or SYSTEM context:
       schtasks /create /tn "cuagent_test" /tr "python broken_app.py" /sc once /st 00:00
       Creates history at C:\Windows\system32\config\systemprofile\.cuagent-win  (WRONG)
    3. Run normally again:
       History is "gone" because it's reading the user profile, not the system profile

The single-instance mechanism (show-signal) was Codex's attempted fix, but it only
prevents duplicate launches -- it doesn't fix the wrong-directory root cause.
"""

from __future__ import annotations

import json
import logging
import os
import time
from pathlib import Path

logger = logging.getLogger(__name__)

# BUG: Path.home() is evaluated at import time. On Windows, when launched from
# a scheduled task, SYSTEM context, or .bat with unusual env, Path.home() may
# resolve to a service profile directory instead of the interactive user's home.
_DATA_DIR = Path.home() / ".cuagent-win"
_HISTORY_PATH = _DATA_DIR / "history.json"
_SETTINGS_PATH = _DATA_DIR / "settings.json"
# Codex's attempted fix: signal file for single-instance. This prevents
# duplicate launches but doesn't fix the wrong directory.
_SHOW_SIGNAL = _DATA_DIR / "show.signal"


def _is_already_running() -> bool:
    """Codex's single-instance check (doesn't fix the real bug)."""
    try:
        import psutil
        my_pid = os.getpid()
        for p in psutil.process_iter(["pid", "name", "cmdline"]):
            info = p.info
            if info["pid"] == my_pid:
                continue
            if info["name"] and "python" in info["name"].lower():
                cmdline = " ".join(info["cmdline"] or [])
                if "broken_app" in cmdline:
                    return True
    except Exception:
        pass
    return False


def launch_app() -> None:
    # Codex's single-instance guard
    if _is_already_running():
        _DATA_DIR.mkdir(parents=True, exist_ok=True)
        _SHOW_SIGNAL.write_text("show")
        print("Another instance is running - sent show signal")
        return

    _DATA_DIR.mkdir(parents=True, exist_ok=True)

    # Write sample history
    if not _HISTORY_PATH.exists():
        sample = [{"task": "test task", "timestamp": time.time(), "success": True}]
        _HISTORY_PATH.write_text(json.dumps(sample))

    # Show where data is stored
    print(f"Path.home()    = {Path.home()}")
    print(f"USERPROFILE    = {os.environ.get('USERPROFILE', '(not set)')}")
    print(f"_DATA_DIR      = {_DATA_DIR}")
    print(f"History exists = {_HISTORY_PATH.exists()}")

    if _HISTORY_PATH.exists():
        history = json.loads(_HISTORY_PATH.read_text())
        print(f"History items  = {len(history)}")
    else:
        print("History items  = 0 (FILE NOT FOUND)")


if __name__ == "__main__":
    launch_app()
