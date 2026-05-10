#!/usr/bin/env python3
"""Generate sitemap.xml from blog posts directory.

Reads all .md files in posts/, extracts slug from frontmatter,
and generates a complete sitemap.xml for agent.ceo.

Usage: python3 scripts/generate-sitemap.py > seo/sitemap.xml
"""

import glob
import re
from datetime import datetime

SITE_URL = "https://agent.ceo"

STATIC_PAGES = [
    ("/", "weekly", "1.0"),
    ("/pricing", "monthly", "0.9"),
    ("/scan", "monthly", "0.9"),
    ("/blog", "daily", "0.8"),
    ("/use-cases/devops", "monthly", "0.8"),
    ("/use-cases/security", "monthly", "0.8"),
    ("/use-cases/engineering", "monthly", "0.8"),
    ("/compare/devin", "monthly", "0.7"),
    ("/enterprise", "monthly", "0.8"),
]

def extract_frontmatter(filepath):
    with open(filepath) as f:
        content = f.read()
    match = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None
    fm = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, val = line.split(':', 1)
            fm[key.strip()] = val.strip().strip('"')
    return fm

def main():
    print('<?xml version="1.0" encoding="UTF-8"?>')
    print('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    for path, freq, priority in STATIC_PAGES:
        print(f'  <url>')
        print(f'    <loc>{SITE_URL}{path}</loc>')
        print(f'    <changefreq>{freq}</changefreq>')
        print(f'    <priority>{priority}</priority>')
        print(f'  </url>')

    for filepath in sorted(glob.glob('posts/**/*.md', recursive=True)):
        fm = extract_frontmatter(filepath)
        if not fm or 'slug' not in fm:
            continue
        slug = fm['slug']
        date = fm.get('date', datetime.now().strftime('%Y-%m-%d'))
        category = fm.get('category', 'technical')
        priority = "0.8" if 'getting-started' in slug or 'case-study' in slug else "0.7"

        print(f'  <url>')
        print(f'    <loc>{SITE_URL}/blog/{slug}</loc>')
        print(f'    <lastmod>{date}</lastmod>')
        print(f'    <changefreq>monthly</changefreq>')
        print(f'    <priority>{priority}</priority>')
        print(f'  </url>')

    print('</urlset>')

if __name__ == '__main__':
    main()
