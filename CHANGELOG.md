# Changelog

All notable changes to the Open Misconceptions are recorded here.
The library follows semantic versioning:

* **patch**: wording, metadata, tooling fixes; no record IDs or statements change.
* **minor**: records added; evidence, discriminators, sources or alignments added to existing records; records deprecated or merged (their IDs keep resolving).
* **major** (after 1.0): the `statement` of a `reviewed` record changes meaning, or a field is removed from the schema.

Before 1.0, minor releases may also change the schema; each such change is called out below.

## [0.2.0] - 2026-09-07

### Changed

* **The project is now Open Misconceptions; the acronym OML is retired** (formerly OML, the Open Misconception Library). It collided with three live things a search engine already knows -- OpenML, openCAESAR's OML modelling language, and Open Metric Learning, whose Python package is imported as `oml`. **The CURIE prefix is now `miscon:`**, the repository and Hugging Face dataset are `open-misconceptions/miscon-data`, the canonical base URI is `https://open-misconceptions.github.io/miscon-data`, the CLI is `miscon`, its config is `miscon.config.json`, and the distributions are `miscon.jsonl`, `miscon.csv` and `miscon.case.json`.
* **Every record ID is respelled in whole words.** `prog` becomes `programming`, and the abbreviated second segments become `fractions`, `decimals`, `arrays`, `booleans`, `functions`, `objects`, `variables`, `execution`, `strings` and `types` -- category areas plural, mass nouns singular, matching the `domain` field, which already spelled them out. The record formerly at `oml:math.frac.add-across` is now `miscon:math.fractions.add-across`. **No v0.1.x ID resolves after this release.** That is a deliberate break, taken at zero adopters and once: `GOVERNANCE.md` now names v0.2.0 as the release from which the never-delete guarantee starts, because a guarantee that does not say when it begins is not a guarantee.
* **`code` is now required on every alignment to an external scheme** (schema change). It applies to both `about[]` and `alignments[]`, and the internal `Miscon` scheme is exempt because its URI is `<base>/c/<concept-id>` and the concept ID already is the code -- the exemption is written into the schema with its reason, so it cannot later be read as an oversight. The argument is the Common Core link rot recorded below: an external scheme's URI can stop resolving without warning, and when it does the code is the only part of the alignment a reader can still act on. No record changed: every external-scheme entry in the corpus already carried a code, which is why this landed before v0.2.0 rather than after, when it would have been a breaking change to a published schema.
* **`kind: missing-prerequisite` is removed from the schema.** A missing prerequisite is an absence, and this library records beliefs -- the public definition is beliefs in, gaps and slips out. Both records using it turned out to state a real belief, so both were re-kinded rather than deprecated: `math.fractions.unequal-parts` to `overgeneralization` (the b-pieces-means-b-ths rule applied past the equal-parts condition), and `programming.functions.base-case-not-needed` to `misapplied-analogy` (everyday stopping-when-done reasoning carried into recursion).
* **The maintainer's durable handle is an ORCID.** `reviewers/registry.json` names `orcid:0009-0002-9041-8322`, keeping `github:vikram-learnco` as an alias. Aliases are now read by `reviewer_weights()`, so a review filed under an earlier handle keeps counting toward `trust` -- without that, promoting the handle would have silently demoted record #1 from `high` to `medium`. The code-of-conduct contact and `CODEOWNERS` follow the same move.
* **Diagnosis records use `miscon_id` and `miscon_version`** in place of the `oml_`-prefixed fields.
* **The library moved to a neutral home.** Canonical base URI is now `https://open-misconceptions.github.io/miscon-data`, and the repository is `open-misconceptions/miscon-data`. **`miscon:` IDs are unchanged and stable** — `miscon:math.fractions.add-across` still means exactly what it meant; only the host that resolves it moved. Applied with `miscon rebase-uri`, which rewrote 188 references across 83 files. The Hugging Face dataset is now `open-misconceptions/miscon-data`.
* **The record licence is unchanged: CC BY 4.0.** A move to CC0 was considered for this release and rejected. CC BY's obligation lands on redistribution rather than use, it is what [OBO Foundry principle 1](https://obofoundry.org/principles/fp-001-open.html) and the Gene Ontology settle on for a resource of this kind, and it keeps the licence continuous across the DOI lineage. Tooling stays MIT. The CASE export's licence title is now read from `miscon.config.json` instead of being hardcoded, so the exported document and the licence URL can no longer disagree.
* **`CONTRIBUTING.md` leads with propose, not contribute.** The front door is an issue; external pull requests are not merged during v0.x, and the path to Contributor (three accepted proposals) is stated. Licence section names the banks whose text must not be pasted, and documents `git commit -s`.
* **The reviewer registry is now authoritative.** A human review with verdict `accept` from a handle not in `reviewers/registry.json` is an error, not a warning: adding yourself to a record no longer promotes it.
* **The library is maintained by Vikram Maram as an individual project.** The MIT copyright holder, the `creator` in `miscon.config.json` (which flows into the CASE `CFDocument`), and the dataset-card attribution now name the maintainer rather than a company. Nothing about the `miscon:` IDs changes.

