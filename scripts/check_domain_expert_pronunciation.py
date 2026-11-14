#!/usr/bin/env python3
"""Validate explicit per-expert speech locale and safe text (not audio fidelity)."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ALLOWED={'zh-CN','ja-JP','en-GB','en-US','es-ES','fr-FR','nl-NL','de-DE'}
def validate(people):
    problems=[]
    for p in people:
        a=p.get('preferred_address') or {}
        c=p.get('pronunciation') or {}
        if not a.get('label') or not a.get('spoken_short_name') or a.get('locale')!=c.get('locale'):
            problems.append(p['id']+': invalid recommended address or short-name locale')
        if a.get('status') not in ('PROVISIONAL','CONFIRMED'):
            problems.append(p['id']+': missing address evidence status')
        if any(x in a.get('spoken_short_name','') for x in ('（','）','(',')')):
            problems.append(p['id']+': mixed short-name text')
        if not c.get('text') or c.get('locale') not in ALLOWED:
            problems.append(p['id']+': missing/unsupported pronunciation locale')
        if c.get('status') not in ('PROVISIONAL','CONFIRMED'):
            problems.append(p['id']+': missing pronunciation evidence status')
        if '（' in c.get('text','') or '）' in c.get('text',''):
            problems.append(p['id']+': bilingual TTS text')
        if p['id'] in ('feng_xiang','lin_dong','cao_yueqiang','xin') and c.get('locale')!='zh-CN':
            problems.append(p['id']+': Mandarin expected')
        if p['id']=='takigawa_ichigaku' and c.get('locale')!='ja-JP':
            problems.append(p['id']+': Japanese expected')
        if p['id']=='hutchings' and c.get('locale')!='en-GB':
            problems.append(p['id']+': British English expected')
    return problems
if __name__=='__main__':
    data=json.loads((ROOT/'_data/domain_experts.json').read_text(encoding='utf-8'))
    errors=validate(data)
    if errors: raise SystemExit('FAIL: '+'; '.join(errors))
    print('PASS: explicit speech configuration for',len(data),'experts; actual audio accuracy not verified')
