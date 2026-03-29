"""Original code (Codex, 5a1304e, Mar 18): -topmost always on, no compact mode.

This is what Codex first wrote. The panel sets -topmost unconditionally and
never toggles it. There is no compact mode at all in the original — that was
added later in ae49aa8/502e87d, but still without toggling -topmost.

The bug: UIA inspection picks up the cuagent panel instead of the target app
because Windows treats the topmost window as the foreground window.
"""

from __future__ import annotations

import subprocess
import time
import tkinter as tk


class OriginalAutomationPanel:
    """Codex's first version: -topmost always on, no mode switching."""

    def __init__(self):
        self._root = tk.Tk()
        self._root.title("cuagent panel")
        self._root.geometry("300x200+10+10")
        self._root.configure(bg="#1a1a2e")

        # Original: -topmost set once, never cleared
        self._root.attributes("-topmost", True)

        self._label = tk.Label(
            self._root, text="Panel is TOPMOST (always)\nNo compact mode exists yet",
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
        """Original task execution: no compact mode, no topmost toggle."""
        # Original had no _enter_compact_mode / _exit_compact_mode at all.
        # The panel stays full-size and topmost during task execution.
        self._label.configure(text="Running task...\nPanel stays topmost (bug)")
        self._root.update()

        proc = subprocess.Popen(["notepad.exe"])
        time.sleep(1)

        try:
            import pywinauto
            desktop = pywinauto.Desktop(backend="uia")
            fg = desktop.top_window()
            title = fg.window_text()

            self._label.configure(
                text=f"UIA foreground: '{title}'\n"
                     f"{'BUG: Got our panel!' if 'cuagent' in title.lower() else 'OK: Got target'}"
            )
        except Exception as e:
            self._label.configure(text=f"UIA error: {e}")

        proc.terminate()


if __name__ == "__main__":
    OriginalAutomationPanel()
