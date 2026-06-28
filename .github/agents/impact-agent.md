---
name: impact-agent
description: |
  Evaluates the potential impact of changes to a target file. This agent traces dependencies and identifies likely affected files.
---

# Impact Agent

This agent handles the `/impact` command.

## Runtime implementation

The runtime behavior is implemented in Python:

- `.github/agents/impact_agent.py`
- `.github/agents/agent_runner.py`

## Behavior

- It invokes `impact_skill.run(repo_path, target_file)` to compute which files are affected by changes.
