"""Tests for loading repos.toml and profiles.toml into domain types."""

from pathlib import Path

import pytest

from se_admin.domain.profiles import ProfileRegistry
from se_admin.domain.repos import RepoRegistry

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

REPOS_TOML = """\
[family]
id = "test-family"
label = "Test Family"
workspace_root = ".."

[repo_sets.core]
label = "Core repositories"
repos = ["repo-a", "repo-b"]

[repos.repo-a]
repo_set = "core"
profiles = ["all_repos", "python_package", "links"]

[repos.repo-b]
repo_set = "core"
profiles = ["all_repos"]
status = "legacy"
"""

PROFILES_TOML = """\
[profiles.python_package]
label = "Python package repository"
description = "Repository containing a Python package."
required_paths = ["pyproject.toml", "src", "tests"]
required_workflows = [".github/workflows/ci.yml"]

[profiles.links]
label = "Link-checked repository"
description = "Repository checked with link-checking workflow."
required_workflows = [".github/workflows/links.yml"]

[profiles.zensical]
label = "Zensical documentation repository"
description = "Repository that builds documentation with Zensical."
required_paths = ["zensical.toml", "docs"]
required_workflows = [".github/workflows/deploy-zensical.yml"]

[profiles.zensical.pyproject]
required_optional_dependency_groups = ["docs"]

[profiles.zensical.pyproject.optional_dependencies.docs]
required = ["zensical"]
"""


@pytest.fixture
def repos_toml(tmp_path: Path) -> Path:
    p = tmp_path / "repos.toml"
    p.write_text(REPOS_TOML)
    return p


@pytest.fixture
def profiles_toml(tmp_path: Path) -> Path:
    p = tmp_path / "profiles.toml"
    p.write_text(PROFILES_TOML)
    return p


# ---------------------------------------------------------------------------
# RepoRegistry
# ---------------------------------------------------------------------------


def test_repo_registry_loads_family(repos_toml: Path) -> None:
    """Family metadata should load correctly."""
    registry = RepoRegistry.from_toml(repos_toml)
    assert registry.family.id == "test-family"
    assert registry.family.workspace_root == ".."


def test_repo_registry_loads_repo_sets(repos_toml: Path) -> None:
    """Repo sets should be indexed by name."""
    registry = RepoRegistry.from_toml(repos_toml)
    assert "core" in registry.repo_sets
    assert registry.repo_sets["core"].repos == ["repo-a", "repo-b"]


def test_repo_registry_loads_repos(repos_toml: Path) -> None:
    """Repos should be indexed by name with profiles assigned."""
    registry = RepoRegistry.from_toml(repos_toml)
    assert "repo-a" in registry.repos
    assert registry.repos["repo-a"].profiles == ["all_repos", "python_package", "links"]


def test_repo_registry_default_status_is_active(repos_toml: Path) -> None:
    """Repos without explicit status should default to active."""
    registry = RepoRegistry.from_toml(repos_toml)
    assert registry.repos["repo-a"].status == "active"


def test_repo_registry_explicit_status(repos_toml: Path) -> None:
    """Explicit status should be preserved."""
    registry = RepoRegistry.from_toml(repos_toml)
    assert registry.repos["repo-b"].status == "legacy"


def test_repo_registry_repos_in_set(repos_toml: Path) -> None:
    """repos_in_set should return RepoEntry objects for the set."""
    registry = RepoRegistry.from_toml(repos_toml)
    entries = registry.repos_in_set("core")
    names = [e.name for e in entries]
    assert "repo-a" in names
    assert "repo-b" in names


def test_repo_registry_active_repos(repos_toml: Path) -> None:
    """active_repos should exclude legacy entries."""
    registry = RepoRegistry.from_toml(repos_toml)
    active = registry.active_repos()
    names = [r.name for r in active]
    assert "repo-a" in names
    assert "repo-b" not in names


def test_repo_registry_unknown_set_returns_empty(repos_toml: Path) -> None:
    """repos_in_set for an unknown name should return empty list."""
    registry = RepoRegistry.from_toml(repos_toml)
    assert registry.repos_in_set("nonexistent") == []


# ---------------------------------------------------------------------------
# ProfileRegistry
# ---------------------------------------------------------------------------


def test_profile_registry_loads_profiles(profiles_toml: Path) -> None:
    """All profiles should be indexed by id."""
    registry = ProfileRegistry.from_toml(profiles_toml)
    assert "python_package" in registry.profiles
    assert "links" in registry.profiles
    assert "zensical" in registry.profiles


def test_profile_registry_required_paths(profiles_toml: Path) -> None:
    """required_paths should load as a list."""
    registry = ProfileRegistry.from_toml(profiles_toml)
    profile = registry.get("python_package")
    assert profile is not None
    assert "pyproject.toml" in profile.required_paths
    assert "src" in profile.required_paths


def test_profile_registry_required_workflows(profiles_toml: Path) -> None:
    """required_workflows should load as a list."""
    registry = ProfileRegistry.from_toml(profiles_toml)
    profile = registry.get("links")
    assert profile is not None
    assert ".github/workflows/links.yml" in profile.required_workflows


def test_profile_registry_pyproject_requirements(profiles_toml: Path) -> None:
    """Nested pyproject requirements should parse correctly."""
    registry = ProfileRegistry.from_toml(profiles_toml)
    profile = registry.get("zensical")
    assert profile is not None
    assert profile.pyproject is not None
    assert "docs" in profile.pyproject.required_optional_dependency_groups
    assert "zensical" in profile.pyproject.optional_dependencies["docs"].required


def test_profile_registry_get_unknown_returns_none(profiles_toml: Path) -> None:
    """get() for an unknown profile should return None."""
    registry = ProfileRegistry.from_toml(profiles_toml)
    assert registry.get("nonexistent") is None


def test_profile_registry_resolve_raises_on_unknown(profiles_toml: Path) -> None:
    """resolve() should raise KeyError for unknown profile names."""
    registry = ProfileRegistry.from_toml(profiles_toml)
    with pytest.raises(KeyError):
        registry.resolve(["python_package", "does_not_exist"])
