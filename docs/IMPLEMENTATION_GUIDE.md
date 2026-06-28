# Agent + Skill System - Complete Implementation Guide

## Architecture Overview

```
Command (/analyze, /architecture, /impact, /ask)
        ↓
Agent Runner (routes command)
        ↓
Agent (orchestrates workflow)
        ↓
Skill (executes workflow)
        ↓
Core Engine (calls services)
        ↓
Services (parser, graph, repository)
```

## Directory Structure

```
.github/agents/
├── core/                          # Core engine wrappers
│   ├── __init__.py
│   ├── parser.py                 # Parse repository
│   ├── graph.py                  # Build graphs
│   └── repository.py             # Load repository
│
├── skills/                        # Reusable workflows
│   ├── __init__.py               # SkillOutput & utilities
│   ├── analyze_repo_skill.py      # Analyze repository
│   ├── architecture_skill.py      # Identify layers
│   ├── impact_skill.py            # Trace dependencies
│   └── qna_skill.py               # Answer questions
│
├── hooks/                         # Event-driven automation
│   ├── __init__.py
│   ├── on_analysis_complete.py   # Generate reports
│   └── on_file_modified.py       # Trigger impact
│
├── __init__.py                    # Public API
├── comprehension_agent.py         # Handles /analyze, /ask
├── architecture_agent.py          # Handles /architecture
├── impact_agent.py                # Handles /impact
├── agent_runner.py                # Routes commands
│
└── analysis-outputs/              # Generated reports (JSON)
```

## Key Concepts

### 1. Core Engine (Deterministic Layer)

**Location:** `.github/agents/core/`

Wraps existing services:
- `parser.py`: Wraps `ParserService`
- `graph.py`: Wraps `RepositoryIntelligenceService`
- `repository.py`: Wraps `RepositoryService`

Returns structured dictionaries. No AI, no prompting.

### 2. Skills (Reusable Workflows)

**Location:** `.github/agents/skills/`

Each skill:
- Has a `run()` function
- Calls core engine functions
- Returns `SkillOutput` (summary + details + evidence)
- Is independent and reusable

**Example Pattern:**

```python
# skills/my_skill.py
from . import SkillOutput
from ..core import some_function

def run(repo_path: str, param: str) -> SkillOutput:
    try:
        data = some_function(repo_path, param)
        return SkillOutput(
            summary="Result summary",
            details={"key": data},
            evidence=["Finding 1", "Finding 2"]
        )
    except Exception as e:
        return SkillOutput(
            summary="Failed",
            details={"error": str(e)},
            evidence=[]
        )
```

### 3. Agents (Orchestrators)

**Location:** `.github/agents/`

Each agent:
- Has methods for different commands
- Calls skills
- Returns `SkillOutput`
- No business logic (just orchestration)

**Example Pattern:**

```python
# agents/my_agent.py
from .skills import my_skill

class MyAgent:
    def do_something(self, repo_path: str) -> SkillOutput:
        return my_skill.run(repo_path)
```

### 4. Agent Runner (Routing)

**Location:** `.github/agents/agent_runner.py`

Maps commands to agents:

```
/analyze       → ComprehensionAgent.analyze()
/architecture  → ArchitectureAgent.analyze()
/impact        → ImpactAgent.analyze()
/ask           → ComprehensionAgent.ask()
```

Usage:

```python
from .agents import run_agent

result = run_agent("/analyze", "/path/to/repo")
result = run_agent("/impact", "/path/to/repo", "src/main.py")
result = run_agent("/ask", "/path/to/repo", "How many files?")
```

### 5. Hooks (Event-Driven)

**Location:** `.github/agents/hooks/`

Trigger automatically:
- `on_analysis_complete`: Generates reports
- `on_file_modified`: Triggers impact analysis

**Usage:**

```python
from .agents import hooks

def my_hook(repo_path: str):
    # Do something
    pass

hooks.register("on_analysis_complete", my_hook)
hooks.trigger("on_analysis_complete", repo_path)
```

