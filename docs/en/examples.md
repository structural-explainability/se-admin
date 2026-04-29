# Examples

## Check a single repo

```bash
uv run python -m se_admin check --repo se-admin
```

```text
se-admin  (6 pass, 0 fail)
  ✓ [required_paths]  pyproject.toml
  ✓ [required_paths]  src
  ✓ [required_paths]  tests
  ✓ [required_workflows]  .github/workflows/ci-python-zensical.yml
  ✓ [required_paths]  zensical.toml
  ✓ [required_workflows]  .github/workflows/deploy-zensical.yml
```

## Check an entire repo set

```bash
uv run python -m se_admin check --set foundation
```

## Dry-run a task

Preview what a task would do without making any changes.

```bash
uv run python -m se_admin run normalize_core_files --dry-run
```

```text
[dry-run] Task: Ensure all canonical files are present

  to se-constitution
    – ensure_exact_files: would run ensure_exact_files
    – delete_files: would run delete_files

  to se-admin
    – ensure_exact_files: would run ensure_exact_files
    – delete_files: would run delete_files
```

## Migrate MkDocs to Zensical across a set

```bash
uv run python -m se_admin run replace_mkdocs_with_zensical --dry-run
uv run python -m se_admin run replace_mkdocs_with_zensical
```

The task is idempotent - repos already on Zensical are no-ops.

## Sync Dependabot PRs and pull

```bash
uv run python -m se_admin run sync_dependabot_and_pull
```

Merges all passing Dependabot PRs via `gh`, then runs `git pull --ff-only`
across the selected repo sets.

## Tool transition pattern

A tool transition is a declarative description of how to remove one
capability and establish another across all affected surfaces.

```text
Sequence(
  Conditional(detect_mkdocs, Sequence(
    delete_file("mkdocs.yml"),
    remove_dependency(group="docs", name="mkdocs"),
    remove_workflow("deploy-mkdocs.yml")
  )),
  Sequence(
    copy_file("zensical.toml"),
    add_dependency(group="docs", name="zensical"),
    ensure_workflow("deploy-zensical.yml"),
    ensure_directory("docs")
  )
)
```

As a task file:

```toml
[task]
id = "replace_mkdocs_with_zensical"
label = "Migrate MkDocs to Zensical"

[source]
repo = "se-admin"

[selector]
repo_sets = ["foundation", "theory"]

[[operations]]
type = "delete_files"
paths = ["mkdocs.yml"]

[[operations]]
type = "remove_dependency"
group = "docs"
name = "mkdocs"

[[operations]]
type = "remove_workflow"
name = "deploy-mkdocs.yml"

[[operations]]
type = "ensure_exact_files"
paths = ["zensical.toml"]

[[operations]]
type = "add_dependency"
group = "docs"
name = "zensical"

[[operations]]
type = "ensure_workflow"
name = "deploy-zensical.yml"
```
