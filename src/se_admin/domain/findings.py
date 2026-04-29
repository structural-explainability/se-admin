"""Finding - the result of a single check against a repo."""

from dataclasses import dataclass
from enum import StrEnum


class FindingStatus(StrEnum):
    """Finding status: pass, fail, skip, or error."""

    PASS = "pass"  # noqa: S105
    FAIL = "fail"
    SKIP = "skip"
    ERROR = "error"


@dataclass
class Finding:
    """A finding represents the result of a single check against a repository."""

    repo: str
    check: str
    status: FindingStatus
    path: str | None = None
    message: str | None = None

    @property
    def passed(self) -> bool:
        """Return True if this finding represents a passing check."""
        return self.status == FindingStatus.PASS

    @property
    def failed(self) -> bool:
        """Return True if this finding represents a failing check."""
        return self.status == FindingStatus.FAIL
