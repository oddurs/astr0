"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                            PLANETS TESTS                                     ║
║                                                                              ║
║  Tests for planetary position calculations.                                  ║
║  Golden tests validated against JPL Horizons ephemeris data.                 ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import math
import allure
import pytest

from starward.core.angles import Angle
from starward.core.time import JulianDate, jd_now
from starward.core.observer import Observer
from starward.core.planets import (
    Planet, PlanetPosition, PLANET_SYMBOLS,
    planet_position, all_planet_positions,
    planet_altitude, planet_rise, planet_set, planet_transit,
)


# ═══════════════════════════════════════════════════════════════════════════════
#  BASIC FUNCTIONALITY
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Planet Enum")
class TestPlanetEnum:
    """Tests for Planet enum."""

    @allure.title("All 7 planets are defined")
    def test_all_planets_exist(self):
        """All 7 planets are defined."""
        with allure.step("Get list of all planets"):
            planets = list(Planet)

        with allure.step(f"Planet count = {len(planets)} (expected 7)"):
            assert len(planets) == 7

    @allure.title("Planet names are correct")
    def test_planet_names(self):
        """Planet names are correct."""
        with allure.step("Verify Mercury"):
            assert Planet.MERCURY.value == "Mercury"

        with allure.step("Verify Venus"):
            assert Planet.VENUS.value == "Venus"

        with allure.step("Verify Mars"):
            assert Planet.MARS.value == "Mars"

        with allure.step("Verify Jupiter"):
            assert Planet.JUPITER.value == "Jupiter"

        with allure.step("Verify Saturn"):
            assert Planet.SATURN.value == "Saturn"

        with allure.step("Verify Uranus"):
            assert Planet.URANUS.value == "Uranus"

        with allure.step("Verify Neptune"):
            assert Planet.NEPTUNE.value == "Neptune"

    @allure.title("Each planet has a symbol")
    def test_planet_symbols(self):
        """Each planet has a symbol."""
        with allure.step("Verify all planets have symbols"):
            for planet in Planet:
                with allure.step(f"{planet.value}: {PLANET_SYMBOLS[planet]}"):
                    assert planet in PLANET_SYMBOLS
                    assert len(PLANET_SYMBOLS[planet]) > 0


@allure.story("Planet Position")
class TestPlanetPosition:
    """Tests for PlanetPosition dataclass."""

    @allure.title("planet_position() returns PlanetPosition")
    def test_returns_planet_position_object(self):
        """planet_position() returns PlanetPosition dataclass."""
        with allure.step("Set date: J2000.0"):
            jd = JulianDate(2451545.0)

        with allure.step("Calculate Mars position"):
            pos = planet_position(Planet.MARS, jd)

        with allure.step("Verify returns PlanetPosition"):
            assert isinstance(pos, PlanetPosition)

    @allure.title("PlanetPosition has all required fields")
    def test_has_required_fields(self):
        """PlanetPosition has all required fields."""
        with allure.step("Calculate Jupiter position at J2000.0"):
            jd = JulianDate(2451545.0)
            pos = planet_position(Planet.JUPITER, jd)

        fields = ['planet', 'helio_longitude', 'helio_latitude', 'helio_distance',
                  'ra', 'dec', 'distance_au', 'magnitude', 'elongation',
                  'phase_angle', 'angular_diameter']

        for field in fields:
            with allure.step(f"Verify '{field}' field exists"):
                assert hasattr(pos, field)

    @allure.title("to_icrs() returns valid ICRSCoord")
    def test_to_icrs_conversion(self):
        """to_icrs() returns valid ICRSCoord."""
        with allure.step("Calculate Saturn position"):
            jd = JulianDate(2451545.0)
            pos = planet_position(Planet.SATURN, jd)

        with allure.step("Convert to ICRS"):
            icrs = pos.to_icrs()

        with allure.step(f"ICRS: RA={icrs.ra.degrees:.2f}°, Dec={icrs.dec.degrees:.2f}°"):
            assert hasattr(icrs, 'ra')
            assert hasattr(icrs, 'dec')
            assert icrs.ra.degrees == pos.ra.degrees
            assert icrs.dec.degrees == pos.dec.degrees

    @allure.title("Illumination property returns valid fraction")
    def test_illumination_property(self):
        """illumination property returns valid fraction."""
        with allure.step("Calculate Venus position"):
            jd = JulianDate(2451545.0)
            pos = planet_position(Planet.VENUS, jd)

        with allure.step(f"Illumination = {pos.illumination:.3f} (expected 0-1)"):
            assert 0 <= pos.illumination <= 1

    @allure.title("Symbol property returns planet symbol")
    def test_symbol_property(self):
        """symbol property returns planet symbol."""
        with allure.step("Calculate Mars position"):
            jd = JulianDate(2451545.0)
            pos = planet_position(Planet.MARS, jd)

        with allure.step(f"Mars symbol = {pos.symbol} (expected ♂)"):
            assert pos.symbol == "♂"


