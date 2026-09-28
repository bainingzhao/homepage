"""Fetch only the public author citation total, preserving last good data on failure."""
import argparse
from datetime import datetime, timezone
import json
import os
import re
import subprocess
import tempfile
from html.parser import HTMLParser
from urllib.parse import urlencode, urlsplit
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


def diagnostics(meta, headers, body, exit_code):
    # Emit only known error phrases, never raw HTML, cookies, IPs or query tokens.
    parts = urlsplit(meta.get('url_effective', ''))
    path = parts.path if parts.path in ('/citations', '/sorry/index', '/sorry/', '/') else '/[path omitted]'
    final_url = parts.scheme + '://' + (parts.hostname or '') + path if parts.hostname else ''
    allowed_headers = {}
    statuses = []
    for line in headers.splitlines():
        if line.startswith('HTTP/'):
            fields = line.split()
            if len(fields) > 1 and fields[1].isdigit():
                statuses.append(int(fields[1]))
            allowed_headers = {}
        elif ':' in line:
            key, value = line.split(':', 1)
            key, value = key.lower().strip(), value.strip()
            if key in ('content-type', 'server') and re.fullmatch(r'[a-zA-Z0-9 /.;=_-]{1,100}', value):
                allowed_headers[key] = value
            elif key == 'retry-after' and value.isdigit():
                allowed_headers[key] = value
    plain = re.sub(r'<[^>]*>', ' ', body).lower()
    phrases = ['unusual traffic', 'automated queries', 'captcha', 'recaptcha',
               'access denied', 'forbidden', 'permission to access',
               'temporarily blocked', 'rate limit', 'not a robot']
    signals = [phrase for phrase in phrases if phrase in plain or phrase in body.lower()]
    report = {
        'http_status': meta.get('http_code'), 'redirect_statuses': statuses,
        'final_url_without_query': final_url, 'headers': allowed_headers,
        'curl_exit_code': exit_code, 'seconds': meta.get('time_total'),
        'body_bytes': len(body.encode('utf-8')), 'error_page_signals': signals,
        'citation_table_present': 'gsc_rsb_st' in body,
        'summary': '; '.join(signals) if signals else 'No recognized error phrase; raw response omitted for privacy.',
    }
    print('Scholar diagnostic: ' + json.dumps(report, ensure_ascii=True), flush=True)
    return report


def fetch_total(author_id):
    url = 'https://scholar.google.com/citations?' + urlencode({'user': author_id, 'hl': 'en'})
    with tempfile.TemporaryDirectory() as folder:
        body_path, headers_path = Path(folder)/'body', Path(folder)/'headers'
        try:
            result = subprocess.run([
                'curl', '--silent', '--show-error', '--fail-with-body', '--location',
                '--connect-timeout', '10', '--max-time', '30',
                '--user-agent', 'Mozilla/5.0', '--output', str(body_path),
                '--dump-header', str(headers_path), '--write-out', '%{json}', url,
            ], capture_output=True, text=True, encoding='utf-8', timeout=40)
        except subprocess.TimeoutExpired:
            diagnostics({}, '', '', 'process-timeout')
            raise RuntimeError('Scholar request exceeded process timeout; existing data retained')
        body = body_path.read_text(encoding='utf-8', errors='replace') if body_path.exists() else ''
        headers = headers_path.read_text(encoding='utf-8', errors='replace') if headers_path.exists() else ''
        try:
            meta = json.loads(result.stdout)
        except (ValueError, TypeError):
            meta = {}
        if result.returncode:
            diagnostics(meta, headers, body, result.returncode)
            raise RuntimeError('Scholar request failed; see sanitized diagnostic above')
        try:
            total = parse_total(body)
        except ValueError:
            diagnostics(meta, headers, body, result.returncode)
            raise
        print('Scholar HTTP status:', meta.get('http_code'), flush=True)
        return total


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
