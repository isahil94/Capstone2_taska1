"""Skill utilities and base classes for skill orchestration."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class SkillOutput:
    """Structured output for all skills."""

    def __init__(self, summary: str, details: dict[str, Any], evidence: list[str] | None = None):
        self.summary = summary
        self.details = details
        self.evidence = evidence or []

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "summary": self.summary,
            "details": self.details,
            "evidence": self.evidence,
        }

    def save(self, output_path: str) -> str:
        """Save skill output to JSON file."""
        path = Path(output_path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2)

        return str(path)


class _DocumentationSkillProxy:
    """Compatibility wrapper that exposes documentation_skill.run()."""

    @staticmethod
    def run(repo_path: str):
        from .documentation_skill import run as documentation_skill_run

        return documentation_skill_run(repo_path)


documentation_skill = _DocumentationSkillProxy()


def ensure_analyzed(repo_path: str) -> dict[str, Any]:
    """
    Ensure repository is analyzed. If not, analyze it.

    Args:
        repo_path: Path to the repository

    Returns:
        Analysis result dictionary
    """
    from .core.parser import parse_repository
    from .core.graph import build_graph
    from .core.repository import load_repository

    # Validate repository
    repo_result = load_repository(repo_path)
    if not repo_result.get("is_valid"):
        raise ValueError(f"Invalid repository: {repo_result.get('message')}")

    # Parse repository
    parse_result = parse_repository(repo_path)
    if "error" in parse_result:
        raise ValueError(f"Parse error: {parse_result['error']}")

    # Build graph
    graph_result = build_graph(repo_path)
    if "error" in graph_result:
        raise ValueError(f"Graph error: {graph_result['error']}")

    return {
        "repository": repo_result,
        "parse": parse_result,
        "graph": graph_result,
    }


# Expose skill modules for convenient imports.
from . import analyze_repo_skill, architecture_skill, impact_skill, qna_skill, graph_skill  # noqa: E402,F401
