#!/usr/bin/env python3
"""Fail deployment if Jekyll omitted any expert or their candidate timeline."""
import argparse
import html
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def check(site):
    page=site/"domain-experts"/"index.html"
    if not page.is_file():
        raise AssertionError(f"Built expert page missing: {page}")
    content=html.unescape(page.read_text(encoding="utf-8"))
    experts=json.loads((ROOT/"_data/domain_experts.json").read_text(encoding="utf-8"))
    candidates=json.loads((ROOT/"_data/domain_expert_milestone_candidates.json").read_text(encoding="utf-8"))["candidates"]
    milestones=json.loads((ROOT/"_data/domain_expert_milestones.json").read_text(encoding="utf-8"))
    for person in experts:
        pid=person["id"]
        if f'id="timeline-{pid}"' not in content:
            raise AssertionError(f"Expert timeline missing: {pid}")
        verified=[m for m in milestones if pid in m.get("expert_ids",[])]
        provisional=[c for c in candidates if c.get("expert_id")==pid]
        if verified:
            for item in verified:
                if item["title"] not in content:
                    raise AssertionError(f"Formal milestone missing: {pid}: {item['title']}")
        elif provisional:
            for item in provisional[:3]:
                if item["title"] not in content:
                    raise AssertionError(f"Fallback candidate missing: {pid}: {item['title']}")
        for item in provisional:
            if item["title"] not in content:
                raise AssertionError(f"Candidate research entry missing: {pid}: {item['title']}")
        print(f"PASS {pid}: formal={len(verified)}, candidates={len(provisional)}")
    print("PASS: built expert page matches repository metadata; live HTTP not checked")

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--site",type=Path,required=True)
    check(p.parse_args().site)
