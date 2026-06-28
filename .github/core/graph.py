"""Core graph builder wrapper - builds and retrieves repository graphs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .parser import _iter_source_files, parse_repository


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

        output_dir = repository_path / "analysis-outputs"
        output_dir.mkdir(parents=True, exist_ok=True)
        graph_path = output_dir / "knowledge-graph.json"
        if graph_path.exists():
            try:
                with graph_path.open("r", encoding="utf-8") as handle:
                    cached_graph = json.load(handle)
                if cached_graph.get("nodes") and cached_graph.get("edges") is not None:
                    return {
                        "local_path": str(repository_path),
                        "graphs": [
                            {
                                "type": "dependency",
                                "nodes": len(cached_graph.get("nodes", [])),
                                "edges": len(cached_graph.get("edges", [])),
                                "details": cached_graph,
                            }
                        ],
                        "summary": {
                            "graph_types": ["dependency"],
                            "total_graphs": 1,
                            "total_nodes": len(cached_graph.get("nodes", [])),
                            "total_edges": len(cached_graph.get("edges", [])),
                        },
                        "graph": cached_graph,
                    }
            except Exception:
                pass

        parse_result = parse_repository(repo_path)
        if "error" in parse_result:
            return {
                "error": parse_result["error"],
                "local_path": str(repository_path),
                "graphs": [],
                "summary": {},
            }

        files = _iter_source_files(repository_path)
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []
        edge_counter = 0

        file_nodes = {}
        for file_path in files:
            relative_path = file_path.relative_to(repository_path).as_posix()
            node_id = _normalize_node_id(relative_path)
            file_nodes[relative_path] = node_id
            nodes.append(
                {
                    "id": node_id,
                    "type": "file",
                    "label": file_path.name,
                    "path": relative_path,
                }
            )

        for file_info in parse_result.get("files", []):
            relative_path = file_info["file_path"]
            file_node_id = file_nodes.get(relative_path)
            if not file_node_id:
                continue
            for class_name in file_info.get("details", {}).get("classes", []):
                class_label = class_name.strip().split(" ")[-1].rstrip(":")
                class_id = f"class:{class_label}"
                nodes.append(
                    {
                        "id": class_id,
                        "type": "class",
                        "label": class_label,
                        "path": relative_path,
                    }
                )
                edges.append(
                    {
                        "id": f"edge{edge_counter}",
                        "source": file_node_id,
                        "target": class_id,
                        "type": "contains",
                    }
                )
                edge_counter += 1

            for function_name in file_info.get("details", {}).get("functions", []):
                function_label = function_name.strip().split(" ")[-1].rstrip(":")
                function_id = f"function:{function_label}"
                nodes.append(
                    {
                        "id": function_id,
                        "type": "function",
                        "label": function_label,
                        "path": relative_path,
                    }
                )
                edges.append(
                    {
                        "id": f"edge{edge_counter}",
                        "source": file_node_id,
                        "target": function_id,
                        "type": "contains",
                    }
                )
                edge_counter += 1

        for file_path in files:
            try:
                content = file_path.read_text(encoding="utf-8")
            except Exception:
                continue
            relative_path = file_path.relative_to(repository_path).as_posix()
            source_node_id = file_nodes.get(relative_path)
            if not source_node_id:
                continue
            for line in content.splitlines():
                imported_name = _extract_imported_module(line)
                if not imported_name:
                    continue
                imported_file = None
                for candidate in files:
                    candidate_name = candidate.stem
                    if candidate_name == imported_name:
                        imported_file = candidate.relative_to(repository_path).as_posix()
                        break
                if imported_file:
                    target_node_id = file_nodes.get(imported_file)
                    if target_node_id:
                        edges.append(
                            {
                                "id": f"edge{edge_counter}",
                                "source": source_node_id,
                                "target": target_node_id,
                                "type": "imports",
                            }
                        )
                        edge_counter += 1

        knowledge_graph = {
            "nodes": nodes,
            "edges": edges,
        }
        graph_path.write_text(json.dumps(knowledge_graph, indent=2), encoding="utf-8")
        (repository_path / ".knowledge-graph.json").write_text(json.dumps(knowledge_graph, indent=2), encoding="utf-8")

        return {
            "local_path": str(repository_path),
            "graphs": [
                {
                    "type": "dependency",
                    "nodes": len(nodes),
                    "edges": len(edges),
                    "details": knowledge_graph,
                }
            ],
            "summary": {
                "graph_types": ["dependency"],
                "total_graphs": 1,
                "total_nodes": len(nodes),
                "total_edges": len(edges),
            },
            "graph": knowledge_graph,
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
