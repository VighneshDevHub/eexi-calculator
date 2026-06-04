"""
test_eexi.py
------------
Comprehensive test suite for the EEXI calculation package.

Run with:  python -m pytest test_eexi.py -v
or:        python test_eexi.py          (standalone, no pytest needed)

Test cases include:
  - Phase 2 worked examples (ground truth)
  - Edge cases and error handling
  - All 9 ship types
  - All fuel types
  - EPL derivation
  - Compliance boundary conditions
"""

import sys
import math

# ---------------------------------------------------------------------------
# Allow running from the project root without installing the package
# ---------------------------------------------------------------------------
sys.path.insert(0, ".")
from eexi import (
    calculate,
    get_capacity, get_cf,
    calc_pme, calc_me_emissions, calc_ae_emissions, calc_numerator,
    calc_attained_eexi, calc_required_eexi, check_compliance,
    calc_epl, calc_epl_percentage,
)


# ===========================================================================
# Helper
# ===========================================================================

def approx(a: float, b: float, tol: float = 0.01) -> bool:
    """Return True if a and b are within tol (absolute tolerance)."""
    return abs(a - b) <= tol


PASS = "\033[92mPASS\033[0m"
FAIL = "\033[91mFAIL\033[0m"
results = []

def check(name: str, condition: bool, detail: str = ""):
    icon = PASS if condition else FAIL
    msg = f"  [{icon}] {name}"
    if detail:
        msg += f"  —  {detail}"
    print(msg)
    results.append((name, condition))


# ===========================================================================
# 1.  ship_params — get_capacity
# ===========================================================================
print("\n── 1. ship_params.get_capacity ──────────────────────────────────────")

check("bulk_carrier uses DWT",       get_capacity("bulk_carrier", 75000) == 75000)
check("tanker uses DWT",             get_capacity("tanker", 50000) == 50000)
check("container uses 0.70*DWT",     approx(get_capacity("container", 100000), 70000))
check("ro_ro_pass uses GT",          get_capacity("ro_ro_pass", 0, gt=25000) == 25000)
check("cruise uses GT",              get_capacity("cruise", 0, gt=100000) == 100000)
check("lng_carrier uses DWT",        get_capacity("lng_carrier", 80000) == 80000)

try:
    get_capacity("unknown_type", 50000)
    check("raises on bad ship_type", False)
except ValueError:
    check("raises on bad ship_type", True)

try:
    get_capacity("ro_ro_pass", 50000, gt=0)
    check("raises when GT=0 for GT ship", False)
except ValueError:
    check("raises when GT=0 for GT ship", True)


# ===========================================================================
# 2.  ship_params — get_cf
# ===========================================================================
print("\n── 2. ship_params.get_cf ────────────────────────────────────────────")

check("HFO CF = 3.114",         get_cf("hfo")         == 3.114)
check("MDO CF = 3.206",         get_cf("mdo")         == 3.206)
check("LNG CF = 2.750",         get_cf("lng")         == 2.750)
check("Methanol CF = 1.375",    get_cf("methanol")    == 1.375)
check("LPG propane CF = 3.000", get_cf("lpg_propane") == 3.000)

try:
    get_cf("diesel_99")
    check("raises on bad fuel_type", False)
except ValueError:
    check("raises on bad fuel_type", True)


# ===========================================================================
# 3.  emissions — calc_pme
# ===========================================================================
print("\n── 3. emissions.calc_pme ────────────────────────────────────────────")

check("PME = 0.75 * 12000 = 9000",  calc_pme(12000) == 9000.0)
check("PME = 0.75 * 3500 = 2625",   calc_pme(3500)  == 2625.0)
check("f_eff scales PME",           approx(calc_pme(10000, f_eff=0.9), 6750.0))

try:
    calc_pme(0)
    check("raises when MCR=0", False)
except ValueError:
    check("raises when MCR=0", True)

try:
    calc_pme(10000, f_eff=1.5)
    check("raises when f_eff > 1", False)
except ValueError:
    check("raises when f_eff > 1", True)


