"""
CO2 Conversion Factors (CF) as per MARPOL Annex VI Regulation 2.
"""

CF_MAP = {
    'hfo': 3.114,          # Heavy fuel oil (RMG, RMK)
    'mdo': 3.206,          # Marine diesel / gas oil (DMA, DMB, DMZ)
    'lng': 2.750,          # Liquefied natural gas (Otto / Diesel cycle)
    'methanol': 1.375,     # Methanol
    'lpg_propane': 3.000,  # LPG propane
    'lpg_butane': 3.030,   # LPG butane
    'ethane': 2.927,       # Ethane
}

def get_cf(fuel_type: str) -> float:
    """Returns the carbon conversion factor for a given fuel type."""
    return CF_MAP.get(fuel_type.lower(), 3.114)  # Default to HFO if not found
