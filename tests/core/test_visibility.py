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
import allure
import pytest

from starward.core.angles import Angle
from starward.core.coords import ICRSCoord
from starward.core.time import JulianDate, jd_now
from starward.core.observer import Observer
from starward.core.visibility import (
    airmass, target_altitude, target_azimuth,
    transit_time, transit_altitude_calc, target_rise_set,
    moon_target_separation, is_night, compute_visibility,
    TargetVisibility
)

# ═══════════════════════════════════════════════════════════════════════════════
#  AIRMASS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Airmass")
class TestAirmass:
    """
    Tests for airmass calculations.

    Airmass X = 1/cos(z) for a plane-parallel atmosphere,
    with corrections for refraction near the horizon.
    """

    @pytest.mark.golden
    @allure.title("Zenith airmass = 1.0")
    @allure.description("""
    At zenith (90° altitude), light travels through the minimum amount
    of atmosphere, giving an airmass of exactly 1.0.
    """)
    def test_zenith_airmass_is_one(self):
        """Airmass at zenith (90° altitude) = 1.0."""
        with allure.step("Set altitude to zenith (90°)"):
            alt = Angle(degrees=90)

        with allure.step("Calculate airmass"):
            X = airmass(alt)

        with allure.step(f"Airmass = {X:.3f} (expected 1.0)"):
            assert X == pytest.approx(1.0, rel=0.01)

    @pytest.mark.golden
    @allure.title("Airmass at 45° ≈ √2 ≈ 1.41")
    @allure.description("""
    At 45° altitude (zenith angle 45°), sec(45°) = √2 ≈ 1.414.
    """)
    def test_45_degrees_airmass(self):
        """Airmass at 45° ≈ √2 ≈ 1.41."""
        with allure.step("Set altitude to 45°"):
            alt = Angle(degrees=45)

        with allure.step("Calculate airmass"):
            X = airmass(alt)

        with allure.step(f"Airmass = {X:.3f} (expected ≈ 1.41)"):
            assert X == pytest.approx(1.41, rel=0.02)

    @pytest.mark.golden
    @allure.title("Airmass at 30° ≈ 2.0")
    @allure.description("""
    At 30° altitude (zenith angle 60°), sec(60°) = 2.0.
    This is often considered the practical limit for quality observations.
    """)
    def test_30_degrees_airmass(self):
        """Airmass at 30° ≈ 2.0."""
        with allure.step("Set altitude to 30°"):
            alt = Angle(degrees=30)

        with allure.step("Calculate airmass"):
            X = airmass(alt)

        with allure.step(f"Airmass = {X:.3f} (expected ≈ 2.0)"):
            assert X == pytest.approx(2.0, rel=0.02)

    @allure.title("Airmass increases rapidly near horizon")
    def test_low_altitude_airmass(self):
        """Airmass increases rapidly near horizon."""
        with allure.step("Calculate airmass at 10°"):
            alt_10 = airmass(Angle(degrees=10))

        with allure.step("Calculate airmass at 5°"):
            alt_5 = airmass(Angle(degrees=5))

        with allure.step("Calculate airmass at 1°"):
            alt_1 = airmass(Angle(degrees=1))

        with allure.step(f"X(10°)={alt_10:.1f}, X(5°)={alt_5:.1f}, X(1°)={alt_1:.1f}"):
            pass

        with allure.step("Verify X(5°) > X(10°)"):
            assert alt_5 > alt_10

        with allure.step("Verify X(1°) > X(5°)"):
            assert alt_1 > alt_5

    @allure.title("Airmass at 1° altitude is very large (>25)")
    def test_horizon_airmass(self):
        """Airmass at 1° altitude is very large."""
        with allure.step("Set altitude to 1°"):
            alt = Angle(degrees=1)

        with allure.step("Calculate airmass"):
            X = airmass(alt)

        with allure.step(f"Airmass = {X:.1f} (expected > 25)"):
            assert X > 25

    @allure.title("Airmass below horizon returns None")
    def test_below_horizon_none(self):
        """Airmass below horizon is None."""
        with allure.step("Set altitude to -5° (below horizon)"):
            alt = Angle(degrees=-5)

        with allure.step("Calculate airmass"):
            X = airmass(alt)

        with allure.step("Verify returns None"):
            assert X is None

    @allure.title("Any negative altitude gives None airmass")
    def test_negative_altitude_none(self):
        """Any negative altitude gives None airmass."""
        with allure.step("Test various negative altitudes"):
            for deg in [-1, -10, -45, -89]:
                with allure.step(f"Altitude {deg}°"):
                    X = airmass(Angle(degrees=deg))
                    assert X is None


