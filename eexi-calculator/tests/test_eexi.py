import pytest
from eexi.calculator import calculate_eexi
from eexi.emissions import calc_pme, calc_me_emissions
from eexi.eexi import calc_attained_eexi, calc_required_eexi

def test_example_a_compliant_bulk_carrier():
    """
    Validation based on User's Example A:
    Ship type: Bulk carrier
    DWT: 75,000
    MCR: 12,000 kW
    SFC: 175 g/kWh
    Fuel: HFO (CF=3.114)
    Speed: 14.5 knots
    """
    data = {
        'ship_type': 'bulk_carrier',
        'dwt': 75000,
        'mcr': 12000,
        'sfc': 175,
        'fuel_type': 'hfo',
        'speed': 14.5
    }
    
    result = calculate_eexi(data)
    
    # User's Step 1: PME = 0.75 * 12000 = 9000
    assert calc_pme(12000) == 9000
    
    # User's Step 4: Attained EEXI = 4.510
    assert round(result['attained_eexi'], 3) == 4.510
    
    # User's Step 5: Required EEXI = 4.3192 (User says 4.319)
    assert round(result['required_eexi'], 3) == 4.319
    
    # User says COMPLIANT in example text, but wait...
    # Attained 4.510 > Required 4.319 -> Actually NON_COMPLIANT?
    # Let's re-read the user's example A.
    # Step 6 says: Attained EEXI = 4.510 < Required EEXI = 4.319 (Wait, 4.510 is NOT less than 4.319)
    # The user's example A text has a contradiction: "Attained EEXI = 4.510 < Required EEXI = 4.3192 ... COMPLIANT"
    # Mathematically 4.510 > 4.3192. My code will return NON_COMPLIANT (or borderline if within 5%).
    # 4.3192 * 1.05 = 4.535. 
    # 4.510 is less than 4.535, so it should be BORDERLINE.
    
    assert result['status'] == 'BORDERLINE'

def test_example_b_non_compliant_general_cargo():
    """
    Validation based on User's Example B:
    Ship type: General cargo
    DWT: 8,000
    MCR: 3,500 kW
    SFC: 190 g/kWh
    Fuel: MDO (CF=3.206)
    Speed: 12.5 knots
    """
    data = {
        'ship_type': 'general_cargo',
        'dwt': 8000,
        'mcr': 3500,
        'sfc': 190,
        'fuel_type': 'mdo',
        'speed': 12.5
    }
    
    result = calculate_eexi(data)
    
    # User's Attained: 15.990
    assert round(result['attained_eexi'], 3) == 15.990
    
    # User's Required: 14.655
    assert round(result['required_eexi'], 3) == 14.655
    
    # Status: NON_COMPLIANT
    assert result['status'] == 'NON_COMPLIANT'
    
    # EPL: Limited MCR = 3207.8
    assert round(result['epl']['limited_mcr'], 1) == 3207.8
    # EPL %: 91.7%
    assert round(result['epl']['epl_percentage'], 1) == 91.7
