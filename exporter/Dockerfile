FROM python:3.10-slim

RUN pip install --no-cache-dir prometheus_client

COPY prom_exporter.py .

# Uruchom skrypt prom_exporter.py
CMD ["python", "prom_exporter.py"]