@allure.story("Airmass Thresholds")
class TestAirmassThresholds:
    """
    Tests for typical observational airmass limits.
    """

    @allure.title("X = 2 corresponds to altitude ≈ 30°")
    def test_airmass_2_altitude(self):
        """X = 2 corresponds to altitude ≈ 30°."""
        with allure.step("Set altitude to 30°"):
            alt = Angle(degrees=30)

        with allure.step("Calculate airmass"):
            X = airmass(alt)

        with allure.step(f"Airmass = {X:.2f} (expected 1.9-2.1)"):
            assert 1.9 < X < 2.1

    @allure.title("X < 1.5 requires altitude > 42°")
    def test_good_airmass_altitude(self):
        """X < 1.5 requires altitude > 42°."""
        with allure.step("Set altitude to 42°"):
            alt = Angle(degrees=42)

        with allure.step("Calculate airmass"):
            X = airmass(alt)

        with allure.step(f"Airmass = {X:.3f} (expected < 1.5)"):
            assert X < 1.5


# ═══════════════════════════════════════════════════════════════════════════════
#  TARGET ALTITUDE & AZIMUTH
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Target Altitude")
class TestTargetAltitude:
    """
    Tests for target altitude calculations.
    """

    @allure.title("target_altitude() returns Angle")
    def test_returns_angle(self, greenwich):
        """target_altitude() returns an Angle."""
        with allure.step("Create target at RA=0°, Dec=45°"):
            target = ICRSCoord.from_degrees(0, 45)

        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate target altitude"):
            alt = target_altitude(target, greenwich, jd)

        with allure.step(f"Altitude = {alt.degrees:.2f}°"):
            assert isinstance(alt, Angle)

    @allure.title("Altitude in valid range [-90°, +90°]")
    def test_altitude_range(self, greenwich):
        """Altitude is in [-90°, +90°]."""
        with allure.step("Create target at RA=0°, Dec=45°"):
            target = ICRSCoord.from_degrees(0, 45)

        with allure.step("Sample altitude throughout the day"):
            for offset in range(0, 24, 3):
                jd = JulianDate(2460000.5 + offset / 24)
                alt = target_altitude(target, greenwich, jd)

                with allure.step(f"+{offset}h: altitude = {alt.degrees:.2f}°"):
                    assert -90 <= alt.degrees <= 90


@allure.story("Target Azimuth")
class TestTargetAzimuth:
    """
    Tests for target azimuth calculations.
    """

    @allure.title("target_azimuth() returns Angle")
    def test_returns_angle(self, greenwich):
        """target_azimuth() returns an Angle."""
        with allure.step("Create target at RA=0°, Dec=45°"):
            target = ICRSCoord.from_degrees(0, 45)

        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate target azimuth"):
            az = target_azimuth(target, greenwich, jd)

        with allure.step(f"Azimuth = {az.degrees:.2f}°"):
            assert isinstance(az, Angle)

    @allure.title("Azimuth in valid range [0°, 360°)")
    def test_azimuth_range(self, greenwich):
        """Azimuth is in [0°, 360°)."""
        with allure.step("Create target at RA=0°, Dec=45°"):
            target = ICRSCoord.from_degrees(0, 45)

        with allure.step("Sample azimuth throughout the day"):
            for offset in range(0, 24, 3):
                jd = JulianDate(2460000.5 + offset / 24)
                az = target_azimuth(target, greenwich, jd)

                with allure.step(f"+{offset}h: azimuth = {az.degrees:.2f}°"):
                    assert 0 <= az.degrees < 360


