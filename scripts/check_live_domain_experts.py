#!/usr/bin/env python3
"""Fail closed unless the deployed public expert page matches repository data."""
import argparse
import html
from html.parser import HTMLParser
import json
from pathlib import Path
import time
from urllib.request import Request, urlopen

ROOT=Path(__file__).resolve().parents[1]
class TimelineHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active=None; self.depth=0; self.text={}; self.links={}; self.page_text=[]; self.page_links=set(); self.short_buttons={} ; self.full_buttons={}
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag=='section' and a.get('id','').startswith('timeline-'):
            self.active=a['id'][9:]; self.depth=1; self.text[self.active]=[]; self.links[self.active]=set()
        elif self.active is not None and tag=='section':
            self.depth+=1
        if tag=='button' and a.get('data-pronounce-id'):
            pid=a['data-pronounce-id']
            bucket=self.short_buttons if a.get('data-pronounce-short')=='true' else self.full_buttons
            bucket[pid]=bucket.get(pid,0)+1
        if tag=='a' and a.get('href'):
            url=html.unescape(a['href']); self.page_links.add(url)
            if self.active is not None: self.links[self.active].add(url)
    def handle_endtag(self,tag):
        if tag=='section' and self.active is not None:
            self.depth-=1
            if not self.depth: self.active=None
    def handle_data(self,data):
        self.page_text.append(data)
        if self.active is not None: self.text[self.active].append(data)
def norm(value):
    return ' '.join(html.unescape(value).split())
def verify(page,experts,candidates,milestones):
    doc=TimelineHTML(); doc.feed(page)
    all_text=norm(' '.join(doc.page_text)); errors=[]
    for person in experts:
        pid=person['id']; section=norm(' '.join(doc.text.get(pid,[])))
        if not section:
            errors.append(f'{pid}: missing or empty timeline'); continue
        if person.get('preferred_address'):
            label=person['preferred_address']['label']
            if norm(label) not in section: errors.append(f'{pid}: missing recommended address on public timeline')
            if not doc.short_buttons.get(pid): errors.append(f'{pid}: missing short pronunciation button')
            if not doc.full_buttons.get(pid): errors.append(f'{pid}: missing full pronunciation button')
        if norm(person['name']) not in section:
            errors.append(f'{pid}: incorrect timeline name')
        confirmed=[m for m in milestones if pid in m.get('expert_ids',[])]
        provisional=[c for c in candidates if c.get('expert_id')==pid]
        expected=confirmed if confirmed else provisional[:3]
        for item in expected:
            url=item.get('url') or item.get('doi_url')
            if norm(item['title']) not in section or (url and url not in doc.links[pid]):
                errors.append(f'{pid}: timeline missing {item.get("doi",item["title"])}')
        if not expected and '暂无可展示的候选记录' not in section:
            errors.append(f'{pid}: missing explicit empty-state notice')
        for item in provisional:
            if norm(item['title']) not in all_text or item['doi_url'] not in doc.page_links:
                errors.append(f'{pid}: candidate database missing {item["doi"]}')
    return errors
def main():
    p=argparse.ArgumentParser()
    p.add_argument('--url',default='https://ly5681672-max.github.io/domain-experts/')
    p.add_argument('--root',type=Path,default=ROOT)
    p.add_argument('--attempts',type=int,default=12)
    p.add_argument('--interval',type=int,default=15)
    a=p.parse_args()
    experts=json.loads((a.root/'_data/domain_experts.json').read_text(encoding='utf-8'))
    candidates=json.loads((a.root/'_data/domain_expert_milestone_candidates.json').read_text(encoding='utf-8'))['candidates']
    milestones=json.loads((a.root/'_data/domain_expert_milestones.json').read_text(encoding='utf-8'))
    from check_domain_expert_pronunciation import validate
    speech_errors=validate(experts)
    if speech_errors: raise SystemExit('FAIL pronunciation configuration: '+'; '.join(speech_errors))
    for n in range(1,a.attempts+1):
        try:
            url=a.url+('&' if '?' in a.url else '?')+f'acceptance={int(time.time())}'
            with urlopen(Request(url,headers={'Cache-Control':'no-cache','User-Agent':'expert-site-acceptance/1.0'}),timeout=25) as response:
                if response.status!=200: raise ValueError(f'HTTP {response.status}')
                page=response.read().decode('utf-8')
            errors=verify(page,experts,candidates,milestones)
        except Exception as exc:
            errors=[f'HTTP retrieval failed: {type(exc).__name__}: {exc}']
        if not errors:
            print(f'PASS PUBLIC: {len(experts)} experts and {len(candidates)} candidates (attempt {n})')
            return 0
        print(f'Attempt {n}/{a.attempts}: '+'; '.join(errors[:12]),flush=True)
        if n<a.attempts: time.sleep(a.interval)
    raise SystemExit('FAIL PUBLIC ACCEPTANCE: '+'; '.join(errors))
if __name__=='__main__': main()
