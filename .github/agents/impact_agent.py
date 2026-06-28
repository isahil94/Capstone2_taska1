"""Agent: Impact Agent - Handles /impact command."""

from __future__ import annotations

from skills import SkillOutput
from skills import impact_skill


class ImpactAgent:
    """Orchestrates change impact analysis workflows."""

    def analyze(self, repo_path: str, target_file: str) -> SkillOutput:
        """Analyze impact of changes to a target file."""
        output = impact_skill.run(repo_path, target_file)
        if output is None or not isinstance(output, SkillOutput):
            raise RuntimeError("ImpactAgent returned invalid output")
        if not output.summary:
            raise ValueError("ImpactAgent returned output without a summary")
        return output
