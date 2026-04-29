"""Filesystem mutation actions.

CopyFile      - copy a file from source repo into target repo
DeleteFile    - delete a file (no-op if missing)
EnsureDirectory - create a directory if absent
"""

from pathlib import Path
import shutil

from se_admin.actions import ActionResult
from se_admin.domain.operations import CopyFile, DeleteFile, EnsureDirectory


def run_copy_file(
    op: CopyFile,
    *,
    target_path: Path,
    source_path: Path,
) -> ActionResult:
    """Copy src (relative to source_path) to dest (relative to target_path).

    Idempotent: overwrites if already present (content may differ).
    Creates intermediate directories as needed.
    """
    src = source_path / op.src
    dest = target_path / op.dest

    if not src.exists():
        return ActionResult.error(f"Source not found: {src}")

    dest.parent.mkdir(parents=True, exist_ok=True)

    already_identical = dest.exists() and dest.read_bytes() == src.read_bytes()
    if already_identical:
        return ActionResult.noop(f"Already identical: {op.dest}")

    shutil.copy2(src, dest)
    return ActionResult.done(f"Copied {op.src} to {op.dest}")


def run_delete_file(op: DeleteFile, *, target_path: Path) -> ActionResult:
    """Delete a file.  No-op if already missing."""
    p = target_path / op.path
    if not p.exists():
        return ActionResult.noop(f"Already absent: {op.path}")
    p.unlink()
    return ActionResult.done(f"Deleted {op.path}")


def run_ensure_directory(op: EnsureDirectory, *, target_path: Path) -> ActionResult:
    """Create a directory (and parents) if not already present."""
    d = target_path / op.path
    if d.is_dir():
        return ActionResult.noop(f"Already exists: {op.path}")
    d.mkdir(parents=True, exist_ok=True)
    return ActionResult.done(f"Created directory {op.path}")
