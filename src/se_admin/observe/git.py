"""Git observation - local repo state via subprocess.

No decisions, no side effects.  Returns plain facts.
"""

from pathlib import Path
import subprocess


def _git(repo_path: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(  # noqa: S603
        ["git", *args],  # noqa: S607
        cwd=repo_path,
        capture_output=True,
        text=True,
    )


def is_git_repo(repo_path: Path) -> bool:
    """Return True if repo_path is inside a Git repository."""
    result = _git(repo_path, "rev-parse", "--git-dir")
    return result.returncode == 0


def current_branch(repo_path: Path) -> str | None:
    """Return the name of the current branch, or None if not on a branch."""
    result: subprocess.CompletedProcess = _git(
        repo_path, "rev-parse", "--abbrev-ref", "HEAD"
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def is_clean(repo_path: Path) -> bool:
    """True if there are no uncommitted changes."""
    result: subprocess.CompletedProcess = _git(repo_path, "status", "--porcelain")
    return result.returncode == 0 and result.stdout.strip() == ""


def has_remote(repo_path: Path, remote: str = "origin") -> bool:
    """Return True if the given remote is configured."""
    result: subprocess.CompletedProcess = _git(repo_path, "remote")
    return remote in result.stdout.splitlines()


def remote_url(repo_path: Path, remote: str = "origin") -> str | None:
    """Return the URL of the given remote, or None if not configured."""
    result: subprocess.CompletedProcess = _git(repo_path, "remote", "get-url", remote)
    if result.returncode != 0:
        return None
    return result.stdout.strip()


def local_branch_exists(repo_path: Path, branch: str) -> bool:
    """Return True if the given branch exists locally."""
    result: subprocess.CompletedProcess = _git(repo_path, "branch", "--list", branch)
    return bool(result.stdout.strip())


def behind_remote(repo_path: Path, branch: str = "main") -> int:
    """Return number of commits local is behind origin/branch (0 = up to date)."""
    result: subprocess.CompletedProcess = _git(
        repo_path,
        "rev-list",
        "--count",
        f"HEAD..origin/{branch}",
    )
    if result.returncode != 0:
        return 0
    try:
        return int(result.stdout.strip())
    except ValueError:
        return 0
