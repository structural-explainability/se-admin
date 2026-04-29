"""Profile registry domain types - loaded from data/profiles.toml."""

from dataclasses import dataclass, field
from pathlib import Path
import tomllib
from typing import Self


@dataclass
class PyprojectDependencyGroup:
    """Profile requirements for a pyproject.toml optional dependency group."""

    required: list[str] = field(default_factory=list)


@dataclass
class PyprojectRequirements:
    """Profile requirements for a pyproject.toml file."""

    required_optional_dependency_groups: list[str] = field(default_factory=list)
    optional_dependencies: dict[str, PyprojectDependencyGroup] = field(
        default_factory=dict
    )


@dataclass
class Profile:
    """A profile of requirements that repos can conform to."""

    id: str
    label: str
    description: str = ""
    extends: list[str] = field(default_factory=list)
    required_paths: list[str] = field(default_factory=list)
    optional_paths: list[str] = field(default_factory=list)
    required_workflows: list[str] = field(default_factory=list)
    pyproject: PyprojectRequirements | None = None


@dataclass
class ProfileRegistry:
    """Profile registry.

    Keyed by profile id.
    A profile is a named set of requirements that repos
    can declare themselves as conforming to.
    """

    profiles: dict[str, Profile]

    def get(self, name: str) -> Profile | None:
        """Get a profile by name, or None if not found."""
        return self.profiles.get(name)

    def resolve(self, names: list[str]) -> list[Profile]:
        """Return profiles for a list of names, raising on unknown."""
        result = []
        for name in names:
            p = self.profiles.get(name)
            if p is None:
                raise KeyError(f"Unknown profile: {name!r}")
            result.append(p)
        return result

    @classmethod
    def from_toml(cls, path: Path) -> Self:
        """Load a profile registry from a TOML file."""
        with path.open("rb") as f:
            data = tomllib.load(f)

        profiles: dict[str, Profile] = {}
        for pid, raw in data.get("profiles", {}).items():
            raw = dict(raw)
            pyproject_raw = raw.pop("pyproject", None)
            pyproject: PyprojectRequirements | None = None

            if pyproject_raw:
                opt_deps: dict[str, PyprojectDependencyGroup] = {}
                for group, gdata in pyproject_raw.get(
                    "optional_dependencies", {}
                ).items():
                    opt_deps[group] = PyprojectDependencyGroup(**gdata)
                pyproject = PyprojectRequirements(
                    required_optional_dependency_groups=pyproject_raw.get(
                        "required_optional_dependency_groups", []
                    ),
                    optional_dependencies=opt_deps,
                )

            profiles[pid] = Profile(id=pid, pyproject=pyproject, **raw)

        return cls(profiles=profiles)