# ===========================================================================
# 4.  emissions — calc_me_emissions
# ===========================================================================
print("\n── 4. emissions.calc_me_emissions ───────────────────────────────────")

# Phase 2 Example A: PME=9000, CF=3.114, SFC=175 → 4,904,550
expected_me_a = 9000 * 3.114 * 175
check(f"Example A ME emissions = {expected_me_a:,.0f}",
      approx(calc_me_emissions(9000, 3.114, 175), expected_me_a, tol=1.0))

# Phase 2 Example B: PME=2625, CF=3.206, SFC=190 → 1,596,735
expected_me_b = 2625 * 3.206 * 190
check(f"Example B ME emissions = {expected_me_b:,.0f}",
      approx(calc_me_emissions(2625, 3.206, 190), expected_me_b, tol=1.0))


# ===========================================================================
# 5.  emissions — calc_ae_emissions
# ===========================================================================
print("\n── 5. emissions.calc_ae_emissions ───────────────────────────────────")

check("PAE=0 returns 0",           calc_ae_emissions(0, 3.114, 200) == 0.0)
check("PAE=500, CF=3.206, SFC=200 = 321600",
      approx(calc_ae_emissions(500, 3.206, 200), 500 * 3.206 * 200, tol=1.0))

try:
    calc_ae_emissions(-10, 3.114, 200)
    check("raises when PAE < 0", False)
except ValueError:
    check("raises when PAE < 0", True)


# ===========================================================================
# 6.  eexi — calc_attained_eexi
# ===========================================================================
print("\n── 6. eexi.calc_attained_eexi ───────────────────────────────────────")

# Example A: numerator=4904550, capacity=75000, v_ref=14.5
num_a = 9000 * 3.114 * 175       # 4,904,550
denom_a = 75000 * 14.5            # 1,087,500
expected_a = num_a / denom_a      # ~4.509

attained_a = calc_attained_eexi(num_a, 75000, 14.5)
check(f"Example A attained EEXI ≈ {expected_a:.3f}",
      approx(attained_a, expected_a, tol=0.001),
      f"got {attained_a:.4f}")

# Example B: numerator=1596735, capacity=8000, v_ref=12.5
num_b = 2625 * 3.206 * 190
denom_b = 8000 * 12.5
expected_b = num_b / denom_b

attained_b = calc_attained_eexi(num_b, 8000, 12.5)
check(f"Example B attained EEXI ≈ {expected_b:.3f}",
      approx(attained_b, expected_b, tol=0.001),
      f"got {attained_b:.4f}")


# ===========================================================================
# 7.  eexi — calc_required_eexi
# ===========================================================================
print("\n── 7. eexi.calc_required_eexi ───────────────────────────────────────")

# Example A: bulk_carrier, DWT=75000 → 961.79 * 75000^(-0.477) * 0.95
req_a = 961.79 * (75000 ** -0.477) * 0.95
result_req_a = calc_required_eexi("bulk_carrier", 75000)
check(f"Example A required EEXI ≈ {req_a:.3f}",
      approx(result_req_a, req_a, tol=0.001),
      f"got {result_req_a:.4f}")

# Example B: general_cargo, DWT=8000
req_b = 107.48 * (8000 ** -0.216) * 0.95
result_req_b = calc_required_eexi("general_cargo", 8000)
check(f"Example B required EEXI ≈ {req_b:.3f}",
      approx(result_req_b, req_b, tol=0.001),
      f"got {result_req_b:.4f}")

# Container: reduction should be 10%
req_container = 174.22 * (50000 ** -0.201) * 0.90
check("Container uses 10% reduction",
      approx(calc_required_eexi("container", 50000), req_container, tol=0.001))


# ===========================================================================
# 8.  eexi — check_compliance
# ===========================================================================
print("\n── 8. eexi.check_compliance ─────────────────────────────────────────")

# Example A is compliant
comp_a = check_compliance(attained_a, result_req_a)
check("Example A status = COMPLIANT",    comp_a["status"] == "COMPLIANT")
check("Example A compliant = True",      comp_a["compliant"] is True)
check("Example A margin > 0",            comp_a["margin"] > 0,
      f"margin = {comp_a['margin']:.1f}%")

