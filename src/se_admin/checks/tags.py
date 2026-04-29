"""Check that a GitHub repo has the expected topic tags."""

from se_admin.domain.findings import Finding, FindingStatus
from se_admin.observe.github import get_repo_topics


def check_tags(
    repo: str,
    owner: str,
    token: str,
    expected: list[str],
) -> list[Finding]:
    """Return one Finding per expected tag - PASS if present, FAIL if missing."""
    actual = set(get_repo_topics(owner, repo, token))
    findings: list[Finding] = []

    for tag in expected:
        present = tag in actual
        findings.append(
            Finding(
                repo=repo,
                check="tags",
                status=FindingStatus.PASS if present else FindingStatus.FAIL,
                path=None,
                message=None if present else f"Topic tag missing: {tag!r}",
            )
        )

    return findings


def check_no_unexpected_tags(
    repo: str,
    owner: str,
    token: str,
    allowed: list[str],
) -> list[Finding]:
    """Return FAIL Findings for any topic tags not in the allowed list."""
    actual = set(get_repo_topics(owner, repo, token))
    allowed_set = set(allowed)
    findings: list[Finding] = []

    for tag in sorted(actual - allowed_set):
        findings.append(
            Finding(
                repo=repo,
                check="tags",
                status=FindingStatus.FAIL,
                path=None,
                message=f"Unexpected topic tag: {tag!r}",
            )
        )

    return findings
