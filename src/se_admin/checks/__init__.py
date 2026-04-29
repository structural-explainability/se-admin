"""se_admin checks layer - pure comparisons, no side effects.

Each check reads actual state via observe/ and returns Finding objects.
Nothing in this layer writes to disk or calls external services
(except checks/tags.py which reads from the GitHub API).
"""

from pathlib import Path

from se_admin.checks.exact_files import check_exact_files
from se_admin.checks.python_version import check_python_version
from se_admin.checks.reference_files import check_reference_files
from se_admin.checks.required_paths import check_required_paths
from se_admin.checks.tags import check_tags
from se_admin.checks.workflows import check_required_workflows
from se_admin.domain.findings import Finding
from se_admin.domain.profiles import Profile, ProfileRegistry
from se_admin.domain.repos import RepoEntry


def run_profile_checks(
    repo: RepoEntry,
    profile: Profile,
    *,
    workspace_path: Path,
    source_path: Path | None = None,
    profile_registry: ProfileRegistry | None = None,
) -> list[Finding]:
    """Run all checks implied by a profile against a repo.

    Returns the combined list of Finding objects.
    source_path is required only for exact_files checks.

    Args:
        repo: the repository to check
        profile: the profile whose checks to run
        *: keyword-only arguments after this point
        workspace_path: the base path where repositories are located on disk
        source_path: optional path to use as source for exact_files checks
        profile_registry: optional profile registry for resolving extended profiles

    Returns:
        list of Finding objects for all checks that failed
    """
    repo_path = workspace_path / repo.name
    findings: list[Finding] = []

    # Expand extended profiles first
    if profile.extends and profile_registry is not None:
        for extended_id in profile.extends:
            extended = profile_registry.get(extended_id)
            if extended is None:
                raise KeyError(
                    f"Profile {profile.id!r} extends unknown profile: {extended_id!r}"
                )
            findings += run_profile_checks(
                repo,
                extended,
                workspace_path=workspace_path,
                source_path=source_path,
                profile_registry=profile_registry,
            )

    if profile.required_paths:
        findings += check_required_paths(repo.name, repo_path, profile.required_paths)

    if profile.required_workflows:
        findings += check_required_workflows(
            repo.name, repo_path, profile.required_workflows
        )

    return findings


__all__ = [
    "check_exact_files",
    "check_python_version",
    "check_reference_files",
    "check_required_paths",
    "check_required_workflows",
    "check_tags",
    "run_profile_checks",
]
