"""Text formatting utilities for se_admin."""


def table(
    rows: list[dict[str, str]],
    columns: list[str],
    *,
    min_width: int = 4,
) -> str:
    """Render a list of dicts as a plain-text table.

    columns defines the ordered keys and header labels.
    Each key is also used as the column header.
    """
    widths = {col: max(min_width, len(col)) for col in columns}
    for row in rows:
        for col in columns:
            widths[col] = max(widths[col], len(row.get(col, "")))

    header = "  ".join(col.ljust(widths[col]) for col in columns)
    divider = "  ".join("-" * widths[col] for col in columns)
    body_rows = [
        "  ".join(row.get(col, "").ljust(widths[col]) for col in columns)
        for row in rows
    ]
    return "\n".join([header, divider, *body_rows])


def truncate(text: str, max_len: int, suffix: str = "…") -> str:
    """Truncate text to max_len characters, appending suffix if cut."""
    if len(text) <= max_len:
        return text
    return text[: max_len - len(suffix)] + suffix


def status_icon(status: str) -> str:
    """Return a single-character icon for a FindingStatus string."""
    return {
        "pass": "✓",
        "fail": "✗",
        "skip": "–",
        "error": "!",
    }.get(status, "?")


def pluralise(count: int, singular: str, plural: str | None = None) -> str:
    """Return '1 repo' or '3 repos'."""
    word = singular if count == 1 else (plural or singular + "s")
    return f"{count} {word}"


def indent(text: str, spaces: int = 2) -> str:
    """Indent every line of text by spaces."""
    pad = " " * spaces
    return "\n".join(pad + line for line in text.splitlines())
