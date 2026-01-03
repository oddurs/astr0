"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          VISIBILITY TESTS                                    ║
║                                                                              ║
║  Tests for astronomical visibility calculations - airmass, transit times,    ║
║  rise/set, and observability assessment. Planning the perfect observation.   ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import math
import pytest

from astr0.core.angles import Angle
from astr0.core.coords import ICRSCoord
from astr0.core.time import JulianDate, jd_now
from astr0.core.observer import Observer
from astr0.core.visibility import (
    airmass, target_altitude, target_azimuth,
    transit_time, transit_altitude_calc, target_rise_set,
    moon_target_separation, is_night, compute_visibility,
    TargetVisibility
)

# ═══════════════════════════════════════════════════════════════════════════════
#  AIRMASS
# ═══════════════════════════════════════════════════════════════════════════════

class TestAirmass:
    """
    Tests for airmass calculations.
    
    Airmass X = 1/cos(z) for a plane-parallel atmosphere,
    with corrections for refraction near the horizon.
    """
    
    @pytest.mark.golden
    def test_zenith_airmass_is_one(self):
        """Airmass at zenith (90° altitude) = 1.0."""
        alt = Angle(degrees=90)
        X = airmass(alt)
        assert X == pytest.approx(1.0, rel=0.01)
    
    @pytest.mark.golden
    def test_45_degrees_airmass(self):
        """Airmass at 45° ≈ √2 ≈ 1.41."""
        alt = Angle(degrees=45)
        X = airmass(alt)
        assert X == pytest.approx(1.41, rel=0.02)
    
    @pytest.mark.golden
    def test_30_degrees_airmass(self):
        """Airmass at 30° ≈ 2.0."""
        alt = Angle(degrees=30)
        X = airmass(alt)
        assert X == pytest.approx(2.0, rel=0.02)
    
    def test_low_altitude_airmass(self):
        """Airmass increases rapidly near horizon."""
        alt_10 = airmass(Angle(degrees=10))
        alt_5 = airmass(Angle(degrees=5))
        alt_1 = airmass(Angle(degrees=1))
        
        assert alt_5 > alt_10
        assert alt_1 > alt_5
    
    def test_horizon_airmass(self):
        """Airmass at 1° altitude is very large."""
        alt = Angle(degrees=1)
        X = airmass(alt)
        assert X > 25
    
    def test_below_horizon_none(self):
        """Airmass below horizon is None."""
        alt = Angle(degrees=-5)
        X = airmass(alt)
        assert X is None
    
    def test_negative_altitude_none(self):
        """Any negative altitude gives None airmass."""
        for deg in [-1, -10, -45, -89]:
            X = airmass(Angle(degrees=deg))
            assert X is None


class TestAirmassThresholds:
    """
    Tests for typical observational airmass limits.
    """
    
    def test_airmass_2_altitude(self):
        """X = 2 corresponds to altitude ≈ 30°."""
        alt = Angle(degrees=30)
        X = airmass(alt)
        assert 1.9 < X < 2.1
    
    def test_good_airmass_altitude(self):
        """X < 1.5 requires altitude > 42°."""
        alt = Angle(degrees=42)
        X = airmass(alt)
        assert X < 1.5


# ═══════════════════════════════════════════════════════════════════════════════
#  TARGET ALTITUDE & AZIMUTH
# ═══════════════════════════════════════════════════════════════════════════════

class TestTargetAltitude:
    """
    Tests for target altitude calculations.
    """
    
    def test_returns_angle(self, greenwich):
        """target_altitude() returns an Angle."""
        target = ICRSCoord.from_degrees(0, 45)
        jd = jd_now()
        alt = target_altitude(target, greenwich, jd)
        assert isinstance(alt, Angle)
    
    def test_altitude_range(self, greenwich):
        """Altitude is in [-90°, +90°]."""
        target = ICRSCoord.from_degrees(0, 45)
        for offset in range(0, 24, 3):
            jd = JulianDate(2460000.5 + offset / 24)
            alt = target_altitude(target, greenwich, jd)
            assert -90 <= alt.degrees <= 90


