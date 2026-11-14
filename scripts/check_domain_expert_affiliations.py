#!/usr/bin/env python3
"""Validate structured bilingual affiliation and research-profile fields."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def validate(people):
    errors=[]
    for p in people:
        pid=p.get('id','unknown')
        for key in ('institution','institution_zh','research_summary','latest_research_note','career_history_note','current_position'):
            if not p.get(key,'').strip(): errors.append(pid+': missing '+key)
        if p.get('current_affiliation_status') not in ('CONFIRMED','PROVISIONAL','UNVERIFIED'):
            errors.append(pid+': missing affiliation evidence status')
        evidence=p.get('profile_evidence') or {}
        if evidence.get('review_status') not in ('CONFIRMED_SOURCE','UNVERIFIED'):
            errors.append(pid+': missing profile evidence status')
        if evidence.get('review_status')=='CONFIRMED_SOURCE':
            if not all(evidence.get(key,'').startswith('https://') for key in ('affiliation_url','career_url','research_url')):
                errors.append(pid+': verified profile lacks field-specific sources')
            if not evidence.get('reviewed_on'):
                errors.append(pid+': missing source review date')
        if p.get('institution_zh') and not any('\u4e00'<=ch<='\u9fff' for ch in p['institution_zh']):
            errors.append(pid+': Chinese institution label has no Chinese characters')
    return errors
if __name__=='__main__':
    people=json.loads((ROOT/'_data/domain_experts.json').read_text(encoding='utf-8'))
    problems=validate(people)
    if problems: raise SystemExit('FAIL: '+'; '.join(problems))
    print('PASS: '+str(len(people))+' bilingual affiliations and structured research profiles; employment and career claims not independently verified')
