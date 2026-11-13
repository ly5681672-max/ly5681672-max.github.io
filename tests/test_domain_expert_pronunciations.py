import importlib.util
import pathlib
import unittest
from unittest.mock import patch

path=pathlib.Path(__file__).resolve().parents[1]/"scripts/sync_domain_expert_pronunciations.py"
spec=importlib.util.spec_from_file_location("ipa_sync",path)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class TestIPA(unittest.TestCase):
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
