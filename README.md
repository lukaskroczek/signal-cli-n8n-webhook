# signal-cli-n8n-webhook

A simple Python bridge that polls messages from a [bbernhard/signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api) instance and forwards them to an n8n webhook.

## Features
- Polls Signal CLI REST API for new messages
- Forwards messages to an n8n webhook
- Configurable via environment variables
- Retry logic for robustness

## Requirements
- Python 3.11+
- Docker (optional)
- [bbernhard/signal-cli-rest-api](https://github.com/bbernhard/signal-cli-rest-api) running and accessible
- n8n webhook URL

## Environment Variables
- `SIGNAL_CLI_URL`: Base URL of your Signal CLI REST API (e.g. `http://localhost:8080`)
- `WEBHOOK_URL`: URL of your n8n webhook
- `SIGNAL_NUMBERS`: Comma/space/newline separated list of Signal phone numbers to poll (e.g. `+420704661381,+420700000000`)
- `POLL_INTERVAL`: Polling interval in seconds (default: 3)
- `IGNORE_ATTACHMENTS`: "true"/"false" (default: false) -> passed to Signal REST API as `ignore_attachments`
- `IGNORE_STORIES`: "true"/"false" (default: true) -> passed to Signal REST API as `ignore_stories`
- `LOG_LEVEL`: Logging level (default: `INFO`). Useful values: `DEBUG`, `INFO`, `WARNING`, `ERROR`

## Usage

### Run with Python
1. Install dependencies:
   ```bash
   pip install requests
   ```
2. Set environment variables:
   ```bash
   export SIGNAL_CLI_URL="http://localhost:8080"
   export WEBHOOK_URL="https://your-n8n-instance/webhook/signal"
   export SIGNAL_NUMBERS="+420704661381,+420700000000"
   export POLL_INTERVAL=3
   export IGNORE_ATTACHMENTS=false
   export IGNORE_STORIES=true
   export LOG_LEVEL=INFO
   ```
3. Run the script:
   ```bash
   python signal_bridge.py
   ```

### Run with Docker

#### Versioning (single source of truth)

The version is defined in the `.env` file:
- `APP_VERSION` (e.g. `1.1`)
- `IMAGE_REPO` (default `lukaskroczek/signal-cli-n8n-webhook`)

Docker Compose will automatically load `.env`.

If you want to use the commands below, load these variables into your shell first:

```bash
set -a
source ./.env
set +a
```

#### Build image

Local build for the current platform:

```bash
docker build \
  --build-arg APP_VERSION="$APP_VERSION" \
  -t "$IMAGE_REPO:$APP_VERSION" \
  .
```

Build for a specific platform (e.g. **linux/arm64**) using buildx (`--load` loads the image into your local Docker engine):

```bash
docker buildx build \
  --platform linux/arm64 \
  --build-arg APP_VERSION="$APP_VERSION" \
  -t "$IMAGE_REPO:$APP_VERSION" \
  --load \
  .
```

Optional multi-arch build (typically for pushing to a registry, note the `--push`):

```bash
docker buildx build \
  --platform linux/amd64,linux/arm64 \
  --build-arg APP_VERSION="$APP_VERSION" \
  -t "$IMAGE_REPO:$APP_VERSION" \
  --push \
  .
```

#### Run the container

```bash
docker run \
  -e SIGNAL_CLI_URL="http://localhost:8080" \
  -e WEBHOOK_URL="https://your-n8n-instance/webhook/signal" \
  -e SIGNAL_NUMBERS="+420704661381,+420700000000" \
  -e POLL_INTERVAL=3 \
  -e IGNORE_ATTACHMENTS=false \
  -e IGNORE_STORIES=true \
  -e LOG_LEVEL=DEBUG \
  "$IMAGE_REPO:$APP_VERSION"
```

## License
MIT
