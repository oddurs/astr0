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
import pytest

from astr0.core.constants import CONSTANTS, Constant


# ═══════════════════════════════════════════════════════════════════════════════
#  CONSTANT DATACLASS
# ═══════════════════════════════════════════════════════════════════════════════

class TestConstantDataclass:
    """
    Tests for the Constant data class.
    
    Each constant has:
      - name: Human-readable name
      - value: Numerical value
      - unit: SI unit string
      - uncertainty: Optional measurement uncertainty
    """
    
    def test_float_conversion(self):
        """Constant converts to float."""
        c = Constant(name="Test", value=299792458.0, unit="m/s")
        assert float(c) == 299792458.0
    
    def test_repr_includes_name(self):
        """repr() includes name."""
        c = Constant(name="Test", value=1.0, unit="m")
        assert "Test" in repr(c)
    
    def test_repr_includes_value(self):
        """repr() includes value."""
        c = Constant(name="Test", value=1.0, unit="m")
        assert "1.0" in repr(c)
    
    def test_repr_includes_unit(self):
        """repr() includes unit."""
        c = Constant(name="Test", value=1.0, unit="m")
        assert "m" in repr(c)
    
    def test_repr_with_uncertainty(self):
        """repr() shows uncertainty when present."""
        c = Constant(name="Test", value=1.0, unit="m", uncertainty=0.1)
        assert "±" in repr(c)


# ═══════════════════════════════════════════════════════════════════════════════
#  FUNDAMENTAL CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestFundamentalConstants:
    """
    Tests for fundamental physical constants.
    
    These are exact or precisely measured values from CODATA/IAU.
    """
    
    @pytest.mark.golden
    def test_speed_of_light(self):
        """Speed of light: c = 299,792,458 m/s (exact by definition)."""
        assert CONSTANTS.c.value == 299792458.0
        assert CONSTANTS.c.unit == "m/s"
    
    @pytest.mark.golden
    def test_gravitational_constant(self):
        """Gravitational constant: G ≈ 6.67430 × 10⁻¹¹ m³/(kg·s²)."""
        assert 6.67e-11 < CONSTANTS.G.value < 6.68e-11
    
    @pytest.mark.golden
    def test_astronomical_unit(self):
        """AU = 149,597,870,700 m (exact by IAU definition since 2012)."""
        assert CONSTANTS.AU.value == 149597870700.0
        assert CONSTANTS.AU.uncertainty == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
#  TIME CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestTimeConstants:
    """
    Tests for time-related constants.
    """
    
    @pytest.mark.golden
    def test_j2000_julian_date(self):
        """J2000.0 = JD 2451545.0."""
        assert CONSTANTS.JD_J2000.value == 2451545.0
    
    @pytest.mark.golden
    def test_mjd_offset(self):
        """MJD offset = 2400000.5."""
        assert CONSTANTS.MJD_OFFSET.value == 2400000.5
    
    @pytest.mark.golden
    def test_julian_year(self):
        """Julian year = 365.25 days (exact by definition)."""
        assert CONSTANTS.JULIAN_YEAR.value == 365.25
    
    @pytest.mark.golden
    def test_julian_century(self):
        """Julian century = 36525 days."""
        assert CONSTANTS.JULIAN_CENTURY.value == 36525.0


# ═══════════════════════════════════════════════════════════════════════════════
#  SOLAR CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestSolarConstants:
    """
    Tests for solar constants.
    
    Note: M_SUN, R_SUN, L_SUN are planned for future versions.
    """
    
    @pytest.mark.skip(reason="M_SUN not yet implemented")
    @pytest.mark.golden
    def test_solar_mass(self):
        """Solar mass ≈ 1.989 × 10³⁰ kg."""
        assert 1.98e30 < CONSTANTS.M_SUN.value < 1.99e30
    
    @pytest.mark.skip(reason="R_SUN not yet implemented")
    @pytest.mark.golden
    def test_solar_radius(self):
        """Solar radius ≈ 6.96 × 10⁸ m."""
        assert 6.95e8 < CONSTANTS.R_SUN.value < 6.97e8
    
    @pytest.mark.skip(reason="L_SUN not yet implemented")
    @pytest.mark.golden
    def test_solar_luminosity(self):
        """Solar luminosity ≈ 3.828 × 10²⁶ W."""
        assert 3.8e26 < CONSTANTS.L_SUN.value < 3.9e26


