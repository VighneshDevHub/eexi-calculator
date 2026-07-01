from flask import Blueprint, jsonify
from calculators.egbp import ENGINE_PRESETS, ROUGHNESS_MAP
from calculators.cii import CII_REDUCTION_FACTORS
from calculators.utils.ship_params import SHIP_LABELS, CF_LABELS
from calculators.pipe_wall import MATERIAL_LABELS, WELD_LABELS, NPS_DEXT_MM

constants_bp = Blueprint("constants", __name__, url_prefix="/api")


@constants_bp.route("/egbp/constants", methods=["GET"])
def get_egbp_constants():
    return jsonify({
        "engine_presets": ENGINE_PRESETS,
        "roughness_options": ROUGHNESS_MAP,
    })


@constants_bp.route("/constants", methods=["GET"])
def get_all_constants():
    return jsonify({
        "ship_labels": SHIP_LABELS,
        "cf_labels": CF_LABELS,
        "cii_reduction_factors": CII_REDUCTION_FACTORS,
        "pipe_materials": MATERIAL_LABELS,
        "pipe_welds": WELD_LABELS,
        "pipe_nps_dext": NPS_DEXT_MM,
    })
