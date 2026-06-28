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

        layers = {
            "API": [],
            "Service": [],
            "Config": [],
            "Documentation": [],
            "Utility": [],
        }
        evidence = []

        ignored_markers = (".git", ".venv", "__pycache__", ".pytest_cache", ".vscode", "analysis-outputs")

        def classify_path(path_value: str) -> str | None:
            normalized_path = str(path_value).lower()
            if any(marker in normalized_path for marker in ignored_markers):
                return None
            if any(token in normalized_path for token in ("agent_cli", "agent", "api")):
                return "API"
            if any(token in normalized_path for token in ("engine", "core", "parser", "graph", "service")):
                return "Service"
            if any(token in normalized_path for token in ("frontend", "react", "component")):
                return "API"
            if any(token in normalized_path for token in ("config", "package.json", "requirements", ".env")):
                return "Config"
            if any(token in normalized_path for token in ("docs", "readme", ".md")):
                return "Documentation"
            return "Utility"

        graph_nodes = graph_result.get("graph", {}).get("nodes", [])
        if not graph_nodes:
            graph_nodes = []

        for node in graph_nodes:
            if node.get("type") != "file":
                continue

            path_value = node.get("path") or node.get("filePath") or node.get("id") or ""
            if not path_value:
                continue

            if path_value.startswith("file:"):
                path_value = path_value[5:]

            layer = classify_path(path_value)
            if not layer:
                continue

            layers[layer].append(path_value)

        if not any(layers.values()):
            for file_info in parse_result.get("files", []):
                file_path = file_info.get("file_path", "")
                if not file_path:
                    continue
                layer = classify_path(file_path)
                if layer:
                    layers[layer].append(file_path)

        layer_counts = {k: len(v) for k, v in layers.items() if v}
        summary = "Identified logical architecture layers based on code roles"

        if layers["API"]:
            evidence.append("API layer contains interface and entry-point components")
        if layers["Service"]:
            evidence.append("Service layer contains core logic modules")
        if layers["Config"]:
            evidence.append("Config layer contains environment and package configuration")
        if layers["Documentation"]:
            evidence.append("Documentation layer contains docs and reference materials")
        if layers["Utility"]:
            evidence.append("Utility layer contains shared helpers and support modules")

        details = {
            "layers": {k: v for k, v in layers.items() if v},
            "layer_distribution": layer_counts,
            "total_components": sum(len(v) for v in layers.values()),
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
