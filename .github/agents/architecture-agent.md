---
name: architecture-agent
description: |
  Identifies architectural layers and structure within a repository. This agent maps files and dependencies into a coherent architecture model.
---

# Architecture Agent

This agent handles the `/architecture` command.

## Runtime implementation

The runtime behavior is implemented in Python:

- `.github/agents/architecture_agent.py`
- `.github/agents/agent_runner.py`

## Behavior

- It invokes `architecture_skill.run(repo_path)` to inspect the repository, build architecture graphs, and produce a layer summary.
