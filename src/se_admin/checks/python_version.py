"""Check Python version alignment in a repo.

Two distinct checks:
  python_version_file   - .python-version pin matches expected
  requires_python       - pyproject.toml requires-python specifier present
"""

from pathlib import Path

from se_admin.domain.findings import Finding, FindingStatus
from se_admin.observe.pyproject import get_python_version_file, get_requires_python


def check_python_version(
    repo: str,
    repo_path: Path,
    expected_version: str,
) -> list[Finding]:
    """Check .python-version pin equals expected_version (e.g. '3.12')."""
    actual = get_python_version_file(repo_path)

    if actual is None:
        return [
            Finding(
                repo=repo,
                check="python_version_file",
                status=FindingStatus.FAIL,
                path=".python-version",
                message=".python-version file missing",
            )
        ]

    if actual == expected_version:
        return [
            Finding(
                repo=repo,
                check="python_version_file",
                status=FindingStatus.PASS,
                path=".python-version",
            )
        ]

    return [
        Finding(
            repo=repo,
            check="python_version_file",
            status=FindingStatus.FAIL,
            path=".python-version",
            message=f"Expected {expected_version!r}, found {actual!r}",
        )
    ]


def check_requires_python(
    repo: str,
    repo_path: Path,
    expected_specifier: str | None = None,
) -> list[Finding]:
    """Check that requires-python is set in pyproject.toml.

    If expected_specifier is given, also assert it matches exactly.
    """
    actual = get_requires_python(repo_path)

    if actual is None:
        return [
            Finding(
                repo=repo,
                check="requires_python",
                status=FindingStatus.FAIL,
                path="pyproject.toml",
                message="requires-python not set in [project]",
            )
        ]

    if expected_specifier is not None and actual != expected_specifier:
        return [
            Finding(
                repo=repo,
                check="requires_python",
                status=FindingStatus.FAIL,
                path="pyproject.toml",
                message=f"Expected requires-python={expected_specifier!r}, found {actual!r}",
            )
        ]

    return [
        Finding(
            repo=repo,
            check="requires_python",
            status=FindingStatus.PASS,
            path="pyproject.toml",
        )
    ]
