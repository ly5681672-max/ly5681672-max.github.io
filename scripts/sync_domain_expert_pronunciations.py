#!/usr/bin/env python3
"""Enrich expert IPA only from Wikidata entries matched by exact ORCID.
No speculative transliteration; existing pronunciation fields remain unchanged.
"""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "_data/domain_experts.json"
API = "https://www.wikidata.org/w/api.php"
IPA = re.compile(r"^[/\[].+[/\]]$")
ORCID = re.compile(r"^\\d{4}-\\d{4}-\\d{4}-[\\dX]{4}$")

def get_json(params):
    url = API + "?" + urlencode(params)
    with urlopen(Request(url, headers={"User-Agent": "academic-expert-ipa-sync/1.0 (GitHub Pages research site)"}), timeout=20) as r:
        return json.load(r)

def matched_ipa(orcid):
    if not ORCID.fullmatch(orcid):
        return None
    found = get_json({"action":"query","list":"search","srsearch":'haswbstatement:P496='+orcid,"srnamespace":0,"srlimit":10,"format":"json"})
    # Wikidata full-text search is not an identity guarantee. Verify entity claims.
    candidates = [row["title"] for row in found.get("query",{}).get("search",[]) if re.fullmatch(r"Q\\d+",row.get("title",""))]
    if not candidates:
        return None
    data = get_json({"action":"wbgetentities","ids":"|".join(candidates),"props":"claims","format":"json"})
    matched = []
    for qid,entity in data.get("entities",{}).items():
        claims = entity.get("claims",{})
        ids = [s.get("mainsnak",{}).get("datavalue",{}).get("value") for s in claims.get("P496",[])]
        if orcid not in ids:
            continue
        values = []
        for s in claims.get("P898",[]):
            if s.get("rank") == "deprecated":
                continue
            v = s.get("mainsnak",{}).get("datavalue",{}).get("value")
            if isinstance(v,str) and IPA.fullmatch(v) and len(v)<180:
                values.append(v)
        if len(set(values))==1:
            matched.append((qid,values[0]))
    return matched[0] if len(matched)==1 else None

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--apply",action="store_true")
    args=ap.parse_args()
    experts=json.loads(DATA.read_text(encoding="utf-8"))
    changed=0
    for p in experts:
        if p.get("pronunciation_ipa") or not p.get("orcid"):
            continue
        result=matched_ipa(p["orcid"])
        if not result:
            print(p["id"]+": no identity-verified unique IPA; leave blank")
            continue
        qid,ipa=result
        p["pronunciation_ipa"]=ipa
        p["pronunciation_status"]="SOURCE_VERIFIED"
        p["pronunciation_source"]="https://www.wikidata.org/wiki/"+qid
        changed+=1
    if args.apply and changed:
        DATA.write_text(json.dumps(experts,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8")
    print("verified IPA candidates: "+str(changed)+("; applied" if args.apply else "; dry-run"))

if __name__=="__main__":
    main()
