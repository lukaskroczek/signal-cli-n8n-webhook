import os
import requests
import time
import logging

SIGNAL_API = os.getenv('SIGNAL_CLI_URL', '')
N8N_WEBHOOK = os.getenv('WEBHOOK_URL', '')
POLL_INTERVAL = int(os.getenv('POLL_INTERVAL', '3'))  # seconds

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper().strip()

# Comma/space/newline separated list of Signal phone numbers (e.g. "+420700000000,+420700000001").
SIGNAL_NUMBERS_RAW = os.getenv('SIGNAL_NUMBERS', '').strip()

# Query params for /v1/receive/<number>
IGNORE_ATTACHMENTS = os.getenv('IGNORE_ATTACHMENTS', 'false').lower() == 'true'
IGNORE_STORIES = os.getenv('IGNORE_STORIES', 'true').lower() == 'true'

MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format='%(asctime)s %(levelname)s %(message)s'
)


def _parse_signal_numbers(raw: str) -> list[str]:
    """Parse SIGNAL_NUMBERS env into a list of phone numbers."""
    if not raw:
        return []
    # allow commas, spaces and newlines
    parts = [p.strip() for p in raw.replace('\n', ',').replace(' ', ',').split(',')]
    return [p for p in parts if p]


SIGNAL_NUMBERS = _parse_signal_numbers(SIGNAL_NUMBERS_RAW)


def poll_one_number(own_number: str) -> None:
    """Poll messages for a specific registered number."""
    params = {
        "ignore_attachments": str(IGNORE_ATTACHMENTS).lower(),
        "ignore_stories": str(IGNORE_STORIES).lower(),
    }

    logging.debug(
        "Polling account=%s (ignore_attachments=%s, ignore_stories=%s)",
        own_number,
        params["ignore_attachments"],
        params["ignore_stories"],
    )

    for attempt in range(MAX_RETRIES):
        try:
            url = f"{SIGNAL_API}/v1/receive/{own_number}"
            r = requests.get(url, params=params, timeout=30, headers={"Accept": "application/json"})
            r.raise_for_status()
            messages = r.json() or []

            total_received = len(messages)
            forwarded = 0
            webhook_failed = 0
            skipped = 0

            for msg in messages:
                if "envelope" not in msg:
                    skipped += 1
                    continue
                envelope = msg["envelope"]
                data = envelope.get("dataMessage")
                if not data or "message" not in data:
                    skipped += 1
                    continue

                payload = {
                    "account": own_number,
                    "from": envelope.get("source"),
                    "timestamp": envelope.get("timestamp"),
                    "text": data.get("message"),
                }

                try:
                    resp = requests.post(N8N_WEBHOOK, json=payload, timeout=5)
                    resp.raise_for_status()
                    forwarded += 1
                except Exception as e:
                    webhook_failed += 1
                    logging.error(f"Webhook POST failed (account={own_number}): {e}")

            if total_received > 0:
                logging.info(
                    "Poll result account=%s: received=%d forwarded=%d webhook_failed=%d skipped=%d",
                    own_number,
                    total_received,
                    forwarded,
                    webhook_failed,
                    skipped,
                )
            else:
                logging.debug("Poll result account=%s: received=0", own_number)

            return
        except Exception as e:
            logging.warning(
                f"Signal API poll failed (account={own_number}, attempt {attempt+1}): {e}"
            )
            time.sleep(RETRY_DELAY)

    logging.error(f"Signal API poll failed after retries (account={own_number}).")


def poll() -> None:
    """Poll messages for all configured numbers."""
    for own_number in SIGNAL_NUMBERS:
        poll_one_number(own_number)


def startCheck():
    if not SIGNAL_API or not N8N_WEBHOOK:
        logging.error("SIGNAL_CLI_URL or WEBHOOK_URL are not set in environment variables.")
        raise RuntimeError("Missing URL in environment variables.")

    if not SIGNAL_NUMBERS:
        logging.error("SIGNAL_NUMBERS is not set (or empty).")
        raise RuntimeError("Missing SIGNAL_NUMBERS in environment variables.")

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

    # n8n webhook endpoints are often POST-only; don't fail hard on GET.
    try:
        requests.get(N8N_WEBHOOK, timeout=10)
    except Exception as e:
        logging.info(f"Webhook GET check skipped/failed (this can be OK): {e}")

    logging.info(
        "Signal CLI bridge to webhook started (accounts=%s, ignore_attachments=%s, ignore_stories=%s)...",
        ",".join(SIGNAL_NUMBERS),
        IGNORE_ATTACHMENTS,
        IGNORE_STORIES,
    )


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
