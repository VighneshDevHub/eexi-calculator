"""
Main EEXI calculation orchestrator.
"""
from .ship_params import get_cf, get_capacity, SHIP_PARAMS
from .emissions import calc_pme, calc_me_emissions, calc_ae_emissions, calc_total_numerator, get_default_pae
from .eexi import calc_attained_eexi, calc_required_eexi, check_compliance
from .epl import calc_epl, calc_epl_percentage

def calculate_eexi(data: dict) -> dict:
    """
    Performs the full EEXI calculation pipeline.
    """
    # 1. Extract inputs
    ship_type = data['ship_type']
    dwt = float(data.get('dwt', 0) or 0)
    gt = float(data.get('gt', 0) or 0)
    mcr = float(data['mcr'])
    sfc = float(data['sfc'])
    fuel_type = data['fuel_type']
    speed = float(data['speed'])
    
    # Correction factors
    f_eff = float(data.get('f_eff', 1.0) or 1.0)
    f_i = float(data.get('f_i', 1.0) or 1.0)
    f_w = float(data.get('f_w', 1.0) or 1.0)
    f_c = float(data.get('f_c', 1.0) or 1.0)
    f_l = float(data.get('f_l', 1.0) or 1.0)
    f_m = float(data.get('f_m', 1.0) or 1.0)
    
    # Optional auxiliary data
    pae = float(data.get('pae', 0) or 0)
    if not pae:
        pae = get_default_pae(mcr)
        
    sfc_ae = float(data.get('sfc_ae', 0) or 0)
    fuel_type_ae = data.get('fuel_type_ae')
    if not fuel_type_ae: # Handle empty string or None
        fuel_type_ae = fuel_type

    # 2. Core Calculations
    cf_me = get_cf(fuel_type)
    cf_ae = get_cf(fuel_type_ae)
    
    capacity = get_capacity(ship_type, dwt, gt)
    pme = calc_pme(mcr, f_eff)
    
    me_emissions = calc_me_emissions(pme, cf_me, sfc)
    ae_emissions = calc_ae_emissions(pae, cf_ae, sfc_ae)
    numerator = calc_total_numerator(me_emissions, ae_emissions)
    
    attained = calc_attained_eexi(numerator, capacity, speed, f_i, f_w, f_c, f_l, f_m)
    
    # Required EEXI uses DWT for most, GT for cruise/ro_ro_pass
    ref_capacity = gt if ship_type in ['ro_ro_pass', 'cruise'] else dwt
    required = calc_required_eexi(ship_type, ref_capacity)
    
    compliance = check_compliance(attained, required)
    
    # 3. EPL / MCRlim Calculation (Always calculated for reference)
    sfc_lim = float(data.get('sfc_lim', 0) or sfc)
    n_exponent = float(data.get('n_exponent', 0) or 0)
    
    epl_data = calc_epl(
        required_eexi=required,
        capacity=capacity,
        v_ref=speed,
        cf_me=cf_me,
        sfc_me=sfc_lim,
        pae=pae,
        cf_ae=cf_ae,
        sfc_ae=sfc_ae,
        f_i=f_i,
        f_w=f_w,
        f_c=f_c,
        f_l=f_l,
        f_m=f_m,
        ship_type=ship_type,
        p_me_original=pme,
        n_exponent=n_exponent
    )
    if epl_data['epl_possible']:
        epl_data['epl_percentage'] = calc_epl_percentage(epl_data['limited_mcr'], mcr)
    
    # 4. Prepare Results
    return {
        "attained_eexi": round(attained, 4),
        "required_eexi": round(required, 4),
        "status": compliance['status'],
        "margin": compliance['margin'],
        "compliant": compliance['compliant'],
        "epl": epl_data,
        "ship_details": {
            "type": ship_type,
            "capacity": capacity,
            "pme": round(pme, 2),
            "me_emissions": round(me_emissions, 2),
            "ae_emissions": round(ae_emissions, 2),
            "numerator": round(numerator, 2)
        }
    }
