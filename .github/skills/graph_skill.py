"""Skill: Knowledge Graph Generation - build and persist an interactive graph."""

from __future__ import annotations

import json
import os
from pathlib import Path

from skills import SkillOutput
from core import build_graph, load_repository


def run(repo_path: str) -> SkillOutput:
    """Build the repository knowledge graph and generate a visualization artifact."""
    repo_result = load_repository(repo_path)
    if not repo_result.get("is_valid"):
        return SkillOutput(
            summary="Knowledge graph generation failed",
            details={"error": repo_result.get("message")},
            evidence=[],
        )

    graph_result = build_graph(repo_path)
    if "error" in graph_result:
        return SkillOutput(
            summary="Knowledge graph generation failed",
            details={"error": graph_result["error"]},
            evidence=[],
        )

    repository_path = Path(repo_path).resolve()
    output_dir = repository_path / "analysis-outputs"
    output_dir.mkdir(parents=True, exist_ok=True)

    graph_data = graph_result.get("graph") or {
        "nodes": [],
        "edges": [],
    }
    json_path = output_dir / "knowledge-graph.json"
    html_path = output_dir / "knowledge-graph.html"

    json_path.write_text(json.dumps(graph_data, indent=2), encoding="utf-8")
    html_content = _build_visualization_html(graph_data)
    os.makedirs(os.path.dirname(str(html_path)), exist_ok=True)
    with open(html_path, "w", encoding="utf-8") as handle:
        handle.write(html_content)

    return SkillOutput(
        summary="Knowledge graph generated successfully",
        details={
            "graph": graph_data,
            "json_path": str(json_path),
            "html_path": str(html_path),
        },
        evidence=[f"Graph saved to {json_path}", f"Visualization saved to {html_path}"],
    )


def _build_visualization_html(graph_data: dict) -> str:
    """Create a lightweight HTML page that renders the graph with vis-network."""
    return f"""<!DOCTYPE html>
<html>
<head>
  <title>Knowledge Graph</title>
  <script type=\"text/javascript\" src=\"https://unpkg.com/vis-network/standalone/umd/vis-network.min.js\"></script>
  <style>
    #network {{
      width: 100%;
      height: 800px;
      border: 1px solid lightgray;
    }}
  </style>
</head>
<body>

<h2>Knowledge Graph</h2>
<div id=\"network\"></div>

<script>
  const nodes = new vis.DataSet({json.dumps(graph_data.get('nodes', []))});
  const edges = new vis.DataSet({json.dumps(graph_data.get('edges', []))});

  const container = document.getElementById('network');
  const data = {{ nodes: nodes, edges: edges }};
  
  const options = {{
    nodes: {{
      shape: 'dot',
      size: 10
    }},
    edges: {{
      arrows: 'to'
    }},
    physics: {{
      stabilization: false
    }}
  }};

  new vis.Network(container, data, options);
</script>

</body>
</html>
"""
