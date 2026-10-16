#!/usr/bin/env python3
"""Conservative, DOI-grounded publication sync for Yaqian Li's academic website.

OpenAlex discovers potential works by the author's verified ID. Crossref
independently supplies publisher-deposited metadata. Uncertain matches are
reported but never committed. Existing hand-curated BibTeX is never rewritten.
"""
from __future__ import annotations

import argparse
import datetime as dt
import difflib
import hashlib
import html
import json
import pathlib
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

AUTHOR_ID = "A5100697597"  # Verified via four existing journal article DOIs.
SEED_DOIS = {
    "10.1038/s41467-025-62192-0",
    "10.1038/s41467-024-54822-w",
    "10.1002/aic.18683",
    "10.1016/j.mcat.2024.114706",
}
BIB = pathlib.Path("_bibliography/papers.bib")
STATS = pathlib.Path("_data/publication_stats.yml")
REPORT = pathlib.Path("publication-sync-report.json")
DOI_RE = re.compile(r"^10\.\d{4,9}/[^\s{}<>]+$", re.I)
ENTRY_RE = re.compile(r"(?m)^@article\{[^\n]+\{?", re.I)
YEAR_MIN = 2024
MAX_NEW_PER_RUN = 10


def doi_clean(value):
    if not isinstance(value, str):
        return ""
    return re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value.strip(), flags=re.I).lower()


def doi_existing(bib):
    return {doi_clean(x) for x in re.findall(r"(?mi)^\s*doi\s*=\s*\{([^}]+)\}", bib)}


def names_existing(bib):
    names = set()
    for value in re.findall(r"(?mi)^\s*author\s*=\s*\{([^}]+)\}", bib):
        for name in value.split(" and "):
            parts = name.split(",")
            if len(parts) == 2 and name.strip().lower() != "others":
                names.add(normalize(" ".join([parts[1], parts[0]])))
    names.discard(normalize("Yaqian Li"))
    return names


def normalize(value):
    return " ".join(re.findall(r"\w+", html.unescape(value).lower())).strip()


def clean_field(value):
    """Permit plain Unicode bibliography text; forbid TeX/field injection."""
    return re.sub(r"\s+", " ", re.sub(r"[{}\\\r\n]", " ", html.unescape(str(value)))).strip()


def get_json(url, attempts=3):
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "Accept": "application/json",
                    "User-Agent": "YaqianLiAcademicSite/1.0 (https://ly5681672-max.github.io/)",
                },
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.load(response)
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
            if isinstance(exc, urllib.error.HTTPError) and exc.code not in (429, 500, 502, 503, 504):
                raise
            if attempt == attempts - 1:
                raise
            time.sleep(2**attempt)
    raise RuntimeError("API retries exhausted")


def openalex_works():
    works = []
    for page in range(1, 5):
        qs = urllib.parse.urlencode(
            {
                "filter": f"author.id:{AUTHOR_ID},from_publication_date:{YEAR_MIN}-01-01",
                "per_page": 100,
                "page": page,
            }
        )
        data = get_json("https://api.openalex.org/works?" + qs)
        items = data.get("results")
        if not isinstance(items, list):
            raise ValueError("OpenAlex works response invalid")
        works.extend(items)
        if len(items) < 100:
            break
    else:
        raise ValueError("Author has >300 works; refusing truncated scan")
    observed = {doi_clean(w.get("doi")) for w in works}
    if len(observed & SEED_DOIS) < 2:
        raise ValueError("Author identity drift: verified DOI seed intersection < 2")
    return works


def work_identity(work):
    """OpenAlex has occasionally missing author IDs; null is not affirmative."""
    for authorship in work.get("authorships") or []:
        author = authorship.get("author") or {}
        aid = str(author.get("id") or "").rsplit("/", 1)[-1]
        if aid == AUTHOR_ID and normalize(author.get("display_name") or "") in (
            "yaqian li", "li yaqian", "ya qian li", "li ya qian"
        ):
            institutions = [
                normalize(i.get("display_name") or "")
                for i in (authorship.get("institutions") or [])
            ]
            affiliation = any(
                "china university of petroleum" in name or "state key laboratory of heavy oil" in name
                for name in institutions
            )
            return True, affiliation
    return False, False


def crossref_author_names(record):
    authors = record.get("author") or []
    names = set()
    target = False
    rendered = []
    for author in authors:
        given = clean_field(author.get("given") or "")
        family = clean_field(author.get("family") or "")
        if not given or not family:
            continue
        full = normalize(given + " " + family)
        if full in ("yaqian li", "li yaqian", "ya qian li", "li ya qian"):
            target = True
        else:
            names.add(full)
        rendered.append(f"{family}, {given}")
    return target, names, rendered