### Added

* **Every CCSS alignment carries its standard code.** All 16 Common Core URIs the dataset cites now return 404 -- corestandards.org was rebuilt and the `/Math/Content/` paths are gone. **The URIs stay**: that URL form is the identifier CASE frameworks and the Achievement Standards Network align on, so changing it would trade a cosmetic problem for an interoperability one. Instead the 35 entries that had no `code` were filled in (derived from the URI, and the derivation was checked against the 33 entries that already had one -- 33 agreements, 0 mismatches -- before anything was written), `schemes/registry.json` records CCSS as `dereferenceable: false` with the reason, and the site shows `CCSS 5.NF.A.1` with the URI as a plain identifier rather than offering a dead link. Relation targets are matched against the registry by URI pattern, so they get the same treatment.
* **The release refuses to run on a stale `library_version`.** That field in `miscon.config.json` is hand-maintained, and it is not cosmetic: the Pages site is built from `main` and prints it in the footer, with nothing downstream to correct it, so a release cut with the field still on the previous version publishes a site naming the wrong one. `release.yml` now compares it with the tag before the tag or the GitHub release is created, and stops with an error saying what to set and why. It also stamps `CITATION.cff`'s `version` and `date-released` from the tag, so the released citation metadata cannot drift the same way.
* **How to cite** in the README: the release version plus the concept DOI, modelled on the Gene Ontology's citation policy, with a note to cite a record's ID and URI alongside the release.
* **The fork-naming norm** in `GOVERNANCE.md`, adapted from OBO Foundry principle 1: use and redistribute freely provided the origin is acknowledged, but do not alter the library and redistribute the result under the original name or with the same `miscon:` identifiers. An identifier is authoritative only if it resolves at this library's own resolver — anyone may mint an `miscon:`-shaped string; only the registry makes it real. The succession clause is the stated exception.
* **Succession and the right to fork** in `GOVERNANCE.md`: if the maintainer is unresponsive for six months, the Reviewers named in the registry may fork under the same name and IDs, and that fork becomes the one to use. The licence, the Zenodo DOI, the Hugging Face mirror and host-independent IDs exist so that this is always possible.
* **`miscon rebase-uri <new-base>`**: moves the library to a new base URI, rewriting every record `uri`, every Miscon concept URI in `about[]` and `relations.*`, both schema `$id`s, the scheme registry's URI pattern, the config and the docs. Idempotent, `--dry-run` supported, and covered by round-trip tests — a record `uri` is a public identifier, so a partial rewrite is the failure mode worth engineering against.

* **`GOVERNANCE.md`**: role ladder (Reader → Proposer → Contributor → Reviewer → Maintainer, with every tier above Proposer empty at launch except Maintainer), the four classes of change and who may make each, the dispute process, and the weekly triage cadence. Linked from the README and the site footer.
* **Dispute fields**: `disputed` (boolean) and `disputes[]` (issue URLs) on a record. A disputed record stays live and citable; the site shows a banner and links the issues. `disputed: true` requires a linked dispute.
* **Duplicate detection**: `miscon validate` reports two same-domain records whose statements overlap above a similarity threshold unless one declares the other in `relations.confusable_with`, `relations.specializes` or `discriminators.vs`. Threshold 0.55, set from the corpus (highest undeclared pair scores 0.29) and tunable with `--duplicate-threshold`.
* **DCO check** (`.github/workflows/dco.yml`): every non-merge commit in a pull request must carry a `Signed-off-by` line.
* **Governance gates** (`.github/workflows/gate.yml`): pull requests from outside the contributor list are closed with a pointer to the issue templates; issues that never completed a template are closed after 7 days (the `keep-open` label exempts one). `CODEOWNERS` names the maintainer.
* Zenodo concept DOI 10.5281/zenodo.22416011 in `CITATION.cff`, the README badge and the dataset card (minted on v0.1.1; version DOI 10.5281/zenodo.22416012).

