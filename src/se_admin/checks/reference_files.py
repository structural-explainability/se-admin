"""Check that a repo's reference/ directory exists and contains expected files."""

from pathlib import Path

from se_admin.domain.findings import Finding, FindingStatus
from se_admin.observe.filesystem import is_directory, path_exists

_REFERENCE_DIR = "reference"


def check_reference_files(
    repo: str,
    repo_path: Path,
    expected_paths: list[str] | None = None,
) -> list[Finding]:
    """Check the reference/ directory and optionally specific files within it.

    Without expected_paths: PASS if reference/ exists, FAIL if not.
    With expected_paths: one Finding per path under reference/.
    """
    findings: list[Finding] = []

    dir_present = is_directory(repo_path, _REFERENCE_DIR)

    if not dir_present:
        findings.append(
            Finding(
                repo=repo,
                check="reference_files",
                status=FindingStatus.FAIL,
                path=_REFERENCE_DIR,
                message="reference/ directory missing",
            )
        )
        # No point checking contents if directory is absent
        return findings

    findings.append(
        Finding(
            repo=repo,
            check="reference_files",
            status=FindingStatus.PASS,
            path=_REFERENCE_DIR,
        )
    )

    if expected_paths:
        for rel in expected_paths:
            full_rel = f"{_REFERENCE_DIR}/{rel}"
            exists = path_exists(repo_path, full_rel)
            findings.append(
                Finding(
                    repo=repo,
                    check="reference_files",
                    status=FindingStatus.PASS if exists else FindingStatus.FAIL,
                    path=full_rel,
                    message=None
                    if exists
                    else f"Expected reference file missing: {full_rel}",
                )
            )

    return findings
