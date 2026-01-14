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
import allure
import pytest

from starward.core.angles import Angle
from starward.core.time import JulianDate, jd_now
from starward.core.observer import Observer
from starward.core.moon import (
    moon_position, moon_phase, moon_altitude,
    moonrise, moonset, next_phase,
    MoonPhase, MoonPosition, MoonPhaseInfo
)


# ═══════════════════════════════════════════════════════════════════════════════
#  MOON POSITION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Moon Position")
class TestMoonPosition:
    """
    Tests for lunar position calculations.

    Uses simplified lunar theory suitable for rise/set
    and phase calculations (accuracy ~0.5° in position).
    """

    @allure.title("moon_position() returns MoonPosition object")
    def test_returns_moon_position_object(self):
        """moon_position() returns MoonPosition dataclass."""
        with allure.step("Calculate moon position at J2000.0"):
            jd = JulianDate(2451545.0)
            pos = moon_position(jd)

        with allure.step("Verify returns MoonPosition instance"):
            assert isinstance(pos, MoonPosition)

    @allure.title("MoonPosition has all required fields")
    def test_has_required_fields(self):
        """MoonPosition has all required fields."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate moon position"):
            pos = moon_position(jd)

        with allure.step("Verify longitude field exists"):
            assert hasattr(pos, 'longitude')

        with allure.step("Verify latitude field exists"):
            assert hasattr(pos, 'latitude')

        with allure.step("Verify ra field exists"):
            assert hasattr(pos, 'ra')

        with allure.step("Verify dec field exists"):
            assert hasattr(pos, 'dec')

        with allure.step("Verify distance_km field exists"):
            assert hasattr(pos, 'distance_km')

        with allure.step("Verify angular_diameter field exists"):
            assert hasattr(pos, 'angular_diameter')

        with allure.step("Verify parallax field exists"):
            assert hasattr(pos, 'parallax')

    @allure.title("Moon distance within perigee-apogee bounds")
    @allure.description("""
    Moon distance varies from perigee to apogee:
      - Perigee: ~356,500 km
      - Apogee: ~406,700 km
    """)
    def test_distance_within_bounds(self):
        """Moon distance varies from perigee to apogee."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate moon position"):
            pos = moon_position(jd)

        with allure.step(f"Distance = {pos.distance_km:.0f} km (expected 350,000-410,000)"):
            assert 350000 < pos.distance_km < 410000

    @allure.title("Moon angular diameter varies with distance")
    @allure.description("""
    Moon angular diameter varies with distance:
      - At apogee: ~29.4'
      - At perigee: ~33.5'
    """)
    def test_angular_diameter_reasonable(self):
        """Moon angular diameter varies with distance."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate moon position"):
            pos = moon_position(jd)

        with allure.step("Convert angular diameter to arcminutes"):
            ang_arcmin = pos.angular_diameter.degrees * 60

        with allure.step(f"Angular diameter = {ang_arcmin:.1f}' (expected 29-34')"):
            assert 29 < ang_arcmin < 34

    @allure.title("Moon ecliptic latitude within orbital inclination")
    def test_ecliptic_latitude_limited(self):
        """Moon's orbit is inclined ~5.14° to ecliptic."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate moon position"):
            pos = moon_position(jd)

        with allure.step(f"Ecliptic latitude = {pos.latitude.degrees:.2f}° (expected < 5.5°)"):
            assert abs(pos.latitude.degrees) < 5.5

    @allure.title("Moon horizontal parallax reasonable")
    def test_parallax_reasonable(self):
        """Moon's horizontal parallax is ~0.9° to ~1.0°."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate moon position"):
            pos = moon_position(jd)

        with allure.step(f"Parallax = {pos.parallax.degrees:.3f}° (expected 0.85-1.05°)"):
            assert 0.85 < pos.parallax.degrees < 1.05


# ═══════════════════════════════════════════════════════════════════════════════
#  MOON PHASE
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Moon Phase")
class TestMoonPhase:
    """
    Tests for moon phase calculations.
    """

    @allure.title("moon_phase() returns MoonPhaseInfo")
    def test_returns_moon_phase_info(self):
        """moon_phase() returns MoonPhaseInfo."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate moon phase"):
            phase = moon_phase(jd)

        with allure.step("Verify returns MoonPhaseInfo instance"):
            assert isinstance(phase, MoonPhaseInfo)

    @allure.title("Moon illumination in valid range [0, 1]")
    def test_illumination_range(self):
        """Illumination is in [0, 1]."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate moon phase"):
            phase = moon_phase(jd)

        with allure.step(f"Illumination = {phase.illumination:.3f} (expected 0-1)"):
            assert 0 <= phase.illumination <= 1

        with allure.step(f"Percent illuminated = {phase.percent_illuminated:.1f}% (expected 0-100%)"):
            assert 0 <= phase.percent_illuminated <= 100

    @allure.title("Phase angle in valid range [0, 360]")
    def test_phase_angle_range(self):
        """Phase angle is in [0, 360]."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate moon phase"):
            phase = moon_phase(jd)

        with allure.step(f"Phase angle = {phase.phase_angle:.1f}° (expected 0-360°)"):
            assert 0 <= phase.phase_angle <= 360

    @allure.title("Moon age in valid range [0, 29.5] days")
    def test_moon_age_range(self):
        """Moon age is in [0, 29.5] days (synodic month)."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate moon phase"):
            phase = moon_phase(jd)

        with allure.step(f"Moon age = {phase.age_days:.1f} days (expected 0-30)"):
            assert 0 <= phase.age_days < 30

    @allure.title("Moon phase has human-readable name")
    def test_has_phase_name(self):
        """Phase has a human-readable name."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate moon phase"):
            phase = moon_phase(jd)

        with allure.step("Define valid phase names"):
            valid_names = [
                'New Moon', 'Waxing Crescent', 'First Quarter', 'Waxing Gibbous',
                'Full Moon', 'Waning Gibbous', 'Last Quarter', 'Waning Crescent'
            ]

        with allure.step(f"Phase name = '{phase.phase_name.value}'"):
            assert phase.phase_name.value in valid_names


