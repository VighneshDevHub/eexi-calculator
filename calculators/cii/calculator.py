"""
calculators/cii/calculator.py
-----------
Carbon Intensity Indicator (CII) calculation module.
Based on IMO Resolutions MEPC.352-355(78).
"""

from ..utils.ship_params import CF_MAP

# ---------------------------------------------------------------------------
# CII REFERENCE LINE PARAMETERS  — MEPC.353(78)
# Required CII = a × DWT^(-c)   [gCO2 / (capacity unit · nm)]
# Capacity units: DWT for most; GT for passenger/cruise/ro-ro passenger
# ---------------------------------------------------------------------------
CII_REF_PARAMS: dict = {
    #  ship_type        a          c       cap_mode
    "bulk_carrier":  (4745.0,   0.622,  "dwt"),
    "tanker":        (5247.0,   0.610,  "dwt"),
    "container":     (1984.0,   0.489,  "dwt"),
    "general_cargo": (31948.0,  0.792,  "dwt"),
    "ro_ro_cargo":   (10952.0,  0.637,  "dwt"),
    "ro_ro_pass":    (7540.0,   0.587,  "gt"),
    "lng_carrier":   (144050.0, 0.865,  "dwt"),
    "gas_carrier":   (8104.0,   0.639,  "dwt"),
    "cruise":        (930.0,    0.383,  "gt"),
}

# ---------------------------------------------------------------------------
# CII REDUCTION FACTORS (dd) by year — MEPC.328(76) Table 1
# Required CII = Reference CII × (1 - dd/100)
# dd values relative to 2019 baseline
# ---------------------------------------------------------------------------
CII_REDUCTION_FACTORS: dict = {
    2023: 5,
    2024: 7,
    2025: 9,
    2026: 11,
    # 2027+ under review per MEPC.354(78) reg. 28.11 (review by Jan 2026)
    2027: 11,
}

# ---------------------------------------------------------------------------
# CII RATING BOUNDARIES — MEPC.354(78)
# Superior boundary = exp(d1) × required CII
# Lower boundary    = exp(d2) × required CII   etc.
# d-vector per ship type [d1, d2, d3, d4]
# A ≤ d1 < B ≤ d2 < C ≤ d3 < D ≤ d4 < E
# ---------------------------------------------------------------------------
CII_RATING_BOUNDARIES: dict = {
    "bulk_carrier":  [-0.86, -0.36, 0.00,  0.27],
    "tanker":        [-0.72, -0.29, 0.00,  0.20],
    "container":     [-0.83, -0.37, 0.00,  0.27],
    "general_cargo": [-1.19, -0.51, 0.00,  0.31],
    "ro_ro_cargo":   [-0.56, -0.23, 0.00,  0.32],
    "ro_ro_pass":    [-0.61, -0.25, 0.00,  0.32],
    "lng_carrier":   [-0.95, -0.30, 0.00,  0.28],
    "gas_carrier":   [-0.78, -0.28, 0.00,  0.31],
    "cruise":        [-0.83, -0.37, 0.00,  0.27],
}

def calc_af_tanker_sts(dwt: float) -> float:
    if dwt <= 0:
        raise ValueError("DWT must be positive for STS correction factor.")
    return 6.1742 * (dwt ** -0.246)

def calc_af_tanker_shuttle(dwt: float) -> float:
    if dwt <= 0:
        raise ValueError("DWT must be positive for shuttle tanker correction factor.")
    return 5.6805 * (dwt ** -0.208)

def calc_fc_electrical_reefer_monitored(reefer_kwh: float, sfoc: float) -> float:
    return reefer_kwh * sfoc

def calc_fc_electrical_reefer_unmonitored(reefer_days_sea: float, reefer_days_port: float, sfoc_avg: float, cx: float = 2.75) -> float:
    return cx * 24 * sfoc_avg * (reefer_days_sea + reefer_days_port)

