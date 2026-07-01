"""
calculators/pipe_wall/calculator.py
ASME B31.3 §304.1.2 pipe wall thickness calculation module.
Based on the Excel-based engineering calculation sheet.
"""

import math

# --- ASME B31.3 Data ---

# Nominal Pipe Size (NPS) to Outside Diameter (mm)
NPS_DEXT_MM = {
    0.125: 10.3, 0.25: 13.7, 0.375: 17.1, 0.5: 21.3, 0.75: 26.7,
    1.0: 33.4, 1.25: 42.2, 1.5: 48.3, 2.0: 60.3, 2.5: 73.0,
    3.0: 88.9, 3.5: 101.6, 4.0: 114.3, 5.0: 141.3, 6.0: 168.3,
    8.0: 219.1, 10.0: 273.1, 12.0: 323.9, 14.0: 355.6, 16.0: 406.4,
    18.0: 457.2, 20.0: 508.0, 24.0: 610.0
}

# Weld joint types and corresponding E factors (Table A-1B)
WELD_E = {
    "S": 1.0, "ERW": 0.85, "LPG": 0.6, "FG": 0.7, "FBW": 0.9
}
WELD_LABELS = {
    "S": "Seamless",
    "ERW": "ERW (Electric Resistance Welded)",
    "LPG": "Longitudinal PGW",
    "FG": "Furnace Butt Weld",
    "FBW": "Flash Butt Weld"
}

# Thread depth (TD) for NPT threads (mm)
THREAD_DEPTH_MM = {
    0.125: 0.572, 0.25: 0.794, 0.375: 1.016, 0.5: 1.270, 0.75: 1.473,
    1.0: 1.829, 1.25: 1.829, 1.5: 1.829, 2.0: 1.913, 2.5: 2.223,
    3.0: 2.223, 3.5: 2.223, 4.0: 2.540, 5.0: 2.540, 6.0: 2.540,
    8.0: 2.858, 10.0: 3.175, 12.0: 3.175, 14.0: 3.175, 16.0: 3.175,
    18.0: 3.175, 20.0: 3.175, 24.0: 3.175
}

# Temperature columns (°C) for Table A-1
TEMP_COLS_C = [
    37.78, 93.33, 148.89, 204.44, 260.00, 315.56, 343.33, 371.11,
    398.89, 426.67, 454.44, 482.22, 510.00, 537.78, 565.56
]

# Material allowable stress values (MPa) at each temperature column
MATERIAL_STRESS = {
    "A106A": [137.9, 137.9, 137.9, 131.0, 119.0, 106.0, 93.0, 82.0, 72.0, 61.0, 51.0, 41.0, 31.0, 20.0, 10.0],
    "A106B": [137.9, 137.9, 137.9, 131.0, 119.0, 106.0, 93.0, 82.0, 72.0, 61.0, 51.0, 41.0, 31.0, 20.0, 10.0],
    "A106C": [165.0, 165.0, 165.0, 159.0, 145.0, 131.0, 117.0, 103.0, 89.0, 76.0, 62.0, 48.0, 34.0, 20.0, 10.0],
    "A53A": [137.9, 137.9, 137.9, 131.0, 119.0, 106.0, 93.0, 82.0, 72.0, 61.0, 51.0, 41.0, 31.0, 20.0, 10.0],
    "A53B": [137.9, 137.9, 137.9, 131.0, 130.31, 106.0, 93.0, 82.0, 72.0, 61.0, 51.0, 41.0, 31.0, 20.0, 10.0],
    "API5LB": [137.9, 137.9, 137.9, 131.0, 119.0, 106.0, 93.0, 82.0, 72.0, 61.0, 51.0, 41.0, 31.0, 20.0, 10.0],
    "API5LX42": [145.0, 145.0, 145.0, 138.0, 124.0, 110.0, 97.0, 84.0, 73.0, 62.0, 51.0, 41.0, 31.0, 20.0, 10.0],
    "API5LX52": [179.0, 179.0, 179.0, 172.0, 156.0, 138.0, 121.0, 106.0, 90.0, 76.0, 62.0, 48.0, 34.0, 20.0, 10.0],
    "SS304L": [117.0, 117.0, 117.0, 117.0, 117.0, 110.0, 101.0, 92.0, 83.0, 74.0, 66.0, 58.0, 49.0, 41.0, 34.0],
    "SS316L": [117.0, 117.0, 117.0, 117.0, 117.0, 110.0, 101.0, 92.0, 83.0, 74.0, 66.0, 58.0, 49.0, 41.0, 34.0],
}

