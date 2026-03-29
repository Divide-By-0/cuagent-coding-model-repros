# Coding Model Comparison: Minimal Repros

3 bugs in a Windows desktop app that **Codex couldn't fix** (4+ attempts) but **Cursor Composer resolved** in 1 commit each. Each repro has 3 versions:

- `original_code.py` — What Codex initially wrote (the code that introduced the bug)
- `broken_app.py` — After Codex's fix attempts (still broken)
- `fixed_app.py` — Cursor's fix
- `prompt.md` — Prompt context and what each model tried

## Were they given the same prompt?

**No.** These weren't "fix this bug" prompts — the bugs emerged during feature work.

- **Codex** received `AGENTS.md` as system instructions (deployment rules, architecture, self-contained constraint). It was asked to build the Windows desktop app, then later asked to fix the issues it introduced. It iterated 4 times on the same files without finding the root causes.

- **Cursor Composer** received `.cursor/skills/` (commit-push, GCP logs) plus the codebase context. It was asked to add OmniParser + screenshot transport features. While working on that commit, it incidentally fixed all 3 Windows UX bugs that Codex couldn't — recognizing root causes that Codex missed across multiple attempts.

The `prompt.md` in each directory reconstructs the effective prompt from the commit messages and AGENTS.md context.

## Repros

### Repro 4: CTkScrollableFrame Bug on Windows

`CTkScrollableFrame(orientation="horizontal")` doesn't render `CTkButton` children on Windows.

```bash
cd repro_4_ctk_widget
pip install customtkinter
python original_code.py   # Codex's first version: static 76px, items invisible
python broken_app.py       # Codex's fix attempts: dynamic height, scroll resets — still empty
python fixed_app.py        # Cursor's fix: native tk.Listbox
```

| Version | What it does | Works on Windows? |
|---------|-------------|-------------------|
| `original_code.py` | CTkScrollableFrame + CTkButton, static height | No |
| `broken_app.py` | + dynamic height, scroll reset, update_idletasks | No |
| `fixed_app.py` | tk.Listbox + tk.Scrollbar (native widgets) | Yes |

### Repro 5: Path.home() Wrong on Non-Interactive Launch

`Path.home()` resolves to system profile directory when run from scheduled task / `.bat` launcher.

```bash
cd repro_5_path_home
python original_code.py   # Codex's first version: Path.home() hardcoded
python broken_app.py       # Codex's fix: added single-instance signal (doesn't fix path)
python fixed_app.py        # Cursor's fix: cuagent_data_dir() with USERPROFILE fallback
```

| Version | What it does | Fixes path issue? |
|---------|-------------|-------------------|
| `original_code.py` | `Path.home()` at import time | No |
| `broken_app.py` | + `_is_already_running()` + signal file | No (treats symptom) |
| `fixed_app.py` | `CUAGENT_DATA_DIR` env > `USERPROFILE` > `Path.home()` | Yes |

### Repro 6: -topmost Panel Blocks UIA Inspection

Panel's `-topmost` makes Windows UIA inspect the agent's panel instead of the target app.

```bash
cd repro_6_topmost_uia
pip install pywinauto
python original_code.py   # Codex's first version: -topmost always on, no compact mode
python broken_app.py       # Codex's fix: added compact mode but kept -topmost always on
python fixed_app.py        # Cursor's fix: toggle -topmost off during execution
```

| Version | What it does | UIA sees target app? |
|---------|-------------|---------------------|
| `original_code.py` | `-topmost` always, no compact mode | No |
| `broken_app.py` | + compact mode, still `-topmost` always | No |
| `fixed_app.py` | Clear `-topmost` during execution, restore on idle | Yes |

## Why Codex Failed

Common pattern across all 3: **Codex iterated on symptoms without identifying root causes.**

| Bug | Codex's approach | Root cause it missed |
|-----|-----------------|---------------------|
| Empty history panel | Tweak CTk widget config (heights, scroll) | The widget class is buggy on Windows |
| Disappearing data | Process lifecycle hacks (signal files) | `Path.home()` resolves wrong directory |
| Agent automates itself | Added compact mode (window resize) | `-topmost` must be cleared for UIA |

## Using as a Benchmark

Feed each `prompt.md` + `original_code.py` to any coding model and compare its fix to `fixed_app.py`:

```bash
# Claude Code
claude -p "$(cat repro_4_ctk_widget/prompt.md)" --allowedTools Edit,Write,Read

# Codex
codex exec "Fix original_code.py: $(head -5 repro_4_ctk_widget/prompt.md)"

# Cursor Composer
# Open original_code.py in Cursor, Cmd+K with the prompt text
```

### Scoring Rubric (per repro, 8 points)

| Criterion | Points |
|-----------|--------|
| Identifies root cause | 2 |
| Fixes the right layer (not just symptom) | 2 |
| Doesn't over-engineer (minimal code) | 1 |
| Adds explanatory comment on non-obvious logic | 1 |
| Handles edge cases | 1 |
| Considers platform-specific behavior | 1 |
