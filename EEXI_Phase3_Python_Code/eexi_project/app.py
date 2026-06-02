"""
app.py
------
Flask application — EEXI Calculator web server.
Run locally:   python app.py
Deploy:        Render / PythonAnywhere (see render.yaml / README)
"""

from flask import Flask, request, jsonify, render_template
from eexi import calculate
from eexi.ship_params import SHIP_LABELS, CF_LABELS

app = Flask(__name__)


# ── Routes ──────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the single-page calculator UI."""
    return render_template(
        "index.html",
        ship_options=SHIP_LABELS,
        fuel_options=CF_LABELS,
    )


@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    """
    POST /api/calculate
    -------------------
    Body (JSON):
        ship_type, dwt, gt, mcr, sfc, fuel_type, v_ref,
        pae (opt), sfc_ae (opt), fuel_ae (opt)

    Returns (JSON):
        Full result dict from eexi.calculator.calculate()
        or {"error": "<message>"} with HTTP 400 on bad input.
    """
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400

    required_fields = ["ship_type", "mcr", "sfc", "fuel_type", "v_ref"]
    missing = [f for f in required_fields if f not in data or data[f] == ""]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    try:
        result = calculate(data)
        return jsonify(result), 200
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:                      # pragma: no cover
        app.logger.error("Unexpected error: %s", exc, exc_info=True)
        return jsonify({"error": "Internal server error. Check server logs."}), 500


@app.route("/api/ship-types")
def api_ship_types():
    """Return available ship types and fuel types (for dynamic frontends)."""
    return jsonify({"ship_types": SHIP_LABELS, "fuel_types": CF_LABELS})


@app.route("/health")
def health():
    """Health-check endpoint for Render / PythonAnywhere."""
    return jsonify({"status": "ok", "version": "1.0.0"})


# ── Entry point ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
