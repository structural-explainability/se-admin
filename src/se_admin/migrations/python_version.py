"""Migration: update the Python version pin in a repo.

Touches:
  .python-version          - pinned interpreter version
  pyproject.toml           - requires-python specifier
"""

from pathlib import Path

from se_admin.actions import ActionResult
from se_admin.actions.patch_toml import run_patch_toml
from se_admin.domain.operations import PatchToml
from se_admin.observe.pyproject import get_python_version_file, get_requires_python


def run_python_version(
    *,
    target_path: Path,
    version: str,
    requires_python: str | None = None,
) -> list[ActionResult]:
    """Update the Python version pin in target_path.

    Args:
        *: Keyword-only for clarity at call site, since version and requires_python
          are related and it's easy to mix them up.
        target_path: The repo root to operate on.
        version:         The exact pin to write to .python-version, e.g. '3.13'.
        requires_python: The specifier to write to pyproject.toml, e.g. '>=3.13'.
                         Derived from version if not provided.

    Idempotent: no-op if already at target version.
    """
    results: list[ActionResult] = []
    specifier = requires_python or f">={version}"

    # --- .python-version ---
    current_pin = get_python_version_file(target_path)
    pin_path = target_path / ".python-version"

    if current_pin == version:
        results.append(ActionResult.noop(f".python-version already {version}"))
    else:
        pin_path.write_text(version + "\n", encoding="utf-8")
        results.append(ActionResult.done(f".python-version to {version}"))

    # --- pyproject.toml requires-python ---
    current_spec = get_requires_python(target_path)

    if current_spec == specifier:
        results.append(ActionResult.noop(f"requires-python already {specifier}"))
    else:
        results.append(
            run_patch_toml(
                PatchToml(
                    file="pyproject.toml",
                    operation="set_key",
                    key="project.requires-python",
                    value=specifier,
                ),
                target_path=target_path,
            )
        )

    return results
