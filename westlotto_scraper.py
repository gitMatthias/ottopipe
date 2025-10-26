from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    # page.goto("https://www.westlotto.de/toto/ergebniswette/spielplan/toto-ergebniswette-spielplan.html")
    page.goto("https://www.westlotto.de/toto/ergebniswette/spielplan/toto-ergebniswette-spielplan.html?datum=2025-11-01")
    # Warten, bis die Tabelle geladen ist
    page.wait_for_selector('table.table--toto-ergebniswette')

    # Tabelle extrahieren
    table_html = page.locator('table.table--toto-ergebniswette').inner_html()

    # HTML bereinigen mit BeautifulSoup
    soup = BeautifulSoup(table_html, "html.parser")

    # Entferne alle Elemente mit class="hidden-print"
    for hidden in soup.select(".hidden-print"):
        hidden.decompose()

    # Bereinigten HTML-Code als Text speichern
    with open("toto_tabelle.txt", "w", encoding="utf-8") as f:
        f.write(str(soup))

    print("✅ Bereinigte Tabelle gespeichert als 'toto_tabelle.txt'")
    browser.close()
