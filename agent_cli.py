#!/usr/bin/env python3
"""Command-line entry point for slash-command agents.

Examples:
    python agent_cli.py /analyze "F:/Projects/Capstone 2"
    python agent_cli.py /impact "F:/Projects/Capstone 2" "backend/main.py"
    python agent_cli.py /ask "F:/Projects/Capstone 2" "What does this repo do?"
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Sequence

ROOT_DIR = Path(__file__).resolve().parent
GITHUB_DIR = ROOT_DIR / ".github"
for candidate in (ROOT_DIR, GITHUB_DIR):
    path_str = str(candidate)
    if path_str not in sys.path:
        sys.path.insert(0, path_str)

from agents.agent_runner import run_agent

SUPPORTED_COMMANDS = {"/analyze", "/architecture", "/impact", "/ask", "/docs"}


def _error_result(command: str | None, message: str) -> dict[str, Any]:
    return {
        "status": "error",
        "command": command,
        "message": message,
    }


def main(argv: Sequence[str] | None = None) -> int:
    """Parse CLI arguments and dispatch to the agent runner."""
    args = list(argv if argv is not None else sys.argv[1:])

    if not args:
        result = _error_result(None, "Usage: agent_cli.py <command> <repo_path> [args...]")
        print(json.dumps(result, indent=2))
        return 2

    command = args[0]
    if command not in SUPPORTED_COMMANDS:
        result = _error_result(command, f"Unsupported command: {command}")
        print(json.dumps(result, indent=2))
        return 2

    if len(args) < 2:
        result = _error_result(command, "Repository path is required")
        print(json.dumps(result, indent=2))
        return 2

    repo_path = args[1]

    try:
        if command in {"/analyze", "/architecture", "/docs"}:
            result = run_agent(command, repo_path)
        elif command == "/impact":
            if len(args) < 3:
                result = _error_result(command, "Target file is required for /impact")
            else:
                result = run_agent(command, repo_path, args[2])
        else:  # /ask
            if len(args) < 3:
                result = _error_result(command, "Question is required for /ask")
            else:
                question = " ".join(args[2:])
                result = run_agent(command, repo_path, question)
    except Exception as exc:  # pragma: no cover - defensive guard
        result = _error_result(command, str(exc))

    print(json.dumps(result, indent=2))
    return 0 if result.get("status") == "success" else 1


if __name__ == "__main__":
    raise SystemExit(main())
