import re
import os
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from multiprocessing import Pool, Manager
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

# ============================================
# CONFIGURACIÓN
# ============================================
NUM_PROCESOS = 4       # Ajusta según CPU y memoria
LIMIT_PAGINAS = 150    # Máximo por dominio
OUTPUT_FILE = "emails_encontrados.txt"

# Palabras clave opcionales para filtrar (puedes ampliar)
DOMINIOS = []

# ============================================
# OBTENER HTML CON PLAYWRIGHT + STEALTH
# ============================================
def obtener_html_playwright(url):
    try:
        stealth = Stealth()
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True, args=["--no-sandbox"])
            context = browser.new_context()
            stealth.apply_stealth_sync(context)
            page = context.new_page()
            page.goto(url, timeout=60000, wait_until="domcontentloaded")
            page.wait_for_timeout(1000)

            # Scroll para cargar contenido dinámico
            height = page.evaluate("document.body.scrollHeight")
            for y in range(0, height, 1200):
                page.evaluate(f"window.scrollTo(0, {y})")
                page.wait_for_timeout(300)

            html = page.content()
            browser.close()
            return html
    except Exception as e:
        print(f"ERROR cargando {url}: {e}")
        return None

# ============================================
# EXTRAER EMAILS
# ============================================
def extraer_emails(html):
    if not html:
        return []
    texto = BeautifulSoup(html, "html.parser").get_text(" ")
    emails = re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[A-Za-z]{2,}", texto)
    return list(set(emails))

# ============================================
# EXTRAER ENLACES INTERNOS
# ============================================
def extraer_enlaces(html, dominio, url_actual):
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    urls = set()
    # Enlaces HTML
    for tag in soup.find_all("a", href=True):
        url = urljoin(url_actual, tag['href'])
        if dominio in url:
            urls.add(url)
    # Enlaces JS simples
    js_links = re.findall(r"location\.href=['\"](.*?)['\"]", html)
    for j in js_links:
        url = urljoin(url_actual, j)
        if dominio in url:
            urls.add(url)
    return list(urls)

# ============================================
# FUNCION DE CRAWL DE UN DOMINIO
# ============================================
def crawl_dominio(url_base):
    dominio = urlparse(url_base).netloc
    visitados = set()
    pendientes = [url_base]

    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(f"\n=== DOMINIO: {dominio} ===\n")

    while pendientes and len(visitados) < LIMIT_PAGINAS:
        url = pendientes.pop(0)
        if url in visitados:
            continue
        visitados.add(url)

        print(f"[{dominio}] Visitando: {url}")
        html = obtener_html_playwright(url)
        if not html:
            continue

        # Extraer emails y guardar inmediatamente
        emails = extraer_emails(html)
        if emails:
            with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
                for e in emails:
                    print(f"   → EMAIL encontrado en {url}: {e}")
                    f.write(f"{url} → {e}\n")

        # Extraer enlaces internos
        nuevos = extraer_enlaces(html, dominio, url)
        for n in nuevos:
            if n not in visitados and n not in pendientes:
                pendientes.append(n)

# ============================================
# PROCESAR VARIOS DOMINIOS SIMULTÁNEAMENTE
# ============================================
def procesar_lista(archivo="lista.txt"):
    if not os.path.exists(archivo):
        print("No existe lista.txt")
        return

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("=== EMAILS ENCONTRADOS ===\n")

    urls = [line.strip() for line in open(archivo, "r", encoding="utf-8") if line.strip()]

    with Pool(processes=NUM_PROCESOS) as pool:
        pool.map(crawl_dominio, urls)

# ============================================
# EJECUCIÓN
# ============================================
if __name__ == "__main__":
    procesar_lista()
