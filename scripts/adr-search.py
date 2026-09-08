#!/usr/bin/env python3
"""
adr-search.py — Find prior decisions before making a new one.

Searches every canonical ADR and spec home at once, so an architectural
decision is checked against what has already been decided. Written after a
session (2026-08-19) rediscovered three existing decisions from scratch:
marlin-adr-058, lmf-adr-023, and the instance/extension vocabulary.

Two things this does that a plain grep or a vault search does not:

  1. It reads the LMF spec from `git show <ref>:` rather than the working
     tree. The ~/git/lmf checkout habitually sits on a feature branch behind
     main, which is how an already-merged ADR-026 was mistaken for stranded
     work. Disk state is not doctrine state.

  2. It covers `spec/` entirely, not just `spec/adrs/`. The costliest miss in
     that session was `spec/vocabulary.md` — the canonical term list, not an
     ADR. Doctrine is not only in files named adr.

Usage:
    python scripts/adr-search.py <query> [<query> ...]
    python scripts/adr-search.py --list
    python scripts/adr-search.py extension dispatch --ref main

Exit status is 0 when hits are found, 1 when none are — so a wrapper can
tell "checked, nothing prior" from "checked, read these first".
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
LMF_REPO = HOME / "git/lmf"

# Canonical homes, per lmf-adr-026 and ~/.claude/decisions/README.md.
# Disk sources are read as-is; the LMF spec is read from git (see docstring).
DISK_SOURCES = [
    ("Personal — Marlin", HOME / "Documents/Obsidian/Marlin/Decisions"),
    ("Personal — Sol3", HOME / "Projects/sol3-restoration/docs/adrs"),
    ("Personal — Prosper0 (legacy)", HOME / "git/prosper0/spec"),
]

GIT_SOURCES = [
    ("LMF framework", LMF_REPO, "spec"),
    ("LMF features", LMF_REPO, "features"),
]

# Only files under a features/ path that look like ADRs are doctrine;
# the rest of features/ is implementation and would drown the results.
FEATURE_ADR_RE = re.compile(r"/adrs?/[^/]+\.md$")


def git_files(repo, ref, prefix):
    """List tracked .md paths under prefix at ref. Empty list if unavailable."""
    try:
        r = subprocess.run(
            ["git", "-C", str(repo), "ls-tree", "-r", "--name-only", ref, prefix],
            capture_output=True, text=True, timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return []
    if r.returncode != 0:
        return []
    return [p for p in r.stdout.splitlines() if p.endswith(".md")]


def git_show(repo, ref, path):
    """Read one file's content at ref. None if unreadable."""
    try:
        r = subprocess.run(
            ["git", "-C", str(repo), "show", f"{ref}:{path}"],
            capture_output=True, text=True, timeout=10,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return None
    return r.stdout if r.returncode == 0 else None


def collect_docs(ref):
    """Yield (level, display_path, text) for every doctrine document."""
    for level, root in DISK_SOURCES:
        if not root.is_dir():
            continue
        for path in sorted(root.glob("*.md")):
            try:
                yield level, str(path).replace(str(HOME), "~"), path.read_text(encoding="utf-8")
            except OSError:
                continue

    for level, repo, prefix in GIT_SOURCES:
        for rel in git_files(repo, ref, prefix):
            if prefix == "features" and not FEATURE_ADR_RE.search("/" + rel):
                continue
            text = git_show(repo, ref, rel)
            if text is not None:
                yield level, f"~/git/lmf/{rel} ({ref})", text


def field(text, name):
    """Pull a scalar frontmatter field, unquoted. Empty string if absent."""
    m = re.search(rf"^{name}:\s*(.+)$", text[:1200], re.M)
    return m.group(1).strip().strip('"').strip("'") if m else ""


def doc_title(text, path):
    """Best available human title: frontmatter, then first H1, then filename.

    Spec documents (vocabulary.md, covenant.md) carry no frontmatter, so
    without the H1 fallback they display as bare stems and read as noise
    next to properly titled ADRs.
    """
    fm = field(text, "title")
    if fm:
        return fm
    m = re.search(r"^#\s+(.+)$", text, re.M)
    if m:
        return m.group(1).strip()
    return Path(path).stem


def decision_line(text):
    """First substantive line of the Decision section, verbatim."""
    m = re.search(r"^## Decision\s*\n(.*?)(?=^## |\Z)", text, re.S | re.M)
    if not m:
        return ""
    for line in m.group(1).splitlines():
        s = line.strip()
        if not s or s.startswith(("#", "|", ">", "-", "```", "1.")) or s.startswith("* "):
            continue
        s = re.sub(r"\s+", " ", s)
        return s if len(s) <= 200 else s[:197].rsplit(" ", 1)[0] + "..."
    return ""


def search(docs, patterns):
    """Rank documents, breadth of match first.

    Covering more of the query is stronger evidence than matching one term
    prominently: a document hitting every term is more likely the prior
    decision being looked for than one whose title happens to contain a
    single common word. Ranking title weight first put an unrelated
    "dispatcher" ADR above spec/vocabulary.md, which defined both terms.
    """
    hits = []
    for level, path, text in docs:
        matched = [p.pattern for p in patterns if p.search(text)]
        if not matched:
            continue
        title = doc_title(text, path)
        title_hits = sum(1 for p in patterns if p.search(title))
        hits.append((len(matched), title_hits, level, path, title, text, matched))
    # Breadth of coverage, then title prominence, then stable by title.
    hits.sort(key=lambda h: (-h[0], -h[1], h[4]))
    return hits


def report(hits, patterns):
    total = len(patterns)
    print(f"\n{len(hits)} document(s) match {', '.join(repr(p.pattern) for p in patterns)}")
    print("Ranked by how many query terms each covers. Read from the top.\n")
    for n_matched, _title_hits, level, path, title, text, matched in hits:
        status = field(text, "status")
        amended = field(text, "amended_by") or field(text, "superseded_by")
        flag = ""
        if status in ("superseded", "deprecated"):
            flag = f"   ⚠️ {status.upper()}"
        elif amended:
            flag = f"   ⚠️ amended by {amended}"
        print(f"\n  [{n_matched}/{total}] {title}{flag}")
        print(f"    {level} — {path}")
        if status:
            print(f"    status: {status}   matched: {', '.join(matched)}")
        d = decision_line(text)
        if d:
            print(f"    decides: {d}")


def main():
    ap = argparse.ArgumentParser(description="Search all canonical ADR and spec homes.")
    ap.add_argument("query", nargs="*", help="terms to search for (regex, case-insensitive)")
    ap.add_argument("--ref", default="main", help="git ref for LMF spec (default: main)")
    ap.add_argument("--list", action="store_true", help="list every document found, no search")
    args = ap.parse_args()

    if not args.query and not args.list:
        ap.error("give at least one query term, or --list")

    docs = list(collect_docs(args.ref))
    if not docs:
        print("No doctrine sources found. Is ~/git/lmf present?", file=sys.stderr)
        return 1

    if args.list:
        current = None
        for level, path, text in sorted(docs, key=lambda d: (d[0], d[1])):
            if level != current:
                print(f"\n=== {level} ===")
                current = level
            print(f"  {field(text, 'title') or Path(path).stem}\n    {path}")
        print(f"\n{len(docs)} documents across {len(set(d[0] for d in docs))} homes.")
        return 0

    try:
        patterns = [re.compile(q, re.I) for q in args.query]
    except re.error as e:
        print(f"Bad pattern: {e}", file=sys.stderr)
        return 2

    hits = search(docs, patterns)
    if not hits:
        print(f"\nNo prior decision matches {args.query}. Searched {len(docs)} documents.\n")
        return 1
    report(hits, patterns)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
