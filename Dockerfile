FROM python:3.10-slim

RUN pip install --no-cache-dir prometheus_client
RUN pip install --no-cache --upgrade pytap2
RUN pip install --no-cache --upgrade meshtastic
# Run prom_exporter.py
CMD ["python", "/app/prom_exporter.py"]

