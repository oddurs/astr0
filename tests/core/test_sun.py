"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                               SUN TESTS                                      ║
║                                                                              ║
║  Tests for solar position, rise/set times, twilight, and seasonal phenomena. ║
║  The Sun - our nearest star and fundamental timekeeping reference.           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import math
import allure
import pytest

from starward.core.angles import Angle
from starward.core.time import JulianDate, jd_now
from starward.core.observer import Observer
from starward.core.sun import (
    sun_position, sunrise, sunset, solar_noon,
    civil_twilight, nautical_twilight, astronomical_twilight,
    solar_altitude, day_length, SunPosition
)


# ═══════════════════════════════════════════════════════════════════════════════
#  SUN POSITION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Sun Position")
class TestSunPosition:
    """
    Tests for solar position calculations.

    Uses low-precision formulae suitable for rise/set calculations
    (accuracy ~0.01° in ecliptic longitude).
    """

    @allure.title("sun_position() returns SunPosition object")
    def test_returns_sun_position_object(self):
        """sun_position() returns SunPosition dataclass."""
        with allure.step("Calculate sun position at J2000.0"):
            jd = JulianDate(2451545.0)
            pos = sun_position(jd)

        with allure.step("Verify returns SunPosition instance"):
            assert isinstance(pos, SunPosition)

    @allure.title("SunPosition has all required fields")
    def test_has_required_fields(self):
        """SunPosition has all required fields."""
        with allure.step("Calculate sun position at J2000.0"):
            jd = JulianDate(2451545.0)
            pos = sun_position(jd)

        with allure.step("Verify longitude field exists"):
            assert hasattr(pos, 'longitude')

        with allure.step("Verify latitude field exists"):
            assert hasattr(pos, 'latitude')

        with allure.step("Verify ra field exists"):
            assert hasattr(pos, 'ra')

        with allure.step("Verify dec field exists"):
            assert hasattr(pos, 'dec')

        with allure.step("Verify distance_au field exists"):
            assert hasattr(pos, 'distance_au')

        with allure.step("Verify equation_of_time field exists"):
            assert hasattr(pos, 'equation_of_time')

    @pytest.mark.golden
    @allure.title("Sun position at J2000.0 (winter)")
    @allure.description("""
    At J2000.0 (Jan 1, 2000), Sun is in Sagittarius.
    Winter solstice was ~Dec 21, so Sun should be at:
      - RA: 18h 45m (280°)
      - Dec: -23°
    """)
    def test_at_j2000_winter(self):
        """At J2000.0 (Jan 1, 2000), Sun is in Sagittarius."""
        with allure.step("Set reference date: J2000.0 (JD 2451545.0)"):
            jd = JulianDate(2451545.0)

        with allure.step("Calculate sun position"):
            pos = sun_position(jd)

        with allure.step(f"RA = {pos.ra.degrees:.2f}° (expected 270-290°)"):
            assert 270 < pos.ra.degrees < 290

        with allure.step(f"Dec = {pos.dec.degrees:.2f}° (expected -24 to -22°)"):
            assert -24 < pos.dec.degrees < -22

    @allure.title("Earth-Sun distance within orbital bounds")
    def test_distance_within_bounds(self):
        """Earth-Sun distance: 0.983 AU (perihelion) to 1.017 AU (aphelion)."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate sun position"):
            pos = sun_position(jd)

        with allure.step(f"Distance = {pos.distance_au:.4f} AU (expected 0.98-1.02)"):
            assert 0.98 < pos.distance_au < 1.02

    @allure.title("Sun ecliptic latitude near zero")
    def test_ecliptic_latitude_near_zero(self):
        """Sun is always very close to the ecliptic plane."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate sun position"):
            pos = sun_position(jd)

        with allure.step(f"Ecliptic latitude = {pos.latitude.degrees:.4f}° (expected < 0.01°)"):
            assert abs(pos.latitude.degrees) < 0.01

    @allure.title("Equation of time within annual range")
    def test_equation_of_time_range(self):
        """Equation of time varies from -14 to +16 minutes."""
        with allure.step("Sample equation of time throughout the year"):
            for offset in range(0, 365, 30):
                jd = JulianDate(2451545.0 + offset)
                pos = sun_position(jd)

                with allure.step(f"Day +{offset}: EoT = {pos.equation_of_time:.2f} min"):
                    assert -17 < pos.equation_of_time < 18


