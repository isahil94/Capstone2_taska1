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

        def normalize_path(path_value: str) -> str:
            normalized = str(path_value).strip()
            if not normalized:
                return ""
            if normalized.startswith("file:"):
                normalized = normalized[5:]
            normalized = normalized.replace("\\", "/")
            normalized = normalized.lstrip("./")
            return normalized

        def normalize_node_id(node_id: str) -> str:
            normalized = str(node_id or "").strip()
            if normalized.startswith("file:"):
                normalized = normalized[5:]
            return normalized

        def classify_path(path_value: str, incoming_count: int = 0, outgoing_count: int = 0, total_degree: int = 0) -> str | None:
            normalized_path = normalize_path(path_value).lower()
            if any(marker in normalized_path for marker in ignored_markers):
                return None
            if normalized_path.startswith("tests/") or "/tests/" in normalized_path or normalized_path.startswith("test_") or normalized_path.endswith("_test.py"):
                return None
            if any(token in normalized_path for token in ("/docs/", "/doc/")) or normalized_path.endswith(".md") or normalized_path.endswith(".txt") or normalized_path.endswith(".rst") or normalized_path.endswith("readme"):
                return "Documentation"
            if any(token in normalized_path for token in ("package.json", "requirements.txt", "requirements", "pyproject.toml", "setup.cfg", "setup.py", "tox.ini", "pytest.ini", ".env", ".yaml", ".yml", "dockerfile", "docker-compose.yml", "config")):
                return "Config"
            if normalized_path.startswith("frontend/") or normalized_path.startswith("frontend") or "/frontend/" in normalized_path:
                return "API"

            if outgoing_count >= 2 and incoming_count <= 1:
                return "API"
            if incoming_count >= 2 and outgoing_count <= 1 and total_degree >= 2:
                return "Utility"
            if total_degree >= 3 and outgoing_count >= 1:
                return "Service"
            if incoming_count >= 1 and outgoing_count >= 1:
                return "Service"
            if outgoing_count >= 1:
                return "API"
            if any(token in normalized_path for token in ("/core/", "/service/", "/engine/", "/parser/", "/graph/")):
                return "Service"
            return "Utility"

        graph_nodes = graph_result.get("graph", {}).get("nodes", [])
        graph_edges = graph_result.get("graph", {}).get("edges", [])
        if not graph_nodes:
            graph_nodes = []
            graph_edges = []

        file_paths: list[str] = []
        indegree: dict[str, int] = {}
        outdegree: dict[str, int] = {}

        for node in graph_nodes:
            if node.get("type") != "file":
                continue

            path_value = node.get("path") or node.get("filePath") or node.get("id") or ""
            file_path = normalize_path(path_value)
            if not file_path:
                continue

            file_paths.append(file_path)
            indegree[file_path] = 0
            outdegree[file_path] = 0

        for edge in graph_edges:
            source_id = normalize_node_id(edge.get("source"))
            target_id = normalize_node_id(edge.get("target"))
            if not source_id or not target_id:
                continue
            source_path = next((path for path in file_paths if normalize_node_id(path) == source_id), None)
            target_path = next((path for path in file_paths if normalize_node_id(path) == target_id), None)
            if not source_path or not target_path or source_path == target_path:
                continue
            edge_type = str(edge.get("type", "")).lower()
            if edge_type in {"imports", "calls", "dependency", "depends"}:
                outdegree[source_path] = outdegree.get(source_path, 0) + 1
                indegree[target_path] = indegree.get(target_path, 0) + 1

        if file_paths:
            for file_path in sorted(set(file_paths)):
                layer = classify_path(
                    file_path,
                    incoming_count=indegree.get(file_path, 0),
                    outgoing_count=outdegree.get(file_path, 0),
                    total_degree=indegree.get(file_path, 0) + outdegree.get(file_path, 0),
                )
                if not layer:
                    continue
                layers[layer].append(file_path)

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
