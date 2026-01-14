"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        INTEGRATION TESTS                                     ║
║                                                                              ║
║  Tests for cross-module functionality and end-to-end workflows.              ║
║  Where the celestial machinery comes together.                               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import allure
import pytest

from starward.core.angles import Angle
from starward.core.coords import ICRSCoord
from starward.core.time import JulianDate, jd_now
from starward.core.observer import Observer
from starward.core.sun import sun_position, sunrise, sunset, solar_noon, solar_altitude
from starward.core.moon import moon_position, moon_phase, MoonPhase
from starward.core.visibility import (
    airmass, target_altitude, target_azimuth,
    transit_time, compute_visibility
)


# ═══════════════════════════════════════════════════════════════════════════════
#  VISIBILITY WORKFLOW
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Visibility Calculations")
class TestVisibilityWorkflow:
    """
    Tests for complete visibility calculation workflows.
    """

    @allure.title("Complete visibility calculation for M31")
    @allure.description("""
    Tests the full visibility calculation workflow for a deep sky target (M31).
    Validates that all visibility metrics are computed correctly.
    """)
    def test_full_visibility_calculation(self, greenwich):
        """Test complete visibility calculation for a target."""
        with allure.step("Parse M31 coordinates: 00h42m44s +41d16m09s"):
            target = ICRSCoord.parse("00h42m44s +41d16m09s")

        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Compute full visibility"):
            vis = compute_visibility(target, greenwich, jd)

        with allure.step(f"Current altitude: {vis.current_altitude.degrees:.2f}°"):
            pass

        with allure.step(f"Moon separation: {vis.moon_separation.degrees:.2f}°"):
            pass

        with allure.step("Validate visibility results"):
            assert vis.target == target
            assert vis.observer == greenwich
            assert isinstance(vis.current_altitude, Angle)
            assert isinstance(vis.transit_time, JulianDate)
            assert isinstance(vis.moon_separation, Angle)

    @allure.title("Observation planning workflow for Vega")
    @allure.description("""
    Simulates a typical observation planning workflow:
    1. Get current altitude of target
    2. Calculate transit time
    3. Compute airmass at transit
    4. Verify transit provides optimal viewing
    """)
    def test_observation_planning_workflow(self, greenwich):
        """Test a typical observation planning workflow."""
        with allure.step("Parse Vega coordinates: 18h36m56.3s +38d47m01s"):
            target = ICRSCoord.parse("18h36m56.3s +38d47m01s")

        with allure.step("Get current time"):
            jd = jd_now()

        with allure.step("Calculate current altitude"):
            alt = target_altitude(target, greenwich, jd)
            assert isinstance(alt, Angle)

        with allure.step(f"Current altitude = {alt.degrees:.2f}°"):
            pass

        with allure.step("Calculate transit time"):
            transit = transit_time(target, greenwich, jd)
            assert isinstance(transit, JulianDate)

        with allure.step(f"Transit JD = {transit.jd:.4f}"):
            pass

        with allure.step("Calculate altitude at transit"):
            alt_at_transit = target_altitude(target, greenwich, transit)

        with allure.step(f"Transit altitude = {alt_at_transit.degrees:.2f}°"):
            pass

        with allure.step("Calculate airmass at transit"):
            X = airmass(alt_at_transit)

        with allure.step(f"Transit airmass = {X:.3f}" if X != float('inf') else "Transit airmass = ∞"):
            pass

        with allure.step("Verify transit has optimal airmass"):
            if alt.degrees > 0:
                X_now = airmass(alt)
                with allure.step(f"Current airmass = {X_now:.3f}" if X_now != float('inf') else "Current airmass = ∞"):
                    pass
                assert X <= X_now or X_now == float('inf'), (
                    f"Transit airmass {X} should be ≤ current {X_now}"
                )


