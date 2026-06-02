"""
eexi/eexi.py
------------
Core EEXI attained / required calculation and compliance check.
"""

from .ship_params import SHIP_PARAMS, get_capacity


def calc_attained_eexi(
    numerator: float,
    capacity: float,
    v_ref: float,
    f_i: float = 1.0,
    f_w: float = 1.0,
) -> float:
    """
    Calculate attained EEXI.

    Attained EEXI = numerator / (f_i * capacity * v_ref * f_w)

    Parameters
    ----------
    numerator : float  Total CO2 emission rate (gCO2/nm)
    capacity  : float  Ship capacity (DWT or GT, tonnes)
    v_ref     : float  Design speed at 75% MCR (knots)
    f_i       : float  Capacity correction factor (default 1.0)
    f_w       : float  Weather correction factor  (default 1.0)

    Returns
    -------
    float  Attained EEXI in gCO2 / (t·nm)

    Raises
    ------
    ValueError  If any denominator term is zero or negative
    """
    if numerator < 0:
        raise ValueError(f"Numerator cannot be negative, got {numerator:.4f}")
    if capacity <= 0:
        raise ValueError(f"Capacity must be positive, got {capacity}")
    if v_ref <= 0:
        raise ValueError(f"V_ref must be positive, got {v_ref}")
    if f_i <= 0 or f_w <= 0:
        raise ValueError("Correction factors f_i and f_w must be positive.")

    denominator = f_i * capacity * v_ref * f_w
    return numerator / denominator


def calc_required_eexi(ship_type: str, dwt_or_gt: float) -> float:
    """
    Calculate required EEXI from the IMO reference line.

    Required EEXI = a * DWT^(-c) * (1 - reduction)

    Parameters
    ----------
    ship_type  : str    Key from SHIP_PARAMS
    dwt_or_gt  : float  DWT for most ships; GT for ro_ro_pass / cruise

    Returns
    -------
    float  Required EEXI in gCO2 / (t·nm)

    Raises
    ------
    ValueError  If ship_type is unknown or dwt_or_gt <= 0
    """
    if ship_type not in SHIP_PARAMS:
        raise ValueError(f"Unknown ship type '{ship_type}'.")
    if dwt_or_gt <= 0:
        raise ValueError("DWT / GT must be positive.")

    a, c, reduction, _ = SHIP_PARAMS[ship_type]
    eedi_ref = a * (dwt_or_gt ** (-c))
    return eedi_ref * (1.0 - reduction)


def check_compliance(attained: float, required: float) -> dict:
    """
    Determine compliance status and margin.

    Parameters
    ----------
    attained : float  Attained EEXI (gCO2/t·nm)
    required : float  Required EEXI (gCO2/t·nm)

    Returns
    -------
    dict with keys:
        status   : str    "COMPLIANT" | "BORDERLINE" | "NON_COMPLIANT"
        margin   : float  Percentage margin  (+ve = headroom, -ve = excess)
        compliant: bool
    """
    margin_pct = ((required - attained) / required) * 100.0

    if attained <= required:
        if margin_pct < 5.0:
            status = "BORDERLINE"
        else:
            status = "COMPLIANT"
        compliant = True
    else:
        status = "NON_COMPLIANT"
        compliant = False

    return {
        "status": status,
        "margin": round(margin_pct, 2),
        "compliant": compliant
    }
