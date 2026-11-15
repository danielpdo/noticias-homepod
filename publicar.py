#!/usr/bin/env python3
"""Convierte un guion en audio con ElevenLabs y actualiza el feed del podcast.

Uso:
  python3 publicar.py guiones/2026-11-16.txt            # genera MP3 con ElevenLabs
  python3 publicar.py guiones/X.txt --audio episodios/X.m4a   # usa un audio ya hecho
  python3 publicar.py --solo-feed                        # solo regenera feed.xml

Necesita la variable de entorno ELEVENLABS_API_KEY (salvo con --audio / --solo-feed).
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


def tts_elevenlabs(texto: str, destino: Path) -> None:
    key = os.environ.get("ELEVENLABS_API_KEY")
    if not key:
        sys.exit("Falta ELEVENLABS_API_KEY en el entorno.")
    url = (f"https://api.elevenlabs.io/v1/text-to-speech/{CONFIG['voice_id']}"
           f"?output_format=mp3_44100_128")
    cuerpo = json.dumps({
        "text": texto,
        "model_id": CONFIG.get("model_id", "eleven_multilingual_v2"),
        "language_code": "es",
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.75},
    }).encode()
    req = urllib.request.Request(url, data=cuerpo, method="POST", headers={
        "xi-api-key": key, "Content-Type": "application/json", "Accept": "audio/mpeg"})
    try:
        with urllib.request.urlopen(req, timeout=180) as r:
            destino.write_bytes(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f"ElevenLabs respondió {e.code}: {e.read().decode(errors='ignore')[:500]}")


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
    p.add_argument("--audio", help="audio ya generado (omite ElevenLabs)")
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
            tts_elevenlabs(texto, destino)
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
