import json
from datetime import datetime
from flask import Blueprint, request, send_file, jsonify
from app.database.db import (
    db,
    CIICalculation,
    EGBPCalculation,
    PipeWallCalculation,
    Vessel,
)
from app.reports.pdf_generator import (
    generate_pdf_report,
    generate_cii_pdf_report,
    generate_egbp_pdf_report,
    generate_pipe_pdf_report,
)

reports_bp = Blueprint("reports", __name__, url_prefix="/api")


@reports_bp.route("/eexi-report", methods=["POST"])
def eexi_report():
    data = request.get_json(force=True, silent=True)
    try:
        if data and 'vessel_id' in data:
            # If we have a vessel_id, use that to get vessel data and recalculate
            vessel = Vessel.query.get_or_404(data['vessel_id'])
            input_data = {
                "ship_type": vessel.ship_type,
                "dwt": vessel.dwt,
                "gt": vessel.gt,
                "mcr": vessel.mcr,
                "sfc": vessel.sfc,
                "fuel_type": vessel.fuel,
                "speed": vessel.speed,
                "pae": vessel.pae,
                "sfc_ae": vessel.sfc_ae,
                "fuel_type_ae": vessel.fuel_ae,
                "f_eff": vessel.f_eff,
                "f_i": vessel.f_i,
                "f_w": vessel.f_w,
            }
            result_data = calculate_eexi(input_data)
            pdf_path = generate_pdf_report(vessel.to_dict(), result_data)
        else:
            # Otherwise assume data has both input and result
            pdf_path = generate_pdf_report(data, data)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"EEXI_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reports_bp.route("/cii-report", methods=["POST"])
def cii_report():
    data = request.get_json(force=True, silent=True)
    try:
        pdf_path = generate_cii_pdf_report({}, data)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"CII_Report_{data.get('year', '2024')}.pdf",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reports_bp.route("/egbp-report", methods=["POST"])
def egbp_report():
    data = request.get_json(force=True, silent=True)
    try:
        pdf_path = generate_egbp_pdf_report(data)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"EGBP_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@reports_bp.route("/pipe-report", methods=["POST"])
def pipe_report():
    data = request.get_json(force=True, silent=True)
    try:
        input_data = data.get("input_data", {})
        result_data = data.get("result_data", {})
        pdf_path = generate_pipe_pdf_report(input_data, result_data)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"Pipe_Wall_Report_{datetime.now().strftime('%Y%m%d')}.pdf",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# History report endpoints
@reports_bp.route("/eexi-report-history/<int:vessel_id>", methods=["GET"])
def eexi_report_history(vessel_id):
    vessel = Vessel.query.get_or_404(vessel_id)
    data = {
        "ship_type": vessel.ship_type,
        "dwt": vessel.dwt,
        "gt": vessel.gt,
        "mcr": vessel.mcr,
        "sfc": vessel.sfc,
        "fuel_type": vessel.fuel,
        "speed": vessel.speed,
        "pae": vessel.pae,
        "sfc_ae": vessel.sfc_ae,
        "fuel_type_ae": vessel.fuel_ae,
        "f_eff": vessel.f_eff,
        "f_i": vessel.f_i,
        "f_w": vessel.f_w,
    }
    result = calculate_eexi(data)
    pdf_path = generate_pdf_report(vessel.to_dict(), result)
    return send_file(
        pdf_path,
        as_attachment=True,
        download_name=f"EEXI_Report_{vessel_id}.pdf",
    )


@reports_bp.route("/cii-report-history/<int:calc_id>", methods=["GET"])
def cii_report_history(calc_id):
    calc = CIICalculation.query.get_or_404(calc_id)
    if not calc.full_data:
        return "No data available for this report", 404
    data = json.loads(calc.full_data)
    try:
        pdf_path = generate_cii_pdf_report({}, data)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"CII_Report_{calc.year}.pdf",
        )
    except Exception as e:
        return str(e), 500


@reports_bp.route("/egbp-report-history/<int:calc_id>", methods=["GET"])
def egbp_report_history(calc_id):
    calc = EGBPCalculation.query.get_or_404(calc_id)
    if not calc.full_data:
        return "No data available for this report", 404
    data = json.loads(calc.full_data)
    try:
        pdf_path = generate_egbp_pdf_report(data)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"EGBP_Report.pdf",
        )
    except Exception as e:
        return str(e), 500


@reports_bp.route("/pipe-report-history/<int:calc_id>", methods=["GET"])
def pipe_report_history(calc_id):
    calc = PipeWallCalculation.query.get_or_404(calc_id)
    if not calc.full_data:
        return "No data available for this report", 404
    data = json.loads(calc.full_data)
    input_data = {
        "nps": calc.nps,
        "pressure_mpa": calc.pressure_mpa,
        "temp_c": calc.temp_c,
        "material": calc.material,
        "weld_type": calc.weld_type,
        "corrosion_mm": calc.corrosion_mm,
        "threaded": calc.threaded,
        "mill_tolerance": calc.mill_tolerance,
    }
    try:
        pdf_path = generate_pipe_pdf_report(input_data, data)
        return send_file(
            pdf_path,
            as_attachment=True,
            download_name=f"Pipe_Wall_Report_{calc_id}.pdf",
        )
    except Exception as e:
        return str(e), 500


# Add missing import for calculate_eexi
from app.calculators.eexi import calculate_eexi
