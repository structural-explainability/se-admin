"""Capability areas exposed by se_admin."""

from enum import StrEnum


class Capability(StrEnum):
    """Distinct capability areas of se_admin functionality."""

    SCAFFOLD = "scaffold"
    SYNC = "sync"
    VALIDATE = "validate"
    WORKFLOWS = "workflows"


CAPABILITY_LABELS: dict[Capability, str] = {
    Capability.SCAFFOLD: "repository templates and creation",
    Capability.SYNC: "propagate configuration across repositories",
    Capability.VALIDATE: "run cross-repo constitution validation",
    Capability.WORKFLOWS: "shared GitHub Actions",
}