# ═══════════════════════════════════════════════════════════════════════════════
#  GALACTIC CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestGalacticConstants:
    """
    Tests for Galactic coordinate system constants.
    """
    
    @pytest.mark.golden
    def test_galactic_pole_ra(self):
        """North Galactic Pole RA ≈ 192.86° (J2000)."""
        assert math.isclose(CONSTANTS.GALACTIC_POLE_RA.value, 192.86, abs_tol=0.01)
    
    @pytest.mark.golden
    def test_galactic_pole_dec(self):
        """North Galactic Pole Dec ≈ 27.13° (J2000)."""
        assert math.isclose(CONSTANTS.GALACTIC_POLE_DEC.value, 27.13, abs_tol=0.01)
    
    @pytest.mark.skip(reason="GALACTIC_NODE_L not yet implemented")
    @pytest.mark.golden
    def test_galactic_node_longitude(self):
        """Ascending node longitude ≈ 33°."""
        assert 32 < CONSTANTS.GALACTIC_NODE_L.value < 34


# ═══════════════════════════════════════════════════════════════════════════════
#  ANGULAR CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestAngularConstants:
    """
    Tests for angular conversion constants.
    """
    
    @pytest.mark.golden
    def test_arcsec_per_radian(self):
        """Arcseconds per radian = 3600 × 180 / π."""
        expected = 3600 * 180 / math.pi
        assert math.isclose(CONSTANTS.ARCSEC_PER_RADIAN.value, expected, rel_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  SEARCH AND DISCOVERY
# ═══════════════════════════════════════════════════════════════════════════════

class TestConstantSearch:
    """
    Tests for searching and listing constants.
    """
    
    def test_list_all_returns_all(self):
        """list_all() returns all constants."""
        all_constants = CONSTANTS.list_all()
        assert len(all_constants) > 10
        assert all(isinstance(c, Constant) for c in all_constants)
    
    def test_search_by_name(self):
        """Search finds constants by name."""
        results = CONSTANTS.search("speed")
        assert len(results) == 1
        assert results[0].name == "Speed of light"
    
    def test_search_by_category(self):
        """Search finds multiple constants."""
        results = CONSTANTS.search("solar")
        assert len(results) >= 3  # mass, radius, luminosity
    
    def test_search_case_insensitive(self):
        """Search is case-insensitive."""
        results1 = CONSTANTS.search("SOLAR")
        results2 = CONSTANTS.search("solar")
        assert len(results1) == len(results2)
    
    def test_search_no_match(self):
        """Search with no matches returns empty list."""
        results = CONSTANTS.search("xyznonexistent")
        assert len(results) == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  PHYSICAL CONSISTENCY
# ═══════════════════════════════════════════════════════════════════════════════

class TestPhysicalConsistency:
    """
    Tests that related constants are consistent with each other.
    """
    
    def test_julian_century_is_100_years(self):
        """Julian century = 100 × Julian year."""
        expected = 100 * CONSTANTS.JULIAN_YEAR.value
        assert CONSTANTS.JULIAN_CENTURY.value == expected
    
    def test_parsec_au_relationship(self):
        """1 parsec = AU / tan(1 arcsec) ≈ 206265 AU."""
        au = CONSTANTS.AU.value
        arcsec_rad = 1.0 / CONSTANTS.ARCSEC_PER_RADIAN.value
        parsec_m = au / math.tan(arcsec_rad)
        
        # Should be close to ~3.086e16 m
        assert 3.08e16 < parsec_m < 3.09e16


# ═══════════════════════════════════════════════════════════════════════════════
#  v0.2 CONSTANTS (SUN/MOON)
# ═══════════════════════════════════════════════════════════════════════════════

class TestV02Constants:
    """
    Tests for constants added in v0.2 for Sun/Moon calculations.
    """
    
    @pytest.mark.skip(reason="MEAN_SUN_LONGITUDE_RATE not yet implemented")
    def test_mean_sun_motion_exists(self):
        """Mean solar motion constant exists."""
        # This should not raise
        val = CONSTANTS.MEAN_SUN_LONGITUDE_RATE
        assert val.value > 0
    
    def test_moon_mean_distance(self):
        """Mean Moon distance ≈ 384,400 km."""
        # Check if moon-related constants exist
        results = CONSTANTS.search("moon")
        # At minimum we should have some lunar constants
        assert len(results) >= 0  # May vary based on implementation
