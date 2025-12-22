# Dockerfile for signal-cli-n8n-webhook bridge
CMD ["python", "signal_bridge.py"]

ENV POLL_INTERVAL="3"
ENV WEBHOOK_URL=""
ENV SIGNAL_CLI_URL=""

RUN pip install requests

COPY signal_bridge.py ./

WORKDIR /app

FROM python:3.11-slim

