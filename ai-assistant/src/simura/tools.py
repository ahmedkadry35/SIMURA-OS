"""Small, deliberately-scoped toolbox the assistant can call.

All tools obey three rules:

1. **No surprising side-effects.** Anything that mutates the system requires
   the user to confirm via the UI (the assistant returns a tool *suggestion*;
   the UI shows a "Run" button).
2. **Output is bounded.** Each tool truncates its output to a reasonable
   length so it fits inside a model's context window.
3. **No network shells.** The shell tool runs locally only and never accepts
   commands as a single string — they pass through ``shlex`` so injection
   from a model can't escape into the shell.
"""
from __future__ import annotations

import os
import shlex
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# A short, opinionated allow-list of binaries the assistant may call without
# any confirmation prompt. Anything outside this list will surface a "needs
# confirmation" UI affordance.
SAFE_READ_BINARIES = frozenset({
    "uname", "uptime", "date", "df", "free", "lscpu", "lsblk", "lsusb",
    "lspci", "neofetch", "fastfetch", "ip", "hostname", "id", "whoami",
    "pwd", "ls", "cat", "head", "tail", "wc", "grep", "find", "rg", "fd",
    "ps", "systemctl", "loginctl", "journalctl", "pacman", "flatpak",
})


@dataclass
class ToolResult:
    """Outcome of a tool call, returned to the controller / UI."""

    name: str
    ok: bool
    output: str = ""
    error: str = ""
    meta: dict[str, Any] = field(default_factory=dict)


def shell_run(argv: list[str], *, timeout: float = 15.0,
              max_bytes: int = 64 * 1024) -> ToolResult:
    """Run a single non-interactive command and capture its output.

    ``argv`` is a list of strings (already split by ``shlex``); we do not run
    a shell, so quoting / globbing / pipelines from the model are inert.
    """
    if not argv:
        return ToolResult(name="shell", ok=False, error="empty command")
    binary = Path(argv[0]).name
    is_safe_read = binary in SAFE_READ_BINARIES
    try:
        proc = subprocess.run(
            argv,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            env={**os.environ, "LC_ALL": "C.UTF-8", "TERM": "dumb"},
        )
    except FileNotFoundError:
        return ToolResult(name="shell", ok=False,
                          error=f"binary not found: {binary}")
    except subprocess.TimeoutExpired:
        return ToolResult(name="shell", ok=False,
                          error=f"timed out after {timeout}s")

    output = (proc.stdout or "")[:max_bytes]
    err = (proc.stderr or "")[:max_bytes]
    return ToolResult(
        name="shell",
        ok=proc.returncode == 0,
        output=output,
        error=err,
        meta={
            "returncode": proc.returncode,
            "binary": binary,
            "is_safe_read": is_safe_read,
        },
    )


def fs_search(root: str, pattern: str, *, max_hits: int = 200) -> ToolResult:
    """Recursive filename search rooted at ``root``."""
    root_path = Path(root).expanduser()
    if not root_path.is_dir():
        return ToolResult(name="fs.search", ok=False,
                          error=f"not a directory: {root}")
    hits: list[str] = []
    pat = pattern.lower()
    for dirpath, _dirs, files in os.walk(root_path):
        for name in files:
            if pat in name.lower():
                hits.append(str(Path(dirpath, name)))
                if len(hits) >= max_hits:
                    break
        if len(hits) >= max_hits:
            break
    return ToolResult(name="fs.search", ok=True,
                      output="\n".join(hits),
                      meta={"hits": len(hits), "truncated": len(hits) >= max_hits})


def fs_read(path: str, *, max_bytes: int = 64 * 1024) -> ToolResult:
    """Read a text file, capped at ``max_bytes``."""
    p = Path(path).expanduser()
    if not p.is_file():
        return ToolResult(name="fs.read", ok=False,
                          error=f"not a file: {path}")
    try:
        data = p.read_bytes()[:max_bytes]
    except OSError as exc:
        return ToolResult(name="fs.read", ok=False, error=str(exc))
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return ToolResult(name="fs.read", ok=False,
                          error="file is not valid UTF-8")
    return ToolResult(name="fs.read", ok=True, output=text,
                      meta={"bytes": len(data)})


def app_launch(app_id: str) -> ToolResult:
    """Launch a desktop application via ``gtk-launch`` / ``kioclient5``."""
    if "/" in app_id or " " in app_id:
        return ToolResult(name="app.launch", ok=False,
                          error="invalid desktop id")
    for launcher in ("gtk-launch", "kioclient5", "kioclient"):
        try:
            cmd = [launcher, app_id] if launcher == "gtk-launch" \
                else [launcher, "exec", f"applications:{app_id}.desktop"]
            subprocess.Popen(cmd, start_new_session=True)
            return ToolResult(name="app.launch", ok=True,
                              output=f"launched {app_id} via {launcher}")
        except FileNotFoundError:
            continue
    return ToolResult(name="app.launch", ok=False,
                      error="no desktop launcher available")


def parse_shell(text: str) -> list[str]:
    """Split a free-form command string into argv. Refuses pipelines / redirs."""
    if any(ch in text for ch in ("|", ">", "<", ";", "&", "`", "$(")):
        raise ValueError("only single, non-redirected commands are supported")
    return shlex.split(text)
