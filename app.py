import streamlit as st
from pathlib import Path
from bs4 import BeautifulSoup
from datetime import datetime
import requests
import zipfile
import io

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

        @media (prefers-color-scheme: dark) {
            tbody {
                background-color: #2a2a2a;
                color: #f0f0f0;
            }
            thead {
                color: #ffffff;
            }
            table, th, td {
                border-color: #444 !important;
            }
        }
    </style>
""", unsafe_allow_html=True)

def get_available_dates():
    res = requests.get(BASE_URL)
    soup = BeautifulSoup(res.text, "html.parser")
    options = soup.select('select[name="datum"] option')
    daten = [opt["value"] for opt in options if opt.get("value")]
    return sorted(daten, key=lambda d: datetime.strptime(d, "%Y-%m-%d"), reverse=True)[:3]

def get_suffix(soup):
    headers = [th.get_text(strip=True).lower() for th in soup.select("thead th")]
    if any("ergebnis" in h for h in headers):
        return "Ergebnis"
    elif any("tendenz" in h for h in headers):
        return "Tipps"
    return "Unbekannt"

def scrape_table_for_date(datum):
    url = f"{BASE_URL}?datum={datum}"
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    table = soup.select_one("table.table--toto-ergebniswette")
    if not table:
        return None

    for hidden in table.select(".hidden-print"):
        hidden.decompose()

    suffix = get_suffix(soup)
    filename = f"tabelle_{datum}_{suffix}.html"
    filepath = output_dir / filename
    html_content = table.prettify()

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(html_content)

    return filepath, html_content

def scrape_all():
    dates = get_available_dates()
    results = [scrape_table_for_date(d) for d in dates if scrape_table_for_date(d)]
    return [r for r in results if r]

def get_latest_bonus_numbers():
    res = requests.get(BONUS_URL)
    soup = BeautifulSoup(res.text, "html.parser")

    # Datum aus <p class="heading-h3">Ergebnisse Wettrunde …
    heading = soup.find("p", class_="heading-h3")
    datum_text = heading.get_text(strip=True) if heading else "Unbekannt"

    # Spiel 77
    spiel77 = soup.find(string=lambda t: "Spiel 77" in t)
    spiel77_numbers = spiel77.find_next().text.strip() if spiel77 else "Nicht gefunden"

    # SUPER 6
    super6 = soup.find(string=lambda t: "SUPER 6" in t)
    super6_numbers = super6.find_next().text.strip() if super6 else "Nicht gefunden"

    return datum_text, spiel77_numbers, super6_numbers

# 🎯 Streamlit UI
st.title("OTTOPIPE Scraper")
st.write("Dieses Tool lädt die neuesten drei Tabellen und zeigt die aktuellen Gewinnzahlen von Spiel 77 und SUPER 6.")

# 🎯 Bonuszahlen anzeigen
try:
    datum_text, spiel77, super6 = get_latest_bonus_numbers()
    st.subheader(f"🎯 Aktuelle Zusatzspielzahlen ({datum_text})")
    st.markdown(f"**Spiel 77:** `{spiel77}`")
    st.markdown(f"**SUPER 6:** `{super6}`")
except Exception as e:
    st.warning(f"Fehler beim Laden der Zusatzspielzahlen: {e}")

if st.button("🔄 Tabellen abrufen und speichern"):
    
    with st.spinner("Lade Daten für OTTOPIPE ... bitte warten ⏳"):
        try:
            results = scrape_all()
            if not results:
                st.warning("Keine Tabellen gefunden.")
                st.stop()
            st.success(f"{len(results)} Dateien erfolgreich gespeichert!")
        except Exception as e:
            st.error(f"Fehler beim Abrufen: {e}")
            st.stop()

    # 📦 ZIP-Datei erstellen
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file_path, _ in results:
            zip_file.write(file_path, arcname=file_path.name)
    zip_buffer.seek(0)

    st.download_button(
        label="📦 Alle Tabellen als ZIP herunterladen",
        data=zip_buffer,
        file_name="tabellen.zip",
        mime="application/zip"
    )

    st.info("Klicke auf den Button, um alle Tabellen gesammelt als ZIP-Datei herunterzuladen.")

    # 📊 Vorschau der Tabellen
    st.subheader("📊 Vorschau der extrahierten Tabellen")
    for file_path, html in results:
        st.markdown(f"### 📄 {file_path.name}")
        st.markdown(html, unsafe_allow_html=True)
else:
    st.info("Klicke auf den Button oben, um die aktuellen Tabellen zu laden.")
