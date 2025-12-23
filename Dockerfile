# Dockerfile for signal-cli-n8n-webhook bridge
FROM python:3.11-slim

WORKDIR /app

COPY signal_bridge.py ./

RUN pip install requests

# Versioning / metadata (set during build: --build-arg APP_VERSION=1.1)
ARG APP_VERSION=dev
LABEL org.opencontainers.image.title="signal-cli-n8n-webhook" \
    org.opencontainers.image.description="Python bridge that polls signal-cli-rest-api and forwards messages to an n8n webhook" \
    org.opencontainers.image.version="$APP_VERSION" \
    org.opencontainers.image.licenses="MIT"

ENV SIGNAL_CLI_URL=""
ENV WEBHOOK_URL=""
ENV SIGNAL_NUMBERS=""
ENV POLL_INTERVAL="3"
ENV IGNORE_ATTACHMENTS="false"
ENV IGNORE_STORIES="true"
ENV LOG_LEVEL="INFO"

CMD ["python", "signal_bridge.py"]
