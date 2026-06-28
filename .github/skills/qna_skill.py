"""Skill: Q&A - Answer questions about the repository."""

from __future__ import annotations

import re

from skills import SkillOutput, ensure_analyzed
from core import build_graph, load_repository, parse_repository


def run(repo_path: str, question: str) -> SkillOutput:
    """
    Answer a question about the repository using repository graph evidence.

    Args:
        repo_path: Path to the repository
        question: The question to answer

    Returns:
        SkillOutput containing:
        - summary: Direct answer
        - details: Supporting information
        - evidence: Supporting facts from analysis
    """
    try:
        try:
            analysis = ensure_analyzed(repo_path)
            graph_data = analysis.get("graph", {}).get("graph", {})
            nodes = graph_data.get("nodes", [])
        except Exception:
            repo_result = load_repository(repo_path)
            if not repo_result.get("is_valid"):
                return SkillOutput(
                    summary="Cannot answer question",
                    details={"answer": "Unable to answer the question", "evidence": []},
                    evidence=[],
                )

            parse_result = parse_repository(repo_path)
            if "error" in parse_result:
                return SkillOutput(
                    summary="Cannot answer question",
                    details={"answer": "Unable to answer the question", "evidence": []},
                    evidence=[],
                )

            graph_result = build_graph(repo_path)
            graph_data = graph_result.get("graph", {})
            nodes = graph_data.get("nodes", [])

        question_lower = question.lower()
        words = re.findall(r"[a-z0-9_]+", question_lower)
        stop_words = {
            "a",
            "an",
            "and",
            "are",
            "can",
            "does",
            "for",
            "from",
            "how",
            "in",
            "is",
            "it",
            "me",
            "of",
            "on",
            "or",
            "the",
            "this",
            "to",
            "what",
            "when",
            "where",
            "why",
            "with",
            "work",
        }
        keywords = [word for word in words if word not in stop_words and len(word) > 2]

        if not keywords:
            keywords = [word for word in words if len(word) > 2]

        evidence = []
        for node in nodes:
            node_label = str(node.get("label", "")).lower()
            node_id = str(node.get("id", "")).lower()
            if any(keyword in node_label or keyword in node_id for keyword in keywords):
                evidence.append(node.get("id"))

        evidence = evidence[:5]

        if evidence:
            top_node = next((node for node in nodes if node.get("id") == evidence[0]), None)
            top_label = top_node.get("label") if top_node else evidence[0]
            answer = f"Relevant components found related to the question. Likely handled in {top_label}."
        else:
            answer = "No relevant information found in repository"

        return SkillOutput(
            summary="Answer generated",
            details={"answer": answer, "evidence": evidence},
            evidence=evidence,
        )

    except Exception as e:
        return SkillOutput(
            summary="Error answering question",
            details={"answer": "Unable to answer the question", "evidence": []},
            evidence=[],
        )
