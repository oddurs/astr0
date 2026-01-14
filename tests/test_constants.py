"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           CONSTANTS TESTS                                    ║
║                                                                              ║
║  Tests for astronomical and physical constants.                              ║
║                                                                              ║
║  Accurate constants are the foundation of astronomical calculations.         ║
║  These values come from authoritative sources:                               ║
║                                                                              ║
║  • IAU (International Astronomical Union) - astronomical definitions         ║
║  • IERS (International Earth Rotation Service) - Earth parameters            ║
║  • CODATA - fundamental physical constants                                   ║
║  • SI system - exact definitions (speed of light, etc.)                      ║
║                                                                              ║
║  Some constants are exact by definition (e.g., speed of light, AU),          ║
║  while others have measurement uncertainties that propagate through          ║
║  calculations and must be tracked for precision work.                        ║
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
class TestConstant:
    """
    Tests for the Constant dataclass structure.

    The Constant class encapsulates a physical constant with:
    - name: Human-readable identifier
    - value: Numeric value
    - unit: Physical units (SI where possible)
    - uncertainty: Measurement uncertainty (0 for exact values)

    This structure ensures constants are self-documenting and that
    uncertainties are available for error propagation calculations.
    """

    @allure.title("Constant converts to float")
    def test_float_conversion(self):
        """
        Verify that Constant objects can be used as floats in calculations.

        The __float__ method enables direct use in mathematical expressions
        without explicit .value access, improving code readability.
        """
        with allure.step("Create Constant(name='Test', value=299792458.0, unit='m/s')"):
            c = Constant(name="Test", value=299792458.0, unit="m/s")
        with allure.step(f"float(c) = {float(c)}"):
            assert float(c) == 299792458.0

    @allure.title("repr includes name, value, and unit")
    def test_repr(self):
        """
        Verify that repr() provides complete constant information.

        A good repr() helps with debugging and interactive exploration,
        showing all relevant attributes at a glance.
        """
        with allure.step("Create Constant(name='Test', value=1.0, unit='m')"):
            c = Constant(name="Test", value=1.0, unit="m")
        with allure.step(f"repr(c) = {repr(c)}"):
            assert "Test" in repr(c)
            assert "1.0" in repr(c)
            assert "m" in repr(c)

    @allure.title("repr includes ± when uncertainty present")
    def test_repr_with_uncertainty(self):
        """
        Verify that uncertainty is displayed in repr() when present.

        Displaying uncertainty reminds users that measured constants
        have limited precision, unlike exact definitions.
        """
        with allure.step("Create Constant with uncertainty=0.1"):
            c = Constant(name="Test", value=1.0, unit="m", uncertainty=0.1)
        with allure.step(f"repr contains '±'"):
            assert "±" in repr(c)


