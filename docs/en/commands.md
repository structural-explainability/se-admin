# Commands

## Global Options

```text
--data PATH    Path to data directory (default: data/)
```

## show

Show available admin capability areas.

```bash
uv run python -m se_admin show
uv run python -m se_admin show --area validate
```

Options: `all` | `scaffold` | `sync` | `validate` | `workflows`

## repos

List repos defined in `repos.toml`.

```bash
uv run python -m se_admin repos
uv run python -m se_admin repos --set foundation
uv run python -m se_admin repos --active-only
```

Repo sets are defined in `repos.toml` under `[repo_sets]`.

Options:

- `--set NAME` - limit output to repos in the named repo set
    (e.g. `foundation`, `theory`, `papers`).
- `--active-only` - exclude repos with `status = "legacy"` or any non-active status.

## tasks

List available tasks from `data/tasks/`.

```bash
uv run python -m se_admin tasks
```

## check

Run profile checks against a repo or repo set.
Exits `0` if all checks pass, `1` if any fail.

```bash
uv run python -m se_admin check --repo se-admin
uv run python -m se_admin check --set foundation
uv run python -m se_admin check --set theory --profile lean
```

## run

Execute a task by id. Use `--dry-run` to preview without making changes.

```bash
uv run python -m se_admin run normalize_core_files --dry-run
uv run python -m se_admin run replace_mkdocs_with_zensical --dry-run
uv run python -m se_admin run sync_dependabot_and_pull --dry-run
```
