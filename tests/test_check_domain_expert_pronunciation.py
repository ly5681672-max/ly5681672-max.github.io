import importlib.util
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('voicecheck',Path(__file__).resolve().parents[1]/'scripts/check_domain_expert_pronunciation.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Tests(unittest.TestCase):
    def test_locale(self):
        self.assertEqual(m.validate([{'id':'lin_dong','pronunciation':{'text':'林栋','locale':'zh-CN','status':'PROVISIONAL'}}]),[])
    def test_wrong_locale(self):
        self.assertTrue(m.validate([{'id':'lin_dong','pronunciation':{'text':'林栋','locale':'en-US','status':'PROVISIONAL'}}]))
    def test_mixed_name(self):
        self.assertTrue(m.validate([{'id':'lin_dong','pronunciation':{'text':'Dong Lin（林栋）','locale':'zh-CN','status':'PROVISIONAL'}}]))
