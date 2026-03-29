r"""Fixed version: proper data dir resolution for Windows.

The fix has two parts:
1. data_dir.py -- resolve data directory from CUAGENT_DATA_DIR or USERPROFILE
2. _sync_storage_paths() -- re-resolve at launch time, not import time
"""

from __future__ import annotations

import json
import os
import time
from pathlib import Path


# ── data_dir.py (new module) ─────────────────────────────────────────

def cuagent_data_dir() -> Path:
    """Resolve the per-user cuagent data directory.

    REASON: On Windows, Path.home() can resolve to a service/system profile when
    the GUI is started from a scheduled task or non-interactive context, while
    operators (and redeploy.ps1) expect data under C:\\Users\\<user>\\.cuagent-win.
    USERPROFILE usually matches the interactive account; CUAGENT_DATA_DIR allows
    the launcher to pin an explicit path so history/logs stay visible and consistent.
    """
    override = os.environ.get("CUAGENT_DATA_DIR", "").strip()
    if override:
        return Path(override).expanduser()
    if os.name == "nt":
        profile = os.environ.get("USERPROFILE", "").strip()
        if profile:
            return Path(profile) / ".cuagent-win"
    return Path.home() / ".cuagent-win"


# ── Module-level paths (set at import, re-resolved at launch) ────────

_DATA_DIR = cuagent_data_dir()
_HISTORY_PATH = _DATA_DIR / "history.json"
_SETTINGS_PATH = _DATA_DIR / "settings.json"
_SHOW_SIGNAL = _DATA_DIR / "show.signal"


def _sync_storage_paths() -> None:
    """Re-resolve data paths from env at process start.

    REASON: Module-level paths are set at import time; launch_app calls this so the
    running app matches the launcher bat even if import order ever changes.
    """
    global _DATA_DIR, _HISTORY_PATH, _SETTINGS_PATH, _SHOW_SIGNAL
    _DATA_DIR = cuagent_data_dir()
    _HISTORY_PATH = _DATA_DIR / "history.json"
    _SETTINGS_PATH = _DATA_DIR / "settings.json"
    _SHOW_SIGNAL = _DATA_DIR / "show.signal"


# ── App ──────────────────────────────────────────────────────────────

def launch_app() -> None:
    _sync_storage_paths()
    _DATA_DIR.mkdir(parents=True, exist_ok=True)

    if not _HISTORY_PATH.exists():
        sample = [{"task": "test task", "timestamp": time.time(), "success": True}]
        _HISTORY_PATH.write_text(json.dumps(sample))

    print(f"Path.home()       = {Path.home()}")
    print(f"USERPROFILE       = {os.environ.get('USERPROFILE', '(not set)')}")
    print(f"CUAGENT_DATA_DIR  = {os.environ.get('CUAGENT_DATA_DIR', '(not set)')}")
    print(f"Resolved data dir = {_DATA_DIR}")
    print(f"History exists    = {_HISTORY_PATH.exists()}")

    if _HISTORY_PATH.exists():
        history = json.loads(_HISTORY_PATH.read_text())
        print(f"History items     = {len(history)}")


if __name__ == "__main__":
    launch_app()
