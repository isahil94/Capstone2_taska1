# Agents and Skills

This folder documents agent and skill usage for the repository intelligence platform.

Agents

- `Comprehension` — orchestrates repository analysis workflows and compiles evidence-grounded explanations.
- `Reviewer` — validates agent outputs against repository evidence and enforces guardrails.

Skills

- `Repository Understanding` — orchestrates scanning + parsing + graph build to produce repository intelligence.
- `Architecture Mapping` — produces architecture graphs (dependency, call, class, import, architecture).
- `Change Impact Analysis` — traverses persisted graphs to compute affected nodes and files.

How to add a new skill

1. Create a deterministic service under `app/application/services/`.
2. Expose a route in `app/presentation/api/routes/` if needed.
3. Add wiring to `app/container.py` for DI.
4. Add a small README in `.github/skills/` describing the skill.
