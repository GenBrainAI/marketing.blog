#!/usr/bin/env python3
"""Convert a marketing.blog post (.md) to an agent-ceo-website blog post (.mdx).

marketing.blog is the source; the website serves content/blog/<slug>.mdx (a
different, editorially-adapted frontmatter schema). This transform is
MERGE-AWARE: when the target .mdx already exists we PRESERVE its editorial
fields (author, category) and only refresh title/date/tags/excerpt + body from
the source — so syncing a changed post never regresses hand-made editorial
decisions (e.g. source category 'technical' kept as website 'Cyborgenic').

Usage: blog_md_to_mdx.py --src <source.md> --dst <target.mdx>
Frontmatter is parsed with a minimal line parser (no PyYAML dependency); the
`tags` line and the body are passed through verbatim.
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

DEFAULT_AUTHOR = "Moshe Beeri, Founder"
DROP = {"slug", "cluster", "relatedposts", "description"}  # not in website schema


def split_frontmatter(text: str) -> tuple[list[str], str]:
    """Return (frontmatter_lines, body). Empty fm list if none."""
    if not text.startswith("---"):
        return [], text
    end = text.find("\n---", 3)
    if end == -1:
        return [], text
    fm = text[3:end].strip("\n").splitlines()
    body = text[end + 4:].lstrip("\n")
    return fm, body


def fm_get(lines: list[str], key: str) -> str | None:
    """Return the raw value (string after 'key:') for a top-level key, or None.
    Captures multi-line list values (indented continuation lines)."""
    out = None
    for i, ln in enumerate(lines):
        m = re.match(rf"^{re.escape(key)}:\s*(.*)$", ln, re.IGNORECASE)
        if m:
            val = m.group(1)
            # gather indented continuation (YAML block list)
            j = i + 1
            cont = []
            while j < len(lines) and re.match(r"^\s+\S", lines[j]):
                cont.append(lines[j]); j += 1
            out = val if not cont else val + "\n" + "\n".join(cont)
            break
    return out


def quote(v: str) -> str:
    v = v.strip().strip('"').strip("'")
    return f'"{v}"'


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--dst", required=True)
    a = ap.parse_args(argv)
    src_text = Path(a.src).read_text(encoding="utf-8")
    s_fm, body = split_frontmatter(src_text)
    if not s_fm:
        print(f"ERROR: no frontmatter in {a.src}", file=sys.stderr); return 1

    dst = Path(a.dst)
    d_fm = split_frontmatter(dst.read_text(encoding="utf-8"))[0] if dst.exists() else []

    title = fm_get(s_fm, "title") or fm_get(d_fm, "title") or '"Untitled"'
    date = fm_get(s_fm, "date") or fm_get(d_fm, "date") or '"2026-01-01"'
    tags = fm_get(s_fm, "tags") or fm_get(d_fm, "tags") or "[]"
    excerpt = fm_get(s_fm, "description") or fm_get(d_fm, "excerpt") or '""'
    # Editorial fields: preserve target's if it exists, else derive.
    # AUTHOR: target wins (an editor's hand-set author is never regressed), then the
    # SOURCE's own author, and only then the default. Reading d_fm alone meant every
    # NEW post was attributed to DEFAULT_AUTHOR no matter who wrote it — a post whose
    # source said `author: "Marketing Agent"` published as "Moshe Beeri, Founder".
    # That is a misattribution on a public page, and it also silently violated
    # CONTENT-STANDARDS ("Named authors only... Technical posts: 'Engineering Team' or
    # specific agent role"). Every other field here already follows source-then-target;
    # author was the one that skipped the source entirely.
    author = fm_get(d_fm, "author") or fm_get(s_fm, "author") or f'"{DEFAULT_AUTHOR}"'
    cat = fm_get(d_fm, "category")
    if not cat:
        sc = (fm_get(s_fm, "category") or "updates").strip().strip('"').strip("'")
        cat = '"' + sc[:1].upper() + sc[1:] + '"'

    out = (
        "---\n"
        f"title: {quote(title)}\n"
        f"date: {quote(date)}\n"
        f"author: {author if author.startswith(chr(34)) else quote(author)}\n"
        f"category: {cat if cat.startswith(chr(34)) else quote(cat)}\n"
        f"tags: {tags}\n"
        f"excerpt: {quote(excerpt)}\n"
        "---\n\n"
        f"{body.rstrip()}\n"
    )
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(out, encoding="utf-8")
    print(f"converted {a.src} -> {a.dst} (category={cat}, new={'no' if d_fm else 'yes'})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
