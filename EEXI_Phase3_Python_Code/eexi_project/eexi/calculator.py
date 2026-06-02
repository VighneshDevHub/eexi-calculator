"""
eexi/calculator.py
------------------
High-level pipeline: receives a validated input dict,
runs all sub-modules, and returns a complete result dict.
This is the single function called by the Flask API endpoint.
"""

from .ship_params import get_capacity, get_cf, SHIP_PARAMS
from .emissions   import calc_pme, calc_me_emissions, calc_ae_emissions, calc_total_numerator
from .eexi        import calc_attained_eexi, calc_required_eexi, check_compliance
from .epl         import calc_epl, calc_epl_percentage


def calculate(inputs: dict) -> dict:
    """
    Run the complete EEXI calculation pipeline.

    Parameters  (all passed as a flat dict — matches the JSON POST body)
    ----------
    ship_type   : str    One of the SHIP_PARAMS keys
    dwt         : float  Deadweight tonnage (tonnes);  required for most types
    gt          : float  Gross tonnage; required for ro_ro_pass / cruise
    mcr         : float  Main engine MCR (kW)
    sfc         : float  Main engine SFC at 75% MCR (g/kWh)
    fuel_type   : str    One of the CF_MAP keys
    v_ref       : float  Design speed at 75% MCR (knots)
    pae         : float  (optional) Auxiliary engine power (kW), default 0
    sfc_ae      : float  (optional) Auxiliary SFC (g/kWh), default 0
    fuel_ae     : str    (optional) Auxiliary fuel type key, default "hfo"

    Returns
    -------
    dict with full intermediate values plus final verdict:
        attained_eexi  : float
        required_eexi  : float
        pme            : float
        me_emissions   : float
        ae_emissions   : float
        numerator      : float
        capacity       : float
        compliance     : dict  {status, margin, compliant}
        epl            : dict | None   (None when compliant)
        inputs_echo    : dict          (sanitised copy of inputs)
    """
    # ── 1. Extract & type-cast inputs ───────────────────────────────────────
    ship_type = str(inputs["ship_type"]).strip().lower()
    dwt       = float(inputs.get("dwt", 0) or 0)
    gt        = float(inputs.get("gt",  0) or 0)
    mcr       = float(inputs["mcr"])
    sfc       = float(inputs["sfc"])
    fuel_type = str(inputs.get("fuel_type", "hfo")).strip().lower()
    v_ref     = float(inputs["v_ref"])
    pae       = float(inputs.get("pae",    0) or 0)
    sfc_ae    = float(inputs.get("sfc_ae", 0) or 0)
    fuel_ae   = str(inputs.get("fuel_ae", "hfo")).strip().lower()

    # ── 2. Validation ───────────────────────────────────────────────────────
    if ship_type not in SHIP_PARAMS:
        raise ValueError(f"Invalid ship_type: '{ship_type}'")
    if mcr <= 0:
        raise ValueError("MCR must be a positive number.")
    if sfc <= 0:
        raise ValueError("SFC must be a positive number.")
    if v_ref <= 0:
        raise ValueError("Design speed must be a positive number.")

    # For GT-based ships validate GT; otherwise validate DWT
    _, _, _, cap_mode = SHIP_PARAMS[ship_type]
    if cap_mode == "gt" and gt <= 0:
        raise ValueError(f"GT must be provided and positive for ship type '{ship_type}'.")
    if cap_mode in ("dwt", "0.70*dwt") and dwt <= 0:
        raise ValueError(f"DWT must be provided and positive for ship type '{ship_type}'.")

    # ── 3. Lookup parameters ────────────────────────────────────────────────
    cf_me = get_cf(fuel_type)
    cf_ae = get_cf(fuel_ae)

    # For required EEXI reference line, GT-based ships use GT as the size argument
    ref_size = gt if cap_mode == "gt" else dwt

    # ── 4. Capacity ─────────────────────────────────────────────────────────
    capacity = get_capacity(ship_type, dwt, gt)

    # ── 5. Emissions ────────────────────────────────────────────────────────
    pme           = calc_pme(mcr)
    me_emissions  = calc_me_emissions(pme, cf_me, sfc)
    ae_emissions  = calc_ae_emissions(pae, cf_ae, sfc_ae)
    numerator     = calc_total_numerator(me_emissions, ae_emissions)

    # ── 6. Attained & required EEXI ─────────────────────────────────────────
    attained = calc_attained_eexi(numerator, capacity, v_ref)
    required = calc_required_eexi(ship_type, ref_size)

    # ── 7. Compliance check ─────────────────────────────────────────────────
    compliance = check_compliance(attained, required)

    # ── 8. EPL (only when non-compliant) ────────────────────────────────────
    epl_result = None
    if not compliance["compliant"]:
        epl_data = calc_epl(
            required_eexi=required,
            capacity=capacity,
            v_ref=v_ref,
            cf_me=cf_me,
            sfc_me=sfc,
            pae=pae,
            cf_ae=cf_ae,
            sfc_ae=sfc_ae,
        )
        epl_pct = (
            calc_epl_percentage(epl_data["limited_mcr"], mcr)
            if epl_data["epl_possible"]
            else None
        )
        epl_result = {**epl_data, "epl_percentage": epl_pct}

    # ── 9. Build & return result dict ───────────────────────────────────────
    return {
        "attained_eexi": round(attained, 4),
        "required_eexi": round(required, 4),
        "pme":           round(pme, 2),
        "me_emissions":  round(me_emissions, 2),
        "ae_emissions":  round(ae_emissions, 2),
        "numerator":     round(numerator, 2),
        "capacity":      round(capacity, 2),
        "cf_me":         cf_me,
        "cf_ae":         cf_ae,
        "compliance":    compliance,
        "epl":           epl_result,
        "inputs_echo": {
            "ship_type": ship_type, "dwt": dwt, "gt": gt,
            "mcr": mcr, "sfc": sfc, "fuel_type": fuel_type,
            "v_ref": v_ref, "pae": pae, "sfc_ae": sfc_ae, "fuel_ae": fuel_ae,
        },
    }
