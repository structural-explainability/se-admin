"""Migration: establish the python_tooling profile in a repo.

Required by profile:
  paths:     pyproject.toml
  workflows: ci-python-zensical-tooling.yml

python_tooling is for repos that use Python for tooling, automation,
or documentation without a package contract (no src/ layout required).
"""

from pathlib import Path

from se_admin.actions import ActionResult
from se_admin.actions.copy_file import run_copy_file
from se_admin.actions.replace_file import run_ensure_workflow
from se_admin.domain.operations import CopyFile, EnsureWorkflow
from se_admin.observe.filesystem import path_exists

_CI_WORKFLOW = "ci-python-zensical-tooling.yml"
_PYPROJECT = "pyproject.toml"


def run_python_tooling_profile(
    *,
    target_path: Path,
    source_path: Path,
) -> list[ActionResult]:
    """Bring target_path up to python_tooling profile requirements.

    Idempotent: skips anything already in place.
    """
    results: list[ActionResult] = []

    if not path_exists(target_path, _PYPROJECT):
        results.append(
            run_copy_file(
                CopyFile(src=_PYPROJECT, dest=_PYPROJECT),
                target_path=target_path,
                source_path=source_path,
            )
        )

    results.append(
        run_ensure_workflow(
            EnsureWorkflow(
                name=_CI_WORKFLOW,
                src=f".github/workflows/{_CI_WORKFLOW}",
            ),
            target_path=target_path,
            source_path=source_path,
        )
    )

    return results
