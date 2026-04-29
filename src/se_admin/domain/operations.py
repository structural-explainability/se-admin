"""Operation type tree for se_admin.

Operation =
  AtomicOperation
  | OpSequence[Operation]
  | Conditional(condition, Operation)
"""

from __future__ import annotations

from dataclasses import dataclass, field

# ===========================================================================
# Detection  (no side effects)
# ===========================================================================


@dataclass
class CheckPath:
    """Assert a path exists or is missing in the target repo."""

    path: str
    present: bool = True  # True = must exist, False = must be absent


@dataclass
class CheckTomlKey:
    """Assert a TOML key exists or holds a specific value."""

    file: str
    key: str  # dotted key path e.g. "tool.uv.dev-dependencies"
    value: object | None = None  # None = check presence only


# ===========================================================================
# Mutation - Filesystem
# ===========================================================================


@dataclass
class CopyFile:
    """Copy a file from the source repo into the target repo."""

    src: str  # relative to source repo root
    dest: str  # relative to target repo root


@dataclass
class ReplaceFile:
    """Replace a file in the target repo from the canonical source."""

    src: str
    dest: str


@dataclass
class DeleteFile:
    """Delete a file.  No-op if already missing."""

    path: str


@dataclass
class EnsureDirectory:
    """Create a directory if it does not already exist."""

    path: str


# ===========================================================================
# Mutation - TOML
# ===========================================================================


@dataclass
class PatchToml:
    """Mutate a TOML file.

    operation values:
      set_key            - write key=value
      remove_key         - delete a key
      add_dependency     - add name to optional-dependency group
      remove_dependency  - remove name from optional-dependency group
      ensure_table       - create table header if absent
    """

    file: str
    operation: str
    key: str | None = None
    value: object | None = None
    group: str | None = None
    name: str | None = None


# ===========================================================================
# Mutation - Workflows  (files, but with distinct intent)
# ===========================================================================


@dataclass
class EnsureWorkflow:
    """Copy a workflow file into .github/workflows/ if not already present."""

    name: str  # filename e.g. "deploy-zensical.yml"
    src: str  # source path relative to source repo


@dataclass
class ReplaceWorkflow:
    """Overwrite a workflow file unconditionally from canonical source."""

    name: str
    src: str


@dataclass
class RemoveWorkflow:
    """Delete a workflow file.  No-op if missing."""

    name: str


# ===========================================================================
# Mutation - Text
# ===========================================================================


@dataclass
class PatchMarkdownSection:
    """Replace, insert, or remove a named heading block in a Markdown file.

    operation values:  replace | insert | remove
    """

    file: str
    section: str  # heading text to match
    operation: str
    content: str | None = None


# ===========================================================================
# Mutation - Process
# ===========================================================================


@dataclass
class RunCommand:
    """Run a shell command inside the target repo directory."""

    command: str
    args: list[str] = field(default_factory=list)


# ===========================================================================
# Composition
# ===========================================================================


@dataclass
class OpSequence:
    """Execute a list of operations in order."""

    steps: list[Operation]


@dataclass
class Conditional:
    """Execute *then* only when *condition* check passes; optionally *otherwise*."""

    condition: CheckPath | CheckTomlKey
    then: Operation
    otherwise: Operation | None = None


# ===========================================================================
# Union types
# ===========================================================================

AtomicOperation = (
    CheckPath
    | CheckTomlKey
    | CopyFile
    | ReplaceFile
    | DeleteFile
    | EnsureDirectory
    | PatchToml
    | EnsureWorkflow
    | ReplaceWorkflow
    | RemoveWorkflow
    | PatchMarkdownSection
    | RunCommand
)

Operation = AtomicOperation | OpSequence | Conditional
