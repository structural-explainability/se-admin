"""TOML mutation action.

PatchToml dispatches to one of five operations:
  set_key            - write a value at a dotted key path
  remove_key         - delete a key (no-op if absent)
  add_dependency     - append to optional-dependency group (idempotent)
  remove_dependency  - remove from optional-dependency group (idempotent)
  ensure_table       - create a table header if absent

Uses tomlkit for style-preserving round-trip editing.
"""

from pathlib import Path

import tomlkit

from se_admin.actions import ActionResult
from se_admin.domain.operations import PatchToml


def _load(p: Path) -> tomlkit.TOMLDocument:
    if p.exists():
        return tomlkit.parse(p.read_text(encoding="utf-8"))
    return tomlkit.document()


def _save(p: Path, doc: tomlkit.TOMLDocument) -> None:
    p.write_text(tomlkit.dumps(doc), encoding="utf-8")


def _resolve(doc: tomlkit.TOMLDocument, dotted: str) -> tuple[dict, str]:
    """Walk dotted key path; return (parent_table, final_key)."""
    parts = dotted.split(".")
    current: dict = doc  # type: ignore[assignment]
    for part in parts[:-1]:
        if part not in current:
            current[part] = tomlkit.table()
        current = current[part]  # type: ignore[assignment]
    return current, parts[-1]


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------


def run_patch_toml(op: PatchToml, *, target_path: Path) -> ActionResult:
    """Run a PatchToml operation."""
    dispatch = {
        "set_key": _set_key,
        "remove_key": _remove_key,
        "add_dependency": _add_dependency,
        "remove_dependency": _remove_dependency,
        "ensure_table": _ensure_table,
    }
    fn = dispatch.get(op.operation)
    if fn is None:
        return ActionResult.error(f"Unknown PatchToml operation: {op.operation!r}")
    return fn(op, target_path=target_path)


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------


def _set_key(op: PatchToml, *, target_path: Path) -> ActionResult:
    """Set a key in a TOML file."""
    p = target_path / op.file
    doc = _load(p)
    parent, key = _resolve(doc, op.key)  # type: ignore[arg-type]
    if parent.get(key) == op.value:
        return ActionResult.noop(f"Key already set: {op.key}")
    parent[key] = op.value
    _save(p, doc)
    return ActionResult.done(f"Set {op.key} = {op.value!r} in {op.file}")


def _remove_key(op: PatchToml, *, target_path: Path) -> ActionResult:
    p = target_path / op.file
    if not p.exists():
        return ActionResult.noop(f"File absent: {op.file}")
    doc = _load(p)
    parts = op.key.split(".")  # type: ignore[union-attr]
    current: dict = doc  # type: ignore[assignment]
    for part in parts[:-1]:
        if part not in current:
            return ActionResult.noop(f"Key already absent: {op.key}")
        current = current[part]  # type: ignore[assignment]
    final = parts[-1]
    if final not in current:
        return ActionResult.noop(f"Key already absent: {op.key}")
    del current[final]
    _save(p, doc)
    return ActionResult.done(f"Removed {op.key} from {op.file}")


def _add_dependency(op: PatchToml, *, target_path: Path) -> ActionResult:
    """Add op.name to [project.optional-dependencies.<group>]."""
    p = target_path / op.file
    doc = _load(p)

    project = doc.setdefault("project", tomlkit.table())
    opt = project.setdefault("optional-dependencies", tomlkit.table())
    group_list: list = opt.setdefault(op.group, tomlkit.array())

    name_lower = op.name.lower()  # type: ignore[union-attr]
    if any(str(d).lower().startswith(name_lower) for d in group_list):
        return ActionResult.noop(f"{op.name!r} already in [{op.group}] in {op.file}")

    group_list.append(op.name)
    _save(p, doc)
    return ActionResult.done(f"Added {op.name!r} to [{op.group}] in {op.file}")


def _remove_dependency(op: PatchToml, *, target_path: Path) -> ActionResult:
    """Remove op.name from [project.optional-dependencies.<group>]."""
    p = target_path / op.file
    if not p.exists():
        return ActionResult.noop(f"File absent: {op.file}")
    doc = _load(p)

    group_list: list = (
        doc.get("project", {}).get("optional-dependencies", {}).get(op.group, [])
    )

    name_lower = op.name.lower()  # type: ignore[union-attr]
    matches = [d for d in group_list if str(d).lower().startswith(name_lower)]
    if not matches:
        return ActionResult.noop(
            f"{op.name!r} already absent from [{op.group}] in {op.file}"
        )

    for m in matches:
        group_list.remove(m)
    _save(p, doc)
    return ActionResult.done(f"Removed {op.name!r} from [{op.group}] in {op.file}")


def _ensure_table(op: PatchToml, *, target_path: Path) -> ActionResult:
    """Create a table at the dotted key path if not already present."""
    p = target_path / op.file
    doc = _load(p)
    parent, key = _resolve(doc, op.key)  # type: ignore[arg-type]
    if key in parent:
        return ActionResult.noop(f"Table already exists: {op.key}")
    parent[key] = tomlkit.table()
    _save(p, doc)
    return ActionResult.done(f"Created table {op.key} in {op.file}")
