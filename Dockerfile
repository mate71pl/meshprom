FROM python:3.10-slim
RUN apt-get update && apt-get install -y curl
RUN pip install --no-cache-dir prometheus_client
RUN pip install --no-cache --upgrade pytap2
RUN pip install --no-cache --upgrade meshtastic
COPY health_check.sh /app/health_check.sh
RUN chmod +x /app/health_check.sh
HEALTHCHECK --interval=60s --timeout=10s --retries=3 CMD /app/health_check.sh

