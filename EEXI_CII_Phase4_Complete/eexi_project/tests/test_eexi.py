"""
tests/test_eexi.py
Tests for EEXI attained/required calculation and compliance check.
Ground truth values from Phase 2 worked examples.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from eexi.eexi import calc_attained_eexi, calc_required_eexi, check_compliance


class TestCalcAttainedEEXI:
    def test_example_a_bulk_carrier(self):
        # Phase 2 Example A: numerator=4904550, capacity=75000, v=14.5
        numerator = 9000 * 3.114 * 175   # 4,904,550
        capacity  = 75000
        v_ref     = 14.5
        result    = calc_attained_eexi(numerator, capacity, v_ref)
        assert result == pytest.approx(numerator / (capacity * v_ref), rel=1e-6)
        assert result == pytest.approx(4.509, abs=0.001)

    def test_zero_numerator(self):
        # Theoretically valid (zero emissions)
        assert calc_attained_eexi(0, 75000, 14.5) == 0.0

    def test_zero_capacity_raises(self):
        with pytest.raises(ValueError):
            calc_attained_eexi(1000000, 0, 14.5)

    def test_zero_vref_raises(self):
        with pytest.raises(ValueError):
            calc_attained_eexi(1000000, 75000, 0)

    def test_negative_numerator_raises(self):
        with pytest.raises(ValueError):
            calc_attained_eexi(-1, 75000, 14.5)

    def test_correction_factors_applied(self):
        n = 9000 * 3.114 * 175
        base = calc_attained_eexi(n, 75000, 14.5)
        with_f = calc_attained_eexi(n, 75000, 14.5, f_i=1.0, f_w=1.0)
        assert base == pytest.approx(with_f)


class TestCalcRequiredEEXI:
    def test_bulk_carrier_75000dwt(self):
        # a=961.79, c=0.477, X=5%
        expected = 961.79 * (75000 ** -0.477) * 0.95
        assert calc_required_eexi("bulk_carrier", 75000) == pytest.approx(expected, rel=1e-6)

    def test_container_100000dwt(self):
        # a=174.22, c=0.201, X=10%
        expected = 174.22 * (100000 ** -0.201) * 0.90
        assert calc_required_eexi("container", 100000) == pytest.approx(expected, rel=1e-6)

    def test_tanker(self):
        expected = 1218.80 * (50000 ** -0.488) * 0.95
        assert calc_required_eexi("tanker", 50000) == pytest.approx(expected, rel=1e-6)

    def test_general_cargo_8000dwt(self):
        # Phase 2 Example B
        expected = 107.48 * (8000 ** -0.216) * 0.95
        assert calc_required_eexi("general_cargo", 8000) == pytest.approx(expected, rel=1e-5)

    def test_invalid_ship_type_raises(self):
        with pytest.raises(ValueError):
            calc_required_eexi("barge", 5000)

    def test_zero_dwt_raises(self):
        with pytest.raises(ValueError):
            calc_required_eexi("bulk_carrier", 0)


class TestCheckCompliance:
    def test_compliant_with_margin(self):
        result = check_compliance(attained=4.5, required=6.7)
        assert result["status"] == "COMPLIANT"
        assert result["compliant"] is True
        assert result["margin"] > 5.0

    def test_borderline(self):
        # attained just below required but within 5%
        required = 6.7
        attained = required * 0.98   # 2% margin
        result = check_compliance(attained, required)
        assert result["status"] == "BORDERLINE"
        assert result["compliant"] is True

    def test_non_compliant(self):
        result = check_compliance(attained=8.5, required=6.7)
        assert result["status"] == "NON_COMPLIANT"
        assert result["compliant"] is False
        assert result["margin"] < 0

    def test_margin_sign_convention(self):
        # Positive margin = headroom (attained < required)
        r = check_compliance(4.0, 6.0)
        assert r["margin"] > 0
        # Negative margin = excess (attained > required)
        r2 = check_compliance(7.0, 6.0)
        assert r2["margin"] < 0
