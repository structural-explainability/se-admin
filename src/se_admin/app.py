"""Application orchestration for se_admin."""

from pathlib import Path

from se_admin.actions import ActionResult
from se_admin.actions.copy_file import (
    run_copy_file,
    run_delete_file,
)
from se_admin.actions.patch_toml import run_patch_toml
from se_admin.actions.replace_file import (
    run_ensure_workflow,
    run_remove_workflow,
    run_replace_workflow,
)
from se_admin.checks import run_profile_checks
from se_admin.domain.capabilities import CAPABILITY_LABELS, Capability
from se_admin.domain.findings import Finding
from se_admin.domain.operations import (
    CopyFile,
    DeleteFile,
    EnsureWorkflow,
    PatchToml,
    RemoveWorkflow,
    ReplaceWorkflow,
)
from se_admin.domain.profiles import ProfileRegistry
from se_admin.domain.repos import RepoEntry, RepoRegistry
from se_admin.domain.selectors import (
    PatternSelector,
    RepoNameSelector,
    RepoSetSelector,
)
from se_admin.domain.tasks import Task

# ---------------------------------------------------------------------------
# show
# ---------------------------------------------------------------------------


def run_show(*, area: str = "all") -> int:
    """Show available admin capabilities."""
    targets: list[Capability] = [*Capability] if area == "all" else [Capability(area)]
    print("SE admin capabilities:")
    for cap in targets:
        print(f"  {cap.value}: {CAPABILITY_LABELS[cap]}")
    return 0


# ---------------------------------------------------------------------------
# repos
# ---------------------------------------------------------------------------


def run_repos(
    *,
    data: Path,
    repo_set: str | None = None,
    active_only: bool = False,
) -> int:
    """List repos from repos.toml."""
    registry = RepoRegistry.from_toml(data / "repos.toml")

    if repo_set:
        repos = registry.repos_in_set(repo_set)
    elif active_only:
        repos = registry.active_repos()
    else:
        repos = list(registry.repos.values())

    if not repos:
        print("No repos matched.")
        return 0

    print(f"{'name':<40} {'set':<16} {'profiles'}")
    print("-" * 72)
    for repo in sorted(repos, key=lambda r: r.name):
        profiles = ", ".join(repo.profiles)
        status = f" [{repo.status}]" if repo.status != "active" else ""
        print(f"{repo.name + status:<40} {repo.repo_set:<16} {profiles}")

    return 0


# ---------------------------------------------------------------------------
# tasks
# ---------------------------------------------------------------------------


def run_tasks(*, data: Path) -> int:
    """List available tasks from data/tasks/."""
    tasks_dir = data / "tasks"
    if not tasks_dir.exists():
        print("No tasks directory found.")
        return 1

    tasks = Task.load_all(tasks_dir)
    if not tasks:
        print("No tasks found.")
        return 0

    print(f"{'id':<48} label")
    print("-" * 72)
    for task_id, task in sorted(tasks.items()):
        print(f"{task_id:<48} {task.label}")

    return 0


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------


def run_check(
    *,
    data: Path,
    repo: str | None = None,
    repo_set: str | None = None,
    profile: str | None = None,
) -> int:
    """Run profile checks against a repo or set."""
    repo_registry = RepoRegistry.from_toml(data / "repos.toml")
    profile_registry = ProfileRegistry.from_toml(data / "profiles.toml")
    workspace = repo_registry.workspace_path()

    if repo:
        entry = repo_registry.repos.get(repo)
        if entry is None:
            print(f"Unknown repo: {repo!r}")
            return 1
        entries = [entry]
    elif repo_set:
        entries = repo_registry.repos_in_set(repo_set)
        if not entries:
            print(f"No repos in set: {repo_set!r}")
            return 1
    else:
        print("Specify --repo or --set.")
        return 2

    all_findings: list[Finding] = []

    for entry in entries:
        profile_names = [profile] if profile else entry.profiles
        profiles = profile_registry.resolve(profile_names)
        for prof in profiles:
            findings = run_profile_checks(
                entry,
                prof,
                workspace_path=workspace,
                profile_registry=profile_registry,
            )
            all_findings.extend(findings)

    _print_findings(all_findings)
    failures = [f for f in all_findings if f.failed]
    return 1 if failures else 0


def _print_findings(findings: list[Finding]) -> None:
    if not findings:
        print("No findings.")
        return

    by_repo: dict[str, list[Finding]] = {}
    for f in findings:
        by_repo.setdefault(f.repo, []).append(f)

    for repo_name, repo_findings in sorted(by_repo.items()):
        passed = sum(1 for f in repo_findings if f.passed)
        failed = sum(1 for f in repo_findings if f.failed)
        print(f"\n{repo_name}  ({passed} pass, {failed} fail)")
        for f in repo_findings:
            icon = "✓" if f.passed else ("✗" if f.failed else "–")
            path = f"  {f.path}" if f.path else ""
            msg = f"  {f.message}" if f.message else ""
            print(f"  {icon} [{f.check}]{path}{msg}")


# ---------------------------------------------------------------------------
# run (task executor)
# ---------------------------------------------------------------------------


