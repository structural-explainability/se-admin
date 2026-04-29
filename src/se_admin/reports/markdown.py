"""Markdown findings report - suitable for saving to reports/ or posting to CI."""

from datetime import UTC, datetime

from se_admin.domain.findings import Finding, FindingStatus
from se_admin.utils.text import status_icon


def render_markdown(
    findings: list[Finding],
    *,
    title: str = "SE Admin Check Report",
    include_timestamp: bool = True,
) -> str:
    """Render findings as a Markdown document."""
    lines: list[str] = []

    lines.append(f"# {title}")
    lines.append("")

    if include_timestamp:
        ts = datetime.now(tz=UTC).strftime("%Y-%m-%d %H:%M UTC")
        lines.append(f"_Generated: {ts}_")
        lines.append("")

    if not findings:
        lines.append("No findings.")
        return "\n".join(lines)

    lines.extend(_summary_table(findings))
    lines.append("")
    lines.extend(_findings_by_repo(findings))

    return "\n".join(lines)


def _summary_table(findings: list[Finding]) -> list[str]:
    passed = sum(1 for f in findings if f.passed)
    failed = sum(1 for f in findings if f.failed)
    skipped = sum(1 for f in findings if f.status == FindingStatus.SKIP)
    errors = sum(1 for f in findings if f.status == FindingStatus.ERROR)
    repos = len({f.repo for f in findings})

    return [
        "## Summary",
        "",
        "| Status | Count |",
        "|--------|-------|",
        f"| ✓ Pass  | {passed} |",
        f"| ✗ Fail  | {failed} |",
        f"| – Skip  | {skipped} |",
        f"| ! Error | {errors} |",
        f"| **Repos checked** | {repos} |",
    ]


def _findings_by_repo(findings: list[Finding]) -> list[str]:
    by_repo: dict[str, list[Finding]] = {}
    for f in findings:
        by_repo.setdefault(f.repo, []).append(f)

    lines: list[str] = ["## Findings by Repo", ""]

    for repo_name, repo_findings in sorted(by_repo.items()):
        failed = any(f.failed for f in repo_findings)
        marker = " ✗" if failed else " ✓"
        lines.append(f"### `{repo_name}`{marker}")
        lines.append("")
        lines.append("| Status | Check | Path | Message |")
        lines.append("|--------|-------|------|---------|")
        for f in repo_findings:
            icon = status_icon(f.status)
            path = f"`{f.path}`" if f.path else ""
            msg = f.message or ""
            lines.append(f"| {icon} | `{f.check}` | {path} | {msg} |")
        lines.append("")

    return lines
