"""Hook: On Analysis Complete - Generate reports."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ..agent_runner import run_agent


def on_analysis_complete(repo_path: str, analysis_result: dict[str, Any]) -> None:
    """
    Hook: triggered when analysis completes.
    Generates a comprehensive report.

    Args:
        repo_path: Path to the repository
        analysis_result: Result from analyze command
    """
    report = {
        "generated": datetime.now().isoformat(),
        "repository": repo_path,
        "analysis": analysis_result,
    }

    # Save report
    output_dir = Path("output/analysis-results")
    output_dir.mkdir(parents=True, exist_ok=True)

    report_file = (
        output_dir / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_analysis-report.json"
    )

    with open(report_file, "w") as f:
        json.dump(report, f, indent=2)

    print(f"Analysis report saved: {report_file}")
