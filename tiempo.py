#!/usr/bin/env python3
"""Imprime el tiempo de hoy en Londres (Open-Meteo, sin API key) como datos para el guion."""
import json, urllib.request, urllib.error

URL = ("https://api.open-meteo.com/v1/forecast?latitude=51.5074&longitude=-0.1278"
       "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max"
       "&hourly=temperature_2m,precipitation_probability,precipitation"
       "&timezone=Europe%2FLondon&forecast_days=1")

import time
for intento in range(4):  # Open-Meteo a veces responde 429 desde IPs compartidas de la nube
    try:
        d = json.load(urllib.request.urlopen(URL, timeout=30))
        break
    except urllib.error.HTTPError as e:
        if e.code != 429 or intento == 3:
            raise
        time.sleep(20 * (intento + 1))
dia, h = d["daily"], d["hourly"]
horas = [t[11:16] for t in h["time"]]
temp_8 = h["temperature_2m"][horas.index("08:00")]

# Horas (07:00–23:00) con probabilidad de lluvia >= 50 % o lluvia >= 0,2 mm
lluvia = [hr for hr, p, mm in zip(horas, h["precipitation_probability"], h["precipitation"])
          if "07:00" <= hr <= "23:00" and ((p or 0) >= 50 or (mm or 0) >= 0.2)]

# Agrupa horas consecutivas en tramos
tramos, ini, prev = [], None, None
for hr in lluvia:
    n = int(hr[:2])
    if ini is None:
        ini = prev = n
    elif n == prev + 1:
        prev = n
    else:
        tramos.append((ini, prev + 1)); ini = prev = n
if ini is not None:
    tramos.append((ini, prev + 1))

print(f"Temperatura a las 8:00: {round(temp_8)} °C")
print(f"Máxima: {round(dia['temperature_2m_max'][0])} °C")
print(f"Mínima: {round(dia['temperature_2m_min'][0])} °C")
print(f"Probabilidad máxima de lluvia: {dia['precipitation_probability_max'][0]} %")
print(f"Lluvia total prevista: {dia['precipitation_sum'][0]} mm")
if tramos:
    print("Lluvia probable entre: " + ", ".join(f"{a}:00 y {b}:00" for a, b in tramos))
else:
    print("Lluvia probable entre: ninguna hora (no se espera lluvia)")
