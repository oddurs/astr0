"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              MOON TESTS                                      ║
║                                                                              ║
║  Tests for lunar position, phases, rise/set times, and orbital mechanics.    ║
║  Our celestial companion through 4.5 billion years of cosmic dance.          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import math
import pytest

from astr0.core.angles import Angle
from astr0.core.time import JulianDate, jd_now
from astr0.core.observer import Observer
from astr0.core.moon import (
    moon_position, moon_phase, moon_altitude,
    moonrise, moonset, next_phase,
    MoonPhase, MoonPosition, MoonPhaseInfo
)


# ═══════════════════════════════════════════════════════════════════════════════
#  MOON POSITION
# ═══════════════════════════════════════════════════════════════════════════════

class TestMoonPosition:
    """
    Tests for lunar position calculations.
    
    Uses simplified lunar theory suitable for rise/set
    and phase calculations (accuracy ~0.5° in position).
    """
    
    def test_returns_moon_position_object(self):
        """moon_position() returns MoonPosition dataclass."""
        jd = JulianDate(2451545.0)
        pos = moon_position(jd)
        assert isinstance(pos, MoonPosition)
    
    def test_has_required_fields(self):
        """MoonPosition has all required fields."""
        jd = jd_now()
        pos = moon_position(jd)
        
        assert hasattr(pos, 'longitude')
        assert hasattr(pos, 'latitude')
        assert hasattr(pos, 'ra')
        assert hasattr(pos, 'dec')
        assert hasattr(pos, 'distance_km')
        assert hasattr(pos, 'angular_diameter')
        assert hasattr(pos, 'parallax')
    
    def test_distance_within_bounds(self):
        """
        Moon distance varies from perigee to apogee.
        
        Perigee: ~356,500 km
        Apogee: ~406,700 km
        """
        jd = jd_now()
        pos = moon_position(jd)
        assert 350000 < pos.distance_km < 410000
    
    def test_angular_diameter_reasonable(self):
        """
        Moon angular diameter varies with distance.
        
        Range: ~29.4' (apogee) to ~33.5' (perigee)
        """
        jd = jd_now()
        pos = moon_position(jd)
        ang_arcmin = pos.angular_diameter.degrees * 60
        assert 29 < ang_arcmin < 34
    
    def test_ecliptic_latitude_limited(self):
        """Moon's orbit is inclined ~5.14° to ecliptic."""
        jd = jd_now()
        pos = moon_position(jd)
        assert abs(pos.latitude.degrees) < 5.5
    
    def test_parallax_reasonable(self):
        """Moon's horizontal parallax is ~0.9° to ~1.0°."""
        jd = jd_now()
        pos = moon_position(jd)
        parallax_deg = pos.parallax.degrees
        assert 0.85 < parallax_deg < 1.05


# ═══════════════════════════════════════════════════════════════════════════════
#  MOON PHASE
# ═══════════════════════════════════════════════════════════════════════════════

class TestMoonPhase:
    """
    Tests for moon phase calculations.
    """
    
    def test_returns_moon_phase_info(self):
        """moon_phase() returns MoonPhaseInfo."""
        jd = jd_now()
        phase = moon_phase(jd)
        assert isinstance(phase, MoonPhaseInfo)
    
    def test_illumination_range(self):
        """Illumination is in [0, 1]."""
        jd = jd_now()
        phase = moon_phase(jd)
        
        assert 0 <= phase.illumination <= 1
        assert 0 <= phase.percent_illuminated <= 100
    
    def test_phase_angle_range(self):
        """Phase angle is in [0, 360]."""
        jd = jd_now()
        phase = moon_phase(jd)
        assert 0 <= phase.phase_angle <= 360
    
    def test_moon_age_range(self):
        """Moon age is in [0, 29.5] days (synodic month)."""
        jd = jd_now()
        phase = moon_phase(jd)
        assert 0 <= phase.age_days < 30
    
    def test_has_phase_name(self):
        """Phase has a human-readable name."""
        jd = jd_now()
        phase = moon_phase(jd)
        
        valid_names = [
            'New Moon', 'Waxing Crescent', 'First Quarter', 'Waxing Gibbous',
            'Full Moon', 'Waning Gibbous', 'Last Quarter', 'Waning Crescent'
        ]
        assert phase.phase_name.value in valid_names


class TestMoonPhaseIllumination:
    """
    Tests for illumination at specific phases.
    """
    
    @pytest.mark.golden
    def test_full_moon_high_illumination(self):
        """Full moon (phase angle ~180°) is highly illuminated."""
        jd = jd_now()
        # Search for a date near full moon
        for i in range(30):
            test_jd = JulianDate(jd.jd + i)
            phase = moon_phase(test_jd)
            if 170 < phase.phase_angle < 190:
                assert phase.illumination > 0.95
                break
    
    @pytest.mark.golden
    def test_new_moon_low_illumination(self):
        """New moon (phase angle ~0°) has low illumination."""
        jd = jd_now()
        for i in range(30):
            test_jd = JulianDate(jd.jd + i)
            phase = moon_phase(test_jd)
            if phase.phase_angle < 10 or phase.phase_angle > 350:
                assert phase.illumination < 0.05
                break
    
    @pytest.mark.golden
    def test_quarter_moon_half_illuminated(self):
        """Quarter moon (phase angle ~90° or ~270°) is ~50% illuminated."""
        jd = jd_now()
        for i in range(30):
            test_jd = JulianDate(jd.jd + i)
            phase = moon_phase(test_jd)
            if 85 < phase.phase_angle < 95 or 265 < phase.phase_angle < 275:
                assert 0.4 < phase.illumination < 0.6
                break


