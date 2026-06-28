"""Core repository wrapper - loads and validates repositories."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def load_repository(repo_path: str) -> dict[str, Any]:
    """
    Load and validate a repository.

    Args:
        repo_path: Path to the repository

    Returns:
        Dictionary containing:
        - local_path: str
        - is_valid: bool
        - message: str
        - metadata: dict with repo info
    """
    try:
        repository_path = Path(repo_path).resolve()
        if not repository_path.exists():
            return {
                "local_path": str(repository_path),
                "is_valid": False,
                "message": "Repository path does not exist",
            }

        if not repository_path.is_dir():
            return {
                "local_path": str(repository_path),
                "is_valid": False,
                "message": "Repository path is not a directory",
            }

        return {
            "local_path": str(repository_path),
            "is_valid": True,
            "message": "Repository is valid",
            "metadata": {
                "path": str(repository_path),
                "name": repository_path.name,
            },
        }
    except Exception as e:
        return {
            "local_path": repo_path,
            "is_valid": False,
            "message": f"Error validating repository: {str(e)}",
        }


def validate_repository(repo_path: str) -> bool:
    """
    Quick validation check for a repository path.

    Args:
        repo_path: Path to the repository

    Returns:
        True if valid git repository, False otherwise
    """
    try:
        repository_path = Path(repo_path).resolve()
        return repository_path.exists() and repository_path.is_dir()
    except Exception:
        return False
