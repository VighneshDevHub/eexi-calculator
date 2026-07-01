from flask import Blueprint, jsonify
from database.db import (
    Vessel,
    CIICalculation,
    EGBPCalculation,
    PipeWallCalculation,
    LinearInterpolatorCalculation,
)

admin_bp = Blueprint("admin", __name__, url_prefix="/api")


@admin_bp.route("/admin/stats", methods=["GET"])
def get_admin_stats():
    vessels = Vessel.query.all()
    cii = CIICalculation.query.all()
    egbp = EGBPCalculation.query.all()
    pipe = PipeWallCalculation.query.all()
    interpolator = LinearInterpolatorCalculation.query.all()

    total = len(vessels) + len(cii) + len(egbp) + len(pipe) + len(interpolator)
    compliant = len([v for v in vessels if v.status == "COMPLIANT"])
    non_compliant = len([v for v in vessels if v.status == "NON_COMPLIANT"])
    recent = list(reversed(vessels[-10:]))

    return jsonify({
        "total_calculations": total,
        "compliant_count": compliant,
        "non_compliant_count": non_compliant,
        "recent_vessels": [v.to_dict() for v in recent],
    })
