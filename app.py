import os
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from database.db import db, init_db, Vessel, CIICalculation, EGBPCalculation
from calculators.eexi import calculate_eexi
from calculators.cii import calculate_cii, CII_REDUCTION_FACTORS
from calculators.egbp import calculate_egbp, ELEMENT_LABELS, ENGINE_PRESETS, ROUGHNESS_MAP
from calculators.utils.validators import validate_inputs
from calculators.utils.ship_params import SHIP_LABELS, CF_LABELS
from reports.pdf_generator import generate_pdf_report, generate_cii_pdf_report, generate_egbp_pdf_report

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vessels.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_db(app)

@app.context_processor
def inject_now():
    return dict(
        now=datetime.now(), 
        SHIP_LABELS=SHIP_LABELS, 
        CF_LABELS=CF_LABELS,
        version="2.0.0"
    )

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    if request.method == 'GET':
        return redirect(url_for('index'))
        
    data = request.form.to_dict()
    is_valid, error_msg = validate_inputs(data)
    if not is_valid:
        return render_template('index.html', error=error_msg, form_data=data)
    
    result = calculate_eexi(data)
    
    vessel = Vessel(
        name=data.get('vessel_name'),
        ship_type=data['ship_type'],
        dwt=float(data.get('dwt', 0) or 0),
        gt=float(data.get('gt', 0) or 0),
        mcr=float(data['mcr']),
        sfc=float(data['sfc']),
        fuel=data['fuel_type'],
        speed=float(data['speed']),
        pae=float(data.get('pae', 0) or 0),
        sfc_ae=float(data.get('sfc_ae', 0) or 0),
        fuel_ae=data.get('fuel_type_ae') if data.get('fuel_type_ae') else data['fuel_type'],
        f_eff=float(data.get('f_eff', 1.0) or 1.0),
        f_i=float(data.get('f_i', 1.0) or 1.0),
        f_w=float(data.get('f_w', 1.0) or 1.0),
        attained_eexi=result['attained_eexi'],
        required_eexi=result['required_eexi'],
        status=result['status'],
        margin=result['margin'],
        user_local_time=data.get('user_local_time')
    )
    db.session.add(vessel)
    db.session.commit()
    
    result['vessel_id'] = vessel.id
    result['vessel_name'] = vessel.name
    return render_template('result.html', result=result)

@app.route('/history')
def history():
    eexi = Vessel.query.order_by(Vessel.created_at.desc()).all()
    cii = CIICalculation.query.order_by(CIICalculation.created_at.desc()).all()
    egbp = EGBPCalculation.query.order_by(EGBPCalculation.created_at.desc()).all()
    
    all_calcs = [v.to_dict() for v in eexi] + [c.to_dict() for c in cii] + [e.to_dict() for e in egbp]
    all_calcs.sort(key=lambda x: x['created_at'], reverse=True)
    
    return render_template('history.html', vessels=all_calcs)

@app.route('/manual')
def manual():
    return render_template('manual.html')

@app.route('/cii')
def cii_page():
    return render_template('cii.html', cii_years=sorted(CII_REDUCTION_FACTORS.keys()))

@app.route('/egbp')
def egbp_page():
    return render_template('egbp.html', 
                         element_types=ELEMENT_LABELS,
                         engine_presets=ENGINE_PRESETS,
                         roughness_options=ROUGHNESS_MAP)

@app.route('/admin')
def admin_dashboard():
    vessels = Vessel.query.all()
    stats = {
        'total_calculations': len(vessels),
        'compliant_count': len([v for v in vessels if v.status == 'COMPLIANT']),
        'non_compliant_count': len([v for v in vessels if v.status == 'NON_COMPLIANT']),
    }
    return render_template('admin.html', stats=stats, recent_vessels=vessels[-10:])

import json

@app.route('/api/calculate-cii', methods=['POST'])
def api_calculate_cii():
    data = request.get_json(force=True, silent=True)
    if not data: return jsonify({"error": "Invalid JSON"}), 400
    try:
        result = calculate_cii(data)
        
        # Save to history
        cii_calc = CIICalculation(
            ship_type=data['ship_type'],
            year=data['year'],
            attained_cii=result['attained_cii'],
            required_cii=result['required_cii'],
            rating=result['rating']['rating'],
            margin_pct=result['rating']['margin_pct'],
            full_data=json.dumps(result)
        )
        db.session.add(cii_calc)
        db.session.commit()
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/calculate-egbp', methods=['POST'])
def api_calculate_egbp():
    data = request.get_json(force=True, silent=True)
    if not data: return jsonify({"error": "Invalid JSON"}), 400
    try:
        result = calculate_egbp(data)
        
        # Save to history
        egbp_calc = EGBPCalculation(
            mass_flow=float(data['mass_flow_kgs']),
            temperature=float(data['temp_tc_c']),
            total_pa=result['total_pressure_pa'],
            max_bp=float(data['max_bp_pa']),
            status=result['status'],
            full_data=json.dumps(result)
        )
        db.session.add(egbp_calc)
        db.session.commit()
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/cii-report-history/<int:calc_id>')
def cii_report_history(calc_id):
    calc = CIICalculation.query.get_or_404(calc_id)
    if not calc.full_data:
        return "No data available for this report", 404
    data = json.loads(calc.full_data)
    try:
        pdf_path = generate_cii_pdf_report({}, data)
        return send_file(pdf_path, as_attachment=True, download_name=f"CII_Report_{calc.year}.pdf")
    except Exception as e:
        return str(e), 500

@app.route('/egbp-report-history/<int:calc_id>')
def egbp_report_history(calc_id):
    calc = EGBPCalculation.query.get_or_404(calc_id)
    if not calc.full_data:
        return "No data available for this report", 404
    data = json.loads(calc.full_data)
    try:
        pdf_path = generate_egbp_pdf_report(data)
        return send_file(pdf_path, as_attachment=True, download_name=f"EGBP_Report.pdf")
    except Exception as e:
        return str(e), 500

@app.route('/api/cii-report', methods=['POST'])
def cii_report():
    data = request.get_json(force=True, silent=True)
    try:
        pdf_path = generate_cii_pdf_report({}, data)
        return send_file(pdf_path, as_attachment=True, download_name=f"CII_Report_{data.get('year', '2024')}.pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/egbp-report', methods=['POST'])
def egbp_report():
    data = request.get_json(force=True, silent=True)
    try:
        pdf_path = generate_egbp_pdf_report(data)
        return send_file(pdf_path, as_attachment=True, download_name=f"EGBP_Report_{datetime.now().strftime('%Y%m%d')}.pdf")
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/report/<int:vessel_id>')
def report(vessel_id):
    vessel = Vessel.query.get_or_404(vessel_id)
    data = {
        'ship_type': vessel.ship_type, 'dwt': vessel.dwt, 'gt': vessel.gt,
        'mcr': vessel.mcr, 'sfc': vessel.sfc, 'fuel_type': vessel.fuel,
        'speed': vessel.speed, 'pae': vessel.pae, 'sfc_ae': vessel.sfc_ae,
        'fuel_type_ae': vessel.fuel_ae, 'f_eff': vessel.f_eff, 'f_i': vessel.f_i, 'f_w': vessel.f_w
    }
    result = calculate_eexi(data)
    pdf_path = generate_pdf_report(vessel.to_dict(), result)
    return send_file(pdf_path, as_attachment=True, download_name=f"EEXI_Report_{vessel_id}.pdf")

if __name__ == '__main__':
    app.run(debug=True)
