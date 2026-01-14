"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           COORDINATE TESTS                                   ║
║                                                                              ║
║  Tests for celestial coordinate systems and transformations.                 ║
║                                                                              ║
║  Astronomy uses multiple coordinate systems, each suited to different        ║
║  purposes:                                                                   ║
║                                                                              ║
║  • ICRS (International Celestial Reference System)                           ║
║    - Right Ascension (RA): 0-24h, measured from vernal equinox               ║
║    - Declination (Dec): ±90°, measured from celestial equator                ║
║    - Standard system for star catalogs and precise positions                 ║
║                                                                              ║
║  • Galactic Coordinates                                                      ║
║    - Longitude (l): 0-360°, measured from galactic center direction          ║
║    - Latitude (b): ±90°, measured from galactic plane                        ║
║    - Used for studying Milky Way structure                                   ║
║                                                                              ║
║  • Horizontal (Alt-Az)                                                       ║
║    - Altitude: 0-90° above horizon (-90° below)                              ║
║    - Azimuth: 0-360° from north through east                                 ║
║    - Observer-specific, changes with time and location                       ║
║                                                                              ║
║  Accurate coordinate transformations are essential for planning              ║
║  observations and interpreting astronomical data.                            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import math
import allure
import pytest

from starward.core.coords import (
    ICRSCoord, GalacticCoord, HorizontalCoord, transform_coords
)
from starward.core.angles import Angle
from starward.core.time import JulianDate
from starward.verbose import VerboseContext


# ═══════════════════════════════════════════════════════════════════════════════
#  ICRS COORDINATES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("ICRS Coordinates")
class TestICRSCoord:
    """
    Tests for ICRS (International Celestial Reference System) coordinates.

    ICRS is the standard celestial reference system, aligned with the
    celestial equator (Earth's equator projected onto the sky) and the
    vernal equinox (where the Sun crosses the celestial equator in spring).

    RA ranges 0-24h (or 0-360°), increasing eastward.
    Dec ranges -90° (south pole) to +90° (north pole).
    """

    @allure.title("Create ICRS from degrees")
    def test_creation_from_degrees(self):
        """
        Verify ICRS coordinate creation from decimal degrees.

        Decimal degrees are commonly used in databases and for
        computational purposes.
        """
        with allure.step("Create ICRSCoord.from_degrees(180.0, 45.0)"):
            coord = ICRSCoord.from_degrees(180.0, 45.0)
        with allure.step(f"RA = {coord.ra.degrees}°, Dec = {coord.dec.degrees}°"):
            assert math.isclose(coord.ra.degrees, 180.0, rel_tol=1e-10)
            assert math.isclose(coord.dec.degrees, 45.0, rel_tol=1e-10)

    @allure.title("Create ICRS from HMS/DMS")
    def test_creation_from_hms_dms(self):
        """
        Verify ICRS coordinate creation from sexagesimal notation.

        HMS/DMS format is traditional in astronomy and commonly used
        in star catalogs and observing lists.
        """
        with allure.step("Create ICRSCoord.from_hms_dms(12, 0, 0, 45, 0, 0)"):
            coord = ICRSCoord.from_hms_dms(12, 0, 0, 45, 0, 0)
        with allure.step(f"RA = {coord.ra.hours}h, Dec = {coord.dec.degrees}°"):
            assert math.isclose(coord.ra.hours, 12.0, rel_tol=1e-10)
            assert math.isclose(coord.dec.degrees, 45.0, rel_tol=1e-10)

    @allure.title("Declination must be in [-90, 90]")
    def test_declination_validation(self):
        """
        Verify that invalid declination values are rejected.

        Declination is bounded by ±90° (the celestial poles).
        Values outside this range are physically meaningless.
        """
        with allure.step("Test Dec = +91° (invalid)"):
            with pytest.raises(ValueError, match="Declination"):
                ICRSCoord.from_degrees(0, 91)

        with allure.step("Test Dec = -91° (invalid)"):
            with pytest.raises(ValueError, match="Declination"):
                ICRSCoord.from_degrees(0, -91)

    @allure.title("Parse HMS/DMS string")
    def test_parse_hms_dms(self):
        """
        Verify parsing of standard coordinate string format.

        This format is ubiquitous in astronomical publications
        and online databases.
        """
        with allure.step("Parse '12h30m00s +45d30m00s'"):
            coord = ICRSCoord.parse("12h30m00s +45d30m00s")
        with allure.step(f"RA = {coord.ra.hours}h, Dec = {coord.dec.degrees}°"):
            assert math.isclose(coord.ra.hours, 12.5, rel_tol=1e-10)
            assert math.isclose(coord.dec.degrees, 45.5, rel_tol=1e-10)

    @allure.title("Parse decimal degrees")
    def test_parse_decimal(self):
        """
        Verify parsing of decimal degree format.

        Space-separated decimal values are common in data files
        and computational applications.
        """
        with allure.step("Parse '187.5 45.5'"):
            coord = ICRSCoord.parse("187.5 45.5")
        with allure.step(f"RA = {coord.ra.degrees}°, Dec = {coord.dec.degrees}°"):
            assert math.isclose(coord.ra.degrees, 187.5, rel_tol=1e-10)
            assert math.isclose(coord.dec.degrees, 45.5, rel_tol=1e-10)

    @allure.title("to_icrs() returns self")
    def test_to_icrs_returns_self(self):
        """
        Verify that converting ICRS to ICRS returns the same object.

        This is an identity operation optimization - no computation
        needed when source and target systems are the same.
        """
        with allure.step("Create ICRS coord"):
            coord = ICRSCoord.from_degrees(180, 45)
        with allure.step("Call to_icrs()"):
            result = coord.to_icrs()
        with allure.step("Result is same object"):
            assert result is coord


