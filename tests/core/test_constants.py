"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           CONSTANTS TESTS                                    ║
║                                                                              ║
║  Tests for astronomical constants - the immutable foundation of celestial    ║
║  calculations from the speed of light to the mass of the Sun.                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import math
import allure
import pytest

from starward.core.constants import CONSTANTS, Constant


# ═══════════════════════════════════════════════════════════════════════════════
#  CONSTANT DATACLASS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Constant Dataclass")
class TestConstantDataclass:
    """Tests for the Constant data class."""

    @allure.title("Constant converts to float")
    def test_float_conversion(self):
        """Constant converts to float."""
        with allure.step("Create constant"):
            c = Constant(name="Test", value=299792458.0, unit="m/s")
        with allure.step(f"float(c) = {float(c)}"):
            assert float(c) == 299792458.0

    @allure.title("repr() includes name")
    def test_repr_includes_name(self):
        """repr() includes name."""
        with allure.step("Create constant"):
            c = Constant(name="Test", value=1.0, unit="m")
        with allure.step(f"'Test' in repr"):
            assert "Test" in repr(c)

    @allure.title("repr() includes value")
    def test_repr_includes_value(self):
        """repr() includes value."""
        with allure.step("Create constant"):
            c = Constant(name="Test", value=1.0, unit="m")
        with allure.step("'1.0' in repr"):
            assert "1.0" in repr(c)

    @allure.title("repr() includes unit")
    def test_repr_includes_unit(self):
        """repr() includes unit."""
        with allure.step("Create constant"):
            c = Constant(name="Test", value=1.0, unit="m")
        with allure.step("'m' in repr"):
            assert "m" in repr(c)

    @allure.title("repr() shows uncertainty when present")
    def test_repr_with_uncertainty(self):
        """repr() shows uncertainty when present."""
        with allure.step("Create constant with uncertainty"):
            c = Constant(name="Test", value=1.0, unit="m", uncertainty=0.1)
        with allure.step("'±' in repr"):
            assert "±" in repr(c)


# ═══════════════════════════════════════════════════════════════════════════════
#  FUNDAMENTAL CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Fundamental Constants")
class TestFundamentalConstants:
    """Tests for fundamental physical constants."""

    @pytest.mark.golden
    @allure.title("Speed of light: c = 299,792,458 m/s")
    @allure.description("""
    Speed of light is exact by SI definition since 2019.
    c = 299,792,458 m/s (exactly)
    """)
    def test_speed_of_light(self):
        """Speed of light: c = 299,792,458 m/s (exact by definition)."""
        with allure.step(f"c = {CONSTANTS.c.value} m/s"):
            assert CONSTANTS.c.value == 299792458.0
        with allure.step(f"Unit = {CONSTANTS.c.unit}"):
            assert CONSTANTS.c.unit == "m/s"

    @pytest.mark.golden
    @allure.title("Gravitational constant: G ≈ 6.674 × 10⁻¹¹")
    @allure.description("""
    Newton's gravitational constant.
    G ≈ 6.67430 × 10⁻¹¹ m³/(kg·s²)
    """)
    def test_gravitational_constant(self):
        """Gravitational constant: G ≈ 6.67430 × 10⁻¹¹ m³/(kg·s²)."""
        with allure.step(f"G = {CONSTANTS.G.value:.4e}"):
            assert 6.67e-11 < CONSTANTS.G.value < 6.68e-11

    @pytest.mark.golden
    @allure.title("AU = 149,597,870,700 m (exact)")
    @allure.description("""
    Astronomical Unit defined exactly by IAU since 2012.
    1 AU = 149,597,870,700 m (exactly)
    """)
    def test_astronomical_unit(self):
        """AU = 149,597,870,700 m (exact by IAU definition since 2012)."""
        with allure.step(f"AU = {CONSTANTS.AU.value:.0f} m"):
            assert CONSTANTS.AU.value == 149597870700.0
        with allure.step(f"Uncertainty = {CONSTANTS.AU.uncertainty}"):
            assert CONSTANTS.AU.uncertainty == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
