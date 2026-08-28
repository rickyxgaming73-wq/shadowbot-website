import os
from flask import Flask, request, jsonify, send_from_directory
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError

app = Flask(__name__)

# Discord Public Key from Developer Portal
DISCORD_PUBLIC_KEY = os.getenv("DISCORD_PUBLIC_KEY", "")


# -------------------------
# Website
# -------------------------

@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/privacy")
def privacy():
    return send_from_directory(".", "privacy.html")


@app.route("/terms")
def terms():
    return send_from_directory(".", "terms.html")


# -------------------------
# Discord Interactions
# -------------------------

@app.route("/interactions", methods=["POST"])
def interactions():

    # Make sure the public key exists
    if not DISCORD_PUBLIC_KEY:
        return jsonify({
            "error": "DISCORD_PUBLIC_KEY environment variable is missing"
        }), 500

    # Discord signature headers
    signature = request.headers.get("X-Signature-Ed25519")
    timestamp = request.headers.get("X-Signature-Timestamp")

    if not signature or not timestamp:
        return jsonify({
            "error": "Missing Discord signature"
        }), 401

    # Get raw request body
    body = request.get_data()

    # Verify Discord request
    try:
        verify_key = VerifyKey(bytes.fromhex(DISCORD_PUBLIC_KEY))

        verify_key.verify(
            timestamp.encode() + body,
            bytes.fromhex(signature)
        )

    except (BadSignatureError, ValueError):
        return jsonify({
            "error": "Invalid Discord signature"
        }), 401

    # Read Discord interaction
    data = request.get_json(silent=True)

    if not data:
        return jsonify({
            "error": "Invalid JSON"
        }), 400

    interaction_type = data.get("type")

    # -------------------------
    # Discord Ping
    # -------------------------

    if interaction_type == 1:
        return jsonify({
            "type": 1
        })

    # -------------------------
    # Slash Commands
    # -------------------------

    if interaction_type == 2:

        command_name = data.get("data", {}).get("name")

        # /ping
        if command_name == "ping":
            return jsonify({
                "type": 4,
                "data": {
                    "content": "🏓 Pong! **ShadowBot is online!**"
                }
            })

        # Unknown command
        return jsonify({
            "type": 4,
            "data": {
                "content": "❓ Unknown ShadowBot command."
            }
        })

    # Unsupported interaction
    return jsonify({
        "error": "Unsupported interaction type"
    }), 400


# -------------------------
# Health Check
# -------------------------

@app.route("/health")
def health():
    return jsonify({
        "status": "online",
        "bot": "ShadowBot"
    })


# -------------------------
# Local Development
# -------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
