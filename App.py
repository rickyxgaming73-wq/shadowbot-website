import os
import time
import logging
import json
from functools import wraps
from flask import Flask, request, jsonify, abort
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

# Load and validate PUBLIC_KEY
PUBLIC_KEY = os.environ.get("PUBLIC_KEY")
if not PUBLIC_KEY:
    app.logger.error("PUBLIC_KEY environment variable is not set. Exiting.")
    raise SystemExit("PUBLIC_KEY environment variable is required")

try:
    verify_key = VerifyKey(bytes.fromhex(PUBLIC_KEY))
except ValueError as e:
    app.logger.error("PUBLIC_KEY is not valid hex: %s", e)
    raise SystemExit("PUBLIC_KEY must be a hex-encoded Ed25519 public key")

# Configuration: timestamp tolerance in seconds to mitigate replay attacks.
TIMESTAMP_TOLERANCE_SECONDS = int(os.environ.get("TIMESTAMP_TOLERANCE_SECONDS", 5))


def verify_discord_request(f):
    """Decorator to verify Discord interaction signature and timestamp."""
    @wraps(f)
    def decorated(*args, **kwargs):
        signature = request.headers.get("X-Signature-Ed25519")
        timestamp = request.headers.get("X-Signature-Timestamp")

        if not signature or not timestamp:
            app.logger.warning("Missing signature or timestamp headers")
            return abort(401)

        # Basic timestamp replay protection
        try:
            ts = int(timestamp)
        except ValueError:
            app.logger.warning("Invalid timestamp value: %s", timestamp)
            return abort(401)

        now = time.time()
        if abs(now - ts) > TIMESTAMP_TOLERANCE_SECONDS:
            app.logger.warning(
                "Timestamp outside tolerance: ts=%s now=%s diff=%s",
                ts, now, abs(now - ts)
            )
            return abort(401)

        body = request.get_data() or b""

        try:
            verify_key.verify(
                timestamp.encode() + body,
                bytes.fromhex(signature)
            )
        except (BadSignatureError, ValueError) as e:
            app.logger.warning("Signature verification failed: %s", e)
            return abort(401)

        return f(*args, **kwargs)
    return decorated


@app.route("/")
def home():
    return "🖤 ShadowBot backend is online!"


@app.route("/interactions", methods=["POST"])
@verify_discord_request
def interactions():
    # Prefer request.get_json but fall back to raw body parsing if needed
    data = request.get_json(silent=True)
    if data is None:
        # fallback: try to decode raw body as json (helps when content-type is missing)
        try:
            raw = request.get_data(as_text=True) or ""
            data = json.loads(raw) if raw else None
        except (ValueError, TypeError):
            app.logger.warning("Invalid JSON payload")
            data = None

    if not data:
        return abort(400)

    # Discord PING
    if data.get("type") == 1:
        return jsonify({"type": 1})

    # Slash commands (APPLICATION_COMMAND)
    if data.get("type") == 2:
        command = data.get("data", {}).get("name", "").lower()

        if command == "shadow":
            return jsonify({
                "type": 4,
                "data": {"content": "🖤 ShadowBot is online!"}
            })

        if command == "ping":
            return jsonify({
                "type": 4,
                "data": {"content": "🏓 ShadowBot Pong!"}
            })

        return jsonify({
            "type": 4,
            "data": {"content": "❌ Unknown ShadowBot command."}
        })

    return jsonify({
        "type": 4,
        "data": {"content": "⚡ ShadowBot received your interaction!"}
    })


if __name__ == "__main__":
    # For development/testing only. In production use gunicorn/uvicorn.
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)