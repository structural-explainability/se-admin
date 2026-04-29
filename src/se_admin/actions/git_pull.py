"""src/se_admin/actions/git_pull.py."""

from pathlib import Path

from se_admin.utils.subprocesses import run_command

# === Git Pull ===


def git_pull(repo_path: Path) -> tuple[bool, str]:
    """Perform a git pull --ff-only in the given repo."""
    result = run_command(["git", "pull", "--ff-only"], cwd=repo_path)

    if result.returncode == 0:
        return True, result.stdout.strip()

    message = result.stderr.strip() or result.stdout.strip()
    return False, message