@allure.story("Moon Phase Illumination")
class TestMoonPhaseIllumination:
    """
    Tests for illumination at specific phases.
    """

    @pytest.mark.golden
    @allure.title("Full moon has high illumination (>95%)")
    @allure.description("""
    At full moon (phase angle ~180°), the Moon is nearly fully illuminated
    as seen from Earth, with illumination > 95%.
    """)
    def test_full_moon_high_illumination(self):
        """Full moon (phase angle ~180°) is highly illuminated."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Search for full moon (phase angle 170-190°)"):
            for i in range(30):
                test_jd = JulianDate(jd.jd + i)
                phase = moon_phase(test_jd)
                if 170 < phase.phase_angle < 190:
                    with allure.step(f"Found at day +{i}: phase angle = {phase.phase_angle:.1f}°"):
                        pass
                    with allure.step(f"Illumination = {phase.illumination:.3f} (expected > 0.95)"):
                        assert phase.illumination > 0.95
                    break

    @pytest.mark.golden
    @allure.title("New moon has low illumination (<5%)")
    @allure.description("""
    At new moon (phase angle ~0° or ~360°), the Moon is nearly invisible
    as seen from Earth, with illumination < 5%.
    """)
    def test_new_moon_low_illumination(self):
        """New moon (phase angle ~0°) has low illumination."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Search for new moon (phase angle < 10° or > 350°)"):
            for i in range(30):
                test_jd = JulianDate(jd.jd + i)
                phase = moon_phase(test_jd)
                if phase.phase_angle < 10 or phase.phase_angle > 350:
                    with allure.step(f"Found at day +{i}: phase angle = {phase.phase_angle:.1f}°"):
                        pass
                    with allure.step(f"Illumination = {phase.illumination:.3f} (expected < 0.05)"):
                        assert phase.illumination < 0.05
                    break

    @pytest.mark.golden
    @allure.title("Quarter moon is ~50% illuminated")
    @allure.description("""
    At quarter moon (phase angle ~90° or ~270°), the Moon is approximately
    half illuminated as seen from Earth.
    """)
    def test_quarter_moon_half_illuminated(self):
        """Quarter moon (phase angle ~90° or ~270°) is ~50% illuminated."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Search for quarter moon"):
            for i in range(30):
                test_jd = JulianDate(jd.jd + i)
                phase = moon_phase(test_jd)
                if 85 < phase.phase_angle < 95 or 265 < phase.phase_angle < 275:
                    with allure.step(f"Found at day +{i}: phase angle = {phase.phase_angle:.1f}°"):
                        pass
                    with allure.step(f"Illumination = {phase.illumination:.3f} (expected 0.4-0.6)"):
                        assert 0.4 < phase.illumination < 0.6
                    break


# ═══════════════════════════════════════════════════════════════════════════════
#  MOONRISE / MOONSET
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Moonrise")
class TestMoonrise:
    """
    Tests for moonrise calculations.
    """

    @allure.title("moonrise() returns JulianDate or None")
    def test_moonrise_returns_julian_date(self, greenwich):
        """moonrise() returns JulianDate or None."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate moonrise"):
            rise = moonrise(greenwich, jd)

        if rise is not None:
            with allure.step(f"Moonrise at JD {rise.jd:.4f}"):
                assert isinstance(rise, JulianDate)
                assert rise.jd > 0
        else:
            with allure.step("No moonrise found for this day"):
                pass

    @allure.title("Moonrise within ~1 day of reference")
    def test_moonrise_within_day(self, greenwich):
        """Moonrise should be within ~1 day of reference."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate moonrise"):
            rise = moonrise(greenwich, jd)

        if rise:
            with allure.step(f"Moonrise at JD {rise.jd:.4f}"):
                pass

            with allure.step("Calculate time difference"):
                diff = abs(rise.jd - jd.jd)

            with allure.step(f"Difference = {diff:.2f} days (expected < 2)"):
                # Moon rises approximately every 24h 50m
                assert diff < 2


@allure.story("Moonset")
class TestMoonset:
    """
    Tests for moonset calculations.
    """

    @allure.title("moonset() returns JulianDate or None")
    def test_moonset_returns_julian_date(self, greenwich):
        """moonset() returns JulianDate or None."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate moonset"):
            set_t = moonset(greenwich, jd)

        if set_t is not None:
            with allure.step(f"Moonset at JD {set_t.jd:.4f}"):
                assert isinstance(set_t, JulianDate)
        else:
            with allure.step("No moonset found for this day"):
                pass


