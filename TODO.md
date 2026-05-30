# SE Admin TODO

Manifest conformance tracker for the `structural-explainability` repos.

**Validator:** `uv run se-manifest verify-graph` (run from `se-manifest-schema`)
**Status enum source:** `se-manifest-schema/manifest-schema.toml` - confirm allowed
`status` / `class` values before applying any below; do not invent a value the
validator rejects.

---

## 0. Capture verifier diagnostics

- [ ] Run `verify-graph` and record the actual pass/fail output (the loading phase
      lists all local manifests; conformance findings come after it).
- [ ] Paste failures into **Verifier findings** below, one repo per line.

---

## 1. Canonical cardinality - confirmed; defined in `se-theory-identity-regimes`

Owned and defined by `se-theory-identity-regimes` (Lean is the only source of truth;
registries in `reference/`: `regime-families.toml`, `regime-profiles.toml`,
`regime-profile-derivation.toml`, classification matrix). Confirmed current there: six
canonical regimes refined into nine profile kinds over a ten-family transformation
basis. The six are correct - "not enough" meant refining them into nine profile kinds,
not that six was wrong.

This is the **theory's** regime/profile axis. It is **not** AE's entity-kind axis. AE's
ALIESO entity kinds (`Actor … Observation`) are a separate, implementation-level axis
(see §2). Never cross-cite one as the other.

- [x] Theory regime / profile-kind structure: confirmed; owned by `se-theory-identity-regimes`.
- [ ] Everything downstream points to that owner for these counts; never restates them (§7).

---

## 2. AccountableEntities - update the implementation against the theory

AE (and EP) are **implementations of the theory**, not the theory itself. AE's six
ALIESO entity kinds (`Actor … Observation`) are AE's own axis; the theory's regimes and
nine profile kinds live in `se-theory-identity-regimes`. AE does not "become nine" - it
needs updating to track the current theory it implements.

Currently AE maps each ALIESO entity kind one-to-one to a `*Bound` regime
(`ActorBound …`), proven total/one-to-one in Lean - but those `*Bound` names are not the
theory's canonical regimes (`OBL/NOR/OCC/CTX/REC/ENR`). AE is carrying its own regime
vocabulary instead of referencing the definer. That gap is the update.

- [ ] Confirm the architecture: AE/EP are implementations of the theory (your working
      model). This reclassifies them away from the README's "Formalizations" framing.
- [ ] Decide whether AE imports regimes/profile kinds from `se-theory-identity-regimes`
      rather than defining its own `*Bound` set. Theory rule: Lean is the only source of
      truth; implementations reference, they don't redefine.
- [ ] Update AE's mapping/proofs to track the current theory, then update the README
      summary + Core Mapping table (both assert the standalone six).
- [ ] Manifest `class`: revisit - implementation, not `theory` (see block below; confirm
      against schema enum).

Manifest direction (confirm enum values against schema):

```toml
[repo]
name    = "AccountableEntities"
org     = "structural-explainability"
class   = "implementation"    # impl of the theory, not "theory"; confirm schema enum
kind    = "lean-implementation"
status  = "active"            # keep active only after the §2 update; else archive
summary = "Lean 4 implementation of Accountable Entities over the SE identity-regime theory."

[layer]
space = "structural-explainability"
role  = "implementation"

[scope]
includes = [
  "AE ALIESO entity kinds and their mapping onto the identity-regime theory",
]
excludes = [
  "definition of regimes / profile kinds (owned by se-theory-identity-regimes)",
  "normative AE specification authority (spec-ae)",
  "operational contract exports",
]
```

---

## 3. Manifest filename inconsistency

- [ ] `records/judicial-record-us-federal-supreme` uses `MANIFEST.toml`, not
      `SE_MANIFEST.toml`. Every other repo uses `SE_MANIFEST.toml`, and the org
      README states all diagram repos declare `SE_MANIFEST.toml`. Confirm
      `verify-graph` ingests it; rename unless the divergence is intentional and
      documented.

---

## 4. Series-number collision (paper companions)

- [ ] Two local repos at series 300: `paper-300-accountable-entities` and
      `paper-300-neutral-representation`. README Papers section documents only
      100/200 + stewardship `SE-ST-Gx`. Confirm intended numbering and resolve.

---

## 5. PascalCase Lean repos - status + six-meaning audit

README states an archived/current split; apply matching `status` + `scope`, and for
each, confirm it carries the nine-profile refinement or is correctly scoped to families
only (§1).

Archived (README "Original / Outdated Foundations"; superseded by `se-theory-*`):

- [ ] `IdentityRegimes` - status archived. Its six-families claim holds (§1); archived
      because the nine-profile-kind refinement lives in `se-theory-identity-regimes`.
- [ ] `NeutralSubstrate` - status archived.
- [ ] `StructuralExplainability` - status archived.

Current (README files these under "Formalizations"; but AE/EP look like implementations
of the theory - see §2, may need a separate grouping) - confirm each maps to its spec:

