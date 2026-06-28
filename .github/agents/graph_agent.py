"""Agent: Graph Agent - Handles /graph command."""

from __future__ import annotations

from skills import SkillOutput
from skills import graph_skill


class GraphAgent:
    """Orchestrates knowledge-graph generation workflows."""

    def analyze(self, repo_path: str) -> SkillOutput:
        """Generate the repository knowledge graph and visualization artifacts."""
        output = graph_skill.run(repo_path)
        if output is None or not isinstance(output, SkillOutput):
            raise RuntimeError("GraphAgent returned invalid output")
        if not output.summary:
            raise ValueError("GraphAgent returned output without a summary")
        return output
