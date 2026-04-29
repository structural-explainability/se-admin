"""Filesystem observation - actual path state in a repo.

No decisions, no side effects.  Returns plain facts.
"""

from pathlib import Path


def path_exists(repo_path: Path, relative: str) -> bool:
    """True if the path exists (file or directory)."""
    return (repo_path / relative).exists()


def path_missing(repo_path: Path, relative: str) -> bool:
    """Return True if the path is missing (does not exist as file or directory)."""
    return not path_exists(repo_path, relative)


def is_file(repo_path: Path, relative: str) -> bool:
    """Return True if the path exists and is a file."""
    return (repo_path / relative).is_file()


def is_directory(repo_path: Path, relative: str) -> bool:
    """Return True if the path exists and is a directory."""
    return (repo_path / relative).is_dir()


def read_text(repo_path: Path, relative: str) -> str:
    """Read a text file.  Raises FileNotFoundError if missing."""
    return (repo_path / relative).read_text(encoding="utf-8")


def list_files(repo_path: Path, pattern: str = "**/*") -> list[Path]:
    """Return all files matching a glob pattern, relative to repo_path."""
    return [p.relative_to(repo_path) for p in repo_path.glob(pattern) if p.is_file()]


def check_required_paths(repo_path: Path, paths: list[str]) -> dict[str, bool]:
    """Return {relative_path: exists} for each required path."""
    return {p: path_exists(repo_path, p) for p in paths}
