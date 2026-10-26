#!/usr/bin/env python3
"""Fetch public publisher RSS independently; publish an honest same-origin snapshot.
No proxy, API key, accounts, article bodies, or private user data are used.
"""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta
from email.utils import parsedate_to_datetime
from html import unescape
import json
import os
from pathlib import Path
import re
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

SOURCES = [
    dict(id='npr', name='NPR News', url='https://feeds.npr.org/1001/rss.xml'),
    dict(id='guardian', name='The Guardian', url='https://www.theguardian.com/world/rss'),
    dict(id='bbc', name='BBC World', url='https://feeds.bbci.co.uk/news/world/rss.xml'),
    dict(id='fox', name='Fox News', url='https://moxie.foxnews.com/google-publisher/latest.xml'),
    dict(id='nbc', name='NBCNews.com', url='https://feeds.nbcnews.com/nbcnews/public/news'),
]
MAX_BYTES = 4 * 1024 * 1024

def stamp(dt):
    return dt.astimezone(timezone.utc).isoformat(timespec='seconds').replace('+00:00', 'Z')

def parse_date(value):
    try:
        dt = parsedate_to_datetime(value)
    except (ValueError, TypeError, OverflowError):
        try:
            dt = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, TypeError, AttributeError):
            return None
    return stamp(dt) if dt.tzinfo else None

def plain(value, limit=600):
    return re.sub(r'\s+', ' ', re.sub(r'<[^>]*>', '', unescape(value or ''))).strip()[:limit]

def http_url(value):
    try:
        p = urllib.parse.urlsplit(value)
        if p.scheme not in ('https', 'http') or not p.hostname or p.username or p.password:
            return None
        return urllib.parse.urlunsplit((p.scheme,p.netloc,p.path,p.query,''))
    except ValueError:
        return None

def child_text(node, names):
    for child in node:
        if child.tag.rsplit('}',1)[-1] in names:
            value = ''.join(child.itertext()).strip()
            if value:
                return value
    return ''

def parse_feed(body):
    # Reject DTD/entity declarations instead of interpreting an external payload.
    if re.search(br'<!\s*(DOCTYPE|ENTITY)', body, re.I):
        raise ValueError('XML declarations not supported')
    root = ET.fromstring(body)
    if root.tag.rsplit('}',1)[-1] not in ('rss', 'RDF', 'feed'):
        raise ValueError('Response is not RSS or Atom')
    items, seen = [], set()
    for node in root.iter():
        if node.tag.rsplit('}',1)[-1] not in ('item', 'entry'):
            continue
        title = plain(child_text(node, {'title'}))
        url = http_url(child_text(node, {'link'}))
        if not url:
            for link in node:
                if link.tag.rsplit('}',1)[-1]=='link' and link.get('rel','alternate')=='alternate':
                    url = http_url(link.get('href',''))
                    if url: break
        if not title or not url or url in seen: continue
        seen.add(url)
        topics = [plain(''.join(c.itertext()) or c.get('term',''),160) for c in node if c.tag.rsplit('}',1)[-1]=='category']
        items.append(dict(title=title,link=url,pubDate=parse_date(child_text(node,{'pubDate','published','updated','date'})),author=plain(child_text(node,{'creator','author'}),200),categories=topics[:50]))
        if len(items)>=60: break
    if not items:
        raise ValueError('Feed contained no usable linked headlines')
    return items

def fetch_feed(source):
    request = urllib.request.Request(source['url'],headers={'User-Agent':'HowItAffectsYou/1.0 (+https://richardaestrada.github.io/How-it-affects-YOU/; public RSS reader)','Accept':'application/rss+xml, application/atom+xml, application/xml, text/xml;q=0.9'})
    with urllib.request.urlopen(request,timeout=25) as response:
        body = response.read(MAX_BYTES+1)
        if len(body)>MAX_BYTES: raise ValueError('Feed exceeds size limit')
        return parse_feed(body)

def refresh_source(source, previous, now, fetcher=fetch_feed):
    result = dict(id=source['id'],name=source['name'],feed_url=source['url'],last_attempt_at=stamp(now),last_success_at=None,status='unavailable',error=None,items=[])
    try:
        result.update(items=fetcher(source),last_success_at=stamp(now),status='ok')
    except Exception as error:
        # No exception bodies or arbitrary remote HTML enter public output.
        if isinstance(error,urllib.error.HTTPError): message=f'Publisher HTTP {error.code}'
        elif isinstance(error,(TimeoutError,urllib.error.URLError)): message='Publisher connection unavailable'
        else: message='Publisher returned unusable RSS'
        result['error']=message
        if isinstance(previous,dict) and isinstance(previous.get('items'),list) and previous.get('last_success_at'):
            result.update(items=previous['items'],last_success_at=previous['last_success_at'],status='retained')
    return result

def collect(previous=None, now=None, fetcher=fetch_feed):
    now=now or datetime.now(timezone.utc)
    old={s.get('id'):s for s in (previous or {}).get('sources',[]) if isinstance(s,dict)}
    with ThreadPoolExecutor(max_workers=len(SOURCES)) as pool:
        rows=list(pool.map(lambda s:refresh_source(s,old.get(s['id']),now,fetcher),SOURCES))
    scheduled=os.environ.get('HIAY_NEWS_REFRESH_MODE')=='scheduled'
    return dict(schema_version=1,generated_at=stamp(now),refresh_mode='scheduled' if scheduled else 'manual',refresh_interval_seconds=1800 if scheduled else None,stale_after_seconds=7200,sources=rows)

def main():
    path=Path('data/news.json');path.parent.mkdir(exist_ok=True)
    try: previous=json.loads(path.read_text())
    except (OSError,ValueError): previous={}
    result=collect(previous)
    temporary=path.with_suffix('.tmp');temporary.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n');temporary.replace(path)
    for source in result['sources']:
        print(f"{source['id']}: {source['status']}; {len(source['items'])} linked headlines; last success {source['last_success_at']}")
    if all(s['status']!='ok' for s in result['sources']):
        print('::warning::No publisher refreshed. Retained data is explicitly marked; no current news was invented.')

if __name__=='__main__': main()
