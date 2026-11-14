import importlib.util
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('affiliation_check',Path(__file__).resolve().parents[1]/'scripts/check_domain_expert_affiliations.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Tests(unittest.TestCase):
    def profile(self):
        return dict(id='x',institution='Virginia Tech',institution_zh='弗吉尼亚理工大学',
                    research_summary='催化研究',latest_research_note='近期研究有来源',
                    career_history_note='官方履历',current_position='教授',
                    current_affiliation_status='CONFIRMED',
                    profile_evidence=dict(review_status='CONFIRMED_SOURCE',reviewed_on='2026-11-14',
                        affiliation_url='https://example.edu/people',
                        career_url='https://example.edu/cv',
                        research_url='https://example.edu/research'))
    def test_valid(self): self.assertEqual(m.validate([self.profile()]),[])
    def test_missing_chinese(self):
        p=self.profile();p['institution_zh']='Virginia Tech';self.assertTrue(m.validate([p]))
    def test_missing_history(self):
        p=self.profile();p['career_history_note']='';self.assertTrue(m.validate([p]))
    def test_missing_research_source(self):
        p=self.profile();p['profile_evidence']['research_url']=''
        self.assertTrue(m.validate([p]))
    def test_missing_current_position(self):
        p=self.profile();p['current_position']=''
        self.assertTrue(m.validate([p]))
