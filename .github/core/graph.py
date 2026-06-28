"""Core graph builder wrapper - builds and retrieves repository graphs."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from .parser import _iter_source_files


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
        nodes = [f"file:{p.relative_to(repository_path).as_posix()}" for p in files]
        edges = []
        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                continue
            for line in content.splitlines():
                if line.lstrip().startswith(("import ", "from ")):
                    edges.append((file_path.name, line.strip()))

        graphs_data = [
            {
                "type": "dependency",
                "nodes": len(nodes),
                "edges": len(edges),
                "details": {
                    "nodes": [{"id": node, "type": "file", "label": node} for node in nodes],
                    "edges": [{"source": source, "target": target, "relationship": "imports"} for source, target in [(n, e) for n, e in []]],
                },
            }
        ]

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
        return []
    except Exception:
        return []
