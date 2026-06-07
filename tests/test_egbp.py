import pytest
from calculators.egbp.calculator import calculate_egbp, ROUGHNESS_MAP

def test_egbp_simple_pipe():
    """Test EGBP for a simple straight pipe."""
    inputs = {
        'mass_flow_kgs': 80.651,
        'temp_tc_c': 240.0,
        'max_bp_pa': 3000,
        'roughness_key': 'steel_welded',
        'elements': [
            {
                'element_type': 'pipe',
                'diameter_mm': 1000,
                'length_mm': 5000
            }
        ]
    }
    
    result = calculate_egbp(inputs)
    
    assert result['total_pressure_pa'] > 0
    assert result['status'] == 'PASSED'
    assert len(result['elements']) == 1
    assert result['elements'][0]['element_type'] == 'pipe'
    assert result['elements'][0]['pressure_loss_pa'] > 0

def test_egbp_complex_system():
    """Test EGBP for a complex system with multiple elements."""
    inputs = {
        'mass_flow_kgs': 80.651,
        'temp_tc_c': 240.0,
        'max_bp_pa': 3000,
        'roughness_key': 'steel_welded',
        'elements': [
            {'element_type': 'pipe', 'diameter_mm': 1000, 'length_mm': 5000},
            {'element_type': 'pipe_bend', 'diameter_mm': 1000, 'rd': 1.5, 'angle_deg': 90},
            {'element_type': 'butterfly_valve', 'diameter_mm': 1000},
            {'element_type': 'outlet', 'diameter_mm': 1000}
        ]
    }
    
    result = calculate_egbp(inputs)
    
    assert result['total_pressure_pa'] > 0
    assert len(result['elements']) == 4
    # Outlet should have xi = 1.0
    outlet = next(e for e in result['elements'] if e['element_type'] == 'outlet')
    assert outlet['xi'] == 1.0

def test_egbp_failed_status():
    """Test EGBP when back pressure exceeds limit."""
    inputs = {
        'mass_flow_kgs': 200.0,  # Very high mass flow
        'temp_tc_c': 240.0,
        'max_bp_pa': 500,        # Very low limit
        'elements': [
            {'element_type': 'pipe', 'diameter_mm': 500, 'length_mm': 10000}
        ]
    }
    
    result = calculate_egbp(inputs)
    assert result['status'] == 'FAILED'
