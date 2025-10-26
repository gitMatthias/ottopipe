from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime

def get_suffix(soup):
    headers = [th.get_text(strip=True).lower() for th in soup.select("thead th")]
    if any("ergebnis" in h for h in headers):
        return "Ergebnis"
    elif any("tendenz" in h for h in headers):
        return "Tipps"
    return "Unbekannt"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("https://www.westlotto.de/toto/ergebniswette/spielplan/toto-ergebniswette-spielplan.html")

    # Dropdown auslesen
    page.wait_for_selector('select[name="datum"]')
    options = page.locator('select[name="datum"] option').all()
    daten = [opt.get_attribute("value") for opt in options if opt.get_attribute("value")]

    # Sortieren nach Datum (neueste zuerst)
    daten_sorted = sorted(daten, key=lambda d: datetime.strptime(d, "%Y-%m-%d"), reverse=True)
    neueste = daten_sorted[:3]

    for datum in neueste:
        url = f"https://www.westlotto.de/toto/ergebniswette/spielplan/toto-ergebniswette-spielplan.html?datum={datum}"
        page.goto(url)
        page.wait_for_selector('table.table--toto-ergebniswette')

        # Tabelle extrahieren
        table_html = page.locator('table.table--toto-ergebniswette').inner_html()
        soup = BeautifulSoup(table_html, "html.parser")

        # Bereinigen
        for hidden in soup.select(".hidden-print"):
            hidden.decompose()

        # Typ erkennen
        suffix = get_suffix(soup)

        # Speichern
        filename = f"toto_tabelle_{datum}_{suffix}.csv"
        with open(filename, "w", encoding="utf-8") as f:
            f.write(str(soup))

        print(f"✅ {datum}: Tabelle gespeichert als '{filename}'")

    browser.close()
