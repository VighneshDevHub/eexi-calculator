"""
eexi/cii.py
-----------
Carbon Intensity Indicator (CII) calculation module.
Based on:
  - IMO Resolution MEPC.352(78) — CII Guidelines G1 (attained annual CII formula)
  - IMO Resolution MEPC.353(78) — CII Reference Lines G2
  - IMO Resolution MEPC.354(78) — CII Rating G4
  - IMO Resolution MEPC.355(78) — CII Correction Factors G5 (uploaded document)

CII is an OPERATIONAL (annual) measure — unlike EEXI which is a one-time design measure.
Ships are rated A–E each year based on their actual fuel consumption and distance sailed.
"""

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

# ---------------------------------------------------------------------------
# STS CORRECTION FACTORS — MEPC.355(78) § 4.2
# AFTanker,STS     = 6.1742 × DWT^(-0.246)
# AFTanker,Shuttle = 5.6805 × DWT^(-0.208)
# ---------------------------------------------------------------------------


def calc_af_tanker_sts(dwt: float) -> float:
    """
    AFTanker,STS correction factor for Ship-to-Ship tanker operations.
    MEPC.355(78) § 4.2
    Criteria: voyage ≤ 600 nm, voyage time (excl. port) ≤ 72 hours.
    """
    if dwt <= 0:
        raise ValueError("DWT must be positive for STS correction factor.")
    return 6.1742 * (dwt ** -0.246)


def calc_af_tanker_shuttle(dwt: float) -> float:
    """
    AFTanker,Shuttle correction factor for shuttle tankers with dynamic positioning.
    MEPC.355(78) § 4.2
    """
    if dwt <= 0:
        raise ValueError("DWT must be positive for shuttle tanker correction factor.")
    return 5.6805 * (dwt ** -0.208)


def calc_fc_electrical_reefer_monitored(reefer_kwh: float, sfoc: float) -> float:
    """
    FCelectrical for reefer containers — ships WITH kWh monitoring.
    MEPC.355(78) Appendix 1, Part A, §1.1

    FCelectrical_reefer = Reefer_kWh × SFOC

    Parameters
    ----------
    reefer_kwh : float  kWh measured by kWh meter on board
    sfoc       : float  Weighted avg SFC of engines supplying electrical power (g/kWh)
                        Default 175 g/kWh (2-stroke) or 200 g/kWh (4-stroke)

    Returns
    -------
    float  Fuel mass in grams
    """
    return reefer_kwh * sfoc


def calc_fc_electrical_reefer_unmonitored(
    reefer_days_sea: float,
    reefer_days_port: float,
    sfoc_avg: float,
    cx: float = 2.75,
) -> float:
    """
    FCelectrical for reefer containers — ships WITHOUT kWh monitoring.
    MEPC.355(78) Appendix 1, Part A, §1.2

    FCelectrical_reefer = Cx × 24 × SFOC_avg × (Reefer_days_sea + Σ Reefer_days_port)

    Parameters
    ----------
    reefer_days_sea  : float  In-use reefer-days at sea
    reefer_days_port : float  In-use reefer-days at port (avg of arrival + departure counts)
    sfoc_avg         : float  Weighted avg SFC of electrical supply engines (g/kWh)
    cx               : float  Default reefer consumption = 2.75 kW/h per MEPC.355(78)

    Returns
    -------
    float  Fuel mass in grams
    """
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
    fi: float = 1.0,
    fm: float = 1.0,
    fc_factor: float = 1.0,
    fi_vse: float = 1.0,
    year: int = 2024,
) -> float:
    """
    Calculate attained annual CII (CIIship).
    MEPC.352(78) as modified by correction factors in MEPC.355(78).

    Full formula:
        CIIship = Σj [ CFj × { FCj − (FCvoyage,j + TFj + (0.75 − 0.03·yi)
                               × (FCelectrical,j + FCboiler,j + FCothers,j) ) } ]
                  ─────────────────────────────────────────────────────────────
                  fi × fm × fc × fi_VSE × Capacity × (Dt − Dx)

    Parameters
    ----------
    fc_j             : dict  {fuel_key: mass_grams}  Total annual fuel by type
    distance_nm      : float  Total distance sailed (nm), Dt
    capacity         : float  DWT or GT (ship-type dependent)
    fc_voyage_j      : dict  {fuel_key: grams} Voyage adjustment deductions
                             (safety scenarios, ice sailing) per §4.1
    tf_j             : dict  {fuel_key: grams} STS / shuttle tanker deduction (1-AF)×FCS
    fc_electrical_j  : dict  {fuel_key: grams} Electrical correction (reefers, cooling, pumps)
    fc_boiler_j      : dict  {fuel_key: grams} Boiler correction (cargo heating on tankers)
    fc_others_j      : dict  {fuel_key: grams} Standalone pump engines on tankers
    dx               : float  Distance deducted for voyage adjustments (nm)
    fi               : float  Capacity correction (ice class), default 1.0
    fm               : float  Ice class IA Super/IA factor, default 1.0
    fc_factor        : float  Cubic capacity correction (chemical tankers), default 1.0
    fi_vse           : float  Voluntary structural enhancement (self-unloading bulk), default 1.0
    year             : int    Calendar year for yi numbering (y2023=0, y2024=1, ...)

    Returns
    -------
    float  Attained CII in gCO2/(capacity·nm)
    """
    from .ship_params import CF_MAP

    # yi numbering: y2023=0, y2024=1, y2025=2 ...
    yi = max(0, year - 2023)

    # Default empty dicts
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

        # Electrical/boiler/others corrections: CANNOT be used during voyage adj periods
        # (MEPC.355(78) §3.3)
        elec_ded  = fc_electrical_j.get(fuel, 0.0)
        boil_ded  = fc_boiler_j.get(fuel, 0.0)
        other_ded = fc_others_j.get(fuel, 0.0)

        correction_factor_term = (0.75 - 0.03 * yi) * (elec_ded + boil_ded + other_ded)
        adjusted_fc = fc - (voyage_ded + tf_ded + correction_factor_term)
        adjusted_fc = max(adjusted_fc, 0.0)   # cannot be negative

        numerator += cf * adjusted_fc

    denominator = fi * fm * fc_factor * fi_vse * capacity * (distance_nm - dx)

    if denominator <= 0:
        raise ValueError(
            f"CII denominator is zero or negative: "
            f"capacity={capacity}, distance={distance_nm}, dx={dx}"
        )

    return numerator / denominator


