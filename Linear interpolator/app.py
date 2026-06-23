"""
app.py — Linear Interpolator Web Application
Based on the specification from the Linear Interpolator Project brief.
"""

import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from interpolator import calculate, FIELD_NAMES

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@app.context_processor
def inject_globals():
    return {"year": datetime.utcnow().year, "version": "1.0.0"}


# ── Pages ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/about")
def about():
    return render_template("about.html")


# ── API ───────────────────────────────────────────────────────────────────────

@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    """
    POST /api/calculate
    -------------------
    Body (JSON): { x1, y1, x2, y2, x3, y3 }
    Exactly one value must be null / empty string.

    Returns 200 with result dict, or 400 with { error: str }.
    """
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    try:
        result = calculate(data)
        logger.info(
            "INTERPOLATE | blank=%s result=%s",
            result["blank_field"], result["result_str"],
        )
        return jsonify(result), 200

    except ValueError as exc:
        logger.warning("Validation error: %s", exc)
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        logger.error("Unexpected error: %s", exc, exc_info=True)
        return jsonify({"error": "Internal server error."}), 500


@app.route("/health")
def health():
    return jsonify({
        "status":    "ok",
        "version":   "1.0.0",
        "timestamp": datetime.utcnow().isoformat(),
    })


@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Endpoint not found."}), 404
    return render_template("404.html"), 404


@app.errorhandler(500)
def server_error(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Internal server error."}), 500
    return render_template("404.html"), 500


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    port  = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "production") == "development"
    app.run(debug=debug, host="0.0.0.0", port=port)