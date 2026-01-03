"""
Tests for v0.2 modules: Sun, Moon, Observer, Visibility.
"""

from __future__ import annotations

import pytest
import math
from datetime import datetime, timezone

from astr0.core.angles import Angle
from astr0.core.time import JulianDate, jd_now
from astr0.core.coords import ICRSCoord
from astr0.core.observer import Observer
from astr0.core.sun import (
    sun_position, sunrise, sunset, solar_noon,
    civil_twilight, nautical_twilight, astronomical_twilight,
    solar_altitude, day_length, SunPosition
)
from astr0.core.moon import (
    moon_position, moon_phase, moon_altitude,
    moonrise, moonset, next_phase,
    MoonPhase, MoonPosition, MoonPhaseInfo
)
from astr0.core.visibility import (
    airmass, target_altitude, target_azimuth,
    transit_time, transit_altitude_calc, target_rise_set,
    moon_target_separation, is_night, compute_visibility
)


# ============================================================================
# Observer Tests
# ============================================================================

class TestObserver:
    """Tests for Observer class."""
    
    def test_create_observer_from_degrees(self):
        """Test creating observer from decimal degrees."""
        obs = Observer.from_degrees("Test", 51.4772, -0.0005, elevation=62.0)
        assert obs.name == "Test"
        assert obs.lat_deg == pytest.approx(51.4772, rel=1e-6)
        assert obs.lon_deg == pytest.approx(-0.0005, rel=1e-6)
        assert obs.elevation == 62.0
    
    def test_observer_latitude_limits(self):
        """Test that latitude is constrained to ±90°."""
        # This should work
        obs = Observer.from_degrees("North Pole", 90.0, 0.0)
        assert obs.lat_deg == 90.0
        
        obs = Observer.from_degrees("South Pole", -90.0, 0.0)
        assert obs.lat_deg == -90.0
    
    def test_observer_longitude_normalization(self):
        """Test longitude is stored as-is (no normalization by Observer class)."""
        obs = Observer.from_degrees("Test", 0.0, 361.0)
        # Longitude is stored as-is, normalization happens elsewhere if needed
        assert obs.lon_deg == 361.0
    
    def test_observer_string_representation(self):
        """Test observer string representation."""
        obs = Observer.from_degrees("Greenwich", 51.4772, 0.0, elevation=62.0)
        s = str(obs)
        assert "Greenwich" in s
        assert "51.4772" in s
    
    def test_observer_to_dict(self):
        """Test converting observer to dictionary."""
        obs = Observer.from_degrees("Test", 34.05, -118.25, timezone="America/Los_Angeles")
        d = obs.to_dict()
        assert d['name'] == "Test"
        assert d['latitude'] == pytest.approx(34.05)
        assert d['longitude'] == pytest.approx(-118.25)


# ============================================================================
# Sun Tests
# ============================================================================

