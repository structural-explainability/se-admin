# DECISIONS.md (se-admin)

Design history and rationale.

---

## Append-Only

This document grows with the project.
New decisions are appended.
Existing decisions are not edited.
Superseding decisions reference the one they replace.

---

## D-001. `se-admin` is an administrative engine, not an SE-only script collection

**Status:** Accepted

**Context:**
`se-admin` began in the Structural Explainability ecosystem, but its useful
boundary is broader:
it loads repository declarations, profiles, tasks, and checks from data files
and applies deterministic administrative operations across repository families.

The package code should be reusable across repository families.
The local `data/` directory in this repository is one instance of that engine
for the SE repository family.

**Decision:**
`se-admin` is the reusable administrative engine.

Repository-family-specific declarations belong in the admin repository for that
family, including:

- `data/repos.toml`
- `data/profiles.toml`
- `data/tasks/*.toml`
- family-specific standards and selectors

The SE repository family may keep SE-specific task declarations in this repo.
Other families, such as course repositories, should provide their own task files.

**Consequences:**

- The Python package must remain independent of hardcoded SE repository names and
  absolute local paths.
- The `--data` option is the boundary for selecting a repository family.
- Each admin repository owns its own task declarations.
- Task files may name a family-specific source repository, such as `se-admin` or
  `streaming-00-admin`.
- The engine can be reused without copying SE-specific declarations.

---

## D-002. Manifest validation is centralized in `se-admin`

**Status:** Accepted

**Context:**
Repositories managed by `se-admin`, may include `SE_MANIFEST.toml` files.
Requiring every managed repository to depend directly on `se-manifest-schema`
would duplicate validation tooling across repositories and add dependencies
to repos that only need to be validated administratively.

`se-admin` is the family-level administration tool. It performs
cross-repository checks, maintenance, and validation orchestration.

**Decision:**
`se-admin` depends on `se-manifest-schema` and owns administrative
manifest validation across managed repositories.

Managed repositories may include `SE_MANIFEST.toml` without depending directly
on `se-manifest-schema`, unless they need manifest validation as part of their
own package behavior.

**Consequences:**

- Manifest validation has one administrative home.
- Course repositories and SE repositories can use `SE_MANIFEST.toml`
  consistently.
- Ordinary managed repositories remain lighter.
- `se-admin` can run manifest checks consistently across repository families.
- Repositories that define schema semantics or expose manifest-validation
  behavior may still depend directly on `se-manifest-schema`.
