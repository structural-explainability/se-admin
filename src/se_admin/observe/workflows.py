"""Workflow observation - actual workflow files present in a repo.

No decisions, no side effects.  Returns plain facts.
"""

from pathlib import Path

_WORKFLOWS_DIR = ".github/workflows"


def workflows_dir(repo_path: Path) -> Path:
    """Return the path to the workflows directory inside the repo."""
    return repo_path / _WORKFLOWS_DIR


def list_workflow_names(repo_path: Path) -> list[str]:
    """Return filenames of all workflow files (*.yml, *.yaml)."""
    d = workflows_dir(repo_path)
    if not d.is_dir():
        return []
    return sorted(
        p.name for p in d.iterdir() if p.is_file() and p.suffix in {".yml", ".yaml"}
    )


def workflow_present(repo_path: Path, name: str) -> bool:
    """True if a workflow file with this name exists."""
    return (workflows_dir(repo_path) / name).exists()


def workflow_missing(repo_path: Path, name: str) -> bool:
    """True if a workflow file with this name is missing."""
    return not workflow_present(repo_path, name)


def read_workflow_text(repo_path: Path, name: str) -> str:
    """Return raw YAML text of a workflow file."""
    return (workflows_dir(repo_path) / name).read_text(encoding="utf-8")


def check_required_workflows(repo_path: Path, names: list[str]) -> dict[str, bool]:
    """Return {workflow_name: present} for each required workflow."""
    return {name: workflow_present(repo_path, name) for name in names}