## Working Examples

### Example 1: Analyze Repository

```python
from .agents import run_agent

result = run_agent("/analyze", "f:/Projects/MyRepo")

# Returns:
# {
#   "command": "analyze",
#   "status": "success",
#   "summary": "Analyzed repository MyRepo...",
#   "details": { "files": {...}, "graphs": {...} },
#   "evidence": ["Found 50 files", "Identified 20 classes", ...]
# }
```

### Example 2: Analyze Architecture

```python
result = run_agent("/architecture", "f:/Projects/MyRepo")

# Returns architecture layers (API, Service, Data)
```

### Example 3: Impact Analysis

```python
result = run_agent("/impact", "f:/Projects/MyRepo", "src/main.py")

# Returns files affected by changes to src/main.py
```

### Example 4: Ask Question

```python
result = run_agent("/ask", "f:/Projects/MyRepo", "How many classes are there?")

# Returns: "Found 20 classes in the repository."
```

## How to Add New Skills

### Step 1: Create Skill File

Create `.github/agents/skills/my_skill.py`:

```python
from . import SkillOutput
from ..core import your_core_function

def run(repo_path: str, param: str) -> SkillOutput:
    """Your skill description."""
    try:
        data = your_core_function(repo_path, param)
        
        return SkillOutput(
            summary="Summary of what was found",
            details={"result": data},
            evidence=["Evidence 1", "Evidence 2"]
        )
    except Exception as e:
        return SkillOutput(
            summary="Skill failed",
            details={"error": str(e)},
            evidence=[]
        )
```

### Step 2: Create or Update Agent

Update existing agent or create new `.github/agents/my_agent.py`:

```python
from .skills import my_skill

class MyAgent:
    def my_command(self, repo_path: str, param: str) -> SkillOutput:
        return my_skill.run(repo_path, param)
```

### Step 3: Update Agent Runner

Add route in `agent_runner.py`:

```python
elif command == "/my_command":
    if not args:
        return self._error("Requires parameter")
    return self._execute_my_command(repo_path, args[0])

def _execute_my_command(self, repo_path: str, param: str) -> dict[str, Any]:
    result = self.my_agent.my_command(repo_path, param)
    return self._format_result(result, "my_command")
```

### Step 4: Test It

```python
from .agents import run_agent

result = run_agent("/my_command", "f:/Projects/MyRepo", "param")
print(result)
```

## How to Add New Core Functions

### Step 1: Create Core Function

Create or update `.github/agents/core/my_module.py`:

```python
from app.container import get_container

def my_function(repo_path: str, param: str) -> dict[str, Any]:
    """Deterministic logic using existing services."""
    container = get_container()
    service = container.my_service()
    
    try:
        result = service.do_something(repo_path, param)
        return {
            "result": result,
            "status": "success"
        }
    except Exception as e:
        return {
            "error": str(e),
            "status": "error"
        }
```

### Step 2: Export from Core

Update `.github/agents/core/__init__.py`:

```python
from .my_module import my_function

__all__ = [..., "my_function"]
```

### Step 3: Use in Skills

```python
from ..core import my_function

def run(...) -> SkillOutput:
    data = my_function(repo_path, param)
    # Process and return SkillOutput
```

## How to Add New Hooks

### Step 1: Create Hook File

Create `.github/agents/hooks/my_hook.py`:

```python
def on_my_event(repo_path: str, param: str) -> None:
    """Hook callback."""
    print(f"Event triggered: {repo_path}, {param}")
    # Do something
```

### Step 2: Register Hook

```python
from .agents import hooks
from .agents.hooks.my_hook import on_my_event

hooks.register("on_my_event", on_my_event)
```

### Step 3: Trigger Hook

```python
hooks.trigger("on_my_event", repo_path, param)
```

## Design Principles

1. **Separation of Concerns**
   - Core: Logic only
   - Skills: Workflows
   - Agents: Orchestration
   - Runners: Routing

