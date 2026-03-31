FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proxy.py .
COPY index.html .

EXPOSE 8080

CMD ["python", "-u", "proxy.py"]
