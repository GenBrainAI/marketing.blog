import os

def _all_posts():
    posts = []
    for root, dirs, files in os.walk('posts'):
        for f in files:
            if f.endswith('.md'):
                posts.append(os.path.join(root, f))
    return posts

def test_post_count():
    assert len(_all_posts()) >= 75

def test_frontmatter():
    for path in _all_posts():
        with open(path) as fh:
            content = fh.read()
        assert '---' in content, f"Missing frontmatter in {path}"
        assert 'title:' in content, f"Missing title in {path}"

def test_internal_links():
    for path in _all_posts():
        with open(path) as fh:
            content = fh.read()
        assert '/blog/' in content, f"No internal links in {path}"

def test_cyborgenic_positioning():
    missing = []
    for path in _all_posts():
        with open(path) as fh:
            content = fh.read().lower()
        if 'cyborgenic' not in content:
            missing.append(path)
    assert len(missing) == 0, f"{len(missing)} posts missing Cyborgenic mention: {missing[:5]}"

def test_legal_documents():
    required = ['terms-of-service.md', 'privacy-policy.md', 'acceptable-use.md', 'org-agreement.md']
    for doc in required:
        path = os.path.join('legal', doc)
        assert os.path.exists(path), f"Missing legal document: {path}"

def test_social_media_content():
    linkedin = [f for f in os.listdir('social/linkedin') if f.endswith('.md')]
    twitter = [f for f in os.listdir('social/twitter') if f.endswith('.md')]
    assert len(linkedin) >= 10, f"Only {len(linkedin)} LinkedIn posts"
    assert len(twitter) >= 10, f"Only {len(twitter)} Twitter threads"

def test_assets_exist():
    assert os.path.isdir('assets/diagrams'), "Missing assets/diagrams directory"
    diagrams = [f for f in os.listdir('assets/diagrams') if f.endswith('.mmd')]
    assert len(diagrams) >= 5, f"Only {len(diagrams)} diagram files"
