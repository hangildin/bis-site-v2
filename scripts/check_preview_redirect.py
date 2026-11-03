#!/usr/bin/env python3
"""Verify that BIS V2 is a non-indexed link-preserving preview of primary BIS."""
import argparse
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.request import Request,urlopen

SRC="https://hangildin.github.io/bis-site/"
PREVIEW="https://hangildin.github.io/bis-site-v2/"
def public_url(url):
 with urlopen(Request(url,headers={"User-Agent":"BIS-PREVIEW-SEO-VERIFY/1.0"}),timeout=25) as r:
  assert r.status==200,(url,r.status)
  return r.read().decode("utf-8")
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--live",action="store_true")
 p.add_argument("--dist",type=Path,default=Path("dist"))
 a=p.parse_args()
 root=Path(__file__).resolve().parents[1]
 ns="{http://www.sitemaps.org/schemas/sitemap/0.9}"
 paths=[e.text for e in ET.parse(root/"sitemap.xml").getroot().findall(ns+"url/"+ns+"loc")]
 assert len(paths)==25 and len(set(paths))==25
 for nameurl in paths:
  assert nameurl.startswith(SRC)
  suffix=nameurl[len(SRC):]
  name=suffix or "index.html"
  data=public_url(PREVIEW+suffix) if a.live else (a.dist/name).read_text(encoding="utf-8")
  assert 'content="noindex, follow"' in data,("noindex missing",name)
  assert f'<link rel="canonical" href="{SRC+suffix}">' in data,("primary canonical missing",name)
  assert f'<meta http-equiv="refresh" content="0; url={SRC+suffix}">' in data,("redirect missing",name)
  assert f'<link rel="canonical" href="{PREVIEW+suffix}">' not in data,("duplicate canonical",name)
 if a.live:
  robots=public_url(PREVIEW+"robots.txt")
  assert "Allow: /" in robots and "Sitemap:" not in robots
 else:
  assert not (a.dist/"sitemap.xml").exists(),"Duplicate sitemap should be absent"
  assert "Sitemap:" not in (a.dist/"robots.txt").read_text(encoding="utf-8")
 print(f"BIS V2 PREVIEW CHECK PASS: {len(paths)} {'live' if a.live else 'built'} pages noindex, canonical and redirect to main BIS.")
if __name__=="__main__":main()