# ═══════════════════════════════════════════════════════════════════════════════
#  MOON ALTITUDE
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Moon Altitude")
class TestMoonAltitude:
    """
    Tests for moon altitude at specific times.
    """

    @allure.title("moon_altitude() returns Angle")
    def test_moon_altitude_returns_angle(self, greenwich):
        """moon_altitude() returns an Angle."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate moon altitude"):
            alt = moon_altitude(greenwich, jd)

        with allure.step(f"Moon altitude = {alt.degrees:.2f}°"):
            assert isinstance(alt, Angle)

    @allure.title("Moon altitude in valid range [-90°, +90°]")
    def test_moon_altitude_range(self, greenwich):
        """Altitude is always in [-90°, +90°]."""
        with allure.step("Sample altitude throughout the day"):
            for offset in range(0, 25):
                jd = JulianDate(2460000.5 + offset / 24)
                alt = moon_altitude(greenwich, jd)

                with allure.step(f"+{offset}h: altitude = {alt.degrees:.2f}°"):
                    assert -90 <= alt.degrees <= 90


# ═══════════════════════════════════════════════════════════════════════════════
#  NEXT PHASE
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Next Phase")
class TestNextPhase:
    """
    Tests for finding the next lunar phase.
    """

    @allure.title("Find next full moon")
    def test_next_full_moon(self):
        """Find next full moon."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate next full moon"):
            next_full = next_phase(jd, MoonPhase.FULL_MOON)

        with allure.step(f"Next full moon at JD {next_full.jd:.4f}"):
            pass

        with allure.step("Calculate days until full moon"):
            days = next_full.jd - jd.jd

        with allure.step(f"Days until full moon = {days:.1f} (expected < 30)"):
            assert next_full.jd > jd.jd
            assert days < 30

    @allure.title("Find next new moon")
    def test_next_new_moon(self):
        """Find next new moon."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate next new moon"):
            next_new = next_phase(jd, MoonPhase.NEW_MOON)

        with allure.step(f"Next new moon at JD {next_new.jd:.4f}"):
            pass

        with allure.step(f"Days until = {next_new.jd - jd.jd:.1f}"):
            assert next_new.jd > jd.jd
            assert next_new.jd - jd.jd < 30

    @allure.title("Find next first quarter")
    def test_next_first_quarter(self):
        """Find next first quarter."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate next first quarter"):
            next_q = next_phase(jd, MoonPhase.FIRST_QUARTER)

        with allure.step(f"Next first quarter at JD {next_q.jd:.4f}"):
            pass

        with allure.step(f"Days until = {next_q.jd - jd.jd:.1f}"):
            assert next_q.jd > jd.jd
            assert next_q.jd - jd.jd < 30

    @allure.title("Find next last quarter")
    def test_next_last_quarter(self):
        """Find next last quarter."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate next last quarter"):
            next_q = next_phase(jd, MoonPhase.LAST_QUARTER)

        with allure.step(f"Next last quarter at JD {next_q.jd:.4f}"):
            pass

        with allure.step(f"Days until = {next_q.jd - jd.jd:.1f}"):
            assert next_q.jd > jd.jd
            assert next_q.jd - jd.jd < 30

    @pytest.mark.golden
    @allure.title("Synodic month between same phases ≈ 29.5 days")
    @allure.description("""
    The synodic month (time between same lunar phases) is approximately
    29.5 days. This is the time for the Moon to return to the same phase
    as seen from Earth.
    """)
    def test_synodic_month_between_phases(self):
        """Time between same phases is ~29.5 days (synodic month)."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Find first full moon"):
            full1 = next_phase(jd, MoonPhase.FULL_MOON)

        with allure.step(f"First full moon at JD {full1.jd:.4f}"):
            pass

        with allure.step("Find second full moon"):
            full2 = next_phase(JulianDate(full1.jd + 1), MoonPhase.FULL_MOON)

        with allure.step(f"Second full moon at JD {full2.jd:.4f}"):
            pass

        with allure.step("Calculate synodic month"):
            synodic = full2.jd - full1.jd

        with allure.step(f"Synodic month = {synodic:.2f} days (expected 29-30)"):
            assert 29 < synodic < 30