# ═══════════════════════════════════════════════════════════════════════════════
#  ALL PLANETS FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("All Planet Positions")
class TestAllPlanetPositions:
    """Tests for all_planet_positions() function."""

    @allure.title("all_planet_positions() returns all 7 planets")
    def test_returns_dict_of_all_planets(self):
        """all_planet_positions() returns positions for all planets."""
        with allure.step("Set date: J2000.0"):
            jd = JulianDate(2451545.0)

        with allure.step("Get all planet positions"):
            positions = all_planet_positions(jd)

        with allure.step(f"Returned {len(positions)} planets (expected 7)"):
            assert isinstance(positions, dict)
            assert len(positions) == 7

        with allure.step("Verify all planets present"):
            for planet in Planet:
                with allure.step(f"{planet.value}: RA={positions[planet].ra.degrees:.1f}°"):
                    assert planet in positions
                    assert isinstance(positions[planet], PlanetPosition)


# ═══════════════════════════════════════════════════════════════════════════════
#  GOLDEN TESTS - Validated against JPL Horizons
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Golden Positions")
class TestGoldenPositions:
    """
    Golden tests using positions from JPL Horizons.

    Accuracy target: ~1 arcminute for positions (using Meeus algorithms).
    These tests use dates where positions are well-known.
    """

    @pytest.mark.golden
    @allure.title("Mars position at J2000.0")
    @allure.description("""
    JPL Horizons (2000-Jan-01 12:00 TDB):
      RA: ~22h 0m, Dec: ~-13°
    """)
    def test_mars_at_j2000(self):
        """Mars position at J2000.0."""
        with allure.step("Set date: J2000.0 (JD 2451545.0)"):
            jd = JulianDate(2451545.0)

        with allure.step("Calculate Mars position"):
            pos = planet_position(Planet.MARS, jd)

        with allure.step(f"RA = {pos.ra.degrees:.2f}° (expected 320-340°)"):
            assert 320 < pos.ra.degrees < 340

        with allure.step(f"Dec = {pos.dec.degrees:.2f}° (expected -16 to -10°)"):
            assert -16 < pos.dec.degrees < -10

    @pytest.mark.golden
    @allure.title("Jupiter position at J2000.0")
    @allure.description("""
    JPL Horizons (2000-Jan-01 12:00 TDB):
      RA: ~1h 36m (~24°), Dec: ~+8°
    """)
    def test_jupiter_at_j2000(self):
        """Jupiter position at J2000.0."""
        with allure.step("Set date: J2000.0"):
            jd = JulianDate(2451545.0)

        with allure.step("Calculate Jupiter position"):
            pos = planet_position(Planet.JUPITER, jd)

        with allure.step(f"RA = {pos.ra.degrees:.2f}° (expected 20-30°)"):
            assert 20 < pos.ra.degrees < 30

        with allure.step(f"Dec = {pos.dec.degrees:.2f}° (expected 6-12°)"):
            assert 6 < pos.dec.degrees < 12

    @pytest.mark.golden
    @allure.title("Saturn position at J2000.0")
    @allure.description("""
    JPL Horizons: RA ~2h 40m, Dec ~+12°
    """)
    def test_saturn_at_j2000(self):
        """Saturn position at J2000.0."""
        with allure.step("Set date: J2000.0"):
            jd = JulianDate(2451545.0)

        with allure.step("Calculate Saturn position"):
            pos = planet_position(Planet.SATURN, jd)

        with allure.step(f"RA = {pos.ra.degrees:.2f}° (expected 35-55°)"):
            assert 35 < pos.ra.degrees < 55

        with allure.step(f"Dec = {pos.dec.degrees:.2f}° (expected 8-16°)"):
            assert 8 < pos.dec.degrees < 16


