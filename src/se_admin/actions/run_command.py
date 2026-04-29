"""Process mutation action.

RunCommand - run a shell command inside the target repo directory.
"""

from pathlib import Path
import subprocess

from se_admin.actions import ActionResult
from se_admin.domain.operations import RunCommand


def run_run_command(op: RunCommand, *, target_path: Path) -> ActionResult:
    """Run op.command with op.args in target_path.

    Returns ActionResult.done on exit code 0, ActionResult.error otherwise.
    stdout/stderr are captured and surfaced in the message on failure.
    """
    cmd = [op.command, *op.args]

    result = subprocess.run(  # noqa: S603
        cmd,
        cwd=target_path,
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        return ActionResult.done(
            f"Ran {' '.join(cmd)!r}"
            + (f": {result.stdout.strip()}" if result.stdout.strip() else "")
        )

    detail = result.stderr.strip() or result.stdout.strip()
    return ActionResult.error(
        f"Command failed (exit {result.returncode}): {' '.join(cmd)!r}"
        + (f"\n{detail}" if detail else "")
    )
