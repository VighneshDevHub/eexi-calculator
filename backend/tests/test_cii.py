import pytest
from calculators.cii.calculator import calculate_cii

def test_cii_basic():
    """Test basic CII calculation for a tanker."""
    inputs = {
        'ship_type': 'tanker',
        'dwt': 50000,
        'year': 2024,
        'distance_nm': 100000,
        'fc_hfo': 5000  # 5000 tonnes
    }
    
    result = calculate_cii(inputs)
    
    assert result['attained_cii'] > 0
    assert result['required_cii'] > 0
    assert 'rating' in result
    assert result['year'] == 2024
    assert result['distance_nm'] == 100000

def test_cii_with_corrections():
    """Test CII with corrections applied."""
    inputs = {
        'ship_type': 'tanker',
        'dwt': 50000,
        'year': 2024,
        'distance_nm': 100000,
        'fc_hfo': 5000,
        'sts_operation': True,
        'reefer_kwh': 10000
    }
    
    result = calculate_cii(inputs)
    
    assert len(result['corrections_applied']) > 0
    # Attained CII should be different (usually lower with deductions)
    assert result['attained_cii'] > 0
