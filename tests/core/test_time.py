"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              TIME TESTS                                      ║
║                                                                              ║
║  Tests for Julian dates, sidereal time, and calendar conversions.            ║
║  Time is the fourth dimension of celestial mechanics.                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
import allure
import pytest
from hypothesis import given, strategies as st, settings

from starward.core.time import (
    JulianDate, jd_now, utc_to_jd, jd_to_utc,
    mjd_to_jd, jd_to_mjd
)
from starward.core.constants import CONSTANTS
from starward.verbose import VerboseContext


# ═══════════════════════════════════════════════════════════════════════════════
#  JULIAN DATE CONSTRUCTION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Julian Date Construction")
class TestJulianDateConstruction:
    """
    Tests for creating JulianDate instances.

    The Julian Date (JD) is a continuous count of days since
    January 1, 4713 BC (Julian calendar) at noon.
    """

    @allure.title("Create JD from numerical value")
    def test_direct_creation(self):
        """Create JD from numerical value."""
        with allure.step("Create JulianDate(2451545.0)"):
            jd = JulianDate(2451545.0)

        with allure.step(f"JD = {jd.jd}"):
            assert jd.jd == 2451545.0

    @allure.title("J2000.0 factory method")
    def test_j2000_epoch(self):
        """J2000.0 factory method."""
        with allure.step("Create JulianDate.j2000()"):
            jd = JulianDate.j2000()

        with allure.step(f"JD = {jd.jd} (expected 2451545.0)"):
            assert jd.jd == 2451545.0

    @allure.title("Create JD from Modified Julian Date")
    def test_from_mjd(self):
        """Create JD from Modified Julian Date."""
        with allure.step("Create from MJD 51544.5"):
            jd = JulianDate.from_mjd(51544.5)

        with allure.step(f"JD = {jd.jd:.1f} (expected 2451545.0)"):
            assert math.isclose(jd.jd, 2451545.0, rel_tol=1e-10)

    @allure.title("Create JD from datetime at J2000.0")
    def test_from_datetime_j2000(self):
        """Create JD from datetime at J2000.0."""
        with allure.step("Create datetime: 2000-01-01 12:00 UTC"):
            dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        with allure.step("Convert to JulianDate"):
            jd = JulianDate.from_datetime(dt)

        with allure.step(f"JD = {jd.jd:.1f} (expected 2451545.0)"):
            assert math.isclose(jd.jd, 2451545.0, rel_tol=1e-10)

    @allure.title("Create JD from calendar components")
    def test_from_calendar(self):
        """Create JD from calendar components."""
        with allure.step("Create from 2000-01-01 12:00:00"):
            jd = JulianDate.from_calendar(2000, 1, 1, 12, 0, 0)

        with allure.step(f"JD = {jd.jd:.1f} (expected 2451545.0)"):
            assert math.isclose(jd.jd, 2451545.0, rel_tol=1e-10)

    @allure.title("Create JD with fractional seconds")
    def test_from_calendar_with_fractions(self):
        """Create JD with fractional seconds."""
        with allure.step("Create two JDs 30 seconds apart"):
            jd1 = JulianDate.from_calendar(2000, 1, 1, 12, 0, 0)
            jd2 = JulianDate.from_calendar(2000, 1, 1, 12, 0, 30)

        with allure.step("Calculate difference"):
            diff = jd2.jd - jd1.jd
            expected = 30 / 86400

        with allure.step(f"Diff = {diff:.9f} days (expected {expected:.9f})"):
            assert math.isclose(diff, expected, abs_tol=1e-9)