def calc_required_cii(ship_type: str, dwt_or_gt: float, year: int = 2024) -> float:
    """
    Calculate required CII for a given ship type, size, and year.
    MEPC.353(78) reference line × (1 - dd/100) reduction factor.

    Required CII = a × DWT^(-c) × (1 - dd/100)

    Parameters
    ----------
    ship_type  : str   Key from CII_REF_PARAMS
    dwt_or_gt  : float DWT or GT depending on ship type
    year       : int   Calendar year (2023–2026+)

    Returns
    -------
    float  Required CII in gCO2/(capacity·nm)
    """
    if ship_type not in CII_REF_PARAMS:
        raise ValueError(f"Unknown ship type '{ship_type}' for CII. "
                         f"Valid: {list(CII_REF_PARAMS)}")
    if dwt_or_gt <= 0:
        raise ValueError("DWT / GT must be positive.")

    a, c, _ = CII_REF_PARAMS[ship_type]
    ref_cii  = a * (dwt_or_gt ** -c)

    dd = CII_REDUCTION_FACTORS.get(year, 11)   # default to 11% for 2027+
    return ref_cii * (1.0 - dd / 100.0)


def get_cii_capacity(ship_type: str, dwt: float, gt: float = 0.0) -> float:
    """Return capacity for CII denominator (mirrors EEXI but uses CII_REF_PARAMS cap_mode)."""
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
    """
    Assign A–E rating based on attained vs required CII.
    MEPC.354(78) — boundary vectors per ship type.

    Rating logic:
        A  : attained ≤ exp(d1) × required
        B  : exp(d1) < attained ≤ exp(d2) × required
        C  : exp(d2) < attained ≤ exp(d3) × required   (d3=0 → boundary = required)
        D  : exp(d3) < attained ≤ exp(d4) × required
        E  : attained > exp(d4) × required

    Parameters
    ----------
    attained  : float  Attained CII
    required  : float  Required CII
    ship_type : str    Key from CII_RATING_BOUNDARIES

    Returns
    -------
    dict:
        rating        : str  "A" | "B" | "C" | "D" | "E"
        boundaries    : dict  {A, B, C, D, E boundary values}
        margin_pct    : float  % above/below C boundary (required CII)
        description   : str   Human-readable verdict
    """
    import math

    if ship_type not in CII_RATING_BOUNDARIES:
        # Fallback to container boundaries if type not listed
        d = CII_RATING_BOUNDARIES.get("container")
    else:
        d = CII_RATING_BOUNDARIES[ship_type]

    d1, d2, d3, d4 = d
    b_a = math.exp(d1) * required   # superior boundary  (A/B)
    b_b = math.exp(d2) * required   # minor superior     (B/C)
    b_c = math.exp(d3) * required   # C/D  (d3=0 → = required CII)
    b_d = math.exp(d4) * required   # D/E

    if attained <= b_a:
        rating = "A"
    elif attained <= b_b:
        rating = "B"
    elif attained <= b_c:
        rating = "C"
    elif attained <= b_d:
        rating = "D"
    else:
        rating = "E"

    margin_pct = ((required - attained) / required) * 100.0

    descriptions = {
        "A": "Superior — well below the required CII. Excellent operational efficiency.",
        "B": "Minor superior — below required CII. Good operational performance.",
        "C": "Moderate — meets the required CII. No corrective action needed.",
        "D": "Minor inferior — above required CII. Corrective measures should be considered (SEEMP update required if D for 3 consecutive years).",
        "E": "Inferior — significantly above required CII. Immediate corrective action and SEEMP update required.",
    }

    return {
        "rating":     rating,
        "boundaries": {
            "A": round(b_a, 4),
            "B": round(b_b, 4),
            "C": round(b_c, 4),
            "D": round(b_d, 4),
        },
        "margin_pct":  round(margin_pct, 2),
        "description": descriptions[rating],
    }


