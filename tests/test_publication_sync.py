"""Offline guardrails for the scheduled publication synchronization."""
import datetime as dt
import importlib.util
import pathlib
import tempfile
import unittest
from unittest import mock

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
        self.assertFalse(pub.work_identity(work("A0000000000", affiliation=False))[0])
        self.assertTrue(pub.work_identity(work("A0000000000", affiliation=True))[0])
        w = work()
        w["authorships"][0]["author"]["id"] = None
        self.assertTrue(pub.work_identity(w)[0])  # Explicit home institution still corroborates.
        w["authorships"][0]["institutions"] = []
        self.assertFalse(pub.work_identity(w)[0])

    def test_publisher_metadata_and_coauthors(self):
        self.assertIsNone(pub.assess_candidate(work(), record(), self.known))
        self.assertIsNotNone(pub.assess_candidate(work("A0000000000", affiliation=False), record(), self.known))
        self.assertIsNone(pub.assess_candidate(work("A0000000000", affiliation=True), record(), self.known))
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

    def test_news_requires_verified_full_recent_online_date(self):
        recent = dt.date.today() - dt.timedelta(days=4)
        meta = record()
        meta["published-online"] = {"date-parts": [[recent.year, recent.month, recent.day]]}
        self.assertEqual(pub.verified_news_date(meta), recent)
        meta["published-online"] = {"date-parts": [[recent.year]]}
        self.assertIsNone(pub.verified_news_date(meta))
        meta["published-online"] = {"date-parts": [[2018, 1, 1]]}
        self.assertIsNone(pub.verified_news_date(meta))
        meta["published-online"] = {"date-parts": [[2032, 1, 1]]}
        self.assertIsNone(pub.verified_news_date(meta))

    def test_news_written_only_once_for_approved_paper(self):
        today = dt.date.today()
        paper = {
            "key": "auto_new_doi", "doi": "10.1234/valid.paper",
            "title": "Trusted catalyst research", "journal": "Catalysis Journal",
            "news_date": today,
        }
        with tempfile.TemporaryDirectory() as root:
            with mock.patch.object(pub, "NEWS_DIR", pathlib.Path(root)):
                written = pub.write_verified_news([paper])
                self.assertEqual(len(written), 1)
                body = pathlib.Path(written[0]).read_text(encoding="utf-8")
                self.assertIn("10.1234/valid.paper", body)
                self.assertIn("date: " + today.isoformat(), body)
                self.assertEqual(pub.write_verified_news([paper]), [])
                self.assertEqual(pub.write_verified_news([{**paper, "news_date": None}]), [])

    def test_existing_bib_preserved(self):
        fixture = "@article{old,\n  author = {Yan, Hao and Li, Yaqian and Feng, Xiang},\n  doi = {10.1234/example},\n}\n"
        self.assertEqual(pub.doi_existing(fixture), {"10.1234/example"})
        self.assertEqual(pub.names_existing(fixture), {"hao yan", "xiang feng"})


    def test_apply_is_append_only_and_idempotent(self):
        initial = ""
        for i in range(23):
            initial += (
                f"@article{{existing{i},\n"
                "  author = {Yan, Hao and Feng, Xiang and Li, Yaqian},\n"
                f"  doi = {{10.1234/seed{i}}},\n"
                "}\n\n"
            )
        with tempfile.TemporaryDirectory() as root:
            folder = pathlib.Path(root)
            bib = folder / "papers.bib"
            stats = folder / "stats.yml"
            news = folder / "_news"
            report_path = folder / "report.json"
            bib.write_text(initial, encoding="utf-8")
            with (
                mock.patch.object(pub, "BIB", bib),
                mock.patch.object(pub, "STATS", stats),
                mock.patch.object(pub, "NEWS_DIR", news),
                mock.patch.object(pub, "REPORT", report_path),
                mock.patch.object(pub, "openalex_works", return_value=[work()]),
                mock.patch.object(pub, "crossref_recent", return_value={}),
                mock.patch.object(pub, "get_json", return_value={"message": record()}),
            ):
                first = pub.sync(apply=True)
                self.assertEqual(len(first["approved"]), 1)
                self.assertTrue(bib.read_text(encoding="utf-8").startswith(initial))
                self.assertIn("journal_count: 24", stats.read_text(encoding="utf-8"))
                second = pub.sync(apply=True)
                self.assertEqual(len(second["approved"]), 0)
                self.assertEqual(bib.read_text(encoding="utf-8").count("doi = {10.1234/valid.paper}"), 1)


if __name__ == "__main__":
    unittest.main()
