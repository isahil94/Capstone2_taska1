# How to Run the Agent System

This document shows how to run the `.github` agent system from the repository root, with examples and expected output locations.

## Prerequisites

- Python 3.8+ installed
- Repository root: `F:\Projects\Capstone 2`
- The backend and `.github` package are present in the repo
- The output folder is `output/analysis-results`

## Run from the repository root

Open a terminal in `F:\Projects\Capstone 2` and run Python from the repo root.

### Example 1: Use `run_agent()` from Python

```python
import sys
from pathlib import Path

repo_root = Path("F:/Projects/Capstone 2")
backend_path = repo_root / "backend"

# Make backend importable
sys.path.insert(0, str(backend_path))

from .github.agents import run_agent

result = run_agent("/analyze", str(repo_root))
print("Summary:", result["summary"])
print("Status:", result["status"])
print("Output file folder: output/analysis-results")
```

### Example 2: Run a command directly in PowerShell

```powershell
cd "F:\Projects\Capstone 2"
python -c "import sys; sys.path.insert(0, 'backend'); from .github.agents import run_agent; print(run_agent('/analyze', '.')['summary'])"
```

### Example 3: Run `/ask` for a repository question

```python
import sys
from pathlib import Path

repo_root = Path("F:/Projects/Capstone 2")
backend_path = repo_root / "backend"
sys.path.insert(0, str(backend_path))

from .github.agents import run_agent

result = run_agent("/ask", str(repo_root), "How many files are in the repository?")
print(result["summary"])
print(result["evidence"])
```

## Output location

All generated reports are written as JSON files under:

```
output/analysis-results/
```

If the folder does not exist, it is created automatically.

### Example saved file path

```
output/analysis-results/20240628_143501_analyze.json
```

## Sample output JSON

A successful `/analyze` run produces a file like this:

```json
{
  "command": "analyze",
  "timestamp": "2026-06-28T14:35:01.234567",
  "status": "success",
  "summary": "Repository analysis completed. 42 files were processed.",
  "details": {
    "total_files": 42,
    "total_classes": 12,
    "total_functions": 56,
    "layers": {
      "backend": 28,
      "frontend": 12,
      "infrastructure": 2
    }
  },
  "evidence": [
    "Found 42 source files",
    "Detected 12 class definitions",
    "Identified 3 architectural layers"
  ]
}
```

## What to fix if nothing is written

- Confirm you are running from the repository root.
- Confirm `backend` is on `sys.path` before importing `run_agent`.
- Confirm the command is one of `/analyze`, `/architecture`, `/impact`, or `/ask`.
- Inspect the folder `output/analysis-results/` for generated JSON.

## Notes

- The agent system is implemented in `.github/agents/`.
- Skills are in `.github/skills/`.
- Core helpers are in `.github/core/`.
- Hooks are in `.github/hooks/`.
- Output is stored in `output/analysis-results/`.
