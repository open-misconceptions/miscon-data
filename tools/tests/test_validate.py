"""Tests for `miscon validate`. Run from the repo root: python -m unittest discover -s tools/tests"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from miscon.config import Config, find_repo_root
from miscon.validate import validate_records

HERE = Path(__file__).resolve().parent
FIXTURES = HERE / "fixtures"
ROOT = find_repo_root(HERE)


def fixture_config(records_dir: Path) -> Config:
    """A Config whose records/ points at a fixture corpus but shares the real schema."""
    cfg = Config.load(ROOT)
    cfg.root = records_dir.parent
    cfg.schema_root = ROOT / "schema"
    for name in ("reviewers", "schemes"):
        dst = records_dir.parent / name / "registry.json"
        dst.parent.mkdir(exist_ok=True)
        src = ROOT / name / "registry.json"
        if not dst.exists() or dst.read_text() != src.read_text():
            dst.write_text(src.read_text())
    return cfg


class GoodFixtures(unittest.TestCase):
    def test_good_records_pass(self):
        records = FIXTURES / "good" / "records"
        report = validate_records(records, fixture_config(records))
        self.assertEqual(report.errors, [], "\n".join(map(str, report.errors)))
        self.assertEqual(report.checked, 2)


class BrokenFixtures(unittest.TestCase):
    def setUp(self):
        self.records = FIXTURES / "broken" / "records"
        # Resolve relations against the good corpus so the only failures are the intended ones.
        self.config = fixture_config(FIXTURES / "good" / "records")
        self.report = validate_records(self.records, self.config, all_records_dir=FIXTURES / "good" / "records")
        self.by_file = {}
        for p in self.report.problems:
            self.by_file.setdefault(p.path.name, []).append(p.message)

    def assertProblem(self, filename: str, needle: str):
        msgs = self.by_file.get(filename, [])
        self.assertTrue(any(needle in m for m in msgs), f"{filename}: expected {needle!r} in {msgs}")

    def test_every_broken_fixture_fails(self):
        for path in sorted(self.records.rglob("*.json")):
            self.assertIn(path.name, self.by_file, f"{path.name} should have produced an error")
        self.assertFalse(self.report.ok)

    def test_id_mismatch(self):
        self.assertProblem("fractions.id-mismatch.json", "does not match path")

    def test_bad_uri(self):
        self.assertProblem("fractions.bad-uri.json", "uri must be")

    def test_duplicate_uuid(self):
        self.assertProblem("fractions.dup-uuid.json", "already used by")

    def test_dangling_relation(self):
        self.assertProblem("fractions.dangling.json", "is not a record in the repo")

    def test_reviewed_without_review(self):
        self.assertProblem("fractions.no-review.json", "review")

    def test_reviewed_with_model_only(self):
        self.assertProblem("fractions.model-only.json", "human review")

    def test_hand_typed_trust(self):
        self.assertProblem("fractions.hand-trust.json", "trust must be")

    def test_human_review_needs_handle(self):
        self.assertProblem("fractions.no-handle.json", "durable handle")

    def test_unregistered_reviewer_cannot_accept(self):
        self.assertProblem("fractions.unregistered-reviewer.json", "not in reviewers/registry.json")

    def test_disputed_needs_a_linked_dispute(self):
        self.assertProblem("fractions.disputed-no-link.json", "disputes")

    def test_merged_without_target(self):
        self.assertProblem("fractions.bad-merge.json", "merged_into")

    def test_no_example_and_bad_kind(self):
        self.assertProblem("fractions.no-example.json", "example")
        self.assertProblem("fractions.no-example.json", "kind")

    def test_invalid_json(self):
        self.assertProblem("fractions.not-json.json", "invalid JSON")


class CliExitCodes(unittest.TestCase):
    def run_cli(self, *args, cwd: Path, env: dict | None = None):
        env = {**os.environ, **(env or {})}
        return subprocess.run(
            [sys.executable, "-m", "miscon", *args], cwd=cwd, env=env, capture_output=True, text=True
        )

    def test_real_records_pass(self):
        proc = self.run_cli("validate", "records/", "--strict", cwd=ROOT)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("records checked / 0 errors", proc.stdout)

    def test_broken_fixture_exits_nonzero(self):
        proc = self.run_cli(
            "validate", "records/", cwd=FIXTURES / "broken", env={"MISCON_SCHEMA_DIR": str(ROOT / "schema")}
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("errors", proc.stdout)


class DiagnosisSchema(unittest.TestCase):
    def test_example_diagnosis_validates(self):
        from miscon.validate import load_schema

        validator = load_schema(Config.load(ROOT), "diagnosis-record.schema.json")
        doc = {
            "item": "1/2 + 1/3",
            "expected": "5/6",
            "response": "2/5",
            "diagnoses": [{"miscon_id": "math.fractions.add-across", "confidence": 0.9, "matched_pattern": 0}],
            "miscon_version": "0.1.0",
            "engine_version": "example/0.0.1",
        }
        self.assertEqual(list(validator.iter_errors(doc)), [])
        doc["diagnoses"][0]["confidence"] = 1.5
        self.assertTrue(list(validator.iter_errors(doc)))


if __name__ == "__main__":
    unittest.main()


class SymmetricRelations(unittest.TestCase):
    def test_missing_reverse_confusable_with_warns(self):
        import copy
        import tempfile

        good = FIXTURES / "good" / "records" / "math"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "records" / "math").mkdir(parents=True)
            (root / "miscon.config.json").write_text((ROOT / "miscon.config.json").read_text())
            a = json.loads((good / "fractions.add-across.json").read_text())
            b = json.loads((good / "fractions.add-numerators-keep-denominator.json").read_text())
            b = copy.deepcopy(b)
            b["relations"].pop("confusable_with", None)
            (root / "reviewers").mkdir()
            (root / "reviewers" / "registry.json").write_text((ROOT / "reviewers" / "registry.json").read_text())
            (root / "schemes").mkdir()
            (root / "schemes" / "registry.json").write_text((ROOT / "schemes" / "registry.json").read_text())
            (root / "records" / "math" / "fractions.add-across.json").write_text(json.dumps(a))
            (root / "records" / "math" / "fractions.add-numerators-keep-denominator.json").write_text(json.dumps(b))
            cfg = fixture_config(root / "records")
            report = validate_records(root / "records", cfg)
            self.assertTrue(report.ok, [str(p) for p in report.errors])
            self.assertTrue(any("symmetric" in w.message for w in report.warnings), [str(w) for w in report.warnings])


class TrustComputation(unittest.TestCase):
    def test_record_one_is_high_and_drafts_are_low(self):
        from miscon.trust import compute_trust, load_reviewers

        reg = load_reviewers(Config.load(ROOT))
        one = json.loads((ROOT / "records" / "math" / "fractions.add-across.json").read_text())
        self.assertEqual(compute_trust(one, reg), "high")
        stub = json.loads((ROOT / "records" / "math" / "fractions.add-numerators-keep-denominator.json").read_text())
        self.assertEqual(compute_trust(stub, reg), "low")

    def test_trust_check_is_clean(self):
        proc = subprocess.run([sys.executable, "-m", "miscon", "trust", "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)


class DuplicateDetection(unittest.TestCase):
    """The duplicate check must fire on a restatement and stay quiet otherwise."""

    def setUp(self):
        self.records = [json.loads(f.read_text()) for f in sorted((ROOT / "records").rglob("*.json"))]
        self.original = next(r for r in self.records if r["id"] == "math.fractions.add-across")

    def _twin(self, **overrides):
        import copy

        twin = copy.deepcopy(self.original)
        twin["id"] = "math.fractions.add-tops-and-bottoms"
        twin["statement"] = "Fractions are added by adding the numerators together and adding the denominators."
        twin["relations"] = {}
        twin["discriminators"] = {"vs_slip": "unchanged"}
        twin.update(overrides)
        return twin

    def test_live_corpus_is_clean(self):
        from miscon.duplicates import find_duplicates

        self.assertEqual(find_duplicates(self.records), [])

    def test_restatement_is_reported(self):
        from miscon.duplicates import find_duplicates

        pairs = find_duplicates(self.records + [self._twin()])
        self.assertEqual([(p.left, p.right) for p in pairs], [("math.fractions.add-across", "math.fractions.add-tops-and-bottoms")])

    def test_declared_neighbour_is_not_reported(self):
        from miscon.duplicates import find_duplicates

        twin = self._twin(relations={"confusable_with": ["math.fractions.add-across"]})
        self.assertEqual(find_duplicates(self.records + [twin]), [])

    def test_discriminator_also_counts_as_declaring(self):
        from miscon.duplicates import find_duplicates

        twin = self._twin(discriminators={"vs_slip": "x", "vs": {"math.fractions.add-across": "differs by ..."}})
        self.assertEqual(find_duplicates(self.records + [twin]), [])

    def test_other_domains_are_not_compared(self):
        from miscon.duplicates import find_duplicates

        twin = self._twin(id="programming.fractions.add-tops-and-bottoms")
        self.assertEqual(find_duplicates(self.records + [twin]), [])

    def test_threshold_has_headroom_over_the_live_corpus(self):
        """No real pair sits near the threshold, so the check has room to tighten."""
        from miscon.duplicates import DEFAULT_THRESHOLD, declared_neighbours, similarity

        worst = 0.0
        for i, left in enumerate(self.records):
            for right in self.records[i + 1 :]:
                if left["id"].split(".")[0] != right["id"].split(".")[0]:
                    continue
                if right["id"] in declared_neighbours(left) or left["id"] in declared_neighbours(right):
                    continue
                worst = max(worst, similarity(left["statement"], right["statement"]))
        self.assertLess(worst, DEFAULT_THRESHOLD - 0.2, f"closest undeclared pair scores {worst:.2f}")


class RebaseUri(unittest.TestCase):
    """A base-URI move rewrites the public ID of every record, so it must be total.

    These run against a throwaway copy of the repo: the operation edits records
    in place, and a half-applied rewrite is exactly the failure being guarded
    against.
    """

    def setUp(self):
        import shutil
        import tempfile

        self.tmp = tempfile.mkdtemp()
        self.root = Path(self.tmp) / "repo"
        self.root.mkdir()
        for name in ("miscon.config.json", "records", "schema", "schemes", "reviewers"):
            src = ROOT / name
            dst = self.root / name
            if src.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy(src, dst)
        self.config = Config.load(self.root)

    def tearDown(self):
        import shutil

        shutil.rmtree(self.tmp, ignore_errors=True)

    def _read(self, rel):
        return json.loads((self.root / rel).read_text())

    def test_rewrites_every_kind_of_reference(self):
        from miscon.rebase import rebase

        new = "https://openmisconceptions.example"
        report = rebase(self.config, new)
        self.assertGreater(report.occurrences, 100, "expected a corpus-wide rewrite")

        record = self._read("records/math/fractions.add-across.json")
        self.assertTrue(record["uri"].startswith(new), "record uri not rewritten")
        self.assertEqual(self._read("miscon.config.json")["base_uri"], new)
        self.assertTrue(self._read("schema/miscon-record.schema.json")["$id"].startswith(new))

        # Concept URIs live in about[] and in relations.*[].external.
        prog = self._read("records/programming/variables.assignment-is-equation.json")
        self.assertTrue(prog["about"][0]["uri"].startswith(new))
        self.assertTrue(prog["relations"]["conflicts_with"][0]["external"].startswith(new))

    def test_scheme_registry_regex_is_rewritten(self):
        """Regression: the Miscon pattern stores the host regex-escaped.

        Plain text substitution misses the escaped form, leaving the Miscon
        scheme matching the old host. That surfaced as a warning on every
        record carrying a Miscon concept URI, which blocks CI under --strict.
        """
        from miscon.rebase import rebase

        new = "https://openmisconceptions.example"
        rebase(self.config, new)
        pattern = next(
            s["uri_pattern"] for s in self._read("schemes/registry.json")["schemes"] if s["name"] == "Miscon"
        )
        self.assertIn("openmisconceptions", pattern)
        self.assertNotIn("github.io", pattern)

        # And the rewritten pattern must actually match the rewritten URIs.
        import re

        concept = self._read("records/programming/variables.assignment-is-equation.json")["about"][0]["uri"]
        self.assertRegex(concept, pattern)

    def test_rebased_corpus_validates_with_no_warnings(self):
        from miscon.rebase import rebase

        rebase(self.config, "https://openmisconceptions.example")
        config = Config.load(self.root)
        config.schema_root = self.root / "schema"
        report = validate_records(config.records_dir, config)
        self.assertEqual(report.errors, [], "\n".join(map(str, report.errors)))
        self.assertEqual(report.warnings, [], "\n".join(map(str, report.warnings)))

    def test_round_trip_leaves_no_residue(self):
        from miscon.rebase import rebase

        original_base = self.config.base_uri
        before = {p: p.read_text() for p in sorted(self.root.rglob("*.json"))}
        rebase(self.config, "https://openmisconceptions.example")
        rebase(Config.load(self.root), original_base)
        after = {p: p.read_text() for p in sorted(self.root.rglob("*.json"))}
        changed = [str(p.relative_to(self.root)) for p in before if before[p] != after.get(p)]
        self.assertEqual(changed, [], f"round trip left residue in {changed}")

    def test_rebasing_to_the_same_base_is_a_no_op(self):
        from miscon.rebase import rebase

        report = rebase(self.config, self.config.base_uri)
        self.assertEqual(report.changed, [])


class BaseUriWithPath(unittest.TestCase):
    """A GitHub Pages project site is <owner>.github.io/<repo>, so the base URI
    carries a path. The record `uri` pattern originally assumed a bare domain
    and rejected every record the moment the library moved to a Pages URL."""

    def test_uri_pattern_accepts_a_base_with_a_path(self):
        import re

        schema = json.loads((ROOT / "schema" / "miscon-record.schema.json").read_text())
        pattern = schema["properties"]["uri"]["pattern"]
        for uri in (
            "https://open-misconceptions.github.io/miscon-data/m/math.fractions.add-across",
            "https://miscon.example.org/m/math.fractions.add-across",
            "https://example.org/a/deeper/path/m/programming.variables.assignment-is-equation",
        ):
            self.assertRegex(uri, pattern, f"{uri} should be a valid record URI")

    def test_uri_pattern_still_rejects_malformed_ids(self):
        import re

        schema = json.loads((ROOT / "schema" / "miscon-record.schema.json").read_text())
        pattern = schema["properties"]["uri"]["pattern"]
        for uri in (
            "https://example.org/m/NoCaps",
            "https://example.org/m/nodot",
            "https://example.org/math.fractions.add-across",
        ):
            self.assertIsNone(re.match(pattern, uri), f"{uri} should not be a valid record URI")

    def test_a_pages_style_base_validates_end_to_end(self):
        """The whole corpus must validate, not just the pattern in isolation."""
        import shutil
        import tempfile

        from miscon.rebase import rebase

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            for name in ("miscon.config.json", "records", "schema", "schemes", "reviewers"):
                src = ROOT / name
                dst = root / name
                shutil.copytree(src, dst) if src.is_dir() else shutil.copy(src, dst)
            rebase(Config.load(root), "https://open-misconceptions.github.io/miscon-data")
            config = Config.load(root)
            report = validate_records(config.records_dir, config)
            self.assertEqual(report.errors, [], "\n".join(map(str, report.errors)))
            self.assertEqual(report.warnings, [], "\n".join(map(str, report.warnings)))


class LicenceIsConfigDriven(unittest.TestCase):
    def test_case_export_licence_matches_the_configured_licence(self):
        """The CASE export hardcoded a CC BY title, so a relicensed library
        exported a document naming the wrong licence beside a correct URL."""
        from miscon.export import build_case, load_all

        config = Config.load(ROOT)
        pkg = build_case(config, load_all(config))
        licence = pkg["CFDefinitions"]["CFLicenses"][0]
        self.assertEqual(licence["title"], config.license_name)
        self.assertIn(config.license, licence["licenseText"])
        self.assertEqual(licence["description"], config.license_uri)

    def test_every_record_carries_the_configured_licence(self):
        config = Config.load(ROOT)
        for path in sorted((ROOT / "records").rglob("*.json")):
            record = json.loads(path.read_text())
            self.assertEqual(record["license"], config.license, f"{path.name} has a stale licence")


class ReviewerAliases(unittest.TestCase):
    """A reviewer's durable handle can change. Reviews filed under the old one
    must keep counting, or promoting a handle silently demotes every record
    that reviewer had accepted."""

    def test_alias_carries_its_owners_weight(self):
        from miscon.trust import reviewer_weights

        registry = {
            "reviewers": [
                {"id": "orcid:0000-0000-0000-0000", "weight": 1.0, "aliases": ["github:old-handle"]},
                {"id": "attested", "weight": 0.6},
            ]
        }
        weights = reviewer_weights(registry)
        self.assertEqual(weights["orcid:0000-0000-0000-0000"], 1.0)
        self.assertEqual(weights["github:old-handle"], 1.0)

    def test_record_one_stays_high_under_the_orcid(self):
        """Record #1's human review is filed under github:vikram-learnco; the
        registry's primary id is now the ORCID. Trust must not move."""
        from miscon.trust import compute_trust, load_reviewers

        registry = load_reviewers(Config.load(ROOT))
        primary = {r["id"] for r in registry["reviewers"]}
        self.assertIn("orcid:0009-0002-9041-8322", primary)
        self.assertNotIn("github:vikram-learnco", primary)

        one = json.loads((ROOT / "records" / "math" / "fractions.add-across.json").read_text())
        self.assertTrue(any("github:vikram-learnco" in str(r.get("by")) for r in one["reviews"]))
        self.assertEqual(compute_trust(one, registry), "high")

    def test_a_review_under_an_alias_is_not_an_unregistered_reviewer(self):
        config = Config.load(ROOT)
        report = validate_records(config.records_dir, config)
        self.assertEqual(
            [str(p) for p in report.problems if "reviewers/registry.json" in p.message], []
        )


