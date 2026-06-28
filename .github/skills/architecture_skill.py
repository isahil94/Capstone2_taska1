"""Skill: Architecture Analysis - Identify layers and patterns."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from skills import SkillOutput
from core import build_graph, load_repository, parse_repository


def run(repo_path: str) -> SkillOutput:
    """
    Analyze repository architecture: identify layers and patterns.

    Args:
        repo_path: Path to the repository

    Returns:
        SkillOutput containing:
        - summary: Architecture overview
        - details: Layer analysis
        - evidence: Identified patterns
    """
    try:
        # Validate repository
        repo_result = load_repository(repo_path)
        if not repo_result.get("is_valid"):
            return SkillOutput(
                summary="Architecture analysis failed",
                details={"error": repo_result.get("message")},
                evidence=[],
            )

        # Parse repository files and derive architecture hints from paths and names
        parse_result = parse_repository(repo_path)
        if "error" in parse_result:
            return SkillOutput(
                summary="Architecture analysis incomplete",
                details={"error": parse_result["error"]},
                evidence=[],
            )

        graph_result = build_graph(repo_path)
        if "error" in graph_result:
            return SkillOutput(
                summary="Architecture analysis incomplete",
                details={"error": graph_result["error"]},
                evidence=[],
            )

        repository_root = Path(repo_path).resolve()
        top_level_dirs = [p.name for p in repository_root.iterdir() if p.is_dir()]

        layers = {
            "frontend": [],
            "engine": [],
            "docs": [],
            "automation": [],
            "other": [],
        }
        evidence = []

        for dir_name in top_level_dirs:
            normalized = dir_name.lower()
            if normalized in {"frontend", "src", "ui"}:
                layers["frontend"].append(dir_name)
            elif normalized in {"engine", "backend", "service", "api", "server"}:
                layers["engine"].append(dir_name)
            elif normalized in {"docs", "documentation", "doc"}:
                layers["docs"].append(dir_name)
            elif normalized in {"tests", ".github", "output", "local_models"}:
                layers["automation"].append(dir_name)
            else:
                layers["other"].append(dir_name)

        layer_counts = {k: len(v) for k, v in layers.items() if v}
        summary = (
            f"Architecture analysis: Identified {sum(len(v) for v in layers.values())} components "
            f"across {len(layer_counts)} layers"
        )

        if layers["frontend"]:
            evidence.append(f"Frontend Layer: {len(layers['frontend'])} components")
        if layers["engine"]:
            evidence.append(f"Engine Layer: {len(layers['engine'])} components")
        if layers["docs"]:
            evidence.append(f"Documentation Layer: {len(layers['docs'])} components")
        if layers["automation"]:
            evidence.append(f"Automation Layer: {len(layers['automation'])} components")
        if layers["other"]:
            evidence.append(f"Other Layer: {len(layers['other'])} components")

        details = {
            "layers": {k: v for k, v in layers.items() if v},
            "layer_distribution": layer_counts,
            "total_components": sum(len(v) for v in layers.values()),
            "top_level_directories": top_level_dirs,
            "graph_summary": graph_result.get("summary", {}),
        }

        return SkillOutput(
            summary=summary,
            details=details,
            evidence=evidence,
        )

    except Exception as e:
        return SkillOutput(
            summary="Architecture analysis failed",
            details={"error": str(e)},
            evidence=[],
        )
