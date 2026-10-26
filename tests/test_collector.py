import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch
from datetime import datetime,timezone
spec=importlib.util.spec_from_file_location('collector',Path(__file__).parents[1]/'scripts/collect_news.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
RSS=b'''<rss><channel><item><title>Flood &amp; transit</title><link>https://example.com/news</link><pubDate>Mon, 26 Oct 2026 20:00:00 GMT</pubDate><category>Weather</category></item><item><title>bad</title><link>javascript:alert(1)</link></item></channel></rss>'''
class CollectorTests(unittest.TestCase):
 def test_scheduled_collection_interval(self):
  with patch.dict(c.os.environ,{'HIAY_NEWS_REFRESH_MODE':'scheduled'}):
   result=c.collect({},datetime(2026,10,26,20,tzinfo=timezone.utc),lambda source:c.parse_feed(RSS))
  self.assertEqual(result['refresh_mode'],'scheduled');self.assertEqual(result['refresh_interval_seconds'],1800)
 def test_parse(self):
  row=c.parse_feed(RSS)[0];self.assertEqual(row['title'],'Flood & transit');self.assertEqual(row['pubDate'],'2026-10-26T20:00:00Z');self.assertEqual(row['categories'],['Weather']);self.assertEqual(len(c.parse_feed(RSS)),1)
 def test_html_rejected(self):
  with self.assertRaises(ValueError):c.parse_feed(b'<html><body>Cloudflare challenge</body></html>')
 def test_entities_rejected(self):
  with self.assertRaises(ValueError):c.parse_feed(b'<!DOCTYPE rss [<!ENTITY x SYSTEM "file:///private">]><rss/>')
 def test_unknown_date(self):
  self.assertIsNone(c.parse_date('bad'));self.assertIsNone(c.parse_date('2026-10-26 20:00:00'))
 def test_partial_and_retained(self):
  now=datetime(2026,10,26,20,tzinfo=timezone.utc)
  prior={'sources':[dict(id='npr',items=c.parse_feed(RSS),last_success_at='2026-10-26T18:00:00Z')]}
  def fake(s):
   if s['id']=='npr':raise TimeoutError()
   return c.parse_feed(RSS)
  snapshot=c.collect(prior,now,fake);a=snapshot['sources'][0]
  self.assertEqual(a['status'],'retained');self.assertEqual(a['last_success_at'],'2026-10-26T18:00:00Z');self.assertEqual(a['last_attempt_at'],'2026-10-26T20:00:00Z');self.assertEqual(sum(s['status']=='ok' for s in snapshot['sources']),4)
 def test_all_failure_never_fabricates(self):
  def fail(s):raise TimeoutError()
  snapshot=c.collect({},datetime.now(timezone.utc),fail)
  self.assertTrue(all(s['status']=='unavailable' and not s['items'] and s['last_success_at'] is None for s in snapshot['sources']))
if __name__=='__main__':unittest.main()
