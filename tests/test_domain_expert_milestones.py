import importlib.util
import pathlib
import unittest
p=pathlib.Path(__file__).resolve().parents[1]/"scripts/verify_domain_expert_milestones.py"
spec=importlib.util.spec_from_file_location("milestone_verify",p)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
class TestMilestones(unittest.TestCase):
    def setUp(self):
        self.c={"doi":"10.1234/example","doi_url":"https://doi.org/10.1234/example","title":"Atomic Design of Catalysts","expert_id":"cao_yueqiang","year":2024}
        self.experts={"cao_yueqiang":{"id":"cao_yueqiang","name":"Yueqiang Cao（曹约强）","orcid":"0000-0002-1036-4049","group":"ai"}}
        self.record={"DOI":"10.1234/example","type":"journal-article","title":["Atomic Design of Catalysts"],"author":[{"given":"Yueqiang","family":"Cao"}],"abstract":"We demonstrate a new method to investigate the catalyst properties through theoretical calculations and experiments. "+"This study provides a careful evaluation of catalyst structures and reaction behavior with systematic measurements and mechanistic evidence."}
    def test_valid_publisher_abstract(self):
        x=mod.verify(self.c,self.experts,self.record)
        self.assertEqual(x["review_status"],"CONFIRMED_ABSTRACT")
    def test_no_abstract_not_promoted(self):
        self.record.pop("abstract")
        self.assertIsNone(mod.verify(self.c,self.experts,self.record))
    def test_wrong_author_not_promoted(self):
        self.record["author"]=[{"family":"Other"}]
        self.assertIsNone(mod.verify(self.c,self.experts,self.record))
    def test_existing_not_overwritten(self):
        old={"url":self.c["doi_url"],"expert_ids":["cao_yueqiang"]}
        additions,errors=mod.build([self.c],[old],self.experts,fetch=lambda _:self.record)
        self.assertEqual((additions,errors),([],[]))
if __name__=="__main__":unittest.main()