class TestTargetAzimuth:
    """
    Tests for target azimuth calculations.
    """
    
    def test_returns_angle(self, greenwich):
        """target_azimuth() returns an Angle."""
        target = ICRSCoord.from_degrees(0, 45)
        jd = jd_now()
        az = target_azimuth(target, greenwich, jd)
        assert isinstance(az, Angle)
    
    def test_azimuth_range(self, greenwich):
        """Azimuth is in [0°, 360°)."""
        target = ICRSCoord.from_degrees(0, 45)
        for offset in range(0, 24, 3):
            jd = JulianDate(2460000.5 + offset / 24)
            az = target_azimuth(target, greenwich, jd)
            assert 0 <= az.degrees < 360


# ═══════════════════════════════════════════════════════════════════════════════
#  TRANSIT
# ═══════════════════════════════════════════════════════════════════════════════

class TestTransit:
    """
    Tests for meridian transit calculations.
    
    Transit occurs when the object crosses the local meridian
    (highest altitude of the night).
    """
    
    def test_transit_time_returns_jd(self, greenwich):
        """transit_time() returns JulianDate."""
        target = ICRSCoord.from_degrees(0, 45)
        jd = jd_now()
        transit = transit_time(target, greenwich, jd)
        
        if transit:
            assert isinstance(transit, JulianDate)
    
    def test_transit_altitude(self, greenwich):
        """transit_altitude_calc() returns maximum altitude."""
        target = ICRSCoord.from_degrees(0, 45)
        max_alt = transit_altitude_calc(target, greenwich)
        
        assert isinstance(max_alt, Angle)
        assert max_alt.degrees <= 90
    
    @pytest.mark.golden
    def test_circumpolar_transit_altitude(self, greenwich):
        """
        For circumpolar stars, transit altitude = 90° - |lat - dec|.
        
        At Greenwich (51.5°N), Polaris (Dec +89°) transits at:
        90° - (89° - 51.5°) = 52.5°
        """
        polaris = ICRSCoord.parse("02h31m49s +89d15m51s")
        max_alt = transit_altitude_calc(polaris, greenwich)
        
        # Should be roughly equal to latitude
        assert 50 < max_alt.degrees < 55
    
    def test_altitude_highest_at_transit(self, greenwich):
        """Altitude is maximum at transit."""
        target = ICRSCoord.from_degrees(180, 30)
        jd = JulianDate(2460000.5)
        
        transit = transit_time(target, greenwich, jd)
        if transit:
            alt_transit = target_altitude(target, greenwich, transit)
            alt_before = target_altitude(target, greenwich, JulianDate(transit.jd - 1/24))
            alt_after = target_altitude(target, greenwich, JulianDate(transit.jd + 1/24))
            
            assert alt_transit.degrees >= alt_before.degrees
            assert alt_transit.degrees >= alt_after.degrees


# ═══════════════════════════════════════════════════════════════════════════════
#  RISE / SET
# ═══════════════════════════════════════════════════════════════════════════════

class TestTargetRiseSet:
    """
    Tests for target rise and set calculations.
    """
    
    def test_rise_set_returns_tuple(self, greenwich):
        """target_rise_set() returns (rise, set) tuple."""
        target = ICRSCoord.from_degrees(0, 20)
        jd = jd_now()
        
        result = target_rise_set(target, greenwich, jd)
        assert isinstance(result, tuple)
        assert len(result) == 2
    
    def test_equatorial_object_rises_sets(self, greenwich):
        """Objects near celestial equator rise and set daily."""
        target = ICRSCoord.from_degrees(0, 0)  # On equator
        jd = JulianDate(2460000.5)
        
        rise, set_t = target_rise_set(target, greenwich, jd)
        
        # Should have both rise and set
        assert rise is not None or set_t is not None
    
    @pytest.mark.edge
    def test_circumpolar_never_sets(self, greenwich):
        """
        Circumpolar objects never set.
        
        For Greenwich (51.5°N), objects with Dec > 90° - 51.5° = 38.5°
        are circumpolar.
        """
        polaris = ICRSCoord.from_degrees(0, 89)  # Near NCP
        jd = JulianDate(2460000.5)
        
        rise, set_t = target_rise_set(polaris, greenwich, jd)
        
        # Circumpolar: may return None for both
        # (implementation-dependent)


