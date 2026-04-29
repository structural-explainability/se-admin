"""File replacement and workflow mutation actions.

ReplaceFile     - overwrite a file unconditionally from canonical source
EnsureWorkflow  - copy workflow into .github/workflows/ if not present
ReplaceWorkflow - overwrite a workflow file unconditionally
RemoveWorkflow  - delete a workflow file (no-op if missing)
"""

from pathlib import Path
import shutil

from se_admin.actions import ActionResult
from se_admin.domain.operations import (
    EnsureWorkflow,
    RemoveWorkflow,
    ReplaceFile,
    ReplaceWorkflow,
)

_WORKFLOWS = ".github/workflows"


def run_replace_file(
    op: ReplaceFile,
    *,
    target_path: Path,
    source_path: Path,
) -> ActionResult:
    """Overwrite dest in target_path from src in source_path.

    Always writes (unconditional replacement).
    Creates intermediate directories as needed.
    """
    src = source_path / op.src
    dest = target_path / op.dest

    if not src.exists():
        return ActionResult.error(f"Source not found: {src}")

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return ActionResult.done(f"Replaced {op.dest}")


def run_ensure_workflow(
    op: EnsureWorkflow,
    *,
    target_path: Path,
    source_path: Path,
) -> ActionResult:
    """Copy workflow into .github/workflows/ only if not already present."""
    dest = target_path / _WORKFLOWS / op.name
    if dest.exists():
        return ActionResult.noop(f"Workflow already present: {op.name}")

    src = source_path / op.src
    if not src.exists():
        return ActionResult.error(f"Source workflow not found: {src}")

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return ActionResult.done(f"Added workflow {op.name}")


def run_replace_workflow(
    op: ReplaceWorkflow,
    *,
    target_path: Path,
    source_path: Path,
) -> ActionResult:
    """Overwrite a workflow file unconditionally."""
    src = source_path / op.src
    dest = target_path / _WORKFLOWS / op.name

    if not src.exists():
        return ActionResult.error(f"Source workflow not found: {src}")

    already_identical = dest.exists() and dest.read_bytes() == src.read_bytes()
    if already_identical:
        return ActionResult.noop(f"Workflow already up to date: {op.name}")

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    return ActionResult.done(f"Replaced workflow {op.name}")


def run_remove_workflow(op: RemoveWorkflow, *, target_path: Path) -> ActionResult:
    """Delete a workflow file.  No-op if already missing."""
    p = target_path / _WORKFLOWS / op.name
    if not p.exists():
        return ActionResult.noop(f"Workflow already absent: {op.name}")
    p.unlink()
    return ActionResult.done(f"Removed workflow {op.name}")
