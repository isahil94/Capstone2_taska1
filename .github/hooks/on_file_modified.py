"""Hook: On File Modified - Trigger impact analysis."""

from __future__ import annotations

from typing import Any

from ..agent_runner import run_agent


def on_file_modified(repo_path: str, file_path: str) -> None:
    """
    Hook: triggered when a file is modified.
    Automatically runs impact analysis.

    Args:
        repo_path: Path to the repository
        file_path: Path to the modified file
    """
    print(f"File modified: {file_path}")
    print(f"Analyzing impact...")

    result = run_agent("/impact", repo_path, file_path)

    print(f"Impact analysis complete: {result.get('summary')}")
