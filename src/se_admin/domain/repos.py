"""Repo registry domain types - loaded from data/repos.toml."""

from dataclasses import dataclass
from pathlib import Path
import tomllib
from typing import Self


@dataclass
class RepoFamily:
    """Repository family, e.g. "theory", "streaming", etc."""

    id: str
    label: str
    workspace_root: str


@dataclass
class RepoSet:
    """A set of repositories, e.g. "core", "extensions", etc."""

    label: str
    repos: list[str]


@dataclass
class RepoEntry:
    """A single repository entry."""

    name: str
    repo_set: str
    profiles: list[str]
    status: str = "active"

    def repo_path(self, workspace_root: Path) -> Path:
        """Get the path to this repository within the workspace."""
        return workspace_root / self.name


@dataclass
class RepoRegistry:
    """A registry of repositories."""

    family: RepoFamily
    repo_sets: dict[str, RepoSet]
    repos: dict[str, RepoEntry]

    def workspace_path(self) -> Path:
        """Get the path to the workspace root."""
        return Path(self.family.workspace_root)

    def repos_in_set(self, set_name: str) -> list[RepoEntry]:
        """Get all repositories in the specified set."""
        rs = self.repo_sets.get(set_name)
        if rs is None:
            return []
        return [self.repos[r] for r in rs.repos if r in self.repos]

    def active_repos(self) -> list[RepoEntry]:
        """Get all active repositories."""
        return [r for r in self.repos.values() if r.status == "active"]

    @classmethod
    def from_toml(cls, path: Path) -> Self:
        """Load a repository registry from a TOML file."""
        with path.open("rb") as f:
            data = tomllib.load(f)

        family = RepoFamily(**data["family"])

        repo_sets = {k: RepoSet(**v) for k, v in data.get("repo_sets", {}).items()}

        repos: dict[str, RepoEntry] = {}
        for name, entry in data.get("repos", {}).items():
            repos[name] = RepoEntry(name=name, **entry)

        return cls(family=family, repo_sets=repo_sets, repos=repos)
