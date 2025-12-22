# Dockerfile for signal-cli-n8n-webhook bridge
FROM python:3.11-slim

WORKDIR /app

COPY signal_bridge.py ./

RUN pip install requests

ENV SIGNAL_CLI_URL=""
ENV WEBHOOK_URL=""
ENV POLL_INTERVAL="3"

CMD ["python", "signal_bridge.py"]
