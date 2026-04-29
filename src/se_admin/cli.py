"""Command-line interface for se_admin."""

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    """Build the argument parser for the se_admin CLI."""
    parser = argparse.ArgumentParser(
        prog="se_admin",
        description="Administrative tools for the SE ecosystem.",
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path("data"),
        help="Path to data directory (default: data/).",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # show - capabilities overview (existing, kept for compat)
    show_parser = subparsers.add_parser("show", help="Show capabilities.")
    show_parser.add_argument(
        "--area",
        choices=["all", "scaffold", "sync", "validate", "workflows"],
        default="all",
    )

    # repos - list known repos, optionally filtered by set
    repos_parser = subparsers.add_parser("repos", help="List known repos.")
    repos_parser.add_argument("--set", dest="repo_set", help="Filter by repo set.")
    repos_parser.add_argument("--active-only", action="store_true", default=False)

    # tasks - list available tasks from data/tasks/
    subparsers.add_parser("tasks", help="List available tasks.")

    # check - run profile checks against a repo or set
    check_parser = subparsers.add_parser("check", help="Run profile checks.")
    check_target = check_parser.add_mutually_exclusive_group(required=True)
    check_target.add_argument("--repo", help="Single repo name.")
    check_target.add_argument("--set", dest="repo_set", help="Repo set name.")
    check_parser.add_argument("--profile", help="Limit to a single profile.")

    # run - execute a task by id
    run_parser = subparsers.add_parser("run", help="Execute a task.")
    run_parser.add_argument("task_id", help="Task id from data/tasks/.")
    run_parser.add_argument("--dry-run", action="store_true", default=False)

    return parser


def main() -> int:
    """Main entry point for the CLI."""
    from se_admin.app import run_check, run_repos, run_show, run_task, run_tasks

    parser = build_parser()
    args = parser.parse_args()

    if args.command == "show":
        return run_show(area=args.area)

    if args.command == "repos":
        return run_repos(
            data=args.data,
            repo_set=args.repo_set,
            active_only=args.active_only,
        )

    if args.command == "tasks":
        return run_tasks(data=args.data)

    if args.command == "check":
        return run_check(
            data=args.data,
            repo=args.repo,
            repo_set=args.repo_set,
            profile=args.profile,
        )

    if args.command == "run":
        return run_task(
            data=args.data,
            task_id=args.task_id,
            dry_run=args.dry_run,
        )

    parser.error(f"Unknown command: {args.command}")
    return 2
