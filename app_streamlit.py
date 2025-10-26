import asyncio
import streamlit as st
from pathlib import Path
from playwright.async_api import async_playwright
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

async def scrape_toto_tables():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto("https://www.westlotto.de/toto/ergebniswette/spielplan/toto-ergebniswette-spielplan.html")

        await page.wait_for_selector('select[name="datum"]')
        options = await page.locator('select[name="datum"] option').all()
        daten = [await opt.get_attribute("value") for opt in options if await opt.get_attribute("value")]

        daten_sorted = sorted(daten, key=lambda d: datetime.strptime(d, "%Y-%m-%d"), reverse=True)
        neueste = daten_sorted[:3]
        saved_files = []

        for datum in neueste:
            url = f"https://www.westlotto.de/toto/ergebniswette/spielplan/toto-ergebniswette-spielplan.html?datum={datum}"
            await page.goto(url)
            await page.wait_for_selector('table.table--toto-ergebniswette')

            table_html = await page.locator('table.table--toto-ergebniswette').inner_html()
            soup = BeautifulSoup(table_html, "html.parser")

            for hidden in soup.select(".hidden-print"):
                hidden.decompose()

            suffix = get_suffix(soup)
            filename = f"toto_tabelle_{datum}_{suffix}.txt"
            filepath = output_dir / filename

            with open(filepath, "w", encoding="utf-8") as f:
                f.write(str(soup))
            saved_files.append(filepath)

        await browser.close()
        return saved_files

# 🎯 Streamlit UI
st.title("Westlotto TOTO-Ergebniswette Scraper")
st.write("Dieses Tool lädt die neuesten drei TOTO-Tabellen und bietet sie zum Download an.")

output_dir = Path("downloads")
output_dir.mkdir(exist_ok=True)

if st.button("🔄 Tabellen abrufen und speichern"):
    with st.spinner("Lade Daten von Westlotto... bitte warten ⏳"):
        try:
            files = asyncio.run(scrape_toto_tables())
            st.success(f"{len(files)} Dateien erfolgreich gespeichert!")
        except Exception as e:
            st.error(f"Fehler beim Abrufen: {e}")
            st.stop()
        st.success("✅ Tabellen gespeichert:")

    for file_path in files:
        with open(file_path, "r", encoding="utf-8") as f:
            data = f.read()
        st.download_button(
            label=f"📄 {file_path.name} herunterladen ",
            data=data,
            file_name=file_path.name,
            mime="text/plain"
        )

    st.info("Klicke auf die Buttons, um die Tabellen als Textdatei herunterzuladen.")
else:
    st.info("Klicke auf den Button oben, um die aktuellen Toto-Tabellen zu laden.")