class MissingPrerequisiteIsGone(unittest.TestCase):
    """A missing prerequisite is a gap, not a belief: it is out of scope for a
    library of misconceptions, so it is not a `kind`."""

    def test_the_kind_is_not_in_the_schema(self):
        schema = json.loads((ROOT / "schema" / "miscon-record.schema.json").read_text())
        self.assertNotIn("missing-prerequisite", schema["properties"]["kind"]["enum"])

    def test_no_record_and_no_issue_template_still_offers_it(self):
        for path in sorted((ROOT / "records").rglob("*.json")):
            self.assertNotIn("missing-prerequisite", json.loads(path.read_text())["kind"])
        template = (ROOT / ".github" / "ISSUE_TEMPLATE" / "new-misconception.yml").read_text()
        self.assertNotIn("missing-prerequisite", template)


class TheNameIsRetired(unittest.TestCase):
    """The rename is only done if nothing still says the old name. The two
    permitted hits are the released CHANGELOG sections, which are history, and
    the github: reviewer alias, which is a real handle."""

    def test_no_stale_name_outside_released_history(self):
        import re

        # word-bounded so that "pyproject.toml" is not a hit
        retired = "".join(("o", "m", "l"))
        stale = re.compile(rf"\b{retired}\b|" + "".join(("learn", "co")), re.IGNORECASE)
        offenders = []
        for path in sorted(ROOT.rglob("*")):
            if not path.is_file() or path.suffix not in {".py", ".json", ".md", ".yml", ".yaml", ".cff", ".toml"}:
                continue
            if any(part in {".git", "__pycache__", "_build"} or part.endswith(".egg-info") for part in path.parts):
                continue
            text = path.read_text(encoding="utf-8")
            if path.name == "CHANGELOG.md":
                text, _, _ = text.partition("\n## [0.1.1]")
            for i, line in enumerate(text.splitlines(), 1):
                if "vikram-learnco" in line:  # the reviewer alias, a real handle
                    continue
                if "formerly" in line:  # the one line that may name the retired acronym
                    continue
                if stale.search(line):
                    offenders.append(f"{path.relative_to(ROOT)}:{i}: {line.strip()}")
        self.assertEqual(offenders, [])