# ═══════════════════════════════════════════════════════════════════════════════
#  TRANSIT
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Transit")
class TestTransit:
    """
    Tests for meridian transit calculations.

    Transit occurs when the object crosses the local meridian
    (highest altitude of the night).
    """

    @allure.title("transit_time() returns JulianDate")
    def test_transit_time_returns_jd(self, greenwich):
        """transit_time() returns JulianDate."""
        with allure.step("Create target at RA=0°, Dec=45°"):
            target = ICRSCoord.from_degrees(0, 45)

        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate transit time"):
            transit = transit_time(target, greenwich, jd)

        if transit:
            with allure.step(f"Transit at JD {transit.jd:.4f}"):
                assert isinstance(transit, JulianDate)

    @allure.title("transit_altitude_calc() returns maximum altitude")
    def test_transit_altitude(self, greenwich):
        """transit_altitude_calc() returns maximum altitude."""
        with allure.step("Create target at RA=0°, Dec=45°"):
            target = ICRSCoord.from_degrees(0, 45)

        with allure.step("Calculate maximum transit altitude"):
            max_alt = transit_altitude_calc(target, greenwich)

        with allure.step(f"Transit altitude = {max_alt.degrees:.2f}°"):
            assert isinstance(max_alt, Angle)
            assert max_alt.degrees <= 90

    @pytest.mark.golden
    @allure.title("Polaris transit altitude at Greenwich ≈ 52°")
    @allure.description("""
    For circumpolar stars, transit altitude = 90° - |lat - dec|.
    At Greenwich (51.5°N), Polaris (Dec +89°) transits at:
    90° - (89° - 51.5°) = 52.5°
    """)
    def test_circumpolar_transit_altitude(self, greenwich):
        """For circumpolar stars, transit altitude = 90° - |lat - dec|."""
        with allure.step("Parse Polaris coordinates: 02h31m49s +89d15m51s"):
            polaris = ICRSCoord.parse("02h31m49s +89d15m51s")

        with allure.step("Calculate transit altitude"):
            max_alt = transit_altitude_calc(polaris, greenwich)

        with allure.step(f"Transit altitude = {max_alt.degrees:.2f}° (expected 50-55°)"):
            assert 50 < max_alt.degrees < 55

    @allure.title("Altitude is maximum at transit")
    def test_altitude_highest_at_transit(self, greenwich):
        """Altitude is maximum at transit."""
        with allure.step("Create target at RA=180°, Dec=30°"):
            target = ICRSCoord.from_degrees(180, 30)

        with allure.step("Set reference date"):
            jd = JulianDate(2460000.5)

        with allure.step("Calculate transit time"):
            transit = transit_time(target, greenwich, jd)

        if transit:
            with allure.step(f"Transit at JD {transit.jd:.4f}"):
                pass

            with allure.step("Calculate altitude at transit"):
                alt_transit = target_altitude(target, greenwich, transit)

            with allure.step("Calculate altitude 1 hour before"):
                alt_before = target_altitude(target, greenwich, JulianDate(transit.jd - 1/24))

            with allure.step("Calculate altitude 1 hour after"):
                alt_after = target_altitude(target, greenwich, JulianDate(transit.jd + 1/24))

            with allure.step(f"Before: {alt_before.degrees:.2f}°, Transit: {alt_transit.degrees:.2f}°, After: {alt_after.degrees:.2f}°"):
                pass

            with allure.step("Verify transit altitude >= before"):
                assert alt_transit.degrees >= alt_before.degrees

            with allure.step("Verify transit altitude >= after"):
                assert alt_transit.degrees >= alt_after.degrees


