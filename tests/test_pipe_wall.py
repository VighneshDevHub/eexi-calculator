"""
Test suite for pipe wall thickness calculator.
"""
import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from calculators.pipe_wall import (
    get_allowable_stress, y_coefficient, find_adequate_schedules,
    calculate_pipe_wall, NPS_DEXT_MM, WELD_E, THREAD_DEPTH_MM
)


class TestGetAllowableStress:
    def test_a106b_at_260c(self):
        """Test allowable stress at 260°C."""
        s = get_allowable_stress("A106B", 260.0)
        assert 119.0 < s <= 137.9

    def test_invalid_material_raises(self):
        with pytest.raises(ValueError, match="not in database"):
            get_allowable_stress("XYZ999", 100.0)

    def test_all_materials_return_positive(self):
        from calculators.pipe_wall import MATERIAL_STRESS
        for mat in MATERIAL_STRESS:
            s = get_allowable_stress(mat, 100.0)
            assert s > 0, f"{mat} returned non-positive stress"

    def test_stress_decreases_at_high_temp(self):
        s_low = get_allowable_stress("A106B", 100.0)
        s_high = get_allowable_stress("A106B", 400.0)
        assert s_low > s_high


class TestYCoefficient:
    def test_below_482_is_04(self):
        assert y_coefficient(200.0) == pytest.approx(0.4)
        assert y_coefficient(482.0) == pytest.approx(0.4)

    def test_at_510_is_05_ferritic(self):
        assert y_coefficient(510.0, "ferritic") == pytest.approx(0.5)

    def test_austenitic_below_566_stays_04(self):
        assert y_coefficient(500.0, "austenitic") == pytest.approx(0.4)


class TestFindAdequateSchedules:
    def test_nps2_returns_all_schedules(self):
        scheds = find_adequate_schedules(2.0, 0.0)
        assert len(scheds) > 3

    def test_small_tmin_all_adequate(self):
        scheds = find_adequate_schedules(2.0, 0.5)
        assert all(s["adequate"] for s in scheds)

    def test_large_tmin_none_adequate(self):
        scheds = find_adequate_schedules(2.0, 999.0)
        assert not any(s["adequate"] for s in scheds)

    def test_sch80_nps2_is_554mm(self):
        scheds = find_adequate_schedules(2.0, 0.0)
        sch80 = next(s for s in scheds if s["schedule"] == "80")
        assert sch80["thickness_mm"] == pytest.approx(5.54)


class TestCalculatePipeWall:
    EXAMPLE = dict(
        nps=2.0, pressure_mpa=1.034, temp_c=260.0,
        material="A53B", weld_type="S",
        corrosion_mm=1.5875, threaded=True
    )

    def test_basic_calculation(self):
        result = calculate_pipe_wall(self.EXAMPLE)
        assert "t_dis_mm" in result
        assert "t_req_mm" in result
        assert "t_min_mm" in result
        assert result["t_min_mm"] > 0

    def test_no_thread_td_is_zero(self):
        data = {**self.EXAMPLE, "threaded": False}
        result = calculate_pipe_wall(data)
        assert result["TD_mm"] == pytest.approx(0.0)

    def test_with_thread_adds_td(self):
        data = {**self.EXAMPLE, "threaded": True}
        result = calculate_pipe_wall(data)
        assert result["TD_mm"] > 0

    def test_fbw_weld_lower_e(self):
        data_s = {**self.EXAMPLE, "weld_type": "S"}
        data_fbw = {**self.EXAMPLE, "weld_type": "FBW"}
        r_s = calculate_pipe_wall(data_s)
        r_fbw = calculate_pipe_wall(data_fbw)
        assert r_fbw["t_dis_mm"] > r_s["t_dis_mm"]

    def test_higher_pressure_thicker_wall(self):
        data_low = {**self.EXAMPLE, "pressure_mpa": 1.0}
        data_high = {**self.EXAMPLE, "pressure_mpa": 5.0}
        r_low = calculate_pipe_wall(data_low)
        r_high = calculate_pipe_wall(data_high)
        assert r_high["t_dis_mm"] > r_low["t_dis_mm"]


class TestFlaskApp:
    """Integration tests for the Flask application routes."""

    def setup_method(self):
        from app import app
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_pipe_page_loads(self):
        """Test that the pipe wall calculator page loads successfully."""
        resp = self.client.get("/pipe")
        assert resp.status_code == 200
        assert b"Pipe Wall Thickness" in resp.data

    def test_valid_calculate_pipe_request(self):
        """Test a valid pipe wall thickness calculation request."""
        resp = self.client.post("/calculate-pipe", json=TestCalculatePipeWall.EXAMPLE)
        assert resp.status_code == 200
        data = resp.get_json()
        assert "t_min_mm" in data
        assert data["t_min_mm"] > 0

    def test_missing_field_returns_error(self):
        """Test that missing required fields return an error."""
        resp = self.client.post("/calculate-pipe", json={"nps": 2.0})
        assert resp.status_code in (400, 500)
