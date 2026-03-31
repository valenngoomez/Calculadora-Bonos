FROM selenium/standalone-chrome:latest

USER root

# Install Python
RUN apt-get update && apt-get install -y python3 python3-pip && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python deps
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY proxy.py .

ENV PORT=8765
ENV CHROME_BIN=/usr/bin/google-chrome
ENV PYTHONUNBUFFERED=1

EXPOSE 8765

CMD ["python3", "-u", "proxy.py"]
