# Configuration

## repos.toml

Declares which repos exist, how they are grouped, and which profiles apply.

```toml
[family]
id = "structural-explainability"
label = "Structural Explainability"
workspace_root = ".."

[repo_sets.foundation]
label = "Foundation repositories"
repos = ["se-constitution", "se-admin", "se-kernel"]

[repos.se-admin]
repo_set = "foundation"
profiles = ["all_repos", "python_package", "zensical", "links"]
```

`workspace_root` is resolved relative to the location of `repos.toml`.
Repos not listed in any `repo_set` are still valid but won't be selected
by set-based selectors.

## profiles.toml

Defines reusable bundles of expectations.

```toml
[profiles.python_package]
label = "Python package repository"
required_paths = ["pyproject.toml", "src", "tests"]
required_workflows = [".github/workflows/ci-python-zensical.yml"]

[profiles.zensical]
label = "Zensical documentation repository"
required_paths = ["zensical.toml", "docs"]
required_workflows = [".github/workflows/deploy-zensical.yml"]

[profiles.zensical.pyproject]
required_optional_dependency_groups = ["docs"]

[profiles.zensical.pyproject.optional_dependencies.docs]
required = ["zensical"]
```

## data/tasks/

Each file is a self-contained declarative task.

```toml
[task]
id = "normalize_core_files"
label = "Ensure all canonical files are present"

[source]
repo = "se-admin"

[[operations]]
type = "ensure_exact_files"
paths = [".gitignore", ".editorconfig", ".github/lychee.toml"]

[[operations]]
type = "delete_files"
paths = ["lychee.toml", ".lychee.toml"]
```

### Task fields

| Field | Required | Description |
|-------|----------|-------------|
| `[task].id` | yes | Unique identifier, used with `run` command |
| `[task].label` | yes | Human-readable description |
| `[source].repo` | no | Canonical source repo for file-copy operations |
| `[selector]` | no | Which repos to target (see below) |
| `[[operations]]` | yes | One or more operation dicts |

### Selectors

```toml
# By repo set
[selector]
repo_sets = ["foundation", "theory"]

# By name
[selector]
repos = ["se-admin", "se-kernel"]

# By pattern
[selector]
pattern = "^se-theory-"
```

### Operation types

| type | required fields | description |
|------|----------------|-------------|
| `ensure_exact_files` | `paths` | Copy files from source repo if absent or changed |
| `delete_files` | `paths` | Delete files, no-op if missing |
| `add_dependency` | `group`, `name` | Add to `pyproject.toml` optional-dependencies |
| `remove_dependency` | `group`, `name` | Remove from optional-dependencies |
| `ensure_workflow` | `name` | Add workflow if not present |
| `replace_workflow` | `name` | Overwrite workflow unconditionally |
| `remove_workflow` | `name` | Delete workflow, no-op if missing |
| `git_pull` | - | `git pull --ff-only` |
| `merge_dependabot_prs` | - | Merge all open Dependabot PRs via `gh` |