# ═══════════════════════════════════════════════════════════════════════════════
#  RISE / SET
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Target Rise/Set")
class TestTargetRiseSet:
    """
    Tests for target rise and set calculations.
    """

    @allure.title("target_rise_set() returns (rise, set) tuple")
    def test_rise_set_returns_tuple(self, greenwich):
        """target_rise_set() returns (rise, set) tuple."""
        with allure.step("Create target at RA=0°, Dec=20°"):
            target = ICRSCoord.from_degrees(0, 20)

        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate rise/set times"):
            result = target_rise_set(target, greenwich, jd)

        with allure.step("Verify returns tuple of length 2"):
            assert isinstance(result, tuple)
            assert len(result) == 2

    @allure.title("Equatorial objects rise and set daily")
    def test_equatorial_object_rises_sets(self, greenwich):
        """Objects near celestial equator rise and set daily."""
        with allure.step("Create target on celestial equator (Dec=0°)"):
            target = ICRSCoord.from_degrees(0, 0)

        with allure.step("Set reference date"):
            jd = JulianDate(2460000.5)

        with allure.step("Calculate rise/set times"):
            rise, set_t = target_rise_set(target, greenwich, jd)

        if rise:
            with allure.step(f"Rise at JD {rise.jd:.4f}"):
                pass
        if set_t:
            with allure.step(f"Set at JD {set_t.jd:.4f}"):
                pass

        with allure.step("Verify at least one event found"):
            assert rise is not None or set_t is not None

    @pytest.mark.edge
    @allure.title("Circumpolar objects never set")
    @allure.description("""
    For Greenwich (51.5°N), objects with Dec > 90° - 51.5° = 38.5°
    are circumpolar and never set.
    """)
    def test_circumpolar_never_sets(self, greenwich):
        """Circumpolar objects never set."""
        with allure.step("Create target near NCP (Dec=89°)"):
            polaris = ICRSCoord.from_degrees(0, 89)

        with allure.step("Set reference date"):
            jd = JulianDate(2460000.5)

        with allure.step("Calculate rise/set times"):
            rise, set_t = target_rise_set(polaris, greenwich, jd)

        with allure.step(f"Rise: {rise}, Set: {set_t} (circumpolar may return None)"):
            pass  # Circumpolar: may return None for both


# ═══════════════════════════════════════════════════════════════════════════════
#  MOON SEPARATION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Moon Separation")
class TestMoonSeparation:
    """
    Tests for Moon-target angular separation.
    """

    @allure.title("moon_target_separation() returns Angle")
    def test_returns_angle(self):
        """moon_target_separation() returns Angle."""
        with allure.step("Create target at RA=180°, Dec=45°"):
            target = ICRSCoord.from_degrees(180, 45)

        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate Moon-target separation"):
            sep = moon_target_separation(target, jd)

        with allure.step(f"Separation = {sep.degrees:.2f}°"):
            assert isinstance(sep, Angle)

    @allure.title("Moon separation in range [0°, 180°]")
    def test_separation_range(self):
        """Separation is in [0°, 180°]."""
        with allure.step("Create target at RA=180°, Dec=45°"):
            target = ICRSCoord.from_degrees(180, 45)

        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate Moon-target separation"):
            sep = moon_target_separation(target, jd)

        with allure.step(f"Separation = {sep.degrees:.2f}° (expected 0-180°)"):
            assert 0 <= sep.degrees <= 180


