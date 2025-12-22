import os
import requests
import time
import logging

SIGNAL_API = os.getenv('SIGNAL_CLI_URL', '')
N8N_WEBHOOK = os.getenv('WEBHOOK_URL', '')
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '3'))  # seconds
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

def poll():
    for attempt in range(MAX_RETRIES):
        try:
            r = requests.get(f"{SIGNAL_API}/v1/receive", timeout=30)
            r.raise_for_status()
            messages = r.json()
            for msg in messages:
                if "envelope" not in msg:
                    continue
                data = msg["envelope"].get("dataMessage")
                if not data or "message" not in data:
                    continue
                payload = {
                    "from": msg["envelope"]["source"],
                    "timestamp": msg["envelope"]["timestamp"],
                    "text": data["message"]
                }
                try:
                    resp = requests.post(N8N_WEBHOOK, json=payload, timeout=5)
                    resp.raise_for_status()
                except Exception as e:
                    logging.error(f"Webhook POST failed: {e}")
            return
        except Exception as e:
            logging.warning(f"Signal API poll failed (attempt {attempt+1}): {e}")
            time.sleep(RETRY_DELAY)
    logging.error("Signal API poll failed after retries.")

def startCheck():
    if not SIGNAL_API or not N8N_WEBHOOK:
        logging.error("SIGNAL_CLI_URL or WEBHOOK_URL are not set in environment variables.")
        raise RuntimeError("Missing URL in environment variables.")
    for attempt in range(MAX_RETRIES):
        try:
            r1 = requests.get(f"{SIGNAL_API}/v1/about", timeout=10)
            r1.raise_for_status()
            break
        except Exception as e:
            logging.warning(f"Signal API is not available (attempt {attempt+1}): {e}")
            time.sleep(RETRY_DELAY)
    else:
        raise RuntimeError("Signal API is not available.")
    for attempt in range(MAX_RETRIES):
        try:
            r2 = requests.get(N8N_WEBHOOK, timeout=10)
            r2.raise_for_status()
            break
        except Exception as e:
            logging.warning(f"Webhook is not available (attempt {attempt+1}): {e}")
            time.sleep(RETRY_DELAY)
    else:
        raise RuntimeError("Webhook is not available.")
    logging.info('Signal CLI bridge to webhook started...')

if __name__ == "__main__":
    try:
        startCheck()
        while True:
            poll()
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        logging.info("Script terminated by user.")
    except Exception as e:
        logging.error(f"Error during script execution: {e}")
