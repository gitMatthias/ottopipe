# Basis-Image mit Python 3.10
FROM python:3.10-slim

# Systembibliotheken für Chromium
RUN apt-get update && apt-get install -y \
    libnspr4 \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libasound2 \
    wget \
    unzip \
    curl

# Arbeitsverzeichnis
WORKDIR /app

# Python-Abhängigkeiten
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Playwright-Browser installieren
RUN playwright install

# App-Code kopieren
COPY . .

# Startbefehl
CMD ["streamlit", "run", "app.py", "--server.port=10000", "--server.address=0.0.0.0"]
