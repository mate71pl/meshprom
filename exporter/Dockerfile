FROM python:3.10-slim

RUN pip install --no-cache-dir prometheus_client

# Run prom_exporter.py
CMD ["python", "/app/prom_exporter.py"]