def run_task(
    *,
    data: Path,
    task_id: str,
    dry_run: bool = False,
) -> int:
    """Execute a task by id."""
    tasks = Task.load_all(data / "tasks")
    task = tasks.get(task_id)
    if task is None:
        available = ", ".join(sorted(tasks.keys()))
        print(
            f"Unknown task: {task_id!r}\n"
            f"  Add a task file: data/tasks/{task_id}.toml\n"
            f"  Available tasks: {available}"
        )
        return 1

    repo_registry = RepoRegistry.from_toml(data / "repos.toml")
    workspace = repo_registry.workspace_path()

    source_path: Path | None = None
    if task.source:
        source_path = workspace / task.source.repo

    entries = _resolve_selector(task, repo_registry)
    if not entries:
        print(f"Task {task_id!r}: no repos matched selector.")
        return 0

    label = "[dry-run] " if dry_run else ""
    print(f"{label}Task: {task.label}")

    total_changed = 0
    total_errors = 0

    for entry in entries:
        target_path = workspace / entry.name
        print(f"\n  to {entry.name}")
        for op_dict in task.operations:
            result = _dispatch(
                op_dict,
                target_path=target_path,
                source_path=source_path,
                dry_run=dry_run,
            )
            icon = "✓" if result.ok else "✗"
            changed = " (changed)" if result.changed else ""
            msg = f": {result.message}" if result.message else ""
            print(f"    {icon} {op_dict.get('type', '?')}{changed}{msg}")
            if result.changed:
                total_changed += 1
            if not result.ok:
                total_errors += 1

    print(f"\n{total_changed} change(s), {total_errors} error(s).")
    return 1 if total_errors else 0


def _resolve_selector(task: Task, registry: RepoRegistry) -> list[RepoEntry]:
    if task.selector is None:
        return []
    sel = task.selector
    if isinstance(sel, RepoSetSelector):
        entries: list[RepoEntry] = []
        for set_name in sel.repo_sets:
            entries.extend(registry.repos_in_set(set_name))
        return entries
    if isinstance(sel, RepoNameSelector):
        return [registry.repos[n] for n in sel.repos if n in registry.repos]
    if isinstance(sel, PatternSelector):
        import re

        pattern = re.compile(sel.pattern)
        return [r for r in registry.repos.values() if pattern.search(r.name)]
    return []


# ---------------------------------------------------------------------------
# Operation interpreter
# ---------------------------------------------------------------------------


def _dispatch(
    op: dict,
    *,
    target_path: Path,
    source_path: Path | None,
    dry_run: bool,
) -> ActionResult:
    """Map a raw TOML operation dict to an action and execute it."""
    op_type = op.get("type", "")

    if dry_run:
        return ActionResult.noop(f"would run {op_type}")

    if op_type == "ensure_exact_files":
        results = [
            run_copy_file(
                CopyFile(src=p, dest=p),
                target_path=target_path,
                source_path=source_path or target_path,
            )
            for p in op.get("paths", [])
        ]
        changed = any(r.changed for r in results)
        errors = [r.message for r in results if not r.ok]
        if errors:
            return ActionResult.error("; ".join(e for e in errors if e))
        return ActionResult(ok=True, changed=changed)

    if op_type == "delete_files":
        results = [
            run_delete_file(DeleteFile(path=p), target_path=target_path)
            for p in op.get("paths", [])
        ]
        changed = any(r.changed for r in results)
        return ActionResult(ok=True, changed=changed)

    if op_type == "add_dependency":
        return run_patch_toml(
            PatchToml(
                file="pyproject.toml",
                operation="add_dependency",
                group=op.get("group"),
                name=op.get("name"),
            ),
            target_path=target_path,
        )

    if op_type == "remove_dependency":
        return run_patch_toml(
            PatchToml(
                file="pyproject.toml",
                operation="remove_dependency",
                group=op.get("group"),
                name=op.get("name"),
            ),
            target_path=target_path,
        )

    if op_type == "ensure_workflow":
        return run_ensure_workflow(
            EnsureWorkflow(name=op["name"], src=op.get("src", op["name"])),
            target_path=target_path,
            source_path=source_path or target_path,
        )

    if op_type == "replace_workflow":
        return run_replace_workflow(
            ReplaceWorkflow(name=op["name"], src=op.get("src", op["name"])),
            target_path=target_path,
            source_path=source_path or target_path,
        )

    if op_type == "remove_workflow":
        return run_remove_workflow(
            RemoveWorkflow(name=op["name"]),
            target_path=target_path,
        )

    if op_type == "git_pull":
        from se_admin.actions.git_pull import git_pull

        ok, message = git_pull(target_path)
        return ActionResult(ok=ok, changed=ok, message=message or None)

    if op_type == "merge_dependabot_prs":
        from se_admin.actions.dependabot import (
            list_dependabot_prs,
            merge_dependabot_pr,
        )

        prs = list_dependabot_prs(target_path)
        if not prs:
            return ActionResult.noop("No open Dependabot PRs")
        merged = 0
        merge_errors: list[str] = []
        for pr in prs:
            ok, msg = merge_dependabot_pr(target_path, pr["number"])
            if ok:
                merged += 1
            else:
                merge_errors.append(f"#{pr['number']}: {msg}")
        if merge_errors:
            return ActionResult.error("; ".join(merge_errors))
        return ActionResult.done(f"Merged {merged} Dependabot PR(s)")

    return ActionResult.error(f"Unknown operation type: {op_type!r}")
