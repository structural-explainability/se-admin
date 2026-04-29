"""pyproject.toml observation - dependencies, version, tool config.

No decisions, no side effects.  Returns plain facts.
"""

from pathlib import Path

from se_admin.observe.toml_files import read_toml_safe


def read_pyproject(repo_path: Path) -> dict:
    """Return the full parsed pyproject.toml, or {} if absent."""
    return read_toml_safe(repo_path, "pyproject.toml")


def get_requires_python(repo_path: Path) -> str | None:
    """Return the requires-python specifier, e.g. '>=3.12'."""
    data = read_pyproject(repo_path)
    return data.get("project", {}).get("requires-python")


def get_python_version_file(repo_path: Path) -> str | None:
    """Return the pinned version from .python-version, stripped."""
    p = repo_path / ".python-version"
    if not p.exists():
        return None
    return p.read_text(encoding="utf-8").strip()


def get_optional_dependencies(repo_path: Path, group: str) -> list[str]:
    """Return the list of packages in an optional-dependency group."""
    data = read_pyproject(repo_path)
    return data.get("project", {}).get("optional-dependencies", {}).get(group, [])


def dependency_present(repo_path: Path, group: str, name: str) -> bool:
    """True if *name* appears (case-insensitive prefix match) in the group."""
    deps = get_optional_dependencies(repo_path, group)
    name_lower = name.lower()
    return any(d.lower().startswith(name_lower) for d in deps)


def get_uv_dev_dependencies(repo_path: Path) -> list[str]:
    """Return [tool.uv.dev-dependencies] entries."""
    data = read_pyproject(repo_path)
    return data.get("tool", {}).get("uv", {}).get("dev-dependencies", [])


def get_project_name(repo_path: Path) -> str | None:
    """Return the project name from pyproject.toml, or None if missing."""
    data = read_pyproject(repo_path)
    return data.get("project", {}).get("name")
