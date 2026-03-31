FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install Python + Chrome
RUN apt-get update && apt-get install -y \
    python3 python3-pip wget gnupg ca-certificates curl \
    && wget -q -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb \
    && apt-get install -y /tmp/chrome.deb \
    && rm /tmp/chrome.deb \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY proxy.py .

ENV CHROME_BIN=/usr/bin/google-chrome

EXPOSE 8080

CMD ["python3", "-u", "proxy.py"]
