# crowler-find-email
buscar email en  todos los directoiros de la web

# Super Email Crawler 

Este proyecto es un **crawler avanzado de sitios web** que permite extraer correos electrónicos desde páginas web, incluyendo contenido generado por JavaScript. Usa **Playwright** para renderizado completo y `BeautifulSoup` para parsear el HTML.

---

## Características

- Renderiza JavaScript para páginas dinámicas.
- Extrae emails del contenido visible.
- Detecta enlaces internos y recorre el sitio hasta un límite de páginas.
- Genera un archivo `emails_encontrados.txt` con todos los correos encontrados.
- Logs detallados en consola para seguimiento del proceso.

---

## Requisitos
httpx
beautifulsoup4
playwright
playwright-stealth

## Configuracion
Puedes limitar el número de páginas visitadas modificando el parámetro limite_paginas en super_crawler(url_base, limite_paginas=150).
El script usa un navegador headless por defecto para no abrir ventanas.
Los emails se filtran mediante expresiones regulares, así que asegúrate de que los sitios no estén demasiado ofuscados.

## Precausiones
Respeta las políticas de cada sitio web.
No abuses del crawler para no generar tráfico excesivo.
Este script es solo para fines educativos o con permiso del propietario del sitio.

####################################NOTA####################################
## ⚠️ Aviso Legal / Disclaimer

Este script se proporciona únicamente **con fines educativos y de investigación**.  
El autor **no se hace responsable** del uso que se le dé a esta herramienta, ni de posibles violaciones a la privacidad o a las leyes de protección de datos que puedan ocurrir.  

Antes de usar este crawler en cualquier sitio web, **asegúrate de tener permiso** del propietario del sitio y de cumplir con la legislación vigente de tu país.
########################################################################