# Example B is non-compliant
comp_b = check_compliance(attained_b, result_req_b)
check("Example B status = NON_COMPLIANT", comp_b["status"] == "NON_COMPLIANT")
check("Example B compliant = False",      comp_b["compliant"] is False)
check("Example B margin < 0",             comp_b["margin"] < 0,
      f"margin = {comp_b['margin']:.1f}%")

# Borderline: attained just above required
comp_border = check_compliance(result_req_a * 1.03, result_req_a)
check("Borderline (3% over) = BORDERLINE", comp_border["status"] == "BORDERLINE")

# Exact match = compliant
comp_exact = check_compliance(result_req_a, result_req_a)
check("Exact match = COMPLIANT",           comp_exact["status"] == "COMPLIANT")


# ===========================================================================
# 9.  epl — calc_epl
# ===========================================================================
print("\n── 9. epl.calc_epl ──────────────────────────────────────────────────")

# Example B EPL: req=result_req_b, capacity=8000, v_ref=12.5, cf=3.206, sfc=190
epl_b = calc_epl(result_req_b, 8000, 12.5, 3.206, 190)
expected_max_pme_b = (result_req_b * 8000 * 12.5) / (3.206 * 190)
expected_limited_mcr_b = expected_max_pme_b / 0.75

check("EPL feasible for Example B",       epl_b["feasible"] is True)
check(f"EPL max_pme ≈ {expected_max_pme_b:.1f}",
      approx(epl_b["max_pme"], expected_max_pme_b, tol=1.0),
      f"got {epl_b['max_pme']:.1f}")
check(f"EPL limited_mcr ≈ {expected_limited_mcr_b:.1f}",
      approx(epl_b["limited_mcr"], expected_limited_mcr_b, tol=1.0),
      f"got {epl_b['limited_mcr']:.1f}")

epl_pct = calc_epl_percentage(epl_b["limited_mcr"], 3500)
check("EPL percentage < 100% (power must be reduced)", epl_pct < 100.0,
      f"got {epl_pct:.1f}%")

# Infeasible EPL: huge AE emissions
epl_infeasible = calc_epl(0.5, 1000, 5.0, 3.114, 175, ae_emissions=999999)
check("Infeasible EPL flagged correctly", epl_infeasible["feasible"] is False)


# ===========================================================================
# 10.  calculator.calculate — end-to-end (ground truth from Phase 2)
# ===========================================================================
print("\n── 10. calculator.calculate — end-to-end ────────────────────────────")

# Example A — compliant bulk carrier
result_a = calculate({
    "ship_type": "bulk_carrier",
    "dwt": 75000, "gt": 0,
    "mcr": 12000, "sfc_me": 175, "fuel_me": "hfo",
    "v_ref": 14.5,
    "pae": 0, "sfc_ae": 0, "fuel_ae": "hfo",
})
check("E2E Example A: attained ≈ 4.509",
      approx(result_a["attained_eexi"], expected_a, tol=0.01),
      f"got {result_a['attained_eexi']}")
check("E2E Example A: compliant = True",  result_a["compliant"] is True)
check("E2E Example A: epl = None",        result_a["epl"] is None)
check("E2E Example A: margin > 0",        result_a["margin"] > 0)

# Example B — non-compliant general cargo
result_b = calculate({
    "ship_type": "general_cargo",
    "dwt": 8000, "gt": 0,
    "mcr": 3500, "sfc_me": 190, "fuel_me": "mdo",
    "v_ref": 12.5,
    "pae": 0, "sfc_ae": 0, "fuel_ae": "hfo",
})
check("E2E Example B: non-compliant",     result_b["compliant"] is False)
check("E2E Example B: epl is not None",   result_b["epl"] is not None)
check("E2E Example B: EPL feasible",      result_b["epl"]["feasible"] is True)
check("E2E Example B: limited_mcr < 3500",result_b["epl"]["limited_mcr"] < 3500)