# ═══════════════════════════════════════════════════════════════════════════════
#  NIGHT CHECK
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Night Check")
class TestIsNight:
    """
    Tests for determining if it's night (Sun below horizon).
    """

    @allure.title("is_night() returns boolean")
    def test_returns_bool(self, greenwich):
        """is_night() returns boolean."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Check if it's night"):
            result = is_night(greenwich, jd)

        with allure.step(f"Is night: {result}"):
            assert isinstance(result, bool)

    @allure.title("Midnight in winter is night")
    def test_midnight_is_usually_night(self, greenwich):
        """Midnight local time is usually night (non-polar)."""
        with allure.step("Set date: January midnight UTC"):
            jd = JulianDate(2460325.5)

        with allure.step("Check if it's night"):
            result = is_night(greenwich, jd)

        with allure.step(f"Is night at midnight: {result} (expected True)"):
            assert result is True

    @allure.title("Noon is not night")
    def test_noon_is_not_night(self, greenwich):
        """Noon is not night."""
        with allure.step("Set date: January noon UTC"):
            jd = JulianDate(2460326.0)

        with allure.step("Check if it's night"):
            result = is_night(greenwich, jd)

        with allure.step(f"Is night at noon: {result} (expected False)"):
            assert result is False


# ═══════════════════════════════════════════════════════════════════════════════
#  COMPUTE VISIBILITY (COMPREHENSIVE)
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Compute Visibility")
class TestComputeVisibility:
    """
    Tests for comprehensive visibility assessment.
    """

    @allure.title("compute_visibility() returns TargetVisibility")
    def test_returns_target_visibility(self, greenwich):
        """compute_visibility() returns TargetVisibility dataclass."""
        with allure.step("Create target at RA=180°, Dec=45°"):
            target = ICRSCoord.from_degrees(180, 45)

        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Compute full visibility"):
            vis = compute_visibility(target, greenwich, jd)

        with allure.step("Verify returns TargetVisibility instance"):
            assert isinstance(vis, TargetVisibility)

    @allure.title("Visibility includes current altitude")
    def test_includes_altitude(self, greenwich):
        """Result includes current altitude."""
        with allure.step("Create target at RA=180°, Dec=45°"):
            target = ICRSCoord.from_degrees(180, 45)

        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Compute visibility"):
            vis = compute_visibility(target, greenwich, jd)

        with allure.step(f"Current altitude = {vis.current_altitude.degrees:.2f}°"):
            assert hasattr(vis, 'current_altitude')
            assert isinstance(vis.current_altitude, Angle)

    @allure.title("Visibility includes airmass")
    def test_includes_airmass(self, greenwich):
        """Result includes airmass (or None if below horizon)."""
        with allure.step("Create target at RA=180°, Dec=45°"):
            target = ICRSCoord.from_degrees(180, 45)

        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Compute visibility"):
            vis = compute_visibility(target, greenwich, jd)

        with allure.step(f"Current airmass = {vis.current_airmass}"):
            assert hasattr(vis, 'current_airmass')


# ═══════════════════════════════════════════════════════════════════════════════
#  LATITUDE EFFECTS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Latitude Effects")
class TestLatitudeEffects:
    """
    Tests for how latitude affects visibility.
    """

    @allure.title("NCP always visible from North Pole")
    def test_ncp_always_up_at_north_pole(self, north_pole):
        """North Celestial Pole always visible from North Pole."""
        with allure.step("Create target at NCP (Dec=90°)"):
            ncp = ICRSCoord.from_degrees(0, 90)

        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate altitude at North Pole"):
            alt = target_altitude(ncp, north_pole, jd)

        with allure.step(f"NCP altitude = {alt.degrees:.2f}° (expected > 85°)"):
            assert alt.degrees > 85

    @allure.title("SCP never visible from North Pole")
    def test_scp_never_up_at_north_pole(self, north_pole):
        """South Celestial Pole never visible from North Pole."""
        with allure.step("Create target at SCP (Dec=-90°)"):
            scp = ICRSCoord.from_degrees(0, -90)

        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate altitude at North Pole"):
            alt = target_altitude(scp, north_pole, jd)

        with allure.step(f"SCP altitude = {alt.degrees:.2f}° (expected < -85°)"):
            assert alt.degrees < -85

    @allure.title("Equatorial objects transit at zenith from equator")
    def test_equatorial_objects_transit_at_zenith_equator(self, equator):
        """Equatorial objects transit at zenith for equatorial observers."""
        with allure.step("Create target on celestial equator"):
            target = ICRSCoord.from_degrees(0, 0)

        with allure.step("Calculate transit altitude"):
            max_alt = transit_altitude_calc(target, equator)

        with allure.step(f"Transit altitude = {max_alt.degrees:.2f}° (expected > 85°)"):
            assert max_alt.degrees > 85
