import asyncio
import sys

# Fix für Windows + Streamlit + asyncio
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
import streamlit as st # type: ignore
from pathlib import Path
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
from datetime import datetime
import os

def get_suffix(soup):
    headers = [th.get_text(strip=True).lower() for th in soup.select("thead th")]
    if any("ergebnis" in h for h in headers):
        return "Ergebnis"
    elif any("tendenz" in h for h in headers):
        return "Tipps"
    return "Unbekannt"

def scrape_toto_tables():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto("https://www.westlotto.de/toto/ergebniswette/spielplan/toto-ergebniswette-spielplan.html")

        page.wait_for_selector('select[name="datum"]')
        options = page.locator('select[name="datum"] option').all()
        daten = [opt.get_attribute("value") for opt in options if opt.get_attribute("value")]

        daten_sorted = sorted(daten, key=lambda d: datetime.strptime(d, "%Y-%m-%d"), reverse=True)
        neueste = daten_sorted[:3]
        saved_files = []

        for datum in neueste:
            url = f"https://www.westlotto.de/toto/ergebniswette/spielplan/toto-ergebniswette-spielplan.html?datum={datum}"
            page.goto(url)
            page.wait_for_selector('table.table--toto-ergebniswette')

            table_html = page.locator('table.table--toto-ergebniswette').inner_html()
            soup = BeautifulSoup(table_html, "html.parser")

            for hidden in soup.select(".hidden-print"):
                hidden.decompose()

            suffix = get_suffix(soup)
            filename = f"toto_tabelle_{datum}_{suffix}.txt"
            filepath = output_dir / filename

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(str(soup))
            saved_files.append(filepath)

        browser.close()
        return saved_files

# 🎯 Streamlit UI
st.title("Westlotto TOTO-Ergebniswette Scraper")
st.write("Dieses Tool lädt die neuesten drei TOTO-Tabellen und bietet sie zum Download an.")

# 📁 Dokumente-Verzeichnis (lokal oder Binder)
output_dir = Path("downloads")
output_dir.mkdir(exist_ok=True)


if st.button("🔄 Tabellen abrufen und speichern"):
    with st.spinner("Lade Daten von Westlotto... bitte warten ⏳"):
        try:
            files = scrape_toto_tables()
            st.success(f"{len(files)} Dateien erfolgreich gespeichert!")
        except Exception as e:
            st.error(f"Fehler beim Abrufen: {e}")
            st.stop()    
        st.success("✅ Tabellen gespeichert:")

    # 📥 Download-Buttons anzeigen
    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read()
        st.download_button(
            label=f"📄 {file_path.name} herunterladen",
            data=data,
            file_name=file_path.name,
            mime="text/plain"
        )

    st.info("Klicke auf die Buttons, um die Tabellen als Textdatei herunterzuladen.")

else:
    st.info("Klicke auf den Button oben, um die aktuellen Toto-Tabellen zu laden.")