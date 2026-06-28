"""Skill: Q&A - Answer questions about the repository."""

from __future__ import annotations

from typing import Any

from skills import SkillOutput
from core import load_repository, parse_repository


def run(repo_path: str, question: str) -> SkillOutput:
    """
    Answer a question about the repository.

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
        # Validate repository
        repo_result = load_repository(repo_path)
        if not repo_result.get("is_valid"):
            return SkillOutput(
                summary="Cannot answer question",
                details={"error": repo_result.get("message")},
                evidence=[],
            )

        # Get parsed data
        parse_result = parse_repository(repo_path)
        if "error" in parse_result:
            return SkillOutput(
                summary="Cannot answer question",
                details={"error": parse_result["error"]},
                evidence=[],
            )

        # Simple pattern matching for common questions
        question_lower = question.lower()

        if "file" in question_lower or "count" in question_lower:
            count = parse_result["summary"]["total_files"]
            summary = f"The repository contains {count} source files."
            evidence = [f"Scanned: {count} files"]
            details = {"file_count": count}

        elif "class" in question_lower:
            count = parse_result["summary"]["total_classes"]
            summary = f"Found {count} classes in the repository."
            evidence = [f"Classes: {count}"]
            details = {"class_count": count}

        elif "function" in question_lower or "method" in question_lower:
            count = parse_result["summary"]["total_functions"]
            summary = f"The repository has {count} functions."
            evidence = [f"Functions: {count}"]
            details = {"function_count": count}

        elif "import" in question_lower or "dependency" in question_lower:
            count = parse_result["summary"]["total_imports"]
            summary = f"Found {count} import statements."
            evidence = [f"Imports: {count}"]
            details = {"import_count": count}

        elif "language" in question_lower:
            languages = set()
            for file_info in parse_result["files"]:
                languages.add(file_info["language"])
            summary = f"Repository uses: {', '.join(sorted(languages))}"
            evidence = [f"Languages: {', '.join(sorted(languages))}"]
            details = {"languages": sorted(languages)}

        else:
            # Default: provide general statistics
            summary = (
                f"Repository contains {parse_result['summary']['total_files']} files "
                f"with {parse_result['summary']['total_classes']} classes and "
                f"{parse_result['summary']['total_functions']} functions."
            )
            evidence = [
                f"Files: {parse_result['summary']['total_files']}",
                f"Classes: {parse_result['summary']['total_classes']}",
                f"Functions: {parse_result['summary']['total_functions']}",
            ]
            details = {
                "files": parse_result["summary"]["total_files"],
                "classes": parse_result["summary"]["total_classes"],
                "functions": parse_result["summary"]["total_functions"],
            }

        return SkillOutput(
            summary=summary,
            details=details,
            evidence=evidence,
        )

    except Exception as e:
        return SkillOutput(
            summary="Error answering question",
            details={"error": str(e)},
            evidence=[],
        )
