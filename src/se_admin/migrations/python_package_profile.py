"""Migration: establish the python_package profile in a repo.

Required by profile:
  paths:     pyproject.toml, src/, tests/
  workflows: ci-python-zensical.yml
"""

from pathlib import Path

from se_admin.actions import ActionResult
from se_admin.actions.copy_file import run_copy_file, run_ensure_directory
from se_admin.actions.replace_file import run_ensure_workflow
from se_admin.domain.operations import CopyFile, EnsureDirectory, EnsureWorkflow
from se_admin.observe.filesystem import path_exists

_CI_WORKFLOW = "ci-python-zensical.yml"
_PYPROJECT = "pyproject.toml"


def run_python_package_profile(
    *,
    target_path: Path,
    source_path: Path,
) -> list[ActionResult]:
    """Bring target_path up to python_package profile requirements.

    Idempotent: skips anything already in place.
    """
    results: list[ActionResult] = []

    # pyproject.toml - copy from source only if absent
    if not path_exists(target_path, _PYPROJECT):
        results.append(
            run_copy_file(
                CopyFile(src=_PYPROJECT, dest=_PYPROJECT),
                target_path=target_path,
                source_path=source_path,
            )
        )

    # src/ and tests/ directories
    for directory in ("src", "tests"):
        results.append(
            run_ensure_directory(
                EnsureDirectory(path=directory),
                target_path=target_path,
            )
        )

    # CI workflow
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