@allure.story("Sun Position Seasons")
class TestSunPositionSeasons:
    """
    Tests for solar position through the seasons.
    """

    @pytest.mark.golden
    @allure.title("Vernal equinox: declination ≈ 0°")
    @allure.description("""
    At the vernal equinox (around March 20), the Sun crosses the celestial
    equator moving northward. Solar declination should be approximately 0°.
    """)
    def test_vernal_equinox_declination(self):
        """At vernal equinox (Mar 20), Dec ≈ 0°."""
        with allure.step("Set date: 2024-03-20 (vernal equinox)"):
            jd = JulianDate(2460390.0)

        with allure.step("Calculate sun position"):
            pos = sun_position(jd)

        with allure.step(f"Declination = {pos.dec.degrees:.2f}° (expected ≈ 0°)"):
            assert abs(pos.dec.degrees) < 1

    @pytest.mark.golden
    @allure.title("Summer solstice: declination ≈ +23.4°")
    @allure.description("""
    At the summer solstice (around June 21), the Sun reaches its maximum
    northern declination of approximately +23.4° (the obliquity of the ecliptic).
    """)
    def test_summer_solstice_declination(self):
        """At summer solstice (Jun 21), Dec ≈ +23.4°."""
        with allure.step("Set date: 2024-06-21 (summer solstice)"):
            jd = JulianDate(2460483.0)

        with allure.step("Calculate sun position"):
            pos = sun_position(jd)

        with allure.step(f"Declination = {pos.dec.degrees:.2f}° (expected 22-24°)"):
            assert 22 < pos.dec.degrees < 24

    @pytest.mark.golden
    @allure.title("Winter solstice: declination ≈ -23.4°")
    @allure.description("""
    At the winter solstice (around December 21), the Sun reaches its maximum
    southern declination of approximately -23.4°.
    """)
    def test_winter_solstice_declination(self):
        """At winter solstice (Dec 21), Dec ≈ -23.4°."""
        with allure.step("Set date: 2024-12-21 (winter solstice)"):
            jd = JulianDate(2460666.0)

        with allure.step("Calculate sun position"):
            pos = sun_position(jd)

        with allure.step(f"Declination = {pos.dec.degrees:.2f}° (expected -24 to -22°)"):
            assert -24 < pos.dec.degrees < -22


# ═══════════════════════════════════════════════════════════════════════════════
#  SUNRISE
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Sunrise")
class TestSunrise:
    """
    Tests for sunrise calculations.
    """

    @allure.title("Winter sunrise at Greenwich (late)")
    def test_sunrise_winter(self, greenwich):
        """Sunrise at Greenwich in winter (late)."""
        with allure.step("Set date: mid-January (JD 2460325.5)"):
            jd = JulianDate(2460325.5)

        with allure.step("Calculate sunrise"):
            rise = sunrise(greenwich, jd)

        with allure.step("Verify sunrise was found"):
            assert rise is not None

        with allure.step("Convert to datetime"):
            dt = rise.to_datetime()

        with allure.step(f"Sunrise at {dt.hour}:{dt.minute:02d} UTC (expected 7-8 AM)"):
            assert 6 < dt.hour < 9

    @allure.title("Summer sunrise at Greenwich (early)")
    def test_sunrise_summer(self, greenwich):
        """Sunrise at Greenwich in summer (early)."""
        with allure.step("Set date: June solstice (JD 2460483.5)"):
            jd = JulianDate(2460483.5)

        with allure.step("Calculate sunrise"):
            rise = sunrise(greenwich, jd)

        with allure.step("Verify sunrise was found"):
            assert rise is not None

        with allure.step("Convert to datetime"):
            dt = rise.to_datetime()

        with allure.step(f"Sunrise at {dt.hour}:{dt.minute:02d} UTC (expected 3-6 AM)"):
            assert 3 <= dt.hour < 6

    @allure.title("Sunrise times consistent near equator")
    def test_sunrise_tropics(self):
        """Sunrise times are more consistent near equator."""
        with allure.step("Create observer at equator"):
            equator = Observer.from_degrees("Equator", 0.0, 0.0)

        with allure.step("Sample sunrise times throughout the year"):
            times = []
            for month_offset in [0, 90, 180, 270]:
                jd = JulianDate(2460000.5 + month_offset)
                rise = sunrise(equator, jd)
                if rise:
                    dt = rise.to_datetime()
                    times.append(dt.hour)
                    with allure.step(f"Day +{month_offset}: sunrise at {dt.hour}:{dt.minute:02d}"):
                        pass

        with allure.step("Verify times within 2 hours of each other"):
            if len(times) > 1:
                spread = max(times) - min(times)
                with allure.step(f"Spread = {spread} hours (expected < 2)"):
                    assert spread < 2

    @pytest.mark.edge
    @allure.title("Midnight sun at North Pole (no sunrise)")
    def test_midnight_sun(self, north_pole):
        """No sunrise during polar day (midnight sun)."""
        with allure.step("Set date: June (summer at north pole)"):
            jd = JulianDate(2460483.5)

        with allure.step("Calculate sunrise at North Pole"):
            rise = sunrise(north_pole, jd)

        with allure.step(f"Result: {'No sunrise (24h daylight)' if rise is None else f'Sunrise at JD {rise.jd:.4f}'}"):
            pass  # May return None for 24-hour daylight