2. **No Duplication**
   - Shared logic goes in Core
   - Workflows in Skills
   - Skills are reusable

3. **Structured Output**
   - All outputs: `SkillOutput` or `dict`
   - Always have: summary + details + evidence
   - Save to JSON for persistence

4. **Error Handling**
   - Try-catch in skills
   - Return error SkillOutput
   - Never crash

5. **Local Only**
   - No HTTP APIs
   - No external services
   - File-based persistence (JSON)

## Storage

All outputs saved to:
```
output/analysis-results/
├── YYYYMMDD_HHMMSS_analyze.json
├── YYYYMMDD_HHMMSS_architecture.json
├── YYYYMMDD_HHMMSS_impact.json
└── YYYYMMDD_HHMMSS_analysis-report.json
```

Each file:
```json
{
  "command": "analyze",
  "timestamp": "2024-01-15T10:30:45.123456",
  "status": "success",
  "summary": "...",
  "details": {...},
  "evidence": [...]
}
```

## Testing

### Test a Skill

```python
from .agents.skills import my_skill

result = my_skill.run("f:/Projects/MyRepo", "param")
assert result.summary is not None
assert result.details is not None
```

### Test an Agent

```python
from .agents import MyAgent

agent = MyAgent()
result = agent.my_command("f:/Projects/MyRepo", "param")
assert result.summary is not None
```

### Test Agent Runner

```python
from .agents import run_agent

result = run_agent("/my_command", "f:/Projects/MyRepo", "param")
assert result["status"] == "success"
```

## Next Steps

1. ✅ Core engine wrappers created
2. ✅ Four example skills created
3. ✅ Three example agents created
4. ✅ Agent runner created
5. ✅ Hook system created

To extend:
1. Create new skills (`.github/agents/skills/new_skill.py`)
2. Create new agents or update existing ones
3. Register routes in agent_runner
4. Test with `run_agent()`

## Common Patterns

### Pattern: Multi-Step Workflow

```python
def run(repo_path: str) -> SkillOutput:
    # Step 1
    data1 = function1(repo_path)
    if "error" in data1:
        return SkillOutput(summary="Failed at step 1", ...)
    
    # Step 2
    data2 = function2(data1)
    if "error" in data2:
        return SkillOutput(summary="Failed at step 2", ...)
    
    # Success
    return SkillOutput(
        summary="All steps completed",
        details={...},
        evidence=[...]
    )
```

### Pattern: Conditional Logic

```python
def run(repo_path: str, param: str) -> SkillOutput:
    if param == "type_a":
        return process_type_a(repo_path)
    elif param == "type_b":
        return process_type_b(repo_path)
    else:
        return SkillOutput(summary="Unknown type", ...)
```

### Pattern: Aggregation

```python
def run(repo_path: str) -> SkillOutput:
    results = []
    for item in items:
        result = process(repo_path, item)
        results.append(result)
    
    return SkillOutput(
        summary=f"Processed {len(results)} items",
        details={"results": results},
        evidence=[...]
    )
```

## Troubleshooting

### Issue: "No module named 'app.container'"

**Solution:** Ensure you're running from the correct working directory. The backend path must be in `sys.path`.

```python
import sys
sys.path.insert(0, "f:/Projects/Capstone 2/backend")
```

### Issue: Skills return empty results

**Solution:** Check that core functions are working. Test individually:

```python
from .agents.core import parse_repository
result = parse_repository("f:/Projects/MyRepo")
print(result)  # Check for errors
```

### Issue: "Agent execution failed"

**Solution:** Check the stored JSON output in `output/analysis-results/` for error details.

---

## Summary

You now have:
- ✅ Complete Agent + Skill system
- ✅ Core engine wrappers
- ✅ 4 working skills (analyze, architecture, impact, qna)
- ✅ 3 working agents
- ✅ Agent runner with command routing
- ✅ Hook system for automation
- ✅ Local JSON-based storage
- ✅ Clear extension patterns

All code is local, no backend API, uses existing services.
