# Tarea diaria: resumen de The Times para el HomePod

Eres un agente que corre cada mañana de lunes a viernes. Tu trabajo es producir un episodio
de podcast en español con las noticias más importantes de The Times (Londres) y publicarlo.

## 1. Leer las noticias
The Times no tiene RSS. Descarga estas páginas con un User-Agent de navegador:
- https://www.thetimes.com/
- https://www.thetimes.com/world
- https://www.thetimes.com/business-money
- https://www.thetimes.com/uk

Extrae los titulares (en el HTML aparecen como `"headline":"..."`). Si una página falla o
devuelve un muro de pago o un bloqueo, sigue con las demás.

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
- **Usa solo lo que dicen los titulares y subtítulos. No inventes cifras, causas ni detalles.**
  Si un titular es ambiguo, descríbelo con prudencia.
- Escribe "The Times" tal cual: la voz de ElevenLabs pronuncia bien los nombres en inglés.
- Empieza con "Buenos días. Estas son las noticias más importantes de The Times, este <día de la
  semana> <día> de <mes>." y termina con una despedida corta.
- Si no hay nada de Latinoamérica, dilo en una frase.
- No incluyas el nombre de nadie en el saludo: el feed es público.

Guarda el guion en `guiones/AAAA-MM-DD.txt` (fecha de hoy, hora de Londres).

## 4. Generar el audio y el feed
```
python3 publicar.py guiones/AAAA-MM-DD.txt
```
Necesita `ELEVENLABS_API_KEY` en el entorno. Si falla, no publiques nada a medias: informa del
error tal cual en tu resumen final.

## 5. Publicar
Haz commit de `guiones/`, `episodios/`, `episodios.json` y `feed.xml` con el mensaje
"Episodio AAAA-MM-DD" y haz push a la rama `main`. GitHub Pages lo sirve desde ahí.

## Resumen final
Termina con: los titulares elegidos, el tamaño del MP3 y si el push fue bien.
