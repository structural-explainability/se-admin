"""Application orchestration for se_admin."""


def run_show(*, area: str = "all") -> int:
    """Show available admin capabilities."""
    items: list[str] = []

    if area in ("all", "scaffold"):
        items.append("scaffold: repository templates and creation")

    if area in ("all", "sync"):
        items.append("sync: propagate configuration across repositories")

    if area in ("all", "validate"):
        items.append("validate: run cross-repo constitution validation")

    if area in ("all", "workflows"):
        items.append("workflows: shared GitHub Actions")

    print("SE admin capabilities:")
    for item in items:
        print(f"- {item}")

    return 0
