---
name: comprehension-agent
description: |
  Orchestrates repository comprehension workflows. This agent performs full repository analysis and answers natural-language questions about the codebase.
---

# Comprehension Agent

This agent handles the following commands:

- `/analyze` — analyze the repository and produce a structured summary with evidence.
- `/ask` — answer a repository-related question using repository intelligence.

## Runtime implementation

The runtime behavior is implemented in Python:

- `.github/agents/comprehension_agent.py`
- `.github/agents/agent_runner.py`

## Behavior

- For `/analyze`, it invokes `analyze_repo_skill.run(repo_path)` to inspect the repository, parse files, build graphs, and generate a summary.
- For `/ask`, it invokes `qna_skill.run(repo_path, question)` to answer the question with evidence from the repository.
