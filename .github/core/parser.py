"""Core parser wrapper - parses repositories and extracts symbols."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

IGNORED_DIRS = {
    ".git",
    ".venv",
    ".pytest_cache",
    "__pycache__",
    "node_modules",
    "output",
    "local_models",
    "dist",
    "build",
    ".mypy_cache",
    ".idea",
    ".vscode",
}
TEXT_SUFFIXES = {".py", ".js", ".ts", ".tsx", ".jsx", ".java", ".go", ".rs", ".c", ".cpp", ".cs", ".php", ".rb", ".swift", ".md", ".json", ".yml", ".yaml", ".toml", ".ini", ".cfg", ".txt"}
MAX_FILE_SIZE = 1024 * 1024


def _iter_source_files(repository_path: Path) -> list[Path]:
    """Yield relevant source files while skipping large/generated directories."""
    source_files: list[Path] = []
    for root, dirs, files in os.walk(repository_path):
        dirs[:] = [d for d in dirs if d not in IGNORED_DIRS]
        for file_name in files:
            file_path = Path(root) / file_name
            if file_path.name.startswith("."):
                continue
            if file_path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            try:
                if file_path.stat().st_size > MAX_FILE_SIZE:
                    continue
            except OSError:
                continue
            source_files.append(file_path)
    return sorted(source_files)


def parse_repository(repo_path: str) -> dict[str, Any]:
    """
    Parse a repository and extract symbols.

    Args:
        repo_path: Path to the repository

    Returns:
        Dictionary containing:
        - local_path: str
        - files: list[dict] with parsed file information
        - summary: dict with counts
    """
    try:
        repository_path = Path(repo_path).resolve()
        if not repository_path.exists() or not repository_path.is_dir():
            return {
                "error": "Repository path is invalid",
                "local_path": str(repository_path),
                "files": [],
                "summary": {},
            }

        files = []
        for file_path in _iter_source_files(repository_path):
            try:
                content = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                content = file_path.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue

            classes = [line.strip() for line in content.splitlines() if line.lstrip().startswith("class ")]
            functions = [line.strip() for line in content.splitlines() if line.lstrip().startswith("def ")]
            imports = [line.strip() for line in content.splitlines() if line.lstrip().startswith(("import ", "from "))]

            files.append(
                {
                    "file_path": str(file_path.relative_to(repository_path)),
                    "language": file_path.suffix.lower().lstrip("."),
                    "classes": len(classes),
                    "functions": len(functions),
                    "imports": len(imports),
                    "methods": 0,
                    "details": {
                        "classes": classes,
                        "functions": functions,
                        "imports": imports,
                        "methods": [],
                    },
                }
            )

        return {
            "local_path": str(repository_path),
            "files": files,
            "summary": {
                "total_files": len(files),
                "total_classes": sum(f["classes"] for f in files),
                "total_functions": sum(f["functions"] for f in files),
                "total_imports": sum(f["imports"] for f in files),
            },
        }
    except Exception as e:
        return {
            "error": str(e),
            "local_path": str(Path(repo_path).resolve()),
            "files": [],
            "summary": {},
        }


def get_parsed_results(repo_path: str) -> list[dict[str, Any]]:
    """
    Retrieve previously parsed results for a repository.

    Args:
        repo_path: Path to the repository

    Returns:
        List of parsed file records
    """
    try:
        repository_path = Path(repo_path).resolve()
        if not repository_path.exists() or not repository_path.is_dir():
            return []

        return []
    except Exception:
        return []