# ═══════════════════════════════════════════════════════════════════════════════
#  MOONRISE / MOONSET
# ═══════════════════════════════════════════════════════════════════════════════

class TestMoonrise:
    """
    Tests for moonrise calculations.
    """
    
    def test_moonrise_returns_julian_date(self, greenwich):
        """moonrise() returns JulianDate or None."""
        jd = jd_now()
        rise = moonrise(greenwich, jd)
        
        if rise is not None:
            assert isinstance(rise, JulianDate)
            assert rise.jd > 0
    
    def test_moonrise_within_day(self, greenwich):
        """Moonrise should be within ~1 day of reference."""
        jd = jd_now()
        rise = moonrise(greenwich, jd)
        
        if rise:
            # Moon rises approximately every 24h 50m
            assert abs(rise.jd - jd.jd) < 2


class TestMoonset:
    """
    Tests for moonset calculations.
    """
    
    def test_moonset_returns_julian_date(self, greenwich):
        """moonset() returns JulianDate or None."""
        jd = jd_now()
        set_t = moonset(greenwich, jd)
        
        if set_t is not None:
            assert isinstance(set_t, JulianDate)


# ═══════════════════════════════════════════════════════════════════════════════
#  MOON ALTITUDE
# ═══════════════════════════════════════════════════════════════════════════════

class TestMoonAltitude:
    """
    Tests for moon altitude at specific times.
    """
    
    def test_moon_altitude_returns_angle(self, greenwich):
        """moon_altitude() returns an Angle."""
        jd = jd_now()
        alt = moon_altitude(greenwich, jd)
        assert isinstance(alt, Angle)
    
    def test_moon_altitude_range(self, greenwich):
        """Altitude is always in [-90°, +90°]."""
        for offset in range(0, 25):
            jd = JulianDate(2460000.5 + offset / 24)
            alt = moon_altitude(greenwich, jd)
            assert -90 <= alt.degrees <= 90


# ═══════════════════════════════════════════════════════════════════════════════
#  NEXT PHASE
# ═══════════════════════════════════════════════════════════════════════════════

class TestNextPhase:
    """
    Tests for finding the next lunar phase.
    """
    
    def test_next_full_moon(self):
        """Find next full moon."""
        jd = jd_now()
        next_full = next_phase(jd, MoonPhase.FULL_MOON)
        
        assert next_full.jd > jd.jd
        assert next_full.jd - jd.jd < 30  # Within synodic month
    
    def test_next_new_moon(self):
        """Find next new moon."""
        jd = jd_now()
        next_new = next_phase(jd, MoonPhase.NEW_MOON)
        
        assert next_new.jd > jd.jd
        assert next_new.jd - jd.jd < 30
    
    def test_next_first_quarter(self):
        """Find next first quarter."""
        jd = jd_now()
        next_q = next_phase(jd, MoonPhase.FIRST_QUARTER)
        
        assert next_q.jd > jd.jd
        assert next_q.jd - jd.jd < 30
    
    def test_next_last_quarter(self):
        """Find next last quarter."""
        jd = jd_now()
        next_q = next_phase(jd, MoonPhase.LAST_QUARTER)
        
        assert next_q.jd > jd.jd
        assert next_q.jd - jd.jd < 30
    
    @pytest.mark.golden
    def test_synodic_month_between_phases(self):
        """Time between same phases is ~29.5 days (synodic month)."""
        jd = jd_now()
        
        full1 = next_phase(jd, MoonPhase.FULL_MOON)
        full2 = next_phase(JulianDate(full1.jd + 1), MoonPhase.FULL_MOON)
        
        synodic = full2.jd - full1.jd
        assert 29 < synodic < 30


# ═══════════════════════════════════════════════════════════════════════════════
#  EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════════

class TestMoonEdgeCases:
    """
    Tests for edge cases in lunar calculations.
    """
    
    @pytest.mark.edge
    def test_moon_at_north_pole(self, north_pole):
        """Moon calculations work at extreme latitudes."""
        jd = jd_now()
        
        # Should not raise
        pos = moon_position(jd)
        phase = moon_phase(jd)
        alt = moon_altitude(north_pole, jd)
        
        assert pos is not None
        assert phase is not None
        assert alt is not None
    
    @pytest.mark.edge
    def test_moon_at_equator(self, equator):
        """Moon calculations work at equator."""
        jd = jd_now()
        
        rise = moonrise(equator, jd)
        set_t = moonset(equator, jd)
        
        # At equator, moon should rise and set every day
        # (though exact timing depends on lunar declination)
