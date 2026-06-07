"""
calculators/egbp/calculator.py
------------
Exhaust Gas Back Pressure (EGBP) calculation module.
Based on engineering methodology from Wärtsilä document 18505-744-001.
"""

import math
from dataclasses import dataclass

# Pipe material roughness (mm)
ROUGHNESS_MAP: dict[str, float] = {
    "steel_welded":    0.06096,
    "steel_corroded":  0.3,
    "stainless_steel": 0.046,
    "steel_galvanized": 0.15,
    "iron_cast":       0.26,
    "copper_brass":    0.0015,
    "plastic":         0.0015,
}

_BEND_XI_BASE: dict[int, float] = {
    15: 0.0847, 30: 0.1629, 45: 0.2352, 60: 0.2843, 90: 0.3769,
}

# Fixed ξ values extracted directly from sheet cells
FIXED_XI: dict[str, float] = {
    "butterfly_valve":    0.3319,
    "gate_valve":         0.06928,
    "swing_check_valve":  0.4777,
    "lift_check_valve":   5.1821,
    "globe_valve":        8.0,
    "ball_valve":         0.05,
    "outlet":             1.0,
    "silencer_35dba":     2.35,    # 35 dB(A) silencer
    "boiler":             6.0,     # Heat recovery boiler
    "wye_through_equal":  0.17,    # Mixed flows Q1=Q2, α=90°
    "wye_branch_45":      0.20,    # α=45°
    "wye_branch_90":      0.49,
}

ENGINE_PRESETS: dict[str, dict] = {
    "ME": {"label": "Main Engine", "mass_flow": 80.651, "temp_tc": 240.0, "max_bp_pa": 3000.0, "roughness": "steel_welded"},
    "AE_T1": {"label": "Aux Engine T1 (9L32/40)", "mass_flow": 7.395, "temp_tc": 365.0, "max_bp_pa": 3000.0, "roughness": "steel_welded"},
    "AE_T2": {"label": "Aux Engine T2 (8L32/40)", "mass_flow": 6.545, "temp_tc": 365.0, "max_bp_pa": 3000.0, "roughness": "steel_welded"},
    "OFB": {"label": "Oil Fired Boiler", "mass_flow": 1.68, "temp_tc": 300.0, "max_bp_pa": 500.0, "roughness": "steel_welded"},
}

PA_TO_MMWC = 1.0 / 9.80665

@dataclass
class PipeElement:
    element_type: str
    position:     int = 0
    diameter_mm:  float = 0.0
    length_mm:    float = 0.0
    rd:           float = 1.5
    angle_deg:    float = 90.0
    inlet_a_mm:   float = 0.0
    outlet_b_mm:  float = 0.0
    roughness_mm: float = 0.06096
    xi_custom:    float = 1.0
    velocity:     float = 0.0
    xi:           float = 0.0
    pressure_loss_pa: float = 0.0
    reynolds:     float = 0.0
    friction_factor: float = 0.0
    note:         str   = ""

ELEMENT_LABELS = {
    "pipe":              "Straight Pipe",
    "pipe_bend":         "Pipe Bend",
    "diffuser":          "Diffuser / Reduction",
    "wye_through":       "Wye (through)",
    "wye_branch":        "Wye (branch)",
    "butterfly_valve":   "Butterfly Valve",
    "gate_valve":        "Gate Valve",
    "swing_check_valve": "Swing Check Valve",
    "lift_check_valve":  "Lift Check Valve",
    "globe_valve":       "Globe Valve",
    "ball_valve":        "Ball Valve",
    "silencer":          "Silencer",
    "boiler":            "Boiler / Heat Recovery",
    "outlet":            "Outlet (atmospheric)",
    "orifice":           "Orifice",
    "custom":            "Custom (specify ξ)",
}

def exhaust_gas_density(temp_c: float) -> float:
    """ρ = 353.05 / T_K"""
    return 353.05 / (temp_c + 273.15)

def exhaust_gas_viscosity(temp_c: float) -> float:
    """Kinematic viscosity ν = μ / ρ"""
    T_K = temp_c + 273.15
    mu = 1.458e-6 * (T_K ** 1.5) / (T_K + 110.4)
    return mu / exhaust_gas_density(temp_c)

def colebrook_white(Re: float, epsilon_D: float) -> float:
    if Re < 1e-9: return 0.02
    if Re < 2300: return 64.0 / Re
    lam = 0.25 / (math.log10(epsilon_D / 3.7 + 5.74 / (Re ** 0.9))) ** 2
    for _ in range(100):
        lam_new = (-2.0 * math.log10(epsilon_D / 3.7 + 2.51 / (Re * math.sqrt(lam)))) ** -2
        if abs(lam_new - lam) < 1e-10: break
        lam = lam_new
    return lam

def pipe_bend_xi(rd: float, angle_deg: float) -> float:
    angles = sorted(_BEND_XI_BASE.keys())
    a_clip = max(angles[0], min(angles[-1], angle_deg))
    lo = max((a for a in angles if a <= a_clip), default=angles[0])
    hi = min((a for a in angles if a >= a_clip), default=angles[-1])
    if lo == hi:
        xi_base = _BEND_XI_BASE[lo]
    else:
        t = (a_clip - lo) / (hi - lo)
        xi_base = _BEND_XI_BASE[lo] + t * (_BEND_XI_BASE[hi] - _BEND_XI_BASE[lo])
    return xi_base * (1.5 / max(rd, 0.5))

