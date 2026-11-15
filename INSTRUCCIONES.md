# Tarea diaria: resumen de The Times para el HomePod

Eres un agente que corre cada mañana de lunes a viernes. Tu trabajo es producir un episodio
de podcast en español con las noticias más importantes de The Times (Londres) y publicarlo.

Hazlo siempre que te ejecuten, sea el día que sea (también en pruebas manuales en fin de
semana). Si ya existe un episodio con la fecha de hoy, **regenéralo y reemplázalo**:
`publicar.py` sustituye la entrada del feed y borra el audio anterior. El feed solo guarda el episodio más reciente.

## 1. Leer las noticias
Ejecuta `python3 titulares.py`. Lista los titulares de The Times de las últimas ~24 horas,
por sección, sacados del RSS público de Google News, con su hora de publicación.

**No descargues thetimes.com directamente.** Muestra una verificación anti-bot a los
servidores en la nube, y no hay que intentar saltársela. Si `titulares.py` falla del todo,
no publiques nada y explica el error.

Ignora entradas que no sean noticias, como nombres de sección ("World News") o páginas
genéricas.

## 1b. El tiempo en Londres
Ejecuta `python3 tiempo.py`. Te da la temperatura a las 8:00, la máxima, la mínima y las horas
con lluvia probable. Si falla, omite el bloque del tiempo y sigue.

## 2. Elegir las noticias
Unas 10 noticias, en este orden de prioridad:
1. Lo más importante de la portada.
2. Internacional, incluida Latinoamérica y España si aparecen.
3. Economía y negocios.
4. Tecnología.
Evita deportes, sociedad, cultura y columnas de opinión, salvo que sean la gran noticia del día.

## 3. Escribir el guion
- Español natural, para escuchar, no para leer: frases cortas y transiciones ("Pasamos a economía").
- Unas 350 a 400 palabras (unos 2,5 minutos).
- **Usa solo lo que dicen los titulares. No inventes cifras, causas ni detalles.**
  Si un titular es ambiguo, descríbelo con prudencia.
- Escribe "The Times" tal cual: la voz de OpenAI pronuncia bien los nombres en inglés.
- Empieza con "Buenos días. Estas son las noticias más importantes de The Times, este <día de la
  semana> <día> de <mes>." y termina con una despedida corta.
- Justo después del saludo, el tiempo en Londres en dos o tres frases: temperatura ahora,
  máxima y mínima, y si va a llover y a qué horas ("Se espera lluvia entre las once y las
  cinco de la tarde, así que lleva paraguas"). Escribe las horas en palabras, en formato de
  12 horas ("las cinco de la tarde"). Si no se espera lluvia, dilo.
- Si no hay nada de Latinoamérica, dilo en una frase.
- No incluyas el nombre de nadie en el saludo: el feed es público.

Guarda el guion en `guiones/AAAA-MM-DD.txt` (fecha de hoy, hora de Londres).

## 4. Generar el audio y el feed
```
python3 publicar.py guiones/AAAA-MM-DD.txt
```
Necesita `OPENAI_API_KEY` en el entorno. Si falla, no publiques nada a medias: informa del
error tal cual en tu resumen final.

## 5. Publicar
Haz commit de `guiones/`, `episodios/`, `episodios.json` y `feed.xml` con el mensaje
"Episodio AAAA-MM-DD" y haz push a la rama `main`. GitHub Pages lo sirve desde ahí.

## Resumen final
Termina con: los titulares elegidos, el tamaño del MP3 y si el push fue bien.
