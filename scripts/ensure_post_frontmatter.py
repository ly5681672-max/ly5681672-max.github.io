#!/usr/bin/env python3
"""Add Jekyll front matter to newly changed dated posts without touching their bodies."""

from __future__ import annotations

import argparse
import re
import subprocess
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo

POST_NAME = re.compile(r"^(\d{4}-\d{2}-\d{2})-(.+)\.md$")
BEIJING = ZoneInfo("Asia/Shanghai")


def insert_frontmatter(path: Path, now: datetime | None = None) -> bool:
    """Return True only if a valid, front-matter-free dated post was modified."""
    match = POST_NAME.fullmatch(path.name)
    if not match or not path.is_file() or path.parent.name != "_posts":
        return False

    post_date = date.fromisoformat(match.group(1))
    original = path.read_bytes()
    content = original.decode("utf-8")
    if content.startswith("---\n") or content.startswith("---\r\n"):
        return False
    if content.startswith("---") or content.startswith("\ufeff"):
        raise ValueError(f"{path}: ambiguous or malformed YAML front matter; source preserved")

    current = (now or datetime.now(BEIJING)).astimezone(BEIJING)
    time_part = current.strftime("%H:%M:%S") if current.date() == post_date else "10:00:00"
    newline = "\r\n" if b"\r\n" in original else "\n"
    header = newline.join(
        (
            "---",
            "layout: post",
            f'title: "{match.group(2)}"',
            f"date: {post_date.isoformat()} {time_part} +0800",
            "---",
            "",
        )
    )
    # Prettier requires no extra blank line after an empty post's closing fence.
    # An existing article body still needs a separating blank line.
    if original:
        header += newline
    path.write_bytes(header.encode("utf-8") + original)
    return True


def changed_posts(before: str, after: str) -> list[Path]:
    if not re.fullmatch(r"[0-9a-fA-F]{40}", after):
        raise ValueError("Expected a full 40-character commit SHA for --after")
    if not re.fullmatch(r"[0-9a-fA-F]{40}", before):
        raise ValueError("Expected a full 40-character commit SHA for --before")

    if before == "0" * 40:
        args = ["git", "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", "-z", "--diff-filter=AM", after, "--", "_posts"]
    else:
        args = ["git", "diff", "--name-only", "--diff-filter=AM", "-z", before, after, "--", "_posts"]
    result = subprocess.run(args, capture_output=True, check=True)
    root = Path("_posts").resolve()
    found = []
    for raw in result.stdout.split(b"\0"):
        if not raw:
            continue
        candidate = Path(raw.decode("utf-8"))
        # Do not follow paths outside the dedicated blog post directory.
        if candidate.parent == Path("_posts") and candidate.resolve().parent == root:
            found.append(candidate)
    return found


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--before", help="Push event's previous commit SHA")
    parser.add_argument("--after", help="Push event's head commit SHA")
    parser.add_argument("--path", help="An explicit _posts/YYYY-MM-DD-name.md file for manual runs")
    args = parser.parse_args()

    if args.path:
        paths = [Path(args.path)]
    elif args.before and args.after:
        paths = changed_posts(args.before, args.after)
    else:
        parser.error("Provide --path, or both --before and --after")

    count = 0
    for path in paths:
        if insert_frontmatter(path):
            print(f"Added front matter: {path}")
            count += 1
    print(f"Created {count} post header(s); existing front matter and article bodies preserved")


if __name__ == "__main__":
    main()
