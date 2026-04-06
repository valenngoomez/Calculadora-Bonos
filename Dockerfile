FROM python:3.11-slim-bookworm

ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONUNBUFFERED=1 \
    DISPLAY=:99

RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl unzip gnupg ca-certificates \
    xvfb x11-utils \
    fonts-liberation libappindicator3-1 libasound2 \
    libatk-bridge2.0-0 libatk1.0-0 libcairo2 libcups2 libdbus-1-3 \
    libexpat1 libfontconfig1 libgbm1 libgdk-pixbuf2.0-0 libglib2.0-0 \
    libgtk-3-0 libnspr4 libnss3 libpango-1.0-0 libpangocairo-1.0-0 \
    libx11-6 libx11-xcb1 libxcb1 libxcomposite1 libxcursor1 libxdamage1 \
    libxext6 libxfixes3 libxi6 libxrandr2 libxrender1 libxss1 libxtst6 \
    lsb-release xdg-utils \
    && rm -rf /var/lib/apt/lists/*

RUN wget -q -O /tmp/chrome.deb \
        "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb" \
    && apt-get update \
    && apt-get install -y /tmp/chrome.deb \
    && rm /tmp/chrome.deb \
    && rm -rf /var/lib/apt/lists/* \
    && google-chrome --version

RUN set -e; \
    CHROME_VER=$(google-chrome --version | grep -oP '\d+\.\d+\.\d+\.\d+'); \
    BASE_URL="https://storage.googleapis.com/chrome-for-testing-public"; \
    DL_URL="$BASE_URL/$CHROME_VER/linux64/chromedriver-linux64.zip"; \
    if wget -q --spider "$DL_URL" 2>/dev/null; then \
        wget -q -O /tmp/cd.zip "$DL_URL"; \
    else \
        LATEST=$(curl -s "https://googlechromelabs.github.io/chrome-for-testing-public/last-known-good-versions.json" \
                 | python3 -c "import sys,json; print(json.load(sys.stdin)['channels']['Stable']['version'])"); \
        wget -q -O /tmp/cd.zip "$BASE_URL/$LATEST/linux64/chromedriver-linux64.zip"; \
    fi; \
    unzip -q /tmp/cd.zip -d /tmp/cd_tmp; \
    mv /tmp/cd_tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver; \
    chmod +x /usr/local/bin/chromedriver; \
    rm -rf /tmp/cd.zip /tmp/cd_tmp; \
    chromedriver --version

# Script de arranque que espera a que Xvfb esté listo
COPY start.sh /start.sh
RUN chmod +x /start.sh

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY proxy.py .

ENV PORT=8080
CMD ["/start.sh"]