# ═══════════════════════════════════════════════════════════════════════════════
#  KNOWN JULIAN DATES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Known Julian Dates")
class TestKnownJulianDates:
    """
    Tests against authoritative Julian Date values.
    """

    @pytest.mark.golden
    @allure.title("Verify JD for known dates")
    @pytest.mark.parametrize("year,month,day,hour,minute,second,expected_jd", [
        (2000, 1, 1, 12, 0, 0, 2451545.0),        # J2000.0
        (1858, 11, 17, 0, 0, 0, 2400000.5),       # MJD epoch
        (2024, 1, 1, 0, 0, 0, 2460310.5),         # Recent date
        (1999, 12, 31, 0, 0, 0, 2451543.5),       # Day before J2000
        (2100, 1, 1, 0, 0, 0, 2488069.5),         # Future date
        (1970, 1, 1, 0, 0, 0, 2440587.5),         # Unix epoch
    ])
    def test_known_jd_values(self, year, month, day, hour, minute, second, expected_jd):
        """Verify JD calculation for known dates."""
        with allure.step(f"Create JD from {year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}:{second:02d}"):
            jd = JulianDate.from_calendar(year, month, day, hour, minute, second)

        with allure.step(f"JD = {jd.jd:.1f} (expected {expected_jd})"):
            assert math.isclose(jd.jd, expected_jd, rel_tol=1e-9)

    @pytest.mark.golden
    @allure.title("Sputnik launch: 1957-10-04")
    def test_historical_sputnik(self):
        """Sputnik launch: 1957-10-04 19:28 UTC."""
        with allure.step("Create JD for Sputnik launch"):
            jd = JulianDate.from_calendar(1957, 10, 4, 19, 28, 0)

        with allure.step(f"JD = {jd.jd:.2f} (expected ~2436116.31)"):
            assert 2436116 < jd.jd < 2436117

    @pytest.mark.golden
    @allure.title("Apollo 11 landing: 1969-07-20")
    def test_historical_apollo11(self):
        """Apollo 11 landing: 1969-07-20 20:17 UTC."""
        with allure.step("Create JD for Apollo 11 landing"):
            jd = JulianDate.from_calendar(1969, 7, 20, 20, 17, 0)

        with allure.step(f"JD = {jd.jd:.2f} (expected ~2440423.35)"):
            assert 2440423 < jd.jd < 2440424


# ═══════════════════════════════════════════════════════════════════════════════
#  ROUNDTRIP CONVERSIONS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Roundtrip Conversions")
class TestJulianDateRoundtrip:
    """
    Tests that datetime ↔ JD conversions are reversible.
    """

    @pytest.mark.roundtrip
    @allure.title("datetime → JD → datetime at J2000.0")
    def test_roundtrip_j2000(self):
        """datetime → JD → datetime at J2000.0."""
        with allure.step("Create original datetime"):
            original = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        with allure.step("Convert to JD"):
            jd = JulianDate.from_datetime(original)

        with allure.step("Convert back to datetime"):
            result = jd.to_datetime()

        with allure.step("Calculate difference"):
            delta = abs((result - original).total_seconds())

        with allure.step(f"Difference = {delta} seconds (expected < 1e-6)"):
            assert delta < 1e-6

    @pytest.mark.roundtrip
    @allure.title("Roundtrip with microseconds")
    def test_roundtrip_arbitrary_date(self):
        """Roundtrip with microseconds."""
        with allure.step("Create datetime with microseconds"):
            original = datetime(2024, 6, 15, 14, 30, 45, 123456, tzinfo=timezone.utc)

        with allure.step("Convert to JD and back"):
            jd = JulianDate.from_datetime(original)
            result = jd.to_datetime()

        with allure.step("Calculate difference"):
            delta = abs((result - original).total_seconds())

        with allure.step(f"Difference = {delta} seconds (expected < 1e-5)"):
            assert delta < 1e-5

    @pytest.mark.roundtrip
    @allure.title("JD → datetime → JD is identity")
    def test_roundtrip_jd_dt_jd(self):
        """JD → datetime → JD is identity."""
        with allure.step("Create original JD"):
            original_jd = 2460000.123456
            jd = JulianDate(original_jd)

        with allure.step("Convert to datetime"):
            dt = jd.to_datetime()

        with allure.step("Convert back to JD"):
            back = JulianDate.from_datetime(dt)

        with allure.step(f"Original: {original_jd}, Back: {back.jd}"):
            assert math.isclose(back.jd, original_jd, rel_tol=1e-10)

    @pytest.mark.roundtrip
    @allure.title("Property test: JD ↔ datetime roundtrip")
    @given(st.floats(min_value=2400000, max_value=2500000, allow_nan=False))
    @settings(max_examples=100)
    def test_roundtrip_property(self, jd_val):
        """Property test: JD ↔ datetime roundtrip."""
        jd = JulianDate(jd_val)
        dt = jd.to_datetime()
        back = JulianDate.from_datetime(dt)

        assert math.isclose(back.jd, jd_val, rel_tol=1e-9)


