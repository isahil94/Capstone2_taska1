---
name: run-agent
summary: |
  Runtime entrypoint for the `.github.agents` package. This manifest documents how the Python agent runner dispatches commands.
---

# Agent Runner Manifest

This manifest documents the runtime command router used by the `.github.agents` package.

## Runtime implementation

- `.github/agents/agent_runner.py`

## Supported commands

- `/analyze` → `ComprehensionAgent.analyze()`
- `/architecture` → `ArchitectureAgent.analyze()`
- `/impact` → `ImpactAgent.analyze()`
- `/ask` → `ComprehensionAgent.ask()`