# ═══════════════════════════════════════════════════════════════════════════════
#  GALACTIC COORDINATES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Galactic Coordinates")
class TestGalacticCoord:
    """
    Tests for Galactic coordinate system.

    Galactic coordinates are centered on the Sun, with:
    - Longitude (l) measured in the galactic plane from the direction
      of the galactic center (Sagittarius A*)
    - Latitude (b) measured perpendicular to the galactic plane

    This system is essential for studying the structure and dynamics
    of the Milky Way galaxy.
    """

    @allure.title("Create Galactic from degrees")
    def test_creation_from_degrees(self):
        """
        Verify Galactic coordinate creation from decimal degrees.
        """
        with allure.step("Create GalacticCoord.from_degrees(90.0, 30.0)"):
            coord = GalacticCoord.from_degrees(90.0, 30.0)
        with allure.step(f"l = {coord.l.degrees}°, b = {coord.b.degrees}°"):
            assert math.isclose(coord.l.degrees, 90.0, rel_tol=1e-10)
            assert math.isclose(coord.b.degrees, 30.0, rel_tol=1e-10)

    @allure.title("Galactic latitude must be in [-90, 90]")
    def test_latitude_validation(self):
        """
        Verify that invalid galactic latitude is rejected.

        Like declination, galactic latitude is bounded by ±90°.
        """
        with allure.step("Test b = +91° (invalid)"):
            with pytest.raises(ValueError):
                GalacticCoord.from_degrees(0, 91)


