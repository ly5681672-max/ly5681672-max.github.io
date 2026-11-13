#!/usr/bin/env python3
"""Discover historical milestone CANDIDATES, never assert verified discoveries.

Uses existing ORCID->OpenAlex identity verification and a year-spanning
citation-ranked shortlist. Outputs independent JSON; does not edit curated
scientific milestones or original research data.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from sync_domain_experts import ROOT, fetch_json, get_author_id, normalize_doi, reconstruct_abstract, match_relevance

OUTPUT = ROOT / '_data/domain_expert_milestone_candidates.json'

def select_candidates(works, expert, limit=8):
    selected = []
    seen = set()
    for row in works:
        doi = normalize_doi(row.get('doi'))
        title = (row.get('title') or '').strip()
        if not doi or doi in seen or not title or row.get('type') not in ('article','review'):
            continue
        if row.get('is_retracted') is True:
            continue
        abstract = reconstruct_abstract(row.get('abstract_inverted_index'))
        relevance = match_relevance(title, abstract, expert['group'])
        if not relevance:
            continue
        source = ((row.get('primary_location') or {}).get('source') or {})
        selected.append({
            'expert_id': expert['id'], 'expert_name': expert['name'],
            'year': row.get('publication_year'),
            'title': title, 'doi': doi, 'doi_url': 'https://doi.org/' + doi,
            'source_url': row.get('id'), 'journal': source.get('display_name') or '期刊待核验',
            'cited_by_count': max(0, int(row.get('cited_by_count') or 0)),
            'relevance_tags': relevance['tags'],
            'abstract_excerpt': abstract[:900] if abstract else '',
            'review_status': 'PROVISIONAL',
            'review_note': '书目与摘要候选；引用数不是科学贡献证明，关键发现及作者贡献须原文核验。',
        })
        seen.add(doi)
    # Limit temporal clustering: allow up to two candidates per publication year.
    chosen = []
    by_year = {}
    for item in sorted(selected, key=lambda x:(x['cited_by_count'],x['year'] or 0), reverse=True):
        year = item['year']
        if by_year.get(year,0) >= 2:
            continue
        chosen.append(item)
        by_year[year] = by_year.get(year,0)+1
        if len(chosen)>=limit:
            break
    return sorted(chosen,key=lambda x:(x['year'] or 0,x['cited_by_count']),reverse=True)

def gather(experts):
    records = []
    report = {'processed':[], 'skipped_no_orcid':[], 'errors':[]}
    for expert in experts:
        if not expert.get('orcid'):
            report['skipped_no_orcid'].append(expert['name'])
            continue
        try:
            aid = get_author_id(expert)
            params = {
                'filter':f'authorships.author.id:{aid}',
                'sort':'cited_by_count:desc', 'per_page':200,
                'select':'id,title,doi,publication_year,type,is_retracted,cited_by_count,authorships,primary_location,abstract_inverted_index',
            }
            rows = fetch_json('works',params).get('results',[])
            # Verify authorship in each work rather than trusting only the filter.
            rows = [r for r in rows if any(
                str(a.get('author',{}).get('id','')).rsplit('/',1)[-1]==aid
                for a in r.get('authorships',[]))]
            items = select_candidates(rows,expert)
            records.extend(items)
            report['processed'].append({'expert':expert['name'],'author_id':aid,'candidates':len(items)})
        except Exception as exc:
            report['errors'].append({'expert':expert['name'],'error':type(exc).__name__})
    return {'generated_at':datetime.now(timezone.utc).isoformat(timespec='seconds'),
            'source':'OpenAlex','selection':'历史高引用+主题规则初筛；非科学里程碑认证',
            'candidates':records},report

def main():
    parser=argparse.ArgumentParser()
    mode=parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run',action='store_true')
    mode.add_argument('--apply',action='store_true')
    args=parser.parse_args()
    experts=json.loads((ROOT/'_data/domain_experts.json').read_text(encoding='utf-8'))
    data,report=gather(experts)
    print(json.dumps(report,ensure_ascii=False,indent=2))
    (ROOT/'domain-expert-milestone-candidates-report.json').write_text(
        json.dumps({'report':report,'data':data},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if report['errors'] or not report['processed']:
        raise SystemExit('FAIL CLOSED: identity/API failure; no milestone candidate publication.')
    if args.apply:
        OUTPUT.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return 0

if __name__=='__main__':
    raise SystemExit(main())
