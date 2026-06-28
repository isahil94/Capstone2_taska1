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
    # Store original nodes with all metadata
    raw_nodes = graph_data.get("nodes", [])
    raw_edges = graph_data.get("edges", [])

    # Prepare nodes for vis-network (id and label only)
    nodes_data = [
        {
            "id": node.get("id"),
            "label": node.get("label", node.get("id", "")),
            "type": node.get("type", ""),
        }
        for node in raw_nodes
    ]

    # Prepare edges for vis-network (source/target to from/to)
    edges_data = [
        {
            "from": edge.get("source"),
            "to": edge.get("target"),
            "arrows": "to",
        }
        for edge in raw_edges
    ]

    return f"""<!DOCTYPE html>
<html>
<head>
  <title>Knowledge Graph</title>
  <script type=\"text/javascript\" src=\"https://unpkg.com/vis-network/standalone/umd/vis-network.min.js\"></script>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 0; padding: 10px; }}
    #controls {{
      margin-bottom: 15px;
      padding: 10px;
      background: #f5f5f5;
      border-radius: 4px;
    }}
    .control-item {{
      display: inline-block;
      margin-right: 20px;
    }}
    #network {{
      width: 100%;
      height: 800px;
      border: 1px solid lightgray;
      border-radius: 4px;
    }}
  </style>
</head>
<body>

<h2>Knowledge Graph</h2>

<div id=\"controls\">
  <div class=\"control-item\">
    <label>
      <input type=\"checkbox\" id=\"hideInit\">
      Hide __init__.py
    </label>
  </div>
  <div class=\"control-item\">
    <label>
      <input type=\"checkbox\" id=\"onlyConnected\">
      Only Connected Nodes
    </label>
  </div>
  <div class=\"control-item\">
    <label>
      <input type=\"checkbox\" id=\"onlyFiles\">
      Only File Nodes
    </label>
  </div>
</div>

<div id=\"network\"></div>

<script>
  // Store original data
  const rawNodes = {json.dumps(nodes_data)};
  const rawEdges = {json.dumps(edges_data)};
  
  let network;
  let container = document.getElementById('network');
  let options = {{
    nodes: {{
      shape: 'dot',
      size: 10
    }},
    edges: {{
      arrows: 'to'
    }},
    physics: {{
      stabilization: true,
      stabilization: {{ iterations: 200 }}
    }}
  }};

  // Filter and update graph
  function applyFilters() {{
    const hideInit = document.getElementById('hideInit').checked;
    const onlyConnected = document.getElementById('onlyConnected').checked;
    const onlyFiles = document.getElementById('onlyFiles').checked;

    // Filter nodes
    let filteredNodes = rawNodes.filter(node => {{
      // Rule 1: Hide __init__.py if checked
      if (hideInit && node.label && node.label.includes('__init__')) {{
        return false;
      }}
      // Rule 3: Only file nodes if checked
      if (onlyFiles && node.type !== 'file') {{
        return false;
      }}
      return true;
    }});

    // Rule 2: Only connected nodes if checked
    if (onlyConnected) {{
      const connectedNodeIds = new Set();
      rawEdges.forEach(edge => {{
        connectedNodeIds.add(edge.from);
        connectedNodeIds.add(edge.to);
      }});
      filteredNodes = filteredNodes.filter(node => connectedNodeIds.has(node.id));
    }}

    // Transform nodes for vis-network
    const visNodes = filteredNodes.map(n => ({{
      id: n.id,
      label: n.label
    }}));

    // Filter edges to only include those between visible nodes
    const visibleNodeIds = new Set(filteredNodes.map(n => n.id));
    const visEdges = rawEdges.filter(e => 
      visibleNodeIds.has(e.from) && visibleNodeIds.has(e.to)
    );

    // Update network
    network.setData({{
      nodes: new vis.DataSet(visNodes),
      edges: new vis.DataSet(visEdges)
    }});
  }}

  // Initialize network
  function initNetwork() {{
    const visNodes = rawNodes.map(n => ({{
      id: n.id,
      label: n.label
    }}));
    
    network = new vis.Network(container, {{
      nodes: new vis.DataSet(visNodes),
      edges: new vis.DataSet(rawEdges)
    }}, options);
  }}

  // Setup event listeners
  document.getElementById('hideInit').addEventListener('change', applyFilters);
  document.getElementById('onlyConnected').addEventListener('change', applyFilters);
  document.getElementById('onlyFiles').addEventListener('change', applyFilters);

  // Initialize on load
  initNetwork();
</script>

</body>
</html>
"""