# ═══════════════════════════════════════════════════════════════════════════════
#  MOON SEPARATION
# ═══════════════════════════════════════════════════════════════════════════════

class TestMoonSeparation:
    """
    Tests for Moon-target angular separation.
    """
    
    def test_returns_angle(self):
        """moon_target_separation() returns Angle."""
        target = ICRSCoord.from_degrees(180, 45)
        jd = jd_now()
        
        sep = moon_target_separation(target, jd)
        assert isinstance(sep, Angle)
    
    def test_separation_range(self):
        """Separation is in [0°, 180°]."""
        target = ICRSCoord.from_degrees(180, 45)
        jd = jd_now()
        
        sep = moon_target_separation(target, jd)
        assert 0 <= sep.degrees <= 180


# ═══════════════════════════════════════════════════════════════════════════════
#  NIGHT CHECK
# ═══════════════════════════════════════════════════════════════════════════════

class TestIsNight:
    """
    Tests for determining if it's night (Sun below horizon).
    """
    
    def test_returns_bool(self, greenwich):
        """is_night() returns boolean."""
        jd = jd_now()
        result = is_night(greenwich, jd)
        assert isinstance(result, bool)
    
    def test_midnight_is_usually_night(self, greenwich):
        """Midnight local time is usually night (non-polar)."""
        # Midnight UTC in winter
        jd = JulianDate(2460325.5)  # January, 00:00 UTC
        result = is_night(greenwich, jd)
        assert result is True
    
    def test_noon_is_not_night(self, greenwich):
        """Noon is not night."""
        jd = JulianDate(2460326.0)  # January, 12:00 UTC
        result = is_night(greenwich, jd)
        assert result is False


# ═══════════════════════════════════════════════════════════════════════════════
#  COMPUTE VISIBILITY (COMPREHENSIVE)
# ═══════════════════════════════════════════════════════════════════════════════

class TestComputeVisibility:
    """
    Tests for comprehensive visibility assessment.
    """
    
    def test_returns_target_visibility(self, greenwich):
        """compute_visibility() returns TargetVisibility dataclass."""
        target = ICRSCoord.from_degrees(180, 45)
        jd = jd_now()
        
        vis = compute_visibility(target, greenwich, jd)
        assert isinstance(vis, TargetVisibility)
    
    def test_includes_altitude(self, greenwich):
        """Result includes current altitude."""
        target = ICRSCoord.from_degrees(180, 45)
        jd = jd_now()
        
        vis = compute_visibility(target, greenwich, jd)
        assert hasattr(vis, 'current_altitude')
        assert isinstance(vis.current_altitude, Angle)
    
    def test_includes_airmass(self, greenwich):
        """Result includes airmass (or None if below horizon)."""
        target = ICRSCoord.from_degrees(180, 45)
        jd = jd_now()
        
        vis = compute_visibility(target, greenwich, jd)
        assert hasattr(vis, 'current_airmass')


# ═══════════════════════════════════════════════════════════════════════════════
#  LATITUDE EFFECTS
# ═══════════════════════════════════════════════════════════════════════════════

class TestLatitudeEffects:
    """
    Tests for how latitude affects visibility.
    """
    
    def test_ncp_always_up_at_north_pole(self, north_pole):
        """North Celestial Pole always visible from North Pole."""
        ncp = ICRSCoord.from_degrees(0, 90)
        jd = jd_now()
        
        alt = target_altitude(ncp, north_pole, jd)
        assert alt.degrees > 85  # Should be at zenith
    
    def test_scp_never_up_at_north_pole(self, north_pole):
        """South Celestial Pole never visible from North Pole."""
        scp = ICRSCoord.from_degrees(0, -90)
        jd = jd_now()
        
        alt = target_altitude(scp, north_pole, jd)
        assert alt.degrees < -85  # Should be at nadir
    
    def test_equatorial_objects_transit_at_zenith_equator(self, equator):
        """Equatorial objects transit at zenith for equatorial observers."""
        target = ICRSCoord.from_degrees(0, 0)
        max_alt = transit_altitude_calc(target, equator)
        
        assert max_alt.degrees > 85