@allure.story("Orbital Distances")
class TestOrbitalDistances:
    """Tests for orbital distances."""

    @allure.title("Inner planets closer than outer planets")
    def test_inner_planets_closer_than_outer(self):
        """Inner planets have smaller heliocentric distances."""
        with allure.step("Get current Julian Date"):
            jd = jd_now()

        with allure.step("Calculate planet positions"):
            mercury = planet_position(Planet.MERCURY, jd)
            venus = planet_position(Planet.VENUS, jd)
            mars = planet_position(Planet.MARS, jd)
            jupiter = planet_position(Planet.JUPITER, jd)

        with allure.step(f"Mercury: {mercury.helio_distance:.2f} AU"):
            pass
        with allure.step(f"Venus: {venus.helio_distance:.2f} AU"):
            pass
        with allure.step(f"Mars: {mars.helio_distance:.2f} AU"):
            pass
        with allure.step(f"Jupiter: {jupiter.helio_distance:.2f} AU"):
            pass

        with allure.step("Verify Mercury < Venus < Mars < Jupiter"):
            assert mercury.helio_distance < venus.helio_distance
            assert venus.helio_distance < mars.helio_distance
            assert mars.helio_distance < jupiter.helio_distance

    @allure.title("Mercury distance: 0.31-0.47 AU")
    def test_mercury_distance_bounds(self):
        """Mercury: 0.31 - 0.47 AU from Sun."""
        with allure.step("Calculate Mercury position"):
            jd = jd_now()
            pos = planet_position(Planet.MERCURY, jd)

        with allure.step(f"Distance = {pos.helio_distance:.3f} AU (expected 0.30-0.48)"):
            assert 0.30 < pos.helio_distance < 0.48

    @allure.title("Venus distance: ~0.72 AU (nearly circular)")
    def test_venus_distance_bounds(self):
        """Venus: ~0.72 AU from Sun (nearly circular)."""
        with allure.step("Calculate Venus position"):
            jd = jd_now()
            pos = planet_position(Planet.VENUS, jd)

        with allure.step(f"Distance = {pos.helio_distance:.3f} AU (expected 0.71-0.73)"):
            assert 0.71 < pos.helio_distance < 0.73

    @allure.title("Mars distance: 1.38-1.67 AU")
    def test_mars_distance_bounds(self):
        """Mars: 1.38 - 1.67 AU from Sun."""
        with allure.step("Calculate Mars position"):
            jd = jd_now()
            pos = planet_position(Planet.MARS, jd)

        with allure.step(f"Distance = {pos.helio_distance:.3f} AU (expected 1.37-1.68)"):
            assert 1.37 < pos.helio_distance < 1.68

    @allure.title("Jupiter distance: 4.95-5.46 AU")
    def test_jupiter_distance_bounds(self):
        """Jupiter: 4.95 - 5.46 AU from Sun."""
        with allure.step("Calculate Jupiter position"):
            jd = jd_now()
            pos = planet_position(Planet.JUPITER, jd)

        with allure.step(f"Distance = {pos.helio_distance:.2f} AU (expected 4.94-5.47)"):
            assert 4.94 < pos.helio_distance < 5.47

    @allure.title("Saturn distance: 9.02-10.05 AU")
    def test_saturn_distance_bounds(self):
        """Saturn: 9.02 - 10.05 AU from Sun."""
        with allure.step("Calculate Saturn position"):
            jd = jd_now()
            pos = planet_position(Planet.SATURN, jd)

        with allure.step(f"Distance = {pos.helio_distance:.2f} AU (expected 9.0-10.1)"):
            assert 9.0 < pos.helio_distance < 10.1

    @allure.title("Uranus distance: 18.3-20.1 AU")
    def test_uranus_distance_bounds(self):
        """Uranus: 18.3 - 20.1 AU from Sun."""
        with allure.step("Calculate Uranus position"):
            jd = jd_now()
            pos = planet_position(Planet.URANUS, jd)

        with allure.step(f"Distance = {pos.helio_distance:.2f} AU (expected 18.2-20.2)"):
            assert 18.2 < pos.helio_distance < 20.2

    @allure.title("Neptune distance: 29.8-30.3 AU")
    def test_neptune_distance_bounds(self):
        """Neptune: 29.8 - 30.3 AU from Sun."""
        with allure.step("Calculate Neptune position"):
            jd = jd_now()
            pos = planet_position(Planet.NEPTUNE, jd)

        with allure.step(f"Distance = {pos.helio_distance:.2f} AU (expected 29.7-30.4)"):
            assert 29.7 < pos.helio_distance < 30.4