# With auxiliary engine
result_aux = calculate({
    "ship_type": "tanker",
    "dwt": 100000, "gt": 0,
    "mcr": 15000, "sfc_me": 168, "fuel_me": "hfo",
    "v_ref": 15.0,
    "pae": 800, "sfc_ae": 200, "fuel_ae": "mdo",
})
check("AE included in numerator",
      result_aux["numerator"] > calc_pme(15000) * 3.114 * 168,
      f"numerator={result_aux['numerator']:.0f}")

# GT-based ship type
result_cruise = calculate({
    "ship_type": "cruise",
    "dwt": 0, "gt": 120000,
    "mcr": 50000, "sfc_me": 175, "fuel_me": "hfo",
    "v_ref": 22.0,
    "pae": 0, "sfc_ae": 0, "fuel_ae": "hfo",
})
check("Cruise ship uses GT as capacity", result_cruise["capacity"] == 120000.0)

# Error handling — missing MCR
try:
    calculate({"ship_type": "bulk_carrier", "dwt": 75000, "mcr": 0,
               "sfc_me": 175, "fuel_me": "hfo", "v_ref": 14.5})
    check("raises ValueError on mcr=0", False)
except ValueError:
    check("raises ValueError on mcr=0", True)


# ===========================================================================
# 11.  All 9 ship types smoke test
# ===========================================================================
print("\n── 11. All ship types — smoke test ──────────────────────────────────")

SMOKE_INPUTS = {
    "bulk_carrier":  {"dwt": 75000,  "gt": 0,      "mcr": 12000, "sfc_me": 175, "v_ref": 14.5},
    "tanker":        {"dwt": 100000, "gt": 0,       "mcr": 15000, "sfc_me": 168, "v_ref": 15.0},
    "container":     {"dwt": 80000,  "gt": 0,       "mcr": 40000, "sfc_me": 165, "v_ref": 22.0},
    "general_cargo": {"dwt": 20000,  "gt": 0,       "mcr": 5000,  "sfc_me": 185, "v_ref": 13.0},
    "ro_ro_cargo":   {"dwt": 15000,  "gt": 0,       "mcr": 8000,  "sfc_me": 180, "v_ref": 18.0},
    "ro_ro_pass":    {"dwt": 0,      "gt": 30000,   "mcr": 20000, "sfc_me": 175, "v_ref": 20.0},
    "lng_carrier":   {"dwt": 70000,  "gt": 0,       "mcr": 22000, "sfc_me": 160, "v_ref": 19.5},
    "gas_carrier":   {"dwt": 40000,  "gt": 0,       "mcr": 10000, "sfc_me": 172, "v_ref": 16.0},
    "cruise":        {"dwt": 0,      "gt": 120000,  "mcr": 50000, "sfc_me": 175, "v_ref": 22.0},
}

for stype, inp in SMOKE_INPUTS.items():
    try:
        r = calculate({**inp, "fuel_me": "hfo", "pae": 0, "sfc_ae": 0, "fuel_ae": "hfo"})
        ok = (
            isinstance(r["attained_eexi"], float) and r["attained_eexi"] > 0
            and isinstance(r["required_eexi"], float) and r["required_eexi"] > 0
            and r["status"] in ("COMPLIANT", "BORDERLINE", "NON_COMPLIANT")
        )
        check(f"{stype}: returns valid result ({r['status']}, att={r['attained_eexi']:.2f}, req={r['required_eexi']:.2f})", ok)
    except Exception as e:
        check(f"{stype}: no exception", False, str(e))


# ===========================================================================
# Summary
# ===========================================================================
print("\n" + "=" * 60)
passed = sum(1 for _, ok in results if ok)
failed = sum(1 for _, ok in results if not ok)
total  = len(results)
print(f"  Results: {passed}/{total} passed  |  {failed} failed")
if failed == 0:
    print("  \033[92mAll tests passed — Phase 3 code verified.\033[0m")
else:
    print("  \033[91mSome tests failed — review output above.\033[0m")
    failed_names = [name for name, ok in results if not ok]
    for n in failed_names:
        print(f"    FAILED: {n}")
print("=" * 60)
