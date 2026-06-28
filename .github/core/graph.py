"""Core graph builder wrapper - builds and retrieves repository graphs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .parser import _iter_source_files


def _normalize_node_id(node_id: str) -> str:
    """Normalize graph node IDs so lookups work with either file paths or prefixed IDs."""
    if not node_id:
        return node_id
    if node_id.startswith("file:"):
        return node_id
    return f"file:{node_id}"


def _extract_imported_module(line: str) -> str | None:
    """Extract the imported module name from a Python import statement."""
    stripped = line.strip()
    if not stripped:
        return None
    if stripped.startswith("from "):
        parts = stripped.split()
        if len(parts) >= 2:
            return parts[1].split(".")[0]
    if stripped.startswith("import "):
        parts = stripped.split()
        if len(parts) >= 2:
            return parts[1].split(".")[0]
    return None


def build_graph(repo_path: str) -> dict[str, Any]:
    """
    Build repository intelligence graphs.

    Args:
        repo_path: Path to the repository

    Returns:
        Dictionary containing:
        - local_path: str
        - graphs: list[dict] with graph snapshots
        - summary: dict with node/edge counts
    """
    try:
        repository_path = Path(repo_path).resolve()
        if not repository_path.exists() or not repository_path.is_dir():
            return {
                "error": "Repository path is invalid",
                "local_path": str(repository_path),
                "graphs": [],
                "summary": {},
            }

        files = _iter_source_files(repository_path)
        nodes = [_normalize_node_id(p.relative_to(repository_path).as_posix()) for p in files]
        edges = []
        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                continue
            relative_path = file_path.relative_to(repository_path).as_posix()
            for line in content.splitlines():
                imported_name = _extract_imported_module(line)
                if imported_name:
                    imported_file = None
                    for candidate in files:
                        candidate_name = candidate.stem
                        if candidate_name == imported_name:
                            imported_file = candidate.relative_to(repository_path).as_posix()
                            break
                    if imported_file:
                        edges.append((relative_path, imported_file))

        graphs_data = [
            {
                "type": "dependency",
                "nodes": len(nodes),
                "edges": len(edges),
                "details": {
                    "nodes": [{"id": node, "type": "file", "label": node} for node in nodes],
                    "edges": [{"source": source, "target": target, "relationship": "imports"} for source, target in edges],
                },
            }
        ]

        knowledge_graph = {
            "nodes": [{"id": node, "type": "file", "label": node} for node in nodes],
            "edges": [{"source": source, "target": target, "relationship": "imports"} for source, target in edges],
        }
        knowledge_graph_path = repository_path / ".knowledge-graph.json"
        knowledge_graph_path.write_text(json.dumps(knowledge_graph, indent=2), encoding="utf-8")

        return {
            "local_path": str(repository_path),
            "graphs": graphs_data,
            "summary": {
                "graph_types": [g["type"] for g in graphs_data],
                "total_graphs": len(graphs_data),
                "total_nodes": len(nodes),
                "total_edges": len(edges),
            },
        }
    except Exception as e:
        return {
            "error": str(e),
            "local_path": str(Path(repo_path).resolve()),
            "graphs": [],
            "summary": {},
        }


def get_graph(repo_path: str, graph_type: str) -> dict[str, Any]:
    """
    Retrieve a specific graph by type.

    Args:
        repo_path: Path to the repository
        graph_type: Type of graph (dependency, call, class, architecture, import)

    Returns:
        Dictionary containing graph nodes and edges
    """
    try:
        repository_path = Path(repo_path).resolve()
        if not repository_path.exists() or not repository_path.is_dir():
            return {
                "error": f"No {graph_type} graph found",
                "type": graph_type,
                "nodes": [],
                "edges": [],
            }

        return {
            "type": graph_type,
            "nodes": [],
            "edges": [],
        }
    except Exception as e:
        return {
            "error": str(e),
            "type": graph_type,
            "nodes": [],
            "edges": [],
        }


def find_dependents(repo_path: str, target_id: str) -> list[str]:
    """
    Find all nodes that depend on a target node.

    Args:
        repo_path: Path to the repository
        target_id: ID of the target node

    Returns:
        List of node IDs that depend on target
    """
    try:
        repository_path = Path(repo_path).resolve()
        if not repository_path.exists() or not repository_path.is_dir():
            return []

        graph_path = repository_path / ".knowledge-graph.json"
        if not graph_path.exists():
            return []

        with graph_path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)

        normalized_target = _normalize_node_id(target_id)
        dependents = []
        for edge in data.get("edges", []):
            edge_target = edge.get("target", "")
            if edge_target == target_id or _normalize_node_id(edge_target) == normalized_target:
                dependents.append(edge.get("source", ""))
        return dependents
    except Exception:
        return []
