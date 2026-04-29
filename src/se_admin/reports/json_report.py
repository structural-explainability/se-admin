"""JSON findings report - machine-readable output for CI and tooling."""

from datetime import UTC, datetime
import json

from se_admin.domain.findings import Finding


def render_json(
    findings: list[Finding],
    *,
    pretty: bool = True,
) -> str:
    """Render findings as a JSON string."""
    ts = datetime.now(tz=UTC).isoformat()

    by_repo: dict[str, list[dict]] = {}
    for f in findings:
        by_repo.setdefault(f.repo, []).append(_finding_dict(f))

    passed = sum(1 for f in findings if f.passed)
    failed = sum(1 for f in findings if f.failed)

    doc = {
        "generated_at": ts,
        "summary": {
            "total": len(findings),
            "passed": passed,
            "failed": failed,
            "repos": len(by_repo),
        },
        "findings": by_repo,
    }

    indent = 2 if pretty else None
    return json.dumps(doc, indent=indent)


def _finding_dict(f: Finding) -> dict:
    d: dict = {
        "check": f.check,
        "status": f.status,
    }
    if f.path is not None:
        d["path"] = f.path
    if f.message is not None:
        d["message"] = f.message
    return d


def write_json_report(
    findings: list[Finding],
    output_path,
    *,
    pretty: bool = True,
) -> None:
    """Write a JSON report to output_path."""
    from pathlib import Path

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_json(findings, pretty=pretty), encoding="utf-8")
