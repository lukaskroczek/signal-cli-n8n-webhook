# Dockerfile for signal-cli-n8n-webhook bridge
FROM python:3.11-slim

WORKDIR /app

COPY signal_bridge.py ./

RUN pip install requests

ENV SIGNAL_CLI_URL=""
ENV WEBHOOK_URL=""
ENV SIGNAL_NUMBERS=""
ENV POLL_INTERVAL="3"
ENV IGNORE_ATTACHMENTS="false"
ENV IGNORE_STORIES="true"
ENV LOG_LEVEL="INFO"

CMD ["python", "signal_bridge.py"]
