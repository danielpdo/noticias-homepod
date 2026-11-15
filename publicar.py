#!/usr/bin/env python3
"""Convierte un guion en audio con OpenAI y actualiza el feed del podcast.

Uso:
  python3 publicar.py guiones/2026-11-16.txt            # genera MP3 con OpenAI
  python3 publicar.py guiones/X.txt --audio episodios/X.m4a   # usa un audio ya hecho
  python3 publicar.py --solo-feed                        # solo regenera feed.xml

Necesita la variable de entorno OPENAI_API_KEY (salvo con --audio / --solo-feed).
Solo usa la biblioteca estándar de Python.
"""
import argparse, json, os, sys, urllib.request, urllib.error
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from xml.sax.saxutils import escape

RAIZ = Path(__file__).resolve().parent
CONFIG = json.loads((RAIZ / "config.json").read_text(encoding="utf-8"))
EPISODIOS = RAIZ / "episodios"
INDICE = RAIZ / "episodios.json"
MAX_EPISODIOS = 30


def trozos(texto: str, maximo: int = 3800) -> list:
    """Divide por párrafos para no pasar el límite de 4096 caracteres de la API."""
    partes, actual = [], ""
    for parrafo in texto.split("\n\n"):
        if actual and len(actual) + len(parrafo) + 2 > maximo:
            partes.append(actual); actual = parrafo
        else:
            actual = f"{actual}\n\n{parrafo}" if actual else parrafo
    if actual:
        partes.append(actual)
    return partes


def tts_openai(texto: str, destino: Path) -> None:
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        sys.exit("Falta OPENAI_API_KEY en el entorno.")
    audio = b""
    for parte in trozos(texto):
        cuerpo = json.dumps({
            "model": CONFIG["model"],
            "voice": CONFIG["voice"],
            "input": parte,
            "instructions": CONFIG["instrucciones_voz"],
            "response_format": "mp3",
        }).encode()
        req = urllib.request.Request("https://api.openai.com/v1/audio/speech", data=cuerpo,
                                     method="POST", headers={
                                         "Authorization": f"Bearer {key}",
                                         "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=300) as r:
                audio += r.read()
        except urllib.error.HTTPError as e:
            sys.exit(f"OpenAI respondió {e.code}: {e.read().decode(errors='ignore')[:500]}")
    destino.write_bytes(audio)


def generar_feed(indice: list) -> None:
    base = CONFIG["base_url"].rstrip("/")
    items = []
    for ep in sorted(indice, key=lambda e: e["fecha"], reverse=True):
        archivo = EPISODIOS / ep["archivo"]
        tipo = "audio/mpeg" if archivo.suffix == ".mp3" else "audio/x-m4a"
        fecha = datetime.fromisoformat(ep["publicado"])
        items.append(f"""    <item>
      <title>{escape(ep['titulo'])}</title>
      <description>{escape(ep['descripcion'])}</description>
      <guid isPermaLink="false">{escape(ep['archivo'])}</guid>
      <pubDate>{format_datetime(fecha)}</pubDate>
      <enclosure url="{base}/episodios/{escape(ep['archivo'])}" length="{archivo.stat().st_size}" type="{tipo}"/>
      <itunes:duration>{ep.get('duracion', 0)}</itunes:duration>
    </item>""")
    feed = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>{escape(CONFIG['titulo'])}</title>
    <link>{base}/</link>
    <language>es</language>
    <description>{escape(CONFIG['descripcion'])}</description>
    <itunes:author>{escape(CONFIG['titulo'])}</itunes:author>
    <itunes:explicit>false</itunes:explicit>
    <itunes:block>Yes</itunes:block>
{chr(10).join(items)}
  </channel>
</rss>
"""
    (RAIZ / "feed.xml").write_text(feed, encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("guion", nargs="?")
    p.add_argument("--audio", help="audio ya generado (omite OpenAI)")
    p.add_argument("--solo-feed", action="store_true")
    a = p.parse_args()

    indice = json.loads(INDICE.read_text(encoding="utf-8")) if INDICE.exists() else []

    if not a.solo_feed:
        guion = Path(a.guion)
        fecha = guion.stem  # AAAA-MM-DD
        texto = guion.read_text(encoding="utf-8").strip()
        EPISODIOS.mkdir(exist_ok=True)
        if a.audio:
            destino = Path(a.audio)
        else:
            destino = EPISODIOS / f"{fecha}.mp3"
            tts_openai(texto, destino)
        primera = next((l for l in texto.splitlines() if l.strip()), "")
        indice = [e for e in indice if e["fecha"] != fecha]
        indice.append({
            "fecha": fecha,
            "archivo": destino.name,
            "titulo": f"Noticias del {fecha}",
            "descripcion": texto[:600],
            "publicado": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "duracion": round(len(texto.split()) / 2.6),  # aprox. segundos
        })
        # Conserva solo los últimos MAX_EPISODIOS
        indice.sort(key=lambda e: e["fecha"])
        for viejo in indice[:-MAX_EPISODIOS]:
            (EPISODIOS / viejo["archivo"]).unlink(missing_ok=True)
        indice = indice[-MAX_EPISODIOS:]
        INDICE.write_text(json.dumps(indice, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Episodio {fecha}: {destino} ({destino.stat().st_size} bytes)")

    generar_feed(indice)
    print("feed.xml actualizado")


if __name__ == "__main__":
    main()
