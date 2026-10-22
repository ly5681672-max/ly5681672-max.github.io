"""Regression tests for GitHub-web / VS Code blog post auto headers."""

import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from ensure_post_frontmatter import insert_frontmatter  # noqa: E402


class PostFrontmatterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.post_dir = Path(self.tmp.name) / "_posts"
        self.post_dir.mkdir()
        self.now = datetime(2026, 10, 22, 10, 41, 0, tzinfo=ZoneInfo("Asia/Shanghai"))

    def new_post(self, filename, content=b""):
        path = self.post_dir / filename
        path.write_bytes(content)
        return path

    def test_empty_post_created_on_github_receives_header(self):
        path = self.new_post("2026-10-22-catmap-06-knowledge-points.md")
        self.assertTrue(insert_frontmatter(path, self.now))
        self.assertEqual(
            path.read_text(),
            '---\nlayout: post\ntitle: "2026-10-22-catmap-06-knowledge-points"\n'
            "date: 2026-10-22 10:41:00 +0800\n---\n",
        )

    def test_existing_article_body_is_byte_for_byte_preserved(self):
        body = "正文包含公式：\n\\frac{1}{x}\nhttps://example.org\n".encode("utf-8")
        path = self.new_post("2026-10-22-科研笔记.md", body)
        self.assertTrue(insert_frontmatter(path, self.now))
        self.assertTrue(path.read_bytes().endswith(body))
        self.assertIn('title: "2026-10-22-科研笔记"', path.read_text(encoding="utf-8"))

    def test_existing_frontmatter_is_not_modified_or_duplicated(self):
        original = b'---\nlayout: post\ntitle: "Custom"\n---\n\nOriginal content\n'
        path = self.new_post("2026-10-22-custom.md", original)
        self.assertFalse(insert_frontmatter(path, self.now))
        self.assertEqual(path.read_bytes(), original)

    def test_idempotent_on_repeated_github_commits(self):
        path = self.new_post("2026-10-22-repeat.md")
        self.assertTrue(insert_frontmatter(path, self.now))
        first = path.read_bytes()
        self.assertFalse(insert_frontmatter(path, self.now))
        self.assertEqual(first, path.read_bytes())

    def test_old_dated_post_uses_its_filename_date(self):
        path = self.new_post("2026-10-18-notes.md")
        self.assertTrue(insert_frontmatter(path, self.now))
        self.assertIn("date: 2026-10-18 10:00:00 +0800", path.read_text())

    def test_preserve_crlf_content(self):
        body = b"First\r\nSecond\r\n"
        path = self.new_post("2026-10-22-crlf.md", body)
        self.assertTrue(insert_frontmatter(path, self.now))
        self.assertTrue(path.read_bytes().endswith(body))
        self.assertIn(b"---\r\nlayout: post\r\n", path.read_bytes())

    def test_malformed_frontmatter_fails_without_destroying_original(self):
        source = b"---\ntitle: broken without closing fence\n"
        path = self.new_post("2026-10-22-broken.md", source)
        # Existing frontmatter has its own integrity checks; never overwrite it.
        self.assertFalse(insert_frontmatter(path, self.now))
        self.assertEqual(source, path.read_bytes())

    def test_ambiguous_horizontal_rule_fails_safely(self):
        source = b"---not-actual-frontmatter\nScience\n"
        path = self.new_post("2026-10-22-ambiguous.md", source)
        with self.assertRaises(ValueError):
            insert_frontmatter(path, self.now)
        self.assertEqual(source, path.read_bytes())

    def test_unrelated_markdown_is_not_changed(self):
        path = self.new_post("README.md", b"Hello\n")
        self.assertFalse(insert_frontmatter(path, self.now))
        self.assertEqual(b"Hello\n", path.read_bytes())


if __name__ == "__main__":
    unittest.main()
