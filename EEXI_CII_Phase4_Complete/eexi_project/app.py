"""
app.py — EEXI + CII Calculator (Production)
"""
import os
import logging
from datetime import datetime
from flask import Flask, request, jsonify, render_template
from eexi import calculate, calculate_cii
from eexi.ship_params import SHIP_LABELS, CF_LABELS
from eexi.cii import CII_REDUCTION_FACTORS

app = Flask(__name__)
logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

@app.context_processor
def inject_globals():
    return {"year": datetime.utcnow().year, "version": "1.1.0"}

# ── Pages ────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html",
        ship_options=SHIP_LABELS, fuel_options=CF_LABELS)

@app.route("/cii")
def cii_page():
    return render_template("cii.html",
        ship_options=SHIP_LABELS, fuel_options=CF_LABELS,
        cii_years=sorted(CII_REDUCTION_FACTORS.keys()))

@app.route("/about")
def about():
    return render_template("about.html")

# ── API ──────────────────────────────────────────────────────────────────────

@app.route("/api/calculate", methods=["POST"])
def api_calculate():
    """EEXI calculation endpoint."""
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400
    missing = [f for f in ["ship_type","mcr","sfc","fuel_type","v_ref"] if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400
    try:
        result = calculate(data)
        logger.info("EEXI | ship=%s → attained=%.3f required=%.3f status=%s",
            data.get("ship_type"), result["attained_eexi"],
            result["required_eexi"], result["compliance"]["status"])
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error("EEXI error: %s", e, exc_info=True)
        return jsonify({"error": "Internal server error."}), 500


@app.route("/api/calculate-cii", methods=["POST"])
def api_calculate_cii():
    """
    CII calculation endpoint.
    MEPC.352-355(78) — attained annual CII with correction factors.
    """
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Request body must be valid JSON."}), 400
    missing = [f for f in ["ship_type","distance_nm"] if not data.get(f)]
    if missing:
        return jsonify({"error": f"Missing required fields: {missing}"}), 400

    # Ensure at least one fuel is provided
    fuel_keys = ["fc_hfo","fc_mdo","fc_lng","fc_methanol","fc_lpg_propane"]
    if not any(float(data.get(k, 0) or 0) > 0 for k in fuel_keys):
        return jsonify({"error": "At least one fuel consumption value must be provided."}), 400

    try:
        result = calculate_cii(data)
        logger.info("CII  | ship=%s year=%s → attained=%.4f required=%.4f rating=%s",
            data.get("ship_type"), data.get("year","2024"),
            result["attained_cii"], result["required_cii"],
            result["rating"]["rating"])
        return jsonify(result), 200
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        logger.error("CII error: %s", e, exc_info=True)
        return jsonify({"error": "Internal server error."}), 500


@app.route("/api/ship-types")
def api_ship_types():
    return jsonify({"ship_types": SHIP_LABELS, "fuel_types": CF_LABELS})

@app.route("/health")
def health():
    return jsonify({"status": "ok", "version": "1.1.0",
                    "timestamp": datetime.utcnow().isoformat()})

@app.errorhandler(404)
def not_found(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Endpoint not found."}), 404
    return render_template("404.html"), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "production") == "development"
    app.run(debug=debug, host="0.0.0.0", port=port)
