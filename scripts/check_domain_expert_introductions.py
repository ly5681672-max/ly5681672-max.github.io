#!/usr/bin/env python3
"""Expert profile completeness checks; not a scientific fact verifier."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def validate(people):
    errors=[]
    ids=set()
    for p in people:
        pid=p.get('id','<missing>')
        if pid in ids: errors.append(pid+': duplicate expert ID')
        ids.add(pid)
        intro=p.get('intro','').strip()
        if len(intro)<75 or len(intro)>350:
            errors.append(pid+': introduction outside 75-350 character range')
        if not p.get('institution') or not p.get('topics'):
            errors.append(pid+': missing institution or research topics')
        if p.get('intro_review_status') not in ('PROVISIONAL','CONFIRMED'):
            errors.append(pid+': missing introduction evidence status')
        url=p.get('intro_source_url','')
        if not url.startswith('https://'):
            errors.append(pid+': missing HTTPS introduction source')
    return errors
if __name__=='__main__':
    data=json.loads((ROOT/'_data/domain_experts.json').read_text(encoding='utf-8'))
    errors=validate(data)
    if errors: raise SystemExit('FAIL: '+'; '.join(errors))
    print('PASS: '+str(len(data))+' expert introductions meet structural requirements; facts remain PROVISIONAL unless verified')
