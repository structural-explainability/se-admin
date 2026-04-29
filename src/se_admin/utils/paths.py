"""Path resolution utilities for se_admin."""

from pathlib import Path


def find_data_dir(start: Path | None = None) -> Path:
    """Walk up from start (default: cwd) to find a data/ directory.

    Returns the first data/ directory found, or data/ relative to cwd
    as a fallback (caller can check existence).
    """
    root = (start or Path.cwd()).resolve()
    for candidate in [root, *root.parents]:
        data = candidate / "data"
        if data.is_dir():
            return data
    return Path("data")


def repo_path(workspace_root: Path, repo_name: str) -> Path:
    """Resolve the absolute path to a repo inside the workspace."""
    return (workspace_root / repo_name).resolve()


def relative_to_workspace(path: Path, workspace_root: Path) -> str:
    """Return path as a string relative to workspace_root, or absolute fallback."""
    try:
        return str(path.relative_to(workspace_root))
    except ValueError:
        return str(path)


def ensure_dir(path: Path) -> Path:
    """Create path as a directory (including parents) and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def is_repo_root(path: Path) -> bool:
    """True if path looks like a git repo root."""
    return (path / ".git").exists()
