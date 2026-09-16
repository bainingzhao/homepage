"""Render the English academic homepage. Content is kept separate for future localization."""
from pathlib import Path
import json
import hashlib
from urllib.parse import urlsplit
from html import escape as e

ROOT=Path(__file__).resolve().parent
d=json.loads((ROOT/'content-en.json').read_text(encoding='utf-8'))

def author_line(value):
    names=[name.strip() for name in value.split(',')]
    shown=[]
    for name in names:
        parts=name.split()
        abbreviated=e(parts[-1]+' '+''.join(part[0] for part in parts[:-1]))
        shown.append('<strong>'+abbreviated+'</strong>' if name=='Baining Zhao' else abbreviated)
    return ', '.join(shown)

def resource_link(label,url):
    host=urlsplit(url).netloc
    detail={'Project':'Website','Platform':'Website','Code':'GitHub','Dataset':'Hugging Face','Simulator':'Download','PDF':'Download','BibTeX':'Cite'}.get(label,'Read')
    if label=='arXiv':
        detail=urlsplit(url).path.rstrip('/').split('/')[-1]
    elif label=='Paper':
        detail='arXiv' if host=='arxiv.org' else 'ACM' if '10.1145/' in url else 'ACL' if host=='aclanthology.org' else 'DOI' if host=='doi.org' else 'Journal'
    link=f'<a class="flat-badge flat-{label.lower()}" href="{e(url)}" aria-label="{e(label)}: {e(detail)}"><span class="badge-key">{e(label)}</span><span class="badge-value">{e(detail)}</span></a>'
    if label=='Code' and host=='github.com':
        repo=urlsplit(url).path.strip('/').removesuffix('.git')
        if len(repo.split('/'))==2:
            badge=f'https://img.shields.io/github/stars/{repo}?style=social&label=Stars'
            link+=f'<a class="github-stars" href="{e(url)}" aria-label="GitHub stars for {e(repo)}"><img src="{e(badge)}" alt="GitHub Stars" height="18" loading="lazy" decoding="async"></a>'
    return link

def paper(p):
    authors=author_line(p['authors'])
    links=''.join(resource_link(label,url) for label,url in p['links'].items())
    venue=f'<p class="publication-venue"><em>{e(p["venue"])}</em> {p["year"]}'+(' · '+e(p['note']) if p.get('note') and 'submission' not in p['note'].lower() else '')+'</p>'
    media=p.get('media')
    if media:
        figure=f'<img src="{e(media["image"])}" alt="{e(media["alt"])}" loading="lazy" decoding="async" width="500" height="300">'
        if media.get('video'):
            visual=f'<video controls autoplay loop muted playsinline preload="metadata" poster="{e(media.get("poster",media["image"]))}" aria-label="{e(media.get("video_alt",media["alt"]))} — video demo"><source src="{e(media["video"])}" type="video/mp4"><a href="{e(media["video"])}">Watch video demo</a></video>'
            caption=f'<a href="{e(media["video"])}" target="_blank" rel="noopener">Click to enlarge ↗</a>'
        else:
            visual=f'<a class="figure-link" href="{e(media["image"])}" target="_blank" rel="noopener" aria-label="View full-size figure: {e(p["title"])}">{figure}</a>'
            caption=f'<a href="{e(media["image"])}" target="_blank" rel="noopener">Click to enlarge ↗</a>'
            if media.get('caption'):
                caption+='<span>'+e(media['caption'])+'</span>' 
        frame_class='media-frame video-frame' if media.get('video') else 'media-frame'
        left=f'<figure class="publication-visual"><div class="{frame_class}">{visual}</div><figcaption>{caption}</figcaption></figure>'
    else:
        left=''
    return f'''<article class="paper-box" id="{p['id']}">{left}<div class="paper-box-text"><h3><a href="{e(p['links']['Paper'])}">{e(p['title'])}</a></h3><p class="authors">{authors}</p>{venue}<div class="paper-links">{links}</div></div></article>'''