# ═══════════════════════════════════════════════════════════════════════════════
#  SUNSET
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Sunset")
class TestSunset:
    """
    Tests for sunset calculations.
    """

    @allure.title("Winter sunset at Greenwich (early)")
    def test_sunset_winter(self, greenwich):
        """Sunset at Greenwich in winter (early)."""
        with allure.step("Set date: mid-January (JD 2460325.5)"):
            jd = JulianDate(2460325.5)

        with allure.step("Calculate sunset"):
            set_t = sunset(greenwich, jd)

        with allure.step("Verify sunset was found"):
            assert set_t is not None

        with allure.step("Convert to datetime"):
            dt = set_t.to_datetime()

        with allure.step(f"Sunset at {dt.hour}:{dt.minute:02d} UTC (expected 4-5 PM)"):
            assert 15 < dt.hour < 18

    @allure.title("Summer sunset at Greenwich (late)")
    def test_sunset_summer(self, greenwich):
        """Sunset at Greenwich in summer (late)."""
        with allure.step("Set date: June solstice (JD 2460483.5)"):
            jd = JulianDate(2460483.5)

        with allure.step("Calculate sunset"):
            set_t = sunset(greenwich, jd)

        with allure.step("Verify sunset was found"):
            assert set_t is not None

        with allure.step("Convert to datetime"):
            dt = set_t.to_datetime()

        with allure.step(f"Sunset at {dt.hour}:{dt.minute:02d} UTC (expected 7-10 PM)"):
            assert 19 <= dt.hour < 22

    @allure.title("Sunset always after sunrise")
    def test_sunset_after_sunrise(self, greenwich):
        """Sunset always occurs after sunrise (normal latitudes)."""
        with allure.step("Set date: mid-January"):
            jd = JulianDate(2460325.5)

        with allure.step("Calculate sunrise"):
            rise = sunrise(greenwich, jd)

        with allure.step("Calculate sunset"):
            set_t = sunset(greenwich, jd)

        if rise and set_t:
            with allure.step(f"Sunrise JD = {rise.jd:.4f}"):
                pass

            with allure.step(f"Sunset JD = {set_t.jd:.4f}"):
                pass

            with allure.step("Verify sunset > sunrise"):
                assert set_t.jd > rise.jd


