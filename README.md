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
- `POLL_INTERVAL`: Polling interval in seconds (default: 3)

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
   export POLL_INTERVAL=3
   ```
3. Run the script:
   ```bash
   python signal_bridge.py
   ```

### Run with Docker
1. Build the image:
   ```bash
   docker build -t signal-cli-n8n-webhook .
   ```
2. Run the container:
   ```bash
   docker run -e SIGNAL_CLI_URL="http://localhost:8080" -e WEBHOOK_URL="https://your-n8n-instance/webhook/signal" -e POLL_INTERVAL=3 signal-cli-n8n-webhook
   ```

## License
MIT
