# Railway solo sirve el dashboard HTML — sin Chrome, sin Selenium
FROM python:3.11-slim-bookworm

ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Servidor HTTP minimo para servir el HTML
RUN pip install --no-cache-dir flask

COPY index.html .
COPY server.py .

ENV PORT=8080
CMD ["python3", "-u", "server.py"]