# ═══════════════════════════════════════════════════════════════════════════════
#  SUN-MOON RELATIONSHIP
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Sun-Moon Relationships")
class TestSunMoonRelationship:
    """
    Tests for Sun-Moon relationships and phase correlation.
    """

    @allure.title("Sun-Moon elongation correlates with lunar phase")
    @allure.description("""
    Verifies that Sun-Moon angular separation (elongation) correlates with phase:
    - New moon: elongation < 45° (Moon near Sun)
    - Full moon: elongation > 135° (Moon opposite Sun)
    """)
    def test_sun_moon_separation_correlates_with_phase(self):
        """Test that Sun-Moon separation varies with phase."""
        from starward.core.angles import angular_separation

        with allure.step("Define test dates: New moon 2024-01-11, Full moon 2024-01-25"):
            new_moon_jd = JulianDate(2460320.5)
            full_moon_jd = JulianDate(2460334.5)

        with allure.step("Calculate Sun/Moon positions at new moon"):
            sun_new = sun_position(new_moon_jd)
            moon_new = moon_position(new_moon_jd)

        with allure.step(f"Sun RA = {sun_new.ra.degrees:.2f}°, Moon RA = {moon_new.ra.degrees:.2f}°"):
            pass

        with allure.step("Calculate elongation at new moon"):
            elongation_new = angular_separation(
                sun_new.ra, sun_new.dec,
                moon_new.ra, moon_new.dec
            )

        with allure.step(f"New moon elongation = {elongation_new.degrees:.1f}°"):
            pass

        with allure.step("Verify new moon elongation < 45°"):
            assert elongation_new.degrees < 45, (
                f"New moon elongation {elongation_new.degrees}° should be < 45°"
            )

        with allure.step("Calculate Sun/Moon positions at full moon"):
            sun_full = sun_position(full_moon_jd)
            moon_full = moon_position(full_moon_jd)

        with allure.step(f"Sun RA = {sun_full.ra.degrees:.2f}°, Moon RA = {moon_full.ra.degrees:.2f}°"):
            pass

        with allure.step("Calculate elongation at full moon"):
            elongation_full = angular_separation(
                sun_full.ra, sun_full.dec,
                moon_full.ra, moon_full.dec
            )

        with allure.step(f"Full moon elongation = {elongation_full.degrees:.1f}°"):
            pass

        with allure.step("Verify full moon elongation > 135°"):
            assert elongation_full.degrees > 135, (
                f"Full moon elongation {elongation_full.degrees}° should be > 135°"
            )


# ═══════════════════════════════════════════════════════════════════════════════
#  SOLAR DAY WORKFLOW
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Solar Day Calculations")
class TestSolarDayWorkflow:
    """
    Tests for complete solar day calculations.
    """

    @allure.title("Solar day timeline: sunrise → noon → sunset")
    @allure.description("""
    Verifies the temporal sequence of solar events:
    1. Sunrise occurs before solar noon
    2. Solar noon occurs before sunset
    3. Solar altitude is highest at noon
    """)
    def test_solar_day_timeline(self, greenwich):
        """Test sunrise → noon → sunset sequence."""
        with allure.step("Set test date: JD 2460325.5 (winter day)"):
            jd = JulianDate(2460325.5)

        with allure.step("Calculate sunrise"):
            rise = sunrise(greenwich, jd)

        with allure.step("Calculate solar noon"):
            noon = solar_noon(greenwich, jd)

        with allure.step("Calculate sunset"):
            set_t = sunset(greenwich, jd)

        if rise and noon and set_t:
            with allure.step(f"Sunrise JD = {rise.jd:.4f}"):
                pass

            with allure.step(f"Solar noon JD = {noon.jd:.4f}"):
                pass

            with allure.step(f"Sunset JD = {set_t.jd:.4f}"):
                pass

            with allure.step("Verify temporal sequence: rise < noon < set"):
                assert rise.jd < noon.jd < set_t.jd

            with allure.step("Calculate altitudes at each event"):
                alt_rise = solar_altitude(greenwich, rise)
                alt_noon = solar_altitude(greenwich, noon)
                alt_set = solar_altitude(greenwich, set_t)

            with allure.step(f"Altitude at sunrise = {alt_rise.degrees:.2f}°"):
                pass

            with allure.step(f"Altitude at noon = {alt_noon.degrees:.2f}°"):
                pass

            with allure.step(f"Altitude at sunset = {alt_set.degrees:.2f}°"):
                pass

            with allure.step("Verify noon has highest altitude"):
                assert alt_noon.degrees > alt_rise.degrees, (
                    f"Noon altitude {alt_noon.degrees}° should > sunrise {alt_rise.degrees}°"
                )
                assert alt_noon.degrees > alt_set.degrees, (
                    f"Noon altitude {alt_noon.degrees}° should > sunset {alt_set.degrees}°"
                )

    @allure.title("Seasonal day length variation")
    @allure.description("""
    Verifies that day length varies with season in northern hemisphere:
    Summer days should be longer than winter days at Greenwich (51.5°N).
    """)
    def test_seasonal_day_length_variation(self, greenwich):
        """Test that day length varies with season."""
        with allure.step("Define seasonal test dates"):
            winter = JulianDate(2460325.5)  # January
            summer = JulianDate(2460483.5)  # June

        with allure.step("Calculate winter sunrise/sunset"):
            rise_w = sunrise(greenwich, winter)
            set_w = sunset(greenwich, winter)

        with allure.step("Calculate summer sunrise/sunset"):
            rise_s = sunrise(greenwich, summer)
            set_s = sunset(greenwich, summer)

        if all([rise_w, set_w, rise_s, set_s]):
            with allure.step("Calculate day lengths"):
                winter_day = (set_w.jd - rise_w.jd) * 24
                summer_day = (set_s.jd - rise_s.jd) * 24

            with allure.step(f"Winter day length = {winter_day:.2f} hours"):
                pass

            with allure.step(f"Summer day length = {summer_day:.2f} hours"):
                pass

            with allure.step("Verify summer days are longer"):
                assert summer_day > winter_day, (
                    f"Summer day ({summer_day:.1f}h) should > winter ({winter_day:.1f}h)"
                )


