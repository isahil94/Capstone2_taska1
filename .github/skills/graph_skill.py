"""Skill: Knowledge Graph Generation - build and persist an interactive graph."""

from __future__ import annotations

import json
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

    json_path.write_text(__import__("json").dumps(graph_data, indent=2), encoding="utf-8")
    html_path.write_text(_build_visualization_html(json_path), encoding="utf-8")

    return SkillOutput(
        summary="Knowledge graph generated successfully",
        details={
            "graph": graph_data,
            "json_path": str(json_path),
            "html_path": str(html_path),
        },
        evidence=[f"Graph saved to {json_path}", f"Visualization saved to {html_path}"],
    )


def _build_visualization_html(graph_json_path: Path) -> str:
    """Create a lightweight HTML page that renders the graph with vis-network."""
    template = """<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"utf-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
    <title>Knowledge Graph</title>
    <script type=\"text/javascript\" src=\"https://unpkg.com/vis-network/standalone/umd/vis-network.min.js\"></script>
    <style>
      body {{ font-family: Arial, sans-serif; margin: 0; background: #111827; color: #f9fafb; }}
      #container {{ width: 100vw; height: 100vh; }}
      #details {{ position: absolute; right: 16px; top: 16px; width: 280px; background: rgba(17,24,39,0.92); border: 1px solid #374151; border-radius: 8px; padding: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.25); }}
      #details h3 {{ margin-top: 0; }}
      .legend {{ margin-top: 12px; font-size: 12px; }}
      .legend div {{ margin: 4px 0; }}
    </style>
  </head>
  <body>
    <div id=\"container\"></div>
    <div id=\"details\">
      <h3>Node Details</h3>
      <div id=\"details-content\">Select a node to inspect it.</div>
    </div>
    <script>
      const graphPath = __GRAPH_PATH__;
      fetch(graphPath)
        .then((response) => response.json())
        .then((graph) => {{
          const nodes = new vis.DataSet(graph.nodes.map((node) => {{
            const colorMap = {{ file: '#3b82f6', class: '#16a34a', function: '#fbbf24' }};
            return {{
              id: node.id,
              label: node.label || node.id,
              color: colorMap[node.type] || '#94a3b8',
              shape: 'dot',
              size: node.type === 'file' ? 18 : 14,
              font: {{ color: '#f9fafb' }},
              title: JSON.stringify(node),
              nodeData: node,
            }};
          }}));
          const edges = new vis.DataSet(graph.edges.map((edge) => ({{
            id: edge.id,
            from: edge.source,
            to: edge.target,
            arrows: 'to',
            label: edge.type,
            color: '#94a3b8',
          }})));
          const container = document.getElementById('container');
          const data = {{ nodes, edges }};
          const options = {{
            physics: {{ stabilization: true }},
            interaction: {{ hover: true, navigationButtons: true, keyboard: true }},
            edges: {{ smooth: {{ type: 'dynamic' }} }},
          }};
          const network = new vis.Network(container, data, options);
          network.on('click', (params) => {{
            if (params.nodes.length) {{
              const nodeId = params.nodes[0];
              const node = nodes.get(nodeId).nodeData;
              document.getElementById('details-content').innerHTML = `
                <strong>ID:</strong> ${{node.id}}<br/>
                <strong>Type:</strong> ${{node.type}}<br/>
                <strong>Label:</strong> ${{node.label || ''}}<br/>
                <strong>Path:</strong> ${{node.path || ''}}
              `;
            }}
          }});
        }});
    </script>
  </body>
</html>
"""
    return template.replace("__GRAPH_PATH__", json.dumps(graph_json_path.as_posix()))
