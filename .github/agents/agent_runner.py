"""Agent Runner - Routes commands to appropriate agents."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from skills import SkillOutput, documentation_skill
from .comprehension_agent import ComprehensionAgent
from .architecture_agent import ArchitectureAgent
from .impact_agent import ImpactAgent


class AgentRunner:
    """Routes commands to agents and manages execution."""

    OUTPUT_DIR = Path("output/analysis-results")

    def __init__(self):
        self.comprehension = ComprehensionAgent()
        self.architecture = ArchitectureAgent()
        self.impact = ImpactAgent()

    def run(self, command: str, repo_path: str, *args: str, **kwargs: str) -> dict[str, Any]:
        """
        Route and execute a command.

        Args:
            command: Slash command name (/analyze, /architecture, /impact, /ask)
            repo_path: Path to the repository
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments

        Returns:
            Execution result with summary, details, and evidence
        """
        try:
            if command == "/analyze":
                return self._execute_analyze(repo_path)

            elif command == "/architecture":
                return self._execute_architecture(repo_path)

            elif command == "/impact":
                if not args:
                    return self._error("Impact analysis requires target file")
                return self._execute_impact(repo_path, args[0])

            elif command == "/ask":
                if not args:
                    return self._error("Ask command requires a question")
                question = " ".join(args)
                return self._execute_ask(repo_path, question)

            elif command == "/docs":
                return self._execute_docs(repo_path)

            else:
                return self._error(f"Unknown command: {command}")

        except Exception as e:
            return self._error(f"Agent execution failed: {str(e)}")

    def _execute_analyze(self, repo_path: str) -> dict[str, Any]:
        """Execute /analyze command."""
        result = self.comprehension.analyze(repo_path)
        return self._format_result(result, "analyze")

    def _execute_architecture(self, repo_path: str) -> dict[str, Any]:
        """Execute /architecture command."""
        result = self.architecture.analyze(repo_path)
        return self._format_result(result, "architecture")

    def _execute_impact(self, repo_path: str, target_file: str) -> dict[str, Any]:
        """Execute /impact command."""
        result = self.impact.analyze(repo_path, target_file)
        return self._format_result(result, "impact")

    def _execute_ask(self, repo_path: str, question: str) -> dict[str, Any]:
        """Execute /ask command."""
        result = self.comprehension.ask(repo_path, question)
        return self._format_result(result, "ask")

    def _execute_docs(self, repo_path: str) -> dict[str, Any]:
        """Execute /docs command."""
        result = documentation_skill.run(repo_path)
        return self._format_result(result, "docs")

    def _format_result(self, output: SkillOutput, command: str) -> dict[str, Any]:
        """Format SkillOutput as result and save to file."""
        details = dict(output.details or {})

        result = {
            "command": command,
            "timestamp": datetime.now().isoformat(),
            "status": "success",
            "summary": output.summary,
            "details": details,
            "evidence": output.evidence,
        }

        # Save to file
        filename = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{command}.json"
        self._save_output(result, filename)

        return result

    def _error(self, message: str) -> dict[str, Any]:
        """Return an error result."""
        return {
            "status": "error",
            "message": message,
            "timestamp": datetime.now().isoformat(),
        }

    def _save_output(self, result: dict[str, Any], filename: str) -> None:
        """Save result to file."""
        self.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_file = self.OUTPUT_DIR / filename

        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)


# Singleton instance
_runner = AgentRunner()


def run_agent(command: str, repo_path: str, *args: str) -> dict[str, Any]:
    """
    Run an agent command.

    Examples:
        run_agent("/analyze", "/path/to/repo")
        run_agent("/architecture", "/path/to/repo")
        run_agent("/impact", "/path/to/repo", "src/main.py")
        run_agent("/ask", "/path/to/repo", "How many files are there?")

    Args:
        command: Command name
        repo_path: Repository path
        *args: Additional arguments

    Returns:
        Result dictionary
    """
    return _runner.run(command, repo_path, *args)


def get_runner() -> AgentRunner:
    """Get the global agent runner instance."""
    return _runner
