#!/usr/bin/env python3
"""Imprime el tiempo de hoy en Londres como datos para el guion.

Fuente principal: met.no (servicio meteorológico noruego, gratis, sin API key).
Si falla, prueba con Open-Meteo (que a veces responde 429 desde la nube).
"""
import json, time, urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo

LON = ZoneInfo("Europe/London")
UA = {"User-Agent": "noticias-homepod/1.0"}


def get(url):
    for intento in range(3):
        try:
            return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))
        except Exception:
            if intento == 2:
                raise
            time.sleep(10 * (intento + 1))


def desde_metno():
    d = get("https://api.met.no/weatherapi/locationforecast/2.0/compact?lat=51.51&lon=-0.13")
    hoy = datetime.now(LON).date()
    horas = []
    for p in d["properties"]["timeseries"]:
        t = datetime.fromisoformat(p["time"].replace("Z", "+00:00")).astimezone(LON)
        if t.date() != hoy or "next_1_hours" not in p["data"]:
            continue
        horas.append((t.hour, p["data"]["instant"]["details"]["air_temperature"],
                      p["data"]["next_1_hours"]["details"].get("precipitation_amount", 0)))
    return horas


def desde_openmeteo():
    d = get("https://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=-0.1278"
            "&hourly=temperature_2m,precipitation&timezone=Europe%2FLondon&forecast_days=1")
    h = d["hourly"]
    return [(int(t[11:13]), temp, mm) for t, temp, mm in
            zip(h["time"], h["temperature_2m"], h["precipitation"])]


try:
    horas, fuente = desde_metno(), "met.no"
except Exception:
    horas, fuente = desde_openmeteo(), "Open-Meteo"

temps = [t for _, t, _ in horas]
temp_8 = next((t for hr, t, _ in horas if hr == 8), temps[0])
lluvia = [hr for hr, _, mm in horas if 7 <= hr <= 23 and mm >= 0.2]

tramos = []
for hr in lluvia:
    if tramos and hr == tramos[-1][1]:
        tramos[-1][1] = hr + 1
    else:
        tramos.append([hr, hr + 1])

print(f"(fuente: {fuente})")
print(f"Temperatura a las 8:00: {round(temp_8)} °C")
print(f"Máxima: {round(max(temps))} °C")
print(f"Mínima: {round(min(temps))} °C")
print(f"Lluvia total prevista (7–23 h): {round(sum(mm for hr, _, mm in horas if 7 <= hr <= 23), 1)} mm")
if tramos:
    print("Lluvia probable entre: " + ", ".join(f"{a}:00 y {b}:00" for a, b in tramos))
else:
    print("Lluvia probable entre: ninguna hora (no se espera lluvia)")
