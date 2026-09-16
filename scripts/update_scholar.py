"""Fetch only the public author citation total, preserving last good data on failure."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path


def validate(data, author_id):
    if data.get('scholar_id') != author_id:
        raise ValueError('Scholar ID mismatch')
    total = data.get('citedby')
    if isinstance(total, bool) or not isinstance(total, int) or total < 0:
        raise ValueError('Citation count must be a nonnegative integer')
    timestamp = datetime.fromisoformat(data['updated'].replace('Z', '+00:00'))
    if timestamp.tzinfo is None:
        raise ValueError('Citation timestamp must include its time zone')
    return data


def save(data, output, author_id):
    validate(data, author_id)
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix('.tmp')
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    temporary.replace(output)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('dist/assets/gs_data.json'))
    args = parser.parse_args()
    author_id = os.environ.get('GOOGLE_SCHOLAR_ID', 'aEts7nUAAAAJ')
    # Import here so validation and offline tests do not need network dependencies.
    from scholarly import scholarly
    author = scholarly.search_author_id(author_id)
    scholarly.fill(author, sections=['indices'])
    data = {'scholar_id': author_id, 'citedby': author.get('citedby'),
            'updated': datetime.now(timezone.utc).isoformat(), 'source': 'Google Scholar'}
    save(data, args.output, author_id)
    print('Updated Google Scholar citation total:', data['citedby'])


if __name__ == '__main__':
    main()
