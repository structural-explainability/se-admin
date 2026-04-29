"""Tests for the required_paths check."""

from pathlib import Path

from se_admin.checks.required_paths import check_required_paths
from se_admin.domain.findings import FindingStatus


def _make_repo(tmp_path: Path, present: list[str]) -> Path:
    """Create a minimal repo directory with the listed paths."""
    repo = tmp_path / "repo"
    repo.mkdir()
    for rel in present:
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        if "." in p.name:
            p.write_text("")
        else:
            p.mkdir(exist_ok=True)
    return repo


# ---------------------------------------------------------------------------
# Basic pass / fail
# ---------------------------------------------------------------------------


def test_all_paths_present_returns_all_pass(tmp_path: Path) -> None:
    """All required paths present should yield all PASS findings."""
    repo = _make_repo(tmp_path, ["pyproject.toml", "src", "tests"])
    findings = check_required_paths("repo", repo, ["pyproject.toml", "src", "tests"])
    assert all(f.status == FindingStatus.PASS for f in findings)


def test_missing_path_returns_fail(tmp_path: Path) -> None:
    """A missing required path should yield a FAIL finding."""
    repo = _make_repo(tmp_path, ["pyproject.toml"])
    findings = check_required_paths("repo", repo, ["pyproject.toml", "src"])
    statuses = {f.path: f.status for f in findings}
    assert statuses["pyproject.toml"] == FindingStatus.PASS
    assert statuses["src"] == FindingStatus.FAIL


def test_all_paths_missing_returns_all_fail(tmp_path: Path) -> None:
    """No paths present should yield all FAIL findings."""
    repo = _make_repo(tmp_path, [])
    findings = check_required_paths("repo", repo, ["pyproject.toml", "src"])
    assert all(f.status == FindingStatus.FAIL for f in findings)


def test_empty_paths_list_returns_no_findings(tmp_path: Path) -> None:
    """Empty required paths list should return no findings."""
    repo = _make_repo(tmp_path, [])
    findings = check_required_paths("repo", repo, [])
    assert findings == []


# ---------------------------------------------------------------------------
# Finding structure
# ---------------------------------------------------------------------------


def test_finding_repo_name_is_set(tmp_path: Path) -> None:
    """Each finding should carry the correct repo name."""
    repo = _make_repo(tmp_path, [])
    findings = check_required_paths("my-repo", repo, ["README.md"])
    assert all(f.repo == "my-repo" for f in findings)


def test_finding_check_name_is_required_paths(tmp_path: Path) -> None:
    """All findings should be tagged with check='required_paths'."""
    repo = _make_repo(tmp_path, ["README.md"])
    findings = check_required_paths("repo", repo, ["README.md"])
    assert all(f.check == "required_paths" for f in findings)


def test_fail_finding_has_message(tmp_path: Path) -> None:
    """FAIL findings should include a human-readable message."""
    repo = _make_repo(tmp_path, [])
    findings = check_required_paths("repo", repo, ["missing.txt"])
    fail = findings[0]
    assert fail.status == FindingStatus.FAIL
    assert fail.message is not None
    assert "missing.txt" in fail.message


def test_pass_finding_has_no_message(tmp_path: Path) -> None:
    """PASS findings should have no message."""
    repo = _make_repo(tmp_path, ["README.md"])
    findings = check_required_paths("repo", repo, ["README.md"])
    assert findings[0].message is None


# ---------------------------------------------------------------------------
# Nested paths
# ---------------------------------------------------------------------------


def test_nested_path_present_passes(tmp_path: Path) -> None:
    """Nested paths like .github/lychee.toml should resolve correctly."""
    repo = _make_repo(tmp_path, [".github/lychee.toml"])
    findings = check_required_paths("repo", repo, [".github/lychee.toml"])
    assert findings[0].status == FindingStatus.PASS


def test_nested_path_missing_fails(tmp_path: Path) -> None:
    """Missing nested path should yield FAIL."""
    repo = _make_repo(tmp_path, [])
    findings = check_required_paths("repo", repo, [".github/workflows/ci.yml"])
    assert findings[0].status == FindingStatus.FAIL
