#!/usr/bin/env python3
"""Validate the poster collection, PDF references, and optional rendered HTML."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


def get_field(front: str, name: str) -> str:
    match = re.search(rf"(?m)^{re.escape(name)}:\s*(.*?)\s*$", front)
    if not match:
        return ""
    value = match.group(1).strip()
    if len(value) >= 2 and value[0] in ("'", '"') and value[-1] == value[0]:
        return value[1:-1]
    return value


def validate(root: Path, site: Path | None = None) -> list[str]:
    talks = root / "_talks"
    assets = root / "assets" / "pdf" / "talks"
    errors: list[str] = []
    referenced: set[Path] = set()
    posters: list[tuple[str, Path]] = []
    awards: list[tuple[str, Path, Path]] = []
    if not talks.is_dir():
        return ["Missing _talks/ collection"]

    for source in sorted(talks.iterdir()):
        if source.is_file() and source.suffix.lower() == ".pdf":
            errors.append(f"{source.relative_to(root)}: PDF belongs in assets/pdf/talks/, not _talks/")
        if source.suffix.lower() != ".md":
            continue
        body = source.read_text(encoding="utf-8")
        match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", body, re.S)
        if not match:
            errors.append(f"{source.relative_to(root)}: missing YAML front matter")
            continue
        front = match.group(1)
        if get_field(front, "category") != "poster":
            continue
        for field in ("title", "date", "venue"):
            if not get_field(front, field):
                errors.append(f"{source.relative_to(root)}: missing poster field {field}")
        found_pdf = False
        for url in re.findall(r"(?m)^\s*url:\s*['\"]?([^'\"\n]+?)['\"]?\s*$", front):
            href = url.strip()
            if not href.lower().endswith(".pdf"):
                continue
            found_pdf = True
            parsed = urlsplit(href)
            relative = unquote(parsed.path)
            if parsed.netloc or not relative.startswith("/assets/pdf/talks/") or ".." in Path(relative).parts:
                errors.append(f"{source.relative_to(root)}: invalid poster PDF reference {href}")
                continue
            target = root / relative.lstrip("/")
            referenced.add(target)
            posters.append((get_field(front, "title"), Path(relative.lstrip("/"))))
            if not target.is_file() or target.stat().st_size < 4:
                errors.append(f"{source.relative_to(root)}: missing or empty poster PDF {href}")
        if not found_pdf:
            errors.append(f"{source.relative_to(root)}: poster has no PDF reference")

        award_title = get_field(front, "award_title")
        if award_title:
            for field in ("award_recipient", "award_issuer", "award_date"):
                if not get_field(front, field):
                    errors.append(f"{source.relative_to(root)}: award field missing: {field}")
            award_assets: dict[str, Path] = {}
            for field, prefix, suffixes in (
                ("award_certificate_image", "/assets/img/talks/awards/", {".webp", ".png", ".jpg", ".jpeg"}),
                ("award_certificate_pdf", "/assets/pdf/talks/awards/", {".pdf"}),
            ):
                href = get_field(front, field)
                if not href:
                    errors.append(f"{source.relative_to(root)}: award certificate missing: {field}")
                    continue
                parsed = urlsplit(href)
                relative = unquote(parsed.path)
                if parsed.netloc or not relative.startswith(prefix) or ".." in Path(relative).parts or Path(relative).suffix.lower() not in suffixes:
                    errors.append(f"{source.relative_to(root)}: invalid award asset: {href}")
                    continue
                asset_path = Path(relative.lstrip("/"))
                target = root / asset_path
                award_assets[field] = asset_path
                if not target.is_file() or target.stat().st_size < 4:
                    errors.append(f"{source.relative_to(root)}: award asset missing or empty: {href}")
            if len(award_assets) == 2:
                awards.append((award_title, award_assets["award_certificate_image"], award_assets["award_certificate_pdf"]))

    if assets.is_dir():
        for pdf in sorted(assets.iterdir()):
            if pdf.is_file() and pdf.suffix.lower() == ".pdf" and pdf not in referenced:
                errors.append(f"{pdf.relative_to(root)}: unreferenced poster PDF (missing _talks/*.md)")

    if site is not None:
        page = site / "talks" / "index.html"
        if not page.is_file():
            errors.append(f"Built talks page missing: {page}")
        else:
            html = page.read_text(encoding="utf-8")
            for title, relative in posters:
                if title not in html:
                    errors.append(f"Poster title missing in built talks page: {title}")
                compiled_pdf = site / relative
                if not compiled_pdf.is_file():
                    errors.append(f"Poster PDF missing in built site: {relative}")
                elif (root / relative).stat().st_size != compiled_pdf.stat().st_size:
                    errors.append(f"Poster PDF size differs in built site: {relative}")
            for award_title, image_rel, pdf_rel in awards:
                if award_title not in html:
                    errors.append(f"Award title missing in built talks page: {award_title}")
                for relative in (image_rel, pdf_rel):
                    if "/" + relative.as_posix() not in html:
                        errors.append(f"Award link missing from built talks page: {relative}")
                    built = site / relative
                    if not built.is_file():
                        errors.append(f"Award proof missing from built site: {relative}")
                    elif (root / relative).stat().st_size != built.stat().st_size:
                        errors.append(f"Award proof size differs in built site: {relative}")
    return errors


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    site = Path(sys.argv[2]).resolve() if len(sys.argv) == 3 and sys.argv[1] == "--site" else None
    errors = validate(root, site)
    for error in errors:
        print(f"POSTER ERROR: {error}")
    if errors:
        return 1
    print("Poster check passed: records, source PDFs, and requested site output are consistent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
