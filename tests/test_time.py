"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              TIME TESTS                                      ║
║                                                                              ║
║  Tests for astronomical time systems and conversions.                        ║
║                                                                              ║
║  Time in astronomy is more complex than civil time:                          ║
║                                                                              ║
║  • Julian Date (JD): Continuous day count since noon on Jan 1, 4713 BCE      ║
║    - Avoids calendar irregularities (leap years, month lengths)              ║
║    - Standard for ephemeris calculations                                     ║
║    - J2000.0 (JD 2451545.0) is the modern reference epoch                    ║
║                                                                              ║
║  • Modified Julian Date (MJD): JD - 2400000.5                                ║
║    - Days begin at midnight instead of noon                                  ║
║    - Fewer digits needed (more practical for computers)                      ║
║                                                                              ║
║  • Sidereal Time: Based on Earth's rotation relative to stars                ║
║    - GMST: Greenwich Mean Sidereal Time                                      ║
║    - LST: Local Sidereal Time (GMST + longitude correction)                  ║
║    - A sidereal day is ~23h 56m 4s (Earth rotates 360° relative to stars)    ║
║                                                                              ║
║  Accurate time handling is essential because celestial positions change      ║
║  with time due to Earth's rotation, precession, and proper motion.           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
import allure
import pytest

from starward.core.time import (
    JulianDate, jd_now, utc_to_jd, jd_to_utc,
    mjd_to_jd, jd_to_mjd
)
from starward.core.constants import CONSTANTS
from starward.verbose import VerboseContext