MATERIAL_LABELS = {
    "A106A": "A106 Grade A",
    "A106B": "A106 Grade B",
    "A106C": "A106 Grade C",
    "A53A": "A53 Grade A",
    "A53B": "A53 Grade B",
    "API5LB": "API 5L Grade B",
    "API5LX42": "API 5L X42",
    "API5LX52": "API 5L X52",
    "SS304L": "304L Stainless Steel",
    "SS316L": "316L Stainless Steel",
}

# ASME B36.10M schedule thicknesses (mm) by NPS
SCHEDULE_THICKNESS = {
    0.5: {
        "5": 1.65, "10": 2.11, "40": 2.77, "80": 3.91, "160": 5.56
    },
    1.0: {
        "5": 2.11, "10": 2.77, "40": 3.38, "80": 4.55, "160": 6.35
    },
    2.0: {
        "5": 2.77, "10": 3.05, "40": 3.91, "80": 5.54, "120": 7.01, "160": 8.74, "XXS": 11.07
    },
    3.0: {
        "5": 3.05, "10": 3.76, "40": 5.49, "80": 7.62, "120": 9.53, "160": 11.13, "XXS": 12.70
    },
    4.0: {
        "5": 3.05, "10": 4.57, "40": 6.35, "80": 8.56, "120": 10.97, "160": 12.70, "XXS": 15.09
    },
    6.0: {
        "5": 3.40, "10": 5.54, "40": 7.11, "80": 10.31, "120": 12.70, "160": 15.09, "XXS": 17.45
    },
    8.0: {
        "5": 3.76, "10": 6.35, "40": 8.18, "80": 12.70, "120": 15.09, "160": 18.26, "XXS": 21.44
    },
    10.0: {
        "5": 4.19, "10": 6.35, "40": 9.27, "80": 14.27, "120": 17.45, "160": 21.44, "XXS": 25.40
    },
    12.0: {
        "5": 4.57, "10": 6.35, "40": 9.53, "80": 15.88, "120": 20.62, "160": 25.40, "XXS": 28.58
    },
}

# Recommended minimum schedules
RECOMMENDED_MIN_SCH = {
    "NPS 1/2\"": {"cs_api": "40", "cs_corp": "40", "ss": "10S"},
    "NPS 3/4\"": {"cs_api": "40", "cs_corp": "40", "ss": "10S"},
    "NPS 1\"": {"cs_api": "40", "cs_corp": "40", "ss": "10S"},
    "NPS 2\"": {"cs_api": "40", "cs_corp": "80", "ss": "10S"},
    "NPS 3\"": {"cs_api": "40", "cs_corp": "80", "ss": "10S"},
    "NPS 4\"": {"cs_api": "40", "cs_corp": "80", "ss": "10S"},
    "NPS 6\"": {"cs_api": "40", "cs_corp": "40", "ss": "10S"},
    "NPS 8\"": {"cs_api": "40", "cs_corp": "40", "ss": "10S"},
    "NPS 10\"": {"cs_api": "40", "cs_corp": "40", "ss": "10S"},
    "NPS 12\"": {"cs_api": "40", "cs_corp": "40", "ss": "10S"},
}


def get_allowable_stress(material, temp_c):
    """Get allowable stress S (MPa) by linear interpolation of Table A-1."""
    if material not in MATERIAL_STRESS:
        raise ValueError(f"Material '{material}' not in database")
    
    stress_vals = MATERIAL_STRESS[material]
    
    # Clamp temperature to table bounds
    if temp_c <= TEMP_COLS_C[0]:
        return stress_vals[0]
    if temp_c >= TEMP_COLS_C[-1]:
        return stress_vals[-1]
    
    # Find two bounding temperatures
    for i in range(len(TEMP_COLS_C) - 1):
        t0, t1 = TEMP_COLS_C[i], TEMP_COLS_C[i+1]
        s0, s1 = stress_vals[i], stress_vals[i+1]
        if t0 <= temp_c <= t1:
            # Linear interpolation
            frac = (temp_c - t0) / (t1 - t0)
            return s0 + frac * (s1 - s0)
    
    return stress_vals[-1]


def y_coefficient(temp_c, material_type="ferritic"):
    """Get Y coefficient per ASME B31.3 §304.1.1."""
    if temp_c <= 482:
        return 0.4
    if temp_c >= 566:
        if material_type in ["austenitic", "other"]:
            return 0.4
        else:
            return 0.7
    # Interpolate between 482-510-566 for ferritic
    if temp_c <= 510:
        return 0.4 + (0.1) * (temp_c - 482) / (28)
    else:
        return 0.5 + (0.2) * (temp_c - 510) / (56)


