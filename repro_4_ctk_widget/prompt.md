# Actual prompts sent to Codex (from session rollout-2026-03-18T20-31-21)

## Initial prompt (created the broken panel)

> make the windows UI have the recent queries box be less tall so we can make the whole thing less tall. also determine the location of the cuagent window itself and make sure none of those elements are interactable or clickable. also make the recent section side scrollable so i can see the full queries instead of them being cutoff with ... . also collapse recent when the task starts running and replace it with the log then, so that also on average the height of the window is shorter

## Follow-up prompts (fixing the panel, all in same session)

> the cancel button gets squished to the side when the text on the left is too long, keep the cancel button full width. also, the log is a bit too tall. keep the log content collapsed when it goes back to recent at end of task. also i dont see any recent tasks anymore.

> i put a prompt then cancelled the task, recent section is still empty, why? can you fix that? also the cancel button sometimes gets squeezed if the text beforehand is long but keep that button always full width and truncate the text instead

> add more logs. i dont see it in recent on the windows app and just did it again. did you load the app onto the windows desktop so i can access it via RDP?

> i still dont see recent when task gets cancelled and it goes back to main screen. also collapsed logs arent there at the bottom. limit iterations to 20 not 50.

## What Codex tried (4 commits, Mar 18-20)

Codex kept iterating on the CTkScrollableFrame configuration — adjusting heights,
padding, scroll positions, pack options — without recognizing that the widget itself
is buggy on Windows. The user kept reporting "i dont see any recent tasks anymore"
and "recent section is still empty" but Codex never identified CTkScrollableFrame as
the root cause.

## What Cursor did (1 commit, Mar 23)

Replaced `CTkScrollableFrame` + `CTkButton` with native `tk.Listbox` + `tk.Scrollbar`.
Comment: "CTkScrollableFrame often fails to lay out children on Windows; classic
tk.Listbox is reliable for RECENT."
