"""Minimal repro: CTkScrollableFrame fails to render children on Windows.

Run on Windows:
    pip install customtkinter
    python broken_app.py

Expected: A horizontal strip of task buttons appears in the RECENT panel.
Actual:   The RECENT panel is empty or items are clipped/invisible.
"""

from __future__ import annotations

import json
import logging
import threading
import time
from pathlib import Path

logger = logging.getLogger(__name__)

_DATA_DIR = Path.home() / ".cuagent-win"
_HISTORY_PATH = _DATA_DIR / "history.json"
_RECENT_PANEL_HEIGHT_EMPTY = 30
_RECENT_PANEL_HEIGHT_WITH_ITEMS = 76

_CLR_BG = "#1a1a2e"
_CLR_GREEN = "#3fb950"
_CLR_DIM = "#6e7681"


def _time_ago(ts: float) -> str:
    delta = time.time() - ts
    if delta < 60:
        return "just now"
    if delta < 3600:
        return f"{int(delta // 60)}m ago"
    if delta < 86400:
        return f"{int(delta // 3600)}h ago"
    return f"{int(delta // 86400)}d ago"


def _load_history() -> list[dict]:
    """Load or create sample history."""
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not _HISTORY_PATH.exists():
        # Seed sample data so the bug is visible
        sample = [
            {"task": f"Sample task {i}", "timestamp": time.time() - i * 3600, "success": i % 2 == 0}
            for i in range(5)
        ]
        _HISTORY_PATH.write_text(json.dumps(sample))
    return json.loads(_HISTORY_PATH.read_text())


class BrokenRecentPanel:
    """Reproduces the Codex approach: CTkScrollableFrame + CTkButton per task."""

    def __init__(self):
        import customtkinter as ctk

        ctk.set_appearance_mode("dark")
        self._root = ctk.CTk()
        self._root.title("Repro: CTkScrollableFrame Bug")
        self._root.geometry("400x300")
        self._root.configure(fg_color=_CLR_BG)

        self._history_font = ctk.CTkFont(size=12)

        # Title
        ctk.CTkLabel(
            self._root, text="RECENT",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=_CLR_DIM, anchor="w",
        ).pack(fill="x", padx=16, pady=(12, 2))

        # ── BUG: CTkScrollableFrame with horizontal orientation ──
        # On Windows, children packed inside this frame are invisible or
        # clipped. The internal canvas doesn't resize to fit CTkButton
        # children.  Codex tried: dynamic height, scroll resets,
        # update_idletasks — none fixed the underlying widget bug.
        self._history_frame = ctk.CTkScrollableFrame(
            self._root, height=_RECENT_PANEL_HEIGHT_EMPTY,
            corner_radius=8, orientation="horizontal",
        )
        self._history_frame.pack(fill="x", padx=12, pady=(0, 12))

        # Status label
        self._status = ctk.CTkLabel(
            self._root, text="Check if buttons appear above ^",
            text_color=_CLR_DIM,
        )
        self._status.pack(pady=10)

        self._refresh_history(ctk)
        self._root.mainloop()

    def _refresh_history(self, ctk) -> None:
        for w in self._history_frame.winfo_children():
            w.destroy()

        history = _load_history()
        if not history:
            self._history_frame.configure(height=_RECENT_PANEL_HEIGHT_EMPTY)
            ctk.CTkLabel(
                self._history_frame, text="No tasks yet",
                text_color=_CLR_DIM, font=ctk.CTkFont(size=12),
            ).pack(side="left", padx=12, pady=4)
            return

        # Grow panel when there are items
        self._history_frame.configure(height=_RECENT_PANEL_HEIGHT_WITH_ITEMS)

        for item in history[:10]:
            task_text = item["task"]
            ago = _time_ago(item.get("timestamp", 0))
            ok = item.get("success", False)
            button_text = f"{task_text}   {ago}"

            btn = ctk.CTkButton(
                self._history_frame,
                text=button_text,
                width=min(2200, max(180, self._history_font.measure(button_text) + 36)),
                anchor="w", height=30, corner_radius=6,
                fg_color="transparent", hover_color=("gray75", "gray25"),
                text_color=("gray10", "gray90"),
                border_width=1,
                border_color=_CLR_GREEN if ok else _CLR_DIM,
                font=self._history_font,
                command=lambda t=task_text: print(f"Selected: {t}"),
            )
            btn.pack(side="left", padx=(6, 0), pady=4)

        self._reset_recent_scroll()

    def _reset_recent_scroll(self) -> None:
        canvas = getattr(self._history_frame, "_parent_canvas", None)
        if canvas is None:
            return
        try:
            self._history_frame.update_idletasks()
            canvas.xview_moveto(0.0)
        except Exception:
            logger.debug("Failed to reset recent-task scroll position", exc_info=True)


if __name__ == "__main__":
    BrokenRecentPanel()