def find_adequate_schedules(nps, t_min_mm):
    """Find all ASME B36.10M schedules with thickness >= t_min."""
    if nps not in SCHEDULE_THICKNESS:
        # Return empty for sizes not in the detailed table
        return []
    scheds = SCHEDULE_THICKNESS[nps]
    result = []
    for sched, thick in scheds.items():
        result.append({
            "schedule": sched,
            "thickness_mm": thick,
            "adequate": thick >= t_min_mm
        })
    # Sort by thickness ascending
    result.sort(key=lambda x: x["thickness_mm"])
    return result


def calculate_pipe_wall(inputs):
    """
    Calculate pipe wall thickness per ASME B31.3 §304.1.2.
    
    Args:
        inputs (dict): Input parameters
            - nps: Nominal pipe size
            - pressure_mpa: Design pressure (MPa gauge)
            - temp_c: Design temperature (°C)
            - material: Material code
            - weld_type: Weld type code
            - corrosion_mm: Corrosion allowance (mm)
            - threaded: Whether pipe is threaded (bool)
            - mill_tolerance: Mill tolerance (%)
            - s_allow_override: Override allowable stress (optional, MPa)
            - dext_override: Override outside diameter (optional, mm)
            - material_type: Material type for Y coefficient (ferritic/austenitic/other)
    
    Returns:
        dict: Calculation results
    """
    nps = inputs["nps"]
    pressure_mpa = inputs["pressure_mpa"]
    temp_c = inputs["temp_c"]
    material = inputs["material"]
    weld_type = inputs["weld_type"]
    corrosion_mm = inputs.get("corrosion_mm", 1.6)
    threaded = inputs.get("threaded", False)
    mill_tolerance = inputs.get("mill_tolerance", 12.5)
    material_type = inputs.get("material_type", "ferritic")
    
    # Input validation
    if pressure_mpa < 0:
        raise ValueError("Design pressure cannot be negative")
    if material not in MATERIAL_STRESS:
        raise ValueError(f"Unknown material: {material}")
    if weld_type not in WELD_E:
        raise ValueError(f"Unknown weld type: {weld_type}")
    
    # Get geometry
    dext_mm = inputs.get("dext_override") or NPS_DEXT_MM.get(nps, 0.0)
    if not dext_mm:
        raise ValueError(f"Unknown NPS: {nps}")
    
    # Get stress and factors
    if "s_allow_override" in inputs and inputs["s_allow_override"]:
        S_mpa = float(inputs["s_allow_override"])
    else:
        S_mpa = get_allowable_stress(material, temp_c)
    
    E = WELD_E[weld_type]
    Y = y_coefficient(temp_c, material_type)
    
    # Thread depth
    TD_mm = THREAD_DEPTH_MM.get(nps, 0.0) if threaded else 0.0
    CA_mm = corrosion_mm
    OT_mm = CA_mm + TD_mm  # total allowance
    
    # Pressure design thickness (Eq 3a)
    if pressure_mpa <= 0:
        t_dis_mm = 0.0
    else:
        numerator = pressure_mpa * dext_mm
        denominator = 2 * (S_mpa * E + pressure_mpa * Y)
        t_dis_mm = numerator / denominator
    
    # Required and minimum thickness
    t_req_mm = t_dis_mm + OT_mm
    t_min_mm = t_req_mm * 100 / (100 - mill_tolerance)
    
    # Find schedules
    schedules = find_adequate_schedules(nps, t_min_mm)
    recommended_schedule = next((s for s in schedules if s["adequate"]), None)
    
    # Check thin-wall condition (t < d/6)
    thin_wall_limit_mm = dext_mm / 6.0
    thin_wall_ok = t_dis_mm < thin_wall_limit_mm
    
    return {
        "dext_mm": dext_mm,
        "S_mpa": S_mpa,
        "E_factor": E,
        "Y_coeff": Y,
        "CA_mm": CA_mm,
        "TD_mm": TD_mm,
        "OT_mm": OT_mm,
        "mill_tolerance": mill_tolerance,
        "t_dis_mm": t_dis_mm,
        "t_req_mm": t_req_mm,
        "t_min_mm": t_min_mm,
        "thin_wall_limit_mm": thin_wall_limit_mm,
        "thin_wall_ok": thin_wall_ok,
        "schedules": schedules,
        "recommended_schedule": recommended_schedule
    }