- [ ] `AccountableEntities` - implementation of the theory; see §2 (↔ `spec-ae`).
- [ ] `EvolutionProtocol` - implementation of the theory; EP graph evolution (↔ `spec-ep`).
- [ ] `CEE` - formalizes the CEE interface (↔ `spec-cee`); confirm formalization vs impl.
- [ ] `GovernanceBoundary` - formalizes GB (↔ `spec-gb`).
- [ ] `InterpretationBoundary` - formalizes IB (↔ `spec-ib`).

---

## 6. Local manifest set vs org documented set

The local `verify-graph` run and the org README cover different repo sets.

- [ ] In README narrative but NOT in local run:
- [ ] 1. `civic-record`
- [ ] 2. `civic-record-py`
- [ ] 3. `energy-record`
- [ ] 4. `infrastructure-record`
- [ ] 5. `judicial-record`
- [ ] 6. `judicial-record-py`
- [ ] 7. `se-govsrc-finland-education`
- [ ] 8. `se-govsrc-norway-education`
- [ ] 9. `se-govsrc-oecd-pisa`
- [ ] 10. `se-govsrc-singapore-education`
- [ ] 11. `se-govsrc-us`
- [ ] 12. `se-govsrc-us-education`
- [ ] 13. `se-govsrc-us-missouri`
- [ ] 14. `se-govsrc-us-missouri-education`
- [ ] In local run but NOT named in README narrative:
- [ ] 1. `records/accountable-record-spec`
- [ ] 2. `records/civic-influence-record-spec`
- [ ] 3. `records/judicial-record-spec`
- [ ] 4. `records/se-verification-civic-influence-record`
- [ ] 5. `records/se-verification-judicial-record`
- [ ] Decide whether `verify-graph` runs against the full org set or a defined local
      subset; document which.

---

## 7. Narrative must point, not specify

Conformance rule: counts, identifier sets, cardinalities,
and enum values live in one machine-readable registry; narrative references it rather
than restating it. Restating lets prose and registry drift.

- [ ] `spec-ae` - "Versioning and Closure" states the entity-kind count in prose. The
      count (six entity kinds) is correct, but replace the prose number with a pointer to
      `IDENTIFIERS.md` so it can't drift; keep entity kinds (six) distinct from profile
      kinds (nine).
- [ ] Scan all SE narrative docs for embedded specifics that duplicate a registry
      (kind/family/profile counts, matrix dimensions, identifier lists, enum values);
      convert each to a pointer.
- [ ] org README theory-layer prose - point to `se-theory-identity-regimes` registries
      (`regime-families.toml`, `regime-profiles.toml`) rather than stating counts inline.
      That repo already enforces this (Lean is sole source of truth; docs must not
      redefine formal semantics) - use it as the model.

---

## Repo inventory

### Local verify-graph set

Schema / tooling:

1. `.github`
2. `se-admin`
3. `se-constitution`
4. `se-kernel`
5. `se-manifest-schema`
6. `se-mapspec`
7. `site`

Specs (normative, Python tooling):

1. `spec-ae`
2. `spec-cee`
3. `spec-ep`
4. `spec-gb`
5. `spec-ib`
6. `spec-se`
7. `spec-se-appendix` (informative)

PascalCase Lean - archived (§5):

1. `IdentityRegimes`
2. `NeutralSubstrate`
3. `StructuralExplainability`

PascalCase Lean - current (§5):

1. `AccountableEntities`
2. `CEE`
3. `EvolutionProtocol`
4. `GovernanceBoundary`
5. `InterpretationBoundary`

se-theory (active formal derivation layer):

1. `se-theory-identity-regimes`
2. `se-theory-neutral-substrate`
3. `se-theory-persistence`
4. `se-theory-structural-explainability`
5. `se-theory-transformation`

Regime execution:

1. `se-regimes`
2. `se-regimes-explorer`
3. `se-regimes-pilot-education-math-g8`

Mapping examples:

1. `se-mapping-education`
2. `se-mapping-education-math`
3. `se-mapping-education-math-g8`

Formal contract / misc:

1. `se-formal-contract`
2. `se-st-g1-definition`

Paper companions:

1. `paper-100-neutral-substrate`
2. `paper-200-identity-regimes`
3. `paper-300-accountable-entities`
4. `paper-300-neutral-representation`
5. `paper-400-neutral-decomposition`
6. `paper-500-neutral-obstructions`
7. `paper-capability`
8. `paper-capacity-trajectories`

Records:

1. `records/accountable-record`
2. `records/accountable-record-py`
3. `records/accountable-record-spec`
4. `records/civic-influence-record-spec`
5. `records/judicial-record-spec`
6. `records/judicial-record-us-federal-supreme`
7. `records/se-contract-kit`
8. `records/se-verification-civic-influence-record`
9. `records/se-verification-judicial-record`

### Org repos documented in README but not in local run (§6)

1. `civic-record`
2. `civic-record-py`
3. `energy-record`
4. `infrastructure-record`
5. `judicial-record`
6. `judicial-record-py`
7. `se-govsrc-finland-education`
8. `se-govsrc-norway-education`
9. `se-govsrc-oecd-pisa`
10. `se-govsrc-singapore-education`
11. `se-govsrc-us`
12. `se-govsrc-us-education`
13. `se-govsrc-us-missouri`
14. `se-govsrc-us-missouri-education`
