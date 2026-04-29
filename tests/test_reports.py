"""Tests for Finding domain types and finding aggregation.

Reports layer consumes these types - these tests cover the facts
that reports depend on being stable.
"""

from se_admin.domain.findings import Finding, FindingStatus

# ---------------------------------------------------------------------------
# FindingStatus
# ---------------------------------------------------------------------------


def test_finding_status_values_are_strings() -> None:
    """FindingStatus values should be usable as plain strings."""
    assert FindingStatus.PASS == "pass"  # noqa: S105
    assert FindingStatus.FAIL == "fail"
    assert FindingStatus.SKIP == "skip"
    assert FindingStatus.ERROR == "error"


# ---------------------------------------------------------------------------
# Finding construction
# ---------------------------------------------------------------------------


def test_finding_pass_is_passed() -> None:
    """passed property should be True for PASS status."""
    f = Finding(repo="repo-a", check="required_paths", status=FindingStatus.PASS)
    assert f.passed is True
    assert f.failed is False


def test_finding_fail_is_failed() -> None:
    """failed property should be True for FAIL status."""
    f = Finding(repo="repo-a", check="required_paths", status=FindingStatus.FAIL)
    assert f.failed is True
    assert f.passed is False


def test_finding_skip_is_neither_passed_nor_failed() -> None:
    """SKIP should not count as passed or failed."""
    f = Finding(repo="repo-a", check="exact_files", status=FindingStatus.SKIP)
    assert f.passed is False
    assert f.failed is False


def test_finding_stores_path() -> None:
    """path field should be stored as provided."""
    f = Finding(
        repo="repo-a",
        check="required_paths",
        status=FindingStatus.FAIL,
        path="pyproject.toml",
    )
    assert f.path == "pyproject.toml"


def test_finding_stores_message() -> None:
    """message field should be stored as provided."""
    f = Finding(
        repo="repo-a",
        check="required_paths",
        status=FindingStatus.FAIL,
        message="Required path missing: src",
    )
    assert f.message == "Required path missing: src"


def test_finding_defaults_path_and_message_to_none() -> None:
    """path and message should default to None."""
    f = Finding(repo="repo-a", check="tags", status=FindingStatus.PASS)
    assert f.path is None
    assert f.message is None


# ---------------------------------------------------------------------------
# Aggregation helpers (used by reports layer)
# ---------------------------------------------------------------------------


def _sample_findings() -> list[Finding]:
    return [
        Finding(repo="repo-a", check="required_paths", status=FindingStatus.PASS),
        Finding(
            repo="repo-a",
            check="required_paths",
            status=FindingStatus.FAIL,
            path="src",
            message="Required path missing: src",
        ),
        Finding(repo="repo-b", check="required_workflows", status=FindingStatus.PASS),
        Finding(repo="repo-b", check="exact_files", status=FindingStatus.SKIP),
        Finding(
            repo="repo-c",
            check="required_paths",
            status=FindingStatus.ERROR,
            message="Unexpected error",
        ),
    ]


def test_filter_failures() -> None:
    """Filtering by failed should isolate only FAIL findings."""
    findings = _sample_findings()
    failures = [f for f in findings if f.failed]
    assert len(failures) == 1
    assert failures[0].path == "src"


def test_filter_by_repo() -> None:
    """Findings should be filterable by repo name."""
    findings = _sample_findings()
    repo_b = [f for f in findings if f.repo == "repo-b"]
    assert len(repo_b) == 2


def test_count_by_status() -> None:
    """Status counts should be derivable from a findings list."""
    findings = _sample_findings()
    counts: dict[FindingStatus, int] = {}
    for f in findings:
        counts[f.status] = counts.get(f.status, 0) + 1
    assert counts[FindingStatus.PASS] == 2
    assert counts[FindingStatus.FAIL] == 1
    assert counts[FindingStatus.SKIP] == 1
    assert counts[FindingStatus.ERROR] == 1


def test_all_passed_when_no_failures() -> None:
    """A findings list with no FAILs should be considered all-passed."""
    findings = [
        Finding(repo="repo-a", check="c", status=FindingStatus.PASS),
        Finding(repo="repo-a", check="c", status=FindingStatus.SKIP),
    ]
    assert all(not f.failed for f in findings)


def test_repos_with_failures() -> None:
    """Should be able to derive which repos have at least one failure."""
    findings = _sample_findings()
    failing_repos = {f.repo for f in findings if f.failed}
    assert failing_repos == {"repo-a"}