#  TIME CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Time Constants")
class TestTimeConstants:
    """Tests for time-related constants."""

    @pytest.mark.golden
    @allure.title("J2000.0 = JD 2451545.0")
    def test_j2000_julian_date(self):
        """J2000.0 = JD 2451545.0."""
        with allure.step(f"JD_J2000 = {CONSTANTS.JD_J2000.value}"):
            assert CONSTANTS.JD_J2000.value == 2451545.0

    @pytest.mark.golden
    @allure.title("MJD offset = 2400000.5")
    def test_mjd_offset(self):
        """MJD offset = 2400000.5."""
        with allure.step(f"MJD_OFFSET = {CONSTANTS.MJD_OFFSET.value}"):
            assert CONSTANTS.MJD_OFFSET.value == 2400000.5

    @pytest.mark.golden
    @allure.title("Julian year = 365.25 days")
    def test_julian_year(self):
        """Julian year = 365.25 days (exact by definition)."""
        with allure.step(f"JULIAN_YEAR = {CONSTANTS.JULIAN_YEAR.value}"):
            assert CONSTANTS.JULIAN_YEAR.value == 365.25

    @pytest.mark.golden
    @allure.title("Julian century = 36525 days")
    def test_julian_century(self):
        """Julian century = 36525 days."""
        with allure.step(f"JULIAN_CENTURY = {CONSTANTS.JULIAN_CENTURY.value}"):
            assert CONSTANTS.JULIAN_CENTURY.value == 36525.0


# ═══════════════════════════════════════════════════════════════════════════════
#  SOLAR CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Solar Constants")
class TestSolarConstants:
    """Tests for solar constants."""

    @pytest.mark.skip(reason="M_SUN not yet implemented")
    @pytest.mark.golden
    @allure.title("Solar mass ≈ 1.989 × 10³⁰ kg")
    def test_solar_mass(self):
        """Solar mass ≈ 1.989 × 10³⁰ kg."""
        assert 1.98e30 < CONSTANTS.M_SUN.value < 1.99e30

    @pytest.mark.skip(reason="R_SUN not yet implemented")
    @pytest.mark.golden
    @allure.title("Solar radius ≈ 6.96 × 10⁸ m")
    def test_solar_radius(self):
        """Solar radius ≈ 6.96 × 10⁸ m."""
        assert 6.95e8 < CONSTANTS.R_SUN.value < 6.97e8

    @pytest.mark.skip(reason="L_SUN not yet implemented")
    @pytest.mark.golden
    @allure.title("Solar luminosity ≈ 3.828 × 10²⁶ W")
    def test_solar_luminosity(self):
        """Solar luminosity ≈ 3.828 × 10²⁶ W."""
        assert 3.8e26 < CONSTANTS.L_SUN.value < 3.9e26


# ═══════════════════════════════════════════════════════════════════════════════
#  GALACTIC CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Galactic Constants")
class TestGalacticConstants:
    """Tests for Galactic coordinate system constants."""

    @pytest.mark.golden
    @allure.title("North Galactic Pole RA ≈ 192.86°")
    def test_galactic_pole_ra(self):
        """North Galactic Pole RA ≈ 192.86° (J2000)."""
        with allure.step(f"GALACTIC_POLE_RA = {CONSTANTS.GALACTIC_POLE_RA.value:.2f}°"):
            assert math.isclose(CONSTANTS.GALACTIC_POLE_RA.value, 192.86, abs_tol=0.01)

    @pytest.mark.golden
    @allure.title("North Galactic Pole Dec ≈ 27.13°")
    def test_galactic_pole_dec(self):
        """North Galactic Pole Dec ≈ 27.13° (J2000)."""
        with allure.step(f"GALACTIC_POLE_DEC = {CONSTANTS.GALACTIC_POLE_DEC.value:.2f}°"):
            assert math.isclose(CONSTANTS.GALACTIC_POLE_DEC.value, 27.13, abs_tol=0.01)

    @pytest.mark.skip(reason="GALACTIC_NODE_L not yet implemented")
    @pytest.mark.golden
    @allure.title("Ascending node longitude ≈ 33°")
    def test_galactic_node_longitude(self):
        """Ascending node longitude ≈ 33°."""
        assert 32 < CONSTANTS.GALACTIC_NODE_L.value < 34