# ═══════════════════════════════════════════════════════════════════════════════
#  ASTRONOMICAL CONSTANTS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Astronomical Constants")
class TestAstronomicalConstants:
    """
    Tests for the built-in astronomical constants.

    These tests verify that fundamental constants have correct values.
    Many are exact by definition (SI or IAU), while others are the
    current best measurements with associated uncertainties.

    Key constants include:
    - Speed of light (c): Exact, defines the meter
    - Astronomical Unit (AU): Exact since 2012 IAU resolution
    - Gravitational constant (G): Measured, has uncertainty
    - Julian Date epochs: Defined for timekeeping
    """

    @allure.title("Speed of light: c = 299,792,458 m/s")
    def test_speed_of_light(self):
        """
        Verify the speed of light in vacuum.

        Since 1983, the meter is defined as the distance light travels
        in 1/299,792,458 seconds, making c exactly 299,792,458 m/s.
        This is the cosmic speed limit and a fundamental constant.
        """
        with allure.step(f"c = {CONSTANTS.c.value} {CONSTANTS.c.unit}"):
            assert CONSTANTS.c.value == 299792458.0
            assert CONSTANTS.c.unit == "m/s"

    @allure.title("AU = 149,597,870,700 m (exact)")
    def test_au_exact(self):
        """
        Verify the Astronomical Unit value.

        The AU was redefined by the IAU in 2012 as exactly
        149,597,870,700 meters. Previously it was defined as the
        mean Earth-Sun distance, which varies slightly.
        """
        with allure.step(f"AU = {CONSTANTS.AU.value:.0f} m"):
            assert CONSTANTS.AU.value == 149597870700.0
        with allure.step(f"Uncertainty = {CONSTANTS.AU.uncertainty}"):
            # Exact by definition, no uncertainty
            assert CONSTANTS.AU.uncertainty == 0.0

    @allure.title("J2000.0 = JD 2451545.0")
    def test_j2000_jd(self):
        """
        Verify the J2000.0 epoch Julian Date.

        J2000.0 (January 1, 2000, 12:00:00 TT) is the standard epoch
        for modern astronomical catalogs and ephemerides. The corresponding
        Julian Date is exactly 2451545.0.
        """
        with allure.step(f"JD_J2000 = {CONSTANTS.JD_J2000.value}"):
            assert CONSTANTS.JD_J2000.value == 2451545.0

    @allure.title("MJD offset = 2400000.5")
    def test_mjd_offset(self):
        """
        Verify the Modified Julian Date offset.

        MJD = JD - 2400000.5, chosen so that days begin at midnight
        instead of noon, and to reduce the number of digits needed.
        MJD 0 corresponds to November 17, 1858.
        """
        with allure.step(f"MJD_OFFSET = {CONSTANTS.MJD_OFFSET.value}"):
            assert CONSTANTS.MJD_OFFSET.value == 2400000.5

    @allure.title("Julian century = 36525 days")
    def test_julian_century(self):
        """
        Verify the Julian century length.

        A Julian century is exactly 36525 days (100 Julian years of
        365.25 days each). This is used in precession calculations
        and for expressing rates of change in astronomical quantities.
        """
        with allure.step(f"JULIAN_CENTURY = {CONSTANTS.JULIAN_CENTURY.value}"):
            assert CONSTANTS.JULIAN_CENTURY.value == 36525.0

    @allure.title("list_all() returns > 10 constants")
    def test_list_all(self):
        """
        Verify that a comprehensive set of constants is available.

        The library should provide all commonly-used astronomical
        constants in a single, authoritative location.
        """
        with allure.step("Get all constants"):
            all_constants = CONSTANTS.list_all()
        with allure.step(f"Count = {len(all_constants)}"):
            assert len(all_constants) > 10
            assert all(isinstance(c, Constant) for c in all_constants)

    @allure.title("Search 'speed' finds Speed of light")
    def test_search_speed(self):
        """
        Verify search functionality finds constants by keyword.

        Search enables discovery of constants without knowing
        exact names, supporting exploratory use.
        """
        with allure.step("Search for 'speed'"):
            results = CONSTANTS.search("speed")
        with allure.step(f"Found {len(results)} result(s)"):
            assert len(results) == 1
            assert results[0].name == "Speed of light"

    @allure.title("Search 'solar' finds ≥3 constants")
    def test_search_solar(self):
        """
        Verify search returns multiple matches for broad terms.

        "Solar" should match solar mass, radius, luminosity, and
        potentially other Sun-related constants.
        """
        with allure.step("Search for 'solar'"):
            results = CONSTANTS.search("solar")
        with allure.step(f"Found {len(results)} solar constant(s)"):
            # Should find mass, radius, luminosity at minimum
            assert len(results) >= 3

    @allure.title("Search is case insensitive")
    def test_search_case_insensitive(self):
        """
        Verify that search is case-insensitive for user convenience.

        Users shouldn't need to remember exact capitalization.
        """
        with allure.step("Search 'SOLAR' vs 'solar'"):
            results1 = CONSTANTS.search("SOLAR")
            results2 = CONSTANTS.search("solar")
        with allure.step(f"SOLAR={len(results1)}, solar={len(results2)}"):
            assert len(results1) == len(results2)

    @allure.title("Galactic pole coordinates are correct")
    def test_galactic_pole_values(self):
        """
        Verify North Galactic Pole coordinates.

        The NGP is at RA = 192.86° (12h51m), Dec = +27.13° (J2000),
        as defined by the IAU. These coordinates define the orientation
        of the Galactic coordinate system relative to ICRS.
        """
        with allure.step(f"GALACTIC_POLE_RA = {CONSTANTS.GALACTIC_POLE_RA.value:.2f}°"):
            assert abs(CONSTANTS.GALACTIC_POLE_RA.value - 192.86) < 0.01
        with allure.step(f"GALACTIC_POLE_DEC = {CONSTANTS.GALACTIC_POLE_DEC.value:.2f}°"):
            assert abs(CONSTANTS.GALACTIC_POLE_DEC.value - 27.13) < 0.01


# ═══════════════════════════════════════════════════════════════════════════════
#  PHYSICAL CONSISTENCY
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Physical Consistency")
class TestPhysicalConsistency:
    """
    Tests verifying that related constants are internally consistent.

    Physical constants are not independent - they're related by
    physical laws and definitions. These tests verify that our
    constant values maintain these relationships, catching any
    transcription errors or inconsistencies.
    """

    @allure.title("Julian year = 365.25 days")
    def test_julian_year_days(self):
        """
        Verify the Julian year length.

        The Julian year is exactly 365.25 days by definition, the
        average length of a year in the Julian calendar. This value
        is used in astronomical timekeeping despite not matching
        the actual tropical or sidereal year.
        """
        with allure.step(f"JULIAN_YEAR = {CONSTANTS.JULIAN_YEAR.value}"):
            assert CONSTANTS.JULIAN_YEAR.value == 365.25

    @allure.title("Julian century = 100 × Julian year")
    def test_julian_century_is_100_years(self):
        """
        Verify consistency between Julian year and century.

        A Julian century must be exactly 100 Julian years.
        This relationship test catches any inconsistencies in
        our constant definitions.
        """
        with allure.step(f"100 × {CONSTANTS.JULIAN_YEAR.value} = {100 * CONSTANTS.JULIAN_YEAR.value}"):
            pass
        with allure.step(f"JULIAN_CENTURY = {CONSTANTS.JULIAN_CENTURY.value}"):
            assert CONSTANTS.JULIAN_CENTURY.value == 100 * CONSTANTS.JULIAN_YEAR.value

    @allure.title("Arcseconds per radian = 3600 × 180 / π")
    def test_arcsec_per_radian(self):
        """
        Verify the arcseconds per radian conversion factor.

        This is a derived constant: 1 radian = 180/π degrees,
        and 1 degree = 3600 arcseconds, so:
        1 radian = 3600 × 180 / π ≈ 206,264.8 arcseconds

        This value is used extensively in small-angle calculations.
        """
        expected = 3600 * 180 / math.pi
        with allure.step(f"Expected: {expected:.2f}"):
            pass
        with allure.step(f"ARCSEC_PER_RADIAN = {CONSTANTS.ARCSEC_PER_RADIAN.value:.2f}"):
            assert abs(CONSTANTS.ARCSEC_PER_RADIAN.value - expected) < 1e-6
