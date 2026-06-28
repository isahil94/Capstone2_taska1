# Architecture Diagrams

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                       User Commands                         │
│  /analyze  /architecture  /impact  /ask                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
┌──────────────────────▼──────────────────────────────────────┐
│                   Agent Runner                              │
│  ├─ Routes commands to appropriate agents                  │
│  ├─ Manages execution                                      │
│  └─ Saves outputs to JSON                                  │
└──────────────────────┬──────────────────────────────────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
┌───────▼────────┐ ┌──▼─────────┐ ┌─▼────────────┐
│ Comprehension  │ │Architecture│ │    Impact    │
│     Agent      │ │   Agent    │ │    Agent     │
├────────────────┤ ├────────────┤ ├──────────────┤
│ ├─ analyze()   │ │ analyze()  │ │ analyze()    │
│ └─ ask()       │ └────────────┘ └──────────────┘
└────────┬───────┘
         │
         │ Uses
         │
    ┌────▼─────────────────────────────────────┐
    │        Skill Layer (Workflows)           │
    ├─────────────────────────────────────────┤
    │  ├─ analyze_repo_skill                  │
    │  ├─ architecture_skill                  │
    │  ├─ impact_skill                        │
    │  └─ qna_skill                           │
    │                                         │
    │  Each skill:                            │
    │  ├─ Calls core functions               │
    │  ├─ Processes results                  │
    │  └─ Returns SkillOutput                │
    └────────┬──────────────────────────────┘
             │
             │ Calls
             │
    ┌────────▼──────────────────────────────────┐
    │    Core Engine (Deterministic Layer)      │
    ├───────────────────────────────────────────┤
    │  ├─ parser.py                            │
    │  │  └─ parse_repository()               │
    │  ├─ graph.py                             │
    │  │  ├─ build_graph()                    │
    │  │  └─ find_dependents()                │
    │  └─ repository.py                        │
    │     ├─ load_repository()                │
    │     └─ validate_repository()            │
    └────────┬──────────────────────────────┘
             │
             │ Wraps
             │
    ┌────────▼──────────────────────────────────┐
    │    Backend Services (Existing Code)       │
    ├───────────────────────────────────────────┤
    │  ├─ ParserService                        │
    │  ├─ RepositoryIntelligenceService        │
    │  └─ RepositoryService                    │
    │                                          │
    │  Returns parsed data and graphs          │
    └────────┬──────────────────────────────┘
             │
             │ Analyzes
             │
    ┌────────▼──────────────────────────────────┐
    │         Repository (Repository Input)     │
    │  Files, symbols, dependencies, etc.      │
    └───────────────────────────────────────────┘
```

## Data Flow - /analyze Command

```
User: /analyze /repo

    Agent Runner
         │
         ├─→ comprehension_agent.analyze(repo)
         │
         └──→ analyze_repo_skill.run(repo)
              │
              ├─→ load_repository(repo)        [core/repository.py]
              │   └─→ RepositoryService
              │
              ├─→ parse_repository(repo)       [core/parser.py]
              │   └─→ ParserService
              │
              ├─→ build_graph(repo)            [core/graph.py]
              │   └─→ RepositoryIntelligenceService
              │
              └─→ SkillOutput
                  ├─ summary: "Analyzed repo..."
                  ├─ details: {files, graphs, ...}
                  └─ evidence: ["Found X files", ...]
                      │
                      └──→ Saved to JSON
                           output/analysis-results/
```

## Data Flow - /architecture Command

```
User: /architecture /repo

    Agent Runner
         │
         ├─→ architecture_agent.analyze(repo)
         │
         └──→ architecture_skill.run(repo)
              │
              ├─→ load_repository(repo)
              │
              ├─→ build_graph(repo)
              │   └─→ Get architecture graph
              │
              ├─→ Analyze layers:
              │   ├─ API layer (controllers, endpoints)
              │   ├─ Service layer (managers, processors)
              │   ├─ Data layer (repositories, models)
              │   └─ Utility layer (helpers, utils)
              │
              └─→ SkillOutput
                  ├─ summary: "Architecture: X components"
                  ├─ details: {layers: {...}}
                  └─ evidence: ["API: X", "Service: Y", ...]
