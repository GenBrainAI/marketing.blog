import os

def test_post_count():
    count = 0
    for root, dirs, files in os.walk('posts'):
        for f in files:
            if f.endswith('.md'):
                count += 1
    assert count >= 75

def test_frontmatter():
    for root, dirs, files in os.walk('posts'):
        for f in files:
            if f.endswith('.md'):
                with open(os.path.join(root, f)) as fh:
                    content = fh.read()
                assert '---' in content
                assert 'title:' in content

def test_internal_links():
    for root, dirs, files in os.walk('posts'):
        for f in files:
            if f.endswith('.md'):
                with open(os.path.join(root, f)) as fh:
                    content = fh.read()
                assert '/blog/' in content
