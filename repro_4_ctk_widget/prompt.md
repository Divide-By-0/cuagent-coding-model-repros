# Prompt sent to Codex (multiple times, never resolved)

> The Recent Tasks panel in our Windows desktop app (CustomTkinter) shows no items.
> `CTkScrollableFrame` with horizontal orientation fails to lay out `CTkButton`
> children on Windows — items are invisible or clipped even though they're packed.
> We've tried dynamic height, scroll resets, and update_idletasks. The same code
> works on macOS. Fix this.

## Context given

- `broken_app.py` in this directory
- The app uses CustomTkinter (`pip install customtkinter`)
- On macOS the buttons appear fine inside CTkScrollableFrame
- On Windows they are invisible, clipped, or overlap
- Previous fix attempts (all by Codex, all failed):
  1. Dynamic height: `_RECENT_PANEL_HEIGHT_EMPTY` vs `_WITH_ITEMS` — panel resizes but items still invisible
  2. Scroll reset: `canvas.xview_moveto(0.0)` via internal `_parent_canvas` — no effect
  3. `update_idletasks()` before scroll — no effect

## What Codex tried (4 commits, Mar 18-20)

Codex kept iterating on the CTkScrollableFrame configuration — adjusting heights,
padding, scroll positions, pack options — without recognizing that the widget itself
is buggy on Windows.

## What Cursor did (1 commit, Mar 23)

Replaced `CTkScrollableFrame` + `CTkButton` with native `tk.Listbox` + `tk.Scrollbar`.
Comment: "CTkScrollableFrame often fails to lay out children on Windows; classic
tk.Listbox is reliable for RECENT."