```

## Data Flow - /impact Command

```
User: /impact /repo src/main.py

    Agent Runner
         │
         ├─→ impact_agent.analyze(repo, file)
         │
         └──→ impact_skill.run(repo, file)
              │
              ├─→ load_repository(repo)
              │
              ├─→ build_graph(repo)
              │   └─→ Get dependency graph
              │
              ├─→ find_dependents(repo, file)
              │   └─→ Find all files that depend on src/main.py
              │
              ├─→ Trace transitive impact
              │
              └─→ SkillOutput
                  ├─ summary: "X direct, Y total impacted"
                  ├─ details: {risk_areas: [...]}
                  └─ evidence: ["Direct: X", "Risk: High/Med/Low"]
```

## Skill Composition Pattern

```
User Input (repo_path, param)
        │
        ├─ Step 1: Core Function
        │  └─→ validate/load data
        │      │
        │      └─ Handle error? → Return error SkillOutput
        │
        ├─ Step 2: Core Function
        │  └─→ Process data
        │      │
        │      └─ Handle error? → Return error SkillOutput
        │
        └─ Step 3: Format Output
           ├─ summary: Brief answer
           ├─ details: Full data
           ├─ evidence: Supporting facts
           │
           └─→ SkillOutput
               └─→ Saved to JSON
```

## Hook System

```
Event Trigger
     │
     ├─→ on_analysis_complete(repo, result)
     │   └─→ Generate report JSON
     │
     ├─→ on_file_modified(repo, file)
     │   └─→ run_agent("/impact", repo, file)
     │
     └─→ Custom hooks
         └─→ User-defined callbacks
```

## Storage Structure

```
.github/agents/
├── analysis-outputs/
│   ├── 20240115_103045_analyze.json
│   │   {
│   │     "command": "analyze",
│   │     "timestamp": "...",
│   │     "status": "success",
│   │     "summary": "...",
│   │     "details": {...},
│   │     "evidence": [...]
│   │   }
│   │
│   ├── 20240115_103102_architecture.json
│   ├── 20240115_103115_impact.json
│   └── 20240115_103130_analysis-report.json
│
└── [source code directories above]
```

## Component Interaction Matrix

```
           │ Core │ Skills │ Agents │ Runner │ Hooks
───────────┼──────┼────────┼────────┼────────┼──────
Core       │  -   │   ↓    │   -    │   -    │  -
Skills     │  ↑   │   -    │   ↓    │   -    │  ↑
Agents     │  -   │   ↑    │   -    │   ↓    │  -
Runner     │  -   │   -    │   ↑    │   -    │  ↓
Hooks      │  -   │   ↓    │   -    │   -    │  -

↑ = calls / uses
↓ = calls / returns to
- = no direct interaction
```

## Adding New Components (Patterns)

### New Skill Pattern

```
User Request
    │
    └──→ New Skill
         ├─ Uses existing core functions
         ├─ Might use existing skills
         ├─ Returns SkillOutput
         └─ Registered in new or existing agent
             └─ Route added in agent_runner.py
```

### New Agent Pattern

```
User Command
    │
    └──→ Agent Runner
         ├─ Routes to new agent
         │
         └──→ New Agent
              ├─ Calls one or more skills
              └─ Returns SkillOutput
                  └─ Formatted and saved
```

### New Core Function Pattern

```
Skill Needs Data
    │
    └──→ New Core Function
         ├─ Wraps backend service
         ├─ Handles errors
         └─ Returns dict
             └─ Consumed by skills
```

## Dependency Graph

```
Test Suite (test_system.py)
├── Tests Core Functions
├── Tests Skills
├── Tests Agents
├── Tests Agent Runner
├── Tests Hooks
└── Tests Output Format

All tests use:
├── agent_runner.py
│   ├── comprehension_agent.py
│   ├── architecture_agent.py
│   ├── impact_agent.py
│   └── skills/*.py
│       └── core/*.py
│           └── app.services (from backend)
```

---

**Key takeaway:** Clean separation of concerns allows each layer to be:
- Independently testable
- Easily extendable
- Reusable across different workflows
- Free of side effects or external dependencies