# ═══════════════════════════════════════════════════════════════════════════════
#  VISUAL PROPERTIES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Magnitudes")
class TestMagnitudes:
    """Tests for apparent magnitude calculations."""

    @allure.title("Venus brighter than Saturn")
    def test_venus_brightest(self):
        """Venus is typically the brightest planet."""
        with allure.step("Get all planet positions"):
            jd = jd_now()
            positions = all_planet_positions(jd)

        with allure.step("Get magnitudes"):
            venus_mag = positions[Planet.VENUS].magnitude
            saturn_mag = positions[Planet.SATURN].magnitude

        with allure.step(f"Venus: {venus_mag:.1f} mag, Saturn: {saturn_mag:.1f} mag"):
            pass

        with allure.step("Verify Venus brighter than Saturn"):
            assert venus_mag < saturn_mag

    @allure.title("Jupiter brighter than Saturn")
    def test_jupiter_brighter_than_saturn(self):
        """Jupiter is always brighter than Saturn."""
        with allure.step("Get planet positions"):
            jd = jd_now()
            positions = all_planet_positions(jd)

        with allure.step("Get magnitudes"):
            jupiter_mag = positions[Planet.JUPITER].magnitude
            saturn_mag = positions[Planet.SATURN].magnitude

        with allure.step(f"Jupiter: {jupiter_mag:.1f} mag, Saturn: {saturn_mag:.1f} mag"):
            pass

        with allure.step("Verify Jupiter < Saturn (brighter)"):
            assert jupiter_mag < saturn_mag

    @allure.title("Outer planets dimmer than inner ones")
    def test_outer_planets_dimmer(self):
        """Outer planets are dimmer than inner ones generally."""
        with allure.step("Get planet positions"):
            jd = jd_now()
            positions = all_planet_positions(jd)

        with allure.step("Get outer planet magnitudes"):
            jupiter_mag = positions[Planet.JUPITER].magnitude
            uranus_mag = positions[Planet.URANUS].magnitude
            neptune_mag = positions[Planet.NEPTUNE].magnitude

        with allure.step(f"Jupiter: {jupiter_mag:.1f}, Uranus: {uranus_mag:.1f}, Neptune: {neptune_mag:.1f}"):
            pass

        with allure.step("Verify Jupiter < Uranus < Neptune"):
            assert jupiter_mag < uranus_mag < neptune_mag


@allure.story("Elongation")
class TestElongation:
    """Tests for elongation calculations."""

    @allure.title("Elongation within [0°, 180°]")
    def test_elongation_within_bounds(self):
        """Elongation is between 0° and 180°."""
        with allure.step("Get current date"):
            jd = jd_now()

        with allure.step("Check elongation for all planets"):
            for planet in Planet:
                pos = planet_position(planet, jd)
                with allure.step(f"{planet.value}: {pos.elongation.degrees:.1f}°"):
                    assert 0 <= pos.elongation.degrees <= 180

    @allure.title("Inner planets have limited max elongation")
    def test_inner_planet_elongation_limited(self):
        """Inner planets have limited maximum elongation."""
        with allure.step("Get current date"):
            jd = jd_now()

        with allure.step("Calculate Mercury position"):
            mercury = planet_position(Planet.MERCURY, jd)

        with allure.step("Calculate Venus position"):
            venus = planet_position(Planet.VENUS, jd)

        with allure.step(f"Mercury elongation = {mercury.elongation.degrees:.1f}° (max ~28°)"):
            assert mercury.elongation.degrees <= 30

        with allure.step(f"Venus elongation = {venus.elongation.degrees:.1f}° (max ~47°)"):
            assert venus.elongation.degrees <= 50


