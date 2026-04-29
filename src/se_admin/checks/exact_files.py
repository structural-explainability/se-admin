"""Check that files in a repo match the canonical source exactly."""

from pathlib import Path

from se_admin.domain.findings import Finding, FindingStatus


def check_exact_files(
    repo: str,
    repo_path: Path,
    paths: list[str],
    source_path: Path,
) -> list[Finding]:
    """Compare each path byte-for-byte against the canonical source.

    Findings:
      FAIL - file missing in target
      FAIL - file present but differs from source
      PASS - file matches source exactly
      SKIP - source file missing (cannot compare)
    """
    findings: list[Finding] = []

    for rel in paths:
        src = source_path / rel
        dest = repo_path / rel

        if not src.exists():
            findings.append(
                Finding(
                    repo=repo,
                    check="exact_files",
                    status=FindingStatus.SKIP,
                    path=rel,
                    message=f"Source file not found, cannot compare: {rel}",
                )
            )
            continue

        if not dest.exists():
            findings.append(
                Finding(
                    repo=repo,
                    check="exact_files",
                    status=FindingStatus.FAIL,
                    path=rel,
                    message=f"File missing in target: {rel}",
                )
            )
            continue

        if dest.read_bytes() == src.read_bytes():
            findings.append(
                Finding(
                    repo=repo,
                    check="exact_files",
                    status=FindingStatus.PASS,
                    path=rel,
                )
            )
        else:
            findings.append(
                Finding(
                    repo=repo,
                    check="exact_files",
                    status=FindingStatus.FAIL,
                    path=rel,
                    message=f"File differs from canonical source: {rel}",
                )
            )

    return findings
