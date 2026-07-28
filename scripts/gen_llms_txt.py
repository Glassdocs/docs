#!/usr/bin/env python3
"""Generate docs/llms.txt and docs/llms-full.txt from the nav in mkdocs.yml.

llms.txt is the convention for pointing LLMs and answer engines at a
token-efficient, canonical version of a docs site. Two files, two jobs:

  llms.txt       a curated index — title, one-line summary, link per page.
                 What an engine reads to decide WHICH page it needs.
  llms-full.txt  every page's Markdown concatenated. What an engine reads
                 when it wants the whole corpus in one fetch.

Generated rather than hand-written on purpose: a hand-maintained index is a
stale index the first time someone adds a page.

Nav order is the authoring order, which is already the order a human should
read these in — so it is also the right order for a machine.

Usage:  python3 scripts/gen_llms_txt.py
Run it whenever docs/ or the nav changes; the output is committed.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOCS = ROOT / "docs"
SITE = "https://docs.glassdocs.site"

# Files that are not prose pages and must never land in the corpus.
SKIP = {"llms.txt", "llms-full.txt", "robots.txt"}


def read_nav(mkdocs: Path) -> list[tuple[str, str]]:
    """[(title, filename)] in nav order.

    Deliberately a small regex rather than a YAML dependency: the nav is a flat
    `- Title: file.md` list, and requiring PyYAML to build a text file would be
    a dependency for nothing. If the nav ever grows nested sections this must
    be revisited rather than silently dropping them — hence the strict match.
    """
    lines = mkdocs.read_text(encoding="utf-8").splitlines()
    try:
        start = next(i for i, l in enumerate(lines) if l.rstrip() == "nav:")
    except StopIteration:
        sys.exit("mkdocs.yml has no `nav:` block")

    out: list[tuple[str, str]] = []
    for line in lines[start + 1 :]:
        if line.strip() and not line.startswith((" ", "\t")):
            break  # dedented to a new top-level key — nav is over
        m = re.match(r'^\s+-\s+"?([^":]+)"?\s*:\s*(\S+\.md)\s*$', line)
        if m:
            out.append((m.group(1).strip(), m.group(2).strip()))
        elif line.strip().startswith("-"):
            sys.exit(f"nav entry not understood (nested section?): {line!r}")
    return out


def summarize(md: str) -> str:
    """The first real paragraph, flattened to one line of plain text.

    This is what an engine sees when deciding whether to fetch the page, so it
    has to survive losing its formatting. Skips the H1, admonitions, and any
    leading front-matter.
    """
    body = re.sub(r"^---\n.*?\n---\n", "", md, flags=re.S)
    for block in re.split(r"\n\s*\n", body):
        b = block.strip()
        if not b or b.startswith(("#", "!!!", "```", "|", "- ", "* ", ">")):
            continue
        # Strip inline markdown that adds noise without meaning in plain text.
        b = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", b)  # links → their text
        b = re.sub(r"[*_`]", "", b)
        b = " ".join(b.split())
        return b if len(b) <= 300 else b[:297].rsplit(" ", 1)[0] + "…"
    return ""


def main() -> None:
    nav = read_nav(ROOT / "mkdocs.yml")
    if not nav:
        sys.exit("nav parsed to zero pages — refusing to write an empty index")

    index = [
        "# Glassdocs",
        "",
        "> Publish a knowledge base from a GitHub repo of Markdown, hosted on your own "
        "Cloudflare account, with an AI assistant that can read and edit it. Glassdocs "
        "is a control plane: it never stores your document content.",
        "",
        "## Docs",
        "",
    ]
    corpus = ["# Glassdocs — full documentation", ""]
    missing = []

    for title, name in nav:
        path = DOCS / name
        if not path.exists():
            missing.append(name)
            continue
        md = path.read_text(encoding="utf-8")
        summary = summarize(md)
        url = f"{SITE}/{'' if name == 'index.md' else name[:-3] + '/'}"
        index.append(f"- [{title}]({url}){': ' + summary if summary else ''}")
        corpus += [f"\n---\n\n# {title}\n\n<!-- {url} -->\n", md.strip(), ""]

    # A page in the nav but not on disk means the site itself is broken; say so
    # loudly rather than quietly shipping an index that omits it.
    if missing:
        sys.exit(f"nav references missing files: {', '.join(missing)}")

    (DOCS / "llms.txt").write_text("\n".join(index).rstrip() + "\n", encoding="utf-8")
    (DOCS / "llms-full.txt").write_text("\n".join(corpus).rstrip() + "\n", encoding="utf-8")
    print(f"wrote docs/llms.txt and docs/llms-full.txt ({len(nav)} pages)")


if __name__ == "__main__":
    main()