def timeline(items):
    return ''.join(f'<article class="timeline-item"><h3>{e(x["title"])}</h3><time>{e(x["date"])}</time><p class="degree">{e(x["subtitle"])}</p><p>{e(x["text"])}</p></article>' for x in items)

def education():
    items=[]
    for x in d['education']:
        lines=f'<p><strong>Major:</strong> {e(x["major"])}'+('; Rank: '+e(x['rank']) if x.get('rank') else '')+'</p>'
        if x.get('research'):
            lines+=f'<p><strong>Research:</strong> {e(x["research"])}</p>'
        lines+=f'<p><strong>Honors:</strong> {e(x["honors"])}</p>'
        items.append(f'<article class="education-item"><div class="education-heading"><h3>{e(x["title"])} <span lang="zh-CN">{e(x["chinese_name"])}</span> <span>({e(x["degree"])})</span></h3><time>{e(x["date"])}</time></div>{lines}</article>')
    return ''.join(items)
def section(id,title,body):
    return f'<section class="section" id="{id}" aria-labelledby="{id}-title"><div class="section-title"><h2 id="{id}-title">{title}</h2></div>{body}</section>'

def bibliography():
    blocks=[]
    next_number=1
    for working in [False,True]:
        entries=[p for p in d['bibliography'] if p.get('working',False)==working]
        blocks.append('<div class="bibliography-category">'+('<h3>Working Papers</h3>' if working else ''))
        blocks.append(f'<ol class="bibliography-list" start="{next_number}">')
        next_number+=len(entries)
        for p in entries:
            authors=[]
            for name in p['authors'].split(', '):
                surname,initials=name.rsplit(' ',1)
                text=e(' '.join(i+'.' for i in initials)+' '+surname)
                authors.append('<strong>'+text+'</strong>' if name=='Zhao B' else text)
            title=e(p['title'])
            if p.get('url'):
                title=f'<a href="{e(p["url"])}">{title}</a>'
            year=f' ({p["year"]}).' if p.get('year') else '.'
            venue=f' <em>{e(p["venue"])}</em>' if p.get('venue') else ''
            details=', '+e(p['details']) if p.get('details') else ''
            note=f' <span class="bibliography-note">({e(p["note"])})</span>' if p.get('note') and 'submission' not in p['note'].lower() else ''
            rating=p.get('rating')
            if rating:
                note+=f' <a class="bibliography-note venue-rating" href="{e(rating["source"])}" title="{e(rating["basis"])}">({e(rating["label"])})</a>'
            blocks.append(f'<li>{", ".join(authors)}{year} <span class="bibliography-paper-title">{title}.</span>{venue}{details}.{note}</li>')
        blocks.append('</ol></div>')
    return section('all-publications','All Publications',''.join(blocks))

def collaborations():
    cards=[]
    for item in d['collaborations']:
        name=e(item['partner'])
        video=e(item['video'])
        poster=e(item['poster'])
        publication=next(p for p in d['bibliography'] if p['title'].startswith(item['paper_prefix']))
        authors=', '.join('<strong>'+e(n)+'</strong>' if n=='Zhao B' else e(n) for n in publication['authors'].split(', '))
        paper_title=e(publication['title'])
        if publication.get('url'):
            paper_title=f'<a href="{e(publication["url"])}">{paper_title}</a>'
        display_venue=e(item.get('display_venue',publication['note']))
        if item.get('display_year'):
            display_venue=f'<em>{display_venue}</em> {item["display_year"]}'
        cards.append(f'<article class="paper-box collaboration-card"><figure class="publication-visual"><div class="media-frame video-frame"><video controls autoplay loop muted playsinline preload="metadata" poster="{poster}" aria-label="{name} collaboration demo"><source src="{video}" type="video/mp4"><a href="{video}">Watch Demo</a></video></div><figcaption><a href="{video}" target="_blank" rel="noopener">Click to enlarge ↗</a></figcaption></figure><div class="paper-box-text"><h3>{e(item["title"])}</h3><p class="collaboration-paper-title">{paper_title}</p><p class="authors">{authors}</p><p class="publication-venue">{display_venue}</p></div></article>')
    return section('industry-collaborations','Selected Industry Collaboration Projects',''.join(cards))

