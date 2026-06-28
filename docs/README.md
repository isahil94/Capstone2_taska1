# Quick Start - Agent System

## Installation

No additional packages needed. The system uses your existing backend services.

## Basic Usage

### Python Script

```python
import sys
sys.path.insert(0, "backend")

from .github.agents import run_agent

# Analyze repository
result = run_agent("/analyze", "f:/Projects/MyRepo")
print(result["summary"])

# Get architecture
result = run_agent("/architecture", "f:/Projects/MyRepo")
print(result["details"])

# Analyze impact
result = run_agent("/impact", "f:/Projects/MyRepo", "src/main.py")
print(result["evidence"])

# Ask question
result = run_agent("/ask", "f:/Projects/MyRepo", "How many classes?")
print(result["summary"])
```

### From Command Line

```bash
cd f:\Projects\Capstone 2

# Using Python
python -c "
import sys
sys.path.insert(0, 'backend')
from .github.agents import run_agent
result = run_agent('/analyze', '.')
print(result['summary'])
"
```

## Available Commands

| Command | Usage | Example |
|---------|-------|---------|
| `/analyze` | `run_agent("/analyze", repo_path)` | Full repository analysis |
| `/architecture` | `run_agent("/architecture", repo_path)` | Identify layers |
| `/impact` | `run_agent("/impact", repo_path, file)` | Change impact |
| `/ask` | `run_agent("/ask", repo_path, question)` | Answer questions |

## Output Location

All outputs saved to:
```
output/analysis-results/
```

Each file is JSON with:
- `command`: Which command was run
- `timestamp`: When it was run
- `status`: success/error
- `summary`: Quick answer
- `details`: Full data
- `evidence`: Supporting facts

## Core Functions (Low-Level)

You can also use core functions directly:

```python
from .github.agents.core import (
    parse_repository,
    build_graph,
    load_repository
)

# Parse only
result = parse_repository("f:/Projects/MyRepo")
print(f"Found {result['summary']['total_files']} files")

# Build graphs only
result = build_graph("f:/Projects/MyRepo")
print(f"Built {result['summary']['total_graphs']} graphs")

# Load repository info
result = load_repository("f:/Projects/MyRepo")
print(f"Valid: {result['is_valid']}")
```

## Skills (Medium-Level)

Run individual skills:

```python
from .github.agents.skills import (
    analyze_repo_skill,
    architecture_skill,
    impact_skill,
    qna_skill
)

# Analyze
output = analyze_repo_skill.run("f:/Projects/MyRepo")
print(output.summary)

# Architecture
output = architecture_skill.run("f:/Projects/MyRepo")
print(output.details)

# Impact
output = impact_skill.run("f:/Projects/MyRepo", "src/main.py")
print(output.evidence)

# Q&A
output = qna_skill.run("f:/Projects/MyRepo", "How many files?")
print(output.summary)
```

## Agents (Medium-Level)

Use agents directly:

```python
from .github.agents import ComprehensionAgent, ArchitectureAgent, ImpactAgent

comp = ComprehensionAgent()
arch = ArchitectureAgent()
impact = ImpactAgent()

# Each returns SkillOutput
result = comp.analyze("f:/Projects/MyRepo")
result = arch.analyze("f:/Projects/MyRepo")
result = impact.analyze("f:/Projects/MyRepo", "file.py")
```

## Hooks

Register event handlers:

```python
from .github.agents.hooks import register, trigger

def my_callback(repo_path: str):
    print(f"Event triggered for {repo_path}")

# Register
register("on_analysis_complete", my_callback)

# Trigger
trigger("on_analysis_complete", "f:/Projects/MyRepo")
```

## Example: Full Workflow

```python
import sys
import json
sys.path.insert(0, "backend")

from .github.agents import run_agent, hooks
from .github.agents.hooks import on_analysis_complete

# Register hook
hooks.register("on_analysis_complete", on_analysis_complete.on_analysis_complete)

# Run analysis
print("📊 Analyzing repository...")
result = run_agent("/analyze", "f:/Projects/MyRepo")

# Check result
if result["status"] == "success":
    print(f"✅ {result['summary']}")
    print(f"\nDetails: {json.dumps(result['details'], indent=2)}")
    print(f"\nEvidence:")
    for evidence in result["evidence"]:
        print(f"  • {evidence}")
    
    # Trigger hook
    hooks.trigger("on_analysis_complete", "f:/Projects/MyRepo", result)
else:
    print(f"❌ {result['message']}")

# Get architecture
print("\n🏗️ Analyzing architecture...")
result = run_agent("/architecture", "f:/Projects/MyRepo")
print(f"✅ {result['summary']}")

# Analyze impact
print("\n📈 Analyzing impact...")
result = run_agent("/impact", "f:/Projects/MyRepo", "src/main.py")
print(f"✅ {result['summary']}")
```

## Integration with Backend

The system automatically imports from your backend:

```
backend/
├── app/
│   ├── application/services/
│   │   ├── parser_service.py      ← Used by core/parser.py
│   │   ├── repository_intelligence_service.py  ← Used by core/graph.py
│   │   └── repository_service.py   ← Used by core/repository.py
│   └── container.py               ← Used by all core modules
```

All core functions automatically get services from the container.

## Next Steps

1. **Test the system:**
   ```bash
   python .github/agents/test_agent_system.py
   ```

2. **Add new skills:** See [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md#how-to-add-new-skills)

3. **Extend with new commands:** See [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md#how-to-add-new-agents)

4. **Integrate with VS Code:** Create a slash command that calls `run_agent()`

## Troubleshooting

**Q: "ModuleNotFoundError: No module named 'app'"**
```python
import sys
sys.path.insert(0, "backend")  # Add backend to path
```

**Q: "No graphs found"**
```python
# Need to analyze first
run_agent("/analyze", repo_path)
# Then graphs are built and available
```

**Q: "Invalid repository"**
```python
# Ensure repo_path is a valid git repository
# Or use absolute path
run_agent("/analyze", "f:/Projects/MyRepo")
```

---

**For detailed implementation guide, see:** [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)