# ═══════════════════════════════════════════════════════════════════════════════
#  JULIAN DATE CREATION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("JulianDate Creation")
class TestJulianDateCreation:
    """
    Tests for JulianDate instantiation from various sources.

    The JulianDate class can be created from:
    - Direct JD value (for astronomical calculations)
    - MJD value (common in satellite tracking)
    - Python datetime (for converting civil time)
    - Calendar components (year, month, day, etc.)

    All methods must produce consistent results.
    """

    @allure.title("Create JulianDate directly")
    def test_direct_creation(self):
        """
        Verify direct JulianDate creation from a JD value.

        This is the most basic constructor, used when the JD
        value is already known from astronomical sources.
        """
        with allure.step("Create JulianDate(2451545.0)"):
            jd = JulianDate(2451545.0)
        with allure.step(f"JD = {jd.jd}"):
            assert jd.jd == 2451545.0

    @allure.title("J2000() returns JD 2451545.0")
    def test_j2000(self):
        """
        Verify the J2000.0 epoch factory method.

        J2000.0 (January 1, 2000, 12:00:00 TT) is the standard epoch
        for modern astronomy. Star catalogs and ephemerides use this
        as their reference point.
        """
        with allure.step("Call JulianDate.j2000()"):
            jd = JulianDate.j2000()
        with allure.step(f"JD = {jd.jd}"):
            assert jd.jd == 2451545.0

    @allure.title("from_mjd() converts correctly")
    def test_from_mjd(self):
        """
        Verify creation from Modified Julian Date.

        MJD = JD - 2400000.5, so MJD 51544.5 corresponds to J2000.0.
        MJD is commonly used in spacecraft operations and GPS.
        """
        with allure.step("Create JulianDate.from_mjd(51544.5)"):
            jd = JulianDate.from_mjd(51544.5)
        with allure.step(f"JD = {jd.jd}"):
            assert math.isclose(jd.jd, 2451545.0, rel_tol=1e-10)

    @allure.title("from_datetime() for J2000.0")
    def test_from_datetime_j2000(self):
        """
        Verify creation from Python datetime for J2000.0.

        J2000.0 is 2000-01-01 12:00:00 UTC (or more precisely, TT).
        This tests the datetime-to-JD conversion algorithm.
        """
        with allure.step("Create datetime(2000, 1, 1, 12, 0, 0, UTC)"):
            dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        with allure.step("Convert to JulianDate"):
            jd = JulianDate.from_datetime(dt)
        with allure.step(f"JD = {jd.jd}"):
            assert math.isclose(jd.jd, 2451545.0, rel_tol=1e-10)

    @allure.title("from_calendar() for J2000.0")
    def test_from_calendar(self):
        """
        Verify creation from calendar components.

        Calendar conversion uses the standard astronomical algorithm
        handling the Gregorian calendar correctly.
        """
        with allure.step("Create JulianDate.from_calendar(2000, 1, 1, 12, 0, 0)"):
            jd = JulianDate.from_calendar(2000, 1, 1, 12, 0, 0)
        with allure.step(f"JD = {jd.jd}"):
            assert math.isclose(jd.jd, 2451545.0, rel_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  KNOWN JULIAN DATE VALUES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Known Julian Date Values")
class TestJulianDateKnownValues:
    """
    Tests against reference JD values from authoritative sources.

    These values come from the US Naval Observatory and other
    authoritative astronomical institutions. They serve as
    ground truth for our conversion algorithms.
    """

    KNOWN_VALUES = [
        # (year, month, day, hour, minute, second, expected_jd)
        (2000, 1, 1, 12, 0, 0, 2451545.0),    # J2000.0 epoch
        (1858, 11, 17, 0, 0, 0, 2400000.5),   # MJD epoch (MJD = 0)
        (2024, 1, 1, 0, 0, 0, 2460310.5),     # Recent date
        (1999, 12, 31, 0, 0, 0, 2451543.5),   # Day before J2000.0
        (2100, 1, 1, 0, 0, 0, 2488069.5),     # Future date
    ]

    @allure.title("Known JD values from USNO")
    @pytest.mark.parametrize("y,m,d,h,mi,s,expected", KNOWN_VALUES)
    def test_known_jd(self, y, m, d, h, mi, s, expected):
        """
        Verify JD calculation against authoritative reference values.

        Each test case represents a well-documented date with known JD,
        ensuring our algorithm matches established standards.
        """
        with allure.step(f"Create JD for {y}-{m:02d}-{d:02d} {h:02d}:{mi:02d}:{s:02d}"):
            jd = JulianDate.from_calendar(y, m, d, h, mi, s)
        with allure.step(f"JD = {jd.jd} (expected {expected})"):
            assert math.isclose(jd.jd, expected, rel_tol=1e-9)


# ═══════════════════════════════════════════════════════════════════════════════
#  DATETIME ROUNDTRIP
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Datetime Roundtrip")
class TestJulianDateRoundtrip:
    """
    Tests for datetime → JD → datetime conversion accuracy.

    Roundtrip tests verify that conversions preserve precision.
    Any loss of precision in one direction should be revealed
    when converting back.
    """

    @allure.title("Roundtrip: J2000.0 datetime")
    def test_roundtrip_j2000(self):
        """
        Verify roundtrip conversion for J2000.0.

        The reference epoch should convert with microsecond precision
        or better.
        """
        with allure.step("Create datetime(2000, 1, 1, 12, 0, 0, UTC)"):
            original = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        with allure.step("Convert to JD"):
            jd = JulianDate.from_datetime(original)
        with allure.step("Convert back to datetime"):
            result = jd.to_datetime()
        with allure.step(f"Delta = {abs((result - original).total_seconds())}s"):
            delta = abs((result - original).total_seconds())
            assert delta < 1e-6

    @allure.title("Roundtrip: arbitrary datetime with microseconds")
    def test_roundtrip_arbitrary_date(self):
        """
        Verify roundtrip conversion preserves microsecond precision.

        This tests a random date/time with full sub-second precision.
        """
        with allure.step("Create datetime(2024, 6, 15, 14, 30, 45, 123456, UTC)"):
            original = datetime(2024, 6, 15, 14, 30, 45, 123456, tzinfo=timezone.utc)
        with allure.step("Convert to JD"):
            jd = JulianDate.from_datetime(original)
        with allure.step("Convert back to datetime"):
            result = jd.to_datetime()
        with allure.step(f"Delta = {abs((result - original).total_seconds())}s"):
            delta = abs((result - original).total_seconds())
            assert delta < 1e-5  # Microsecond-level precision

    @allure.title("Roundtrip: JD → datetime → JD")
    def test_roundtrip_jd_to_datetime_to_jd(self):
        """
        Verify roundtrip in the opposite direction (JD → datetime → JD).

        Both directions should preserve precision equally well.
        """
        original_jd = 2460000.123456
        with allure.step(f"Create JulianDate({original_jd})"):
            jd = JulianDate(original_jd)
        with allure.step("Convert to datetime"):
            dt = jd.to_datetime()
        with allure.step("Convert back to JD"):
            back = JulianDate.from_datetime(dt)
        with allure.step(f"Original = {original_jd}, Back = {back.jd}"):
            assert math.isclose(back.jd, original_jd, rel_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  MJD CONVERSIONS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("MJD Conversions")
class TestMJDConversions:
    """
    Tests for Modified Julian Date conversions.

    MJD = JD - 2400000.5 offers two advantages:
    1. Days begin at midnight (civil convention) instead of noon
    2. Smaller numbers (5 digits instead of 7 for current dates)

    MJD is widely used in spacecraft operations and timekeeping.
    """

    @allure.title("mjd property returns correct value")
    def test_mjd_property(self):
        """
        Verify the MJD property calculation.

        JD 2451545.0 (J2000.0) corresponds to MJD 51544.5.
        """
        with allure.step("Create JulianDate(2451545.0)"):
            jd = JulianDate(2451545.0)
        with allure.step(f"MJD = {jd.mjd}"):
            assert math.isclose(jd.mjd, 51544.5, rel_tol=1e-10)

    @allure.title("mjd_to_jd() converts correctly")
    def test_mjd_to_jd_function(self):
        """
        Verify MJD to JD conversion function.
        """
        with allure.step("Call mjd_to_jd(51544.5)"):
            result = mjd_to_jd(51544.5)
        with allure.step(f"Result = {result}"):
            assert math.isclose(result, 2451545.0, rel_tol=1e-10)

    @allure.title("jd_to_mjd() converts correctly")
    def test_jd_to_mjd_function(self):
        """
        Verify JD to MJD conversion function.
        """
        with allure.step("Call jd_to_mjd(2451545.0)"):
            result = jd_to_mjd(2451545.0)
        with allure.step(f"Result = {result}"):
            assert math.isclose(result, 51544.5, rel_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  JULIAN CENTURIES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Julian Centuries")
class TestJulianCenturies:
    """
    Tests for Julian centuries since J2000.0.

    Many astronomical formulas express time as Julian centuries (T)
    since J2000.0:

    T = (JD - 2451545.0) / 36525.0

    This normalized time scale is used in precession calculations,
    planetary ephemerides, and coordinate transformations.
    """

    @allure.title("t_j2000 = 0 at J2000.0")
    def test_t_j2000_at_j2000(self):
        """
        Verify that T = 0 exactly at the J2000.0 epoch.

        This is the definition of the time scale - J2000.0 is the origin.
        """
        with allure.step("Create JulianDate.j2000()"):
            jd = JulianDate.j2000()
        with allure.step(f"t_j2000 = {jd.t_j2000}"):
            assert math.isclose(jd.t_j2000, 0.0, abs_tol=1e-10)

    @allure.title("t_j2000 = 1.0 at J2100.0")
    def test_t_j2000_one_century_later(self):
        """
        Verify that T = 1.0 exactly one Julian century after J2000.0.

        J2000.0 + 36525 days = J2100.0, giving T = 1.0.
        """
        with allure.step("Create JD at J2000.0 + 36525 days"):
            jd = JulianDate(2451545.0 + 36525.0)
        with allure.step(f"t_j2000 = {jd.t_j2000}"):
            assert math.isclose(jd.t_j2000, 1.0, rel_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  GREENWICH MEAN SIDEREAL TIME
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Greenwich Mean Sidereal Time")
class TestGMST:
    """
    Tests for Greenwich Mean Sidereal Time calculation.

    GMST is the hour angle of the vernal equinox at Greenwich.
    It increases by about 24h 00m 00s per mean solar day (actually
    23h 56m 4.09s per sidereal day because Earth completes one extra
    rotation per year relative to the stars).

    GMST at J2000.0 is approximately 18h 41m (280.46°).
    """

    @allure.title("GMST at J2000.0 ≈ 18h 41m")
    def test_gmst_at_j2000(self):
        """
        Verify GMST calculation at the J2000.0 epoch.

        The GMST at J2000.0 is well-documented (approximately 18.697h).
        """
        with allure.step("Create JulianDate.j2000()"):
            jd = JulianDate.j2000()
        with allure.step("Calculate GMST"):
            gmst = jd.gmst()
        with allure.step(f"GMST = {gmst:.3f}h (expected ~18.697h)"):
            assert 18.6 < gmst < 18.8

    @allure.title("GMST is always in [0, 24) hours")
    def test_gmst_range(self):
        """
        Verify GMST is properly normalized to [0, 24) hours.

        Regardless of the date, GMST should be a valid hour angle.
        """
        for offset in [0, 100, 1000, -100, -1000]:
            with allure.step(f"Test JD offset = {offset} days"):
                jd = JulianDate.j2000() + offset
                gmst = jd.gmst()
                assert 0 <= gmst < 24, f"GMST {gmst} out of range for offset {offset}"

    @allure.title("GMST verbose mode produces steps")
    def test_gmst_verbose(self):
        """
        Verify verbose mode shows GMST calculation steps.

        Verbose output helps students understand the GMST calculation
        algorithm.
        """
        with allure.step("Create verbose context"):
            ctx = VerboseContext()
        with allure.step("Calculate GMST with verbose"):
            jd = JulianDate.j2000()
            jd.gmst(verbose=ctx)
        with allure.step(f"Verbose steps: {len(ctx.steps)}"):
            assert len(ctx.steps) > 0


# ═══════════════════════════════════════════════════════════════════════════════
#  LOCAL SIDEREAL TIME
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Local Sidereal Time")
class TestLST:
    """
    Tests for Local Sidereal Time calculation.

    LST = GMST + (longitude in hours)

    LST tells observers which Right Ascension is currently on their
    meridian. When LST equals an object's RA, that object is at its
    highest point in the sky (crossing the meridian).
    """

    @allure.title("LST at Greenwich = GMST")
    def test_lst_at_greenwich(self):
        """
        Verify that LST equals GMST at Greenwich (longitude 0°).

        Greenwich is the reference meridian, so no longitude correction
        is needed.
        """
        with allure.step("Create JulianDate.j2000()"):
            jd = JulianDate.j2000()
        with allure.step("Calculate GMST"):
            gmst = jd.gmst()
        with allure.step("Calculate LST at lon=0°"):
            lst = jd.lst(0.0)
        with allure.step(f"GMST = {gmst:.4f}h, LST = {lst:.4f}h"):
            assert math.isclose(lst, gmst, rel_tol=1e-10)

    @allure.title("LST at 180°E = GMST + 12h")
    def test_lst_180_east(self):
        """
        Verify LST calculation at 180° East longitude.

        180° = 12 hours of longitude, so LST should be GMST + 12h
        (with wraparound at 24h).
        """
        with allure.step("Create JulianDate.j2000()"):
            jd = JulianDate.j2000()
        with allure.step("Calculate GMST"):
            gmst = jd.gmst()
        with allure.step("Calculate LST at lon=180°"):
            lst = jd.lst(180.0)
        expected = (gmst + 12.0) % 24
        with allure.step(f"LST = {lst:.4f}h (expected {expected:.4f}h)"):
            assert math.isclose(lst, expected, rel_tol=1e-10)

    @allure.title("LST is always in [0, 24) hours")
    def test_lst_range(self):
        """
        Verify LST is properly normalized for all longitudes.

        LST should always be a valid hour angle regardless of longitude.
        """
        jd = JulianDate.j2000()
        for lon in [-180, -90, 0, 90, 180]:
            with allure.step(f"Test longitude = {lon}°"):
                lst = jd.lst(lon)
                assert 0 <= lst < 24, f"LST {lst} out of range for lon={lon}"


# ═══════════════════════════════════════════════════════════════════════════════
#  JULIAN DATE ARITHMETIC
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("JulianDate Arithmetic")
class TestJulianDateArithmetic:
    """
    Tests for arithmetic operations on JulianDate objects.

    JulianDate supports intuitive operations:
    - JD + days → JD (future date)
    - JD - days → JD (past date)
    - JD - JD → days (time difference)

    These operations simplify calculations involving time intervals.
    """

    @allure.title("Add days to JulianDate")
    def test_add_days(self):
        """
        Verify adding days to a JulianDate.

        This is used for predictions like "where will the Moon be
        in 5 days?"
        """
        with allure.step("Create JulianDate(2451545.0)"):
            jd = JulianDate(2451545.0)
        with allure.step("Add 1 day"):
            result = jd + 1.0
        with allure.step(f"Result = {result.jd}"):
            assert result.jd == 2451546.0

    @allure.title("Subtract days from JulianDate")
    def test_subtract_days(self):
        """
        Verify subtracting days from a JulianDate.

        This is used for historical calculations like "what was the
        Moon phase on a past date?"
        """
        with allure.step("Create JulianDate(2451545.0)"):
            jd = JulianDate(2451545.0)
        with allure.step("Subtract 1 day"):
            result = jd - 1.0
        with allure.step(f"Result = {result.jd}"):
            assert isinstance(result, JulianDate)
            assert result.jd == 2451544.0

    @allure.title("Subtract JulianDates returns float")
    def test_subtract_jd(self):
        """
        Verify that subtracting two JulianDates gives days elapsed.

        This calculates time intervals for synodic periods, proper
        motion calculations, etc.
        """
        with allure.step("Create JD1 = 2451545.0, JD2 = 2451544.0"):
            jd1 = JulianDate(2451545.0)
            jd2 = JulianDate(2451544.0)
        with allure.step("Calculate JD1 - JD2"):
            result = jd1 - jd2
        with allure.step(f"Result = {result} (days)"):
            assert isinstance(result, float)
            assert result == 1.0


# ═══════════════════════════════════════════════════════════════════════════════
#  CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Convenience Functions")
class TestConvenienceFunctions:
    """
    Tests for convenience functions that simplify common operations.

    These functions provide quick access to common operations without
    needing to construct JulianDate objects explicitly.
    """

    @allure.title("jd_now() returns reasonable JD")
    def test_jd_now(self):
        """
        Verify jd_now() returns the current Julian Date.

        The result should be after J2000.0 (in the past) and before
        some far-future date.
        """
        with allure.step("Call jd_now()"):
            jd = jd_now()
        with allure.step(f"JD = {jd.jd}"):
            # After J2000.0 (year 2000)
            assert jd.jd > 2451545.0, "JD should be after J2000.0"
            # Before year 3000
            assert jd.jd < 2816788.0, "JD should be before year 3000"

    @allure.title("utc_to_jd() for J2000.0")
    def test_utc_to_jd(self):
        """
        Verify the utc_to_jd() convenience function.

        Provides a quick way to convert calendar date to JD.
        """
        with allure.step("Call utc_to_jd(2000, 1, 1, 12, 0, 0)"):
            jd = utc_to_jd(2000, 1, 1, 12, 0, 0)
        with allure.step(f"JD = {jd.jd}"):
            assert math.isclose(jd.jd, 2451545.0, rel_tol=1e-10)

    @allure.title("jd_to_utc() for J2000.0")
    def test_jd_to_utc(self):
        """
        Verify the jd_to_utc() convenience function.

        Provides a quick way to convert JD to calendar date.
        """
        with allure.step("Call jd_to_utc(2451545.0)"):
            dt = jd_to_utc(2451545.0)
        with allure.step(f"Result: {dt.year}-{dt.month:02d}-{dt.day:02d} {dt.hour:02d}:00"):
            assert dt.year == 2000
            assert dt.month == 1
            assert dt.day == 1
            assert dt.hour == 12
