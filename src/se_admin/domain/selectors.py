"""Selector types - how a task chooses which repos to target."""

from dataclasses import dataclass


@dataclass
class RepoSetSelector:
    """All repos in one or more named sets."""

    repo_sets: list[str]


@dataclass
class RepoNameSelector:
    """Explicit list of repo names."""

    repos: list[str]


@dataclass
class PatternSelector:
    """Repos whose name matches a glob/regex pattern."""

    pattern: str


Selector = RepoSetSelector | RepoNameSelector | PatternSelector


def selector_from_dict(data: dict) -> Selector:
    """Parse a selector from a TOML [selector] table."""
    if "repo_sets" in data:
        return RepoSetSelector(repo_sets=data["repo_sets"])
    if "repos" in data:
        return RepoNameSelector(repos=data["repos"])
    if "pattern" in data:
        return PatternSelector(pattern=data["pattern"])
    raise ValueError(f"Cannot parse selector from: {data!r}")
