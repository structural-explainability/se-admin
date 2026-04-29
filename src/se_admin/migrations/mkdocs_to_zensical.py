"""Migration: MkDocs to Zensical.

Composed sequence:
  1. If mkdocs.yml present then remove config, dependency, workflow
  2. Add zensical.toml from source repo
  3. Add zensical to [docs] optional-dependency group
  4. Ensure deploy-zensical workflow
  5. Ensure docs/ directory
"""

from pathlib import Path

from se_admin.actions import ActionResult
from se_admin.actions.copy_file import run_copy_file, run_ensure_directory
from se_admin.actions.patch_toml import run_patch_toml
from se_admin.actions.replace_file import run_ensure_workflow, run_remove_workflow
from se_admin.domain.operations import (
    CopyFile,
    EnsureDirectory,
    EnsureWorkflow,
    PatchToml,
    RemoveWorkflow,
)
from se_admin.observe.filesystem import path_exists

_MKDOCS_CONFIG = "mkdocs.yml"
_MKDOCS_WORKFLOW = "deploy-mkdocs.yml"
_ZENSICAL_CONFIG = "zensical.toml"
_ZENSICAL_WORKFLOW = "deploy-zensical.yml"
_DOCS_DIR = "docs"


def run_replace_mkdocs_with_zensical(
    *,
    target_path: Path,
    source_path: Path,
) -> list[ActionResult]:
    """Remove MkDocs and establish Zensical in target_path.

    Idempotent: each step is a no-op if already in target state.
    """
    results: list[ActionResult] = []

    # --- Conditional: tear down MkDocs only if present ---

    if path_exists(target_path, _MKDOCS_CONFIG):
        from se_admin.actions.copy_file import run_delete_file
        from se_admin.domain.operations import DeleteFile

        results.append(
            run_delete_file(DeleteFile(path=_MKDOCS_CONFIG), target_path=target_path)
        )
        results.append(
            run_patch_toml(
                PatchToml(
                    file="pyproject.toml",
                    operation="remove_dependency",
                    group="docs",
                    name="mkdocs",
                ),
                target_path=target_path,
            )
        )
        results.append(
            run_remove_workflow(
                RemoveWorkflow(name=_MKDOCS_WORKFLOW),
                target_path=target_path,
            )
        )

    # --- Establish Zensical ---

    results.append(
        run_copy_file(
            CopyFile(src=_ZENSICAL_CONFIG, dest=_ZENSICAL_CONFIG),
            target_path=target_path,
            source_path=source_path,
        )
    )
    results.append(
        run_patch_toml(
            PatchToml(
                file="pyproject.toml",
                operation="add_dependency",
                group="docs",
                name="zensical",
            ),
            target_path=target_path,
        )
    )
    results.append(
        run_ensure_workflow(
            EnsureWorkflow(
                name=_ZENSICAL_WORKFLOW,
                src=f".github/workflows/{_ZENSICAL_WORKFLOW}",
            ),
            target_path=target_path,
            source_path=source_path,
        )
    )
    results.append(
        run_ensure_directory(
            EnsureDirectory(path=_DOCS_DIR),
            target_path=target_path,
        )
    )

    return results
