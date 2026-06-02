import os
from flask import Flask, render_template, request, jsonify, send_file, redirect, url_for
from database.db import db, init_db, Vessel
from eexi.calculator import calculate_eexi
from eexi.validators import validate_inputs
from reports.pdf_generator import generate_pdf_report
from eexi.ship_params import SHIP_LABELS, CF_LABELS

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vessels.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
init_db(app)

@app.context_processor
def inject_labels():
    return dict(SHIP_LABELS=SHIP_LABELS, CF_LABELS=CF_LABELS)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['GET', 'POST'])
def calculate():
    if request.method == 'GET':
        return redirect(url_for('index'))
        
    data = request.form.to_dict()
    
    # Validate inputs
    is_valid, error_msg = validate_inputs(data)
    if not is_valid:
        return render_template('index.html', error=error_msg, form_data=data)
    
    # Perform calculation
    result = calculate_eexi(data)
    
    # Save to database
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
    
    # Store ID in result for PDF generation
    result['vessel_id'] = vessel.id
    result['vessel_name'] = vessel.name
    
    return render_template('result.html', result=result)

@app.route('/history')
def history():
    vessels = Vessel.query.order_by(Vessel.created_at.desc()).all()
    return render_template('history.html', vessels=[v.to_dict() for v in vessels])

@app.route('/manual')
def manual():
    return render_template('manual.html')

@app.route('/report/<int:vessel_id>')
def report(vessel_id):
    vessel = Vessel.query.get_or_404(vessel_id)
    
    # Re-calculate result for report generation
    data = {
        'ship_type': vessel.ship_type,
        'dwt': vessel.dwt,
        'gt': vessel.gt,
        'mcr': vessel.mcr,
        'sfc': vessel.sfc,
        'fuel_type': vessel.fuel,
        'speed': vessel.speed,
        'pae': vessel.pae,
        'sfc_ae': vessel.sfc_ae,
        'fuel_type_ae': vessel.fuel_ae,
        'f_eff': vessel.f_eff,
        'f_i': vessel.f_i,
        'f_w': vessel.f_w
    }
    result = calculate_eexi(data)
    
    pdf_path = generate_pdf_report(vessel.to_dict(), result)
    
    return send_file(pdf_path, as_attachment=True, download_name=f"EEXI_Report_{vessel_id}.pdf")

if __name__ == '__main__':
    app.run(debug=True)
