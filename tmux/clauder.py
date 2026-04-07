#!/usr/bin/env python3
"""clauder — drive Claude CLI via tmux.

Launches claude in a tmux session, sends an initial prompt, then repeatedly
nudges it to continue until it reports no more work to do.

Requires: tmux, claude (in PATH)

Usage:
  clauder.py <prompt> [--dir DIR] [--idle SECONDS] [--detach] [--claude-args ARGS]
"""

import subprocess
import time
import sys
import os
import shutil
import hashlib
import argparse


CONTINUE_PROMPT = (
    "Please perform the next work item. "
    "If there is no more work to do, print the words "
    "'no more work to do' but in all-uppercase letters."
)

DONE_SIGNAL = "NO MORE WORK TO DO"


def check_dependencies():
    missing = []
    for tool in ["tmux", "claude"]:
        if not shutil.which(tool):
            missing.append(tool)
    if missing:
        print(f"[clauder] ERROR: Missing required tools: {', '.join(missing)}")
        sys.exit(1)


def tmux_capture(session: str) -> str:
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", session, "-p"],
        capture_output=True, text=True
    )
    return result.stdout


def tmux_send(session: str, text: str):
    subprocess.run(["tmux", "send-keys", "-t", session, text, "Enter"])


def tmux_session_alive(session: str) -> bool:
    result = subprocess.run(
        ["tmux", "has-session", "-t", session],
        capture_output=True
    )
    return result.returncode == 0


def content_hash(content: str) -> str:
    return hashlib.md5(content.encode()).hexdigest()


def wait_for_prompt(session: str, timeout: float = 60.0) -> bool:
    start = time.time()
    while time.time() - start < timeout:
        content = tmux_capture(session)
        if is_prompt_ready(content):
            return True
        time.sleep(0.5)
    return False


def is_prompt_ready(content: str) -> bool:
    lines = content.strip().split('\n')
    for line in reversed(lines[-10:]):
        line = line.strip()
        if not line:
            continue
        if '❯' in line:
            return True
        if 'bypass permissions' in line:
            return True
        break
    return False


def wait_for_idle(session: str, idle_seconds: float = 30.0) -> str:
    prev_hash = ""
    idle_count = 0.0
    poll = 3.0

    while True:
        if not tmux_session_alive(session):
            return ""

        content = tmux_capture(session)
        curr_hash = content_hash(content)

        if curr_hash == prev_hash:
            idle_count += poll
            if idle_count >= idle_seconds:
                return content
        else:
            idle_count = 0.0
            prev_hash = curr_hash

        time.sleep(poll)


def has_done_signal(content: str) -> bool:
    return DONE_SIGNAL in content


def main():
    parser = argparse.ArgumentParser(
        description="Launches claude in a tmux session, sends an initial prompt, "
                    "then repeatedly nudges it to continue until it reports no more work to do."
    )
    parser.add_argument("prompt", help="Initial prompt to send to Claude")
    parser.add_argument("--dir", default=".", help="Work directory (default: current dir)")
    parser.add_argument("--session", default=f"clauder-{os.getpid()}", help="tmux session name (default: clauder-<pid>)")
    parser.add_argument("--idle", type=float, default=30.0, help="Idle detection seconds (default: %(default)s)")
    parser.add_argument("--detach", action="store_true", help="Run detached (no visible terminal)")
    parser.add_argument("--claude-args", default="", help="Extra args to pass to claude")
    args = parser.parse_args()

    check_dependencies()

    session = args.session
    workdir = os.path.realpath(args.dir)

    print(f"[clauder] Work dir: {workdir}")
    print(f"[clauder] Session: {session}")
    print(f"[clauder] Idle timeout: {args.idle}s")
    print(f"[clauder] Prompt: {args.prompt[:80]}...")

    # Launch claude in tmux
    subprocess.run([
        "tmux", "new-session", "-d", "-s", session, "-x", "200", "-y", "50",
        f"cd {workdir} && claude {args.claude_args}"
    ])

    if not args.detach:
        pid = os.fork()
        if pid == 0:
            os.execlp("tmux", "tmux", "attach", "-t", session)

    # Wait for claude to be ready
    print("[clauder] Waiting for Claude prompt...")
    if not wait_for_prompt(session):
        print("[clauder] ERROR: Claude prompt not detected. Timeout.")
        subprocess.run(["tmux", "kill-session", "-t", session])
        sys.exit(1)

    # Send initial prompt
    print("[clauder] Prompt detected. Sending...")
    tmux_send(session, args.prompt)

    # Main loop: wait for idle, check for done, nudge to continue
    iteration = 0
    while True:
        iteration += 1
        print(f"[clauder] Waiting for idle (iteration {iteration})...")

        content = wait_for_idle(session, args.idle)

        if not content:
            print("[clauder] Session died. Exiting.")
            break

        if has_done_signal(content):
            print(f"[clauder] Done signal detected after {iteration} iterations.")
            break

        print(f"[clauder] Idle detected. Sending continue prompt...")
        tmux_send(session, CONTINUE_PROMPT)

    # Cleanup
    if tmux_session_alive(session):
        final = tmux_capture(session)
        print(f"[clauder] Final pane ({len(final)} chars)")
        subprocess.run(["tmux", "kill-session", "-t", session])

    print(f"[clauder] Finished. Total iterations: {iteration}")


if __name__ == "__main__":
    main()
