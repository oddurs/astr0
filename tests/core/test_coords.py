"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           COORDINATE TESTS                                   ║
║                                                                              ║
║  Tests for celestial coordinate systems and transformations.                 ║
║  Supports ICRS, Galactic, and Horizontal coordinate frames.                  ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import math
import allure
import pytest
from hypothesis import given, strategies as st, settings

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
    Tests for the International Celestial Reference System (ICRS).

    ICRS is the fundamental celestial reference frame aligned with
    the J2000.0 equator and equinox.
    """

    # ─── Construction ───────────────────────────────────────────────────────

    @allure.title("Create ICRS from decimal degrees")
    def test_from_degrees(self):
        """Create ICRS coordinate from decimal degrees."""
        with allure.step("Create coordinate: RA=180°, Dec=45°"):
            coord = ICRSCoord.from_degrees(180.0, 45.0)

        with allure.step(f"RA = {coord.ra.degrees}° (expected 180.0)"):
            assert math.isclose(coord.ra.degrees, 180.0, rel_tol=1e-10)

        with allure.step(f"Dec = {coord.dec.degrees}° (expected 45.0)"):
            assert math.isclose(coord.dec.degrees, 45.0, rel_tol=1e-10)

    @allure.title("Create ICRS from HMS/DMS")
    def test_from_hms_dms(self):
        """Create ICRS coordinate from HMS/DMS."""
        with allure.step("Create coordinate: 12h 0m 0s +45° 0' 0\""):
            coord = ICRSCoord.from_hms_dms(12, 0, 0, 45, 0, 0)

        with allure.step(f"RA = {coord.ra.hours}h (expected 12.0)"):
            assert math.isclose(coord.ra.hours, 12.0, rel_tol=1e-10)

        with allure.step(f"Dec = {coord.dec.degrees}° (expected 45.0)"):
            assert math.isclose(coord.dec.degrees, 45.0, rel_tol=1e-10)

    # ─── Parsing ────────────────────────────────────────────────────────────

    @allure.title("Parse coordinate from HMS/DMS string")
    def test_parse_hms_dms(self):
        """Parse coordinate from HMS/DMS string."""
        with allure.step("Parse '12h30m00s +45d30m00s'"):
            coord = ICRSCoord.parse("12h30m00s +45d30m00s")

        with allure.step(f"RA = {coord.ra.hours}h (expected 12.5)"):
            assert math.isclose(coord.ra.hours, 12.5, rel_tol=1e-10)

        with allure.step(f"Dec = {coord.dec.degrees}° (expected 45.5)"):
            assert math.isclose(coord.dec.degrees, 45.5, rel_tol=1e-10)

    @allure.title("Parse coordinate from decimal string")
    def test_parse_decimal(self):
        """Parse coordinate from decimal string."""
        with allure.step("Parse '187.5 45.5'"):
            coord = ICRSCoord.parse("187.5 45.5")

        with allure.step(f"RA = {coord.ra.degrees}° (expected 187.5)"):
            assert math.isclose(coord.ra.degrees, 187.5, rel_tol=1e-10)

        with allure.step(f"Dec = {coord.dec.degrees}° (expected 45.5)"):
            assert math.isclose(coord.dec.degrees, 45.5, rel_tol=1e-10)

    @allure.title("Parse coordinate with negative declination")
    def test_parse_negative_dec(self):
        """Parse coordinate with negative declination."""
        with allure.step("Parse '06h45m09s -16d42m58s' (Sirius-like)"):
            coord = ICRSCoord.parse("06h45m09s -16d42m58s")

        with allure.step(f"Dec = {coord.dec.degrees}° (expected < 0)"):
            assert coord.dec.degrees < 0

    # ─── Validation ─────────────────────────────────────────────────────────

    @allure.title("Declination > 90° raises ValueError")
    def test_declination_upper_bound(self):
        """Declination > 90° is invalid."""
        with allure.step("Attempt to create coordinate with Dec=91°"):
            with pytest.raises(ValueError, match="Declination"):
                ICRSCoord.from_degrees(0, 91)

    @allure.title("Declination < -90° raises ValueError")
    def test_declination_lower_bound(self):
        """Declination < -90° is invalid."""
        with allure.step("Attempt to create coordinate with Dec=-91°"):
            with pytest.raises(ValueError, match="Declination"):
                ICRSCoord.from_degrees(0, -91)

    @pytest.mark.edge
    @allure.title("Declination at poles (±90°) is valid")
    def test_declination_at_poles(self):
        """Dec = ±90° is valid."""
        with allure.step("Create North Celestial Pole (Dec=90°)"):
            north = ICRSCoord.from_degrees(0, 90)

        with allure.step("Create South Celestial Pole (Dec=-90°)"):
            south = ICRSCoord.from_degrees(0, -90)

        with allure.step(f"North pole Dec = {north.dec.degrees}°"):
            assert north.dec.degrees == 90

        with allure.step(f"South pole Dec = {south.dec.degrees}°"):
            assert south.dec.degrees == -90

    # ─── Identity Transform ─────────────────────────────────────────────────

    @allure.title("to_icrs() returns self")
    def test_to_icrs_returns_self(self):
        """Converting ICRS to ICRS returns self."""
        with allure.step("Create ICRS coordinate"):
            coord = ICRSCoord.from_degrees(180, 45)

        with allure.step("Call to_icrs()"):
            result = coord.to_icrs()

        with allure.step("Verify returns same object"):
            assert result is coord


# ═══════════════════════════════════════════════════════════════════════════════
#  GALACTIC COORDINATES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Galactic Coordinates")
class TestGalacticCoord:
    """
    Tests for Galactic coordinate system.

    Centered on the Milky Way:
      - l (longitude): 0° toward Galactic center
      - b (latitude): 0° in Galactic plane, ±90° at poles
    """

    # ─── Construction ───────────────────────────────────────────────────────

    @allure.title("Create Galactic coordinate from degrees")
    def test_from_degrees(self):
        """Create Galactic coordinate from degrees."""
        with allure.step("Create coordinate: l=90°, b=30°"):
            coord = GalacticCoord.from_degrees(90.0, 30.0)

        with allure.step(f"l = {coord.l.degrees}° (expected 90.0)"):
            assert math.isclose(coord.l.degrees, 90.0, rel_tol=1e-10)

        with allure.step(f"b = {coord.b.degrees}° (expected 30.0)"):
            assert math.isclose(coord.b.degrees, 30.0, rel_tol=1e-10)

    # ─── Validation ─────────────────────────────────────────────────────────

    @allure.title("Galactic latitude must be in [-90, 90]")
    def test_latitude_bounds(self):
        """Galactic latitude must be in [-90, 90]."""
        with allure.step("Attempt b=91° (should fail)"):
            with pytest.raises(ValueError):
                GalacticCoord.from_degrees(0, 91)

        with allure.step("Attempt b=-91° (should fail)"):
            with pytest.raises(ValueError):
                GalacticCoord.from_degrees(0, -91)


# ═══════════════════════════════════════════════════════════════════════════════
#  ICRS ↔ GALACTIC TRANSFORMATIONS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Galactic-ICRS Transformations")
class TestGalacticICRSTransform:
    """
    Tests for ICRS ↔ Galactic coordinate transformations.

    These transforms use the IAU-defined Galactic coordinate system
    with the North Galactic Pole at (RA=192.86°, Dec=27.13°).
    """

    @pytest.mark.golden
    @allure.title("Galactic center → ICRS (Sgr A* region)")
    @allure.description("""
    Galactic center (l=0°, b=0°) transforms to the Sgr A* region.
    Expected: RA ≈ 266.4°, Dec ≈ -29°
    """)
    def test_galactic_center_to_icrs(self):
        """Galactic center (l=0°, b=0°) transforms to Sgr A* region."""
        with allure.step("Create Galactic center (l=0°, b=0°)"):
            gc = GalacticCoord.from_degrees(0.0, 0.0)

        with allure.step("Transform to ICRS"):
            icrs = gc.to_icrs()

        with allure.step(f"RA = {icrs.ra.degrees:.2f}° (expected 265-268°)"):
            assert 265 < icrs.ra.degrees < 268

        with allure.step(f"Dec = {icrs.dec.degrees:.2f}° (expected -30 to -28°)"):
            assert -30 < icrs.dec.degrees < -28

    @pytest.mark.golden
    @allure.title("North Galactic Pole → ICRS (fixed point)")
    @allure.description("""
    North Galactic Pole (l=any, b=90°) transforms to fixed ICRS point.
    Expected: RA ≈ 192.86°, Dec ≈ 27.13° (by IAU definition)
    """)
    def test_north_galactic_pole_to_icrs(self):
        """North Galactic Pole transforms to fixed ICRS point."""
        with allure.step("Create NGP (l=0°, b=90°)"):
            ngp = GalacticCoord.from_degrees(0.0, 90.0)

        with allure.step("Transform to ICRS"):
            icrs = ngp.to_icrs()

        with allure.step(f"RA = {icrs.ra.degrees:.2f}° (expected ≈192.86°)"):
            assert math.isclose(icrs.ra.degrees, 192.86, abs_tol=0.1)

        with allure.step(f"Dec = {icrs.dec.degrees:.2f}° (expected ≈27.13°)"):
            assert math.isclose(icrs.dec.degrees, 27.13, abs_tol=0.1)

    @pytest.mark.roundtrip
    @allure.title("ICRS → Galactic → ICRS roundtrip")
    def test_icrs_to_galactic_roundtrip(self):
        """ICRS → Galactic → ICRS preserves coordinates."""
        with allure.step("Create original ICRS (187.5°, 45.5°)"):
            original = ICRSCoord.from_degrees(187.5, 45.5)

        with allure.step("Transform to Galactic"):
            galactic = original.to_galactic()

        with allure.step(f"Galactic: l={galactic.l.degrees:.2f}°, b={galactic.b.degrees:.2f}°"):
            pass

        with allure.step("Transform back to ICRS"):
            back = galactic.to_icrs()

        with allure.step(f"Original: {original.ra.degrees:.6f}°, Back: {back.ra.degrees:.6f}°"):
            assert math.isclose(original.ra.degrees, back.ra.degrees, abs_tol=1e-8)
            assert math.isclose(original.dec.degrees, back.dec.degrees, abs_tol=1e-8)

    @pytest.mark.roundtrip
    @allure.title("Galactic → ICRS → Galactic roundtrip")
    def test_galactic_to_icrs_roundtrip(self):
        """Galactic → ICRS → Galactic preserves coordinates."""
        with allure.step("Create original Galactic (90°, 30°)"):
            original = GalacticCoord.from_degrees(90.0, 30.0)

        with allure.step("Transform to ICRS"):
            icrs = original.to_icrs()

        with allure.step("Transform back to Galactic"):
            back = GalacticCoord.from_icrs(icrs)

        with allure.step(f"Original l={original.l.degrees:.6f}°, Back l={back.l.degrees:.6f}°"):
            assert math.isclose(original.l.degrees, back.l.degrees, abs_tol=1e-8)
            assert math.isclose(original.b.degrees, back.b.degrees, abs_tol=1e-8)

    @pytest.mark.roundtrip
    @allure.title("Property test: Galactic ↔ ICRS roundtrip")
    @given(
        st.floats(min_value=0, max_value=360, allow_nan=False),
        st.floats(min_value=-89, max_value=89, allow_nan=False)
    )
    @settings(max_examples=100)
    def test_galactic_roundtrip_property(self, lon, lat):
        """Property test: Galactic ↔ ICRS roundtrip for arbitrary coords."""
        original = GalacticCoord.from_degrees(lon, lat)
        back = GalacticCoord.from_icrs(original.to_icrs())

        orig_l = original.l.degrees % 360
        back_l = back.l.degrees % 360

        assert math.isclose(orig_l, back_l, abs_tol=1e-6) or \
               math.isclose(abs(orig_l - back_l), 360, abs_tol=1e-6)
        assert math.isclose(original.b.degrees, back.b.degrees, abs_tol=1e-6)


# ═══════════════════════════════════════════════════════════════════════════════
#  HORIZONTAL COORDINATES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Horizontal Coordinates")
class TestHorizontalCoord:
    """
    Tests for horizontal (alt-az) coordinate system.

    Observer-dependent coordinate system:
      - Alt (Altitude): -90° (nadir) to +90° (zenith)
      - Az (Azimuth): 0° = North, 90° = East, 180° = South
    """

    # ─── Construction ───────────────────────────────────────────────────────

    @allure.title("Create horizontal coordinate from degrees")
    def test_from_degrees(self):
        """Create horizontal coordinate from degrees."""
        with allure.step("Create coordinate: Alt=45°, Az=180°"):
            coord = HorizontalCoord.from_degrees(45.0, 180.0)

        with allure.step(f"Alt = {coord.alt.degrees}° (expected 45.0)"):
            assert math.isclose(coord.alt.degrees, 45.0, rel_tol=1e-10)

        with allure.step(f"Az = {coord.az.degrees}° (expected 180.0)"):
            assert math.isclose(coord.az.degrees, 180.0, rel_tol=1e-10)

    # ─── Validation ─────────────────────────────────────────────────────────

    @allure.title("Altitude must be in [-90, 90]")
    def test_altitude_bounds(self):
        """Altitude must be in [-90, 90]."""
        with allure.step("Attempt Alt=91° (should fail)"):
            with pytest.raises(ValueError):
                HorizontalCoord.from_degrees(91, 0)

        with allure.step("Attempt Alt=-91° (should fail)"):
            with pytest.raises(ValueError):
                HorizontalCoord.from_degrees(-91, 0)

    # ─── Airmass ────────────────────────────────────────────────────────────

    @pytest.mark.golden
    @allure.title("Airmass at zenith = 1.0")
    def test_airmass_at_zenith(self):
        """Airmass at zenith is 1.0."""
        with allure.step("Create coordinate at zenith (Alt=90°)"):
            coord = HorizontalCoord.from_degrees(90.0, 0.0)

        with allure.step(f"Airmass = {coord.airmass:.3f} (expected 1.0)"):
            assert math.isclose(coord.airmass, 1.0, rel_tol=0.01)

    @pytest.mark.golden
    @allure.title("Airmass at 45° ≈ √2 ≈ 1.41")
    def test_airmass_at_45_degrees(self):
        """Airmass at 45° ≈ √2 ≈ 1.41."""
        with allure.step("Create coordinate at Alt=45°"):
            coord = HorizontalCoord.from_degrees(45.0, 0.0)

        with allure.step(f"Airmass = {coord.airmass:.3f} (expected ≈1.41)"):
            assert math.isclose(coord.airmass, 1.41, rel_tol=0.02)

    @allure.title("Airmass near horizon is very large")
    def test_airmass_at_horizon(self):
        """Airmass near horizon is very large."""
        with allure.step("Create coordinate at Alt=1°"):
            coord = HorizontalCoord.from_degrees(1.0, 0.0)

        with allure.step(f"Airmass = {coord.airmass:.1f} (expected > 25)"):
            assert coord.airmass > 25

    @allure.title("Airmass below horizon is infinite")
    def test_airmass_below_horizon(self):
        """Airmass below horizon is infinite."""
        with allure.step("Create coordinate below horizon (Alt=-5°)"):
            coord = HorizontalCoord.from_degrees(-5.0, 0.0)

        with allure.step("Airmass = ∞"):
            assert coord.airmass == float('inf')

    # ─── Zenith Angle ───────────────────────────────────────────────────────

    @allure.title("Zenith angle = 90° - altitude")
    def test_zenith_angle(self):
        """Zenith angle = 90° - altitude."""
        with allure.step("Create coordinate at Alt=60°"):
            coord = HorizontalCoord.from_degrees(60.0, 0.0)

        with allure.step(f"Zenith angle = {coord.zenith_angle.degrees}° (expected 30°)"):
            assert math.isclose(coord.zenith_angle.degrees, 30.0, rel_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  ICRS → HORIZONTAL TRANSFORMATIONS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("ICRS to Horizontal")
class TestICRSToHorizontal:
    """
    Tests for ICRS → Horizontal coordinate transformation.

    This transform requires: Julian Date, Observer latitude, Observer longitude
    """

    @allure.title("Transform requires jd, lat, lon parameters")
    def test_requires_parameters(self):
        """Must provide jd, lat, lon for transformation."""
        with allure.step("Attempt transform without required params"):
            with pytest.raises(ValueError, match="jd, lat, and lon are required"):
                HorizontalCoord.from_icrs(ICRSCoord.from_degrees(0, 0))

    @pytest.mark.golden
    @allure.title("Object at RA=LST, Dec=lat is at zenith")
    def test_zenith_at_lst(self):
        """Object at RA=LST, Dec=lat is at zenith."""
        with allure.step("Set up observer at 40°N, 75°W"):
            jd = JulianDate(2460000.5)
            lat = Angle(degrees=40.0)
            lon = Angle(degrees=-75.0)

        with allure.step("Get LST at observer location"):
            lst = jd.lst(lon.degrees)

        with allure.step(f"LST = {lst:.2f}h"):
            pass

        with allure.step("Create star at RA=LST, Dec=lat"):
            coord = ICRSCoord(Angle(hours=lst), lat)

        with allure.step("Transform to horizontal"):
            horiz = HorizontalCoord.from_icrs(coord, jd=jd, lat=lat, lon=lon)

        with allure.step(f"Altitude = {horiz.alt.degrees:.2f}° (expected > 89.9°)"):
            assert horiz.alt.degrees > 89.9

    @pytest.mark.golden
    @allure.title("NCP altitude = observer latitude")
    def test_ncp_altitude_equals_latitude(self):
        """North Celestial Pole altitude = observer latitude."""
        with allure.step("Set up observer at 40°N"):
            jd = JulianDate.j2000()
            lat = Angle(degrees=40.0)
            lon = Angle(degrees=0.0)

        with allure.step("Create NCP (Dec=90°)"):
            ncp = ICRSCoord.from_degrees(0, 90)

        with allure.step("Transform to horizontal"):
            horiz = HorizontalCoord.from_icrs(ncp, jd=jd, lat=lat, lon=lon)

        with allure.step(f"NCP altitude = {horiz.alt.degrees:.2f}° (expected ≈40°)"):
            assert math.isclose(horiz.alt.degrees, lat.degrees, abs_tol=0.1)

    @allure.title("NCP azimuth is ~0° (North)")
    def test_ncp_azimuth_is_north(self):
        """NCP azimuth is ~0° (North)."""
        with allure.step("Set up observer"):
            jd = JulianDate.j2000()
            lat = Angle(degrees=40.0)
            lon = Angle(degrees=0.0)

        with allure.step("Transform NCP to horizontal"):
            ncp = ICRSCoord.from_degrees(0, 90)
            horiz = HorizontalCoord.from_icrs(ncp, jd=jd, lat=lat, lon=lon)

        with allure.step(f"Azimuth = {horiz.az.degrees:.2f}° (expected ≈0° or ≈360°)"):
            assert horiz.az.degrees < 1 or horiz.az.degrees > 359


# ═══════════════════════════════════════════════════════════════════════════════
#  TRANSFORM_COORDS INTERFACE
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Transform Coords Interface")
class TestTransformCoords:
    """
    Tests for the unified transform_coords() function.
    """

    @allure.title("Transform ICRS to Galactic via function")
    def test_icrs_to_galactic(self):
        """Transform ICRS to Galactic via function."""
        with allure.step("Create ICRS coordinate"):
            coord = ICRSCoord.from_degrees(187.5, 45.5)

        with allure.step("Transform to 'galactic'"):
            result = transform_coords(coord, 'galactic')

        with allure.step("Verify returns GalacticCoord"):
            assert isinstance(result, GalacticCoord)

    @allure.title("Transform Galactic to ICRS via function")
    def test_galactic_to_icrs(self):
        """Transform Galactic to ICRS via function."""
        with allure.step("Create Galactic coordinate"):
            coord = GalacticCoord.from_degrees(90, 30)

        with allure.step("Transform to 'icrs'"):
            result = transform_coords(coord, 'icrs')

        with allure.step("Verify returns ICRSCoord"):
            assert isinstance(result, ICRSCoord)

    @allure.title("System aliases work correctly")
    def test_system_aliases(self):
        """Various system aliases work correctly."""
        with allure.step("Create ICRS coordinate"):
            coord = ICRSCoord.from_degrees(180, 45)

        with allure.step("Test Galactic aliases"):
            for alias in ['galactic', 'gal', 'GALACTIC']:
                result = transform_coords(coord, alias)
                with allure.step(f"'{alias}' → GalacticCoord"):
                    assert isinstance(result, GalacticCoord)

        with allure.step("Test ICRS aliases"):
            for alias in ['icrs', 'j2000', 'equatorial', 'ICRS']:
                result = transform_coords(coord, alias)
                with allure.step(f"'{alias}' → ICRSCoord"):
                    assert isinstance(result, ICRSCoord)

    @allure.title("Unknown system raises ValueError")
    def test_unknown_system_raises(self):
        """Unknown coordinate system raises ValueError."""
        with allure.step("Create coordinate"):
            coord = ICRSCoord.from_degrees(180, 45)

        with allure.step("Transform to 'xyz' (unknown)"):
            with pytest.raises(ValueError, match="Unknown"):
                transform_coords(coord, 'xyz')

    @pytest.mark.verbose
    @allure.title("Verbose mode produces steps")
    def test_verbose_output(self):
        """Verbose mode produces steps."""
        with allure.step("Create VerboseContext"):
            ctx = VerboseContext()

        with allure.step("Transform with verbose=ctx"):
            coord = ICRSCoord.from_degrees(187.5, 45.5)
            transform_coords(coord, 'galactic', verbose=ctx)

        with allure.step(f"Produced {len(ctx.steps)} steps"):
            assert len(ctx.steps) > 0


# ═══════════════════════════════════════════════════════════════════════════════
#  KNOWN ASTRONOMICAL OBJECTS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Known Objects")
class TestKnownObjects:
    """
    Tests against authoritative coordinates of well-known objects.
    """

    @pytest.mark.golden
    @allure.title("Star Galactic coordinates verification")
    @pytest.mark.parametrize("name,ra_h,ra_m,ra_s,dec_d,dec_m,dec_s,l_exp,b_exp", [
        ("Vega", 18, 36, 56, 38, 47, 1, 67.45, 19.24),
        ("Polaris", 2, 31, 49, 89, 15, 51, 123.28, 26.46),
    ])
    def test_star_galactic_coords(self, name, ra_h, ra_m, ra_s,
                                    dec_d, dec_m, dec_s, l_exp, b_exp):
        """Verify ICRS → Galactic for known stars."""
        with allure.step(f"Create {name} ICRS coordinates"):
            coord = ICRSCoord.from_hms_dms(ra_h, ra_m, ra_s, dec_d, dec_m, dec_s)

        with allure.step("Transform to Galactic"):
            gal = coord.to_galactic()

        with allure.step(f"l = {gal.l.degrees:.2f}° (expected ≈{l_exp}°)"):
            assert math.isclose(gal.l.degrees, l_exp, abs_tol=1.0)

        with allure.step(f"b = {gal.b.degrees:.2f}° (expected ≈{b_exp}°)"):
            assert math.isclose(gal.b.degrees, b_exp, abs_tol=1.0)

    @allure.title("Verify Sirius coordinates from fixture")
    def test_sirius_coordinates(self, famous_stars):
        """Verify Sirius coordinates from fixture."""
        with allure.step("Get Sirius from fixture"):
            sirius = famous_stars['sirius']

        with allure.step(f"RA = {sirius.ra.hours:.2f}h (expected 6-7h)"):
            assert 6 < sirius.ra.hours < 7

        with allure.step(f"Dec = {sirius.dec.degrees:.2f}° (expected -17 to -16°)"):
            assert -17 < sirius.dec.degrees < -16

    @allure.title("Verify M31 coordinates from fixture")
    def test_m31_coordinates(self, messier_objects):
        """Verify M31 (Andromeda) coordinates from fixture."""
        with allure.step("Get M31 from fixture"):
            m31 = messier_objects['M31']

        with allure.step(f"RA = {m31.ra.hours:.2f}h (expected 0-1h)"):
            assert 0 < m31.ra.hours < 1

        with allure.step(f"Dec = {m31.dec.degrees:.2f}° (expected 41-42°)"):
            assert 41 < m31.dec.degrees < 42


# ═══════════════════════════════════════════════════════════════════════════════
#  EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Coordinate Edge Cases")
class TestCoordEdgeCases:
    """
    Tests for coordinate edge cases and boundary conditions.
    """

    @pytest.mark.edge
    @allure.title("RA indeterminate at celestial poles")
    def test_celestial_pole_ra_indeterminate(self):
        """At celestial poles, RA is indeterminate but transform works."""
        with allure.step("Create NCP with RA=0°"):
            pole1 = ICRSCoord.from_degrees(0, 90)

        with allure.step("Create NCP with RA=180°"):
            pole2 = ICRSCoord.from_degrees(180, 90)

        with allure.step("Both have Dec=90° (same pole)"):
            assert pole1.dec.degrees == pole2.dec.degrees == 90

    @pytest.mark.edge
    @allure.title("RA wraps at 0h/24h boundary")
    def test_ra_wrap_around(self):
        """RA wraps at 0h/24h boundary."""
        with allure.step("Create coord at RA=359.9°"):
            coord1 = ICRSCoord.from_degrees(359.9, 0)

        with allure.step("Create coord at RA=0.1°"):
            coord2 = ICRSCoord.from_degrees(0.1, 0)

        with allure.step("Calculate angular separation"):
            from starward.core.angles import angular_separation
            sep = angular_separation(coord1.ra, coord1.dec, coord2.ra, coord2.dec)

        with allure.step(f"Separation = {sep.degrees:.2f}° (expected < 0.3°)"):
            assert sep.degrees < 0.3
