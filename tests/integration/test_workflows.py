"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        INTEGRATION TESTS                                     ║
║                                                                              ║
║  Tests for cross-module functionality and end-to-end workflows.              ║
║  Where the celestial machinery comes together.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import pytest

from astr0.core.angles import Angle
from astr0.core.coords import ICRSCoord
from astr0.core.time import JulianDate, jd_now
from astr0.core.observer import Observer
from astr0.core.sun import sun_position, sunrise, sunset, solar_noon, solar_altitude
from astr0.core.moon import moon_position, moon_phase, MoonPhase
from astr0.core.visibility import (
    airmass, target_altitude, target_azimuth,
    transit_time, compute_visibility
)


# ═══════════════════════════════════════════════════════════════════════════════
#  VISIBILITY WORKFLOW
# ═══════════════════════════════════════════════════════════════════════════════

class TestVisibilityWorkflow:
    """
    Tests for complete visibility calculation workflows.
    """
    
    def test_full_visibility_calculation(self, greenwich):
        """Test complete visibility calculation for a target."""
        target = ICRSCoord.parse("00h42m44s +41d16m09s")  # M31
        jd = jd_now()
        
        vis = compute_visibility(target, greenwich, jd)
        
        # Check that we got valid results
        assert vis.target == target
        assert vis.observer == greenwich
        assert isinstance(vis.current_altitude, Angle)
        assert isinstance(vis.transit_time, JulianDate)
        assert isinstance(vis.moon_separation, Angle)
    
    def test_observation_planning_workflow(self, greenwich):
        """Test a typical observation planning workflow."""
        # Target: Vega
        target = ICRSCoord.parse("18h36m56.3s +38d47m01s")
        jd = jd_now()
        
        # 1. Get current altitude
        alt = target_altitude(target, greenwich, jd)
        assert isinstance(alt, Angle)
        
        # 2. Get transit time
        transit = transit_time(target, greenwich, jd)
        assert isinstance(transit, JulianDate)
        
        # 3. Get airmass at transit
        alt_at_transit = target_altitude(target, greenwich, transit)
        X = airmass(alt_at_transit)
        
        # Transit should have best airmass
        if alt.degrees > 0:
            X_now = airmass(alt)
            assert X <= X_now or X_now == float('inf')


# ═══════════════════════════════════════════════════════════════════════════════
#  SUN-MOON RELATIONSHIP
# ═══════════════════════════════════════════════════════════════════════════════

class TestSunMoonRelationship:
    """
    Tests for Sun-Moon relationships and phase correlation.
    """
    
    def test_sun_moon_separation_correlates_with_phase(self):
        """Test that Sun-Moon separation varies with phase."""
        jd = jd_now()
        
        # Get phase info
        phase = moon_phase(jd)
        
        # Get positions
        sun_pos = sun_position(jd)
        moon_pos = moon_position(jd)
        
        # Calculate elongation (Sun-Moon separation)
        from astr0.core.angles import angular_separation
        elongation = angular_separation(
            sun_pos.ra, sun_pos.dec,
            moon_pos.ra, moon_pos.dec
        )
        
        # Elongation should correlate with phase angle
        # New moon: elongation ≈ 0°
        # Full moon: elongation ≈ 180°
        # This is a rough correlation check
        if phase.phase_angle < 30:
            assert elongation.degrees < 45
        elif phase.phase_angle > 150:
            assert elongation.degrees > 135


# ═══════════════════════════════════════════════════════════════════════════════
#  SOLAR DAY WORKFLOW
# ═══════════════════════════════════════════════════════════════════════════════

class TestSolarDayWorkflow:
    """
    Tests for complete solar day calculations.
    """
    
    def test_solar_day_timeline(self, greenwich):
        """Test sunrise → noon → sunset sequence."""
        jd = JulianDate(2460325.5)  # Winter day
        
        rise = sunrise(greenwich, jd)
        noon = solar_noon(greenwich, jd)
        set_t = sunset(greenwich, jd)
        
        # Verify sequence
        if rise and noon and set_t:
            assert rise.jd < noon.jd < set_t.jd
            
            # Altitude should be highest at noon
            alt_rise = solar_altitude(greenwich, rise)
            alt_noon = solar_altitude(greenwich, noon)
            alt_set = solar_altitude(greenwich, set_t)
            
            assert alt_noon.degrees > alt_rise.degrees
            assert alt_noon.degrees > alt_set.degrees
    
    def test_seasonal_day_length_variation(self, greenwich):
        """Test that day length varies with season."""
        winter = JulianDate(2460325.5)  # January
        summer = JulianDate(2460483.5)  # June
        
        rise_w = sunrise(greenwich, winter)
        set_w = sunset(greenwich, winter)
        rise_s = sunrise(greenwich, summer)
        set_s = sunset(greenwich, summer)
        
        if all([rise_w, set_w, rise_s, set_s]):
            winter_day = (set_w.jd - rise_w.jd) * 24  # hours
            summer_day = (set_s.jd - rise_s.jd) * 24  # hours
            
            # Summer days should be longer in northern hemisphere
            assert summer_day > winter_day


# ═══════════════════════════════════════════════════════════════════════════════
#  MULTI-TARGET COMPARISON
# ═══════════════════════════════════════════════════════════════════════════════

class TestMultiTargetComparison:
    """
    Tests for comparing visibility of multiple targets.
    """
    
    def test_compare_target_altitudes(self, greenwich, famous_stars):
        """Compare altitudes of multiple targets."""
        jd = jd_now()
        
        altitudes = {}
        for name, coord in famous_stars.items():
            alt = target_altitude(coord, greenwich, jd)
            altitudes[name] = alt.degrees
        
        # All should be valid angles
        for name, alt in altitudes.items():
            assert -90 <= alt <= 90
    
    def test_circumpolar_vs_rising_setting(self, greenwich, famous_stars):
        """Test that Polaris is always up from Greenwich."""
        jd = jd_now()
        
        # Polaris should always be visible from 51.5°N
        polaris = famous_stars.get('polaris')
        if polaris:
            # Check throughout the day
            for hour in range(0, 24, 6):
                test_jd = JulianDate(jd.jd + hour/24)
                alt = target_altitude(polaris, greenwich, test_jd)
                # Should always be above horizon
                assert alt.degrees > 0


# ═══════════════════════════════════════════════════════════════════════════════
#  COORDINATE SYSTEM CHAIN
# ═══════════════════════════════════════════════════════════════════════════════

class TestCoordinateChain:
    """
    Tests for coordinate system transformations in workflows.
    """
    
    def test_icrs_to_horizontal_via_observer(self, greenwich):
        """Test ICRS → Horizontal transformation chain."""
        target = ICRSCoord.from_degrees(180.0, 45.0)
        jd = jd_now()
        
        # Get altitude and azimuth
        alt = target_altitude(target, greenwich, jd)
        az = target_azimuth(target, greenwich, jd)
        
        # Both should be valid
        assert -90 <= alt.degrees <= 90
        assert 0 <= az.degrees < 360
        
        # Airmass should be calculable
        X = airmass(alt)
        if alt.degrees > 0:
            assert X >= 1.0
        else:
            assert X == float('inf')
