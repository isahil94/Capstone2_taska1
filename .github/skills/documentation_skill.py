"""Skill: Documentation - Generate onboarding markdown for a repository."""

from __future__ import annotations

from pathlib import Path

from skills import SkillOutput
from core import load_repository, parse_repository


def run(repo_path: str) -> SkillOutput:
    """Generate a lightweight onboarding document for the repository."""
    repo_result = load_repository(repo_path)
    if not repo_result.get("is_valid"):
        return SkillOutput(
            summary="Documentation generation failed",
            details={"error": repo_result.get("message")},
            evidence=[],
        )

    parse_result = parse_repository(repo_path)
    if "error" in parse_result:
        return SkillOutput(
            summary="Documentation generation failed",
            details={"error": parse_result["error"]},
            evidence=[],
        )

    repository_root = Path(repo_path).resolve()
    top_level_dirs = [p.name for p in repository_root.iterdir() if p.is_dir()]

    markdown = []
    markdown.append("# Repository Onboarding")
    markdown.append("")
    markdown.append("## Overview")
    markdown.append(f"- Repository: {repo_result['metadata']['name']}")
    markdown.append(f"- Source files: {parse_result['summary']['total_files']}")
    markdown.append(f"- Classes: {parse_result['summary']['total_classes']}")
    markdown.append(f"- Functions: {parse_result['summary']['total_functions']}")
    markdown.append("")
    markdown.append("## Architecture")
    for directory in top_level_dirs:
        markdown.append(f"- {directory}")
    markdown.append("")
    markdown.append("## Key Modules")
    for file_info in parse_result.get("files", [])[:10]:
        markdown.append(f"- {file_info['file_path']}")
    markdown.append("")
    markdown.append("## Execution Flow")
    markdown.append("- Start from the repository entry points and follow imports across modules.")

    return SkillOutput(
        summary="Documentation generated",
        details={"markdown": "\n".join(markdown)},
        evidence=["Generated onboarding guide"],
    )
