# Actual prompts sent to Codex (from session rollout-2026-03-18T20-31-21)

## The self-clicking prompts (same session as repro 4 & 5)

> ok look at the most recent run. it clicked the curius extension mistakenly, why did that happen? did it have GCP segmentation applied to each screenshot?

> Look at the most recent run. Come on why did it click the Wi-Fi button and why did it click a random bookmark?

> so it was trying to click a button but then kept clicking itself since it was on top of the intended button to click. can you just temporarily make the window transparent to clicks for the split second during the click

> also determine the location of the cuagent window itself and make sure none of those elements are interactable or clickable

> look at the logs of the most recent windows run. one, so first, the cuagent started then disappeared, whyd that happen. also, why did it keep clicking the wrong search bar in the amazon task?

> ok so look at the most recent run. it was supposed to find the floss picks i ordered before, why didnt it try to select one i purchased before, or search in past orders? also why did the clicking fail so much

Note: The user explicitly identified the self-clicking problem ("kept clicking itself
since it was on top of the intended button") and even suggested making the window
transparent. Codex responded by adding element exclusion and foreground guards, but
never toggled `-topmost` — the actual root cause of UIA attaching to the wrong window.

## What Codex did (Mar 18-20)

Added `_sync_interaction_guard()` to exclude the cuagent window rect from screenshots
and element maps. Added foreground guards. But kept `-topmost` always on, so UIA still
attached to the cuagent panel instead of the browser.

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