class TestSunPosition:
    """Tests for solar position calculations."""
    
    def test_sun_position_returns_sun_position_object(self):
        """Test that sun_position returns a SunPosition object."""
        jd = JulianDate(2451545.0)  # J2000.0
        pos = sun_position(jd)
        assert isinstance(pos, SunPosition)
    
    def test_sun_position_has_required_fields(self):
        """Test SunPosition has all required fields."""
        jd = JulianDate(2451545.0)
        pos = sun_position(jd)
        
        assert hasattr(pos, 'longitude')
        assert hasattr(pos, 'latitude')
        assert hasattr(pos, 'ra')
        assert hasattr(pos, 'dec')
        assert hasattr(pos, 'distance_au')
        assert hasattr(pos, 'equation_of_time')
    
    def test_sun_at_j2000(self):
        """Test solar position at J2000.0 epoch."""
        jd = JulianDate(2451545.0)  # 2000-01-01 12:00 TT
        pos = sun_position(jd)
        
        # At J2000.0, the Sun should be around RA 18h 45m, Dec -23°
        # (winter solstice was ~Dec 21, so Sun is in Sagittarius)
        assert 270 < pos.ra.degrees < 290  # ~18-19h
        assert -24 < pos.dec.degrees < -22
    
    def test_sun_distance_reasonable(self):
        """Test that Sun distance is within reasonable bounds."""
        jd = jd_now()
        pos = sun_position(jd)
        
        # Earth-Sun distance varies from ~0.983 AU (perihelion) to ~1.017 AU (aphelion)
        assert 0.98 < pos.distance_au < 1.02
    
    def test_sun_ecliptic_latitude_near_zero(self):
        """Test that Sun's ecliptic latitude is essentially zero."""
        jd = jd_now()
        pos = sun_position(jd)
        
        # Sun should always be very close to ecliptic plane
        assert abs(pos.latitude.degrees) < 0.01
    
    def test_equation_of_time_range(self):
        """Test equation of time is within reasonable range."""
        # Test several dates throughout the year
        for offset in range(0, 365, 30):
            jd = JulianDate(2451545.0 + offset)
            pos = sun_position(jd)
            # EoT varies from about -14 to +16 minutes
            assert -17 < pos.equation_of_time < 18


class TestSunrise:
    """Tests for sunrise calculations."""
    
    def test_sunrise_at_greenwich_winter(self):
        """Test sunrise at Greenwich in winter."""
        obs = Observer.from_degrees("Greenwich", 51.4772, 0.0)
        # 2024-01-15 (mid-winter)
        jd = JulianDate(2460325.5)  # Approximate
        
        rise = sunrise(obs, jd)
        
        # Sunrise should exist
        assert rise is not None
        # Should be in the morning UTC (around 7-8 UTC in winter)
        dt = rise.to_datetime()
        assert 6 < dt.hour < 9
    
    def test_sunrise_at_greenwich_summer(self):
        """Test sunrise at Greenwich in summer."""
        obs = Observer.from_degrees("Greenwich", 51.4772, 0.0)
        # 2024-06-21 (summer solstice)
        jd = JulianDate(2460483.5)  # Approximate
        
        rise = sunrise(obs, jd)
        
        # Sunrise should exist and be early
        assert rise is not None
        dt = rise.to_datetime()
        assert 3 <= dt.hour < 6  # Very early in summer (can be as early as 3:43)


class TestSunset:
    """Tests for sunset calculations."""
    
    def test_sunset_at_greenwich_winter(self):
        """Test sunset at Greenwich in winter."""
        obs = Observer.from_degrees("Greenwich", 51.4772, 0.0)
        jd = JulianDate(2460325.5)
        
        set_t = sunset(obs, jd)
        
        assert set_t is not None
        dt = set_t.to_datetime()
        # Sunset around 16:00-17:00 UTC in winter
        assert 15 < dt.hour < 18


class TestSolarAltitude:
    """Tests for solar altitude calculations."""
    
    def test_solar_altitude_at_noon(self):
        """Test solar altitude is highest around local noon."""
        obs = Observer.from_degrees("Greenwich", 51.4772, 0.0)
        
        # Get today's noon
        jd = jd_now()
        noon = solar_noon(obs, jd)
        
        # Altitude at noon
        alt_noon = solar_altitude(obs, noon)
        
        # Check altitude 2 hours before and after
        alt_before = solar_altitude(obs, JulianDate(noon.jd - 2/24))
        alt_after = solar_altitude(obs, JulianDate(noon.jd + 2/24))
        
        # Noon altitude should be highest
        assert alt_noon.degrees > alt_before.degrees
        assert alt_noon.degrees > alt_after.degrees


