"""
tests/test_cii.py
Tests for CII module: MEPC.352(78) + MEPC.355(78) correction factors.
"""
import pytest, math, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from eexi.cii import (
    calc_af_tanker_sts, calc_af_tanker_shuttle,
    calc_fc_electrical_reefer_monitored, calc_fc_electrical_reefer_unmonitored,
    calc_attained_cii, calc_required_cii, get_cii_capacity, rate_cii, calculate_cii
)


class TestSTS_Corrections:
    """MEPC.355(78) §4.2 — STS and shuttle tanker correction factors."""

    def test_af_sts_formula(self):
        dwt = 100000
        expected = 6.1742 * (dwt ** -0.246)
        assert calc_af_tanker_sts(dwt) == pytest.approx(expected, rel=1e-6)

    def test_af_shuttle_formula(self):
        dwt = 80000
        expected = 5.6805 * (dwt ** -0.208)
        assert calc_af_tanker_shuttle(dwt) == pytest.approx(expected, rel=1e-6)

    def test_af_sts_positive(self):
        assert calc_af_tanker_sts(50000) > 0

    def test_af_shuttle_less_than_1(self):
        # For large ships AF < 1 (it's a correction factor, not a multiplier > 1)
        assert calc_af_tanker_shuttle(100000) < 1.0

    def test_zero_dwt_raises(self):
        with pytest.raises(ValueError):
            calc_af_tanker_sts(0)
        with pytest.raises(ValueError):
            calc_af_tanker_shuttle(0)


class TestReeferCorrections:
    """MEPC.355(78) Appendix 1, Part A — electrical corrections for reefers."""

    def test_monitored_formula(self):
        # FCelectrical = Reefer_kWh × SFOC
        kwh, sfoc = 500000, 175
        assert calc_fc_electrical_reefer_monitored(kwh, sfoc) == pytest.approx(kwh * sfoc)

    def test_unmonitored_formula(self):
        # FCelectrical = 2.75 × 24 × SFOC × (days_sea + days_port)
        days_sea, days_port, sfoc = 200, 50, 175
        expected = 2.75 * 24 * sfoc * (days_sea + days_port)
        assert calc_fc_electrical_reefer_unmonitored(days_sea, days_port, sfoc) == pytest.approx(expected)

    def test_unmonitored_zero_port_days(self):
        result = calc_fc_electrical_reefer_unmonitored(100, 0, 175)
        assert result == pytest.approx(2.75 * 24 * 175 * 100)

    def test_custom_cx(self):
        # cx = 3.0 instead of default 2.75
        r1 = calc_fc_electrical_reefer_unmonitored(100, 0, 175, cx=2.75)
        r2 = calc_fc_electrical_reefer_unmonitored(100, 0, 175, cx=3.0)
        assert r2 > r1


class TestRequiredCII:
    """MEPC.353(78) reference lines × reduction factor."""

    def test_bulk_carrier_2024(self):
        # a=4745, c=0.622, dd=7% for 2024
        expected = 4745.0 * (75000 ** -0.622) * (1 - 7/100)
        assert calc_required_cii("bulk_carrier", 75000, 2024) == pytest.approx(expected, rel=1e-5)

    def test_reduction_increases_with_year(self):
        r2023 = calc_required_cii("tanker", 50000, 2023)
        r2024 = calc_required_cii("tanker", 50000, 2024)
        r2025 = calc_required_cii("tanker", 50000, 2025)
        # Higher reduction → lower required CII each year
        assert r2023 > r2024 > r2025

    def test_container_2025(self):
        expected = 1984.0 * (100000 ** -0.489) * (1 - 9/100)
        assert calc_required_cii("container", 100000, 2025) == pytest.approx(expected, rel=1e-5)

    def test_invalid_ship_raises(self):
        with pytest.raises(ValueError):
            calc_required_cii("barge", 50000, 2024)

    def test_zero_dwt_raises(self):
        with pytest.raises(ValueError):
            calc_required_cii("bulk_carrier", 0, 2024)