# ═══════════════════════════════════════════════════════════════════════════════
#  ICRS ↔ GALACTIC TRANSFORMATION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("ICRS ↔ Galactic Transformation")
class TestGalacticICRSTransform:
    """
    Tests for transformations between ICRS and Galactic coordinates.

    The transformation involves a rotation of the coordinate frame
    defined by the position of the North Galactic Pole and the
    direction of the galactic center in ICRS coordinates.

    These are well-defined transformations that should be reversible
    to high precision.
    """

    @allure.title("Galactic center → ICRS near Sgr A*")
    def test_galactic_center_to_icrs(self):
        """
        Verify that the Galactic center transforms to the known position of Sgr A*.

        Sagittarius A* (the supermassive black hole at the galactic center)
        is at approximately RA 17h45m40s, Dec -29°00'28" (J2000).
        The Galactic center (l=0°, b=0°) should transform to this location.
        """
        with allure.step("Create Galactic center (l=0°, b=0°)"):
            gc = GalacticCoord.from_degrees(0.0, 0.0)
        with allure.step("Transform to ICRS"):
            icrs = gc.to_icrs()
        with allure.step(f"RA = {icrs.ra.degrees:.1f}°, Dec = {icrs.dec.degrees:.1f}°"):
            # Sgr A* position: ~266.4° RA, ~-29° Dec
            assert 265 < icrs.ra.degrees < 268
            assert -30 < icrs.dec.degrees < -28

    @allure.title("North Galactic Pole → ICRS (RA ~192.86°, Dec ~27.13°)")
    def test_galactic_pole_to_icrs(self):
        """
        Verify the North Galactic Pole transformation.

        The NGP position in ICRS is defined by IAU convention:
        RA = 192.85948° (12h51m26.28s), Dec = +27.12825° (+27°07'41.7")

        This test validates our coordinate transformation implementation.
        """
        with allure.step("Create NGP (l=0°, b=90°)"):
            ngp = GalacticCoord.from_degrees(0.0, 90.0)
        with allure.step("Transform to ICRS"):
            icrs = ngp.to_icrs()
        with allure.step(f"RA = {icrs.ra.degrees:.2f}°, Dec = {icrs.dec.degrees:.2f}°"):
            assert math.isclose(icrs.ra.degrees, 192.86, abs_tol=0.1)
            assert math.isclose(icrs.dec.degrees, 27.13, abs_tol=0.1)

    @allure.title("ICRS → Galactic → ICRS roundtrip")
    def test_icrs_to_galactic_roundtrip(self):
        """
        Verify that ICRS → Galactic → ICRS returns the original coordinates.

        Coordinate transformations should be reversible to high precision.
        Roundtrip errors indicate implementation bugs.
        """
        with allure.step("Create ICRS (RA=187.5°, Dec=45.5°)"):
            original = ICRSCoord.from_degrees(187.5, 45.5)
        with allure.step("Convert to Galactic"):
            galactic = original.to_galactic()
        with allure.step("Convert back to ICRS"):
            back = galactic.to_icrs()
        with allure.step(f"Original RA={original.ra.degrees}°, Back RA={back.ra.degrees}°"):
            assert math.isclose(original.ra.degrees, back.ra.degrees, abs_tol=1e-8)
            assert math.isclose(original.dec.degrees, back.dec.degrees, abs_tol=1e-8)

    @allure.title("Galactic → ICRS → Galactic roundtrip")
    def test_galactic_to_icrs_roundtrip(self):
        """
        Verify that Galactic → ICRS → Galactic returns the original coordinates.

        Both directions of the roundtrip should work equally well.
        """
        with allure.step("Create Galactic (l=90°, b=30°)"):
            original = GalacticCoord.from_degrees(90.0, 30.0)
        with allure.step("Convert to ICRS"):
            icrs = original.to_icrs()
        with allure.step("Convert back to Galactic"):
            back = GalacticCoord.from_icrs(icrs)
        with allure.step(f"Original l={original.l.degrees}°, Back l={back.l.degrees}°"):
            assert math.isclose(original.l.degrees, back.l.degrees, abs_tol=1e-8)
            assert math.isclose(original.b.degrees, back.b.degrees, abs_tol=1e-8)