class TestTwilight:
    """Tests for twilight calculations."""
    
    def test_civil_twilight_exists(self):
        """Test civil twilight calculation."""
        obs = Observer.from_degrees("Greenwich", 51.4772, 0.0)
        jd = JulianDate(2460325.5)
        
        morning, evening = civil_twilight(obs, jd)
        
        assert morning is not None
        assert evening is not None
        assert morning.jd < evening.jd  # Morning before evening
    
    def test_twilight_order(self):
        """Test that twilight types occur in correct order."""
        obs = Observer.from_degrees("Greenwich", 51.4772, 0.0)
        jd = JulianDate(2460325.5)
        
        astro = astronomical_twilight(obs, jd)
        naut = nautical_twilight(obs, jd)
        civil = civil_twilight(obs, jd)
        rise = sunrise(obs, jd)
        
        if all([astro[0], naut[0], civil[0], rise]):
            # Morning order: astronomical < nautical < civil < sunrise
            assert astro[0].jd < naut[0].jd < civil[0].jd < rise.jd


# ============================================================================
# Moon Tests
# ============================================================================

class TestMoonPosition:
    """Tests for lunar position calculations."""
    
    def test_moon_position_returns_moon_position_object(self):
        """Test that moon_position returns a MoonPosition object."""
        jd = JulianDate(2451545.0)
        pos = moon_position(jd)
        assert isinstance(pos, MoonPosition)
    
    def test_moon_position_has_required_fields(self):
        """Test MoonPosition has all required fields."""
        jd = jd_now()
        pos = moon_position(jd)
        
        assert hasattr(pos, 'longitude')
        assert hasattr(pos, 'latitude')
        assert hasattr(pos, 'ra')
        assert hasattr(pos, 'dec')
        assert hasattr(pos, 'distance_km')
        assert hasattr(pos, 'angular_diameter')
        assert hasattr(pos, 'parallax')
    
    def test_moon_distance_reasonable(self):
        """Test that Moon distance is within reasonable bounds."""
        jd = jd_now()
        pos = moon_position(jd)
        
        # Moon distance varies from ~356,500 km (perigee) to ~406,700 km (apogee)
        assert 350000 < pos.distance_km < 410000
    
    def test_moon_angular_diameter_reasonable(self):
        """Test that Moon angular diameter is reasonable."""
        jd = jd_now()
        pos = moon_position(jd)
        
        # Moon angular diameter varies from ~29.4' to ~33.5'
        ang_min = pos.angular_diameter.degrees * 60
        assert 29 < ang_min < 34
    
    def test_moon_ecliptic_latitude_limited(self):
        """Test that Moon's ecliptic latitude is within ±5.3°."""
        jd = jd_now()
        pos = moon_position(jd)
        
        # Moon's orbit is inclined ~5.14° to ecliptic
        assert abs(pos.latitude.degrees) < 5.5


class TestMoonPhase:
    """Tests for moon phase calculations."""
    
    def test_moon_phase_returns_phase_info(self):
        """Test that moon_phase returns MoonPhaseInfo."""
        jd = jd_now()
        phase = moon_phase(jd)
        assert isinstance(phase, MoonPhaseInfo)
    
    def test_moon_phase_illumination_range(self):
        """Test illumination is in valid range."""
        jd = jd_now()
        phase = moon_phase(jd)
        
        assert 0 <= phase.illumination <= 1
        assert 0 <= phase.percent_illuminated <= 100
    
    def test_moon_phase_angle_range(self):
        """Test phase angle is in valid range."""
        jd = jd_now()
        phase = moon_phase(jd)
        
        # Phase angle can be any value in 0-360
        assert 0 <= phase.phase_angle <= 360
    
    def test_moon_age_range(self):
        """Test moon age is in valid range."""
        jd = jd_now()
        phase = moon_phase(jd)
        
        # Moon age should be 0-29.5 days (synodic month)
        assert 0 <= phase.age_days < 30
    
    def test_full_moon_high_illumination(self):
        """Test that full moon has high illumination."""
        # Find a full moon phase angle (~180°)
        jd = jd_now()
        for i in range(30):
            test_jd = JulianDate(jd.jd + i)
            phase = moon_phase(test_jd)
            if 170 < phase.phase_angle < 190:
                # Should be highly illuminated
                assert phase.illumination > 0.95
                break


