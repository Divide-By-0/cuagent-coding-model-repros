# Actual prompts sent to Codex (from session rollout-2026-03-18T20-31-21)

## The launch/disappear prompts (same session as repro 4)

> now i get cuagent launch failed permission denied when i double click the desktop icon?

> i still get it, did you overwrite the old icon? what can i do to test or debug to help here

> i double clicked cuagent and it didnt seem to launch, what happened

> why is there two cuagent icons, neither seem to launch anything, just make one and have it work

> look at the logs of the most recent windows run. one, so first, the cuagent started then disappeared, whyd that happen. also, why did it keep clicking the wrong search bar in the amazon task?

> whys the app not responding rn? can you check the logs

## What Codex tried (2 commits, Mar 20)

1. **ae49aa8**: Added `_SHOW_SIGNAL` file + `_is_already_running()` single-instance
   mechanism via psutil. This prevents kill+restart from losing window state, but
   doesn't fix the path resolution issue at all. The user kept saying "the cuagent
   started then disappeared" and Codex assumed it was a duplicate-process problem.

2. **502e87d**: Added `_get_version_str()` to show code version in UI. Added deploy
   workflow to AGENTS.md. Still using `Path.home()` for data dir.

Codex never identified that `Path.home()` was resolving to the wrong directory.
The user's reports of "disappeared" and "not responding" were symptoms of the app
writing/reading data from a different location than expected.

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
