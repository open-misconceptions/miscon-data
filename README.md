# Open Misconceptions

[![validate](https://github.com/open-misconceptions/miscon-data/actions/workflows/validate.yml/badge.svg)](https://github.com/open-misconceptions/miscon-data/actions/workflows/validate.yml)
[![data: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-lightgrey.svg)](LICENSE-DATA)
[![code: MIT](https://img.shields.io/badge/code-MIT-lightgrey.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22416011.svg)](https://doi.org/10.5281/zenodo.22416011)
[![Hugging Face dataset](https://img.shields.io/badge/dataset-open--misconceptions%2Fmiscon--data-yellow.svg)](https://huggingface.co/datasets/open-misconceptions/miscon-data)

Open Misconceptions is a public catalogue of misconceptions with stable IDs. A misconception
is a false but stable belief that produces predictable wrong answers, such as
"to add fractions you add the numerators and add the denominators". Each
record states the belief, names its kind, gives the evidence pattern that
distinguishes it from a slip or a neighbouring misconception, and records
where the claim comes from. Because the IDs are stable and public, any
learning platform, item bank, or research group can say *why* a learner got
something wrong in a shared vocabulary, and two systems that have never met
can agree they are talking about the same error.

## How to cite a record

Every record has a short ID and a stable URI. Cite either.

| Form  | Example                                              |
|-------|------------------------------------------------------|
| ID    | `miscon:math.fractions.add-across`                           |
| URI   | `https://open-misconceptions.github.io/miscon-data/m/math.fractions.add-across`      |
| JSON  | `https://open-misconceptions.github.io/miscon-data/m/math.fractions.add-across.json` |

IDs are lowercase, dot-separated, and never reused. A record may be
`deprecated` or `merged` into another, but its ID and URI keep resolving
and point you to the successor. Each record also carries a UUID for systems
that prefer opaque identifiers.

To cite the library as a whole, use the concept DOI
[10.5281/zenodo.22416011](https://doi.org/10.5281/zenodo.22416011), which always resolves to
the latest release; each release also has its own version DOI (v0.1.1:
[10.5281/zenodo.22416012](https://doi.org/10.5281/zenodo.22416012)). Author and title
metadata are in [`CITATION.cff`](CITATION.cff). The whole library is also
mirrored as the Hugging Face dataset
[`open-misconceptions/miscon-data`](https://huggingface.co/datasets/open-misconceptions/miscon-data).

## How to consume

* **One record as JSON.** `records/<domain>/<rest-of-id>.json` in this repo,
  or `<URI>.json` on the site. Records conform to
  [`schema/miscon-record.schema.json`](schema/miscon-record.schema.json).
* **The whole library as JSON Lines or CSV.** `dist/miscon.jsonl` and
  `dist/miscon.csv`, attached to every release.
* **As a CASE framework.** `dist/miscon.case.json` is a
  [1EdTech CASE 1.1](https://www.imsglobal.org/spec/case/v1p1) document with
  one `CFItem` per misconception, so it imports into any CASE consumer
  alongside your standards frameworks.
* **Diagnoses.** If your system emits a diagnosis that cites an Open Misconceptions record,
  [`schema/diagnosis-record.schema.json`](schema/diagnosis-record.schema.json)
  is the interchange shape.

Regenerate the distribution files locally with:

```sh
pip install -e tools/miscon
miscon validate records/
miscon export all
miscon build-site
```

The tooling is Python (3.10 or newer) with `jsonschema` as its only
dependency.

## Record status

| Status       | Meaning                                                            |
|--------------|--------------------------------------------------------------------|
| `draft`      | Proposed; has evidence and provenance but no human review yet.     |
| `reviewed`   | A maintainer has checked the statement, kind, evidence and sources. |
| `deprecated` | No longer recommended; the record says why.                        |
| `merged`     | Folded into another record; `history.merged_into` names it.        |

Most records in an early release are `draft`. Treat `draft` as "someone
thought this was worth writing down", not as a settled claim.

## How to contribute

**Propose a misconception by opening an issue**, not a pull request. You get
a structured response without waiting for a maintainer, and three accepted
proposals earns the right to open pull requests directly.

* [CONTRIBUTING.md](CONTRIBUTING.md) — what a good proposal contains, and
  what `reviewed` means.
* [GOVERNANCE.md](GOVERNANCE.md) — who may make which change, how disputes
  are settled, and why a `miscon:` ID is never deleted.

## How to cite

Cite the release you actually used, and the concept DOI so the reference
survives later versions:

> Maram, Vikram, and contributors. *Open Misconceptions*, version
> 0.1.1. Zenodo, 2026. <https://doi.org/10.5281/zenodo.22416011>

The concept DOI [10.5281/zenodo.22416011](https://doi.org/10.5281/zenodo.22416011)
always resolves to the latest release; each release also has its own
version DOI. Machine-readable author and title metadata are in
[`CITATION.cff`](CITATION.cff), which GitHub renders as "Cite this
repository".

When you cite a single record, cite its ID and URI as well as the release
— `miscon:math.fractions.add-across`, at
`https://open-misconceptions.github.io/miscon-data/m/math.fractions.add-across` — so a
reader can tell which version of that record you meant.

## Licence

Code under `tools/` and `site/` is [MIT](LICENSE). Everything under
`records/`, `schema/` and `dist/` is
[CC BY 4.0](LICENSE-DATA). Cite the library when you redistribute the data.

CC BY obliges attribution on **redistribution**, not on use. Reading the
records, ingesting them, and storing a `miscon:` ID in your own database
oblige you to nothing. Bundling the dataset into something you ship, or
publishing a dataset derived from it, means naming where it came from.
That is the norm for shared vocabularies of this kind — the Gene Ontology
is CC BY 4.0 on the same reasoning — and it is what
[OBO Foundry principle 1](https://obofoundry.org/principles/fp-001-open.html)
asks of an open ontology.