def calc_attained_cii(
    fc_j: dict,
    distance_nm: float,
    capacity: float,
    fc_voyage_j: dict | None = None,
    tf_j: dict | None = None,
    fc_electrical_j: dict | None = None,
    fc_boiler_j: dict | None = None,
    fc_others_j: dict | None = None,
    dx: float = 0.0,
    year: int = 2024,
) -> float:
    yi = max(0, year - 2023)
    fc_voyage_j     = fc_voyage_j     or {}
    tf_j            = tf_j            or {}
    fc_electrical_j = fc_electrical_j or {}
    fc_boiler_j     = fc_boiler_j     or {}
    fc_others_j     = fc_others_j     or {}

    numerator = 0.0
    for fuel, fc in fc_j.items():
        cf = CF_MAP.get(fuel, 3.114)
        voyage_ded   = fc_voyage_j.get(fuel, 0.0)
        tf_ded       = tf_j.get(fuel, 0.0)
        elec_ded  = fc_electrical_j.get(fuel, 0.0)
        boil_ded  = fc_boiler_j.get(fuel, 0.0)
        other_ded = fc_others_j.get(fuel, 0.0)

        correction_factor_term = (0.75 - 0.03 * yi) * (elec_ded + boil_ded + other_ded)
        adjusted_fc = fc - (voyage_ded + tf_ded + correction_factor_term)
        adjusted_fc = max(adjusted_fc, 0.0)
        numerator += cf * adjusted_fc

    denominator = capacity * (distance_nm - dx)
    if denominator <= 0:
        raise ValueError(f"CII denominator is zero or negative: capacity={capacity}, distance={distance_nm}")
    return numerator / denominator

def calc_required_cii(ship_type: str, dwt_or_gt: float, year: int = 2024) -> float:
    if ship_type not in CII_REF_PARAMS:
        raise ValueError(f"Unknown ship type '{ship_type}' for CII.")
    a, c, _ = CII_REF_PARAMS[ship_type]
    ref_cii  = a * (dwt_or_gt ** -c)
    dd = CII_REDUCTION_FACTORS.get(year, 11)
    return ref_cii * (1.0 - dd / 100.0)

def get_cii_capacity(ship_type: str, dwt: float, gt: float = 0.0) -> float:
    if ship_type not in CII_REF_PARAMS:
        raise ValueError(f"Unknown ship type '{ship_type}'.")
    _, _, cap_mode = CII_REF_PARAMS[ship_type]
    if cap_mode == "gt":
        if gt <= 0:
            raise ValueError("GT must be positive for this ship type.")
        return float(gt)
    if dwt <= 0:
        raise ValueError("DWT must be positive for this ship type.")
    return float(dwt)

def rate_cii(attained: float, required: float, ship_type: str) -> dict:
    import math
    d = CII_RATING_BOUNDARIES.get(ship_type, CII_RATING_BOUNDARIES["container"])
    d1, d2, d3, d4 = d
    b_a = math.exp(d1) * required
    b_b = math.exp(d2) * required
    b_c = math.exp(d3) * required
    b_d = math.exp(d4) * required

    if attained <= b_a: rating = "A"
    elif attained <= b_b: rating = "B"
    elif attained <= b_c: rating = "C"
    elif attained <= b_d: rating = "D"
    else: rating = "E"

    margin_pct = ((required - attained) / required) * 100.0
    descriptions = {
        "A": "Superior — well below the required CII.",
        "B": "Minor superior — below required CII.",
        "C": "Moderate — meets the required CII.",
        "D": "Minor inferior — above required CII.",
        "E": "Inferior — significantly above required CII.",
    }
    return {
        "rating": rating,
        "boundaries": {"A": round(b_a, 4), "B": round(b_b, 4), "C": round(b_c, 4), "D": round(b_d, 4)},
        "margin_pct": round(margin_pct, 2),
        "description": descriptions[rating],
    }

