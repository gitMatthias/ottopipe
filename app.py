import streamlit as st
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import zipfile
import io
import os

BASE_URL = "https://www.westlotto.de/toto/ergebniswette/spielplan/toto-ergebniswette-spielplan.html"
BONUS_URL = "https://www.westlotto.de/infos-und-zahlen/gewinnzahlen/toto-ergebniswette/toto-ergebniswette-gewinnzahlen.html"
output_dir = Path("downloads")
output_dir.mkdir(exist_ok=True)

# 💅 CSS Styling for light & dark mode
st.markdown("""
    <style>
        thead {
            background-color: transparent !important;
        }
        tbody {
            background-color: #f2f2f2;
        }
    </style>
""", unsafe_allow_html=True)

def lade_bonuszahlen():
    try:
        response = requests.get(BONUS_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        heading = soup.find("p", class_="heading-h3")
        round_info = heading.text.strip() if heading else "Unbekannte Runde"

        spiel77 = soup.find("span", class_="superzahl-gewinnzahl")
        super6 = soup.find("span", class_="super6-gewinnzahl")

        spiel77_text = spiel77.text.strip() if spiel77 else "Keine Zahl gefunden"
        super6_text = super6.text.strip() if super6 else "Keine Zahl gefunden"

        st.markdown(f"### 🎯 Aktuelle Zusatzspielzahlen (Ergebnisse {round_info})")
        st.markdown(f"**77:** {spiel77_text}")
        st.markdown(f"**6:** {super6_text}")
    except Exception as e:
        st.error(f"Fehler beim Laden der Zusatzspielzahlen: {e}")

def lade_und_speichere_tabellen():
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        tables = soup.find_all("table")[:3]

        filenames = []
        for i, table in enumerate(tables):
            date_str = datetime.today().strftime("%Y-%m-%d")
            filename = f"tabelle_{date_str}_{i+1}.html"
            filepath = output_dir / filename
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(str(table))
            filenames.append(filepath)

        st.success("📦 Dateien erfolgreich gespeichert!")

        # ZIP-Download anbieten
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for file in filenames:
                zip_file.write(file, arcname=os.path.basename(file))
        st.download_button("📥 Alle Tabellen als ZIP herunterladen", data=zip_buffer.getvalue(), file_name="tabellen.zip")

        # Tabellen anzeigen
        st.markdown("### 📊 Extrahierte Tabellen")
        for file in filenames:
            with open(file, "r", encoding="utf-8") as f:
                html = f.read()
                st.components.v1.html(html, height=300, scrolling=True)

    except Exception as e:
        st.error(f"Fehler beim Laden der Tabellen: {e}")

if st.button("🔄 Tabellen und Zusatzspielzahlen abrufen"):
    lade_und_speichere_tabellen()
    lade_bonuszahlen()
