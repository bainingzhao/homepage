"""Fetch only the public author citation total, preserving last good data on failure."""
import argparse
from datetime import datetime, timezone
import json
import os
import re
import subprocess
from html.parser import HTMLParser
from urllib.parse import urlencode
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


class StatisticsParser(HTMLParser):
    """Read only the citation statistics table, never publication counts."""
    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_cell = False
        self.cells = []
        self.current = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'table' and attrs.get('id') == 'gsc_rsb_st':
            self.in_table = True
        if self.in_table and tag == 'td':
            self.in_cell = True
            self.current = []

    def handle_data(self, data):
        if self.in_cell:
            self.current.append(data)

    def handle_endtag(self, tag):
        if tag == 'td' and self.in_cell:
            self.cells.append(''.join(self.current).strip())
            self.in_cell = False
        if tag == 'table':
            self.in_table = False


def parse_total(html):
    parser = StatisticsParser()
    parser.feed(html)
    # English Scholar table: Citations | All | Since YYYY; then h-index/i10-index.
    if len(parser.cells) < 3 or parser.cells[0] != 'Citations':
        raise ValueError('Google Scholar citation table absent (blocked, incomplete, or changed page)')
    number = parser.cells[1].replace(',', '')
    if not re.fullmatch(r'[0-9]+', number):
        raise ValueError('Google Scholar returned an invalid citation total')
    return int(number)


def fetch_total(author_id):
    url = 'https://scholar.google.com/citations?' + urlencode({'user': author_id, 'hl': 'en'})
    # A single public profile request avoids scholarly's extra requests and hidden retries.
    result = subprocess.run([
        'curl', '--silent', '--show-error', '--fail-with-body', '--location',
        '--connect-timeout', '10', '--max-time', '30',
        '--user-agent', 'Mozilla/5.0', url,
    ], capture_output=True, text=True, encoding='utf-8', timeout=40)
    if result.returncode:
        raise RuntimeError('Scholar request failed: ' + result.stderr.strip())
    return parse_total(result.stdout)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, default=Path('dist/assets/gs_data.json'))
    args = parser.parse_args()
    author_id = os.environ.get('GOOGLE_SCHOLAR_ID', 'aEts7nUAAAAJ')
    try:
        total = fetch_total(author_id)
        data = {'scholar_id': author_id, 'citedby': total,
                'updated': datetime.now(timezone.utc).isoformat(), 'source': 'Google Scholar'}
        save(data, args.output, author_id)
    except (RuntimeError, ValueError, subprocess.TimeoutExpired) as exc:
        print(str(exc), flush=True)
        raise SystemExit(1)
    print('Updated Google Scholar citation total:', data['citedby'], flush=True)


if __name__ == '__main__':
    main()
