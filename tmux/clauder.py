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
import datetime


_log_path = None


def log(msg: str):
    if _log_path is None:
        return
    try:
        ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(_log_path, "a") as f:
            f.write(f"{ts} [clauder] {msg}\n")
    except OSError:
        pass


CONTINUE_PROMPT = (
    "Please perform the next work item. "
    "If there is no more work to do, print the words "
    "'no more work to do' but in all-uppercase letters."
)

DONE_SIGNAL = "NO MORE WORK TO DO"

RATE_LIMIT_SIGNAL = "Request rejected (429)"


def check_dependencies():
    missing = []
    for tool in ["tmux", "claude"]:
        if not shutil.which(tool):
            missing.append(tool)
    if missing:
        sys.stderr.write(f"[clauder] ERROR: Missing required tools: {', '.join(missing)}\n")
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
    # Look for the ❯ prompt character anywhere in the content
    # It appears on the input line when Claude is ready for input
    return '❯' in content


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


def has_rate_limit(content: str) -> bool:
    return RATE_LIMIT_SIGNAL in content


def rate_limit_near_prompt(content: str, max_lines_above: int = 10) -> bool:
    """True only if the 429 message sits within max_lines_above lines of the ❯ prompt.

    Prevents firing on stale rate-limit text that's still visible but has been
    superseded by newer Claude output.
    """
    lines = content.splitlines()
    prompt_idx = None
    for i, line in enumerate(lines):
        if '❯' in line:
            prompt_idx = i
            break
    if prompt_idx is None:
        return False
    start = max(0, prompt_idx - max_lines_above)
    return any(RATE_LIMIT_SIGNAL in l for l in lines[start:prompt_idx])


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
    parser.add_argument("--no-nudge", action="store_true",
                        help="Don't send the work-item nudge on idle. Keeps the 429 "
                             "rate-limit watcher running for interactive human use.")
    args = parser.parse_args()

    check_dependencies()

    session = args.session
    workdir = os.path.realpath(args.dir)

    global _log_path
    _log_path = os.path.join(workdir, "clauder.log")

    log(f"Work dir: {workdir}")
    log(f"Session: {session}")
    log(f"Idle timeout: {args.idle}s")
    log(f"Prompt: {args.prompt[:80]}")

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
    log("Waiting for Claude prompt...")
    if not wait_for_prompt(session):
        log("ERROR: Claude prompt not detected. Timeout.")
        subprocess.run(["tmux", "kill-session", "-t", session])
        sys.exit(1)

    # Send initial prompt — small delay to ensure prompt is fully ready
    if args.prompt:
        log("Prompt detected. Sending initial prompt.")
        time.sleep(1)
        tmux_send(session, args.prompt)
    else:
        log("Prompt detected. No initial prompt to send.")

    # Main loop: wait for idle, check for done, nudge to continue
    iteration = 0
    while True:
        iteration += 1
        log(f"Waiting for idle (iteration {iteration})...")

        content = wait_for_idle(session, args.idle)

        if not content:
            log("Session died. Exiting.")
            break

        if has_done_signal(content):
            log(f"Done signal detected after {iteration} iterations.")
            break

        if rate_limit_near_prompt(content):
            log("Rate limit (429) detected at prompt. Sending 'continue' to retry.")
            tmux_send(session, "continue")
            continue

        if args.no_nudge:
            # Interactive mode: just keep watching, never perturb the session.
            continue

        log("Idle detected. Sending continue prompt.")
        tmux_send(session, CONTINUE_PROMPT)

    # Cleanup
    if tmux_session_alive(session):
        final = tmux_capture(session)
        log(f"Final pane ({len(final)} chars)")
        subprocess.run(["tmux", "kill-session", "-t", session])

    log(f"Finished. Total iterations: {iteration}")


if __name__ == "__main__":
    main()
