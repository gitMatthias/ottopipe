from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()
    page.goto("https://www.westlotto.de/toto/ergebniswette/spielplan/toto-ergebniswette-spielplan.html?datum=2025-11-01")
    page.wait_for_selector('table.table--toto-ergebniswette')

    table_html = page.locator('table.table--toto-ergebniswette').inner_html()
    soup = BeautifulSoup(table_html, "html.parser")

    # Entferne alle Elemente mit class="hidden-print"
    for hidden in soup.select(".hidden-print"):
        hidden.decompose()

    # Finde die Indexposition der Spalte mit dem Titel "Spiel"
    spiel_index = None
    header_row = soup.find("thead").find("tr")
    headers = header_row.find_all("th")
    for i, th in enumerate(headers):
        if th.get_text(strip=True).lower() == "spiel":
            spiel_index = i
            th.decompose()  # Entferne die Header-Zelle
            break

    # Entferne die entsprechende <td> aus jeder Zeile im <tbody>
    if spiel_index is not None:
        for row in soup.find("tbody").find_all("tr"):
            cells = row.find_all("td")
            if len(cells) > spiel_index:
                cells[spiel_index].decompose()

    # Bereinigten HTML-Code als Text speichern
    with open("toto_tabelle.txt", "w", encoding="utf-8") as f:
        f.write(str(soup))

    print("✅ Spalte 'Spiel' entfernt und Tabelle gespeichert als 'toto_tabelle.txt'")
    browser.close()