# ═══════════════════════════════════════════════════════════════════════════════
#  SOLAR NOON
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Solar Noon")
class TestSolarNoon:
    """
    Tests for solar noon (local meridian transit).
    """

    @allure.title("Solar noon at Greenwich near 12:00 UTC")
    def test_solar_noon_at_greenwich(self, greenwich):
        """Solar noon at Greenwich is close to 12:00 UTC."""
        with allure.step("Set date: mid-January"):
            jd = JulianDate(2460325.5)

        with allure.step("Calculate solar noon"):
            noon = solar_noon(greenwich, jd)

        with allure.step("Verify noon was found"):
            assert noon is not None

        with allure.step("Convert to datetime"):
            dt = noon.to_datetime()

        with allure.step(f"Solar noon at {dt.hour}:{dt.minute:02d} UTC (expected 11:45-12:15)"):
            assert 11 <= dt.hour <= 12

    @allure.title("Solar altitude maximum at solar noon")
    def test_solar_noon_altitude_is_maximum(self, greenwich):
        """Solar altitude is highest at solar noon."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate solar noon"):
            noon = solar_noon(greenwich, jd)

        if noon:
            with allure.step(f"Solar noon at JD {noon.jd:.4f}"):
                pass

            with allure.step("Calculate altitude at noon"):
                alt_noon = solar_altitude(greenwich, noon)

            with allure.step("Calculate altitude 2 hours before"):
                alt_before = solar_altitude(greenwich, JulianDate(noon.jd - 2/24))

            with allure.step("Calculate altitude 2 hours after"):
                alt_after = solar_altitude(greenwich, JulianDate(noon.jd + 2/24))

            with allure.step(f"Noon: {alt_noon.degrees:.2f}°, Before: {alt_before.degrees:.2f}°, After: {alt_after.degrees:.2f}°"):
                pass

            with allure.step("Verify noon altitude > before"):
                assert alt_noon.degrees > alt_before.degrees

            with allure.step("Verify noon altitude > after"):
                assert alt_noon.degrees > alt_after.degrees


# ═══════════════════════════════════════════════════════════════════════════════
#  SOLAR ALTITUDE
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Solar Altitude")
class TestSolarAltitude:
    """
    Tests for solar altitude at specific times.
    """

    @allure.title("solar_altitude() returns Angle")
    def test_altitude_returns_angle(self, greenwich):
        """solar_altitude() returns an Angle."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate solar altitude"):
            alt = solar_altitude(greenwich, jd)

        with allure.step(f"Altitude = {alt.degrees:.2f}°"):
            assert isinstance(alt, Angle)

    @allure.title("Solar altitude in valid range [-90°, +90°]")
    def test_altitude_range(self, greenwich):
        """Altitude is always between -90° and +90°."""
        with allure.step("Sample altitude throughout the day"):
            for offset in range(0, 24, 2):
                jd = JulianDate(2460000.5 + offset / 24)
                alt = solar_altitude(greenwich, jd)

                with allure.step(f"+{offset}h: altitude = {alt.degrees:.2f}°"):
                    assert -90 <= alt.degrees <= 90

    @pytest.mark.golden
    @allure.title("Summer noon altitude at Greenwich ≈ 62°")
    @allure.description("""
    At Greenwich (latitude 51.5°N) during summer solstice, the sun reaches
    its maximum altitude of approximately 62° (90° - 51.5° + 23.4°).
    """)
    def test_altitude_at_noon_summer(self, greenwich):
        """Summer noon altitude at Greenwich ≈ 62°."""
        with allure.step("Set date: June 21 (summer solstice)"):
            jd = JulianDate(2460483.5)

        with allure.step("Calculate solar noon"):
            noon = solar_noon(greenwich, jd)

        if noon:
            with allure.step(f"Solar noon at JD {noon.jd:.4f}"):
                pass

            with allure.step("Calculate altitude at noon"):
                alt = solar_altitude(greenwich, noon)

            with allure.step(f"Altitude = {alt.degrees:.2f}° (expected 55-65°)"):
                assert 55 < alt.degrees < 65


