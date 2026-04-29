"""src/se_admin/actions/dependabot.py.

Actions related to Dependabot PRs, using GitHub CLI.
"""

import json
from pathlib import Path

from se_admin.utils.subprocesses import run_command

# === List Dependabot PRs ===


def list_dependabot_prs(repo_path: Path) -> list[dict]:
    """List open Dependabot PRs in the given repo, with metadata."""
    result = run_command(
        [
            "gh",
            "pr",
            "list",
            "--author",
            "dependabot[bot]",
            "--state",
            "open",
            "--json",
            "number,title,mergeable,reviewDecision,statusCheckRollup",
        ],
        cwd=repo_path,
    )

    if result.returncode != 0:
        return []

    return json.loads(result.stdout)


# === Merge Dependabot PR ===


def merge_dependabot_pr(repo_path: Path, pr_number: int) -> tuple[bool, str]:
    """Merge the given Dependabot PR number in the given repo, using squash merge."""
    result = run_command(
        [
            "gh",
            "pr",
            "merge",
            str(pr_number),
            "--squash",
            "--delete-branch",
        ],
        cwd=repo_path,
    )

    if result.returncode == 0:
        return True, result.stdout.strip()

    message = result.stderr.strip() or result.stdout.strip()
    return False, message
