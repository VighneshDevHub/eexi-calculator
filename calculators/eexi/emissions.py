"""
calculators/eexi/emissions.py
-----------------
Emission calculation functions.
All values in SI-compatible units: power in kW, SFC in g/kWh, CF dimensionless.
"""


def calc_pme(mcr: float, f_eff: float = 1.0) -> float:
    """
    Calculate main engine reference power (PME) for EEXI.

    PME = 0.75 * MCR * f_eff

    Parameters
    ----------
    mcr   : float  Maximum continuous rating of main engine (kW)
    f_eff : float  Efficiency correction factor for shaft generator /
                   waste-heat recovery system (default 1.0 = no saving device)

    Returns
    -------
    float  PME in kW

    Raises
    ------
    ValueError  If MCR <= 0 or f_eff out of range
    """
    if mcr <= 0:
        raise ValueError(f"MCR must be positive, got {mcr}")
    if not (0.0 < f_eff <= 1.0):
        raise ValueError(f"f_eff must be in (0, 1], got {f_eff}")
    return 0.75 * mcr * f_eff


def calc_me_emissions(pme: float, cf: float, sfc: float) -> float:
    """
    Main engine CO2 emission term (numerator contribution).

    ME_emissions = PME * CF_ME * SFC_ME   [gCO2 / nautical mile]

    Parameters
    ----------
    pme : float  Main engine power at EEXI reference condition (kW)
    cf  : float  CO2 conversion factor (gCO2/gFuel)
    sfc : float  Specific fuel consumption at 75% MCR (g/kWh)

    Returns
    -------
    float  gCO2/nm
    """
    if pme < 0:
        raise ValueError(f"PME cannot be negative, got {pme}")
    if cf <= 0:
        raise ValueError(f"CF must be positive, got {cf}")
    if sfc <= 0:
        raise ValueError(f"SFC must be positive, got {sfc}")
    return pme * cf * sfc


def get_default_pae(mcr: float) -> float:
    """
    Calculate default auxiliary engine power (PAE) per IMO guidelines.
    
    For MCR >= 10,000 kW: PAE = (0.025 * MCR) + 250
    For MCR < 10,000 kW:  PAE = 0.05 * MCR
    """
    if mcr >= 10000:
        return (0.025 * mcr) + 250
    return 0.05 * mcr


def calc_ae_emissions(pae: float, cf_ae: float, sfc_ae: float) -> float:
    """
    Auxiliary engine CO2 emission term (numerator contribution).

    AE_emissions = PAE * CF_AE * SFC_AE   [gCO2 / nautical mile]

    Parameters
    ----------
    pae    : float  Total auxiliary engine power (kW); 0 if not fitted / unknown
    cf_ae  : float  CO2 conversion factor for auxiliary fuel
    sfc_ae : float  Auxiliary engine SFC (g/kWh); ignored if pae == 0

    Returns
    -------
    float  gCO2/nm  (0.0 when pae == 0)
    """
    if pae < 0:
        raise ValueError(f"PAE cannot be negative, got {pae}")
    if pae == 0.0:
        return 0.0
    if cf_ae <= 0:
        raise ValueError(f"CF_AE must be positive, got {cf_ae}")
    if sfc_ae <= 0:
        raise ValueError(f"SFC_AE must be positive, got {sfc_ae}")
    return pae * cf_ae * sfc_ae


def calc_total_numerator(me_emissions: float, ae_emissions: float) -> float:
    """Sum of all CO2 emission components."""
    return me_emissions + ae_emissions
