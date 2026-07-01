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
        
        if data.get('dwt'):
            try:
                if float(data['dwt']) < 0:
                    return False, "DWT cannot be negative."
            except (ValueError, TypeError):
                pass
        if data.get('gt'):
            try:
                if float(data['gt']) < 0:
                    return False, "GT cannot be negative."
            except (ValueError, TypeError):
                pass
            
        # Optional fields validation
        if data.get('pae'):
            try:
                if float(data['pae']) < 0:
                    return False, "PAE cannot be negative."
            except (ValueError, TypeError):
                pass
        if data.get('sfc_ae'):
            try:
                if float(data['sfc_ae']) < 0:
                    return False, "Auxiliary SFC cannot be negative."
            except (ValueError, TypeError):
                pass
        if data.get('f_eff'):
            try:
                f_eff = float(data['f_eff'])
                if not (0.0 < f_eff <= 1.0):
                    return False, "f_eff must be between 0 and 1."
            except (ValueError, TypeError):
                pass
        if data.get('f_i'):
            try:
                if float(data['f_i']) <= 0:
                    return False, "f_i must be positive."
            except (ValueError, TypeError):
                pass
        if data.get('f_w'):
            try:
                if float(data['f_w']) <= 0:
                    return False, "f_w must be positive."
            except (ValueError, TypeError):
                pass
        if data.get('f_c'):
            try:
                if float(data['f_c']) <= 0:
                    return False, "f_c must be positive."
            except (ValueError, TypeError):
                pass
        if data.get('f_l'):
            try:
                if float(data['f_l']) <= 0:
                    return False, "f_l must be positive."
            except (ValueError, TypeError):
                pass
        if data.get('f_m'):
            try:
                if float(data['f_m']) <= 0:
                    return False, "f_m must be positive."
            except (ValueError, TypeError):
                pass
        
        # Advanced EPL fields
        if data.get('sfc_lim'):
            try:
                if float(data['sfc_lim']) <= 0:
                    return False, "SFC at MCRlim must be greater than 0."
            except (ValueError, TypeError):
                pass
        
        return True, ""
    except (ValueError, TypeError):
        return False, "Invalid numeric input."