def calculate_cii(inputs: dict) -> dict:
    """
    Full CII calculation pipeline.

    Parameters (flat dict)
    ----------
    ship_type        : str    SHIP_PARAMS key
    dwt              : float  DWT (tonnes)
    gt               : float  GT (for ro_ro_pass / cruise)
    year             : int    Calendar year (default 2024)
    distance_nm      : float  Total annual distance sailed (nm)

    # Fuel consumption — at least one fuel required
    fc_hfo           : float  HFO consumed (tonnes) — converted internally to grams
    fc_mdo           : float  MDO consumed (tonnes)
    fc_lng           : float  LNG consumed (tonnes)
    fc_methanol      : float  Methanol consumed (tonnes)
    fc_lpg_propane   : float  LPG propane consumed (tonnes)

    # Voyage adjustments (MEPC.355(78) §4.1) — optional
    voyage_hfo        : float  HFO deducted for voyage adjustment (tonnes)
    voyage_mdo        : float  MDO deducted for voyage adjustment (tonnes)
    voyage_distance   : float  Distance deducted (nm), Dx

    # STS / Shuttle correction (MEPC.355(78) §4.2) — optional
    sts_operation    : bool   Is this a STS tanker?
    shuttle_tanker   : bool   Is this a shuttle tanker?

    # Electrical corrections (MEPC.355(78) §4.3) — optional
    reefer_kwh       : float  Reefer kWh (if monitored)
    reefer_days_sea  : float  Reefer-days at sea (if unmonitored)
    reefer_days_port : float  Reefer-days at port (if unmonitored)
    sfoc_electrical  : float  SFC of engines for electrical supply (g/kWh)

    # Boiler / others (MEPC.355(78) §4.4, §4.5) — optional, tankers only
    fc_boiler_hfo    : float  Boiler HFO consumption (tonnes)
    fc_others_hfo    : float  Standalone pump engine HFO (tonnes)

    Returns
    -------
    dict:
        attained_cii, required_cii, rating (dict), capacity,
        corrections_applied (list), inputs_echo
    """
    ship_type   = str(inputs["ship_type"]).strip().lower()
    dwt         = float(inputs.get("dwt", 0) or 0)
    gt          = float(inputs.get("gt",  0) or 0)
    year        = int(inputs.get("year", 2024))
    distance_nm = float(inputs["distance_nm"])

    if distance_nm <= 0:
        raise ValueError("Annual distance sailed must be positive.")

    # Build fc_j dict (convert tonnes → grams: × 1,000,000)
    FUEL_KEYS = ["hfo", "mdo", "lng", "methanol", "lpg_propane", "lpg_butane", "ethane"]
    fc_j = {}
    for fuel in FUEL_KEYS:
        val = float(inputs.get(f"fc_{fuel}", 0) or 0)
        if val > 0:
            fc_j[fuel] = val * 1_000_000   # tonnes → grams

    if not fc_j:
        raise ValueError("At least one fuel consumption value must be provided.")

    # Capacity
    capacity = get_cii_capacity(ship_type, dwt, gt)

    # Reference size (DWT or GT) for required CII
    _, _, cap_mode = CII_REF_PARAMS[ship_type]
    ref_size = gt if cap_mode == "gt" else dwt

    # Voyage adjustments §4.1
    fc_voyage_j = {}
    for fuel in FUEL_KEYS:
        val = float(inputs.get(f"voyage_{fuel}", 0) or 0)
        if val > 0:
            fc_voyage_j[fuel] = val * 1_000_000
    dx = float(inputs.get("voyage_distance", 0) or 0)

    # STS / Shuttle corrections §4.2
    tf_j = {}
    corrections_applied = []
    sts       = inputs.get("sts_operation", False)
    shuttle   = inputs.get("shuttle_tanker", False)

    if shuttle and ship_type == "tanker":
        af = calc_af_tanker_shuttle(dwt)
        for fuel, fc in fc_j.items():
            tf_j[fuel] = (1 - af) * fc
        corrections_applied.append(f"ShaPoLi/Shuttle correction applied (AF={af:.4f})")

    elif sts and ship_type == "tanker":
        af = calc_af_tanker_sts(dwt)
        for fuel, fc_s in fc_j.items():
            tf_j[fuel] = (1 - af) * fc_s
        corrections_applied.append(f"STS correction applied (AF={af:.4f})")

    # Electrical corrections §4.3
    fc_electrical_j = {}
    sfoc_elec = float(inputs.get("sfoc_electrical", 175) or 175)

    reefer_kwh       = float(inputs.get("reefer_kwh", 0) or 0)
    reefer_days_sea  = float(inputs.get("reefer_days_sea",  0) or 0)
    reefer_days_port = float(inputs.get("reefer_days_port", 0) or 0)

    if reefer_kwh > 0:
        fc_reefer_g = calc_fc_electrical_reefer_monitored(reefer_kwh, sfoc_elec)
        fc_electrical_j["hfo"] = fc_electrical_j.get("hfo", 0) + fc_reefer_g
        corrections_applied.append(
            f"Reefer electrical correction (monitored): {fc_reefer_g/1e6:.2f} t HFO equiv."
        )
    elif reefer_days_sea > 0 or reefer_days_port > 0:
        fc_reefer_g = calc_fc_electrical_reefer_unmonitored(
            reefer_days_sea, reefer_days_port, sfoc_elec
        )
        fc_electrical_j["hfo"] = fc_electrical_j.get("hfo", 0) + fc_reefer_g
        corrections_applied.append(
            f"Reefer electrical correction (unmonitored): {fc_reefer_g/1e6:.2f} t HFO equiv."
        )

    # Boiler corrections §4.4 (tankers)
    fc_boiler_j = {}
    fc_boiler_hfo = float(inputs.get("fc_boiler_hfo", 0) or 0)
    if fc_boiler_hfo > 0 and ship_type == "tanker":
        fc_boiler_j["hfo"] = fc_boiler_hfo * 1_000_000
        corrections_applied.append(
            f"Boiler fuel correction: {fc_boiler_hfo:.1f} t HFO"
        )

    # FCOthers §4.5 (tankers)
    fc_others_j = {}
    fc_others_hfo = float(inputs.get("fc_others_hfo", 0) or 0)
    if fc_others_hfo > 0 and ship_type == "tanker":
        fc_others_j["hfo"] = fc_others_hfo * 1_000_000
        corrections_applied.append(
            f"Standalone pump engine correction: {fc_others_hfo:.1f} t HFO"
        )

    # Voyage adjustment note
    if fc_voyage_j:
        total_voyage_ded = sum(fc_voyage_j.values()) / 1_000_000
        corrections_applied.append(
            f"Voyage adjustment deduction: {total_voyage_ded:.1f} t fuel, {dx:.0f} nm"
        )

    # Calculate attained CII
    attained = calc_attained_cii(
        fc_j=fc_j,
        distance_nm=distance_nm,
        capacity=capacity,
        fc_voyage_j=fc_voyage_j,
        tf_j=tf_j,
        fc_electrical_j=fc_electrical_j,
        fc_boiler_j=fc_boiler_j,
        fc_others_j=fc_others_j,
        dx=dx,
        year=year,
    )

    # Required CII
    required = calc_required_cii(ship_type, ref_size, year)

    # Rating
    rating_result = rate_cii(attained, required, ship_type)

    return {
        "attained_cii":        round(attained, 4),
        "required_cii":        round(required, 4),
        "capacity":            round(capacity, 0),
        "year":                year,
        "distance_nm":         distance_nm,
        "rating":              rating_result,
        "corrections_applied": corrections_applied,
        "reduction_factor_pct": CII_REDUCTION_FACTORS.get(year, 11),
        "inputs_echo": {
            "ship_type": ship_type, "dwt": dwt, "gt": gt,
            "year": year, "distance_nm": distance_nm,
        },
    }