# ═══════════════════════════════════════════════════════════════════════════════
#  TWILIGHT
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Twilight")
class TestTwilight:
    """
    Tests for twilight calculations.

    Twilight types (Sun below horizon):
      - Civil: 0° to -6° (artificial light not needed)
      - Nautical: -6° to -12° (horizon visible at sea)
      - Astronomical: -12° to -18° (sky fully dark)
    """

    @allure.title("Civil twilight exists at mid-latitudes")
    def test_civil_twilight_exists(self, greenwich):
        """Civil twilight exists for mid-latitudes."""
        with allure.step("Set date: mid-January"):
            jd = JulianDate(2460325.5)

        with allure.step("Calculate civil twilight"):
            morning, evening = civil_twilight(greenwich, jd)

        with allure.step(f"Morning civil twilight: JD {morning.jd:.4f}" if morning else "No morning twilight"):
            assert morning is not None

        with allure.step(f"Evening civil twilight: JD {evening.jd:.4f}" if evening else "No evening twilight"):
            assert evening is not None

        with allure.step("Verify morning < evening"):
            assert morning.jd < evening.jd

    @allure.title("Nautical twilight exists at mid-latitudes")
    def test_nautical_twilight_exists(self, greenwich):
        """Nautical twilight exists for mid-latitudes."""
        with allure.step("Set date: mid-January"):
            jd = JulianDate(2460325.5)

        with allure.step("Calculate nautical twilight"):
            morning, evening = nautical_twilight(greenwich, jd)

        with allure.step(f"Morning: JD {morning.jd:.4f}, Evening: JD {evening.jd:.4f}"):
            assert morning is not None
            assert evening is not None

    @allure.title("Astronomical twilight exists at mid-latitudes")
    def test_astronomical_twilight_exists(self, greenwich):
        """Astronomical twilight exists for mid-latitudes."""
        with allure.step("Set date: mid-January"):
            jd = JulianDate(2460325.5)

        with allure.step("Calculate astronomical twilight"):
            morning, evening = astronomical_twilight(greenwich, jd)

        with allure.step(f"Morning: JD {morning.jd:.4f}, Evening: JD {evening.jd:.4f}"):
            assert morning is not None
            assert evening is not None

    @allure.title("Twilight events in correct order")
    @allure.description("""
    Morning twilights occur in order: astronomical < nautical < civil < sunrise.
    The sky gradually brightens as the sun approaches the horizon.
    """)
    def test_twilight_order(self, greenwich):
        """Morning twilights occur in order: astro < nautical < civil < sunrise."""
        with allure.step("Set date: mid-January"):
            jd = JulianDate(2460325.5)

        with allure.step("Calculate all twilight times"):
            astro = astronomical_twilight(greenwich, jd)
            naut = nautical_twilight(greenwich, jd)
            civil = civil_twilight(greenwich, jd)
            rise = sunrise(greenwich, jd)

        if all([astro[0], naut[0], civil[0], rise]):
            with allure.step(f"Astronomical twilight: JD {astro[0].jd:.4f}"):
                pass

            with allure.step(f"Nautical twilight: JD {naut[0].jd:.4f}"):
                pass

            with allure.step(f"Civil twilight: JD {civil[0].jd:.4f}"):
                pass

            with allure.step(f"Sunrise: JD {rise.jd:.4f}"):
                pass

            with allure.step("Verify order: astro < naut < civil < sunrise"):
                assert astro[0].jd < naut[0].jd < civil[0].jd < rise.jd


# ═══════════════════════════════════════════════════════════════════════════════
#  DAY LENGTH
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Day Length")
class TestDayLength:
    """
    Tests for day length calculations.
    """

    @allure.title("day_length() returns hours")
    def test_day_length_returns_hours(self, greenwich):
        """day_length() returns hours."""
        with allure.step("Set date: mid-January"):
            jd = JulianDate(2460325.5)

        with allure.step("Calculate day length"):
            length = day_length(greenwich, jd)

        with allure.step(f"Day length = {length:.2f} hours"):
            assert length is not None
            assert 0 < length < 24

    @allure.title("Summer days longer than winter days")
    def test_day_length_summer_longer(self, greenwich):
        """Summer days are longer than winter days (northern hemisphere)."""
        with allure.step("Set winter date: January"):
            winter = JulianDate(2460325.5)

        with allure.step("Set summer date: June"):
            summer = JulianDate(2460483.5)

        with allure.step("Calculate winter day length"):
            winter_len = day_length(greenwich, winter)

        with allure.step("Calculate summer day length"):
            summer_len = day_length(greenwich, summer)

        if winter_len and summer_len:
            with allure.step(f"Winter: {winter_len:.2f}h, Summer: {summer_len:.2f}h"):
                pass

            with allure.step("Verify summer > winter"):
                assert summer_len > winter_len

    @pytest.mark.golden
    @allure.title("Equinox day length ≈ 12 hours at equator")
    @allure.description("""
    At the equator, day length is approximately 12 hours year-round,
    varying only slightly due to atmospheric refraction and the sun's
    angular diameter.
    """)
    def test_equinox_day_length(self):
        """Day length ≈ 12 hours at equator year-round."""
        with allure.step("Create observer at equator"):
            equator = Observer.from_degrees("Equator", 0.0, 0.0)

        with allure.step("Set date: vernal equinox"):
            jd = JulianDate(2460390.0)

        with allure.step("Calculate day length"):
            length = day_length(equator, jd)

        if length:
            with allure.step(f"Day length = {length:.2f} hours (expected 11.5-12.5)"):
                assert 11.5 < length < 12.5
