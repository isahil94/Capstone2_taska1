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
            # Language detection based on extension (deterministic)
            ext = file_path.suffix.lower()
            lang_map = {
                ".py": "python",
                ".js": "javascript",
                ".jsx": "javascript",
                ".ts": "javascript",
                ".tsx": "javascript",
                ".go": "go",
                ".java": "java",
                ".json": "config",
                ".yml": "config",
                ".yaml": "config",
                ".md": "document",
            }
            language = lang_map.get(ext, "generic")

            imports: list[str] = []
            classes: list[str] = []
            functions: list[str] = []

            # Use AST parsing for Python files to get accurate symbols and imports
            if language == "python":
                try:
                    import ast

                    tree = ast.parse(content)
                    for node in ast.walk(tree):
                        if isinstance(node, ast.Import):
                            for n in node.names:
                                # e.g., import a.b as c -> store 'a.b'
                                if n.name:
                                    imports.append(n.name)
                        elif isinstance(node, ast.ImportFrom):
                            # node.module may be None for relative imports
                            mod = node.module or ""
                            # level indicates relative import (number of leading dots)
                            level = getattr(node, "level", 0)
                            for n in node.names:
                                # prefer full dotted name like a.b.c when possible
                                if mod:
                                    imports.append(f"{'.'*level}{mod}.{n.name}" if level else f"{mod}.{n.name}")
                                    # also include base module
                                    imports.append(f"{'.'*level}{mod}" if level else f"{mod}")
                                else:
                                    # relative import like from . import x
                                    imports.append(f"{'.'*level}{n.name}")
                        elif isinstance(node, ast.FunctionDef) or isinstance(node, ast.AsyncFunctionDef):
                            functions.append(node.name)
                        elif isinstance(node, ast.ClassDef):
                            classes.append(node.name)
                except Exception:
                    # fall back to lightweight regex if AST fails
                    import re

                    for m in re.finditer(r"class\s+([A-Za-z_][A-Za-z0-9_]*)", content):
                        classes.append(m.group(1))
                    for m in re.finditer(r"(?:def|function|func)\s+([A-Za-z_][A-Za-z0-9_]*)", content):
                        functions.append(m.group(1))
                    import_patterns = [
                        re.compile(r"^\s*from\s+([A-Za-z0-9_.\-/]+)\s+import"),
                        re.compile(r"^\s*import\s+([A-Za-z0-9_.\-/]+)"),
                    ]
                    for line in content.splitlines():
                        for pat in import_patterns:
                            m = pat.search(line)
                            if m:
                                imports.append(m.group(1))
                                break
            else:
                # Skip symbol extraction for documentation and text files
                if ext in {".md", ".txt"}:
                    imports = []
                    classes = []
                    functions = []
                else:
                    # fallback regex-based extraction for other languages
                    import re

                    import_patterns = [
                        re.compile(r"^\s*from\s+([A-Za-z0-9_./\-]+)\s+import"),
                        re.compile(r"^\s*import\s+([A-Za-z0-9_./\-]+)"),
                        re.compile(r"import\s+.*from\s+[\'\"]([^\"\']+)[\'\"]"),
                        re.compile(r"require\(\s*[\'\"]([^\"\']+)[\'\"]\s*\)"),
                        re.compile(r"^\s*import\s+[\'\"]([^\"\']+)[\'\"]"),
                    ]
                    for line in content.splitlines():
                        for pat in import_patterns:
                            m = pat.search(line)
                            if m:
                                imports.append(m.group(1) if m.groups() else line.strip())
                                break
                    for m in re.finditer(r"class\s+([A-Za-z_][A-Za-z0-9_]*)", content):
                        classes.append(m.group(1))
                    for m in re.finditer(r"(?:def|function|func)\s+([A-Za-z_][A-Za-z0-9_]*)", content):
                        functions.append(m.group(1))

            files.append(
                {
                    "file_path": Path(file_path.relative_to(repository_path)).as_posix(),
                    "language": language,
                    "classes": len(classes),
                    "functions": len(functions),
                    "imports": len(imports),
                    "methods": 0,
                    "details": {
                        "classes": classes,
                        "functions": functions,
                        "imports": imports,
                        "methods": [],
                        "raw_content": content,
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
