"""TOML file observation - read keys and values from any TOML file.

No decisions, no side effects.  Returns plain facts.
"""

from pathlib import Path
import tomllib
from typing import Any


def read_toml(repo_path: Path, relative: str) -> dict[Any, Any]:
    """Parse a TOML file and return the raw dict.  Raises if missing."""
    p = repo_path / relative
    with p.open("rb") as f:
        return tomllib.load(f)


def read_toml_safe(repo_path: Path, relative: str) -> dict[Any, Any]:
    """Parse a TOML file; return empty dict if file is missing."""
    p = repo_path / relative
    if not p.exists():
        return {}
    with p.open("rb") as f:
        return tomllib.load(f)


def _resolve_key(data: dict[Any, Any], dotted_key: str) -> object | None:
    """Walk a dotted key path through nested dicts.  Returns None if absent."""
    parts = dotted_key.split(".")
    current: object = data
    for part in parts:
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def toml_key_exists(repo_path: Path, relative: str, dotted_key: str) -> bool:
    """True if the dotted key path exists in the TOML file."""
    data = read_toml_safe(repo_path, relative)
    return _resolve_key(data, dotted_key) is not None


def toml_get_value(repo_path: Path, relative: str, dotted_key: str) -> object | None:
    """Return the value at dotted_key, or None if absent."""
    data = read_toml_safe(repo_path, relative)
    return _resolve_key(data, dotted_key)


def toml_value_equals(
    repo_path: Path, relative: str, dotted_key: str, expected: object
) -> bool:
    """True if the value at dotted_key equals expected."""
    return toml_get_value(repo_path, relative, dotted_key) == expected
