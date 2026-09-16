"""Create a clean upload bundle; excludes originals, resumes and Sites credentials."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from html.parser import HTMLParser

root = Path(__file__).resolve().parents[1]
references = set()
class Assets(HTMLParser):
    def handle_starttag(self, tag, attrs):
        for key, value in attrs:
            if key in ('src', 'poster', 'href') and value and value.startswith('assets/'):
                references.add('dist/' + value.split('?')[0])
Assets().feed((root/'dist/index.html').read_text(encoding='utf-8'))
files = [root/name for name in ['build.py', 'content-en.json', 'README.md', 'GITHUB-PAGES.md', 'LICENSE']]
for folder in ['dist', 'scripts', '.github', 'tests']:
    files.extend(p for p in (root/folder).rglob('*') if p.is_file()
                 and '__pycache__' not in p.parts and '.openai' not in p.parts)
def include(path):
    relative = path.relative_to(root).as_posix()
    if relative.startswith(('dist/assets/gallery/', 'dist/assets/publications/', 'dist/assets/collaborations/')) or relative.startswith('dist/assets/portrait-'):
        return relative in references
    return True
files = [p for p in files if include(p)]
with ZipFile(root/'github-pages-ready.zip', 'w', ZIP_DEFLATED, compresslevel=6) as archive:
    for path in files:
        archive.write(path, path.relative_to(root).as_posix())
with ZipFile(root/'github-pages-ready.zip') as archive:
    assert archive.testzip() is None
    names = archive.namelist()
    assert '.github/workflows/pages.yml' in names
    assert 'dist/assets/scholar.js' in names
    assert not any(x.startswith('assets/') or x.endswith('.docx') for x in names)
    assert all(reference in names for reference in references)
    assert not any(x.startswith('dist/assets/gallery/') for x in names)
print('Created and verified github-pages-ready.zip')
