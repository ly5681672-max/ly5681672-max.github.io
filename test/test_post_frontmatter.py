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
            '---\nlayout: post\ntitle: "catmap-06-knowledge-points"\n'
            "date: 2026-10-22 10:41:00 +0800\n---\n",
        )

    def test_existing_article_body_is_byte_for_byte_preserved(self):
        body = "正文包含公式：\n\\frac{1}{x}\nhttps://example.org\n".encode("utf-8")
        path = self.new_post("2026-10-22-科研笔记.md", body)
        self.assertTrue(insert_frontmatter(path, self.now))
        self.assertTrue(path.read_bytes().endswith(body))
        self.assertIn('title: "科研笔记"', path.read_text(encoding="utf-8"))

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
        self.assertIn('title: "notes"', path.read_text())
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

    def test_any_markdown_directly_inside_posts_is_processed(self):
        path = self.new_post("README.md", b"Hello\n")
        self.assertTrue(insert_frontmatter(path, self.now))
        self.assertTrue(path.read_text(encoding="utf-8").startswith("---\nlayout: post\n"))
        self.assertTrue(path.read_bytes().endswith(b"Hello\n"))


    def test_undated_chinese_filename_receives_current_beijing_header(self):
        path = self.new_post("OOH吸附能分析.md")
        self.assertTrue(insert_frontmatter(path, self.now))
        self.assertEqual(
            path.read_text(encoding="utf-8"),
            '---\nlayout: post\ntitle: "OOH吸附能分析"\n'
            "date: 2026-10-22 10:41:00 +0800\n---\n",
        )

    def test_arbitrary_filename_preserves_existing_body(self):
        body = "已有正文\\n第二行\\n".encode("utf-8")
        path = self.new_post("任意名称测试.md", body)
        self.assertTrue(insert_frontmatter(path, self.now))
        result = path.read_bytes()
        self.assertTrue(result.endswith(body))
        self.assertIn('title: "任意名称测试"', result.decode("utf-8"))

    def test_existing_frontmatter_on_undated_filename_is_preserved(self):
        original = b'---\nlayout: post\ntitle: "Existing"\n---\nBody\n'
        path = self.new_post("existing-note.md", original)
        self.assertFalse(insert_frontmatter(path, self.now))
        self.assertEqual(path.read_bytes(), original)

    def test_non_markdown_file_is_ignored(self):
        path = self.new_post("not-a-post.txt", b"keep me\n")
        self.assertFalse(insert_frontmatter(path, self.now))
        self.assertEqual(path.read_bytes(), b"keep me\n")


    def test_leading_space_in_filename_is_removed_and_title_is_clean(self):
        path = self.new_post(" 2016-11-14-林栋师兄讨论catmap.md", b"原始正文\\n")
        self.assertTrue(insert_frontmatter(path, self.now))
        normalized = self.post_dir / "2016-11-14-林栋师兄讨论catmap.md"
        self.assertTrue(normalized.exists())
        self.assertFalse(path.exists())
        result = normalized.read_text(encoding="utf-8")
        self.assertIn('title: "林栋师兄讨论catmap"', result)
        self.assertIn("date: 2016-11-14 10:00:00 +0800", result)
        self.assertTrue(result.endswith("原始正文\\n"))

    def test_trailing_filename_spaces_are_removed(self):
        path = self.new_post("OOH吸附能分析.md  ", b"正文\\n")
        self.assertTrue(insert_frontmatter(path, self.now))
        normalized = self.post_dir / "OOH吸附能分析.md"
        self.assertTrue(normalized.exists())
        self.assertFalse(path.exists())
        self.assertIn('title: "OOH吸附能分析"', normalized.read_text(encoding="utf-8"))

    def test_filename_normalization_collision_does_not_overwrite(self):
        source = self.new_post(" OOH吸附能分析.md", b"原文件正文\\n")
        target = self.new_post("OOH吸附能分析.md", b"目标文件正文\\n")
        with self.assertRaises(FileExistsError):
            insert_frontmatter(source, self.now)
        self.assertEqual(source.read_bytes(), b"原文件正文\\n")
        self.assertEqual(target.read_bytes(), b"目标文件正文\\n")


if __name__ == "__main__":
    unittest.main()
