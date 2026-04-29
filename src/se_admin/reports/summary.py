"""Plain-text summary report - terminal-friendly findings output."""

from se_admin.domain.findings import Finding, FindingStatus
from se_admin.utils.text import pluralise, status_icon


def render_summary(findings: list[Finding]) -> str:
    """Render findings grouped by repo as a plain-text string."""
    if not findings:
        return "No findings."

    by_repo: dict[str, list[Finding]] = {}
    for f in findings:
        by_repo.setdefault(f.repo, []).append(f)

    lines: list[str] = []

    for repo_name, repo_findings in sorted(by_repo.items()):
        passed = sum(1 for f in repo_findings if f.passed)
        failed = sum(1 for f in repo_findings if f.failed)
        skipped = sum(1 for f in repo_findings if f.status == FindingStatus.SKIP)

        counts = f"{pluralise(passed, 'pass', 'pass')}"
        if failed:
            counts += f", {pluralise(failed, 'fail')}"
        if skipped:
            counts += f", {pluralise(skipped, 'skip')}"

        lines.append(f"\n{repo_name}  ({counts})")

        for f in repo_findings:
            icon = status_icon(f.status)
            path_part = f"  {f.path}" if f.path else ""
            msg_part = f"  {f.message}" if f.message else ""
            lines.append(f"  {icon} [{f.check}]{path_part}{msg_part}")

    lines.append("")
    lines.append(_totals(findings))
    return "\n".join(lines)


def render_totals(findings: list[Finding]) -> str:
    """One-line summary: '12 pass, 2 fail across 4 repos'."""
    return _totals(findings)


def _totals(findings: list[Finding]) -> str:
    passed = sum(1 for f in findings if f.passed)
    failed = sum(1 for f in findings if f.failed)
    repos = len({f.repo for f in findings})

    parts = [pluralise(passed, "pass", "pass")]
    if failed:
        parts.append(pluralise(failed, "fail"))
    parts.append(f"across {pluralise(repos, 'repo')}")
    return ", ".join(parts)
