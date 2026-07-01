import json
from flask import Blueprint, request, jsonify
from database.db import (
    db,
    Vessel,
    CIICalculation,
    EGBPCalculation,
    PipeWallCalculation,
    LinearInterpolatorCalculation
)
from calculators.eexi import calculate_eexi
from calculators.cii import calculate_cii
from calculators.egbp import calculate_egbp, ENGINE_PRESETS, ROUGHNESS_MAP, ELEMENT_LABELS
from calculators.pipe_wall import calculate_pipe_wall
from calculators.linear_interpolator import calculate_linear_interpolator
from calculators.utils.validators import validate_inputs

calculators_bp = Blueprint("calculators", __name__, url_prefix="/api")


@calculators_bp.route("/egbp/constants", methods=["GET"])
def get_egbp_constants():
    return jsonify({
        "engine_presets": ENGINE_PRESETS,
        "roughness_options": ROUGHNESS_MAP,
        "element_labels": ELEMENT_LABELS
    })


@calculators_bp.route("/calculate-eexi", methods=["POST"])
def calculate_eexi_api():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400

    is_valid, error_msg = validate_inputs(data)
    if not is_valid:
        return jsonify({"error": error_msg}), 400

    try:
        result = calculate_eexi(data)

        # Save to history
        vessel = Vessel(
            name=data.get("vessel_name"),
            ship_type=data["ship_type"],
            dwt=float(data.get("dwt", 0) or 0),
            gt=float(data.get("gt", 0) or 0),
            mcr=float(data["mcr"]),
            sfc=float(data["sfc"]),
            fuel=data["fuel_type"],
            speed=float(data["speed"]),
            pae=float(data.get("pae", 0) or 0),
            sfc_ae=float(data.get("sfc_ae", 0) or 0),
            fuel_ae=data.get("fuel_type_ae") if data.get("fuel_type_ae") else data["fuel_type"],
            f_eff=float(data.get("f_eff", 1.0) or 1.0),
            f_i=float(data.get("f_i", 1.0) or 1.0),
            f_w=float(data.get("f_w", 1.0) or 1.0),
            attained_eexi=result["attained_eexi"],
            required_eexi=result["required_eexi"],
            status=result["status"],
            margin=result["margin"],
            user_local_time=data.get("user_local_time"),
        )
        db.session.add(vessel)
        db.session.commit()

        result["vessel_id"] = vessel.id
        result["vessel_name"] = vessel.name
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calculators_bp.route("/calculate-cii", methods=["POST"])
def calculate_cii_api():
    data = request.get_json(force=True, silent=True)
    if not data:
        return jsonify({"error": "Invalid JSON"}), 400
    try:
        result = calculate_cii(data)

        cii_calc = CIICalculation(
            ship_type=data["ship_type"],
            year=data["year"],
            attained_cii=result["attained_cii"],
            required_cii=result["required_cii"],
            rating=result["rating"]["rating"],
            margin_pct=result["rating"]["margin_pct"],
            full_data=json.dumps(result),
        )
        db.session.add(cii_calc)
        db.session.commit()

        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calculators_bp.route("/calculate-egbp", methods=["POST"])
def calculate_egbp_api():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing input data"}), 400

        result = calculate_egbp(data)

        calc = EGBPCalculation(
            mass_flow=float(data["mass_flow_kgs"]),
            temperature=float(data["temp_tc_c"]),
            total_pa=result["total_pressure_pa"],
            max_bp=float(data["max_bp_pa"]),
            status=result["status"],
            full_data=json.dumps(result),
        )
        db.session.add(calc)
        db.session.commit()

        result["id"] = calc.id
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calculators_bp.route("/calculate-pipe", methods=["POST"])
def calculate_pipe_api():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing input data"}), 400

        result = calculate_pipe_wall(data)

        status = "PASS" if result["recommended_schedule"] else "FAIL"

        calc = PipeWallCalculation(
            nps=float(data["nps"]),
            pressure_mpa=float(data["pressure_mpa"]),
            temp_c=float(data["temp_c"]),
            material=data["material"],
            weld_type=data["weld_type"],
            corrosion_mm=float(data.get("corrosion_mm", 0.0)),
            threaded=data.get("threaded", False),
            mill_tolerance=float(data.get("mill_tolerance", 12.5)),
            t_dis_mm=result["t_dis_mm"],
            t_req_mm=result["t_req_mm"],
            t_min_mm=result["t_min_mm"],
            S_mpa=result["S_mpa"],
            dext_mm=result["dext_mm"],
            recommended_schedule=result["recommended_schedule"]["schedule"] if result["recommended_schedule"] else None,
            available_thickness_mm=result["recommended_schedule"]["thickness_mm"] if result["recommended_schedule"] else None,
            status=status,
            full_data=json.dumps(result),
        )
        db.session.add(calc)
        db.session.commit()

        result["id"] = calc.id
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@calculators_bp.route("/calculate-interpolator", methods=["POST"])
def calculate_interpolator_api():
    try:
        data = request.get_json(force=True, silent=True)
        if not data:
            return jsonify({"error": "Request body must be valid JSON."}), 400

        result = calculate_linear_interpolator(data)

        def to_float_or_none(val):
            if val is None or val == "":
                return None
            try:
                return float(val)
            except (ValueError, TypeError):
                return None

        calc = LinearInterpolatorCalculation(
            x1=to_float_or_none(data.get("x1")),
            y1=to_float_or_none(data.get("y1")),
            x2=to_float_or_none(data.get("x2")),
            y2=to_float_or_none(data.get("y2")),
            x3=to_float_or_none(data.get("x3")),
            y3=to_float_or_none(data.get("y3")),
            blank_field=result["blank_field"],
            result=result["result"],
            formula_used=result["formula_used"],
            full_data=json.dumps(result),
        )
        db.session.add(calc)
        db.session.commit()

        result["id"] = calc.id
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500