# ═══════════════════════════════════════════════════════════════════════════════
#  EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Moon Edge Cases")
class TestMoonEdgeCases:
    """
    Tests for edge cases in lunar calculations.
    """

    @pytest.mark.edge
    @allure.title("Moon calculations work at North Pole")
    def test_moon_at_north_pole(self, north_pole):
        """Moon calculations work at extreme latitudes."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate moon position"):
            pos = moon_position(jd)

        with allure.step(f"Position: RA={pos.ra.degrees:.2f}°, Dec={pos.dec.degrees:.2f}°"):
            assert pos is not None

        with allure.step("Calculate moon phase"):
            phase = moon_phase(jd)

        with allure.step(f"Phase: {phase.phase_name.value} ({phase.percent_illuminated:.1f}%)"):
            assert phase is not None

        with allure.step("Calculate moon altitude at North Pole"):
            alt = moon_altitude(north_pole, jd)

        with allure.step(f"Altitude at North Pole = {alt.degrees:.2f}°"):
            assert alt is not None

    @pytest.mark.edge
    @allure.title("Moon calculations work at Equator")
    def test_moon_at_equator(self, equator):
        """Moon calculations work at equator."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate moonrise at equator"):
            rise = moonrise(equator, jd)

        with allure.step("Calculate moonset at equator"):
            set_t = moonset(equator, jd)

        if rise:
            with allure.step(f"Moonrise at JD {rise.jd:.4f}"):
                pass
        else:
            with allure.step("No moonrise for this day"):
                pass

        if set_t:
            with allure.step(f"Moonset at JD {set_t.jd:.4f}"):
                pass
        else:
            with allure.step("No moonset for this day"):
                pass
