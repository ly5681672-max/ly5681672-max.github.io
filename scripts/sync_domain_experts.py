#!/usr/bin/env python3
"""Verified bibliographic metadata synchronizer for curated domain experts.

Writes only _data/domain_expert_updates.json on --apply.
Expert identities are checked through ORCID -> OpenAlex ID -> work authorships.
Keyword relevance is provisional and must not be mistaken for full-text review.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timedelta, timezone
import json
import os
from pathlib import Path
import re
import sys
import time
import unicodedata
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
API = 'https://api.openalex.org'
AI_TERMS = {
    '知识图谱': ('knowledge graph', 'knowledge graphs'),
    '文献数据': ('literature mining', 'data extraction', 'scientific literature', 'text mining'),
    'RAG/LLM': ('large language model', 'language models', 'retrieval augmented', 'llm', 'foundation model', 'agentic'),
    '机器学习': ('machine learning', 'deep learning', 'artificial intelligence', 'neural network', 'active learning', 'graph neural'),
    '微观动力学': ('microkinetic', 'reaction kinetics', 'kinetic modeling'),
    '催化描述符': ('catalytic descriptor', 'catalysis descriptor', 'adsorption energy', 'bep relation'),
}
EPOX_TERMS = {
    '烯烃环氧化': ('epoxidation', 'epoxide', 'propylene oxide', 'hexene oxide', 'olefin oxidation'),
    'TS-1': ('ts-1', 'titanium silicalite', 'titano-silicalite', 'titanosilicate', 'ti-mfi'),
    'H₂O₂/OOH': ('hydrogen peroxide', 'h2o2', 'hydroperox', 'ooh'),
    '分子筛': ('zeolite', 'mfi', 'microporous'),
    '选择性氧化': ('selective oxidation', 'oxidation catalyst', 'oxidation reaction'),
}
# Editorial shortlist, not a claim of current JCR quartile or SCI indexing.
# Journal names must be checked against publisher/Clarivate sources before calling them SCI.
PRIORITY_JOURNALS = {
    'nature catalysis', 'nature chemistry', 'nature chemical engineering',
    'nature communications', 'science', 'science advances',
    'journal of the american chemical society', 'angewandte chemie international edition',
    'acs catalysis', 'chemical science', 'chem', 'chemical engineering journal',
    'applied catalysis b: environment and energy', 'applied catalysis b: environmental',
    'journal of catalysis', 'energy & environmental science',
    'advanced materials', 'advanced science', 'chemistry of materials',
}
DOI_PATTERN = re.compile(r'^10\.\d{4,9}/\S+$', re.I)


def fetch_json(path: str, params: dict, timeout: int = 20) -> dict:
    url = f'{API}/{path}?{urlencode(params)}'
    headers = {'User-Agent': 'academic-domain-experts/0.2 (verified bibliography monitor)'}
    key = os.environ.get('OPENALEX_API_KEY')
    if key:
        url += '&' + urlencode({'api_key': key})
    req = Request(url, headers=headers)
    last = None
    for attempt in range(3):
        try:
            with urlopen(req, timeout=timeout) as resp:
                data = json.load(resp)
            if not isinstance(data, dict):
                raise ValueError('OpenAlex response is not an object')
            return data
        except Exception as exc:
            last = exc
            if attempt < 2:
                time.sleep(2 ** attempt)
    if isinstance(last, HTTPError):
        # Preserve the HTTP cause without exposing the optional API key or full URL.
        try:
            detail = last.read().decode('utf-8', errors='replace')[:280]
        except Exception:
            detail = ''
        if key:
            detail = detail.replace(key, '[REDACTED]')
        raise RuntimeError(f'OpenAlex query failed for {path}: HTTP {last.code}; {detail}') from last
    raise RuntimeError(f'OpenAlex query failed for {path}: {type(last).__name__}') from last


def normalize_doi(value) -> str | None:
    if not value:
        return None
    doi = str(value).strip()
    doi = re.sub(r'^https?://(?:dx\.)?doi\.org/', '', doi, flags=re.I)
    return doi.lower() if DOI_PATTERN.fullmatch(doi) else None


def fold_name(value: str) -> str:
    return ''.join(c for c in unicodedata.normalize('NFKD', value.casefold()) if not unicodedata.combining(c))


def get_author_id(expert: dict) -> str | None:
    if not expert.get('orcid'):
        return None
    orcid = expert['orcid']
    res = fetch_json('authors', {'filter': f'orcid:{orcid}', 'per_page': 5, 'select': 'id,display_name,orcid,observed_orcids,works_count'})
    matches = [row for row in res.get('results', [])
               if any(str(o).rstrip('/').endswith(orcid)
                      for o in ([row.get('orcid')] + (row.get('observed_orcids') or [])) if o)]
    preferred = expert.get('openalex_author_id')
    if preferred:
        # Explicitly curated after reviewing duplicate ORCID candidates.
        # Still require the ORCID to match; an arbitrary ID cannot bypass identity validation.
        matches = [row for row in matches
                   if str(row.get('id', '')).rsplit('/', 1)[-1] == preferred]
    else:
        primary = [row for row in matches if str(row.get('orcid', '')).rstrip('/').endswith(orcid)]
        if len(primary) == 1:
            matches = primary
    if len(matches) != 1:
        candidates = [(row.get('id', '').rsplit('/', 1)[-1],
                       row.get('display_name'), row.get('works_count'))
                      for row in matches]
        raise ValueError(f'Author identity not unique for {expert["id"]}: {candidates}')
    surname = fold_name(re.split(r'[（(]', expert['name'], maxsplit=1)[0].strip().split()[-1])
    if surname not in fold_name(str(matches[0].get('display_name', ''))):
        raise ValueError(f'Author display name mismatch for {expert["id"]}')
    return str(matches[0]['id']).rsplit('/', 1)[-1]


def reconstruct_abstract(inverted) -> str:
    if not isinstance(inverted, dict):
        return ''
    positions = [(idx, word) for word, indexes in inverted.items()
                 for idx in indexes if isinstance(idx, int) and 0 <= idx < 5000]
    return ' '.join(word for _, word in sorted(positions))


def match_relevance(title: str, abstract: str, group: str):
    low_title = title.casefold()
    full = (title + ' ' + abstract).casefold()
    terms = AI_TERMS if group == 'ai' else EPOX_TERMS
    tags = [label for label, words in terms.items() if any(w in full for w in words)]
    if not tags:
        return None
    if group == 'ai':
        chemistry = any(w in full for w in ('cataly', 'chemistr', 'material', 'reaction', 'molecul', 'zeolit', 'atomic', 'atomistic', 'dft'))
        if not chemistry:
            return None
        high = ('知识图谱' in tags or '文献数据' in tags or '微观动力学' in tags
                or any(w in low_title for w in ('cataly', 'microkinetic', 'knowledge graph')))
    else:
        high = any(x in tags for x in ('烯烃环氧化', 'TS-1', 'H₂O₂/OOH'))
    return {'tags': tags, 'relevance': '高' if high else '中'}


def gather(experts: list, days: int, date_now: datetime):
    since = (date_now.date() - timedelta(days=days)).isoformat()
    all_papers = {}
    report = {'processed': [], 'skipped_no_orcid': [], 'errors': []}
    for person in experts:
        if not person.get('orcid'):
            report['skipped_no_orcid'].append(person['name'])
            continue
        try:
            aid = get_author_id(person)
            params = {'filter': f'authorships.author.id:{aid},from_publication_date:{since}',
                      'per_page': 100, 'sort': 'publication_date:desc',
                      'select': 'id,title,publication_date,doi,authorships,abstract_inverted_index,type,primary_location'}
            result = fetch_json('works', params)
            count = 0
            for row in result.get('results', []):
                doi = normalize_doi(row.get('doi'))
                if not doi or row.get('type') not in ('article', 'review', 'preprint'):
                    continue
                if not any(str(a.get('author', {}).get('id', '')).rsplit('/', 1)[-1] == aid
                           for a in row.get('authorships', [])):
                    continue
                title = row.get('title') or ''
                if not title:
                    continue
                found = match_relevance(title, reconstruct_abstract(row.get('abstract_inverted_index')), person['group'])
                if not found:
                    continue
                date = row.get('publication_date') or ''
                if not re.fullmatch(r'\d{4}-\d{2}-\d{2}', date):
                    continue
                source = (row.get('primary_location') or {}).get('source') or {}
                journal = (source.get('display_name') or '').strip()
                priority = journal.casefold() in PRIORITY_JOURNALS
                # Preprints are tracked separately, never labelled as top-journal SCI.
                if row.get('type') == 'preprint':
                    priority = False
                paper = all_papers.setdefault(doi, {
                    'title': title, 'doi': doi, 'doi_url': 'https://doi.org/' + doi,
                    'source_url': row.get('id'), 'publication_date': date,
                    'journal': journal or '期刊待核验', 'priority_journal': priority,
                    'publication_type': row.get('type'),
                    'group': person['group'],
                    'group_label': 'AI 结合知识学习' if person['group'] == 'ai' else '烯烃环氧化',
                    'relevance': found['relevance'], 'match_tags': [], 'author_names': []
                })
                if person['name'] not in paper['author_names']:
                    paper['author_names'].append(person['name'])
                for tag in found['tags']:
                    if tag not in paper['match_tags']:
                        paper['match_tags'].append(tag)
                if found['relevance'] == '高':
                    paper['relevance'] = '高'
                count += 1
            report['processed'].append({'expert': person['name'], 'matched_papers': count, 'author_id': aid})
        except Exception as exc:
            root_error = exc.__cause__ if exc.__cause__ is not None else exc
            safe_detail = (str(exc)[:350] if hasattr(root_error, 'code')
                           else str(exc) if isinstance(exc, ValueError)
                           else type(root_error).__name__)
            report['errors'].append({'expert': person['name'],
                                     'error': type(exc).__name__,
                                     'detail': safe_detail})
    papers = sorted(all_papers.values(), key=lambda p: (p['publication_date'], p['doi']), reverse=True)
    payload = {'generated_at': date_now.isoformat(timespec='seconds'), 'window_days': days,
               'papers': papers[:250],
               'journal_policy': '优先期刊为人工维护的期刊名单，非SCI/JCR自动认证',
               'status': '基于书目和摘要的规则相关性；关键发现尚未完成原文核验。'}
    return payload, report


def main():
    ap = argparse.ArgumentParser()
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run', action='store_true')
    mode.add_argument('--apply', action='store_true')
    ap.add_argument('--days', type=int, default=180)
    args = ap.parse_args()
    if not (1 <= args.days <= 3650):
        ap.error('--days must be 1..3650')
    roster = json.loads((ROOT / '_data/domain_experts.json').read_text(encoding='utf-8'))
    result, report = gather(roster, args.days, datetime.now(timezone.utc))
    report_payload = {'source': 'OpenAlex', 'count': len(result['papers']), **report}
    print(json.dumps(report_payload, ensure_ascii=False, indent=2))
    (ROOT / 'domain-experts-report.json').write_text(
        json.dumps({'report': report_payload, 'candidate_data': result}, ensure_ascii=False, indent=2) + '\n',
        encoding='utf-8'
    )
    if report['errors'] or not report['processed']:
        print('FAIL CLOSED: identity/API failure; previous website data retained.', file=sys.stderr)
        return 1
    if args.apply:
        (ROOT / '_data/domain_expert_updates.json').write_text(
            json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
        )
        print('Updated _data/domain_expert_updates.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())
