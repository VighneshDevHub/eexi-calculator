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
            'name': self.name,
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
            'attained_eexi': self.attained_eexi,
            'required_eexi': self.required_eexi,
            'status': self.status,
            'margin': self.margin,
            'created_at': self.user_local_time if self.user_local_time else self.created_at.strftime('%Y-%m-%d %H:%M:%S UTC')
        }

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
