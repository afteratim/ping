
import os
import time
import threading
import logging
from datetime import datetime, timezone

import requests
from flask import Flask, jsonify

app = Flask(__name__)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("url-pinger")

URLS = [
    url.strip()
    for url in os.getenv("URLS", "").split(",")
    if url.strip()
]

PING_INTERVAL = max(30, int(os.getenv("PING_INTERVAL", "300")))


def ping_urls():
    while True:
        for url in URLS:
            try:
                start = time.monotonic()

                response = requests.get(
                    url,
                    timeout=25,
                    headers={"User-Agent": "Render-URL-Pinger/1.0"},
                    allow_redirects=True
                )

                elapsed = round(
                    (time.monotonic() - start) * 1000
                )

                logger.info(
                    "URL=%s STATUS=%s TIME=%sms",
                    url,
                    response.status_code,
                    elapsed
                )

            except requests.RequestException as exc:
                logger.error("URL=%s ERROR=%s", url, exc)

        time.sleep(PING_INTERVAL)


@app.route("/")
def home():
    return jsonify({
        "service": "URL Pinger",
        "status": "running",
        "urls_configured": len(URLS),
        "interval_seconds": PING_INTERVAL
    })


@app.route("/health")
def health():
    return jsonify({"status": "healthy"}), 200


def start_pinger():
    thread = threading.Thread(
        target=ping_urls,
        daemon=True
    )
    thread.start()


start_pinger()


if __name__ == "__main__":
    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)
