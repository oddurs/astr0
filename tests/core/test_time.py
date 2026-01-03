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
import pytest
from hypothesis import given, strategies as st, settings

from astr0.core.time import (
    JulianDate, jd_now, utc_to_jd, jd_to_utc,
    mjd_to_jd, jd_to_mjd
)
from astr0.core.constants import CONSTANTS
from astr0.verbose import VerboseContext


# ═══════════════════════════════════════════════════════════════════════════════
#  JULIAN DATE CONSTRUCTION
# ═══════════════════════════════════════════════════════════════════════════════

class TestJulianDateConstruction:
    """
    Tests for creating JulianDate instances.
    
    The Julian Date (JD) is a continuous count of days since
    January 1, 4713 BC (Julian calendar) at noon.
    """
    
    def test_direct_creation(self):
        """Create JD from numerical value."""
        jd = JulianDate(2451545.0)
        assert jd.jd == 2451545.0
    
    def test_j2000_epoch(self):
        """J2000.0 factory method."""
        jd = JulianDate.j2000()
        assert jd.jd == 2451545.0
    
    def test_from_mjd(self):
        """Create JD from Modified Julian Date."""
        jd = JulianDate.from_mjd(51544.5)
        assert math.isclose(jd.jd, 2451545.0, rel_tol=1e-10)
    
    def test_from_datetime_j2000(self):
        """Create JD from datetime at J2000.0."""
        dt = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        jd = JulianDate.from_datetime(dt)
        assert math.isclose(jd.jd, 2451545.0, rel_tol=1e-10)
    
    def test_from_calendar(self):
        """Create JD from calendar components."""
        jd = JulianDate.from_calendar(2000, 1, 1, 12, 0, 0)
        assert math.isclose(jd.jd, 2451545.0, rel_tol=1e-10)
    
    def test_from_calendar_with_fractions(self):
        """Create JD with fractional seconds."""
        jd1 = JulianDate.from_calendar(2000, 1, 1, 12, 0, 0)
        jd2 = JulianDate.from_calendar(2000, 1, 1, 12, 0, 30)
        
        # 30 seconds = 30/86400 days ≈ 0.000347222
        # Use abs_tol since the values are very small
        diff = jd2.jd - jd1.jd
        assert math.isclose(diff, 30 / 86400, abs_tol=1e-9)


# ═══════════════════════════════════════════════════════════════════════════════
#  KNOWN JULIAN DATES
# ═══════════════════════════════════════════════════════════════════════════════

class TestKnownJulianDates:
    """
    Tests against authoritative Julian Date values.
    
    Sources: US Naval Observatory, IAU standards
    """
    
    @pytest.mark.golden
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
        jd = JulianDate.from_calendar(year, month, day, hour, minute, second)
        assert math.isclose(jd.jd, expected_jd, rel_tol=1e-9)
    
    @pytest.mark.golden
    def test_historical_sputnik(self):
        """Sputnik launch: 1957-10-04 19:28 UTC."""
        jd = JulianDate.from_calendar(1957, 10, 4, 19, 28, 0)
        # JD 2436116.31 (approximate)
        assert 2436116 < jd.jd < 2436117
    
    @pytest.mark.golden
    def test_historical_apollo11(self):
        """Apollo 11 landing: 1969-07-20 20:17 UTC."""
        jd = JulianDate.from_calendar(1969, 7, 20, 20, 17, 0)
        # JD ~2440423.35
        assert 2440423 < jd.jd < 2440424


# ═══════════════════════════════════════════════════════════════════════════════
#  ROUNDTRIP CONVERSIONS
# ═══════════════════════════════════════════════════════════════════════════════

