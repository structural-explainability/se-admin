# se-admin

[![PyPI](https://img.shields.io/pypi/v/se-admin?logo=pypi&label=pypi)](https://pypi.org/project/se-admin/)
[![Docs Site](https://img.shields.io/badge/docs-site-blue?logo=github)](https://structural-explainability.github.io/se-admin/)
[![Repo](https://img.shields.io/badge/repo-GitHub-black?logo=github)](https://github.com/structural-explainability/se-admin)
[![Python 3.15+](https://img.shields.io/badge/python-3.15%2B-blue?logo=python)](./pyproject.toml)
[![License](https://img.shields.io/badge/license-MIT-yellow.svg)](./LICENSE)

[![CI](https://github.com/structural-explainability/se-admin/actions/workflows/ci-python-zensical.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-admin/actions/workflows/ci-python-zensical.yml)
[![Docs](https://github.com/structural-explainability/se-admin/actions/workflows/deploy-zensical.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-admin/actions/workflows/deploy-zensical.yml)
[![Release](https://github.com/structural-explainability/se-admin/actions/workflows/release-pypi.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-admin/actions/workflows/release-pypi.yml)
[![Links](https://github.com/structural-explainability/se-admin/actions/workflows/links.yml/badge.svg?branch=main)](https://github.com/structural-explainability/se-admin/actions/workflows/links.yml)

> Structural Explainability Admin:
> administration of the SE ecosystem.

SE Admin is a data-driven system that applies composable operations
over repository surfaces
with declarative targets and selectable scope
to move repos between states.

## Owns

- enforcement of constitution (automation)
- repository lifecycle operations
- cross-repository consistency

## Includes

scaffolding

- repository templates

synchronization

- configuration propagation

validation orchestration

- multi-repo validation execution

workflow reuse

- shared GitHub Actions

bulk operations

- dependency upgrades
- structural updates

## Overview

```text
data/       = declared desired state, no logic, only declarations
observe/    = actual repo state, no decisions, only facts
checks/     = pure comparison, no side effects
actions/    = primitive mutations
migrations/ = composed actions
reports/    = human/machine output projections only
```

```text
domain/
  repo        - repository
  profile     = named bundle of expectations (paths, workflows, checks)
  selector    = how you choose repos (set, name, pattern)
  finding     = result of a check
```

```text
repos.toml       = instances: which repos exist, repo sets, assigned profiles
profiles.toml    = reusable traits: profile definitions
checks.toml      = constraints: check definitions and canonical comparisons
migrations.toml  = transformations: named migration recipes
```

```text
data (declared) -> observe (actual) -> checks (compare) -> actions/migrations -> reports
```

## Operation Requirements

Data describes operations and a small interpreter executing them

All operations must be:

- deterministic
- idempotent
- side-effect scoped

Examples:

- delete_file is OK if missing
- add_dependency is OK if already present
- replace_text is no-op if not found

## Operation Taxonomy

### Detection (no side effects)

- path_exists
- path_missing
- toml_key_exists
- toml_value_equals
- dependency_present
- workflow_present

### Mutation (single responsibility)

Filesystem

- create_file
- delete_file
- copy_file
- ensure_directory
- rename_path
  TOML
- toml_set_key
- toml_remove_key
- toml_add_dependency
- toml_remove_dependency
- toml_ensure_table
  Workflows (still files, but special intent)
- ensure_workflow
- remove_workflow
- replace_workflow
  Text
- replace_block
- insert_block
- remove_block
  Process
- run_command

## Composition

```text
Operation =
  AtomicOperation
  | Sequence[Operation]
  | Conditional(condition, Operation)
```

## Example

A tool transition is a declarative description of how to
remove one capability and establish another across all affected surfaces.

```text
Sequence(
  Conditional(detect_mkdocs, Sequence(
    delete_file("mkdocs.yml"),
    toml_remove_dependency("mkdocs"),
    remove_workflow("deploy-mkdocs.yml")
  )),

  Sequence(
    create_file("zensical.toml"),
    toml_add_dependency(group="docs", name="zensical"),
    ensure_workflow("deploy-zensical.yml"),
    ensure_directory("docs")
  )
)
```

## Command Reference

<details>
<summary>Show command reference</summary>

### In a machine terminal

Open a machine terminal where you want the project:

```shell
git clone https://github.com/structural-explainability/se-admin

cd se-admin
code .
```

### In a VS Code terminal

```shell
# if strange errors, clean uv cache
# uv cache clean

uv self update
uv python pin 3.15
uv sync --extra dev --extra docs --upgrade

uvx pre-commit install

git add -A
uvx pre-commit run --all-files
# repeat if changes were made
git add -A
uvx pre-commit run --all-files

# run the module
uv run python -m se_admin show

# do chores
uv run python -m pyright
uv run python -m pytest
uv run python -m zensical build

# save progress
git add -A
git commit -m "update"
git push -u origin main
```

Portability fixture checks verifying that `se-admin`
can load and operate on a non-SE repository family
using an alternate data root.

```shell
uv run python -m se_admin --data tests/fixtures/streaming-admin/data repos
uv run python -m se_admin --data tests/fixtures/streaming-admin/data check --set modules
uv run python -m se_admin --data tests/fixtures/streaming-admin/data check --set admin
uv run python -m se_admin --data tests/fixtures/streaming-admin/data run --dry-run normalize_core_files

</details>

## Citation

[CITATION.cff](./CITATION.cff)

## License

[LICENSE](./LICENSE)

## Manifest

[SE_MANIFEST.toml](./SE_MANIFEST.toml)
