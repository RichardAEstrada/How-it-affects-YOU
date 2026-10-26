from html.parser import HTMLParser
from pathlib import Path
import unittest
class Page(HTMLParser):
 def __init__(self):super().__init__();self.select=None;self.options={};self.ids=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if a.get('id'):self.ids.append(a['id'])
  if tag=='select':self.select=a.get('id');self.options[self.select]=[]
  if tag=='option' and self.select:self.options[self.select].append(a.get('value'))
 def handle_endtag(self,tag):
  if tag=='select':self.select=None
class MarkupTests(unittest.TestCase):
 def setUp(self):self.page=Page();self.page.feed((Path(__file__).parents[1]/'index.html').read_text())
 def test_all_provider_options_are_real_elements(self):self.assertEqual(self.page.options['internetProvider'],['','att','spectrum','frontier','other'])
 def test_ids_are_unique(self):self.assertEqual(len(self.page.ids),len(set(self.page.ids)))
 def test_all_five_publishers_are_selectable(self):self.assertEqual(set(self.page.options['publisherFilter']),{'all','npr','bbc','guardian','fox','nbc'})
if __name__=='__main__':unittest.main()
