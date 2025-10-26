import streamlit as st
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

def scrape_and_save():
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
            with open(filename, "w", encoding="utf-8") as f:
                f.write(str(soup))
            saved_files.append(filename)

        browser.close()
        return saved_files

# 🎯 Streamlit UI
st.title("Westlotto TOTO-Ergebniswette Scraper")
st.write("Dieses Tool lädt die neuesten TOTO-Tabellen und speichert sie als Textdateien.")

if st.button("🔄 Tabellen abrufen und speichern"):
    with st.spinner("Scraping läuft..."):
        files = scrape_and_save()
    st.success("✅ Tabellen gespeichert:")
    for f in files:
        st.write(f"📄 {f}")
