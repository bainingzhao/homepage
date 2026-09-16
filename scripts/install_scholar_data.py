"""Select the newest valid count from committed and cached data."""
from pathlib import Path
from datetime import datetime
import json
import os
from update_scholar import validate, save

author_id = os.environ.get('GOOGLE_SCHOLAR_ID', 'aEts7nUAAAAJ')
target = Path('dist/assets/gs_data.json')
candidates = []
for path in [target, Path('.scholar-cache/gs_data.json')]:
    if path.exists():
        try:
            candidates.append(validate(json.loads(path.read_text(encoding='utf-8')), author_id))
        except (ValueError, KeyError, TypeError):
            print('Ignoring invalid citation data:', path)
if candidates:
    newest = max(candidates, key=lambda x: datetime.fromisoformat(x['updated'].replace('Z', '+00:00')))
    save(newest, target, author_id)
    print('Installed citation data dated', newest['updated'])
else:
    print('No verified citation data available yet; badge remains unavailable.')
