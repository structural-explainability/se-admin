"""Migration: rename workflow files to canonical names.

Handles cases where workflows were created with legacy names
and need to be moved to the canonical names declared in profiles.

Each rename is:
  - No-op if destination already exists with correct content
  - Copy old to new, then delete old
  - No-op if old name is absent (already migrated or never existed)
"""

from pathlib import Path

from se_admin.actions import ActionResult

_WORKFLOWS_DIR = ".github/workflows"

# Legacy name to canonical name
DEFAULT_RENAMES: dict[str, str] = {
    "ci-python.yml": "ci-python-zensical.yml",
    "ci-python-tooling.yml": "ci-python-zensical-tooling.yml",
    "deploy-docs.yml": "deploy-zensical.yml",
    "link-check.yml": "links.yml",
}


def run_workflow_names(
    *,
    target_path: Path,
    renames: dict[str, str] | None = None,
) -> list[ActionResult]:
    """Rename workflow files from legacy names to canonical names.

    Args:
        *: Keyword-only for clarity at call site, since target_path and renames are related.
        target_path: The repo root to operate on.
        renames: mapping of {old_name: new_name}.
                 Defaults to DEFAULT_RENAMES if not provided.

    Idempotent: skips if old name absent or new name already present.
    """
    rename_map = renames if renames is not None else DEFAULT_RENAMES
    results: list[ActionResult] = []

    for old_name, new_name in rename_map.items():
        result = _rename_workflow(
            target_path=target_path,
            old_name=old_name,
            new_name=new_name,
        )
        results.append(result)

    return results


def _rename_workflow(
    *,
    target_path: Path,
    old_name: str,
    new_name: str,
) -> ActionResult:
    workflows = target_path / _WORKFLOWS_DIR
    old_path = workflows / old_name
    new_path = workflows / new_name

    if not old_path.exists():
        return ActionResult.noop(f"Workflow absent, nothing to rename: {old_name}")

    if new_path.exists():
        if new_path.read_bytes() == old_path.read_bytes():
            old_path.unlink()
            return ActionResult.done(
                f"Removed redundant {old_name} (canonical {new_name} already present)"
            )
        return ActionResult.error(
            f"Cannot rename {old_name} to {new_name}: destination exists with different content"
        )

    new_path.parent.mkdir(parents=True, exist_ok=True)
    new_path.write_bytes(old_path.read_bytes())
    old_path.unlink()
    return ActionResult.done(f"Renamed workflow {old_name} to {new_name}")
