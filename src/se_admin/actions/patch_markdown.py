"""Markdown section mutation action.

PatchMarkdownSection - find a heading block and replace, insert, or remove it.

Section boundaries are defined by ATX headings (# through ######).
A section runs from its heading line to the line before the next
heading of equal or lesser depth (or end of file).
"""

from pathlib import Path
import re

from se_admin.actions import ActionResult
from se_admin.domain.operations import PatchMarkdownSection

_HEADING = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


def _heading_depth(line: str) -> int:
    m = re.match(r"^(#{1,6})\s", line)
    return len(m.group(1)) if m else 0


def _find_section(lines: list[str], heading_text: str) -> tuple[int, int] | None:
    """Return (start, end) line indices for the section, or None if not found.

    *start* is the heading line; *end* is exclusive (first line of next
    same-or-lesser-depth heading, or len(lines)).
    """
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,6})\s+(.+)$", line.rstrip())
        if m and m.group(2).strip() == heading_text.strip():
            depth = len(m.group(1))
            end = len(lines)
            for j in range(i + 1, len(lines)):
                d = _heading_depth(lines[j])
                if d > 0 and d <= depth:
                    end = j
                    break
            return i, end
    return None


def run_patch_markdown_section(
    op: PatchMarkdownSection, *, target_path: Path
) -> ActionResult:
    """Run the given PatchMarkdownSection operation on the target repo."""
    dispatch = {
        "replace": _replace_section,
        "insert": _insert_section,
        "remove": _remove_section,
    }
    fn = dispatch.get(op.operation)
    if fn is None:
        return ActionResult.error(
            f"Unknown PatchMarkdownSection operation: {op.operation!r}"
        )
    return fn(op, target_path=target_path)


def _replace_section(op: PatchMarkdownSection, *, target_path: Path) -> ActionResult:
    p = target_path / op.file
    if not p.exists():
        return ActionResult.error(f"File not found: {op.file}")

    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    span = _find_section(lines, op.section)
    if span is None:
        return ActionResult.error(f"Section not found: {op.section!r} in {op.file}")

    start, end = span
    replacement = (op.content or "").rstrip("\n") + "\n"
    new_lines = lines[:start] + [replacement] + lines[end:]
    p.write_text("".join(new_lines), encoding="utf-8")
    return ActionResult.done(f"Replaced section {op.section!r} in {op.file}")


def _insert_section(op: PatchMarkdownSection, *, target_path: Path) -> ActionResult:
    """Append the section at end of file if not already present."""
    p = target_path / op.file
    text = p.read_text(encoding="utf-8") if p.exists() else ""
    lines = text.splitlines(keepends=True)

    if _find_section(lines, op.section) is not None:
        return ActionResult.noop(
            f"Section already present: {op.section!r} in {op.file}"
        )

    content = (op.content or "").rstrip("\n") + "\n"
    separator = "\n" if text and not text.endswith("\n\n") else ""
    p.write_text(text + separator + content, encoding="utf-8")
    return ActionResult.done(f"Inserted section {op.section!r} in {op.file}")


def _remove_section(op: PatchMarkdownSection, *, target_path: Path) -> ActionResult:
    p = target_path / op.file
    if not p.exists():
        return ActionResult.noop(f"File absent: {op.file}")

    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
    span = _find_section(lines, op.section)
    if span is None:
        return ActionResult.noop(f"Section already absent: {op.section!r} in {op.file}")

    start, end = span
    new_lines = lines[:start] + lines[end:]
    p.write_text("".join(new_lines), encoding="utf-8")
    return ActionResult.done(f"Removed section {op.section!r} from {op.file}")