# ═══════════════════════════════════════════════════════════════════════════════
#  HORIZONTAL COORDINATES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Horizontal Coordinates")
class TestHorizontalCoord:
    """
    Tests for Horizontal (Alt-Az) coordinate system.

    Horizontal coordinates describe positions as seen by an observer:
    - Altitude: angle above the horizon (0° = horizon, 90° = zenith)
    - Azimuth: compass direction (0° = north, 90° = east, etc.)

    Unlike ICRS and Galactic, horizontal coordinates depend on:
    - Observer's geographic location (latitude and longitude)
    - Time of observation (as Earth rotates)

    These tests verify altitude/azimuth creation and airmass calculations.
    """

    @allure.title("Create Horizontal from degrees")
    def test_creation_from_degrees(self):
        """
        Verify Horizontal coordinate creation from degrees.
        """
        with allure.step("Create HorizontalCoord.from_degrees(45.0, 180.0)"):
            coord = HorizontalCoord.from_degrees(45.0, 180.0)
        with allure.step(f"Alt = {coord.alt.degrees}°, Az = {coord.az.degrees}°"):
            assert math.isclose(coord.alt.degrees, 45.0, rel_tol=1e-10)
            assert math.isclose(coord.az.degrees, 180.0, rel_tol=1e-10)

    @allure.title("Altitude must be in [-90, 90]")
    def test_altitude_validation(self):
        """
        Verify that invalid altitude values are rejected.

        Altitude above 90° is undefined (zenith is maximum),
        though negative values represent objects below the horizon.
        """
        with allure.step("Test Alt = +91° (invalid)"):
            with pytest.raises(ValueError):
                HorizontalCoord.from_degrees(91, 0)

    @allure.title("Airmass at zenith ≈ 1.0")
    def test_airmass_zenith(self):
        """
        Verify airmass calculation at the zenith.

        Airmass measures how much atmosphere light passes through.
        At zenith (alt=90°), light takes the shortest path, giving
        airmass ≈ 1.0 (one atmosphere thickness).
        """
        with allure.step("Create zenith (Alt=90°)"):
            coord = HorizontalCoord.from_degrees(90.0, 0.0)
        with allure.step(f"Airmass = {coord.airmass:.3f}"):
            assert math.isclose(coord.airmass, 1.0, rel_tol=0.01)

    @allure.title("Airmass at 45° ≈ 1.41")
    def test_airmass_45_degrees(self):
        """
        Verify airmass at 45° altitude.

        At 45°, light passes through √2 ≈ 1.41 times more atmosphere
        than at zenith (simple secant approximation). Accurate airmass
        formulas account for atmospheric refraction and curvature.
        """
        with allure.step("Create coord (Alt=45°)"):
            coord = HorizontalCoord.from_degrees(45.0, 0.0)
        with allure.step(f"Airmass = {coord.airmass:.3f}"):
            assert math.isclose(coord.airmass, 1.41, rel_tol=0.02)

    @allure.title("Airmass near horizon is very large")
    def test_airmass_horizon(self):
        """
        Verify airmass increases dramatically near the horizon.

        At low altitudes, light passes through many times more
        atmosphere, causing significant extinction and seeing degradation.
        Most observations are limited to altitudes above 30° for this reason.
        """
        with allure.step("Create coord (Alt=1°)"):
            coord = HorizontalCoord.from_degrees(1.0, 0.0)
        with allure.step(f"Airmass = {coord.airmass:.1f} (> 25)"):
            assert coord.airmass > 25

    @allure.title("Airmass below horizon = ∞")
    def test_airmass_below_horizon(self):
        """
        Verify airmass is infinite for objects below the horizon.

        Objects below the horizon cannot be observed (negative altitude),
        so airmass is undefined/infinite.
        """
        with allure.step("Create coord (Alt=-5°)"):
            coord = HorizontalCoord.from_degrees(-5.0, 0.0)
        with allure.step("Airmass = inf"):
            assert coord.airmass == float('inf')

    @allure.title("Zenith angle = 90° - altitude")
    def test_zenith_angle(self):
        """
        Verify zenith angle calculation.

        Zenith angle (z) is the complement of altitude (a): z = 90° - a.
        At zenith, z = 0°; at horizon, z = 90°.
        """
        with allure.step("Create coord (Alt=60°)"):
            coord = HorizontalCoord.from_degrees(60.0, 0.0)
        with allure.step(f"Zenith angle = {coord.zenith_angle.degrees}°"):
            assert math.isclose(coord.zenith_angle.degrees, 30.0, rel_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  ICRS → HORIZONTAL TRANSFORMATION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("ICRS → Horizontal Transformation")
class TestICRSToHorizontal:
    """
    Tests for transforming ICRS coordinates to horizontal (alt-az).

    This transformation requires:
    - Observer's geographic position (latitude, longitude)
    - Time of observation (as Julian Date)

    The transformation involves:
    1. Computing Local Sidereal Time from JD and longitude
    2. Converting RA/Dec to Hour Angle/Dec
    3. Rotating to the local horizon frame
    """

    @allure.title("Requires JD, lat, lon parameters")
    def test_requires_parameters(self):
        """
        Verify that horizontal transformation requires all parameters.

        Without time and location, horizontal coordinates are undefined.
        """
        with allure.step("Create ICRS coord"):
            coord = ICRSCoord.from_degrees(0, 0)
        with allure.step("Call from_icrs without parameters"):
            with pytest.raises(ValueError, match="jd, lat, and lon are required"):
                HorizontalCoord.from_icrs(coord)

    @allure.title("Object at RA=LST, Dec=lat is at zenith")
    def test_zenith_at_lst(self):
        """
        Verify that an object with RA = LST and Dec = latitude is at zenith.

        When a star's Right Ascension equals the Local Sidereal Time,
        it's crossing the observer's meridian. If its declination also
        equals the observer's latitude, it passes directly overhead.
        """
        with allure.step("Set test JD and location"):
            jd = JulianDate(2460000.5)
            lat = Angle(degrees=40.0)
            lon = Angle(degrees=-75.0)

        with allure.step("Get LST at this time and location"):
            lst = jd.lst(lon.degrees)

        with allure.step(f"Create star at RA={lst:.2f}h, Dec={lat.degrees}°"):
            coord = ICRSCoord(Angle(hours=lst), lat)

        with allure.step("Transform to horizontal"):
            horiz = HorizontalCoord.from_icrs(coord, jd=jd, lat=lat, lon=lon)

        with allure.step(f"Altitude = {horiz.alt.degrees:.1f}° (should be ~90°)"):
            assert horiz.alt.degrees > 89.9

    @allure.title("NCP altitude = observer latitude")
    def test_north_celestial_pole(self):
        """
        Verify that the North Celestial Pole altitude equals observer latitude.

        The NCP (Dec = +90°) appears at an altitude equal to the observer's
        latitude. At the equator, it's on the horizon; at the poles, it's
        at zenith. This is a fundamental result of spherical astronomy.
        """
        with allure.step("Set observer at lat=40°N"):
            jd = JulianDate.j2000()
            lat = Angle(degrees=40.0)
            lon = Angle(degrees=0.0)

        with allure.step("Create NCP (Dec=90°)"):
            ncp = ICRSCoord.from_degrees(0, 90)

        with allure.step("Transform to horizontal"):
            horiz = HorizontalCoord.from_icrs(ncp, jd=jd, lat=lat, lon=lon)

        with allure.step(f"Altitude = {horiz.alt.degrees:.1f}° (should ≈ 40°)"):
            assert math.isclose(horiz.alt.degrees, lat.degrees, abs_tol=0.1)

        with allure.step(f"Azimuth = {horiz.az.degrees:.1f}° (should ≈ 0° North)"):
            # NCP is due north
            assert horiz.az.degrees < 1 or horiz.az.degrees > 359


# ═══════════════════════════════════════════════════════════════════════════════
#  TRANSFORM FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Transform Function")
class TestTransformCoords:
    """
    Tests for the unified transform_coords() function.

    This function provides a convenient interface for coordinate
    transformations, accepting coordinate system names as strings
    and handling the appropriate conversions automatically.
    """

    @allure.title("ICRS → Galactic")
    def test_icrs_to_galactic(self):
        """
        Verify ICRS to Galactic transformation via transform_coords().
        """
        with allure.step("Create ICRS (187.5°, 45.5°)"):
            coord = ICRSCoord.from_degrees(187.5, 45.5)
        with allure.step("Transform to 'galactic'"):
            result = transform_coords(coord, 'galactic')
        with allure.step(f"Result type: {type(result).__name__}"):
            assert isinstance(result, GalacticCoord)

    @allure.title("Galactic → ICRS")
    def test_galactic_to_icrs(self):
        """
        Verify Galactic to ICRS transformation via transform_coords().
        """
        with allure.step("Create Galactic (90°, 30°)"):
            coord = GalacticCoord.from_degrees(90, 30)
        with allure.step("Transform to 'icrs'"):
            result = transform_coords(coord, 'icrs')
        with allure.step(f"Result type: {type(result).__name__}"):
            assert isinstance(result, ICRSCoord)

    @allure.title("System aliases work (gal, j2000, equatorial)")
    def test_aliases(self):
        """
        Verify that coordinate system aliases are recognized.

        Multiple names for the same system improves usability:
        - 'galactic', 'gal', 'GALACTIC' all work
        - 'icrs', 'j2000', 'equatorial' all work
        """
        with allure.step("Create ICRS coord"):
            coord = ICRSCoord.from_degrees(180, 45)

        with allure.step("Test galactic aliases"):
            for alias in ['galactic', 'gal', 'GALACTIC']:
                result = transform_coords(coord, alias)
                assert isinstance(result, GalacticCoord)

        with allure.step("Test ICRS aliases"):
            for alias in ['icrs', 'j2000', 'equatorial', 'ICRS']:
                result = transform_coords(coord, alias)
                assert isinstance(result, ICRSCoord)

    @allure.title("Unknown system raises ValueError")
    def test_unknown_system(self):
        """
        Verify that unknown coordinate systems are rejected with clear errors.
        """
        with allure.step("Create ICRS coord"):
            coord = ICRSCoord.from_degrees(180, 45)
        with allure.step("Transform to 'xyz' (invalid)"):
            with pytest.raises(ValueError, match="Unknown"):
                transform_coords(coord, 'xyz')

    @allure.title("Verbose mode produces steps")
    def test_verbose(self):
        """
        Verify that verbose mode captures transformation steps.

        Verbose output shows the rotation matrix and intermediate
        calculations, valuable for educational purposes.
        """
        with allure.step("Create verbose context"):
            ctx = VerboseContext()
        with allure.step("Transform with verbose=ctx"):
            coord = ICRSCoord.from_degrees(187.5, 45.5)
            transform_coords(coord, 'galactic', verbose=ctx)
        with allure.step(f"Verbose steps: {len(ctx.steps)}"):
            assert len(ctx.steps) > 0


# ═══════════════════════════════════════════════════════════════════════════════
#  KNOWN COORDINATES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Known Coordinates")
class TestKnownCoordinates:
    """
    Tests against well-established reference coordinates.

    Validating against known positions of famous stars ensures
    our transformations are correct in practice, not just mathematically.
    """

    KNOWN_OBJECTS = [
        # (name, ra_h, ra_m, ra_s, dec_d, dec_m, dec_s, l, b)
        # Vega: A0V star, one of the brightest in the sky
        ("Vega", 18, 36, 56.3, 38, 47, 1, 67.45, 19.24),
    ]

    @allure.title("Vega: ICRS → Galactic matches known values")
    @pytest.mark.parametrize("name,ra_h,ra_m,ra_s,dec_d,dec_m,dec_s,l_exp,b_exp", KNOWN_OBJECTS)
    def test_known_galactic(self, name, ra_h, ra_m, ra_s, dec_d, dec_m, dec_s, l_exp, b_exp):
        """
        Verify ICRS to Galactic transformation for well-known stars.

        Vega (α Lyrae) is a well-studied star with precisely known
        coordinates, making it ideal for validation.
        """
        with allure.step(f"Create {name} ICRS: {ra_h}h{ra_m}m{ra_s}s {dec_d}°{dec_m}′{dec_s}″"):
            coord = ICRSCoord.from_hms_dms(ra_h, ra_m, ra_s, dec_d, dec_m, dec_s)

        with allure.step("Transform to Galactic"):
            gal = coord.to_galactic()

        with allure.step(f"l = {gal.l.degrees:.2f}° (expected {l_exp}°)"):
            assert math.isclose(gal.l.degrees, l_exp, abs_tol=1.0), f"{name}: l mismatch"

        with allure.step(f"b = {gal.b.degrees:.2f}° (expected {b_exp}°)"):
            assert math.isclose(gal.b.degrees, b_exp, abs_tol=1.0), f"{name}: b mismatch"