### Fixed

* **The released `[0.1.1]` section said things v0.1.1 did not ship.** The move to the new home had run its find-and-replace through the released sections, making them claim the release mirrored to `open-misconceptions/oml`; `git show v0.1.1:CHANGELOG.md` says `vikram-learnco/oml`. Two bullets describing the `CONTRIBUTING.md` rework and the authoritative reviewer registry were also filed under `[0.1.1]` although both landed after the tag, and have moved to this release. A changelog that edits its own history is worth less than no changelog. The link definitions at the foot are the deliberate exception: they are navigation, so they point at the repository's current home.

## [0.1.1] - 2026-09-05

First release archived by Zenodo; the concept DOI is minted on this tag.

### Changed (record schema 0.2)

* **Review model.** `review` is replaced by `reviews[]` (`kind: human|model|attested`, `by`, `date`, `scope[]`, `verdict`, `notes?`). Status lifecycle is `draft` → `llm-reviewed` → `reviewed` → `deprecated` | `merged`; the validator enforces that `llm-reviewed` has a model accept covering statement and evidence and that `reviewed` has a human accept or an attested review.
* **Computed trust.** New `trust` field (`low|medium|high`) computed by `oml trust` from `reviews[]` against `reviewers/registry.json`; never hand-typed, checked in CI.
* **Framework-agnostic alignments.** `about[]` and `alignments[]` are `{scheme, uri, code?, note?}` with a free-string `scheme`; known schemes are data in `schemes/registry.json` and the validator warns on unknown ones. corestandards.org URLs are labelled `CCSS` across all mathematics records.
* New optional top-level `notes` field for text that is not the belief itself (e.g. likely origins).
* `math.frac.add-across` (record #1, version 1.1.0): statement trimmed to the belief; likely origins moved to `notes`; review closed with Vikram Maram on 2026-09-05 and recorded as `reviews[]` (human accept, model accept, two attested reviews); `status: reviewed`, `trust: high`.
* Every other record gains a changelog entry and a patch version bump for the migration; all remain `draft` with `trust: low`.
* Hugging Face mirror targets the dataset `vikram-learnco/oml`.

### Fixed

* Release workflow was invalid (`secrets` used in a step `if`), so no run had ever executed before v0.1.0 was re-cut. The Hugging Face step now authenticates through the Hub's Trusted Publisher (GitHub OIDC), falls back to `HF_TOKEN` if present, and is skipped otherwise; the workflow can be re-run for an existing tag via `workflow_dispatch`.

## [0.1.0] - 2026-09-05

First citable release.

### Added

* `schema/oml-record.schema.json` v0.1 and `schema/diagnosis-record.schema.json` v0.1 (JSON Schema 2020-12).
* `oml` command-line tooling: `validate`, `index`, `export case|jsonl|csv|all`, `build-site`.
* 58 records: 1 `reviewed` (`math.frac.add-across`) and 57 `draft` across `math.fractions`, `math.decimals` and seven programming areas.
* CASE 1.1 export (`dist/oml.case.json`), JSON Lines and CSV distributions.
* Static site with one page per record at its stable URI.
* Contribution path: CONTRIBUTING.md, PR checklist, issue templates, Contributor Covenant 2.1.

### Decided before release (2026-09-05)

* Relations are a closed set: `conflicts_with`, `resolved_by` (to concepts), `confusable_with` (symmetric), `specializes` (to misconceptions).
* `about[]` entries are `{scheme: CASE|OML, uri}`; CASE preferred.
* The record `id`/`uri` is the canonical ID of the Knowledge Map Misconception node.

### Provisional

* Base URI `https://oml.learnco.io` is a placeholder pending the domain decision.

[0.2.0]: https://github.com/open-misconceptions/miscon-data/releases/tag/v0.2.0
[0.1.1]: https://github.com/open-misconceptions/miscon-data/releases/tag/v0.1.1
[0.1.0]: https://github.com/open-misconceptions/miscon-data/releases/tag/v0.1.0
