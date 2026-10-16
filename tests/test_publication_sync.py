"""Offline guardrails for the scheduled publication synchronization."""
import importlib.util
import pathlib
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location(
    "pubsync", pathlib.Path(__file__).resolve().parents[1] / "scripts" / "sync_publications.py"
)
pub = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pub)


def work(author_id="A5100697597", title="Trusted catalyst research in journals", affiliation=True):
    return {
        "doi": "https://doi.org/10.1234/valid.paper",
        "title": title,
        "publication_year": 2026,
        "authorships": [{
            "author": {"id": "https://openalex.org/" + author_id, "display_name": "Yaqian Li"},
            "institutions": [{"display_name": "China University of Petroleum, East China"}] if affiliation else [],
        }],
    }


def record(title="Trusted catalyst research in journals"):
    return {
        "DOI": "10.1234/valid.paper",
        "type": "journal-article",
        "title": [title],
        "container-title": ["Catalysis Journal"],
        "published": {"date-parts": [[2026, 1, 12]]},
        "author": [
            {"given": "Yaqian", "family": "Li"},
            {"given": "Hao", "family": "Yan"},
            {"given": "Xiang", "family": "Feng"},
        ],
    }


class PublicationSyncTest(unittest.TestCase):
    def setUp(self):
        self.known = {"hao yan", "xiang feng"}

    def test_identity_from_multiple_papers(self):
        self.assertEqual(pub.AUTHOR_ID, "A5100697597")
        self.assertTrue(pub.work_identity(work())[0])
        self.assertFalse(pub.work_identity(work("A0000000000"))[0])
        w = work()
        w["authorships"][0]["author"]["id"] = None
        self.assertFalse(pub.work_identity(w)[0])

    def test_publisher_metadata_and_coauthors(self):
        self.assertIsNone(pub.assess_candidate(work(), record(), self.known))
        self.assertIsNotNone(pub.assess_candidate(work("A0000000000"), record(), self.known))
        bad = record()
        bad["author"][0] = {"given": "Someone", "family": "Else"}
        self.assertIn("Yaqian Li", pub.assess_candidate(work(), bad, self.known))
        bad = record("An entirely unrelated paper about gene editing")
        self.assertIn("title disagreement", pub.assess_candidate(work(), bad, self.known))
        bad = record()
        bad["type"] = "posted-content"
        self.assertIn("journal article", pub.assess_candidate(work(), bad, self.known))

    def test_weak_coauthor_evidence_rejected(self):
        self.assertIn("coauthors", pub.assess_candidate(work(affiliation=False), record(), {"unrelated colleague"}))
        self.assertIsNone(pub.assess_candidate(work(affiliation=True), record(), {"hao yan"}))

    def test_safe_doi_key_and_bibtex(self):
        key, entry = pub.render_bibtex(work(), record(), set())
        self.assertRegex(key, r"^auto2026_[0-9a-f]{12}$")
        self.assertIn("doi = {10.1234/valid.paper}", entry)
        self.assertIn("Li, Yaqian", entry)
        self.assertFalse("selected = {true}" in entry)
        self.assertEqual(pub.doi_clean("HTTPS://DOI.ORG/10.1234/Valid.Paper"), "10.1234/valid.paper")

    def test_existing_bib_preserved(self):
        fixture = "@article{old,\n  author = {Yan, Hao and Li, Yaqian and Feng, Xiang},\n  doi = {10.1234/example},\n}\n"
        self.assertEqual(pub.doi_existing(fixture), {"10.1234/example"})
        self.assertEqual(pub.names_existing(fixture), {"hao yan", "xiang feng"})


if __name__ == "__main__":
    unittest.main()