class TestAttainedCII:
    """MEPC.352(78) attained annual CII formula."""

    def test_simple_single_fuel(self):
        # bulk carrier: 8500 t HFO, 120000 nm, 75000 DWT
        fc_j = {"hfo": 8500 * 1e6}   # tonnes → grams
        capacity, dist = 75000, 120000
        result = calc_attained_cii(fc_j, dist, capacity)
        expected = (3.114 * 8500e6) / (capacity * dist)
        assert result == pytest.approx(expected, rel=1e-6)

    def test_multi_fuel(self):
        fc_j = {"hfo": 8000e6, "mdo": 200e6}
        capacity, dist = 75000, 120000
        result = calc_attained_cii(fc_j, dist, capacity)
        expected = (3.114 * 8000e6 + 3.206 * 200e6) / (capacity * dist)
        assert result == pytest.approx(expected, rel=1e-6)

    def test_voyage_adjustment_reduces_cii(self):
        fc_j = {"hfo": 8500e6}
        base = calc_attained_cii(fc_j, 120000, 75000)
        adjusted = calc_attained_cii(fc_j, 120000, 75000,
                                      fc_voyage_j={"hfo": 500e6}, dx=5000)
        assert adjusted < base

    def test_electrical_correction_reduces_numerator(self):
        fc_j = {"hfo": 8500e6}
        base = calc_attained_cii(fc_j, 120000, 75000)
        corrected = calc_attained_cii(fc_j, 120000, 75000,
                                       fc_electrical_j={"hfo": 300e6})
        assert corrected < base

    def test_yi_factor_changes_over_years(self):
        """(0.75 - 0.03*yi) decreases with year, reducing electrical deduction."""
        fc_j = {"hfo": 8500e6}
        elec = {"hfo": 500e6}
        r2023 = calc_attained_cii(fc_j, 120000, 75000, fc_electrical_j=elec, year=2023)
        r2026 = calc_attained_cii(fc_j, 120000, 75000, fc_electrical_j=elec, year=2026)
        # yi2023=0 → 0.75*elec deducted; yi2026=3 → 0.66*elec deducted → higher attained
        assert r2026 > r2023

    def test_zero_distance_raises(self):
        with pytest.raises(ValueError):
            calc_attained_cii({"hfo": 8500e6}, 0, 75000)


class TestRateCII:
    """MEPC.354(78) A–E rating boundaries."""

    def test_low_attained_is_A(self):
        # Attained well below required → A
        req = calc_required_cii("bulk_carrier", 75000, 2024)
        r = rate_cii(req * 0.3, req, "bulk_carrier")
        assert r["rating"] == "A"

    def test_high_attained_is_E(self):
        req = calc_required_cii("bulk_carrier", 75000, 2024)
        r = rate_cii(req * 2.0, req, "bulk_carrier")
        assert r["rating"] == "E"

    def test_at_required_is_C(self):
        # Exactly at required CII → C (d3 = 0, so boundary = required)
        req = calc_required_cii("bulk_carrier", 75000, 2024)
        r = rate_cii(req, req, "bulk_carrier")
        assert r["rating"] == "C"

    def test_margin_sign(self):
        req = 5.0
        r_below = rate_cii(3.0, req, "bulk_carrier")
        r_above = rate_cii(7.0, req, "bulk_carrier")
        assert r_below["margin_pct"] > 0
        assert r_above["margin_pct"] < 0

    def test_boundaries_ordered(self):
        req = calc_required_cii("tanker", 80000, 2024)
        r = rate_cii(req, req, "tanker")
        b = r["boundaries"]
        assert b["A"] < b["B"] < b["C"] < b["D"]


class TestCalculateCIIPipeline:
    """Integration tests for the full CII pipeline."""

    BASE = dict(ship_type="bulk_carrier", dwt=75000, year=2024,
                distance_nm=120000, fc_hfo=8500, fc_mdo=200)

    def test_returns_required_keys(self):
        r = calculate_cii(self.BASE)
        for key in ["attained_cii","required_cii","rating","capacity",
                    "corrections_applied","reduction_factor_pct"]:
            assert key in r

    def test_rating_is_valid(self):
        r = calculate_cii(self.BASE)
        assert r["rating"]["rating"] in ("A","B","C","D","E")

    def test_capacity_correct(self):
        r = calculate_cii(self.BASE)
        assert r["capacity"] == pytest.approx(75000)

    def test_reduction_factor_2024(self):
        r = calculate_cii(self.BASE)
        assert r["reduction_factor_pct"] == 7

    def test_no_fuel_raises(self):
        bad = {**self.BASE, "fc_hfo": 0, "fc_mdo": 0}
        with pytest.raises(ValueError, match="fuel"):
            calculate_cii(bad)

    def test_zero_distance_raises(self):
        with pytest.raises(ValueError):
            calculate_cii({**self.BASE, "distance_nm": 0})

    def test_sts_correction_applied(self):
        inp = {**self.BASE, "ship_type": "tanker", "sts_operation": True}
        r = calculate_cii(inp)
        assert any("STS" in c for c in r["corrections_applied"])

    def test_reefer_correction_applied(self):
        inp = {**self.BASE, "reefer_kwh": 500000, "sfoc_electrical": 175}
        r = calculate_cii(inp)
        assert any("Reefer" in c for c in r["corrections_applied"])

    def test_voyage_adjustment_applied(self):
        inp = {**self.BASE, "voyage_hfo": 300, "voyage_distance": 8000}
        r = calculate_cii(inp)
        assert any("Voyage" in c for c in r["corrections_applied"])

    def test_ro_ro_pass_uses_gt(self):
        inp = dict(ship_type="ro_ro_pass", gt=45000, dwt=0, year=2024,
                   distance_nm=80000, fc_hfo=3000)
        r = calculate_cii(inp)
        assert r["capacity"] == pytest.approx(45000)
