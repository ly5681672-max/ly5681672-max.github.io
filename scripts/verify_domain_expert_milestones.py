#!/usr/bin/env python3
"""Promote historical candidates only with publisher-deposited Crossref abstracts.

CONFIRMED_ABSTRACT means metadata/abstract evidence verified, not scientific
independent replication. Never overwrite curated milestones or auto-promote
from OpenAlex abstracts alone.
"""
import argparse
import html
import json
import re
import time
from urllib.error import HTTPError
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "_data/domain_expert_milestone_candidates.json"
MILESTONES = ROOT / "_data/domain_expert_milestones.json"
EVIDENCE = re.compile(r"\b(we (?:report|demonstrate|show|develop|present|find|design|propose)|our (?:results|study|work) (?:show|demonstrate)|this (?:work|study) (?:shows|demonstrates|reports|presents))\b", re.I)

def clean(value):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]*>", " ", value or ""))).strip()

def crossref(doi):
    req = Request("https://api.crossref.org/works/" + quote(doi, safe="/"), headers={"User-Agent":"academic-expert-milestone-sync/1.0 (research verification)"})
    for attempt in range(4):
        try:
            with urlopen(req, timeout=20) as res:
                return json.load(res)["message"]
        except HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 3:
                raise
            time.sleep(min(12, 2 ** attempt + 1))
    raise RuntimeError("unreachable")

def normalize(value):
    return re.sub(r"[^a-z0-9]", "", (value or "").casefold())

def verify(candidate, experts, record):
    doi = candidate["doi"]
    if (record.get("DOI") or "").lower() != doi.lower():
        return None
    if record.get("type") not in ("journal-article", "journal-review"):
        return None
    titles = record.get("title") or []
    if not titles or normalize(clean(titles[0])) != normalize(candidate["title"]):
        return None
    expert = experts.get(candidate["expert_id"])
    if not expert or not expert.get("orcid"):
        return None
    surname = expert["name"].split("（")[0].split("(")[0].split()[-1]
    authors = record.get("author") or []
    if not any(normalize(a.get("family")) == normalize(surname) for a in authors):
        return None
    abstract = clean(record.get("abstract"))
    if len(abstract) < 180:
        return None
    sentences = re.split(r"(?<=[.!?])\s+", abstract)
    claim = next((s for s in sentences if EVIDENCE.search(s) and 30 <= len(s) <= 550), None)
    if not claim:
        return None
    # Short direct excerpt only; no invented Chinese scientific interpretation.
    excerpt = " ".join(claim.split()[:18])
    return {
        "year":str(candidate["year"]), "group":expert["group"], "type":"研究成果·出版商摘要核验",
        "title":candidate["title"], "authors":", ".join(" ".join(filter(None,[a.get("given"),a.get("family")])) for a in authors[:12]),
        "evidence":"出版商登记摘要中的研究贡献原文片段（不等于全文核验）：“"+excerpt+"…”；具体结论请核对原文。",
        "url":candidate["doi_url"], "publisher_source":record.get("URL") or candidate["doi_url"],
        "expert_ids":[candidate["expert_id"]], "review_status":"CONFIRMED_ABSTRACT",
        "review_note":"自动核验Crossref出版商登记的DOI、题名、作者姓氏及摘要；只确认摘要原文存在，不代表全文审核或独立复现。",
        "verification_source":"Crossref publisher-deposited abstract", "verification_doi":doi,
        "verification_method":"automated_abstract_only"
    }

def build(candidates, existing, experts, fetch=crossref):
    known = {(x.get("url","").lower(),i) for x in existing for i in x.get("expert_ids",[])}
    additions = []
    errors = []
    for c in candidates:
        key = (c.get("doi_url","").lower(),c.get("expert_id"))
        if key in known or not c.get("doi"):
            continue
        try:
            item = verify(c, experts, fetch(c["doi"]))
            if item:
                additions.append(item)
                known.add(key)
        except Exception as exc:
            errors.append({"doi":c["doi"],"error":type(exc).__name__,"http_status":getattr(exc,"code",None)})
    return additions, errors

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--apply",action="store_true")
    args=ap.parse_args()
    candidates=json.loads(CANDIDATES.read_text(encoding="utf-8"))["candidates"]
    existing=json.loads(MILESTONES.read_text(encoding="utf-8"))
    experts={p["id"]:p for p in json.loads((ROOT/"_data/domain_experts.json").read_text(encoding="utf-8"))}
    additions,errors=build(candidates,existing,experts)
    print(json.dumps({"new_confirmed_abstract":len(additions),"crossref_lookup_errors":errors},ensure_ascii=False))
    if errors:
        raise SystemExit("FAIL CLOSED: publisher metadata retrieval incomplete; no milestone write")
    if args.apply and additions:
        MILESTONES.write_text(json.dumps(existing+additions,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

if __name__=="__main__":
    main()
