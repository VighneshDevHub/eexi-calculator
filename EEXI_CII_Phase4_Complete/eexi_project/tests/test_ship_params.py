"""
tests/test_ship_params.py
Tests for ship_params module: capacity calculation and CF lookup.
"""
import pytest
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from eexi.ship_params import get_capacity, get_cf, SHIP_PARAMS, CF_MAP


class TestGetCapacity:
    def test_bulk_carrier_returns_dwt(self):
        assert get_capacity("bulk_carrier", dwt=75000) == 75000.0

    def test_tanker_returns_dwt(self):
        assert get_capacity("tanker", dwt=50000) == 50000.0

    def test_container_returns_070_dwt(self):
        assert get_capacity("container", dwt=100000) == pytest.approx(70000.0)

    def test_ro_ro_pass_returns_gt(self):
        assert get_capacity("ro_ro_pass", dwt=0, gt=45000) == 45000.0

    def test_cruise_returns_gt(self):
        assert get_capacity("cruise", dwt=0, gt=120000) == 120000.0

    def test_lng_carrier_returns_dwt(self):
        assert get_capacity("lng_carrier", dwt=80000) == 80000.0

    def test_invalid_ship_type_raises(self):
        with pytest.raises(ValueError, match="Unknown ship type"):
            get_capacity("supertanker", dwt=50000)

    def test_zero_dwt_raises_for_bulk_carrier(self):
        with pytest.raises(ValueError):
            get_capacity("bulk_carrier", dwt=0)

    def test_zero_gt_raises_for_cruise(self):
        with pytest.raises(ValueError):
            get_capacity("cruise", dwt=0, gt=0)

    def test_all_ship_types_defined(self):
        """Every key in SHIP_PARAMS must work without error."""
        for ship_type, (_, _, _, cap_mode) in SHIP_PARAMS.items():
            if cap_mode == "gt":
                get_capacity(ship_type, dwt=0, gt=50000)
            else:
                get_capacity(ship_type, dwt=50000)


class TestGetCF:
    def test_hfo(self):
        assert get_cf("hfo") == pytest.approx(3.114)

    def test_mdo(self):
        assert get_cf("mdo") == pytest.approx(3.206)

    def test_lng(self):
        assert get_cf("lng") == pytest.approx(2.750)

    def test_methanol(self):
        assert get_cf("methanol") == pytest.approx(1.375)

    def test_lpg_propane(self):
        assert get_cf("lpg_propane") == pytest.approx(3.000)

    def test_invalid_fuel_raises(self):
        with pytest.raises(ValueError, match="Unknown fuel type"):
            get_cf("diesel")

    def test_all_fuels_defined(self):
        for fuel in CF_MAP:
            assert get_cf(fuel) > 0
