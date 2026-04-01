FROM zenika/alpine-chrome:with-python

USER root

# Install pip packages
COPY requirements.txt .
RUN pip3 install --no-cache-dir --break-system-packages -r requirements.txt

COPY proxy.py .

ENV PYTHONUNBUFFERED=1

EXPOSE 8080

CMD ["python3", "-u", "proxy.py"]
