"""Tests for profile domain logic and resolution."""

from pathlib import Path

import pytest

from se_admin.domain.profiles import (
    Profile,
    ProfileRegistry,
    PyprojectDependencyGroup,
    PyprojectRequirements,
)

# ---------------------------------------------------------------------------
# Profile construction
# ---------------------------------------------------------------------------


def test_profile_defaults_to_empty_lists() -> None:
    """Profile should default required/optional lists to empty."""
    p = Profile(id="bare", label="Bare")
    assert p.required_paths == []
    assert p.optional_paths == []
    assert p.required_workflows == []
    assert p.pyproject is None


def test_profile_stores_required_paths() -> None:
    """required_paths should be stored as provided."""
    p = Profile(id="pkg", label="Pkg", required_paths=["pyproject.toml", "src"])
    assert "pyproject.toml" in p.required_paths
    assert "src" in p.required_paths


def test_profile_stores_required_workflows() -> None:
    """required_workflows should be stored as provided."""
    p = Profile(
        id="ci",
        label="CI",
        required_workflows=[".github/workflows/ci.yml"],
    )
    assert ".github/workflows/ci.yml" in p.required_workflows


# ---------------------------------------------------------------------------
# PyprojectRequirements
# ---------------------------------------------------------------------------


def test_pyproject_requirements_defaults() -> None:
    """PyprojectRequirements should default to empty structures."""
    req = PyprojectRequirements()
    assert req.required_optional_dependency_groups == []
    assert req.optional_dependencies == {}


def test_pyproject_dependency_group_stores_required() -> None:
    """PyprojectDependencyGroup should store required list."""
    group = PyprojectDependencyGroup(required=["zensical", "mkdocs"])
    assert "zensical" in group.required


# ---------------------------------------------------------------------------
# ProfileRegistry.resolve
# ---------------------------------------------------------------------------


def _make_registry() -> ProfileRegistry:
    return ProfileRegistry(
        profiles={
            "lean": Profile(id="lean", label="Lean"),
            "links": Profile(id="links", label="Links"),
            "python_package": Profile(
                id="python_package",
                label="Python Package",
                required_paths=["pyproject.toml", "src"],
            ),
            "zensical": Profile(
                id="zensical",
                label="Zensical",
                required_paths=["zensical.toml"],
                pyproject=PyprojectRequirements(
                    required_optional_dependency_groups=["docs"],
                    optional_dependencies={
                        "docs": PyprojectDependencyGroup(required=["zensical"])
                    },
                ),
            ),
        }
    )


def test_resolve_single_profile() -> None:
    """resolve should return a list with the matching profile."""
    registry = _make_registry()
    result = registry.resolve(["lean"])
    assert len(result) == 1
    assert result[0].id == "lean"


def test_resolve_multiple_profiles() -> None:
    """resolve should return profiles in the order given."""
    registry = _make_registry()
    result = registry.resolve(["python_package", "zensical", "links"])
    ids = [p.id for p in result]
    assert ids == ["python_package", "zensical", "links"]


def test_resolve_unknown_raises_key_error() -> None:
    """resolve should raise KeyError for any unknown profile name."""
    registry = _make_registry()
    with pytest.raises(KeyError, match="unknown_profile"):
        registry.resolve(["lean", "unknown_profile"])


def test_resolve_empty_list() -> None:
    """resolve of empty list should return empty list."""
    registry = _make_registry()
    assert registry.resolve([]) == []


def test_get_returns_none_for_missing() -> None:
    """get should return None for an unknown profile id."""
    registry = _make_registry()
    assert registry.get("not_there") is None


def test_get_returns_profile_for_known() -> None:
    """get should return the correct Profile for a known id."""
    registry = _make_registry()
    p = registry.get("zensical")
    assert p is not None
    assert p.id == "zensical"
    assert p.pyproject is not None


# ---------------------------------------------------------------------------
# ProfileRegistry.from_toml round-trip
# ---------------------------------------------------------------------------


PROFILES_TOML = """\
[profiles.alpha]
label = "Alpha"
description = "First profile."
required_paths = ["README.md"]
required_workflows = [".github/workflows/ci.yml"]

[profiles.beta]
label = "Beta"
description = "Second profile."
required_paths = ["pyproject.toml"]

[profiles.beta.pyproject]
required_optional_dependency_groups = ["docs"]

[profiles.beta.pyproject.optional_dependencies.docs]
required = ["zensical"]
"""


def test_from_toml_round_trip(tmp_path: Path) -> None:
    """from_toml should reconstruct profiles with all nested fields."""
    p = tmp_path / "profiles.toml"
    p.write_text(PROFILES_TOML)
    registry = ProfileRegistry.from_toml(p)

    alpha = registry.get("alpha")
    assert alpha is not None
    assert alpha.label == "Alpha"
    assert "README.md" in alpha.required_paths
    assert alpha.pyproject is None

    beta = registry.get("beta")
    assert beta is not None
    assert beta.pyproject is not None
    assert "docs" in beta.pyproject.required_optional_dependency_groups
    assert "zensical" in beta.pyproject.optional_dependencies["docs"].required
