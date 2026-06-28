# GitHub Copilot Instructions

## Project Context

Before making any changes, read:
AI_CONTEXT.md

AI_CONTEXT.md is the single source of truth for:
- project objective
- architecture
- technology stack
- agent design
- workflows
- folder structure
- development phases
- design decisions

Do not duplicate or redefine information from AI_CONTEXT.md here.

---

# General Development Rules

## Architecture Compliance

Always follow the architecture defined in AI_CONTEXT.md.

Do not:
- introduce new frameworks without approval
- redesign existing architecture
- create additional agents without approval
- move responsibilities between components without reason

---

# Agent Design Rules

Agents are responsible for:

- reasoning
- planning
- orchestration
- decision making

Do not put deterministic processing inside agents.

Examples:

Repository scanning → Tool

Code parsing → Tool

Embedding generation → Tool

Graph traversal → Tool

---

# Code Generation Process

Before implementing a feature:

1. Identify the correct component
2. Explain impacted files
3. Explain why the implementation belongs there
4. Implement only required changes

Avoid unrelated refactoring.

---

# Coding Standards

Always:

- follow existing project structure
- write clean maintainable code
- add type hints
- handle errors properly
- keep functions focused
- create reusable components

Prefer simple solutions over unnecessary abstraction.

---

# Testing Rules

Every new feature must include tests.

Required:

- unit tests for business logic
- API tests for endpoints
- workflow tests for LangGraph changes

Do not mark work complete without validation.

---

# Dependency Rules

Before adding a dependency explain:

- why it is required
- what problem it solves
- alternatives considered

Avoid unnecessary packages.

---

# LLM Usage Rules

When implementing AI features:

Prefer:

- retrieval
- context filtering
- citations
- deterministic preprocessing

Avoid:

- sending unnecessary data to LLM
- repository-wide prompts
- unsupported assumptions

---

# Security Rules

Never commit:

- secrets
- API keys
- passwords
- tokens

Use environment configuration.

---

# Documentation Rules

When changing architecture or behaviour:

Update relevant documentation.

Keep documentation aligned with AI_CONTEXT.md.

---

# Git Rules

Create meaningful commits.

Use format:

feat:
fix:
refactor:
docs:
test:

---

# Completion Checklist

Before finishing a task verify:

[ ] AI_CONTEXT.md rules followed

[ ] Correct component updated

[ ] No unnecessary architecture changes

[ ] Tests added

[ ] No duplicate logic introduced

[ ] Documentation updated if required