"""
Input validation for ship parameters.
"""

def validate_inputs(data: dict) -> tuple[bool, str]:
    """
    Validates the input dictionary for EEXI calculation.
    Returns (True, "") if valid, (False, "error message") otherwise.
    """
    required_fields = ['ship_type', 'mcr', 'sfc', 'fuel_type', 'speed']
    
    # Check if at least one of DWT or GT is provided
    if not data.get('dwt') and not data.get('gt'):
        return False, "Either DWT or GT must be provided."

    for field in required_fields:
        if field not in data or data[field] == "":
            return False, f"Missing required field: {field}"
            
    try:
        # Numeric validations
        if float(data['mcr']) <= 0:
            return False, "MCR must be greater than 0."
        if float(data['sfc']) <= 0:
            return False, "SFC must be greater than 0."
        if float(data['speed']) <= 0:
            return False, "Design speed must be greater than 0."
        
        if data.get('dwt') and data.get('dwt') != "" and float(data['dwt']) < 0:
            return False, "DWT cannot be negative."
        if data.get('gt') and data.get('gt') != "" and float(data['gt']) < 0:
            return False, "GT cannot be negative."
            
        # Optional fields validation
        if data.get('pae') and data.get('pae') != "" and float(data['pae']) < 0:
            return False, "PAE cannot be negative."
        if data.get('sfc_ae') and data.get('sfc_ae') != "" and float(data['sfc_ae']) < 0:
            return False, "Auxiliary SFC cannot be negative."
        if data.get('f_eff') and data.get('f_eff') != "":
            f_eff = float(data['f_eff'])
            if not (0.0 < f_eff <= 1.0):
                return False, "f_eff must be between 0 and 1."
        if data.get('f_i') and data.get('f_i') != "" and float(data['f_i']) <= 0:
            return False, "f_i must be positive."
        if data.get('f_w') and data.get('f_w') != "" and float(data['f_w']) <= 0:
            return False, "f_w must be positive."

    except ValueError:
        return False, "Invalid numeric input."
        
    return True, ""
