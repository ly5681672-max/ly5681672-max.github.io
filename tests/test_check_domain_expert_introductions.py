import importlib.util
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('intro_check',Path(__file__).resolve().parents[1]/'scripts/check_domain_expert_introductions.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
def item(text='研究催化材料的结构与性能关系，结合计算化学与数据分析研究催化反应中的活性位及其变化规律，并分析反应条件对催化过程的影响。'):
    return {'id':'test','intro':text,'institution':'Research Institute','topics':['催化'],'intro_review_status':'PROVISIONAL','intro_source_url':'https://example.org/profile'}
class IntroductionTests(unittest.TestCase):
    def test_valid(self): self.assertEqual(m.validate([item()]),[])
    def test_too_short(self): self.assertTrue(m.validate([item('研究催化')]))
    def test_missing_source(self):
        p=item();p['intro_source_url']='';self.assertTrue(m.validate([p]))
    def test_missing_status(self):
        p=item();p.pop('intro_review_status');self.assertTrue(m.validate([p]))
