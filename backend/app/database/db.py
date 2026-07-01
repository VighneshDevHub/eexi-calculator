from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone

db = SQLAlchemy()

class Vessel(db.Model):
    __tablename__ = 'vessels'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    ship_type = db.Column(db.String(50), nullable=False)
    dwt = db.Column(db.Float, nullable=True)
    gt = db.Column(db.Float, nullable=True)
    
    # Main Engine
    mcr = db.Column(db.Float, nullable=False)
    sfc = db.Column(db.Float, nullable=False)
    fuel = db.Column(db.String(20), nullable=False)
    speed = db.Column(db.Float, nullable=False)
    
    # Auxiliary Engine (Optional)
    pae = db.Column(db.Float, nullable=True, default=0.0)
    sfc_ae = db.Column(db.Float, nullable=True, default=0.0)
    fuel_ae = db.Column(db.String(20), nullable=True)
    
    # Correction Factors
    f_eff = db.Column(db.Float, nullable=True, default=1.0)
    f_i = db.Column(db.Float, nullable=True, default=1.0)
    f_w = db.Column(db.Float, nullable=True, default=1.0)
    
    # Results
    attained_eexi = db.Column(db.Float, nullable=False)
    required_eexi = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    margin = db.Column(db.Float, nullable=True)
    
    # Timing
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_local_time = db.Column(db.String(50), nullable=True) # To store time exactly as seen by user

    def to_dict(self):
        return {
            'id': self.id,
            'calc_type': 'EEXI',
            'name': self.name or 'Unnamed Vessel',
            'ship_type': self.ship_type,
            'dwt': self.dwt,
            'gt': self.gt,
            'mcr': self.mcr,
            'sfc': self.sfc,
            'fuel': self.fuel,
            'speed': self.speed,
            'pae': self.pae,
            'sfc_ae': self.sfc_ae,
            'fuel_ae': self.fuel_ae,
            'f_eff': self.f_eff,
            'f_i': self.f_i,
            'f_w': self.f_w,
            'attained': self.attained_eexi,
            'required': self.required_eexi,
            'attained_eexi': self.attained_eexi,
            'required_eexi': self.required_eexi,
            'status': self.status,
            'margin': self.margin,
            'created_at_raw': self.created_at.isoformat(),
            'created_at': self.user_local_time if self.user_local_time else self.created_at.strftime('%Y-%m-%d %H:%M')
        }

class CIICalculation(db.Model):
    __tablename__ = 'cii_calculations'
    id = db.Column(db.Integer, primary_key=True)
    ship_type = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    attained_cii = db.Column(db.Float, nullable=False)
    required_cii = db.Column(db.Float, nullable=False)
    rating = db.Column(db.String(1), nullable=False)
    margin_pct = db.Column(db.Float, nullable=True)
    full_data = db.Column(db.Text, nullable=True) # JSON string
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'calc_type': 'CII',
            'name': f"{self.ship_type.replace('_', ' ').title()} ({self.year})",
            'ship_type': self.ship_type,
            'attained': round(self.attained_cii, 4),
            'required': round(self.required_cii, 4),
            'status': f"RATING {self.rating}",
            'margin': self.margin_pct,
            'created_at_raw': self.created_at.isoformat(),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

class EGBPCalculation(db.Model):
    __tablename__ = 'egbp_calculations'
    id = db.Column(db.Integer, primary_key=True)
    mass_flow = db.Column(db.Float, nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    total_pa = db.Column(db.Float, nullable=False)
    max_bp = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False)
    full_data = db.Column(db.Text, nullable=True) # JSON string
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'calc_type': 'EGBP',
            'name': f"Back Pressure Test",
            'ship_type': f"{self.mass_flow} kg/s @ {self.temperature}°C",
            'attained': f"{int(self.total_pa)} Pa",
            'required': f"{int(self.max_bp)} Pa",
            'status': self.status,
            'margin': round(self.max_bp - self.total_pa, 0),
            'created_at_raw': self.created_at.isoformat(),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

class PipeWallCalculation(db.Model):
    __tablename__ = 'pipe_wall_calculations'
    id = db.Column(db.Integer, primary_key=True)
    nps = db.Column(db.Float, nullable=False)
    pressure_mpa = db.Column(db.Float, nullable=False)
    temp_c = db.Column(db.Float, nullable=False)
    material = db.Column(db.String(50), nullable=False)
    weld_type = db.Column(db.String(20), nullable=False)
    corrosion_mm = db.Column(db.Float, nullable=True, default=0.0)
    threaded = db.Column(db.Boolean, nullable=False, default=False)
    mill_tolerance = db.Column(db.Float, nullable=False, default=12.5)
    t_dis_mm = db.Column(db.Float, nullable=False)
    t_req_mm = db.Column(db.Float, nullable=False)
    t_min_mm = db.Column(db.Float, nullable=False)
    S_mpa = db.Column(db.Float, nullable=False)
    dext_mm = db.Column(db.Float, nullable=False)
    recommended_schedule = db.Column(db.String(20), nullable=True)
    available_thickness_mm = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(20), nullable=False)
    full_data = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'calc_type': 'Pipe Wall',
            'name': f"Pipe NPS {self.nps}",
            'ship_type': f"{self.material} @ {self.pressure_mpa} MPa",
            'attained': f"{self.t_min_mm:.2f} mm",
            'required': f"{self.available_thickness_mm:.2f} mm" if self.available_thickness_mm else "N/A",
            'status': self.status,
            'margin': (self.available_thickness_mm - self.t_min_mm) if self.available_thickness_mm else None,
            'created_at_raw': self.created_at.isoformat(),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

class LinearInterpolatorCalculation(db.Model):
    __tablename__ = 'linear_interpolator_calculations'
    id = db.Column(db.Integer, primary_key=True)
    x1 = db.Column(db.Float, nullable=True)
    y1 = db.Column(db.Float, nullable=True)
    x2 = db.Column(db.Float, nullable=True)
    y2 = db.Column(db.Float, nullable=True)
    x3 = db.Column(db.Float, nullable=True)
    y3 = db.Column(db.Float, nullable=True)
    blank_field = db.Column(db.String(10), nullable=False)
    result = db.Column(db.Float, nullable=False)
    formula_used = db.Column(db.String(200), nullable=False)
    full_data = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'calc_type': 'Interpolator',
            'name': f"Linear Interpolation",
            'ship_type': f"x1={self.x1}, y1={self.y1}, x2={self.x2}, y2={self.y2}",
            'attained': f"{self.result:.2f}",
            'required': f"Find {self.blank_field}",
            'status': 'COMPLETED',
            'margin': None,
            'created_at_raw': self.created_at.isoformat(),
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M')
        }

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
