"""Agent: Comprehension Agent - Handles /analyze and /ask commands."""

from __future__ import annotations

from skills import SkillOutput
from skills import analyze_repo_skill, qna_skill


class ComprehensionAgent:
    """Orchestrates repository comprehension workflows."""

    def analyze(self, repo_path: str) -> SkillOutput:
        """Analyze a repository."""
        output = analyze_repo_skill.run(repo_path)
        if output is None or not isinstance(output, SkillOutput):
            raise RuntimeError("ComprehensionAgent returned invalid output")
        if not output.summary:
            raise ValueError("ComprehensionAgent returned output without a summary")
        return output

    def ask(self, repo_path: str, question: str) -> SkillOutput:
        """Answer a question about the repository."""
        output = qna_skill.run(repo_path, question)
        if output is None or not isinstance(output, SkillOutput):
            raise RuntimeError("ComprehensionAgent returned invalid output")
        if not output.summary:
            raise ValueError("ComprehensionAgent returned output without a summary")
        return output
