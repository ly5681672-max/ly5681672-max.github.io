import sys
from pathlib import Path
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import discover_domain_expert_milestones as module

class MilestoneDiscoveryTests(unittest.TestCase):
    def test_no_doi_no_candidate(self):
        self.assertEqual(module.select_candidates([{'title':'catalysis machine learning','doi':None,'type':'article'}],{'id':'x','name':'X','group':'ai'}),[])
    def test_year_diversity_and_status(self):
        rows=[]
        for i in range(5):
            rows.append({'title':'Machine learning for catalysis '+str(i),'doi':f'10.1234/abc{i}',
                         'type':'article','publication_year':2020,'cited_by_count':100-i,
                         'primary_location':{'source':{'display_name':'ACS Catalysis'}}})
        result=module.select_candidates(rows,{'id':'x','name':'X','group':'ai'})
        self.assertEqual(len(result),2)
        self.assertTrue(all(x['review_status']=='PROVISIONAL' for x in result))
    def test_retracted_excluded(self):
        rows=[{'title':'Machine learning for catalysis','doi':'10.1234/retracted','type':'article',
               'is_retracted':True,'publication_year':2020,'cited_by_count':999}]
        self.assertEqual(module.select_candidates(rows,{'id':'x','name':'X','group':'ai'}),[])

if __name__=='__main__':
    unittest.main()
