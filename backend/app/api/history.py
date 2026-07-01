from flask import Blueprint, jsonify
from app.database.db import (
    db,
    Vessel,
    CIICalculation,
    EGBPCalculation,
    PipeWallCalculation,
    LinearInterpolatorCalculation,
)

history_bp = Blueprint("history", __name__, url_prefix="/api")


@history_bp.route("/history", methods=["GET"])
def get_history():
    eexi = Vessel.query.order_by(Vessel.created_at.desc()).all()
    cii = CIICalculation.query.order_by(CIICalculation.created_at.desc()).all()
    egbp = EGBPCalculation.query.order_by(EGBPCalculation.created_at.desc()).all()
    pipe = PipeWallCalculation.query.order_by(PipeWallCalculation.created_at.desc()).all()
    interpolator = LinearInterpolatorCalculation.query.order_by(
        LinearInterpolatorCalculation.created_at.desc()
    ).all()

    all_calcs = (
        [v.to_dict() for v in eexi]
        + [c.to_dict() for c in cii]
        + [e.to_dict() for e in egbp]
        + [p.to_dict() for p in pipe]
        + [i.to_dict() for i in interpolator]
    )
    all_calcs.sort(key=lambda x: x.get("created_at_raw", ""), reverse=True)
    return jsonify(all_calcs)