scholar='https://scholar.google.com/citations?user=aEts7nUAAAAJ&amp;hl=en'
icon='<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M4 5h16v14H4zM4 5l8 7 8-7"/></svg>'
style_version=hashlib.sha256((ROOT/'dist/assets/style.css').read_bytes()).hexdigest()[:12]
html=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Baining Zhao · 赵柏宁 | Tsinghua University</title><meta name="description" content="Baining Zhao is a Ph.D. student at Tsinghua University studying embodied spatial intelligence, world models, and reinforcement learning for aerial navigation.">
<meta property="og:title" content="Baining Zhao | Academic Homepage"><meta property="og:description" content="Embodied spatial intelligence, world models, and learning to reason and act."><meta property="og:type" content="website">
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='12' fill='%23244d72'/%3E%3Ctext x='32' y='44' text-anchor='middle' fill='white' font-size='36' font-family='Georgia'%3EB%3C/text%3E%3C/svg%3E"><link rel="stylesheet" href="assets/style.css?v={style_version}"></head>
<body><a class="skip" href="#about-me">Skip to content</a><header class="masthead"><div class="masthead-inner"><a class="brand" href="#about-me">Homepage</a><nav aria-label="Main navigation"><a href="#about-me">About</a><a href="#publications">Highlights</a><a href="#industry-collaborations">Collaborations</a><a href="#education">Education</a><a href="#all-publications">All Publications</a></nav></div></header>
<div class="layout"><aside class="sidebar" aria-label="Profile"><div class="portrait"><img src="assets/portrait-6e569de00f.jpg" alt="Baining Zhao at ACL 2025 in Vienna" width="711" height="745"></div><h1>Baining Zhao</h1><p class="chinese" lang="zh-CN">赵柏宁</p><p class="role">Ph.D. Student</p><p class="affiliation">Tsinghua University</p><div class="profile-links"><a href="{scholar}"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m2 9 10-5 10 5-10 5zM6 11v7q6 4 12 0v-7M22 9v9"/></svg>google scholar<span class="citation-badge" title="Google Scholar total citations; {e(d['scholar_metrics'].get('updated') or 'count not yet verified')}"><span>Citations</span><b>{d['scholar_metrics']['total_citations'] if d['scholar_metrics']['total_citations'] is not None else '—'}</b></span></a><a class="email" href="mailto:zbn22@mails.tsinghua.edu.cn">{icon}zbn22@mails.tsinghua.edu.cn</a><a href="tel:+8615915005265"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 3h4l2 5-3 2a15 15 0 0 0 6 6l2-3 5 2v4a2 2 0 0 1-2 2C10 21 3 14 3 5a2 2 0 0 1 2-2z"/></svg>+86 159 1500 5265</a></div></aside>
<main><section class="intro" id="about-me" aria-labelledby="about-title"><h2 id="about-title">About Me</h2>{''.join('<p>'+p+'</p>' for p in d['about'])}<div class="topics" aria-label="Research interests">{''.join('<span>'+e(t)+'</span>' for t in d['topics'])}</div></section>
<section class="section" id="publications" aria-labelledby="publications-title"><div class="section-title"><h2 id="publications-title">Research Highlights</h2></div>{''.join(paper(p) for p in d['papers'] if not p.get('earlier'))}</section>
{collaborations()}
{section('education','Education',education())}
{section('academic-service','Academic Service','<p><strong>'+e(d['academic_service']['role'])+':</strong> '+e(', '.join(d['academic_service']['venues'][:-1]))+', and '+e(d['academic_service']['venues'][-1])+', among others.</p>')}
{bibliography()}
</main></div><script src="assets/scholar.js" defer></script></body></html>'''
(ROOT/'dist/index.html').write_text(html,encoding='utf-8')
print('Rendered dist/index.html with',len(d['papers']),'selected publications.')
