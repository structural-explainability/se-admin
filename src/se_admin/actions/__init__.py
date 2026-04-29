"""se_admin actions layer - primitive mutations, single responsibility each.

Every action:
- is deterministic
- is idempotent (no-op if already in target state)
- returns ActionResult
- scopes side effects to the target repo_path
"""

from dataclasses import dataclass
from typing import Self


@dataclass
class ActionResult:
    """Result of performing an action."""

    ok: bool
    changed: bool
    message: str | None = None

    @classmethod
    def noop(cls, message: str | None = None) -> Self:
        """Return an ActionResult representing a no-op (no changes made)."""
        return cls(ok=True, changed=False, message=message)

    @classmethod
    def done(cls, message: str | None = None) -> Self:
        """Return an ActionResult representing a successful action with changes."""
        return cls(ok=True, changed=True, message=message)

    @classmethod
    def error(cls, message: str) -> Self:
        """Return an ActionResult representing a failed action."""
        return cls(ok=False, changed=False, message=message)