class TestMoonriseSet:
    """Tests for moonrise/moonset calculations."""
    
    def test_moonrise_at_greenwich(self):
        """Test moonrise calculation."""
        obs = Observer.from_degrees("Greenwich", 51.4772, 0.0)
        jd = jd_now()
        
        rise = moonrise(obs, jd)
        # Moonrise should exist for most days
        # (occasionally Moon may be circumpolar or never rise)
        if rise is not None:
            # Should be a valid JulianDate
            assert isinstance(rise, JulianDate)
            assert rise.jd > 0


class TestNextPhase:
    """Tests for finding next lunar phase."""
    
    def test_next_full_moon(self):
        """Test finding next full moon."""
        jd = jd_now()
        
        next_full = next_phase(jd, MoonPhase.FULL_MOON)
        
        # Should be in the future
        assert next_full.jd > jd.jd
        # Should be within a synodic month
        assert next_full.jd - jd.jd < 30
    
    def test_next_new_moon(self):
        """Test finding next new moon."""
        jd = jd_now()
        
        next_new = next_phase(jd, MoonPhase.NEW_MOON)
        
        assert next_new.jd > jd.jd
        assert next_new.jd - jd.jd < 30


# ============================================================================
# Visibility Tests
# ============================================================================

class TestAirmass:
    """Tests for airmass calculations."""
    
    def test_airmass_at_zenith(self):
        """Test airmass at zenith is 1.0."""
        alt = Angle(degrees=90)
        X = airmass(alt)
        assert X == pytest.approx(1.0, rel=0.01)
    
    def test_airmass_at_45_degrees(self):
        """Test airmass at 45° altitude."""
        alt = Angle(degrees=45)
        X = airmass(alt)
        # Airmass at 45° is approximately 1.41
        assert X == pytest.approx(1.41, rel=0.02)
    
    def test_airmass_at_30_degrees(self):
        """Test airmass at 30° altitude."""
        alt = Angle(degrees=30)
        X = airmass(alt)
        # Airmass at 30° is approximately 2.0
        assert X == pytest.approx(2.0, rel=0.05)
    
    def test_airmass_below_horizon(self):
        """Test airmass is None below horizon."""
        alt = Angle(degrees=-5)
        X = airmass(alt)
        assert X is None
    
    def test_airmass_at_horizon(self):
        """Test airmass at horizon is not infinite."""
        alt = Angle(degrees=0.5)  # Just above horizon
        X = airmass(alt)
        assert X is not None
        # Should be high but not infinite
        assert X < 100


class TestTargetAltitude:
    """Tests for target altitude calculations."""
    
    def test_polaris_altitude_matches_latitude(self):
        """Test that Polaris altitude ≈ observer latitude."""
        # Polaris is at Dec ≈ +89.3°
        polaris = ICRSCoord.from_degrees(37.95, 89.3)
        
        for lat in [30, 45, 60]:
            obs = Observer.from_degrees("Test", lat, 0.0)
            jd = jd_now()
            
            alt = target_altitude(polaris, obs, jd)
            
            # Polaris altitude should be close to latitude
            assert abs(alt.degrees - lat) < 2
    
    def test_circumpolar_target_always_up(self):
        """Test circumpolar target is always above horizon."""
        # Polaris from high latitude
        polaris = ICRSCoord.from_degrees(37.95, 89.3)
        obs = Observer.from_degrees("Arctic", 70.0, 0.0)
        
        # Test every 2 hours through the day
        jd_base = jd_now()
        for hour in range(0, 24, 2):
            jd = JulianDate(jd_base.jd + hour/24)
            alt = target_altitude(polaris, obs, jd)
            assert alt.degrees > 0


