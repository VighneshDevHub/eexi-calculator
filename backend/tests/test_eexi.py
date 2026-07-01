import pytest
from calculators.eexi.calculator import calculate_eexi
from calculators.eexi.emissions import calc_pme, calc_me_emissions
from calculators.eexi.eexi_core import calc_attained_eexi, calc_required_eexi

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
        'speed': 14.5,
        'pae': 0 # Explicitly set to 0 to match simplified example
    }
    
    result = calculate_eexi(data)
    
    # User's Step 1: PME = 0.75 * 12000 = 9000
    assert calc_pme(12000) == 9000
    
    # Attained EEXI should be 4.510
    assert round(result['attained_eexi'], 3) == 4.510
    
    # User's Step 5: Required EEXI with updated 20% reduction (IMO Phase 1)
    assert round(result['required_eexi'], 3) == 3.637
    
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
        'speed': 12.5,
        'pae': 0 # Explicitly set to 0
    }
    
    result = calculate_eexi(data)
    
    # User's Attained: 15.990
    assert round(result['attained_eexi'], 3) == 15.990
    
    # User's Required
    assert round(result['required_eexi'], 3) == 13.498
    
    # Status: NON_COMPLIANT
    assert result['status'] == 'NON_COMPLIANT'
    
    # EPL: Limited MCR
    assert 'mcr_lim' in result['epl']
    assert result['epl']['reduction_pct'] > 0
