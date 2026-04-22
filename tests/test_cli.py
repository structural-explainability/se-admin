"""Minimal CLI smoke tests for se_admin."""

from se_admin.app import run_show
from se_admin.cli import build_parser


def test_run_show_all() -> None:
    """Default show should succeed."""
    rc = run_show(area="all")
    assert rc == 0


def test_run_show_scaffold() -> None:
    """Scaffold area should succeed."""
    rc = run_show(area="scaffold")
    assert rc == 0


def test_run_show_validate() -> None:
    """Validate area should succeed."""
    rc = run_show(area="validate")
    assert rc == 0


def test_parser_accepts_show() -> None:
    """Parser should accept show command."""
    parser = build_parser()
    args = parser.parse_args(["show"])
    assert args.command == "show"
