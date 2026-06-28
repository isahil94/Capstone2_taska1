# Agentic AI Code Intelligence Platform

## Purpose

Build an Agentic AI Code Intelligence Platform that helps developers understand existing software repositories through repository intelligence, retrieval, reasoning, documentation, architecture visualization, and change impact analysis.

The platform analyzes existing repositories. It does **not** generate, modify, or autonomously write application code.

---

## Core Objectives

Given an unfamiliar repository, the system should:

* Analyze repository structure
* Build repository intelligence
* Understand relationships
* Explain architecture and execution flow
* Answer developer questions using repository evidence
* Generate technical documentation
* Analyze change impact

---

## Architecture Principles

* Repository Intelligence is the canonical source of repository knowledge.
* All agents, tools, and skills consume repository information through Repository Intelligence.
* Deterministic work belongs in services.
* Tools expose deterministic capabilities to agents.
* Skills orchestrate multiple tools into reusable developer capabilities.
* Agents perform planning, reasoning, orchestration, and validation only.
* Agents never scan or parse repositories directly.
* AI responses must always be grounded in verified repository evidence.

---

## High-Level Architecture

```text
Repository
    │
    ▼
Repository Intelligence
    │
    ▼
Services
    │
    ▼
Tools
    │
    ▼
Skills
    │
    ▼
Context Builder
    │
    ▼
LangGraph Workflow
    │
    ▼
Evidence-Based Response
```

---

## Repository Intelligence

Repository Intelligence is the shared knowledge layer used by the entire system.

Capabilities include:

* Repository scanning
* AST parsing
* Symbol extraction
* Dependency analysis
* Knowledge graph construction
* Embedding generation
* Git analysis

---

## Services

Services implement deterministic processing.

### Repository Scanner

* File discovery
* Metadata collection
* Language detection
* Repository statistics

### Code Parser

Technology: **Tree-sitter**

Provides:

* AST generation
* Classes
* Functions
* Methods
* Imports
* Symbols

### Knowledge Graph Service

Maintains repository relationships.

**Node Types**

* Repository
* File
* Module
* Class
* Function
* API
* Database Entity

**Relationship Types**

* contains
* imports
* calls
* depends_on
* reads
* writes
* modifies

### Embedding Service

* Code chunking
* Embedding generation
* Semantic retrieval

### Git Analysis Service

* Git history
* Changed files
* Change impact analysis

### Context Builder

Builds execution context from:

* User query
* Repository metadata
* Retrieved files
* Symbols
* Graph relationships
* Semantic retrieval
* Architecture documents
* Policies

Agents reason only over Context Builder output.

---

## Tools

Tools expose deterministic capabilities to agents.

Current tools include:

* Repository Scan
* Repository Metadata
* Code Parsing
* Symbol Lookup
* Dependency Search
* Graph Traversal
* Semantic Search
* Git History
* Context Builder

---

## Skills

Skills orchestrate one or more tools into reusable developer capabilities.

Current skills:

* Repository Understanding
* Code Comprehension
* Architecture Analysis
* Documentation Generation
* Change Impact Analysis

---

## Visualization

Visualization tools generate graphical representations of repository intelligence.

Supported visualizations:

* Architecture Diagram
* Code Flow Diagram
* Dependency Graph
* Call Graph
* Change Impact Diagram

---

## Agents

| Agent                   | Responsibility                                                                |
| ----------------------- | ----------------------------------------------------------------------------- |
| Planner                 | Intent classification and workflow planning                                   |
| Repository Intelligence | Repository metadata and knowledge access (never scans or parses repositories) |
| Analysis                | Technical reasoning using retrieved repository evidence                       |
| Documentation           | Generate developer-facing documentation                                       |
| Reviewer                | Validate correctness, evidence, and confidence                                |

---

## Storage

| Technology            | Purpose                             |
| --------------------- | ----------------------------------- |
| SQLite                | Repository metadata, files, symbols |
| ChromaDB              | Embeddings and semantic retrieval   |
| NetworkX              | Repository knowledge graph          |
| LangGraph Checkpoints | Workflow state and recovery         |

---

## Retrieval

Hybrid retrieval combines:

* Vector Search
* Graph Search
* Symbol Search

Retrieved results are reranked before reaching the Context Builder.

---

## Guardrails

Before execution:

* Validate repository
* Validate resources
* Validate permissions

During execution:

* Prevent hallucinations using evidence
* Require confidence
* Reject unrelated requests
* Protect sensitive repository data

---

## Hooks

Execution hooks:

* Pre Analysis
* Before Model Call
* After Model Response
* Repository Processing
* Audit

---

## Triggers

System workflows begin from:

* Repository Added
* Repository Updated
* User Query
* Analysis Completed

---

## Technology Stack

### Backend

* Python 3.12
* FastAPI
* LangGraph
* LangChain
* SQLAlchemy
* SQLite

### AI

| Purpose                  | Model                  |
| ------------------------ | ---------------------- |
| Code Understanding       | Qwen Code              |
| Planning & Validation    | Gemma 3                |
| Embeddings               | BAAI/bge-small-en-v1.5 |
| Reranking                | BAAI/bge-reranker-base |
| Optional Cloud Reasoning | Gemini                 |

### Frontend

* React
* TypeScript
* React Flow
* Mermaid
* Monaco Editor

---

## Governance

Production requirements:

* Structured logging
* Auditing
* Monitoring
* Quality gates
* Access control
* Policy enforcement

---

## Development Process

```text
Implement
    ↓
Review
    ↓
Test
    ↓
Refactor
    ↓
Commit
```

Build incrementally. Do not implement the entire platform at once.

---

## Development Phases

1. Repository Scanner
2. Code Parser
3. Knowledge Graph
4. Semantic Retrieval
5. LangGraph Workflow
6. API Layer
7. Frontend
