"""Agent: Architecture Agent - Handles /architecture command."""

from __future__ import annotations

from skills import SkillOutput
from skills import architecture_skill


class ArchitectureAgent:
    """Orchestrates architecture analysis workflows."""

    def analyze(self, repo_path: str) -> SkillOutput:
        """Analyze repository architecture."""
        output = architecture_skill.run(repo_path)
        if output is None or not isinstance(output, SkillOutput):
            raise RuntimeError("ArchitectureAgent returned invalid output")
        if not output.summary:
            raise ValueError("ArchitectureAgent returned output without a summary")
        return output
