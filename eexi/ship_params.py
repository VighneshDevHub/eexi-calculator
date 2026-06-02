"""
eexi/ship_params.py
-------------------
Reference line parameters from IMO MEPC.350(78) Annex 9, Table 1.
Provides ship-type lookups and capacity calculation.
"""

SHIP_PARAMS: dict = {
    #  key              a          c       cap_mode
    "bulk_carrier":  (961.79,   0.477,  "dwt"),
    "tanker":        (1218.80,  0.488,  "dwt"),
    "container":     (174.22,   0.201,  "0.70*dwt"),
    "general_cargo": (107.48,   0.216,  "dwt"),
    "ro_ro_cargo":   (1686.17,  0.623,  "dwt"),
    "ro_ro_pass":    (752.16,   0.381,  "gt"),
    "lng_carrier":   (2253.70,  0.474,  "dwt"),
    "gas_carrier":   (1120.00,  0.456,  "dwt"),
    "cruise":        (170.84,   0.217,  "gt"),
}

SHIP_LABELS: dict = {
    "bulk_carrier":  "Bulk Carrier",
    "tanker":        "Tanker",
    "container":     "Container Ship",
    "general_cargo": "General Cargo",
    "ro_ro_cargo":   "Ro-Ro Cargo",
    "ro_ro_pass":    "Ro-Ro Passenger",
    "lng_carrier":   "LNG Carrier",
    "gas_carrier":   "Gas Carrier",
    "cruise":        "Cruise Ship",
}

CF_MAP: dict = {
    "hfo":          3.114,
    "mdo":          3.206,
    "lng":          2.750,
    "methanol":     1.375,
    "lpg_propane":  3.000,
    "lpg_butane":   3.030,
    "ethane":       2.927,
}

CF_LABELS: dict = {
    "hfo":          "HFO / RMG (CF = 3.114)",
    "mdo":          "MDO / MGO (CF = 3.206)",
    "lng":          "LNG (CF = 2.750)",
    "methanol":     "Methanol (CF = 1.375)",
    "lpg_propane":  "LPG Propane (CF = 3.000)",
    "lpg_butane":   "LPG Butane (CF = 3.030)",
    "ethane":       "Ethane (CF = 2.927)",
}


def get_reduction_factor(ship_type: str, capacity: float) -> float:
    """
    Returns the EEXI reduction factor (as a decimal) based on ship type and capacity.
    Source: IMO MEPC.350(78)
    """
    if ship_type == "bulk_carrier":
        if capacity >= 200000: return 0.15
        if capacity >= 20000: return 0.20
        if capacity >= 10000:
            return 0.20 * (capacity - 10000) / 10000
        return 0.0
    
    if ship_type == "tanker":
        if capacity >= 200000: return 0.15
        if capacity >= 20000: return 0.20
        if capacity >= 4000:
            return 0.20 * (capacity - 4000) / 16000
        return 0.0

    if ship_type == "gas_carrier":
        if capacity >= 15000: return 0.30
        if capacity >= 10000: return 0.20
        if capacity >= 2000:
            return 0.20 * (capacity - 2000) / 8000
        return 0.0

    if ship_type == "container":
        if capacity >= 200000: return 0.50
        if capacity >= 120000: return 0.45
        if capacity >= 80000: return 0.35
        if capacity >= 40000: return 0.30
        if capacity >= 15000: return 0.20
        if capacity >= 10000:
            return 0.20 * (capacity - 10000) / 5000
        return 0.0

    if ship_type == "general_cargo":
        if capacity >= 15000: return 0.30
        if capacity >= 3000:
            return 0.30 * (capacity - 3000) / 12000
        return 0.0

    if ship_type == "lng_carrier":
        if capacity >= 10000: return 0.30
        return 0.0

    if ship_type == "ro_ro_cargo":
        if capacity >= 2000: return 0.05
        if capacity >= 1000:
            return 0.05 * (capacity - 1000) / 1000
        return 0.0

    if ship_type == "ro_ro_pass":
        if capacity >= 1000: return 0.05
        if capacity >= 250:
            return 0.05 * (capacity - 250) / 750
        return 0.0

    if ship_type == "cruise":
        if capacity >= 85000: return 0.30
        if capacity >= 25000:
            return 0.30 * (capacity - 25000) / 60000
        return 0.0

    return 0.0


def get_capacity(ship_type: str, dwt: float, gt: float = 0.0) -> float:
    """Return EEXI capacity for the given ship type."""
    if ship_type not in SHIP_PARAMS:
        raise ValueError(f"Unknown ship type '{ship_type}'. Valid: {list(SHIP_PARAMS)}")
    _, _, cap_mode = SHIP_PARAMS[ship_type]
    if cap_mode == "dwt":
        if dwt <= 0:
            raise ValueError("DWT must be positive for this ship type.")
        return float(dwt)
    if cap_mode == "0.70*dwt":
        if dwt <= 0:
            raise ValueError("DWT must be positive for container ships.")
        return 0.70 * float(dwt)
    if cap_mode == "gt":
        if gt <= 0:
            raise ValueError("GT must be positive for Ro-Ro passenger / Cruise ships.")
        return float(gt)
    raise ValueError(f"Unknown capacity mode '{cap_mode}'.")


def get_cf(fuel_type: str) -> float:
    """Return CO2 conversion factor for the given fuel type."""
    if fuel_type not in CF_MAP:
        raise ValueError(f"Unknown fuel type '{fuel_type}'. Valid: {list(CF_MAP)}")
    return CF_MAP[fuel_type]

def get_ship_params(ship_type: str):
    """Returns (a, c, capacity_type) for the given ship type."""
    return SHIP_PARAMS.get(ship_type.lower())