class TestTransit:
    """Tests for transit calculations."""
    
    def test_transit_altitude_equals_formula(self):
        """Test transit altitude formula."""
        # Transit altitude = 90° - |lat - dec|
        target = ICRSCoord.from_degrees(0.0, 30.0)  # Dec = +30°
        obs = Observer.from_degrees("Test", 45.0, 0.0)  # Lat = 45°
        
        trans_alt = transit_altitude_calc(target, obs)
        
        # Expected: 90 - |45 - 30| = 75°
        assert trans_alt.degrees == pytest.approx(75.0, rel=0.01)
    
    def test_transit_time_is_when_hour_angle_zero(self):
        """Test transit occurs when hour angle = 0."""
        # At transit, LST = RA
        target = ICRSCoord.from_degrees(90.0, 0.0)  # RA = 6h = 90°
        obs = Observer.from_degrees("Test", 45.0, 0.0)
        jd = jd_now()
        
        trans = transit_time(target, obs, jd)
        
        # At transit, altitude should be at maximum
        alt_at_trans = target_altitude(target, obs, trans)
        alt_before = target_altitude(target, obs, JulianDate(trans.jd - 0.1))
        alt_after = target_altitude(target, obs, JulianDate(trans.jd + 0.1))
        
        assert alt_at_trans.degrees >= alt_before.degrees - 0.1
        assert alt_at_trans.degrees >= alt_after.degrees - 0.1


class TestMoonSeparation:
    """Tests for moon-target separation."""
    
    def test_moon_separation_in_valid_range(self):
        """Test moon separation is in 0-180° range."""
        target = ICRSCoord.from_degrees(90.0, 30.0)
        jd = jd_now()
        
        sep = moon_target_separation(target, jd)
        
        assert 0 <= sep.degrees <= 180


class TestIsNight:
    """Tests for night determination."""
    
    def test_is_night_at_midnight(self):
        """Test that it's night at local midnight (for mid-latitudes in winter)."""
        # Use a location and time where it's definitely night
        obs = Observer.from_degrees("Test", 45.0, 0.0)
        # Local midnight in winter - use a JD that's definitely dark
        # JD 2460325.5 is 2024-01-15 00:00 UTC
        jd = JulianDate(2460325.5)
        
        # At this location at midnight in winter, it should be astronomically dark
        # The function just checks sun altitude, we just verify it returns a bool
        result = is_night(obs, jd, 'civil')
        assert isinstance(result, bool)
        
        # At midnight at 45° lat in January, it should definitely be civil night
        # (sun well below -6°)
        assert result == True


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests combining multiple modules."""
    
    def test_full_visibility_calculation(self):
        """Test complete visibility calculation for a target."""
        target = ICRSCoord.parse("00h42m44s +41d16m09s")  # M31
        obs = Observer.from_degrees("Greenwich", 51.4772, 0.0)
        jd = jd_now()
        
        vis = compute_visibility(target, obs, jd)
        
        # Check that we got valid results
        assert vis.target == target
        assert vis.observer == obs
        assert isinstance(vis.current_altitude, Angle)
        assert isinstance(vis.transit_time, JulianDate)
        assert isinstance(vis.moon_separation, Angle)
    
    def test_sun_moon_separation(self):
        """Test that Sun-Moon separation varies with phase."""
        jd = jd_now()
        
        # At new moon, Sun-Moon separation ≈ 0°
        # At full moon, Sun-Moon separation ≈ 180°
        phase = moon_phase(jd)
        
        from astr0.core.moon import lunar_distance_to_sun
        sep = lunar_distance_to_sun(jd)
        
        # Separation should correlate with phase
        # If phase angle is near 0 (new), separation should be small
        # If phase angle is near 180 (full), separation should be large
        if phase.phase_angle < 45:
            assert sep.degrees < 60
        elif phase.phase_angle > 135:
            assert sep.degrees > 120


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
