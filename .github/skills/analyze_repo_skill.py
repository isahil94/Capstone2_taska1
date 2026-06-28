"""Skill: Analyze Repository - Core analysis workflow."""

from __future__ import annotations

from typing import Any

from skills import SkillOutput, ensure_analyzed
from core import parse_repository, build_graph, load_repository


def run(repo_path: str) -> SkillOutput:
    """
    Analyze a repository: load, parse, and build graph.

    Args:
        repo_path: Path to the repository to analyze

    Returns:
        SkillOutput containing:
        - summary: Quick overview
        - details: Comprehensive analysis results
        - evidence: List of findings
    """
    try:
        # Step 1: Load repository
        repo_result = load_repository(repo_path)
        if not repo_result.get("is_valid"):
            return SkillOutput(
                summary="Repository analysis failed",
                details={"error": repo_result.get("message")},
                evidence=["Repository validation failed"],
            )

        # Step 2: Parse repository
        parse_result = parse_repository(repo_path)
        if "error" in parse_result:
            return SkillOutput(
                summary="Repository analysis failed",
                details={"error": parse_result["error"]},
                evidence=["Parsing failed"],
            )

        # Step 3: Build graphs
        graph_result = build_graph(repo_path)
        if "error" in graph_result:
            return SkillOutput(
                summary="Repository analysis completed with partial results",
                details={"parse": parse_result, "graph_error": graph_result["error"]},
                evidence=["Graph building encountered an error"],
            )

        # Compile analysis summary
        summary = (
            f"Analyzed repository: {repo_result['metadata']['name']} "
            f"({parse_result['summary']['total_files']} files, "
            f"{parse_result['summary']['total_classes']} classes)"
        )

        # Build comprehensive details
        details = {
            "repository": repo_result["metadata"],
            "files": {
                "total": parse_result["summary"]["total_files"],
                "classes": parse_result["summary"]["total_classes"],
                "functions": parse_result["summary"]["total_functions"],
                "imports": parse_result["summary"]["total_imports"],
            },
            "graphs": {
                "types": graph_result["summary"]["graph_types"],
                "nodes": graph_result["summary"]["total_nodes"],
                "edges": graph_result["summary"]["total_edges"],
            },
            "file_list": [f["file_path"] for f in parse_result["files"][:10]],  # First 10
        }

        # Build evidence list
        evidence = [
            f"Found {parse_result['summary']['total_files']} source files",
            f"Identified {parse_result['summary']['total_classes']} classes",
            f"Identified {parse_result['summary']['total_functions']} functions",
            f"Built {len(graph_result['summary']['graph_types'])} dependency graphs",
            f"Extracted {graph_result['summary']['total_nodes']} nodes",
        ]

        return SkillOutput(
            summary=summary,
            details=details,
            evidence=evidence,
        )

    except Exception as e:
        return SkillOutput(
            summary="Repository analysis failed",
            details={"error": str(e)},
            evidence=[f"Exception: {str(e)}"],
        )
