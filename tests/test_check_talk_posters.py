"""Regression tests for poster records and their PDF assets."""

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from check_talk_posters import validate  # noqa: E402


class PosterIntegrityTests(unittest.TestCase):
    def setUp(self):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.root = Path(folder.name)
        (self.root / "_talks").mkdir()
        (self.root / "assets/pdf/talks").mkdir(parents=True)

    def record(self, href="/assets/pdf/talks/poster.pdf"):
        (self.root / "_talks/poster.md").write_text(
            '---\ntitle: "真实墙报"\ndate: 2026-11-18\ncategory: poster\n'
            'venue: "会议名称待核实"\nmaterials:\n  - label: "PDF"\n'
            f'    url: "{href}"\n    type: slides\n---\n',
            encoding="utf-8",
        )

    def test_existing_pdf_with_record(self):
        self.record()
        (self.root / "assets/pdf/talks/poster.pdf").write_bytes(b"%PDF-example")
        self.assertEqual(validate(self.root), [])

    def test_missing_pdf(self):
        self.record()
        self.assertTrue(any("missing or empty" in x for x in validate(self.root)))

    def test_orphan_pdf(self):
        (self.root / "assets/pdf/talks/poster.pdf").write_bytes(b"%PDF-example")
        self.assertTrue(any("unreferenced" in x for x in validate(self.root)))

    def test_wrong_pdf_directory(self):
        (self.root / "_talks/wrong.pdf").write_bytes(b"%PDF-example")
        self.assertTrue(any("not _talks/" in x for x in validate(self.root)))


if __name__ == "__main__":
    unittest.main()
