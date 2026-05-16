#!/usr/bin/env python3
"""Generate sitemap.xml from blog posts directory.

Reads all .md files in posts/, extracts slug from frontmatter,
and generates a complete sitemap.xml for agent.ceo.

Usage: cd marketing.blog && python3 scripts/generate-sitemap.py > seo/sitemap.xml
"""

import glob
import os
import re
from datetime import datetime

SITE_URL = "https://agent.ceo"
TODAY = datetime.now().strftime('%Y-%m-%d')

STATIC_PAGES = [
    ("/", "weekly", "1.0", TODAY),
    ("/pricing", "monthly", "0.9", TODAY),
    ("/scan", "monthly", "0.9", TODAY),
    ("/blog", "daily", "0.8", TODAY),
    ("/use-cases/devops", "monthly", "0.8", "2026-05-10"),
    ("/use-cases/security", "monthly", "0.8", "2026-05-10"),
    ("/use-cases/engineering", "monthly", "0.8", "2026-05-10"),
    ("/compare/devin", "monthly", "0.7", "2026-05-10"),
    ("/enterprise", "monthly", "0.8", "2026-05-10"),
    ("/legal/terms", "monthly", "0.6", "2026-05-15"),
    ("/legal/privacy", "monthly", "0.6", "2026-05-15"),
    ("/legal/eula", "monthly", "0.6", "2026-05-15"),
    ("/blog/faq-cyborgenic-organization", "monthly", "0.8", "2026-05-16"),
    ("/blog/glossary-ai-agent-orchestration", "monthly", "0.8", "2026-05-16"),
    ("/docs", "weekly", "0.8", TODAY),
]

DOCS_PAGES = [
    ("/docs/getting-started", "weekly", "0.8"),
    ("/docs/concepts/cyborgenic-orgs", "monthly", "0.8"),
    ("/docs/concepts/agents", "monthly", "0.7"),
    ("/docs/concepts/organizations", "monthly", "0.7"),
    ("/docs/concepts/tasks", "monthly", "0.7"),
    ("/docs/concepts/messaging", "monthly", "0.7"),
    ("/docs/concepts/knowledge-base", "monthly", "0.7"),
    ("/docs/getting-started/saas", "monthly", "0.7"),
    ("/docs/getting-started/first-agent", "monthly", "0.7"),
    ("/docs/getting-started/billing", "monthly", "0.7"),
    ("/docs/platform/architecture", "monthly", "0.7"),
    ("/docs/security/overview", "monthly", "0.7"),
    ("/docs/deployment/install-on-kubernetes", "monthly", "0.7"),
    ("/docs/api-reference/rest-api", "monthly", "0.6"),
    ("/docs/integrations/github", "monthly", "0.6"),
    ("/docs/integrations/slack", "monthly", "0.6"),
    ("/docs/guides/faq", "monthly", "0.7"),
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

    for path, freq, priority, lastmod in STATIC_PAGES:
        print(f'  <url>')
        print(f'    <loc>{SITE_URL}{path}</loc>')
        print(f'    <lastmod>{lastmod}</lastmod>')
        print(f'    <changefreq>{freq}</changefreq>')
        print(f'    <priority>{priority}</priority>')
        print(f'  </url>')

    for path, freq, priority in DOCS_PAGES:
        print(f'  <url>')
        print(f'    <loc>{SITE_URL}{path}</loc>')
        print(f'    <lastmod>{TODAY}</lastmod>')
        print(f'    <changefreq>{freq}</changefreq>')
        print(f'    <priority>{priority}</priority>')
        print(f'  </url>')

    for filepath in sorted(glob.glob('posts/**/*.md', recursive=True)):
        fm = extract_frontmatter(filepath)
        if not fm or 'slug' not in fm:
            continue
        slug = fm['slug']
        date = fm.get('date', TODAY)
        priority = "0.8" if 'getting-started' in slug or 'case-study' in slug or 'cyborgenic' in slug else "0.7"

        print(f'  <url>')
        print(f'    <loc>{SITE_URL}/blog/{slug}</loc>')
        print(f'    <lastmod>{date}</lastmod>')
        print(f'    <changefreq>monthly</changefreq>')
        print(f'    <priority>{priority}</priority>')
        print(f'  </url>')

    print('</urlset>')


if __name__ == '__main__':
    main()
