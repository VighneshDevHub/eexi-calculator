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
    
    # User's Step 5: Required EEXI with updated 20% reduction (IMO Phase 1)
    # EEDI_ref = 961.79 * (75000 ^ -0.477) = 4.5465
    # Required = 4.5465 * (1 - 0.20) = 3.6372
    assert round(result['required_eexi'], 3) == 3.637
    
    # User says COMPLIANT in example text, but wait...
    # Attained 4.510 > Required 4.319 -> Actually NON_COMPLIANT?
    # Let's re-read the user's example A.
    # Step 6 says: Attained EEXI = 4.510 < Required EEXI = 4.319 (Wait, 4.510 is NOT less than 4.319)
    # The user's example A text has a contradiction: "Attained EEXI = 4.510 < Required EEXI = 4.3192 ... COMPLIANT"
    # Mathematically 4.510 > 4.3192. My code will return NON_COMPLIANT.
    
    assert result['status'] == 'NON_COMPLIANT'

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
    
    # User's Required with updated reduction factor for 8000 DWT
    # EEDI_ref = 107.48 * (8000 ^ -0.216) = 15.426
    # Reduction = 0.30 * (8000-3000)/12000 = 0.125
    # Required = 15.426 * (1 - 0.125) = 13.498
    assert round(result['required_eexi'], 3) == 13.498
    
    # Status: NON_COMPLIANT
    assert result['status'] == 'NON_COMPLIANT'
    
    # EPL: Limited MCR with 83% PME rule
    # Max PME = (13.498 * 8000 * 12.5) / (3.206 * 190) = 1349800 / 609.14 = 2215.9
    # Limited MCR = 2215.9 / 0.83 = 2669.8
    assert round(result['epl']['limited_mcr'], 1) == 2669.8
    # EPL %: 76.3%
    assert round(result['epl']['epl_percentage'], 1) == 76.3
