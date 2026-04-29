"""Check that required workflow files are present in a repo."""

from pathlib import Path

from se_admin.domain.findings import Finding, FindingStatus
from se_admin.observe.workflows import check_required_workflows as _observe


def check_required_workflows(
    repo: str,
    repo_path: Path,
    names: list[str],
) -> list[Finding]:
    """Return one Finding per workflow - PASS if present, FAIL if missing."""
    results = _observe(repo_path, names)
    findings: list[Finding] = []

    for name, present in results.items():
        findings.append(
            Finding(
                repo=repo,
                check="required_workflows",
                status=FindingStatus.PASS if present else FindingStatus.FAIL,
                path=f".github/workflows/{name}",
                message=None if present else f"Required workflow missing: {name}",
            )
        )

    return findings
