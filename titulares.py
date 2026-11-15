#!/usr/bin/env python3
"""Titulares recientes de The Times a través del RSS público de Google News.

thetimes.com muestra una verificación anti-bot a los servidores en la nube, así que usamos
Google News, que indexa los artículos de The Times con su titular y hora de publicación.
Imprime una lista por sección, sin duplicados, de las últimas ~24 horas.
"""
import urllib.parse, urllib.request, xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime

SECCIONES = {
    "Portada / general": "site:thetimes.com",
    "Internacional": "site:thetimes.com/world",
    "Economía y negocios": "site:thetimes.com/business-money",
    "Tecnología": "site:thetimes.com technology OR AI",
    "Latinoamérica / España": "site:thetimes.com (Latin America OR Mexico OR Brazil OR Argentina OR Peru OR Colombia OR Chile OR Venezuela OR Spain)",
}
RUIDO = ("Latest news & breaking headlines", "Recipes", "crossword", "Puzzles", "horoscope")

vistos = set()
for seccion, q in SECCIONES.items():
    url = ("https://news.google.com/rss/search?" +
           urllib.parse.urlencode({"q": q + " when:1d", "hl": "en-GB", "gl": "GB", "ceid": "GB:en"}))
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        raiz = ET.fromstring(urllib.request.urlopen(req, timeout=30).read())
    except Exception as e:
        print(f"\n## {seccion}: error ({e})")
        continue
    print(f"\n## {seccion}")
    n = 0
    for item in raiz.findall(".//item"):
        titulo = (item.findtext("title") or "").removesuffix(" - The Times").strip()
        if not titulo or titulo in vistos or any(r.lower() in titulo.lower() for r in RUIDO):
            continue
        vistos.add(titulo)
        hora = parsedate_to_datetime(item.findtext("pubDate")).strftime("%d/%m %H:%M")
        print(f"- [{hora}] {titulo}")
        n += 1
        if n >= 25:
            break