@allure.story("Phase Angle")
class TestPhaseAngle:
    """Tests for phase angle calculations."""

    @allure.title("Phase angle within [0°, 180°]")
    def test_phase_angle_within_bounds(self):
        """Phase angle is between 0° and 180°."""
        with allure.step("Get current date"):
            jd = jd_now()

        with allure.step("Check phase angle for all planets"):
            for planet in Planet:
                pos = planet_position(planet, jd)
                with allure.step(f"{planet.value}: {pos.phase_angle.degrees:.1f}°"):
                    assert 0 <= pos.phase_angle.degrees <= 180

    @allure.title("Outer planets have small phase angles")
    def test_outer_planets_small_phase_angle(self):
        """Outer planets always have small phase angles."""
        with allure.step("Get current date"):
            jd = jd_now()

        with allure.step("Calculate outer planet positions"):
            jupiter = planet_position(Planet.JUPITER, jd)
            saturn = planet_position(Planet.SATURN, jd)
            neptune = planet_position(Planet.NEPTUNE, jd)

        with allure.step(f"Jupiter phase angle = {jupiter.phase_angle.degrees:.1f}° (expected < 12°)"):
            assert jupiter.phase_angle.degrees < 12

        with allure.step(f"Saturn phase angle = {saturn.phase_angle.degrees:.1f}° (expected < 7°)"):
            assert saturn.phase_angle.degrees < 7

        with allure.step(f"Neptune phase angle = {neptune.phase_angle.degrees:.1f}° (expected < 2°)"):
            assert neptune.phase_angle.degrees < 2


# ═══════════════════════════════════════════════════════════════════════════════
#  RISE/SET/TRANSIT
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Rise/Set/Transit")
class TestRiseSetTransit:
    """Tests for rise, set, and transit calculations."""

    @pytest.fixture
    def greenwich(self):
        """Greenwich observatory."""
        return Observer.from_degrees("Greenwich", 51.4769, -0.0005)

    @pytest.fixture
    def new_york(self):
        """New York City."""
        return Observer.from_degrees("New York", 40.7128, -74.0060)

    @allure.title("planet_transit() returns JulianDate")
    def test_transit_returns_julian_date(self, greenwich):
        """planet_transit() returns JulianDate."""
        with allure.step("Get current date"):
            jd = jd_now()

        with allure.step("Calculate Jupiter transit"):
            transit = planet_transit(Planet.JUPITER, greenwich, jd)

        with allure.step(f"Transit at JD {transit.jd:.4f}"):
            assert isinstance(transit, JulianDate)

    @allure.title("Rise < Transit < Set for Jupiter")
    def test_rise_before_transit_before_set(self, greenwich):
        """For most cases: rise < transit < set."""
        with allure.step("Get current date"):
            jd = jd_now()

        with allure.step("Calculate Jupiter rise"):
            rise = planet_rise(Planet.JUPITER, greenwich, jd)

        with allure.step("Calculate Jupiter transit"):
            transit = planet_transit(Planet.JUPITER, greenwich, jd)

        with allure.step("Calculate Jupiter set"):
            set_time = planet_set(Planet.JUPITER, greenwich, jd)

        if rise and set_time:
            with allure.step(f"Rise: {rise.jd:.4f}, Transit: {transit.jd:.4f}, Set: {set_time.jd:.4f}"):
                pass

            with allure.step("Verify rise < transit < set"):
                assert rise.jd < transit.jd < set_time.jd

    @allure.title("Rise/set can return None")
    def test_rise_set_returns_optional(self, greenwich):
        """Rise/set can return None for circumpolar/never-rises."""
        with allure.step("Get current date"):
            jd = jd_now()

        with allure.step("Calculate Jupiter rise"):
            rise = planet_rise(Planet.JUPITER, greenwich, jd)

        with allure.step("Calculate Jupiter set"):
            set_time = planet_set(Planet.JUPITER, greenwich, jd)

        with allure.step(f"Rise: {rise}, Set: {set_time}"):
            assert rise is None or isinstance(rise, JulianDate)
            assert set_time is None or isinstance(set_time, JulianDate)

    @allure.title("Altitude at transit is maximum")
    def test_altitude_at_transit_is_maximum(self, greenwich):
        """Altitude at transit should be near maximum."""
        with allure.step("Get current date"):
            jd = jd_now()

        with allure.step("Calculate Jupiter transit"):
            transit = planet_transit(Planet.JUPITER, greenwich, jd)

        with allure.step("Calculate altitude at transit"):
            alt_transit = planet_altitude(Planet.JUPITER, greenwich, transit)

        with allure.step("Calculate altitude 1 hour before"):
            before = JulianDate(transit.jd - 1/24)
            alt_before = planet_altitude(Planet.JUPITER, greenwich, before)

        with allure.step(f"Transit: {alt_transit.degrees:.2f}°, Before: {alt_before.degrees:.2f}°"):
            pass

        with allure.step("Verify transit altitude >= before"):
            assert alt_transit.degrees >= alt_before.degrees - 0.1


