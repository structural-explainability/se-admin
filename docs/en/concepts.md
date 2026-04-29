# Concepts

SE Admin is a data-driven system that applies composable operations
over repository surfaces with declarative targets and selectable scope
to move repos between states.

## Layers

```text
data/       = declared desired state - no logic, only declarations
observe/    = actual repo state - no decisions, only facts
checks/     = pure comparison - no side effects
actions/    = primitive mutations
migrations/ = composed actions
reports/    = human/machine output projections only
```

## Domain

```text
repo        - a git repository in the SE ecosystem
profile     - named bundle of expectations (paths, workflows, checks)
selector    - how you choose repos (set, name, pattern)
finding     - result of a check (pass, fail, skip, error)
task        - declarative unit of work: selector + operations
```

## Data Files

```text
repos.toml       - which repos exist, repo sets, assigned profiles
profiles.toml    - reusable traits: profile definitions
checks.toml      - check definitions and canonical comparisons
migrations.toml  - named migration recipes
data/tasks/      - individual task files, one per operation recipe
```

## Operation Taxonomy

### Detection (no side effects)

- `check_path` - assert a path exists or is missing
- `check_toml_key` - assert a TOML key exists or holds a value

### Mutation - Filesystem

- `copy_file`, `replace_file`, `delete_file`, `ensure_directory`

### Mutation - TOML

- `patch_toml` - set key, remove key, add/remove dependency, ensure table

### Mutation - Workflows

- `ensure_workflow`, `replace_workflow`, `remove_workflow`

### Mutation - Text

- `patch_markdown_section` - replace, insert, or remove a heading block

### Mutation - Process

- `run_command`

## Composition

```text
Operation =
  AtomicOperation
  | OpSequence[Operation]
  | Conditional(condition, Operation)
```

All operations are deterministic, idempotent, and side-effect scoped.
