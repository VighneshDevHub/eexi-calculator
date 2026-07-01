import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from flask_cors import CORS
from flask_talisman import Talisman
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_migrate import Migrate
from werkzeug.exceptions import HTTPException
from app.config import Config
from app.database.db import db, init_db, Vessel, CIICalculation, EGBPCalculation, PipeWallCalculation, LinearInterpolatorCalculation
from app.calculators.eexi import calculate_eexi
from app.calculators.cii import calculate_cii, CII_REDUCTION_FACTORS
from app.calculators.egbp import calculate_egbp, ELEMENT_LABELS, ENGINE_PRESETS, ROUGHNESS_MAP
from app.calculators.pipe_wall import calculate_pipe_wall, MATERIAL_LABELS, WELD_LABELS
from app.calculators.utils.validators import validate_inputs
from app.calculators.utils.ship_params import SHIP_LABELS, CF_LABELS
from app.reports.pdf_generator import generate_pdf_report, generate_cii_pdf_report, generate_egbp_pdf_report, generate_pipe_pdf_report
from app.api.calculators import calculators_bp
from app.api.constants import constants_bp
from app.api.reports import reports_bp
from app.api.history import history_bp
from app.api.admin import admin_bp
from app.utils.logger import setup_logger

# Initialize logger
logger = setup_logger()

