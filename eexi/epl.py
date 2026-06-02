"""
eexi/epl.py
-----------
Engine Power Limitation (EPL) and Shaft Power Limitation (ShaPoLi) calculations.
Derives the maximum allowable MCR to achieve EEXI compliance.
"""


def calc_epl(
    required_eexi: float,
    capacity: float,
    v_ref: float,
    cf_me: float,
    sfc_me: float,
    pae: float = 0.0,
    cf_ae: float = 3.114,
    sfc_ae: float = 0.0,
    f_i: float = 1.0,
    f_w: float = 1.0,
) -> dict:
    """
    Calculate Engine Power Limitation target.

    Rearranges attained EEXI formula to solve for maximum allowable PME:

        Max_PME = (Req_EEXI * capacity * v_ref * f_i * f_w
                   - PAE * CF_AE * SFC_AE)
                  / (CF_ME * SFC_ME)

        Limited_MCR = Max_PME / 0.75

    Parameters
    ----------
    required_eexi : float  Required EEXI (gCO2/t·nm)
    capacity      : float  Ship capacity (DWT or GT)
    v_ref         : float  Design speed (knots)
    cf_me         : float  Main engine CO2 conversion factor
    sfc_me        : float  Main engine SFC (g/kWh)
    pae           : float  Auxiliary engine power (kW), 0 if none
    cf_ae         : float  Auxiliary fuel CO2 conversion factor
    sfc_ae        : float  Auxiliary SFC (g/kWh)
    f_i, f_w      : float  Correction factors (default 1.0)

    Returns
    -------
    dict with keys:
        max_pme        : float  Maximum allowable PME (kW)
        limited_mcr    : float  Corresponding MCR limit (kW)
        epl_possible   : bool   False if max_pme <= 0 (extreme non-compliance)
        note           : str    Human-readable guidance
    """
    transport_work = required_eexi * capacity * v_ref * f_i * f_w
    ae_term = pae * cf_ae * sfc_ae if (pae > 0 and sfc_ae > 0) else 0.0
    max_pme = (transport_work - ae_term) / (cf_me * sfc_me)

    if max_pme <= 0:
        return {
            "max_pme": max_pme,
            "limited_mcr": 0.0,
            "epl_possible": False,
            "note": (
                "EPL alone is insufficient to achieve compliance. "
                "The auxiliary engine emissions already exceed the EEXI budget. "
                "Consult a naval architect for alternative compliance measures "
                "(e.g. fuel change, speed reduction, wind-assist)."
            ),
        }

    limited_mcr = max_pme / 0.75

    return {
        "max_pme": round(max_pme, 2),
        "limited_mcr": round(limited_mcr, 2),
        "epl_possible": True,
        "note": (
            f"Limit the installed MCR to {limited_mcr:.0f} kW "
            f"via Engine Power Limitation (EPL) or Shaft Power Limitation (ShaPoLi) "
            f"to achieve compliance with the required EEXI."
        ),
    }


def calc_epl_percentage(limited_mcr: float, installed_mcr: float) -> float:
    """
    Express the EPL limit as a percentage of the installed MCR.

    Parameters
    ----------
    limited_mcr   : float  EPL-limited MCR (kW)
    installed_mcr : float  Original installed MCR (kW)

    Returns
    -------
    float  Percentage of installed MCR that may be used (e.g. 78.3)
    """
    if installed_mcr <= 0:
        raise ValueError("Installed MCR must be positive.")
    return round((limited_mcr / installed_mcr) * 100.0, 2)
