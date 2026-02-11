"""Analyzer layer for read-only git context extraction.

This module must only read git state and convert it to structured `DiffContext`.
It must never modify diffs, stage files, or mutate repository state.
"""

from __future__ import annotations

import subprocess

from core.logger import debug_log
from core.types import DiffContext


def _run_git_command(cmd: list[str]) -> str:
    """Execute a git command and return stdout text.

    Input contract:
    - `cmd` must be a valid argument vector beginning with `git`.

    Output contract:
    - Returns decoded stdout string, possibly empty.

    Side effects:
    - Spawns subprocess.
    """

    completed = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return completed.stdout.strip()


def _get_staged_diff() -> str:
    """Read staged unified diff text.

    Input contract:
    - None.

    Output contract:
    - Returns staged diff from `git diff --cached`.

    Side effects:
    - Calls git subprocess.
    """

    return _run_git_command(["git", "diff", "--cached"])


def _get_git_status() -> str:
    """Read short-format git status.

    Input contract:
    - None.

    Output contract:
    - Returns raw `git status --short` output.

    Side effects:
    - Calls git subprocess.
    """

    return _run_git_command(["git", "status", "--short"])


def _parse_changed_files(status_output: str) -> list[str]:
    """Extract changed file paths from short status output.

    Input contract:
    - `status_output` must follow `git status --short` line format.

    Output contract:
    - Returns list of file path strings.

    Side effects:
    - None.
    """

    files: list[str] = []
    for line in status_output.splitlines():
        if len(line) < 4:
            continue
        files.append(line[3:].strip())
    return files


def _count_diff_stats(diff: str) -> tuple[int, int]:
    """Count insertion/deletion lines in a unified diff.

    Input contract:
    - `diff` is unified diff text.

    Output contract:
    - Returns `(insertions, deletions)` as non-negative integers.

    Side effects:
    - None.
    """

    insertions = 0
    deletions = 0
    for line in diff.splitlines():
        if line.startswith("+++") or line.startswith("---"):
            continue
        if line.startswith("+"):
            insertions += 1
        elif line.startswith("-"):
            deletions += 1
    return insertions, deletions


def read_git_context(debug: bool = False) -> DiffContext:
    """Build a `DiffContext` from current staged repository state.

    Input contract:
    - `debug` toggles diagnostic logging only.

    Output contract:
    - Returns `DiffContext` with diff/status/file/stat counts.

    Side effects:
    - Calls git subprocess commands.
    - Emits debug logs when `debug=True`.
    """

    diff = _get_staged_diff()
    status = _get_git_status()
    files_changed = _parse_changed_files(status)
    insertions, deletions = _count_diff_stats(diff)

    context = DiffContext(
        diff=diff,
        status=status,
        files_changed=files_changed,
        insertions=insertions,
        deletions=deletions,
    )
    debug_log(debug, "read_git_context", {"files_changed": len(files_changed)})
    return context
