import requests
from bs4 import BeautifulSoup
from datetime import datetime
from pathlib import Path

BASE_URL = "https://www.westlotto.de/toto/ergebniswette/spielplan/toto-ergebniswette-spielplan.html"
output_dir = Path("downloads")
output_dir.mkdir(exist_ok=True)

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
    filename = f"toto_tabelle_{datum}_{suffix}.txt"
    filepath = output_dir / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(str(table))
    return filepath

def scrape_all():
    dates = get_available_dates()
    return [scrape_table_for_date(d) for d in dates]

if __name__ == "__main__":
    files = scrape_all()
    print("Gespeichert:", files)
