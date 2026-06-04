"""
tests/test_emissions.py
Tests for emissions module: PME, ME/AE emission terms.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from eexi.emissions import calc_pme, calc_me_emissions, calc_ae_emissions, calc_total_numerator


class TestCalcPME:
    def test_standard_75pct(self):
        assert calc_pme(12000) == pytest.approx(9000.0)

    def test_with_feff(self):
        assert calc_pme(12000, f_eff=0.95) == pytest.approx(8550.0)

    def test_zero_mcr_raises(self):
        with pytest.raises(ValueError):
            calc_pme(0)

    def test_negative_mcr_raises(self):
        with pytest.raises(ValueError):
            calc_pme(-500)

    def test_feff_out_of_range_raises(self):
        with pytest.raises(ValueError):
            calc_pme(12000, f_eff=1.5)

    def test_feff_zero_raises(self):
        with pytest.raises(ValueError):
            calc_pme(12000, f_eff=0.0)


class TestCalcMEEmissions:
    def test_bulk_carrier_example(self):
        # Phase 2 Example A: PME=9000, CF=3.114, SFC=175
        result = calc_me_emissions(9000, 3.114, 175)
        assert result == pytest.approx(9000 * 3.114 * 175, rel=1e-6)

    def test_zero_pme_returns_zero(self):
        assert calc_me_emissions(0, 3.114, 175) == 0.0

    def test_negative_pme_raises(self):
        with pytest.raises(ValueError):
            calc_me_emissions(-100, 3.114, 175)

    def test_zero_cf_raises(self):
        with pytest.raises(ValueError):
            calc_me_emissions(9000, 0, 175)

    def test_zero_sfc_raises(self):
        with pytest.raises(ValueError):
            calc_me_emissions(9000, 3.114, 0)


class TestCalcAEEmissions:
    def test_with_aux_engine(self):
        result = calc_ae_emissions(500, 3.206, 200)
        assert result == pytest.approx(500 * 3.206 * 200, rel=1e-6)

    def test_zero_pae_returns_zero(self):
        assert calc_ae_emissions(0, 3.114, 200) == 0.0

    def test_negative_pae_raises(self):
        with pytest.raises(ValueError):
            calc_ae_emissions(-100, 3.114, 200)

    def test_zero_cf_ae_raises(self):
        with pytest.raises(ValueError):
            calc_ae_emissions(500, 0, 200)

    def test_zero_sfc_ae_raises(self):
        with pytest.raises(ValueError):
            calc_ae_emissions(500, 3.114, 0)


class TestCalcTotalNumerator:
    def test_sum(self):
        assert calc_total_numerator(4904550, 321000) == pytest.approx(5225550)

    def test_zero_ae(self):
        assert calc_total_numerator(4904550, 0) == pytest.approx(4904550)
