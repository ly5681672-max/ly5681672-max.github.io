import importlib.util
import unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('live_check',Path(__file__).resolve().parents[1]/'scripts/check_live_domain_experts.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
E=[{'id':'lin_dong','name':'Dong Lin（林栋）'}]
C=[{'expert_id':'lin_dong','title':'Paper title','doi':'10.1000/abc','doi_url':'https://doi.org/10.1000/abc'}]
P='<section id="timeline-lin_dong"><h3>Dong Lin（林栋）</h3><a href="https://doi.org/10.1000/abc">Paper title</a></section><a href="https://doi.org/10.1000/abc">Paper title</a>'
class AcceptanceTests(unittest.TestCase):
    def test_valid(self): self.assertEqual(m.verify(P,E,C,[]),[])
    def test_missing_timeline(self): self.assertTrue(m.verify('<p>empty</p>',E,C,[]))
    def test_missing_paper(self): self.assertTrue(m.verify('<section id="timeline-lin_dong">Dong Lin（林栋）</section>',E,C,[]))
    def test_wrong_identity(self): self.assertTrue(m.verify(P.replace('Dong Lin（林栋）','Other'),E,C,[]))