# ═══════════════════════════════════════════════════════════════════════════════
#  MULTI-TARGET COMPARISON
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Multi-Target Comparisons")
class TestMultiTargetComparison:
    """
    Tests for comparing visibility of multiple targets.
    """

    @allure.title("Compare altitudes of famous stars")
    @allure.description("""
    Calculates and compares the current altitude of multiple famous stars
    from Greenwich observatory.
    """)
    def test_compare_target_altitudes(self, greenwich, famous_stars):
        """Compare altitudes of multiple targets."""
        with allure.step("Get current time"):
            jd = jd_now()

        altitudes = {}
        for name, coord in famous_stars.items():
            alt = target_altitude(coord, greenwich, jd)
            altitudes[name] = alt.degrees
            with allure.step(f"{name.capitalize()} altitude = {alt.degrees:.2f}°"):
                pass

        with allure.step("Verify all altitudes are valid (-90° to +90°)"):
            for name, alt in altitudes.items():
                assert -90 <= alt <= 90, f"{name} altitude {alt}° out of range"

    @allure.title("Polaris circumpolar from Greenwich")
    @allure.description("""
    Verifies that Polaris (near celestial north pole) is circumpolar
    from Greenwich (51.5°N) - always above the horizon throughout the day.
    """)
    def test_circumpolar_vs_rising_setting(self, greenwich, famous_stars):
        """Test that Polaris is always up from Greenwich."""
        with allure.step("Get base Julian Date"):
            jd = jd_now()

        polaris = famous_stars.get('polaris')
        if polaris:
            with allure.step(f"Polaris coordinates: RA={polaris.ra.degrees:.2f}°, Dec={polaris.dec.degrees:.2f}°"):
                pass

            with allure.step("Check altitude throughout 24 hours"):
                for hour in range(0, 24, 6):
                    test_jd = JulianDate(jd.jd + hour / 24)
                    alt = target_altitude(polaris, greenwich, test_jd)
                    with allure.step(f"+{hour}h: altitude = {alt.degrees:.2f}°"):
                        assert alt.degrees > 0, (
                            f"Polaris should be above horizon at +{hour}h, got {alt.degrees}°"
                        )


# ═══════════════════════════════════════════════════════════════════════════════
#  COORDINATE SYSTEM CHAIN
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Coordinate Transformations")
class TestCoordinateChain:
    """
    Tests for coordinate system transformations in workflows.
    """

    @allure.title("ICRS to Horizontal transformation chain")
    @allure.description("""
    Tests the complete transformation chain from ICRS (celestial) coordinates
    to horizontal (alt-az) coordinates via an observer location.
    Also validates airmass calculation based on altitude.
    """)
    def test_icrs_to_horizontal_via_observer(self, greenwich):
        """Test ICRS → Horizontal transformation chain."""
        with allure.step("Define ICRS target: RA=180.0°, Dec=45.0°"):
            target = ICRSCoord.from_degrees(180.0, 45.0)

        with allure.step("Get current time"):
            jd = jd_now()

        with allure.step("Transform to altitude"):
            alt = target_altitude(target, greenwich, jd)

        with allure.step(f"Altitude = {alt.degrees:.2f}°"):
            assert -90 <= alt.degrees <= 90

        with allure.step("Transform to azimuth"):
            az = target_azimuth(target, greenwich, jd)

        with allure.step(f"Azimuth = {az.degrees:.2f}°"):
            assert 0 <= az.degrees < 360

        with allure.step("Calculate airmass"):
            X = airmass(alt)

        if alt.degrees > 0:
            with allure.step(f"Airmass = {X:.3f} (target above horizon)"):
                assert X >= 1.0, f"Airmass should be ≥ 1.0 above horizon, got {X}"
        else:
            with allure.step("Airmass = ∞ (target below horizon)"):
                assert X == float('inf'), f"Airmass should be inf below horizon, got {X}"
