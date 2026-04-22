"""Command-line interface for se_admin."""

import argparse

from se_admin.app import run_show


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser."""
    parser = argparse.ArgumentParser(
        prog="se_admin",
        description="Administrative tools for the SE ecosystem.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    show_parser = subparsers.add_parser(
        "show",
        help="Show available admin capabilities.",
    )
    show_parser.add_argument(
        "--area",
        choices=["all", "scaffold", "sync", "validate", "workflows"],
        default="all",
        help="Admin capability area to display.",
    )

    return parser


def main() -> int:
    """Run the command-line interface."""
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "show":
        return run_show(area=args.area)

    parser.error(f"Unknown command: {args.command}")
    return 2
