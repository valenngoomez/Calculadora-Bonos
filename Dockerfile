# ──────────────────────────────────────────────────────────────────────────────
# Bonos AR — Dockerfile para Railway
# Base: Debian 12 Bookworm (compatible con el .deb oficial de Google Chrome)
# Intentos anteriores fallidos:
#   - zenika/alpine-chrome:with-python  → imagen eliminada de Docker Hub
#   - python:3.11-slim (sin tag)        → apunta a Trixie (Debian 13), incompatible
#   - selenium/standalone-chrome        → supervisord interfiere, puerto fijo
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

# ── Dependencias del sistema para Chrome headless ─────────────────────────────
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl unzip gnupg ca-certificates \
    fonts-liberation libappindicator3-1 libasound2 \
    libatk-bridge2.0-0 libatk1.0-0 libcairo2 libcups2 libdbus-1-3 \
    libexpat1 libfontconfig1 libgbm1 libgdk-pixbuf2.0-0 libglib2.0-0 \
    libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libpangocairo-1.0-0 \
    libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 \
    libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 \
    lsb-release xdg-utils \
    && rm -rf /var/lib/apt/lists/*

# ── Google Chrome estable (desde dl.google.com — funciona en Bookworm) ────────
RUN wget -q -O /tmp/chrome.deb \
        "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb" \
    && apt-get update \
    && apt-get install -y /tmp/chrome.deb \
    && rm /tmp/chrome.deb \
    && rm -rf /var/lib/apt/lists/* \
    && google-chrome --version

# ── ChromeDriver que matchea la versión de Chrome instalada ───────────────────
RUN set -e; \
    CHROME_VER=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+'); \
    echo "Chrome instalado: $CHROME_VER"; \
    BASE_URL="https://storage.googleapis.com/chrome-for-testing-public"; \
    DL_URL="$BASE_URL/$CHROME_VER/linux64/chromedriver-linux64.zip"; \
    echo "Intentando: $DL_URL"; \
    if wget -q --spider "$DL_URL" 2>/dev/null; then \
        wget -q -O /tmp/cd.zip "$DL_URL"; \
    else \
        echo "Version exacta no disponible, usando ultimo stable..."; \
        LATEST=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json" \
                 | python3 -c "import sys,json; print(json.load(sys.stdin)['channels']['Stable']['version'])"); \
        echo "ChromeDriver latest stable: $LATEST"; \
        wget -q -O /tmp/cd.zip "$BASE_URL/$LATEST/linux64/chromedriver-linux64.zip"; \
    fi; \
    unzip -q /tmp/cd.zip -d /tmp/cd_tmp; \
    mv /tmp/cd_tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver; \
    chmod +x /usr/local/bin/chromedriver; \
    rm -rf /tmp/cd.zip /tmp/cd_tmp; \
    chromedriver --version

# ── Código de la aplicación ───────────────────────────────────────────────────
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proxy.py .

# Railway asigna PORT dinámicamente
ENV PORT=8080

CMD ["python3", "-u", "proxy.py"]
