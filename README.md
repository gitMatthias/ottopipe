# 🧾 OTTOPIPE Scraper

Dieses Tool lädt die neuesten drei TOTO-Ergebniswette-Tabellen von [westlotto.de](https://www.westlotto.de) und bietet sie als `.html`-Dateien zum Download an — gesammelt als ZIP über eine benutzerfreundliche Streamlit-Oberfläche.

---

## 🚀 Features

- Abruf der drei aktuellsten Spieltage
- HTML-Export der Tabellen inklusive vollständiger `<table>`-Header und Formatierung
- ZIP-Download aller Dateien direkt über die Weboberfläche
- Läuft stabil auf [Render](https://render.com) im Free Tier — ohne Docker, ohne Playwright

---

## 📁 Projektstruktur

Folgende Dateien müssen im GitHub-Repo (`ottopipe`) enthalten sein:


```bash
ottopipe/ 
├── app.py # Hauptskript mit Streamlit UI und Scraping-Logik 
├── requirements.txt # Python-Abhängigkeiten 
├── render.yaml # Render-Konfiguration für automatisches Deployment 
├── downloads/ # Wird zur Laufzeit erstellt, enthält die gespeicherten Tabellen
```

---

## 📦 `requirements.txt`

```txt
streamlit
requests
beautifulsoup4
```


---

## ⚙️ `render.yaml`

```txt
services:
  - type: web
    name: westlotto-scraper
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run app.py
    repo: https://github.com/gitMatthias/ottopipe
    branch: main
    autoDeploy: true
```
🌐 Deployment auf Render
Melde dich bei Render an

Erstelle ein neues Web Service-Projekt

Start-Command ist "streamlit run app.py"

Wähle dein GitHub-Repo ottopipe

Render erkennt automatisch render.yaml und startet den Build

Die App ist erreichbar unter https://ottopipe-0g3q.onrender.com

📥 Nutzung
Öffne die Web-App

Klicke auf „🔄 Tabellen abrufen und speichern“

Lade die ZIP-Datei mit den HTML-Tabellen herunter

🛡️ Hinweise
Kein Playwright nötig — die Seite liefert statisches HTML

Keine Systempakete erforderlich — ideal für Render Free Tier

Die Dateien werden lokal im Ordner downloads/ gespeichert und gepackt

