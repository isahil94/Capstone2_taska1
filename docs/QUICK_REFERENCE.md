# Agent System: Quick Reference & Troubleshooting

## Quick Command Reference

```python
from .github.agents import run_agent

# Analyze a repository
result = run_agent("/analyze", "f:/Projects/MyRepo")

# Analyze architecture
result = run_agent("/architecture", "f:/Projects/MyRepo")

# Analyze change impact
result = run_agent("/impact", "f:/Projects/MyRepo", "src/main.py")

# Answer question
result = run_agent("/ask", "f:/Projects/MyRepo", "How many files?")
```

## Result Structure

```python
result = {
    "command": "analyze",
    "timestamp": "2024-01-15T10:30:45.123456",
    "status": "success",  # or "error"
    "summary": "Analyzed repository MyRepo (42 files, 15 classes)",
    "details": {
        "repository": {...},
        "files": {...},
        "graphs": {...}
    },
    "evidence": [
        "Found 42 source files",
        "Identified 15 classes",
        ...
    ]
}

# Access results
print(result["summary"])
for evidence in result["evidence"]:
    print(f"  • {evidence}")
```

## Troubleshooting

### Problem: "ModuleNotFoundError: No module named 'app'"

**Solution:** Ensure backend is in Python path
```python
import sys
sys.path.insert(0, "backend")

from .github.agents import run_agent
```

### Problem: "Invalid repository" error

**Solution:** Use absolute path to valid git repository
```python
from pathlib import Path

repo_path = Path("f:/Projects/MyRepo").resolve()
result = run_agent("/analyze", str(repo_path))
```

### Problem: "No graphs found" for /architecture

**Solution:** Run /analyze first to build graphs
```python
# Step 1: Analyze (builds graphs)
run_agent("/analyze", repo_path)

# Step 2: Now architecture works
run_agent("/architecture", repo_path)
```

### Problem: Skills return empty results

**Solution:** Check that core functions work independently
```python
from .github.agents.core import parse_repository

result = parse_repository("f:/Projects/MyRepo")
print(result)  # Check for "error" key
```

### Problem: "Agent execution failed" error message

**Solution:** Check JSON output files
```
output/analysis-results/
├── Latest_timestamp_command.json   ← Contains error details
```

### Problem: "No such file or directory" in output save

**Solution:** Ensure `output/analysis-results/` exists
```bash
mkdir -p output/analysis-results
```

## Common Issues & Solutions

| Issue | Solution |
|-------|----------|
| Import errors | Add backend to sys.path |
| Invalid repo | Use absolute path to .git repo |
| Empty results | Run /analyze first |
| No output files | Check output/analysis-results/ |
| Hook not triggering | Register before trigger |
| Memory issues (large repo) | Core functions handle pagination |
| Slow analysis | Normal - parsing large repos takes time |

## Performance Tips

1. **First run is slowest** - Creates graphs
2. **Subsequent runs faster** - Reuses stored data
3. **Large repos** - May take 30-60 seconds
4. **Use /ask for quick stats** - Faster than full analysis

## Output Location

All results saved to:
```
output/analysis-results/YYYYMMDD_HHMMSS_COMMAND.json
```

View latest:
```bash
ls -lt output/analysis-results/ | head -1
```

## Environment Requirements

- Python 3.8+
- Backend code in `backend/`
- Git repository to analyze
- ~100MB disk space for outputs

## Testing Checklist

- [ ] `python -m .github.agents.examples.test_system`
- [ ] Check `output/analysis-results/` has JSON files
- [ ] Read IMPLEMENTATION_GUIDE.md
- [ ] Try custom question in /ask
- [ ] Run /analyze on your repository

## Integration Checklist

- [ ] Understand architecture (see ARCHITECTURE_DIAGRAMS.md)
- [ ] Test all 4 commands
- [ ] Add custom skills if needed
- [ ] Register hooks for automation
- [ ] Connect to VS Code (future step)

## Next Steps

1. **Immediate:** Run test suite
2. **Short-term:** Add new skills
3. **Medium-term:** Integrate with VS Code
4. **Long-term:** Add ML-based analysis

## Support

**For questions about:**
- **Usage:** See README.md
- **Implementation:** See IMPLEMENTATION_GUIDE.md
- **Architecture:** See ARCHITECTURE_DIAGRAMS.md
- **Errors:** Check output/analysis-results/

## Code Examples

### Example 1: Custom Workflow

```python
import sys
sys.path.insert(0, "backend")

from .github.agents import run_agent, hooks
from .github.agents.hooks import on_analysis_complete

# Register hook
hooks.register("on_analysis_complete", on_analysis_complete.on_analysis_complete)

# Run analysis
result = run_agent("/analyze", "f:/Projects/MyRepo")

# Check status
if result["status"] == "success":
    print(f"✅ {result['summary']}")
    hooks.trigger("on_analysis_complete", "f:/Projects/MyRepo", result)
else:
    print(f"❌ Error: {result['message']}")
```

### Example 2: Impact Analysis

```python
# Analyze impact of changes
result = run_agent("/impact", "f:/Projects/MyRepo", "src/core/main.py")

print(f"Direct dependents: {result['details'].get('direct_dependents', [])}")
print(f"Risk areas: {result['evidence']}")

if len(result['details'].get('direct_dependents', [])) > 10:
    print("⚠️ High impact - many dependents")
```

### Example 3: Architecture Review

```python
# Get architecture info
result = run_agent("/architecture", "f:/Projects/MyRepo")

layers = result["details"].get("layers", {})
print("Architecture layers:")
for layer, components in layers.items():
    print(f"  {layer.upper()}: {len(components)} components")
```

### Example 4: Question Loop

```python
import sys
sys.path.insert(0, "backend")

from .github.agents import run_agent

repo_path = "f:/Projects/MyRepo"

# Ask multiple questions
questions = [
    "How many files are there?",
    "What languages are used?",
    "How many classes?",
]

for question in questions:
    result = run_agent("/ask", repo_path, question)
    print(f"Q: {question}")
    print(f"A: {result['summary']}")
    print()
```

## Performance Metrics

Typical execution times on modern hardware:

| Operation | Time |
|-----------|------|
| Analyze small repo (1-10 files) | 0.5s |
| Analyze medium repo (10-100 files) | 2-5s |
| Analyze large repo (100+ files) | 10-60s |
| Architecture analysis | 0.1-0.5s |
| Impact analysis | 0.1-1s |
| Q&A lookup | 0.1s |

## Memory Usage

- Typical: 50-100MB
- Large repos: 200-500MB
- Peak during graph building

## Disk Usage

Per analysis output: 1-50KB JSON file

## Logging

Enable Python logging to debug:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Now see detailed logs
result = run_agent("/analyze", repo_path)
```

---

**For complete documentation, see:**
- README.md - Quick start
- IMPLEMENTATION_GUIDE.md - Full reference
- ARCHITECTURE_DIAGRAMS.md - Visual guides
- COMPLETION_SUMMARY.md - What was created
