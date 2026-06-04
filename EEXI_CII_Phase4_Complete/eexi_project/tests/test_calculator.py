"""
tests/test_calculator.py
Integration tests — full pipeline through calculator.calculate().
Validates against Phase 2 worked examples.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from eexi.calculator import calculate


EXAMPLE_A = dict(
    ship_type="bulk_carrier", dwt=150000, mcr=12000,
    sfc=175, fuel_type="hfo", v_ref=14.5
)

EXAMPLE_B = dict(
    ship_type="general_cargo", dwt=8000, mcr=3500,
    sfc=190, fuel_type="mdo", v_ref=12.5
)


class TestCalculatorExampleA:
    """Phase 2 Example A — bulk carrier, compliant."""

    def setup_method(self):
        self.result = calculate(EXAMPLE_A)

    def test_attained_eexi_approx(self):
        assert self.result["attained_eexi"] == pytest.approx(2.255, abs=0.002)

    def test_required_eexi_approx(self):
        import math
        expected = 961.79 * (150000 ** -0.477) * 0.95
        assert self.result["required_eexi"] == pytest.approx(expected, rel=1e-4)

    def test_pme(self):
        assert self.result["pme"] == pytest.approx(9000.0)

    def test_capacity(self):
        assert self.result["capacity"] == pytest.approx(150000.0)

    def test_compliant(self):
        assert self.result["compliance"]["compliant"] is True

    def test_status_compliant(self):
        assert self.result["compliance"]["status"] in ("COMPLIANT", "BORDERLINE")

    def test_epl_is_none_when_compliant(self):
        assert self.result["epl"] is None

    def test_margin_positive(self):
        assert self.result["compliance"]["margin"] > 0


class TestCalculatorExampleB:
    """Phase 2 Example B — general cargo, non-compliant, EPL required."""

    def setup_method(self):
        self.result = calculate(EXAMPLE_B)

    def test_non_compliant(self):
        assert self.result["compliance"]["compliant"] is False

    def test_status_non_compliant(self):
        assert self.result["compliance"]["status"] == "NON_COMPLIANT"

    def test_margin_negative(self):
        assert self.result["compliance"]["margin"] < 0

    def test_epl_present(self):
        assert self.result["epl"] is not None

    def test_epl_possible(self):
        assert self.result["epl"]["epl_possible"] is True

    def test_epl_limited_mcr_less_than_installed(self):
        assert self.result["epl"]["limited_mcr"] < EXAMPLE_B["mcr"]

    def test_epl_percentage_less_than_100(self):
        assert self.result["epl"]["epl_percentage"] < 100.0


class TestCalculatorEdgeCases:
    def test_container_ship_capacity_factor(self):
        r = calculate(dict(ship_type="container", dwt=100000, mcr=20000,
                           sfc=170, fuel_type="hfo", v_ref=22.0))
        assert r["capacity"] == pytest.approx(70000.0)

    def test_ro_ro_pass_uses_gt(self):
        r = calculate(dict(ship_type="ro_ro_pass", gt=45000, dwt=0,
                           mcr=8000, sfc=185, fuel_type="mdo", v_ref=18.0))
        assert r["capacity"] == pytest.approx(45000.0)

    def test_with_auxiliary_engine(self):
        inp = {**EXAMPLE_A, "pae": 500, "sfc_ae": 200, "fuel_ae": "mdo"}
        r = calculate(inp)
        assert r["ae_emissions"] == pytest.approx(500 * 3.206 * 200, rel=1e-4)

    def test_missing_mcr_raises(self):
        bad = {k: v for k, v in EXAMPLE_A.items() if k != "mcr"}
        with pytest.raises(KeyError):
            calculate(bad)

    def test_invalid_ship_type_raises(self):
        with pytest.raises(ValueError):
            calculate({**EXAMPLE_A, "ship_type": "barge"})

    def test_zero_speed_raises(self):
        with pytest.raises(ValueError):
            calculate({**EXAMPLE_A, "v_ref": 0})

    def test_lng_fuel(self):
        r = calculate({**EXAMPLE_A, "fuel_type": "lng"})
        assert r["cf_me"] == pytest.approx(2.750)
