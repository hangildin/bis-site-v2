#!/usr/bin/env python3
"""Make the former BIS V2 Pages address a non-indexed redirect to BIS primary.

GitHub Pages does not expose an HTTP 301 configuration for this project.
A zero-second HTML refresh and canonical/noindex preserve visitor access while
preventing a second indexed set of 25 duplicate articles and service pages.
"""
from pathlib import Path
import argparse,re
import xml.etree.ElementTree as ET

SRC="https://hangildin.github.io/bis-site-v2/"
PRIMARY="https://hangildin.github.io/bis-site/"
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--dist",type=Path,default=Path("dist"))
 a=p.parse_args()
 root=a.dist
 sitemap=root/"sitemap.xml"
 assert sitemap.exists(),"Expected staged sitemap"
 ns="{http://www.sitemaps.org/schemas/sitemap/0.9}"
 urls=[e.text for e in ET.parse(sitemap).getroot().findall(ns+"url/"+ns+"loc")]
 assert len(urls)==25 and all(x.startswith(SRC) for x in urls),"Expected complete V2 public site"
 for url in urls:
  name=url[len(SRC):] or "index.html"
  path=root/name
  data=path.read_text(encoding="utf-8")
  assert 'content="noindex' not in data,("Unexpected staged noindex",name)
  assert f'<link rel="canonical" href="{url}">' in data,("Missing staging canonical",name)
  newurl=PRIMARY+url[len(SRC):]
  data=data.replace(f'<link rel="canonical" href="{url}">',f'<link rel="canonical" href="{newurl}">')
  data=data.replace(f'<meta property="og:url" content="{url}">',f'<meta property="og:url" content="{newurl}">')
  inject=f'<meta name="robots" content="noindex, follow"><meta http-equiv="refresh" content="0; url={newurl}">'
  assert "</head>" in data,("Page missing head",name)
  data=data.replace("</head>",inject+"</head>",1)
  path.write_text(data,encoding="utf-8")
 # Do not advertise a duplicate sitemap; let crawlers see the noindex+canonical.
 sitemap.unlink()
 (root/"robots.txt").write_text("User-agent: *\nAllow: /\n",encoding="utf-8")
 print(f"BIS PREVIEW DEINDEX PASS: {len(urls)} V2 pages now direct visitors and search engines to {PRIMARY}")
if __name__=="__main__":main()