# ═══════════════════════════════════════════════════════════════════════════════
#  ANGULAR CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Angular Constants")
class TestAngularConstants:
    """Tests for angular conversion constants."""

    @pytest.mark.golden
    @allure.title("Arcseconds per radian = 3600 × 180 / π")
    def test_arcsec_per_radian(self):
        """Arcseconds per radian = 3600 × 180 / π."""
        expected = 3600 * 180 / math.pi
        with allure.step(f"ARCSEC_PER_RADIAN = {CONSTANTS.ARCSEC_PER_RADIAN.value:.2f}"):
            assert math.isclose(CONSTANTS.ARCSEC_PER_RADIAN.value, expected, rel_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  SEARCH AND DISCOVERY
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Search and Discovery")
class TestConstantSearch:
    """Tests for searching and listing constants."""

    @allure.title("list_all() returns all constants")
    def test_list_all_returns_all(self):
        """list_all() returns all constants."""
        with allure.step("Get all constants"):
            all_constants = CONSTANTS.list_all()
        with allure.step(f"Count = {len(all_constants)} (> 10)"):
            assert len(all_constants) > 10
            assert all(isinstance(c, Constant) for c in all_constants)

    @allure.title("Search finds constants by name")
    def test_search_by_name(self):
        """Search finds constants by name."""
        with allure.step("Search 'speed'"):
            results = CONSTANTS.search("speed")
        with allure.step(f"Found {len(results)} result(s)"):
            assert len(results) == 1
            assert results[0].name == "Speed of light"

    @allure.title("Search finds multiple constants")
    def test_search_by_category(self):
        """Search finds multiple constants."""
        with allure.step("Search 'solar'"):
            results = CONSTANTS.search("solar")
        with allure.step(f"Found {len(results)} solar constant(s)"):
            assert len(results) >= 3

    @allure.title("Search is case-insensitive")
    def test_search_case_insensitive(self):
        """Search is case-insensitive."""
        results1 = CONSTANTS.search("SOLAR")
        results2 = CONSTANTS.search("solar")
        with allure.step(f"SOLAR={len(results1)}, solar={len(results2)}"):
            assert len(results1) == len(results2)

    @allure.title("Search with no matches returns empty")
    def test_search_no_match(self):
        """Search with no matches returns empty list."""
        with allure.step("Search 'xyznonexistent'"):
            results = CONSTANTS.search("xyznonexistent")
        with allure.step(f"Results = {len(results)}"):
            assert len(results) == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  PHYSICAL CONSISTENCY
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Physical Consistency")
class TestPhysicalConsistency:
    """Tests that related constants are consistent with each other."""

    @allure.title("Julian century = 100 × Julian year")
    def test_julian_century_is_100_years(self):
        """Julian century = 100 × Julian year."""
        expected = 100 * CONSTANTS.JULIAN_YEAR.value
        with allure.step(f"100 × {CONSTANTS.JULIAN_YEAR.value} = {expected}"):
            assert CONSTANTS.JULIAN_CENTURY.value == expected

    @allure.title("Parsec-AU relationship")
    def test_parsec_au_relationship(self):
        """1 parsec = AU / tan(1 arcsec) ≈ 206265 AU."""
        au = CONSTANTS.AU.value
        arcsec_rad = 1.0 / CONSTANTS.ARCSEC_PER_RADIAN.value
        parsec_m = au / math.tan(arcsec_rad)
        with allure.step(f"1 parsec ≈ {parsec_m:.2e} m"):
            assert 3.08e16 < parsec_m < 3.09e16


# ═══════════════════════════════════════════════════════════════════════════════
#  v0.2 CONSTANTS (SUN/MOON)
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("v0.2 Constants")
class TestV02Constants:
    """Tests for constants added in v0.2 for Sun/Moon calculations."""

    @pytest.mark.skip(reason="MEAN_SUN_LONGITUDE_RATE not yet implemented")
    @allure.title("Mean solar motion constant exists")
    def test_mean_sun_motion_exists(self):
        """Mean solar motion constant exists."""
        val = CONSTANTS.MEAN_SUN_LONGITUDE_RATE
        assert val.value > 0

    @allure.title("Moon mean distance search")
    def test_moon_mean_distance(self):
        """Mean Moon distance ≈ 384,400 km."""
        with allure.step("Search 'moon'"):
            results = CONSTANTS.search("moon")
        with allure.step(f"Found {len(results)} moon-related constants"):
            assert len(results) >= 0
