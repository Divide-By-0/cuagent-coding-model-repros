# Prompt sent to Codex (1 attempt, missed the issue entirely)

> Our Windows automation agent has a floating panel (tkinter `-topmost`) that stays
> above all windows. During task execution, the agent captures screenshots and extracts
> the UIA tree of the frontmost app (usually a browser). But since our panel is
> `-topmost`, Windows treats it as the foreground app, and UIA extracts our own panel's
> elements instead of the browser. The agent ends up trying to automate itself.
> Fix this — we still want the panel to float when idle.

## Context given

- `broken_app.py` in this directory
- Windows-only issue (macOS NSPanel doesn't interfere with accessibility)
- The panel must float above other windows when idle (so user can see it)
- During task execution, UIA/accessibility must see the target app, not our panel
- Screenshots also capture our panel overlaid on top

## What Codex did (Mar 18)

Set `-topmost` unconditionally in `__init__`. Never toggled it. Ported the macOS
pattern (NSPanel floats above without interfering with accessibility) to Windows
without testing that Windows UIA uses the topmost window for accessibility tree
extraction.

Codex never identified this as a bug — it was found when the agent started clicking
its own UI elements during task execution.

## What Cursor did (Mar 23)

Toggle `-topmost` based on execution state:
```python
def _enter_compact_mode(self):
    # ...
    # REASON: While -topmost is set, Windows treats our panel as foreground
    # over the browser — UIA/verify then attach to cuagent instead of Edge.
    self._root.attributes("-topmost", False)

def _exit_compact_mode(self):
    # ...
    self._root.attributes("-topmost", True)
```
