"""Fixed version: native tk.Listbox replaces CTkScrollableFrame.

Run on Windows:
    pip install customtkinter
    python fixed_app.py

The RECENT panel now reliably shows task history on Windows.
"""

from __future__ import annotations

import json
import logging
import threading
import time
import tkinter as tk
from pathlib import Path

logger = logging.getLogger(__name__)

_DATA_DIR = Path.home() / ".cuagent-win"
_HISTORY_PATH = _DATA_DIR / "history.json"
_RECENT_PANEL_HEIGHT_EMPTY = 30
_RECENT_PANEL_HEIGHT_WITH_ITEMS = 120

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


def _truncate_hist_display(text: str, max_len: int = 72) -> str:
    t = text.replace("\n", " ").strip()
    return t if len(t) <= max_len else t[: max_len - 3] + "..."


def _load_history() -> list[dict]:
    _DATA_DIR.mkdir(parents=True, exist_ok=True)
    if not _HISTORY_PATH.exists():
        sample = [
            {"task": f"Sample task {i}", "timestamp": time.time() - i * 3600, "success": i % 2 == 0}
            for i in range(5)
        ]
        _HISTORY_PATH.write_text(json.dumps(sample))
    return json.loads(_HISTORY_PATH.read_text())


class FixedRecentPanel:
    """Cursor's fix: native tk.Listbox instead of CTkScrollableFrame."""

    def __init__(self):
        import customtkinter as ctk

        ctk.set_appearance_mode("dark")
        self._root = ctk.CTk()
        self._root.title("Fixed: tk.Listbox")
        self._root.geometry("400x300")
        self._root.configure(fg_color=_CLR_BG)

        # Title
        ctk.CTkLabel(
            self._root, text="RECENT",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color=_CLR_DIM, anchor="w",
        ).pack(fill="x", padx=16, pady=(12, 2))

        # REASON: CTkScrollableFrame often fails to lay out children on Windows;
        # classic tk.Listbox is reliable for RECENT.
        self._history_host = ctk.CTkFrame(
            self._root,
            height=_RECENT_PANEL_HEIGHT_EMPTY,
            corner_radius=8,
            fg_color=_CLR_BG,
            border_width=1,
            border_color=_CLR_DIM,
        )
        self._history_host.pack(fill="x", padx=12, pady=(0, 12))
        self._history_host.pack_propagate(False)

        _hist_wrap = tk.Frame(self._history_host, bg=_CLR_BG, highlightthickness=0, bd=0)
        _hist_wrap.pack(fill="both", expand=True, padx=4, pady=4)

        _lb_font = ("Segoe UI", 10)
        self._history_listbox = tk.Listbox(
            _hist_wrap,
            height=4,
            activestyle="dotbox",
            selectmode=tk.SINGLE,
            exportselection=False,
            bg="#16213e",
            fg="#eaeaea",
            selectbackground="#0f4c75",
            selectforeground="#ffffff",
            highlightthickness=0,
            borderwidth=0,
            font=_lb_font,
        )
        _hist_sb = tk.Scrollbar(_hist_wrap, orient="vertical", command=self._history_listbox.yview)
        self._history_listbox.configure(yscrollcommand=_hist_sb.set)
        self._history_listbox.pack(side="left", fill="both", expand=True)
        _hist_sb.pack(side="right", fill="y")
        self._history_listbox.bind("<Double-Button-1>", self._on_history_double_click)

        self._history_tasks: list[str] = []

        # Status label
        self._status = ctk.CTkLabel(
            self._root, text="Double-click a task to select it",
            text_color=_CLR_DIM,
        )
        self._status.pack(pady=10)

        self._refresh_history()
        self._root.mainloop()

    def _refresh_history(self) -> None:
        self._history_listbox.delete(0, "end")
        self._history_tasks = []

        history = _load_history()
        if not history:
            self._history_host.configure(height=_RECENT_PANEL_HEIGHT_EMPTY)
            self._history_listbox.insert("end", "(No tasks yet)")
            self._history_tasks.append("")
            return

        self._history_host.configure(height=_RECENT_PANEL_HEIGHT_WITH_ITEMS)

        for item in history:
            task_text = item["task"]
            ago = _time_ago(item.get("timestamp", 0))
            ok = item.get("success", False)
            mark = "+" if ok else "\u00d7"
            snippet = _truncate_hist_display(task_text)
            line = f"{mark}  {ago:<12}  {snippet}"
            self._history_listbox.insert("end", line)
            self._history_tasks.append(task_text)

        self._history_listbox.yview_moveto(0.0)

    def _on_history_double_click(self, _event=None) -> None:
        sel = self._history_listbox.curselection()
        if not sel:
            return
        idx = int(sel[0])
        if 0 <= idx < len(self._history_tasks):
            task = self._history_tasks[idx]
            if task:
                print(f"Selected: {task}")


if __name__ == "__main__":
    FixedRecentPanel()
