# Changelog

<!-- markdownlint-disable MD024 -->

All notable changes to this project will be documented in this file.

The format is based on **[Keep a Changelog](https://keepachangelog.com/en/1.1.0/)**
and this project adheres to **[Semantic Versioning](https://semver.org/spec/v2.0.0.html)**.

## [Unreleased]

---

## [0.1.1] - 2026-04-29

### Added

- Data-driven DSL architecture: declarative TOML task files interpreted by
  a composable operation tree (`AtomicOperation | OpSequence | Conditional`)
- Domain layer: `repos`, `profiles`, `selectors`, `tasks`, `findings`,
  `operations`, `capabilities`
- Observe layer: `filesystem`, `toml_files`, `pyproject`, `workflows`,
  `git`, `github` - actual repo state, no decisions
- Actions layer: `copy_file`, `replace_file`, `patch_toml`,
  `patch_markdown`, `run_command` - primitive idempotent mutations
- Checks layer: `required_paths`, `exact_files`, `workflows`,
  `python_version`, `reference_files`, `tags` - pure comparisons
  returning `Finding` objects
- Migrations layer: `replace_mkdocs_with_zensical`, `python_package_profile`,
  `python_tooling_profile`, `python_version`, `workflow_names` -
  composed action sequences
- Reports layer: `summary` (terminal), `markdown` (docs/CI),
  `json_report` (machine-readable)
- CLI commands: `show`, `repos`, `tasks`, `check`, `run`
- `check` command: profile checks against a single repo or repo set,
  exits 1 on any failure
- `run` command: execute a task by id with `--dry-run` support
- Profile `extends` - profiles can reference other profiles;
  `all_repos` baseline profile composes `markdown` + `links`
- `all_repos` added as first profile on all repo entries, replacing
  explicit `links` declarations
- `profiles.toml`: structured by language/toolchain then docs generator
  then cross-cutting; `html_static`, `markdown`, `all_repos` profiles added
- `repos.toml`: all repos updated to use `all_repos` baseline
- Task files: `normalize_core_files`, `normalize_lychee_location` label
  fields added; friendly error on missing `[task].label`
- `utils/paths.py`, `utils/text.py` - path resolution and text formatting
  utilities
- Tests: `test_config_loader`, `test_profiles`, `test_required_paths`,
  `test_reports`
- Docs: `concepts.md`, `commands.md`, `configuration.md`, `examples.md`

### Fixed

- `domain/operations.py` forward reference resolved with
  `from __future__ import annotations`
- Ruff suppressions: `S603`, `S607` (subprocess), `S310` (urlopen)

---

## [0.1.0] - 2026-04-22

### Added

- Initial release of administrative tooling for the SE ecosystem
- Canonical admin capabilities:
  - scaffolding
  - synchronization
  - validation orchestration
  - workflow reuse
- Minimal Python CLI for inspecting admin capabilities
- SE_MANIFEST repository declaration for `se-admin`
- Documentation site (folder-based navigation)
- CI: GitHub Actions (lint, type check, tests, docs build)
- Repository hygiene:
  - Ruff (lint and format)
  - pre-commit hooks

---

## Notes on versioning and releases

- We use **SemVer**:
  - **MAJOR** – breaking changes to artifact structure or validation semantics
  - **MINOR** – backward-compatible additions to schema or validation rules
  - **PATCH** – fixes, documentation, tooling
- Versions are driven by git tags. Tag `vX.Y.Z` to release.
- Docs are deployed per version tag and aliased to **latest**.
- Sample commands:

```shell
# as needed
git tag -d v0.1.0
git push origin :refs/tags/v0.1.0

# new tag / release
git tag v0.1.0 -m "0.1.0"
git push origin v0.1.0
```

[Unreleased]: https://github.com/structural-explainability/se-admin/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/structural-explainability/se-admin/releases/tag/v0.1.1
[0.1.0]: https://github.com/structural-explainability/se-admin/releases/tag/v0.1.0
