"""
tests/test_epl.py
Tests for Engine Power Limitation calculation.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from eexi.epl import calc_epl, calc_epl_percentage


class TestCalcEPL:
    def test_example_b_general_cargo(self):
        """Phase 2 Example B: general cargo, non-compliant case."""
        req  = 107.48 * (8000 ** -0.216) * 0.95
        cap  = 8000.0
        v    = 12.5
        cf   = 3.206
        sfc  = 190.0
        res  = calc_epl(req, cap, v, cf, sfc)
        expected_pme = (req * cap * v) / (cf * sfc)
        assert res["epl_possible"] is True
        assert res["max_pme"] == pytest.approx(expected_pme, rel=1e-4)
        assert res["limited_mcr"] == pytest.approx(expected_pme / 0.75, rel=1e-4)

    def test_epl_possible_true_for_normal_case(self):
        res = calc_epl(5.0, 50000, 13.0, 3.114, 175)
        assert res["epl_possible"] is True
        assert res["max_pme"] > 0

    def test_epl_impossible_when_ae_exceeds_budget(self):
        # Extremely high AE forces max_pme negative
        res = calc_epl(
            required_eexi=1.0, capacity=1000, v_ref=5.0,
            cf_me=3.114, sfc_me=175,
            pae=99999, cf_ae=3.114, sfc_ae=500
        )
        assert res["epl_possible"] is False
        assert "insufficient" in res["note"].lower()

    def test_with_auxiliary_engine(self):
        req = 5.0; cap = 50000; v = 13.0; cf = 3.114; sfc = 175
        pae = 500; cf_ae = 3.206; sfc_ae = 200
        res = calc_epl(req, cap, v, cf, sfc, pae, cf_ae, sfc_ae)
        ae_term = pae * cf_ae * sfc_ae
        expected = (req * cap * v - ae_term) / (cf * sfc)
        assert res["max_pme"] == pytest.approx(expected, rel=1e-4)


class TestCalcEPLPercentage:
    def test_basic(self):
        assert calc_epl_percentage(9000, 12000) == pytest.approx(75.0)

    def test_full_power(self):
        assert calc_epl_percentage(12000, 12000) == pytest.approx(100.0)

    def test_zero_installed_raises(self):
        with pytest.raises(ValueError):
            calc_epl_percentage(9000, 0)