@allure.story("Planet Altitude")
class TestPlanetAltitude:
    """Tests for planet_altitude() function."""

    @pytest.fixture
    def greenwich(self):
        return Observer.from_degrees("Greenwich", 51.4769, -0.0005)

    @allure.title("planet_altitude() returns Angle")
    def test_returns_angle(self, greenwich):
        """planet_altitude() returns Angle."""
        with allure.step("Get current date"):
            jd = jd_now()

        with allure.step("Calculate Mars altitude"):
            alt = planet_altitude(Planet.MARS, greenwich, jd)

        with allure.step(f"Mars altitude = {alt.degrees:.2f}°"):
            assert isinstance(alt, Angle)

    @allure.title("Planet altitude within [-90°, +90°]")
    def test_altitude_within_bounds(self, greenwich):
        """Altitude is between -90° and +90°."""
        with allure.step("Get current date"):
            jd = jd_now()

        with allure.step("Check altitude for all planets"):
            for planet in Planet:
                alt = planet_altitude(planet, greenwich, jd)
                with allure.step(f"{planet.value}: {alt.degrees:.2f}°"):
                    assert -90 <= alt.degrees <= 90


# ═══════════════════════════════════════════════════════════════════════════════
#  EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Edge Cases")
class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    @allure.title("Default JD is current time")
    def test_default_jd_is_now(self):
        """Functions default to current time when jd=None."""
        with allure.step("Calculate Mars with jd=None"):
            pos1 = planet_position(Planet.MARS)

        with allure.step("Calculate Mars with jd=jd_now()"):
            pos2 = planet_position(Planet.MARS, jd_now())

        with allure.step(f"Difference: RA={abs(pos1.ra.degrees - pos2.ra.degrees):.4f}°"):
            assert abs(pos1.ra.degrees - pos2.ra.degrees) < 0.01
            assert abs(pos1.dec.degrees - pos2.dec.degrees) < 0.01

    @allure.title("Calculate for year 2100")
    def test_far_future_date(self):
        """Can calculate for dates far in the future."""
        with allure.step("Set date: Year 2100 (JD 2488070.0)"):
            jd = JulianDate(2488070.0)

        with allure.step("Calculate Jupiter position"):
            pos = planet_position(Planet.JUPITER, jd)

        with allure.step(f"RA = {pos.ra.degrees:.2f}°, Dec = {pos.dec.degrees:.2f}°"):
            assert isinstance(pos, PlanetPosition)
            assert 0 <= pos.ra.degrees < 360

    @allure.title("Calculate for year 1900")
    def test_far_past_date(self):
        """Can calculate for dates in the past."""
        with allure.step("Set date: Year 1900 (JD 2415021.0)"):
            jd = JulianDate(2415021.0)

        with allure.step("Calculate Saturn position"):
            pos = planet_position(Planet.SATURN, jd)

        with allure.step(f"RA = {pos.ra.degrees:.2f}°, Dec = {pos.dec.degrees:.2f}°"):
            assert isinstance(pos, PlanetPosition)
            assert 0 <= pos.ra.degrees < 360

    @allure.title("All planets at same instant")
    def test_all_planets_at_same_time(self):
        """Can calculate all planets at the same instant."""
        with allure.step("Set date: J2000.0"):
            jd = JulianDate(2451545.0)

        with allure.step("Get all planet positions"):
            positions = all_planet_positions(jd)

        with allure.step("Verify all have valid RA/Dec"):
            for planet, pos in positions.items():
                with allure.step(f"{planet.value}: RA={pos.ra.degrees:.1f}°, Dec={pos.dec.degrees:.1f}°"):
                    assert 0 <= pos.ra.degrees < 360
                    assert -90 <= pos.dec.degrees <= 90