def diffuser_xi(inlet_dia_mm: float, outlet_dia_mm: float) -> float:
    if inlet_dia_mm <= 0 or outlet_dia_mm <= 0: return 0.45
    A1 = math.pi / 4 * (inlet_dia_mm / 1000) ** 2
    A2 = math.pi / 4 * (outlet_dia_mm / 1000) ** 2
    ratio = A1 / A2
    if ratio < 1: # expansion
        return (1 - ratio) ** 2
    return 0.5 * (1 - 1 / ratio) # contraction

def orifice_xi(pipe_dia_mm: float, orifice_dia_mm: float) -> float:
    if pipe_dia_mm <= 0 or orifice_dia_mm <= 0: return 1.45
    beta = orifice_dia_mm / pipe_dia_mm
    if beta <= 0 or beta >= 1: return 1.45
    return (1 / (0.61 * beta ** 2)) ** 2 - 1

def calculate_element(el: PipeElement, mass_flow: float, density: float, visc: float) -> PipeElement:
    D = el.diameter_mm / 1000.0
    A = math.pi / 4 * D ** 2 if D > 0 else 0.0
    Q = mass_flow / density
    v = Q / A if A > 0 else 0.0
    Re = v * D / visc if (D > 0 and visc > 0) else 0.0
    eps_D = (el.roughness_mm / 1000.0) / D if D > 0 else 0.0
    dyn_p = 0.5 * density * v ** 2
    
    xi, lam, note = 0.0, 0.0, ""
    etype = el.element_type
    
    if etype == "pipe":
        lam = colebrook_white(Re, eps_D)
        xi = lam * (el.length_mm / 1000.0) / D if D > 0 else 0.0
        note = f"lambda={lam:.4f} Re={Re:.0f}"
    elif etype == "pipe_bend":
        xi = pipe_bend_xi(el.rd, el.angle_deg)
        note = f"R/d={el.rd} alpha={el.angle_deg} deg"
    elif etype == "diffuser":
        xi = diffuser_xi(el.inlet_a_mm, el.outlet_b_mm)
        # Use inlet diameter for velocity calculation if provided
        a_mm = min(el.inlet_a_mm, el.outlet_b_mm) if el.inlet_a_mm > 0 and el.outlet_b_mm > 0 else el.diameter_mm
        A_in = math.pi / 4 * (a_mm / 1000) ** 2 if a_mm > 0 else A
        v = Q / A_in if A_in > 0 else v
        note = f"in={el.inlet_a_mm} out={el.outlet_b_mm}"
    elif etype == "wye_through":
        xi = FIXED_XI["wye_through_equal"]
    elif etype == "wye_branch":
        xi = FIXED_XI["wye_branch_45"]
    elif etype == "silencer":
        xi = FIXED_XI["silencer_35dba"]
    elif etype == "boiler":
        xi = FIXED_XI["boiler"]
    elif etype == "orifice":
        xi = orifice_xi(el.inlet_a_mm, el.outlet_b_mm)
        note = f"pipe={el.inlet_a_mm} orifice={el.outlet_b_mm}"
    elif etype == "custom":
        xi = el.xi_custom
        note = "user-defined xi"
    else:
        xi = FIXED_XI.get(etype, 0.0)

    el.velocity = round(v, 2)
    el.xi = round(xi, 6)
    el.pressure_loss_pa = round(xi * dyn_p, 2)
    el.reynolds = round(Re, 0)
    el.friction_factor = round(lam, 4)
    el.note = note
    return el

def calculate_egbp(inputs: dict) -> dict:
    mass_flow = float(inputs["mass_flow_kgs"])
    temp_c = float(inputs["temp_tc_c"])
    max_bp = float(inputs.get("max_bp_pa", 3000))
    density = exhaust_gas_density(temp_c)
    visc = exhaust_gas_viscosity(temp_c)
    roughness = ROUGHNESS_MAP.get(inputs.get("roughness_key", "steel_welded"), 0.06096)

    elements = []
    total_pa = 0.0
    for i, e in enumerate(inputs.get("elements", [])):
        el = PipeElement(
            element_type=e["element_type"], position=i+1,
            diameter_mm=float(e.get("diameter_mm", 0) or 0), 
            length_mm=float(e.get("length_mm", 0) or 0),
            rd=float(e.get("rd", 1.5) or 1.5), 
            angle_deg=float(e.get("angle_deg", 90) or 90),
            inlet_a_mm=float(e.get("inlet_a_mm", 0) or 0), 
            outlet_b_mm=float(e.get("outlet_b_mm", 0) or 0),
            roughness_mm=roughness, 
            xi_custom=float(e.get("xi_custom", 1.0) or 1.0)
        )
        el = calculate_element(el, mass_flow, density, visc)
        total_pa += el.pressure_loss_pa
        elements.append(el)

    status = "PASSED" if total_pa <= max_bp * 0.85 else "BORDERLINE" if total_pa <= max_bp else "FAILED"
    return {
        "total_pressure_pa": round(total_pa, 2),
        "total_pressure_mmwc": round(total_pa * PA_TO_MMWC, 2),
        "max_bp_pa": max_bp,
        "status": status,
        "margin_pa": round(max_bp - total_pa, 2),
        "mass_flow_kgs": mass_flow,
        "temp_tc_c": temp_c,
        "roughness_key": inputs.get("roughness_key", "steel_welded"),
        "elements": [
            {**el.__dict__, "label": ELEMENT_LABELS.get(el.element_type, el.element_type)}
            for el in elements
        ]
    }
