import re
import os
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth


# =========================================================
# RENDERIZADO COMPLETO CON LOGS
# =========================================================
def obtener_html_renderizado(url):
    print(f"      » Renderizando JS para: {url}")

    try:
        stealth = Stealth()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True,
                                        args=["--no-sandbox", "--disable-setuid-sandbox"])

            context = browser.new_context()
            stealth.apply_stealth_sync(context)
            page = context.new_page()

            print(f"      » Cargando página...")
            page.goto(url, timeout=60000, wait_until="domcontentloaded")

            # Scroll inicial
            page.mouse.wheel(0, 1200)
            page.wait_for_timeout(900)

            # Scroll largo
            height = page.evaluate("document.body.scrollHeight")
            print(f"      » Altura documento: {height}")

            for y in range(0, height, 1400):
                page.evaluate(f"window.scrollTo(0, {y})")
                page.wait_for_timeout(600)

            print("      » Renderizado completo OK")
            html = page.content()
            browser.close()
            return html

    except Exception as e:
        print(f"      !!! ERROR RENDERIZANDO {url}: {e}")
        return None


# =========================================================
# EXTRAER EMAILS
# =========================================================
def extraer_emails(html):
    texto = BeautifulSoup(html, "html.parser").get_text(" ")
    return list(set(re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", texto)))


# =========================================================
# EXTRAER ENLACES CON LOGS
# =========================================================
def extraer_enlaces(html, dominio, url_actual):
    print(f"      » Extrayendo enlaces de: {url_actual}")
    urls = set()

    if not html:
        print("      !!! HTML vacío — no se pueden extraer enlaces.")
        return []

    soup = BeautifulSoup(html, "html.parser")

    # Enlaces normales
    for tag in soup.find_all("a", href=True):
        url = urljoin(url_actual, tag["href"])
        if dominio in url:
            print(f"         → Enlace encontrado: {url}")
            urls.add(url)

    # JS-based links
    js_links = re.findall(r"location\.href=['\"](.*?)['\"]", html)
    for js in js_links:
        url = urljoin(url_actual, js)
        if dominio in url:
            print(f"         → JS-link encontrado: {url}")
            urls.add(url)

    return list(urls)


# =========================================================
# SUPER CRAWLER CON LOGS DETALLADOS
# =========================================================
def super_crawler(url_base, limite_paginas=150):

    dominio = urlparse(url_base).netloc
    pendientes = [url_base]
    visitados = set()
    resultados = []

    print(f"\n========== INICIANDO CRAWLER EN {dominio} ==========\n")

    while pendientes and len(visitados) < limite_paginas:

        url = pendientes.pop(0)

        if url in visitados:
            print(f"SKIP Visitado antes → {url}")
            continue

        print(f"\n>>> VISITANDO ({len(visitados)+1}/{limite_paginas}): {url}")
        visitados.add(url)

        # 1) Obtener HTML
        html = obtener_html_renderizado(url)
        if not html:
            print("   !!! No se pudo renderizar esta página\n")
            continue

        # 2) Buscar emails
        emails = extraer_emails(html)
        if emails:
            for e in emails:
                print(f"      ✔ EMAIL encontrado: {e}")
                resultados.append((url, e))
        else:
            print("      (No se encontraron emails en esta página)")

        # 3) Buscar nuevos enlaces
        nuevos = extraer_enlaces(html, dominio, url)

        for n in nuevos:
            if n not in visitados and n not in pendientes:
                print(f"      + Añadiendo a cola → {n}")
                pendientes.append(n)
            else:
                print(f"      - Ignorado (ya conocido) → {n}")

    print("\n========== CRAWLER TERMINADO ==========")
    return resultados


# =========================================================
# PROCESAR lista.txt
# =========================================================
def procesar_urls(archivo="lista.txt"):
    if not os.path.exists(archivo):
        print("No existe lista.txt")
        return

    with open("emails_encontrados.txt", "w", encoding="utf-8") as out:
        out.write("=== EMAILS ENCONTRADOS ===\n\n")

        for url in open(archivo, "r", encoding="utf-8"):
            url = url.strip()
            if not url:
                continue

            resultados = super_crawler(url)

            if resultados:
                for pagina, mail in resultados:
                    out.write(f"{pagina} → {mail}\n")
            else:
                out.write(f"{url} → NO SE ENCONTRÓ NINGÚN EMAIL\n")

    print("\n✔ Emails guardados en emails_encontrados.txt")


if __name__ == "__main__":
    procesar_urls()
