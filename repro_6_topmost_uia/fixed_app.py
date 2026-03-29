"""Fixed version: toggle -topmost based on execution state.

Run on Windows:
    pip install pywinauto
    python fixed_app.py

The panel clears -topmost during task execution so UIA sees Notepad (or browser),
then restores -topmost when returning to idle.
"""

from __future__ import annotations

import subprocess
import time
import tkinter as tk


class FixedAutomationPanel:
    """Cursor's fix: toggle -topmost per execution state."""

    def __init__(self):
        self._root = tk.Tk()
        self._root.title("cuagent panel")
        self._root.geometry("300x200+10+10")
        self._root.configure(bg="#1a1a2e")

        # Start with -topmost so panel floats when idle
        self._root.attributes("-topmost", True)

        self._label = tk.Label(
            self._root, text="Panel is TOPMOST (idle)\nClick to run task",
            fg="white", bg="#1a1a2e", font=("Segoe UI", 11),
        )
        self._label.pack(expand=True)

        self._btn = tk.Button(
            self._root, text="Simulate Task Execution",
            command=self._run_task, bg="#3fb950", fg="white",
        )
        self._btn.pack(pady=10)

        self._root.mainloop()

    def _enter_compact_mode(self) -> None:
        """Shrink panel and clear topmost for task execution."""
        # REASON: While -topmost is set, Windows treats our panel as foreground
        # over the browser — UIA/verify then attach to cuagent instead of Edge.
        self._root.attributes("-topmost", False)
        self._label.configure(text="Panel is NOT topmost (running)\nUIA will see target app")

    def _exit_compact_mode(self) -> None:
        """Restore panel to idle state with topmost."""
        self._root.attributes("-topmost", True)
        self._label.configure(text="Panel is TOPMOST (idle)\nClick to run task")

    def _run_task(self) -> None:
        """Simulate task execution: open Notepad and inspect via UIA."""
        self._enter_compact_mode()
        self._root.update()

        proc = subprocess.Popen(["notepad.exe"])
        time.sleep(1)

        try:
            import pywinauto
            desktop = pywinauto.Desktop(backend="uia")
            fg = desktop.top_window()
            title = fg.window_text()
            children = [c.window_text() for c in fg.children() if c.window_text()]

            result = (
                f"UIA foreground: '{title}'\n"
                f"Children: {children[:5]}\n"
                f"{'OK: Got target app!' if 'cuagent' not in title.lower() else 'BUG: Got our panel!'}"
            )
            self._label.configure(text=result)
        except Exception as e:
            self._label.configure(text=f"UIA error: {e}")

        proc.terminate()
        time.sleep(0.5)
        self._exit_compact_mode()


if __name__ == "__main__":
    FixedAutomationPanel()
