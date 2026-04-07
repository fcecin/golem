# The clauder story

## The problem

golem processes tasks across many sessions. Each session does one file (or
one scope), writes its results, and stops. The user has to manually:

1. Run `golem run`
2. Paste the boot phrase
3. Watch it work
4. Wait for it to finish
5. Run `golem run` again

For 546 files, that's 546 manual restarts. Unacceptable.

## Why not just use --print?

Claude CLI has `-p` (print mode) for non-interactive use. But `-p` doesn't
show progress, renders differently, and we couldn't get it to work reliably
with the boot phrase (quoting issues with `script`, etc.). The interactive
TUI is what works.

## The tmux insight

tmux lets you create a terminal session, type into it programmatically, and
read its screen — all without needing a display, a GUI, or Wayland/X11
cooperation. The key primitives:

- `tmux new-session -d` — create a background terminal
- `tmux send-keys` — type into it
- `tmux capture-pane -p` — read what's on screen
- `tmux attach` — watch it live

This is enough to puppet Claude CLI.

## First experiments (~/golem/tmux/)

### claude-tmux.sh

The simplest wrapper: launch claude inside tmux, attach to it. When claude
exits, tmux closes, you're back in your shell. Proved that claude works
fine inside tmux with no behavioral changes.

### claude-tmux-auto.sh

Added auto-typing: launch claude in tmux background, wait, then
`tmux send-keys "hi" Enter`. The user sees claude boot, then "hi" types
itself. Ghost in the machine.

The first version used `sleep 5` to wait for the prompt. Too fragile.

### Prompt detection

The critical challenge: how do you know claude is ready for input? The TUI
renders asynchronously. If you send keys too early, they get lost.

Solution: poll `tmux capture-pane` looking for the `❯` character, which
only appears in Claude's input prompt. Simple, reliable:

```python
def is_prompt_ready(content):
    return '❯' in content
```

Earlier versions tried parsing the last 10 lines looking for various
prompt indicators. Overengineered. The `❯` check is all you need.

### The fork trick

The user wants to SEE claude working (attached tmux) while the automation
runs in the background. Solution: `os.fork()`. The child process attaches
to tmux (blocking), the parent continues with the automation loop.

```python
if not args.detach:
    pid = os.fork()
    if pid == 0:
        os.execlp("tmux", "tmux", "attach", "-t", session)
```

## clauder.py

The final tool. A Python script that:

1. Launches claude in a tmux session
2. Waits for the prompt (polling for `❯`)
3. Sends the initial prompt (boot phrase or anything)
4. Waits for idle (no screen changes for N seconds)
5. Checks for the done signal (`NO MORE WORK TO DO`)
6. If not done, sends a continue prompt
7. Repeats until done or session dies

### The done signal trick

The continue prompt says: "If there is no more work to do, print the words
'no more work to do' but in all-uppercase letters."

The instruction is in lowercase. The model prints it in UPPERCASE. The
detector only matches uppercase. This prevents the instruction text itself
from triggering a false positive.

### Idle detection

```python
prev_hash = md5(capture_pane)
sleep(3)
curr_hash = md5(capture_pane)
if prev == curr for N seconds:
    # claude is idle
```

Simple content hashing. If the screen doesn't change for 30 seconds,
claude has stopped. Either it finished a work item and is waiting, or it
crashed. Either way, the driver should act.

## golem-clauder.sh

A thin wrapper that calls `golem boot` to get the boot phrase, then passes
it to clauder.py as the initial prompt. This is what `golem clauder` runs.

## golem driver (golem-driver.sh)

An earlier attempt at a bash-only driver loop. Worked but was fragile —
no prompt detection, blind sleep timers, no idle detection. Replaced by
clauder.py.

## What works

- Prompt detection via `❯` polling
- Auto-typing the boot phrase
- Idle detection via content hashing
- Done signal via case-sensitive matching
- Live viewing via fork+attach
- `golem clauder` as a first-class subcommand

## What doesn't work

- Console logging (`script` command captures raw terminal control codes
  that are unreadable garbage — ANSI stripping doesn't help because the
  TUI uses cursor positioning, not just colors)
- Non-interactive mode (`-p`) — quoting issues, different behavior
- Wayland screen capture — not needed since tmux bypasses it entirely

## Remaining questions

- Is 30s idle timeout right? Too short = premature nudge. Too long = wasted
  time on a genuinely idle model.
- Can clauder detect context exhaustion vs deliberate stop?
- Should clauder save each pane capture to a file for diagnostics?
- Can we detect and handle the permission/trust dialogs automatically?