# Create Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Configure CORS properly
CORS(app, resources={
    r"/api/*": {
        "origins": app.config["CORS_ALLOWED_ORIGINS"],
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Configure session cookie security
app.config.update(
    SESSION_COOKIE_SECURE=app.config["FLASK_ENV"] == "production",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax"
)

# Security headers with Talisman
Talisman(app, 
    content_security_policy=None,
    force_https=False  # Disable for dev, enable in prod behind reverse proxy
)

# Rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=[app.config["RATE_LIMIT_DEFAULT"]],
    storage_uri=app.config["RATE_LIMIT_STORAGE_URI"]
)

# Initialize database
init_db(app)

# Initialize Flask-Migrate for database migrations
migrate = Migrate(app, db)

# Register blueprints
app.register_blueprint(calculators_bp)
app.register_blueprint(constants_bp)
app.register_blueprint(reports_bp)
app.register_blueprint(history_bp)
app.register_blueprint(admin_bp)


# Error handlers
@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    if isinstance(e, HTTPException):
        return jsonify(error=str(e.description)), e.code
    return jsonify(error="Internal server error"), 500


@app.errorhandler(404)
def not_found(e):
    return jsonify(error="Resource not found"), 404


@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify(error="Rate limit exceeded"), 429


# Health check endpoint
@app.route('/health')
def health_check():
    return jsonify(status="healthy", timestamp=datetime.utcnow().isoformat()), 200


@app.route('/api/health')
def api_health_check():
    # Check database connection
    try:
        db.session.execute('SELECT 1')
        db_status = "healthy"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "unhealthy"
    
    return jsonify(
        status="healthy" if db_status == "healthy" else "degraded",
        database=db_status,
        timestamp=datetime.utcnow().isoformat()
    ), 200 if db_status == "healthy" else 503

# Legacy template routes are commented out - using Next.js frontend exclusively
# @app.context_processor
# def inject_now():
#     return dict(
#         now=datetime.now(), 
#         SHIP_LABELS=SHIP_LABELS, 
#         CF_LABELS=CF_LABELS,
#         version="2.0.0"
#     )

# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/calculate', methods=['GET', 'POST'])
# def calculate():
#     if request.method == 'GET':
#         return redirect(url_for('index'))
#     
#     data = request.form.to_dict()
#     is_valid, error_msg = validate_inputs(data)
#     if not is_valid:
#         logger.warning(f"Invalid input for EEXI calculation: {error_msg}")
#         return render_template('index.html', error=error_msg, form_data=data)
# 
#     logger.info("Starting EEXI calculation", extra={"ship_type": data.get('ship_type')})
#     try:
#         result = calculate_eexi(data)
#         
#         vessel = Vessel(
#             name=data.get('vessel_name'),
#             ship_type=data['ship_type'],
#             dwt=float(data.get('dwt', 0) or 0),
#             gt=float(data.get('gt', 0) or 0),
#             mcr=float(data['mcr']),
#             sfc=float(data['sfc']),
#             fuel=data['fuel_type'],
#             speed=float(data['speed']),
#             pae=float(data.get('pae', 0) or 0),
#             sfc_ae=float(data.get('sfc_ae', 0) or 0),
#             fuel_ae=data.get('fuel_type_ae') if data.get('fuel_type_ae') else data['fuel_type'],
#             f_eff=float(data.get('f_eff', 1.0) or 1.0),
#             f_i=float(data.get('f_i', 1.0) or 1.0),
#             f_w=float(data.get('f_w', 1.0) or 1.0),
#             attained_eexi=result['attained_eexi'],
#             required_eexi=result['required_eexi'],
#             status=result['status'],
#             margin=result['margin'],
#             user_local_time=data.get('user_local_time')
#         )
#         db.session.add(vessel)
#         db.session.commit()
#         
#         logger.info("EEXI calculation completed", extra={"vessel_id": vessel.id, "status": result['status']})
#         
#         result['vessel_id'] = vessel.id
#         result['vessel_name'] = vessel.name
#         return render_template('result.html', result=result)
#     except Exception as e:
#         logger.error(f"EEXI calculation failed: {str(e)}", exc_info=True)
#         return render_template('index.html', error="Calculation failed. Please try again.", form_data=data)

# @app.route('/history')
# def history():
#     eexi = Vessel.query.order_by(Vessel.created_at.desc()).all()
#     cii = CIICalculation.query.order_by(CIICalculation.created_at.desc()).all()
#     egbp = EGBPCalculation.query.order_by(EGBPCalculation.created_at.desc()).all()
#     pipe_wall = PipeWallCalculation.query.order_by(PipeWallCalculation.created_at.desc()).all()
#     interpolator = LinearInterpolatorCalculation.query.order_by(LinearInterpolatorCalculation.created_at.desc()).all()
#     
#     all_calcs = (
#         [v.to_dict() for v in eexi] + 
#         [c.to_dict() for c in cii] + 
#         [e.to_dict() for e in egbp] +
#         [p.to_dict() for p in pipe_wall] +
#         [i.to_dict() for i in interpolator]
#     )
#     # Re-sort because we merged multiple sorted lists
#     all_calcs.sort(key=lambda x: x.get('created_at_raw', ''), reverse=True)
#     
#     return render_template('history.html', vessels=all_calcs)

# @app.route('/manual')
# def manual():
#     return render_template('manual.html')

# @app.route('/cii')
# def cii_page():
#     return render_template('cii.html', cii_years=sorted(CII_REDUCTION_FACTORS.keys()))

# @app.route('/egbp')
# def egbp_page():
#     return render_template('egbp.html', 
#                          element_types=ELEMENT_LABELS,
#                          engine_presets=ENGINE_PRESETS,
#                          roughness_options=ROUGHNESS_MAP)

# @app.route('/pipe')
# def pipe_page():
#     from app.calculators.pipe_wall import NPS_DEXT_MM, MATERIAL_LABELS, WELD_LABELS
#     nps_options = sorted(NPS_DEXT_MM.keys())
#     material_options = MATERIAL_LABELS
#     weld_options = WELD_LABELS
#     return render_template('pipe.html', 
#                          nps_options=nps_options,
#                          material_options=material_options,
#                          weld_options=weld_options,
#                          material_options_json=json.dumps(material_options),
#                          nps_dext_json=json.dumps(NPS_DEXT_MM),
#                          weld_options_json=json.dumps(weld_options))

# @app.route('/interpolator')
# def interpolator_page():
#     return render_template('interpolator.html')

# @app.route('/calculate-egbp', methods=['POST'])
# def api_calculate_egbp():
#     try:
#         data = request.get_json()
#         if not data:
#             return jsonify({"error": "Missing input data"}), 400
#         
#         result = calculate_egbp(data)
#         
#         # Save to history
#         calc = EGBPCalculation(
#             mass_flow=float(data['mass_flow_kgs']),
#             temperature=float(data['temp_tc_c']),
#             total_pa=result['total_pressure_pa'],
#             max_bp=float(data['max_bp_pa']),
#             status=result['status'],
#             full_data=json.dumps(result)
#         )
#         db.session.add(calc)
#         db.session.commit()
#         
#         result['id'] = calc.id
#         return jsonify(result)
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/admin')
# def admin_dashboard():
#     vessels = Vessel.query.all()
#     stats = {
#         'total_calculations': len(vessels),
#         'compliant_count': len([v for v in vessels if v.status == 'COMPLIANT']),
#         'non_compliant_count': len([v for v in vessels if v.status == 'NON_COMPLIANT']),
#     }
#     return render_template('admin.html', stats=stats, recent_vessels=vessels[-10:], vessels=vessels)

# @app.route('/api/calculate-cii', methods=['POST'])
# def api_calculate_cii():
#     data = request.get_json(force=True, silent=True)
#     if not data: return jsonify({"error": "Invalid JSON"}), 400
#     try:
#         result = calculate_cii(data)
#         
#         # Save to history
#         cii_calc = CIICalculation(
#             ship_type=data['ship_type'],
#             year=data['year'],
#             attained_cii=result['attained_cii'],
#             required_cii=result['required_cii'],
#             rating=result['rating']['rating'],
#             margin_pct=result['rating']['margin_pct'],
#             full_data=json.dumps(result)
#         )
#         db.session.add(cii_calc)
#         db.session.commit()
#         
#         return jsonify(result), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/cii-report-history/<int:calc_id>')
# def cii_report_history(calc_id):
#     calc = CIICalculation.query.get_or_404(calc_id)
#     if not calc.full_data:
#         return "No data available for this report", 404
#     data = json.loads(calc.full_data)
#     try:
#         pdf_path = generate_cii_pdf_report({}, data)
#         return send_file(pdf_path, as_attachment=True, download_name=f"CII_Report_{calc.year}.pdf")
#     except Exception as e:
#         return str(e), 500

# @app.route('/egbp-report-history/<int:calc_id>')
# def egbp_report_history(calc_id):
#     calc = EGBPCalculation.query.get_or_404(calc_id)
#     if not calc.full_data:
#         return "No data available for this report", 404
#     data = json.loads(calc.full_data)
#     try:
#         pdf_path = generate_egbp_pdf_report(data)
#         return send_file(pdf_path, as_attachment=True, download_name=f"EGBP_Report.pdf")
#     except Exception as e:
#         return str(e), 500

# @app.route('/api/cii-report', methods=['POST'])
# def cii_report():
#     data = request.get_json(force=True, silent=True)
#     try:
#         pdf_path = generate_cii_pdf_report({}, data)
#         return send_file(pdf_path, as_attachment=True, download_name=f"CII_Report_{data.get('year', '2024')}.pdf")
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/api/egbp-report', methods=['POST'])
# def egbp_report():
#     data = request.get_json(force=True, silent=True)
#     try:
#         pdf_path = generate_egbp_pdf_report(data)
#         return send_file(pdf_path, as_attachment=True, download_name=f"EGBP_Report_{datetime.now().strftime('%Y%m%d')}.pdf")
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route('/report/<int:vessel_id>')
# def report(vessel_id):
#     vessel = Vessel.query.get_or_404(vessel_id)
#     data = {
#         'ship_type': vessel.ship_type, 'dwt': vessel.dwt, 'gt': vessel.gt,
#         'mcr': vessel.mcr, 'sfc': vessel.sfc, 'fuel_type': vessel.fuel,
#         'speed': vessel.speed, 'pae': vessel.pae, 'sfc_ae': vessel.sfc_ae,
#         'fuel_type_ae': vessel.fuel_ae, 'f_eff': vessel.f_eff, 'f_i': vessel.f_i, 'f_w': vessel.f_w
#     }
#     result = calculate_eexi(data)
#     pdf_path = generate_pdf_report(vessel.to_dict(), result)
#     return send_file(pdf_path, as_attachment=True, download_name=f"EEXI_Report_{vessel_id}.pdf")

if __name__ == '__main__':
    app.run(debug=True)