# ═══════════════════════════════════════════════════════════════════════════════
#  MODIFIED JULIAN DATE
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Modified Julian Date")
class TestModifiedJulianDate:
    """
    Tests for Modified Julian Date (MJD).

    MJD = JD - 2400000.5
    """

    @allure.title("JD.mjd accessor")
    def test_mjd_property(self):
        """JD.mjd accessor."""
        with allure.step("Create JD 2451545.0"):
            jd = JulianDate(2451545.0)

        with allure.step(f"MJD = {jd.mjd:.1f} (expected 51544.5)"):
            assert math.isclose(jd.mjd, 51544.5, rel_tol=1e-10)

    @allure.title("Convert MJD to JD")
    def test_mjd_to_jd_function(self):
        """Convert MJD to JD."""
        with allure.step("Convert MJD 51544.5"):
            result = mjd_to_jd(51544.5)

        with allure.step(f"JD = {result:.1f} (expected 2451545.0)"):
            assert math.isclose(result, 2451545.0, rel_tol=1e-10)

    @allure.title("Convert JD to MJD")
    def test_jd_to_mjd_function(self):
        """Convert JD to MJD."""
        with allure.step("Convert JD 2451545.0"):
            result = jd_to_mjd(2451545.0)

        with allure.step(f"MJD = {result:.1f} (expected 51544.5)"):
            assert math.isclose(result, 51544.5, rel_tol=1e-10)

    @pytest.mark.golden
    @allure.title("MJD = 0 at JD = 2400000.5")
    def test_mjd_epoch(self):
        """MJD = 0 at JD = 2400000.5."""
        with allure.step("Create JD at MJD epoch"):
            jd = JulianDate(2400000.5)

        with allure.step(f"MJD = {jd.mjd} (expected 0.0)"):
            assert math.isclose(jd.mjd, 0.0, abs_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  JULIAN CENTURIES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Julian Centuries")
class TestJulianCenturies:
    """
    Tests for Julian centuries since J2000.0.

    T = (JD - 2451545.0) / 36525
    """

    @allure.title("T = 0 at J2000.0")
    def test_t_j2000_at_j2000(self):
        """T = 0 at J2000.0."""
        with allure.step("Create J2000.0"):
            jd = JulianDate.j2000()

        with allure.step(f"T = {jd.t_j2000} (expected 0.0)"):
            assert math.isclose(jd.t_j2000, 0.0, abs_tol=1e-10)

    @allure.title("T = 1 one century after J2000.0")
    def test_t_j2000_one_century_later(self):
        """T = 1 one century after J2000.0."""
        with allure.step("Create JD one century after J2000.0"):
            jd = JulianDate(2451545.0 + 36525.0)

        with allure.step(f"T = {jd.t_j2000:.6f} (expected 1.0)"):
            assert math.isclose(jd.t_j2000, 1.0, rel_tol=1e-10)

    @allure.title("T < 0 before J2000.0")
    def test_t_j2000_negative(self):
        """T < 0 before J2000.0."""
        with allure.step("Create JD one century before J2000.0 (J1900.0)"):
            jd = JulianDate(2451545.0 - 36525.0)

        with allure.step(f"T = {jd.t_j2000:.6f} (expected -1.0)"):
            assert math.isclose(jd.t_j2000, -1.0, rel_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  GREENWICH MEAN SIDEREAL TIME
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("GMST")
class TestGMST:
    """
    Tests for Greenwich Mean Sidereal Time.

    GMST measures the rotation of Earth relative to the vernal equinox.
    """

    @pytest.mark.golden
    @allure.title("GMST at J2000.0 ≈ 18.697h")
    def test_gmst_at_j2000(self):
        """GMST at J2000.0 ≈ 18h 41m (18.697h)."""
        with allure.step("Create J2000.0"):
            jd = JulianDate.j2000()

        with allure.step("Calculate GMST"):
            gmst = jd.gmst()

        with allure.step(f"GMST = {gmst:.3f}h (expected 18.6-18.8h)"):
            assert 18.6 < gmst < 18.8

    @allure.title("GMST always in [0, 24) hours")
    def test_gmst_always_in_range(self):
        """GMST is always in [0, 24) hours."""
        with allure.step("Test various JD offsets"):
            for offset in [0, 100, 1000, -100, -1000]:
                jd = JulianDate.j2000() + offset
                gmst = jd.gmst()
                with allure.step(f"Offset {offset}: GMST = {gmst:.3f}h"):
                    assert 0 <= gmst < 24

    @allure.title("GMST increases with time")
    def test_gmst_increases_with_time(self):
        """GMST increases as time passes."""
        with allure.step("Create two JDs 2.4 hours apart"):
            jd1 = JulianDate.j2000()
            jd2 = JulianDate.j2000() + 0.1

        with allure.step("Calculate GMST values"):
            gmst1 = jd1.gmst()
            gmst2 = jd2.gmst()

        with allure.step("Account for wraparound"):
            diff = (gmst2 - gmst1) % 24

        with allure.step(f"GMST1 = {gmst1:.3f}h, GMST2 = {gmst2:.3f}h, Diff = {diff:.3f}h"):
            assert 0 < diff < 12

    @pytest.mark.verbose
    @allure.title("Verbose mode produces calculation steps")
    def test_gmst_verbose(self):
        """Verbose mode produces calculation steps."""
        with allure.step("Create VerboseContext"):
            ctx = VerboseContext()

        with allure.step("Calculate GMST with verbose=ctx"):
            jd = JulianDate.j2000()
            jd.gmst(verbose=ctx)

        with allure.step(f"Produced {len(ctx.steps)} steps"):
            assert len(ctx.steps) > 0


# ═══════════════════════════════════════════════════════════════════════════════
#  LOCAL SIDEREAL TIME
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("LST")
class TestLST:
    """
    Tests for Local Sidereal Time.

    LST = GMST + longitude/15 (hours)
    """

    @allure.title("LST at Greenwich equals GMST")
    def test_lst_at_greenwich(self):
        """LST at Greenwich (lon=0°) equals GMST."""
        with allure.step("Calculate GMST and LST at Greenwich"):
            jd = JulianDate.j2000()
            gmst = jd.gmst()
            lst = jd.lst(0.0)

        with allure.step(f"GMST = {gmst:.6f}h, LST = {lst:.6f}h"):
            assert math.isclose(lst, gmst, rel_tol=1e-10)

    @allure.title("LST at 180°E = GMST + 12h")
    def test_lst_180_east(self):
        """LST at 180°E is GMST + 12h."""
        with allure.step("Calculate GMST and LST at 180°E"):
            jd = JulianDate.j2000()
            gmst = jd.gmst()
            lst = jd.lst(180.0)
            expected = (gmst + 12.0) % 24

        with allure.step(f"LST = {lst:.3f}h (expected {expected:.3f}h)"):
            assert math.isclose(lst, expected, rel_tol=1e-10)

    @allure.title("LST at 90°W = GMST - 6h")
    def test_lst_90_west(self):
        """LST at 90°W is GMST - 6h."""
        with allure.step("Calculate GMST and LST at 90°W"):
            jd = JulianDate.j2000()
            gmst = jd.gmst()
            lst = jd.lst(-90.0)
            expected = (gmst - 6.0) % 24

        with allure.step(f"LST = {lst:.3f}h (expected {expected:.3f}h)"):
            assert math.isclose(lst, expected, rel_tol=1e-10)

    @allure.title("LST always in [0, 24) hours")
    def test_lst_always_in_range(self):
        """LST is always in [0, 24) hours."""
        with allure.step("Test various longitudes"):
            jd = JulianDate.j2000()
            for lon in [-180, -90, 0, 90, 180]:
                lst = jd.lst(lon)
                with allure.step(f"Lon {lon}°: LST = {lst:.3f}h"):
                    assert 0 <= lst < 24


# ═══════════════════════════════════════════════════════════════════════════════
#  ARITHMETIC OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Arithmetic")
class TestJulianDateArithmetic:
    """
    Tests for JulianDate arithmetic.
    """

    @allure.title("JD + days")
    def test_add_days(self):
        """Add days to JD."""
        with allure.step("Create JD 2451545.0"):
            jd = JulianDate(2451545.0)

        with allure.step("Add 1 day"):
            result = jd + 1.0

        with allure.step(f"Result = {result.jd} (expected 2451546.0)"):
            assert result.jd == 2451546.0

    @allure.title("JD + fractional days")
    def test_add_fractional_days(self):
        """Add fractional days (hours)."""
        with allure.step("Create JD 2451545.0"):
            jd = JulianDate(2451545.0)

        with allure.step("Add 0.5 days (12 hours)"):
            result = jd + 0.5

        with allure.step(f"Result = {result.jd} (expected 2451545.5)"):
            assert result.jd == 2451545.5

    @allure.title("JD - days")
    def test_subtract_days(self):
        """Subtract days from JD."""
        with allure.step("Create JD 2451545.0"):
            jd = JulianDate(2451545.0)

        with allure.step("Subtract 1 day"):
            result = jd - 1.0

        with allure.step("Verify returns JulianDate"):
            assert isinstance(result, JulianDate)

        with allure.step(f"Result = {result.jd} (expected 2451544.0)"):
            assert result.jd == 2451544.0

    @allure.title("JD - JD = days")
    def test_subtract_jd_from_jd(self):
        """Difference between two JDs is days."""
        with allure.step("Create two JDs"):
            jd1 = JulianDate(2451545.0)
            jd2 = JulianDate(2451544.0)

        with allure.step("Calculate difference"):
            result = jd1 - jd2

        with allure.step("Verify returns float"):
            assert isinstance(result, float)

        with allure.step(f"Difference = {result} days (expected 1.0)"):
            assert result == 1.0

    @allure.title("Chained arithmetic")
    def test_arithmetic_chain(self):
        """Chain multiple operations."""
        with allure.step("Create JD 2451545.0"):
            jd = JulianDate(2451545.0)

        with allure.step("Calculate jd + 1 + 2 - 0.5"):
            result = jd + 1.0 + 2.0 - 0.5

        with allure.step(f"Result = {result.jd} (expected 2451547.5)"):
            assert result.jd == 2451547.5


# ═══════════════════════════════════════════════════════════════════════════════
#  CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Convenience Functions")
class TestConvenienceFunctions:
    """
    Tests for convenience functions.
    """

    @allure.title("jd_now() returns current time")
    def test_jd_now_is_current(self):
        """jd_now() returns current time."""
        with allure.step("Get current JD"):
            jd = jd_now()

        with allure.step(f"Current JD = {jd.jd:.4f}"):
            pass

        with allure.step("Verify after J2000.0 (year 2000)"):
            assert jd.jd > 2451545.0

        with allure.step("Verify before year 3000"):
            assert jd.jd < 2816788.0

    @allure.title("utc_to_jd convenience function")
    def test_utc_to_jd(self):
        """utc_to_jd convenience function."""
        with allure.step("Convert 2000-01-01 12:00:00 UTC"):
            jd = utc_to_jd(2000, 1, 1, 12, 0, 0)

        with allure.step(f"JD = {jd.jd:.1f} (expected 2451545.0)"):
            assert math.isclose(jd.jd, 2451545.0, rel_tol=1e-10)

    @allure.title("jd_to_utc convenience function")
    def test_jd_to_utc(self):
        """jd_to_utc convenience function."""
        with allure.step("Convert JD 2451545.0 to UTC"):
            dt = jd_to_utc(2451545.0)

        with allure.step(f"Result: {dt}"):
            assert dt.year == 2000
            assert dt.month == 1
            assert dt.day == 1
            assert dt.hour == 12


# ═══════════════════════════════════════════════════════════════════════════════
#  EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Time Edge Cases")
class TestTimeEdgeCases:
    """
    Tests for edge cases in time handling.
    """

    @pytest.mark.edge
    @allure.title("Leap year handling (Feb 29)")
    def test_leap_year(self):
        """Correctly handle leap year (Feb 29)."""
        with allure.step("Create JD for 2000-02-29"):
            jd = JulianDate.from_calendar(2000, 2, 29, 0, 0, 0)

        with allure.step("Convert back to datetime"):
            dt = jd.to_datetime()

        with allure.step(f"Month = {dt.month}, Day = {dt.day}"):
            assert dt.month == 2
            assert dt.day == 29

    @pytest.mark.edge
    @allure.title("Feb 29 in non-leap year fails")
    def test_non_leap_year(self):
        """Feb 29 in non-leap year should fail."""
        with allure.step("Attempt to create 2001-02-29"):
            with pytest.raises(ValueError):
                JulianDate.from_calendar(2001, 2, 29, 0, 0, 0)

    @pytest.mark.edge
    @allure.title("2100 is NOT a leap year")
    def test_year_2100_not_leap(self):
        """2100 is NOT a leap year (divisible by 100 but not 400)."""
        with allure.step("Attempt to create 2100-02-29"):
            with pytest.raises(ValueError):
                JulianDate.from_calendar(2100, 2, 29, 0, 0, 0)

    @pytest.mark.edge
    @allure.title("2000 IS a leap year")
    def test_year_2000_is_leap(self):
        """2000 IS a leap year (divisible by 400)."""
        with allure.step("Create 2000-02-29"):
            jd = JulianDate.from_calendar(2000, 2, 29, 0, 0, 0)

        with allure.step("Convert back to datetime"):
            dt = jd.to_datetime()

        with allure.step(f"Month = {dt.month}, Day = {dt.day}"):
            assert dt.month == 2
            assert dt.day == 29

    @pytest.mark.edge
    @allure.title("Midnight boundary")
    def test_midnight_boundary(self):
        """Test midnight boundary correctly."""
        with allure.step("Create JDs at 23:59:59 and 00:00:00"):
            jd1 = JulianDate.from_calendar(2000, 1, 1, 23, 59, 59)
            jd2 = JulianDate.from_calendar(2000, 1, 2, 0, 0, 0)

        with allure.step("Calculate difference"):
            diff = jd2.jd - jd1.jd
            expected = 1/86400

        with allure.step(f"Diff = {diff:.9f} days (expected ~{expected:.9f})"):
            assert math.isclose(diff, expected, rel_tol=0.01)
