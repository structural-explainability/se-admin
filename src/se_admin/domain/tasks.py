"""Task domain type - loaded from data/tasks/*.toml."""

import tomllib  # noqa: I001
from dataclasses import dataclass, field
from pathlib import Path
from typing import Self

from se_admin.domain.selectors import Selector, selector_from_dict


@dataclass
class TaskSource:
    """Canonical source repo for file-copy operations."""

    repo: str


@dataclass
class Task:
    """A named, declarative unit of work over a set of repos.

    *operations* is kept as raw dicts here; the interpreter
    (app.py / runner) is responsible for parsing them into
    domain/operations.py types and dispatching to actions.
    """

    id: str
    label: str
    source: TaskSource | None
    selector: Selector | None
    operations: list[dict] = field(default_factory=list)

    @classmethod
    def from_toml(cls, path: Path) -> Self:
        """Load a Task from a TOML file."""
        with path.open("rb") as f:
            data = tomllib.load(f)

        task_meta = data.get("task", {})
        task_id = task_meta.get("id")
        task_label = task_meta.get("label")

        if not task_id:
            raise ValueError(
                f"Task file {path.name} is missing required field: [task].id"
            )
        if not task_label:
            raise ValueError(
                f"Task file {path.name} is missing required field: [task].label\n"
                f"  Fix: add 'label = \"...\"' under [task] in {path}"
            )

        source = TaskSource(**data["source"]) if "source" in data else None
        selector = selector_from_dict(data["selector"]) if "selector" in data else None
        operations = data.get("operations", [])

        return cls(
            id=task_id,
            label=task_label,
            source=source,
            selector=selector,
            operations=operations,
        )

    @classmethod
    def load_all(cls, tasks_dir: Path) -> dict[str, Self]:
        """Load every *.toml in tasks_dir, keyed by task id."""
        tasks: dict[str, Self] = {}
        for p in sorted(tasks_dir.glob("*.toml")):
            t = cls.from_toml(p)
            tasks[t.id] = t
        return tasks
