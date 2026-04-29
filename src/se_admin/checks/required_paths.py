"""Check that declared required paths exist in a repo."""

from pathlib import Path

from se_admin.domain.findings import Finding, FindingStatus
from se_admin.observe.filesystem import check_required_paths as _observe


def check_required_paths(
    repo: str,
    repo_path: Path,
    paths: list[str],
) -> list[Finding]:
    """Return one Finding per path - PASS if present, FAIL if missing."""
    results = _observe(repo_path, paths)
    findings: list[Finding] = []

    for rel_path, exists in results.items():
        findings.append(
            Finding(
                repo=repo,
                check="required_paths",
                status=FindingStatus.PASS if exists else FindingStatus.FAIL,
                path=rel_path,
                message=None if exists else f"Required path missing: {rel_path}",
            )
        )

    return findings
