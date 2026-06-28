"""Core graph builder wrapper - builds and retrieves repository graphs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .parser import _iter_source_files, parse_repository
import re


def _normalize_node_id(node_id: str) -> str:
    """Normalize graph node IDs so lookups work with either file paths or prefixed IDs."""
    if not node_id:
        return node_id
    if node_id.startswith("file:"):
        return node_id
    return f"file:{node_id}"


def _extract_imported_module(line: str) -> str | None:
    """Extract a reasonable module token from a variety of import syntaxes.

    Supports: from X import Y, import X, import X from "Y", require("X"), import "X"
    Returns the captured module text (raw) or None.
    """
    if not line:
        return None
    line = line.strip()
    patterns = [
        re.compile(r"^from\s+([A-Za-z0-9_./\-]+)\s+import"),
        re.compile(r"^import\s+([A-Za-z0-9_./\-]+)"),
        re.compile(r"import\s+.*from\s+[\'\"]([^\"\']+)[\'\"]"),
        re.compile(r"require\(\s*[\'\"]([^\"\']+)[\'\"]\s*\)"),
        re.compile(r"^import\s+[\'\"]([^\"\']+)[\'\"]"),
    ]
    for pat in patterns:
        m = pat.search(line)
        if m:
            return m.group(1)
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
        # module index for python module resolution
        module_index: dict[str, str] = {}
        # map file -> module
        file_to_module: dict[str, str] = {}
        # fallback file_map for non-python heuristics
        file_map: dict[str, list[str]] = {}

        for file_path in files:
            relative_path = file_path.relative_to(repository_path).as_posix()
            node_id = _normalize_node_id(relative_path)
            file_nodes[relative_path] = node_id

            # build fallback file_map entries
            stem = file_path.stem.lower()
            name = file_path.name.lower()
            no_ext = relative_path.rsplit(".", 1)[0].lower()
            dotted = no_ext.replace("/", ".").lstrip(".")
            file_map.setdefault(stem, []).append(relative_path)
            file_map.setdefault(name, []).append(relative_path)
            file_map.setdefault(dotted, []).append(relative_path)
            # last two segments
            parts = no_ext.split("/")
            if len(parts) >= 2:
                key2 = f"{parts[-2]}.{parts[-1]}"
                file_map.setdefault(key2, []).append(relative_path)

            # build python module index for .py files
            if file_path.suffix.lower() == ".py":
                # convert path to module path: strip leading ./ and leading dot
                mod = relative_path.lstrip("./")
                if mod.startswith("."):
                    mod = mod.lstrip(".")
                mod = mod.rsplit(".", 1)[0].replace("/", ".")
                # if this is an __init__, module is the package
                if mod.endswith(".__init__"):
                    mod = mod.rsplit(".__init__", 1)[0]
                if mod:
                    # full module
                    module_index[mod] = relative_path
                    file_to_module[relative_path] = mod
                    # also index without top-level package if present (e.g., core.graph)
                    segs = mod.split(".")
                    if len(segs) >= 2:
                        module_index[".".join(segs[-2:])] = relative_path
                    # last segment
                    module_index[segs[-1]] = relative_path

            nodes.append(
                {
                    "id": node_id,
                    "type": "file",
                    "label": file_path.name,
                    "path": relative_path,
                    "language": file_path.suffix.lower().lstrip("."),
                }
            )
        # Debug: module index summary
        try:
            print(f"Module index size: {len(module_index)}; file_map keys: {len(file_map)}")
        except Exception:
            pass

        # Keep track of created function/class nodes to support call-edge creation
        function_index: dict[str, list[str]] = {}
        class_index: dict[str, list[str]] = {}

        for file_info in parse_result.get("files", []):
            # normalize file path from parser to posix form to match file_nodes keys
            try:
                relative_path = Path(file_info["file_path"]).as_posix()
            except Exception:
                relative_path = str(file_info["file_path"]).replace("\\", "/")
            file_node_id = file_nodes.get(relative_path)
            if not file_node_id:
                continue
            for class_name in file_info.get("details", {}).get("classes", []):
                class_label = class_name.strip().split(" ")[-1].rstrip(":")
                # make class id unique per file to avoid collisions across repo
                class_id = f"class:{relative_path}:{class_label}"
                nodes.append(
                    {
                        "id": class_id,
                        "type": "class",
                        "label": class_label,
                        "path": relative_path,
                        "language": file_info.get("language", "generic"),
                    }
                )
                class_index.setdefault(class_label, []).append(class_id)
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
                # make function id unique per file
                function_id = f"function:{relative_path}:{function_label}"
                nodes.append(
                    {
                        "id": function_id,
                        "type": "function",
                        "label": function_label,
                        "path": relative_path,
                        "language": file_info.get("language", "generic"),
                    }
                )
                function_index.setdefault(function_label, []).append(function_id)
                edges.append(
                    {
                        "id": f"edge{edge_counter}",
                        "source": file_node_id,
                        "target": function_id,
                        "type": "contains",
                    }
                )
                edge_counter += 1

        # Resolve imports using module_index (for python) and file_map (fallback)
        total_imports_detected = 0
        total_imports_resolved = 0
        dbg_path = repository_path / "analysis-outputs" / "import-debug.txt"
        try:
            if dbg_path.exists():
                dbg_path.unlink()
        except Exception:
            pass

        for file_info in parse_result.get("files", []):
            relative_path = Path(file_info["file_path"]).as_posix()
            source_node_id = file_nodes.get(relative_path)
            if not source_node_id:
                continue

            imports_list = file_info.get("details", {}).get("imports", []) or []
            for imp in imports_list:
                if not imp:
                    continue
                total_imports_detected += 1
                matched_rel = None
                imp_raw = str(imp)

                # Python-specific resolution using module_index
                if file_info.get("language") == "python":
                    token = imp_raw.strip()
                    # handle relative imports starting with dots
                    if token.startswith("."):
                        # need source module to resolve relative imports
                        src_mod = file_to_module.get(relative_path)
                        if src_mod:
                            # count leading dots
                            m = re.match(r"^(\.+)(.*)$", token)
                            if m:
                                dots = m.group(1)
                                rest = m.group(2).lstrip('.')
                                level = len(dots)
                                parts = src_mod.split('.')
                                base = parts[:-level] if level <= len(parts) else []
                                if rest:
                                    candidate = ".".join(base + [rest]) if base else rest
                                else:
                                    candidate = ".".join(base)
                                # try progressive matching
                                to_try = []
                                if candidate:
                                    to_try.append(candidate)
                                    segs = candidate.split('.')
                                    for i in range(len(segs) - 1, 0, -1):
                                        to_try.append('.'.join(segs[:i]))
                                # also try last segment
                                if candidate:
                                    to_try.append(candidate.split('.')[-1])
                                for t in to_try:
                                    if t in module_index:
                                        matched_rel = module_index[t]
                                        break
                    else:
                        # absolute import: try full module, then progressively shorten
                        token = token.lstrip('.')
                        segs = token.split('.')
                        to_try = [".".join(segs[: i + 1]) for i in range(len(segs))]
                        # to_try currently ['a','a.b','a.b.c'] but we want full first, so reverse
                        to_try = list(reversed([".".join(segs[: i + 1]) for i in range(len(segs))]))
                        # also try progressively shorter from full
                        full = ".".join(segs)
                        to_try = [full]
                        for i in range(len(segs) - 1, 0, -1):
                            to_try.append('.'.join(segs[:i]))
                        to_try.append(segs[-1])
                        for t in to_try:
                            if t in module_index:
                                matched_rel = module_index[t]
                                break
                        # fallback: suffix match
                        if not matched_rel:
                            for k, v in module_index.items():
                                if k.endswith(segs[-1]):
                                    matched_rel = v
                                    break

                # Non-python fallback using file_map heuristics
                if not matched_rel:
                    token = imp_raw.strip().strip('"').strip("'")
                    t = token.lower()
                    # strip leading ./ or ../
                    t_strip = re.sub(r'^\.+/', '', t)
                    candidates = [t_strip, t_strip.replace('/', '.'), t_strip.split('.')[-1]]
                    # last two segments
                    segs = t_strip.replace('/', '.').split('.')
                    if len(segs) >= 2:
                        candidates.append(segs[-2] + '.' + segs[-1])
                    for c in candidates:
                        if not c:
                            continue
                        matches = file_map.get(c)
                        if matches:
                            matched_rel = matches[0]
                            break
                    # fallback suffix matching on file_map keys
                    if not matched_rel:
                        for k, v in file_map.items():
                            if k.endswith(segs[-1]):
                                matched_rel = v[0]
                                break

                # create import edge if resolved
                try:
                    with dbg_path.open('a', encoding='utf-8') as dbg:
                        dbg.write(f"[RESOLVE] {relative_path} -> {imp_raw} -> {matched_rel or 'NOT FOUND'}\n")
                except Exception:
                    pass

                if matched_rel:
                    target_node_id = file_nodes.get(matched_rel)
                    if target_node_id:
                        # avoid duplicate
                        exists = any(e for e in edges if e.get('source') == source_node_id and e.get('target') == target_node_id and e.get('type') == 'imports')
                        if not exists:
                            edges.append({'id': f'edge{edge_counter}', 'source': source_node_id, 'target': target_node_id, 'type': 'imports'})
                            edge_counter += 1
                            total_imports_resolved += 1

            # detect function calls in this file by scanning raw_content
            raw_content = file_info.get('details', {}).get('raw_content', '') or ''
            if raw_content:
                for func_name, func_ids in function_index.items():
                    call_pat = re.compile(rf"\b{re.escape(func_name)}\s*\(")
                    if call_pat.search(raw_content):
                        for fid in func_ids:
                            exists = any(e for e in edges if e.get('source') == source_node_id and e.get('target') == fid and e.get('type') == 'calls')
                            if not exists:
                                edges.append({'id': f'edge{edge_counter}', 'source': source_node_id, 'target': fid, 'type': 'calls'})
                                edge_counter += 1

        # debug log import stats
        try:
            print(f"Total imports detected: {total_imports_detected}")
            print(f"Total imports resolved: {total_imports_resolved}")
        except Exception:
            pass

        # sanitize node ids and edge endpoints (remove newlines/carriage returns)
        def _sanitize(s: str) -> str:
            if not isinstance(s, str):
                return s
            return s.replace("\n", "").replace("\r", "")

        for n in nodes:
            if "id" in n:
                n["id"] = _sanitize(n["id"])
            if "path" in n:
                n["path"] = _sanitize(n["path"])

        for e in edges:
            if "source" in e:
                e["source"] = _sanitize(e["source"])
            if "target" in e:
                e["target"] = _sanitize(e["target"])

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
