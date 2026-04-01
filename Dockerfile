FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1

# Dependencias del sistema
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

# Chrome 120 — ultima version estable antes de los crashes headless con JS pesado
# Usamos chrome-for-testing que tiene binarios exactos por version
RUN set -e; \
    CHROME_VERSION="120.0.6099.109"; \
    BASE="https://storage.googleapis.com/chrome-for-testing-public"; \
    echo "Descargando Chrome $CHROME_VERSION..."; \
    wget -q -O /tmp/chrome.zip "$BASE/$CHROME_VERSION/linux64/chrome-linux64.zip"; \
    unzip -q /tmp/chrome.zip -d /opt/; \
    ln -s /opt/chrome-linux64/chrome /usr/local/bin/google-chrome; \
    rm /tmp/chrome.zip; \
    echo "Descargando ChromeDriver $CHROME_VERSION..."; \
    wget -q -O /tmp/cd.zip "$BASE/$CHROME_VERSION/linux64/chromedriver-linux64.zip"; \
    unzip -q /tmp/cd.zip -d /tmp/cd_tmp; \
    mv /tmp/cd_tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver; \
    chmod +x /usr/local/bin/chromedriver /usr/local/bin/google-chrome; \
    rm -rf /tmp/cd.zip /tmp/cd_tmp; \
    google-chrome --version; \
    chromedriver --version

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proxy.py .

ENV PORT=8080

CMD ["python3", "-u", "proxy.py"]

