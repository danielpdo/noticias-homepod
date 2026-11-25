#!/usr/bin/env python3
"""Tipo de cambio de la libra frente al dólar y al euro (Frankfurter, datos del BCE, sin API key).

Imprime el último valor publicado y la variación frente al día hábil anterior.
El BCE publica una vez al día (hacia las 16:00 CET), así que por la mañana el dato es el
del día hábil anterior.
"""
import json, time, urllib.request
from datetime import date, timedelta


def get(url):
    for intento in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "noticias-homepod/1.0"})
            return json.load(urllib.request.urlopen(req, timeout=30))
        except Exception:
            if intento == 2:
                raise
            time.sleep(10 * (intento + 1))


desde = (date.today() - timedelta(days=10)).isoformat()
d = get(f"https://api.frankfurter.app/{desde}..?from=GBP&to=USD,EUR")
fechas = sorted(d["rates"])
hoy, ayer = d["rates"][fechas[-1]], d["rates"][fechas[-2]]

print(f"Fecha del dato (BCE): {fechas[-1]}")
for moneda, nombre in (("USD", "dólares"), ("EUR", "euros")):
    v, a = hoy[moneda], ayer[moneda]
    cambio = (v - a) / a * 100
    tendencia = "sube" if cambio > 0.05 else "baja" if cambio < -0.05 else "se mantiene estable"
    print(f"1 libra = {v:.4f} {nombre} ({tendencia}, {cambio:+.2f} % frente a {fechas[-2]})")
