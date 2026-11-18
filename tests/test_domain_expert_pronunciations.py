import importlib.util
import pathlib
import unittest
import io
import json
import tempfile
from contextlib import redirect_stdout
from urllib.error import HTTPError
from unittest.mock import patch

path=pathlib.Path(__file__).resolve().parents[1]/"scripts/sync_domain_expert_pronunciations.py"
spec=importlib.util.spec_from_file_location("ipa_sync",path)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestIPA(unittest.TestCase):
    def test_rate_limit_skips_optional_enrichment_without_data_loss(self):
        records = [
            {"id": "first", "orcid": "0000-0000-0000-0001", "pronunciation_ipa": ""},
            {"id": "second", "orcid": "0000-0000-0000-0002", "pronunciation_ipa": ""},
        ]
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / "experts.json"
            original = json.dumps(records, ensure_ascii=False)
            path.write_text(original, encoding="utf-8")
            with patch.object(mod, "DATA", path), patch.object(
                mod, "matched_ipa", side_effect=HTTPError("https://www.wikidata.org", 429, "rate limited", {}, None)
            ) as mocked, patch("sys.argv", ["ipa_sync", "--apply"]):
                output = io.StringIO()
                with redirect_stdout(output):
                    mod.main()
            self.assertEqual(mocked.call_count, 1)
            self.assertEqual(path.read_text(encoding="utf-8"), original)
            self.assertIn("HTTP 429", output.getvalue())

    def test_non_rate_limit_http_errors_remain_failures(self):
        records = [{"id": "first", "orcid": "0000-0000-0000-0001", "pronunciation_ipa": ""}]
        with tempfile.TemporaryDirectory() as folder:
            path = pathlib.Path(folder) / "experts.json"
            path.write_text(json.dumps(records), encoding="utf-8")
            with patch.object(mod, "DATA", path), patch.object(
                mod, "matched_ipa", side_effect=HTTPError("https://www.wikidata.org", 403, "forbidden", {}, None)
            ), patch("sys.argv", ["ipa_sync", "--apply"]):
                with self.assertRaises(HTTPError):
                    mod.main()

    def test_no_orcid(self):
        self.assertIsNone(mod.matched_ipa("unknown"))
    def test_verified_unique(self):
        search={"query":{"search":[{"title":"Q123"}]}}
        entities={"entities":{"Q123":{"claims":{"P496":[{"mainsnak":{"datavalue":{"value":"0000-0000-0000-0001"}}}],"P898":[{"mainsnak":{"datavalue":{"value":"/abc/"}}}]}}}}
        with patch.object(mod,"get_json",side_effect=[search,entities]):
            self.assertEqual(mod.matched_ipa("0000-0000-0000-0001"),("Q123","/abc/"))
    def test_wrong_orcid(self):
        search={"query":{"search":[{"title":"Q123"}]}}
        entities={"entities":{"Q123":{"claims":{"P496":[{"mainsnak":{"datavalue":{"value":"0000-0000-0000-0002"}}}],"P898":[{"mainsnak":{"datavalue":{"value":"/abc/"}}}]}}}}
        with patch.object(mod,"get_json",side_effect=[search,entities]):
            self.assertIsNone(mod.matched_ipa("0000-0000-0000-0001"))
    def test_ambiguous_ipa(self):
        search={"query":{"search":[{"title":"Q123"}]}}
        entities={"entities":{"Q123":{"claims":{"P496":[{"mainsnak":{"datavalue":{"value":"0000-0000-0000-0001"}}}],"P898":[{"mainsnak":{"datavalue":{"value":"/abc/"}}},{"mainsnak":{"datavalue":{"value":"/def/"}}}]}}}}
        with patch.object(mod,"get_json",side_effect=[search,entities]):
            self.assertIsNone(mod.matched_ipa("0000-0000-0000-0001"))
if __name__=="__main__":unittest.main()
