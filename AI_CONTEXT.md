# Agentic Code Comprehension Platform

## Purpose

Build an Agentic AI Code Comprehension Platform inside VS Code + Copilot that enables developers to understand unfamiliar repositories through:

- Repository intelligence
- Graph-based analysis
- Agent-driven workflows
- Evidence-grounded reasoning

The platform focuses on analyzing existing codebases, not generating or modifying code.

## Core Objectives

Given an unfamiliar repository, the system should:

- Analyze repository structure
- Build repository intelligence
- Understand relationships between components
- Explain architecture and execution flow
- Answer developer questions using repository evidence
- Generate technical and onboarding documentation
- Analyze change impact
- Create interactive knowledge graphs

## Architecture Principles

- Repository Intelligence is the single source of truth
- All agents and skills must use structured repository data
- Deterministic logic must be implemented in core modules
- Agents must NOT parse or scan repositories directly
- Skills orchestrate workflows using core functions
- Agents handle planning, reasoning, and validation only
- Responses must always be evidence-grounded
- The system minimizes runtime prompting using curated prompts

## High-Level Architecture (No Backend)

```
VS Code + Copilot
    ↓
Slash Commands / Hooks
    ↓
Agent Layer
    ↓
Skill Layer
    ↓
Tool Layer
    ↓
Core Engine (Parser + Graph + Intelligence)
    ↓
Local Storage (JSON / Memory)
```

## User Interaction

Users interact through slash commands:

- `/analyze`
- `/architecture`
- `/impact <file>`
- `/graph`
- `/ask <question>`

These commands trigger agents, not direct logic.

## Agent Layer

Agents are runtime orchestrators.

### Agents

**Comprehension Agent**
- Handles repository analysis
- Answers developer questions

**Architecture Agent**
- Explains system design
- Identifies patterns and layers

**Impact Agent**
- Performs dependency tracing
- Calculates change impact

**Reviewer Agent** (optional but recommended)
- Validates outputs
- Ensures correctness and grounding

### Agent Responsibilities

- Interpret user intent
- Select appropriate skills
- Orchestrate execution
- Validate results
- Generate structured responses


## Agent Execution Model

All agents follow:
```
PLAN → ACT → RUN → SELF-CHECK → OUTPUT → HUMAN APPROVAL
```

## Skills Layer (Workflows)

Skills are executable workflows (not documentation).

### Core Skills

**Analyze Repository**
- Parse repository
- Build dependency graph
- Generate summary

**Architecture Analysis**
- Identify layers (API, service, data)
- Detect structure patterns

**Execution Flow**
- Trace request paths
- Use call graph

**Developer Q&A**
- Answer questions using repository data

**Change Impact Analysis**
- Identify affected modules
- Detect downstream impact

**Documentation Generation**
- Create reports and onboarding guides

### Skill Rules

- Skills orchestrate tools + core functions
- No business logic inside skills
- Must return structured results

## Tool Layer

Tools are thin wrappers over core functions.

### Example Tools

- `parse_repository(repo_path)`
- `build_dependency_graph(data)`
- `get_call_graph(graph)`
- `find_references(symbol)`

### Tools Must

- Call core engine functions
- Never implement logic


## Core Engine (Deterministic Layer)

This replaces backend services.

### Modules

**Parser**
- Parses code using Tree-sitter
- Extracts files, classes, functions

**Graph Builder**
- Builds:
  - Dependency graph
  - Call graph
  - Relationships

**Repository Loader**
- Loads files and metadata

### Rule

Core engine contains ALL deterministic logic. No AI inside core layer.

## Repository Intelligence

Repository Intelligence is the runtime data layer.

### Represents

- Files and modules
- Classes and functions
- Imports and dependencies
- Call relationships
- Architecture structure

### Data Format

Stored locally as:
- `.knowledge-graph.json`
- `.symbols.json`

## Visualization & Outputs

### Outputs

```
analysis-outputs/
├── {timestamp}-comprehensive-report.md
├── {timestamp}-knowledge-graph.html
├── {timestamp}-architecture-diagram.mermaid
├── {timestamp}-workflow-paths.md
├── {timestamp}-component-catalog.md
├── {timestamp}-impact-analysis.md
└── {timestamp}-index.md
```

### Visualizations

- Interactive knowledge graph
- Dependency graph
- Call graph
- Architecture diagrams

## Hooks (Event-Driven Automation)

Hooks trigger agents automatically.

### Supported Hooks

**onCodebaseLoad**
- Run repository analysis

**onFileModified**
- Trigger impact analysis

**onAnalysisComplete**
- Generate reports

**onImpactQuery**
- Execute impact agent

**Pre-commit Hook**
- Validate changes

**PR Hook**
- Run reviewer agent

## Prompt System

All prompts must be:
- Predefined
- Embedded
- Reusable

### Types

- Agent prompts
- Skill prompts
- Validation prompts

### Rule

No ad-hoc prompting during execution. All intelligence driven by curated prompts.

## Guardrails

### Before Execution

- Validate repository
- Validate input

### During Execution

- Prevent hallucination
- Use only repository evidence

### After Execution

- Validate output
- Ensure consistency

## Storage

No database is required.

### Local Storage

- JSON files
- In-memory data structures

## Development Approach

```
Implement core engine
    ↓
Add skills
    ↓
Add agents
    ↓
Add hooks
    ↓
Connect commands
    ↓
Add visualization
```

