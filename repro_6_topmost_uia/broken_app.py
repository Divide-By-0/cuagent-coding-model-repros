"""Minimal repro: -topmost panel blocks UIA inspection on Windows.

Run on Windows:
    pip install customtkinter pywinauto
    python broken_app.py

The panel stays topmost during "task execution". UIA inspection via pywinauto
attaches to the topmost window (our panel) instead of the target app (Notepad).

Expected: UIA tree shows Notepad's elements.
Actual:   UIA tree shows our panel's elements (the agent automates itself).
"""

from __future__ import annotations

import subprocess
import threading
import time
import tkinter as tk


class BrokenAutomationPanel:
    """Reproduces the Codex approach: -topmost is always on."""

    def __init__(self):
        self._root = tk.Tk()
        self._root.title("cuagent panel")
        self._root.geometry("300x150+10+10")
        self._root.configure(bg="#1a1a2e")

        # BUG: -topmost keeps the panel floating above all windows.
        # On Windows, UIA considers the topmost window as the "foreground"
        # window, so accessibility tree extraction attaches to OUR panel
        # instead of the app we're trying to automate.
        self._root.attributes("-topmost", True)

        self._label = tk.Label(
            self._root, text="Panel is TOPMOST\n(UIA will inspect THIS window)",
            fg="white", bg="#1a1a2e", font=("Segoe UI", 11),
        )
        self._label.pack(expand=True)

        self._btn = tk.Button(
            self._root, text="Simulate Task Execution",
            command=self._run_task, bg="#3fb950", fg="white",
        )
        self._btn.pack(pady=10)

        self._root.mainloop()

    def _run_task(self) -> None:
        """Simulate task execution: open Notepad and try to inspect it."""
        self._label.configure(text="Running task...\nOpening Notepad + inspecting UIA")
        self._root.update()

        # Open Notepad as a target app
        proc = subprocess.Popen(["notepad.exe"])
        time.sleep(1)

        # Try to get the foreground window's UIA tree
        try:
            import pywinauto
            # This connects to the "foreground" window — but because our panel
            # is -topmost, pywinauto may pick up our Tk window instead of Notepad
            desktop = pywinauto.Desktop(backend="uia")
            fg = desktop.top_window()
            title = fg.window_text()
            children = [c.window_text() for c in fg.children() if c.window_text()]

            self._label.configure(
                text=f"UIA foreground: '{title}'\n"
                     f"Children: {children[:5]}\n"
                     f"{'BUG: Got our panel!' if 'cuagent' in title.lower() else 'OK: Got Notepad'}"
            )
        except Exception as e:
            self._label.configure(text=f"UIA error: {e}")

        proc.terminate()


if __name__ == "__main__":
    BrokenAutomationPanel()
