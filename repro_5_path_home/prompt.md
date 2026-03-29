# Prompt sent to Codex (2 attempts, never found root cause)

> Our Windows desktop app stores data at `Path.home() / ".cuagent-win"`. When
> launched from a `.bat` file or scheduled task, `Path.home()` sometimes resolves
> to a system profile directory (e.g. `C:\Windows\system32\config\systemprofile`)
> instead of the user's actual home. History and settings disappear. The app also
> "disappears" when the launcher kills and restarts the process. Fix both issues.

## Context given

- `broken_app.py` in this directory
- Windows-only issue; macOS works fine with `Path.home()`
- The `.bat` launcher runs `pythonw broken_app.py` which may inherit a different env
- Users deploy via `redeploy.ps1` which kills the old process and starts a new one

## What Codex tried (2 commits, Mar 20)

1. **ae49aa8**: Added `_SHOW_SIGNAL` file + `_is_already_running()` single-instance
   mechanism via psutil. This prevents kill+restart from losing window state, but
   doesn't fix the path resolution issue at all.

2. **502e87d**: Added `_get_version_str()` to show code version in UI. Added deploy
   workflow to AGENTS.md. Still using `Path.home()` for data dir.

Codex treated the symptom ("app disappears on relaunch") instead of diagnosing WHY
the data was missing.

## What Cursor did (1 commit, Mar 23)

Created `data_dir.py`:
```python
def cuagent_data_dir() -> Path:
    override = os.environ.get("CUAGENT_DATA_DIR", "").strip()
    if override:
        return Path(override).expanduser()
    if os.name == "nt":
        profile = os.environ.get("USERPROFILE", "").strip()
        if profile:
            return Path(profile) / ".cuagent-win"
    return Path.home() / ".cuagent-win"
```

Plus `_sync_storage_paths()` called at launch time (not import time) to re-resolve
all module-level path constants.