def assess_candidate(work, record, known_names):
    valid, institution = work_identity(work)
    if not valid:
        return "OpenAlex author ID/name not confirmed"
    if record.get("type") != "journal-article":
        return "Not a journal article in publisher Crossref record"
    doi = doi_clean(record.get("DOI"))
    if doi != doi_clean(work.get("doi")) or not DOI_RE.match(doi):
        return "DOI mismatch"
    has_target, names, rendered = crossref_author_names(record)
    if not has_target:
        return "Crossref does not explicitly name Yaqian Li"
    coauthor_count = len(known_names & names)
    if coauthor_count < 2 and not (institution and coauthor_count >= 1):
        return "Insufficient corroborating known coauthors/affiliation"
    title = (record.get("title") or [""])[0]
    if not isinstance(title, str) or len(clean_field(title)) < 18:
        return "Invalid publisher title"
    openalex_title = work.get("title") or ""
    similarity = difflib.SequenceMatcher(None, normalize(title), normalize(openalex_title)).ratio()
    if similarity < 0.86:
        return "Publisher/OpenAlex title disagreement"
    if not record.get("container-title") or not rendered:
        return "Incomplete publisher journal/authors"
    return None


def render_bibtex(work, record, existing_keys):
    doi = doi_clean(record["DOI"])
    published = record.get("published-print") or record.get("published") or record.get("published-online") or record.get("issued") or {}
    try:
        year = int(published["date-parts"][0][0])
    except (KeyError, IndexError, TypeError, ValueError):
        year = int(work.get("publication_year") or 0)
    if not YEAR_MIN <= year <= dt.date.today().year + 2:
        raise ValueError("Publication year inconsistent")
    _, _, authors = crossref_author_names(record)
    title = clean_field(record["title"][0])
    journal = clean_field(record["container-title"][0])
    if not title or not journal or not authors:
        raise ValueError("Missing required BibTeX field")
    key = "auto" + str(year) + "_" + hashlib.sha256(doi.encode()).hexdigest()[:12]
    if key in existing_keys:
        raise ValueError("Generated BibTeX key collision")
    abbr = "".join(re.findall(r"[A-Za-z]+", journal))[:16] or "Journal"
    entry = (
        f"@article{{{key},\n"
        f"  title = {{{title}}},\n"
        f"  author = {{{' and '.join(authors)}}},\n"
        f"  journal = {{{journal}}},\n"
        f"  year = {{{year}}},\n"
        f"  doi = {{{doi}}},\n"
        f"  url = {{https://doi.org/{doi}}},\n"
        f"  abbr = {{{abbr}}},\n"
        f"  bibtex_show = {{true}}\n"
        f"}}\n"
    )
    return key, entry


def sync(apply=False):
    original = BIB.read_text(encoding="utf-8")
    existing = doi_existing(original)
    known_names = names_existing(original)
    keys = set(re.findall(r"(?mi)^@article\{([^,\n]+)", original))
    if len(existing) != len(keys) or len(keys) < 23:
        raise ValueError("Existing bibliography IDs/DOIs inconsistent; refusing to update")
    pending, approved = [], []
    seen = set()
    works = openalex_works()
    for work in works:
        doi = doi_clean(work.get("doi"))
        if doi in seen or doi in existing or not DOI_RE.match(doi):
            continue
        seen.add(doi)
        try:
            record = get_json("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/"))["message"]
            reason = assess_candidate(work, record, known_names)
            if reason:
                pending.append({"doi": doi, "title": work.get("title"), "reason": reason})
                continue
            key, entry = render_bibtex(work, record, keys)
            keys.add(key)
            approved.append({"doi": doi, "key": key, "title": record["title"][0], "entry": entry})
        except (Exception) as exc:
            pending.append({"doi": doi, "title": work.get("title"), "reason": str(exc)[:180]})
    approved.sort(key=lambda paper: paper["doi"])
    if len(approved) > MAX_NEW_PER_RUN:
        raise ValueError("Too many proposed publications; refusing mass changes")
    report = {
        "checked_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "openalex_author_id": AUTHOR_ID,
        "found_by_openalex": len(works),
        "existing_journal_dois": len(existing),
        "approved": [{k: v for k, v in paper.items() if k != "entry"} for paper in approved],
        "pending_review": pending,
        "mode": "apply" if apply else "dry-run",
    }
    REPORT.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if apply and approved:
        BIB.write_text(original.rstrip() + "\n\n" + "\n".join(p["entry"].rstrip() for p in approved) + "\n", encoding="utf-8")
        STATS.write_text(
            "# Distinct journal-article DOIs; updated by scripts/sync_publications.py.\n"
            f"journal_count: {len(existing) + len(approved)}\n"
            "baseline_researchgate_records: 25\n"
            "baseline_preprints: 2\n",
            encoding="utf-8",
        )
    print(json.dumps({k: v for k, v in report.items() if k != "pending_review"}, ensure_ascii=False, indent=2))
    print(f"PENDING_REVIEW_COUNT={len(pending)}")
    print(f"APPROVED_NEW_COUNT={len(approved)}")
    return report


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description=__doc__)
    group = argparser.add_mutually_exclusive_group()
    group.add_argument("--apply", action="store_true", help="Append only strongly verified DOI records")
    group.add_argument("--dry-run", action="store_true", help="Report candidates without modifying bibliography")
    args = argparser.parse_args()
    sync(apply=args.apply)