class TestJulianDateRoundtrip:
    """
    Tests that datetime ↔ JD conversions are reversible.
    """
    
    @pytest.mark.roundtrip
    def test_roundtrip_j2000(self):
        """datetime → JD → datetime at J2000.0."""
        original = datetime(2000, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        jd = JulianDate.from_datetime(original)
        result = jd.to_datetime()
        
        delta = abs((result - original).total_seconds())
        assert delta < 1e-6
    
    @pytest.mark.roundtrip
    def test_roundtrip_arbitrary_date(self):
        """Roundtrip with microseconds."""
        original = datetime(2024, 6, 15, 14, 30, 45, 123456, tzinfo=timezone.utc)
        jd = JulianDate.from_datetime(original)
        result = jd.to_datetime()
        
        delta = abs((result - original).total_seconds())
        assert delta < 1e-5
    
    @pytest.mark.roundtrip
    def test_roundtrip_jd_dt_jd(self):
        """JD → datetime → JD is identity."""
        original_jd = 2460000.123456
        jd = JulianDate(original_jd)
        dt = jd.to_datetime()
        back = JulianDate.from_datetime(dt)
        
        assert math.isclose(back.jd, original_jd, rel_tol=1e-10)
    
    @pytest.mark.roundtrip
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

class TestModifiedJulianDate:
    """
    Tests for Modified Julian Date (MJD).
    
    MJD = JD - 2400000.5
    
    Advantages:
      - Smaller numbers (fits in fewer digits)
      - Day starts at midnight (not noon)
    """
    
    def test_mjd_property(self):
        """JD.mjd accessor."""
        jd = JulianDate(2451545.0)
        assert math.isclose(jd.mjd, 51544.5, rel_tol=1e-10)
    
    def test_mjd_to_jd_function(self):
        """Convert MJD to JD."""
        assert math.isclose(mjd_to_jd(51544.5), 2451545.0, rel_tol=1e-10)
    
    def test_jd_to_mjd_function(self):
        """Convert JD to MJD."""
        assert math.isclose(jd_to_mjd(2451545.0), 51544.5, rel_tol=1e-10)
    
    @pytest.mark.golden
    def test_mjd_epoch(self):
        """MJD = 0 at JD = 2400000.5."""
        jd = JulianDate(2400000.5)
        assert math.isclose(jd.mjd, 0.0, abs_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  JULIAN CENTURIES
# ═══════════════════════════════════════════════════════════════════════════════

class TestJulianCenturies:
    """
    Tests for Julian centuries since J2000.0.
    
    Many astronomical calculations use T = (JD - 2451545.0) / 36525
    as the time parameter.
    """
    
    def test_t_j2000_at_j2000(self):
        """T = 0 at J2000.0."""
        jd = JulianDate.j2000()
        assert math.isclose(jd.t_j2000, 0.0, abs_tol=1e-10)
    
    def test_t_j2000_one_century_later(self):
        """T = 1 one century after J2000.0."""
        jd = JulianDate(2451545.0 + 36525.0)
        assert math.isclose(jd.t_j2000, 1.0, rel_tol=1e-10)
    
    def test_t_j2000_negative(self):
        """T < 0 before J2000.0."""
        jd = JulianDate(2451545.0 - 36525.0)  # J1900.0
        assert math.isclose(jd.t_j2000, -1.0, rel_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  GREENWICH MEAN SIDEREAL TIME
# ═══════════════════════════════════════════════════════════════════════════════

class TestGMST:
    """
    Tests for Greenwich Mean Sidereal Time.
    
    GMST measures the rotation of Earth relative to the vernal equinox.
    One sidereal day ≈ 23h 56m 4s.
    """
    
    @pytest.mark.golden
    def test_gmst_at_j2000(self):
        """GMST at J2000.0 ≈ 18h 41m (18.697h)."""
        jd = JulianDate.j2000()
        gmst = jd.gmst()
        assert 18.6 < gmst < 18.8
    
    def test_gmst_always_in_range(self):
        """GMST is always in [0, 24) hours."""
        for offset in [0, 100, 1000, -100, -1000]:
            jd = JulianDate.j2000() + offset
            gmst = jd.gmst()
            assert 0 <= gmst < 24
    
    def test_gmst_increases_with_time(self):
        """GMST increases as time passes."""
        jd1 = JulianDate.j2000()
        jd2 = JulianDate.j2000() + 0.1  # 2.4 hours later
        
        gmst1 = jd1.gmst()
        gmst2 = jd2.gmst()
        
        # Account for wraparound
        diff = (gmst2 - gmst1) % 24
        assert 0 < diff < 12
    
    @pytest.mark.verbose
    def test_gmst_verbose(self):
        """Verbose mode produces calculation steps."""
        ctx = VerboseContext()
        jd = JulianDate.j2000()
        jd.gmst(verbose=ctx)
        assert len(ctx.steps) > 0


# ═══════════════════════════════════════════════════════════════════════════════
#  LOCAL SIDEREAL TIME
# ═══════════════════════════════════════════════════════════════════════════════

class TestLST:
    """
    Tests for Local Sidereal Time.
    
    LST = GMST + longitude/15 (hours)
    """
    
    def test_lst_at_greenwich(self):
        """LST at Greenwich (lon=0°) equals GMST."""
        jd = JulianDate.j2000()
        gmst = jd.gmst()
        lst = jd.lst(0.0)
        assert math.isclose(lst, gmst, rel_tol=1e-10)
    
    def test_lst_180_east(self):
        """LST at 180°E is GMST + 12h."""
        jd = JulianDate.j2000()
        gmst = jd.gmst()
        lst = jd.lst(180.0)
        expected = (gmst + 12.0) % 24
        assert math.isclose(lst, expected, rel_tol=1e-10)
    
    def test_lst_90_west(self):
        """LST at 90°W is GMST - 6h."""
        jd = JulianDate.j2000()
        gmst = jd.gmst()
        lst = jd.lst(-90.0)
        expected = (gmst - 6.0) % 24
        assert math.isclose(lst, expected, rel_tol=1e-10)
    
    def test_lst_always_in_range(self):
        """LST is always in [0, 24) hours."""
        jd = JulianDate.j2000()
        for lon in [-180, -90, 0, 90, 180]:
            lst = jd.lst(lon)
            assert 0 <= lst < 24


# ═══════════════════════════════════════════════════════════════════════════════
#  ARITHMETIC OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════

class TestJulianDateArithmetic:
    """
    Tests for JulianDate arithmetic.
    
    Operations:
      - JD + days → JD
      - JD - days → JD
      - JD - JD → days (float)
    """
    
    def test_add_days(self):
        """Add days to JD."""
        jd = JulianDate(2451545.0)
        result = jd + 1.0
        assert result.jd == 2451546.0
    
    def test_add_fractional_days(self):
        """Add fractional days (hours)."""
        jd = JulianDate(2451545.0)
        result = jd + 0.5  # 12 hours
        assert result.jd == 2451545.5
    
    def test_subtract_days(self):
        """Subtract days from JD."""
        jd = JulianDate(2451545.0)
        result = jd - 1.0
        assert isinstance(result, JulianDate)
        assert result.jd == 2451544.0
    
    def test_subtract_jd_from_jd(self):
        """Difference between two JDs is days."""
        jd1 = JulianDate(2451545.0)
        jd2 = JulianDate(2451544.0)
        result = jd1 - jd2
        assert isinstance(result, float)
        assert result == 1.0
    
    def test_arithmetic_chain(self):
        """Chain multiple operations."""
        jd = JulianDate(2451545.0)
        result = jd + 1.0 + 2.0 - 0.5
        assert result.jd == 2451547.5


# ═══════════════════════════════════════════════════════════════════════════════
#  CONVENIENCE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

class TestConvenienceFunctions:
    """
    Tests for convenience functions.
    """
    
    def test_jd_now_is_current(self):
        """jd_now() returns current time."""
        jd = jd_now()
        # Should be after J2000.0 (year 2000)
        assert jd.jd > 2451545.0
        # Should be before year 3000
        assert jd.jd < 2816788.0
    
    def test_utc_to_jd(self):
        """utc_to_jd convenience function."""
        jd = utc_to_jd(2000, 1, 1, 12, 0, 0)
        assert math.isclose(jd.jd, 2451545.0, rel_tol=1e-10)
    
    def test_jd_to_utc(self):
        """jd_to_utc convenience function."""
        dt = jd_to_utc(2451545.0)
        assert dt.year == 2000
        assert dt.month == 1
        assert dt.day == 1
        assert dt.hour == 12


# ═══════════════════════════════════════════════════════════════════════════════
#  EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════════

class TestTimeEdgeCases:
    """
    Tests for edge cases in time handling.
    """
    
    @pytest.mark.edge
    def test_leap_year(self):
        """Correctly handle leap year (Feb 29)."""
        jd = JulianDate.from_calendar(2000, 2, 29, 0, 0, 0)
        dt = jd.to_datetime()
        assert dt.month == 2
        assert dt.day == 29
    
    @pytest.mark.edge
    def test_non_leap_year(self):
        """Feb 29 in non-leap year should fail."""
        with pytest.raises(ValueError):
            JulianDate.from_calendar(2001, 2, 29, 0, 0, 0)
    
    @pytest.mark.edge
    def test_year_2100_not_leap(self):
        """2100 is NOT a leap year (divisible by 100 but not 400)."""
        with pytest.raises(ValueError):
            JulianDate.from_calendar(2100, 2, 29, 0, 0, 0)
    
    @pytest.mark.edge
    def test_year_2000_is_leap(self):
        """2000 IS a leap year (divisible by 400)."""
        jd = JulianDate.from_calendar(2000, 2, 29, 0, 0, 0)
        dt = jd.to_datetime()
        assert dt.month == 2
        assert dt.day == 29
    
    @pytest.mark.edge
    def test_midnight_boundary(self):
        """Test midnight boundary correctly."""
        jd1 = JulianDate.from_calendar(2000, 1, 1, 23, 59, 59)
        jd2 = JulianDate.from_calendar(2000, 1, 2, 0, 0, 0)
        
        diff = jd2.jd - jd1.jd
        assert math.isclose(diff, 1/86400, rel_tol=0.01)