def calculate_cii(inputs: dict) -> dict:
    ship_type   = str(inputs["ship_type"]).strip().lower()
    dwt         = float(inputs.get("dwt", 0) or 0)
    gt          = float(inputs.get("gt",  0) or 0)
    year        = int(inputs.get("year", 2024))
    distance_nm = float(inputs["distance_nm"])

    FUEL_KEYS = ["hfo", "mdo", "lng", "methanol", "lpg_propane", "lpg_butane", "ethane"]
    fc_j = {}
    for fuel in FUEL_KEYS:
        val = float(inputs.get(f"fc_{fuel}", 0) or 0)
        if val > 0: fc_j[fuel] = val * 1_000_000

    capacity = get_cii_capacity(ship_type, dwt, gt)
    _, _, cap_mode = CII_REF_PARAMS[ship_type]
    ref_size = gt if cap_mode == "gt" else dwt

    fc_voyage_j = {}
    for fuel in FUEL_KEYS:
        val = float(inputs.get(f"voyage_{fuel}", 0) or 0)
        if val > 0: fc_voyage_j[fuel] = val * 1_000_000
    dx = float(inputs.get("voyage_distance", 0) or 0)

    tf_j = {}
    corrections_applied = []
    if inputs.get("shuttle_tanker", False) and ship_type == "tanker":
        af = calc_af_tanker_shuttle(dwt)
        for fuel, fc in fc_j.items(): tf_j[fuel] = (1 - af) * fc
        corrections_applied.append(f"Shuttle correction applied (AF={af:.4f})")
    elif inputs.get("sts_operation", False) and ship_type == "tanker":
        af = calc_af_tanker_sts(dwt)
        for fuel, fc_s in fc_j.items(): tf_j[fuel] = (1 - af) * fc_s
        corrections_applied.append(f"STS correction applied (AF={af:.4f})")

    fc_electrical_j = {}
    sfoc_elec = float(inputs.get("sfoc_electrical", 175) or 175)
    reefer_kwh = float(inputs.get("reefer_kwh", 0) or 0)
    reefer_days_sea = float(inputs.get("reefer_days_sea", 0) or 0)
    reefer_days_port = float(inputs.get("reefer_days_port", 0) or 0)

    if reefer_kwh > 0:
        fc_reefer_g = calc_fc_electrical_reefer_monitored(reefer_kwh, sfoc_elec)
        fc_electrical_j["hfo"] = fc_electrical_j.get("hfo", 0) + fc_reefer_g
        corrections_applied.append(f"Reefer (monitored): {fc_reefer_g/1e6:.2f} t HFO")
    elif reefer_days_sea > 0 or reefer_days_port > 0:
        fc_reefer_g = calc_fc_electrical_reefer_unmonitored(reefer_days_sea, reefer_days_port, sfoc_elec)
        fc_electrical_j["hfo"] = fc_electrical_j.get("hfo", 0) + fc_reefer_g
        corrections_applied.append(f"Reefer (unmonitored): {fc_reefer_g/1e6:.2f} t HFO")

    fc_boiler_j = {}
    if float(inputs.get("fc_boiler_hfo", 0) or 0) > 0 and ship_type == "tanker":
        fc_boiler_j["hfo"] = float(inputs["fc_boiler_hfo"]) * 1_000_000
        corrections_applied.append(f"Boiler fuel: {inputs['fc_boiler_hfo']} t HFO")

    fc_others_j = {}
    if float(inputs.get("fc_others_hfo", 0) or 0) > 0 and ship_type == "tanker":
        fc_others_j["hfo"] = float(inputs["fc_others_hfo"]) * 1_000_000
        corrections_applied.append(f"Pump fuel: {inputs['fc_others_hfo']} t HFO")

    attained = calc_attained_cii(fc_j, distance_nm, capacity, fc_voyage_j, tf_j, fc_electrical_j, fc_boiler_j, fc_others_j, dx, year)
    required = calc_required_cii(ship_type, ref_size, year)
    rating_result = rate_cii(attained, required, ship_type)

    return {
        "attained_cii": round(attained, 4),
        "required_cii": round(required, 4),
        "capacity": round(capacity, 0),
        "year": year,
        "distance_nm": distance_nm,
        "rating": rating_result,
        "corrections_applied": corrections_applied,
        "reduction_factor_pct": CII_REDUCTION_FACTORS.get(year, 11),
        "inputs_echo": {
            "ship_type": ship_type,
            "dwt": dwt,
            "gt": gt
        }
    }
