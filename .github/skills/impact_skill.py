"""Skill: Change Impact Analysis - Trace file dependencies."""

from __future__ import annotations

from typing import Any

from skills import SkillOutput
from core import load_repository, build_graph, find_dependents


def run(repo_path: str, target_file: str) -> SkillOutput:
    """
    Analyze impact of changes to a target file.

    Args:
        repo_path: Path to the repository
        target_file: File or symbol ID to analyze impact for

    Returns:
        SkillOutput containing:
        - summary: Impact overview
        - details: Affected modules and risk areas
        - evidence: Dependency chain analysis
    """
    try:
        # Validate repository
        repo_result = load_repository(repo_path)
        if not repo_result.get("is_valid"):
            return SkillOutput(
                summary="Impact analysis failed",
                details={"error": repo_result.get("message")},
                evidence=[],
            )

        # Get dependency graph
        graph_result = build_graph(repo_path)
        if "error" in graph_result:
            return SkillOutput(
                summary="Impact analysis incomplete",
                details={"error": graph_result["error"]},
                evidence=[],
            )

        target_id = target_file
        dependents = find_dependents(repo_path, target_id)
        visited = set(dependents)
        queue = list(dependents)

        while queue:
            current = queue.pop()
            next_dependents = find_dependents(repo_path, current)
            for dependent in next_dependents:
                if dependent not in visited:
                    visited.add(dependent)
                    queue.append(dependent)

        all_impacted = sorted(visited)

        summary = (
            f"Impact analysis for '{target_file}': "
            f"{len(dependents)} direct dependents, "
            f"{len(all_impacted)} total affected components"
        )

        evidence = [
            f"Direct dependents: {len(dependents)}",
            f"Transitive impact: {len(all_impacted)} components",
            f"Risk level: {'High' if len(all_impacted) > 10 else 'Medium' if len(all_impacted) > 5 else 'Low'}",
        ]

        details = {
            "target": target_file,
            "direct_dependents": dependents[:20],
            "impacted_count": len(all_impacted),
            "risk_areas": all_impacted,
            "impacted": all_impacted,
        }

        return SkillOutput(
            summary=summary,
            details=details,
            evidence=evidence,
        )

    except Exception as e:
        return SkillOutput(
            summary="Impact analysis failed",
            details={"error": str(e)},
            evidence=[],
        )
