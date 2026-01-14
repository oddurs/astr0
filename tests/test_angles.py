"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              ANGLE TESTS                                     ║
║                                                                              ║
║  Comprehensive tests for astronomical angle handling and calculations.       ║
║                                                                              ║
║  In astronomy, angles are fundamental measurements used to describe:         ║
║  • Celestial positions (Right Ascension, Declination)                        ║
║  • Angular distances between objects (separation)                            ║
║  • Directional relationships (position angle)                                ║
║  • Field of view and instrument specifications                               ║
║                                                                              ║
║  Angles can be expressed in multiple unit systems:                           ║
║  • Degrees (°): 360° in a full circle, common for declination                ║
║  • Hours (h): 24h in a full circle, used for Right Ascension                 ║
║  • Radians: 2π in a full circle, used in trigonometric calculations          ║
║  • Arcminutes (′) and arcseconds (″): subdivisions of degrees                ║
║                                                                              ║
║  The sexagesimal notation (base-60) dates back to Babylonian astronomy       ║
║  and remains standard in modern celestial coordinate systems.                ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import math
import allure
import pytest

from starward.core.angles import Angle, angular_separation, position_angle
from starward.verbose import VerboseContext


# ═══════════════════════════════════════════════════════════════════════════════
#  ANGLE CREATION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Angle Creation")
class TestAngleCreation:
    """
    Tests for Angle instantiation from various unit systems.

    The Angle class provides a unified interface for working with angular
    measurements, automatically handling conversions between different units.
    This is essential because astronomical data sources use varying formats:

    - Star catalogs often use hours for RA, degrees for Dec
    - Planetary ephemerides may use radians internally
    - Observer instruments might report in arcminutes or arcseconds

    The flexibility to create angles from any unit system and seamlessly
    convert between them is fundamental to astronomical software.
    """

    @allure.title("Create angle from degrees")
    def test_from_degrees(self):
        """
        Verify angle creation from decimal degrees.

        Degrees are the most intuitive unit for angles, with 360° in a full
        circle. Declination is always expressed in degrees (-90° to +90°).
        """
        with allure.step("Create Angle(degrees=45.5)"):
            a = Angle(degrees=45.5)
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)

    @allure.title("Create angle from radians")
    def test_from_radians(self):
        """
        Verify angle creation from radians.

        Radians are the natural unit for trigonometric functions. One radian
        is the angle subtended at the center of a circle by an arc equal in
        length to the radius. There are 2π radians in a full circle.

        π/4 radians = 45° (one-eighth of a circle)
        """
        with allure.step("Create Angle(radians=π/4)"):
            a = Angle(radians=math.pi / 4)
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 45.0, rel_tol=1e-10)

    @allure.title("Create angle from hours")
    def test_from_hours(self):
        """
        Verify angle creation from hour angle.

        Hours are used for Right Ascension because the celestial sphere
        appears to rotate once every 24 hours due to Earth's rotation.
        This makes hour angle a natural measure for tracking objects.

        24 hours = 360°, so 1 hour = 15°
        12 hours = 180° (halfway around the sky)
        """
        with allure.step("Create Angle(hours=12.0)"):
            a = Angle(hours=12.0)
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 180.0, rel_tol=1e-10)

    @allure.title("Create angle from arcminutes")
    def test_from_arcminutes(self):
        """
        Verify angle creation from arcminutes.

        One arcminute (′) is 1/60 of a degree. This subdivision provides
        precision needed for astronomical measurements. For reference:

        - The Moon's diameter is about 31 arcminutes
        - Human visual acuity resolves about 1 arcminute
        - 60 arcminutes = 1 degree
        """
        with allure.step("Create Angle(arcminutes=60.0)"):
            a = Angle(arcminutes=60.0)
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 1.0, rel_tol=1e-10)

    @allure.title("Create angle from arcseconds")
    def test_from_arcseconds(self):
        """
        Verify angle creation from arcseconds.

        One arcsecond (″) is 1/60 of an arcminute, or 1/3600 of a degree.
        This is a tiny angle - roughly the apparent size of a quarter
        viewed from 5 kilometers away. For reference:

        - Best ground-based seeing: ~0.5 arcseconds
        - Hubble resolution: ~0.05 arcseconds
        - 3600 arcseconds = 1 degree
        """
        with allure.step("Create Angle(arcseconds=3600.0)"):
            a = Angle(arcseconds=3600.0)
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 1.0, rel_tol=1e-10)

    @allure.title("Create angle from DMS")
    def test_from_dms(self):
        """
        Verify angle creation from degrees-minutes-seconds notation.

        DMS (Degrees, Minutes, Seconds) is the traditional sexagesimal
        format inherited from Babylonian mathematics. It remains standard
        for expressing declination in star catalogs.

        45°30′00″ = 45.5° (45 degrees plus 30/60 of a degree)
        """
        with allure.step("Create Angle.from_dms(45, 30, 0)"):
            a = Angle.from_dms(45, 30, 0)
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)

    @allure.title("Create negative angle from DMS")
    def test_from_dms_negative(self):
        """
        Verify negative angle creation from DMS notation.

        Negative angles are essential for southern declinations and
        certain position angles. The sign applies to the entire angle,
        not just the degrees component.

        -45°30′00″ = -45.5° (in the southern celestial hemisphere)
        """
        with allure.step("Create Angle.from_dms(-45, 30, 0)"):
            a = Angle.from_dms(-45, 30, 0)
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, -45.5, rel_tol=1e-10)

    @allure.title("Create angle from HMS")
    def test_from_hms(self):
        """
        Verify angle creation from hours-minutes-seconds notation.

        HMS (Hours, Minutes, Seconds) is standard for Right Ascension.
        Like DMS, it uses base-60 subdivisions, but applied to hours:

        12h30m00s = 12.5 hours = 187.5° (12 hours plus 30/60 of an hour)
        """
        with allure.step("Create Angle.from_hms(12, 30, 0)"):
            a = Angle.from_hms(12, 30, 0)
        with allure.step(f"Result: {a.hours}h"):
            assert math.isclose(a.hours, 12.5, rel_tol=1e-10)

    @allure.title("Requires exactly one unit")
    def test_requires_exactly_one_unit(self):
        """
        Verify that Angle construction requires exactly one unit specification.

        Allowing multiple units would create ambiguity - should they be
        added? Which takes precedence? The single-unit requirement ensures
        clear, unambiguous angle creation.
        """
        with allure.step("Test Angle() with no arguments"):
            with pytest.raises(ValueError, match="Exactly one"):
                Angle()

        with allure.step("Test Angle(degrees=45, radians=0.5)"):
            with pytest.raises(ValueError, match="Exactly one"):
                Angle(degrees=45, radians=0.5)


# ═══════════════════════════════════════════════════════════════════════════════
#  ANGLE PARSING
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Angle Parsing")
class TestAngleParsing:
    """
    Tests for parsing angle strings in various formats.

    Astronomical data comes in many text formats from different sources:
    catalogs, databases, user input, and legacy systems. A robust parser
    must handle all common notations while rejecting invalid input.

    Common formats include:
    - Decimal: "45.5" or "45.5d"
    - DMS: "45d30m00s" or "45°30′00″"
    - HMS: "12h30m00s"
    - Colon-separated: "45:30:00"
    - Space-separated: "45 30 00"
    """

    @allure.title("Parse plain degrees")
    def test_parse_degrees_plain(self):
        """
        Verify parsing of plain decimal degree values.

        Simple numeric strings are interpreted as degrees by default,
        which is the most common case for user input.
        """
        with allure.step("Parse '45.5'"):
            a = Angle.parse("45.5")
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)

    @allure.title("Parse degrees with 'd' suffix")
    def test_parse_degrees_with_d(self):
        """
        Verify parsing of degrees with explicit 'd' unit marker.

        The 'd' suffix makes the unit explicit, useful when the context
        might be ambiguous or for clarity in configuration files.
        """
        with allure.step("Parse '45.5d'"):
            a = Angle.parse("45.5d")
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)

    @allure.title("Parse DMS format")
    def test_parse_dms(self):
        """
        Verify parsing of traditional DMS notation with letter separators.

        The format "45d30m00s" uses ASCII letters that are easy to type
        and widely supported, making it ideal for command-line tools.
        """
        with allure.step("Parse '45d30m00s'"):
            a = Angle.parse("45d30m00s")
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)

    @allure.title("Parse Unicode DMS format")
    def test_parse_dms_unicode(self):
        """
        Verify parsing of DMS notation with proper Unicode symbols.

        Unicode symbols (° ′ ″) are the typographically correct way to
        write angles and are increasingly common in modern applications
        and internationalized interfaces.
        """
        with allure.step("Parse '45°30′00″'"):
            a = Angle.parse("45°30′00″")
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)

    @allure.title("Parse HMS format")
    def test_parse_hms(self):
        """
        Verify parsing of HMS (hours-minutes-seconds) notation.

        The 'h' marker distinguishes this from DMS and indicates that
        the result should be interpreted as an hour angle (used for RA).
        """
        with allure.step("Parse '12h30m00s'"):
            a = Angle.parse("12h30m00s")
        with allure.step(f"Result: {a.hours}h"):
            assert math.isclose(a.hours, 12.5, rel_tol=1e-10)

    @allure.title("Parse colon-separated format")
    def test_parse_colon_separated(self):
        """
        Verify parsing of colon-separated sexagesimal notation.

        The format "45:30:00" is common in database exports and some
        catalog formats. Without a unit marker, it's interpreted as DMS.
        """
        with allure.step("Parse '45:30:00'"):
            a = Angle.parse("45:30:00")
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)

    @allure.title("Parse space-separated format")
    def test_parse_space_separated(self):
        """
        Verify parsing of space-separated sexagesimal notation.

        Space separation is common in fixed-width catalog formats and
        some legacy astronomical data files.
        """
        with allure.step("Parse '45 30 00'"):
            a = Angle.parse("45 30 00")
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)

    @allure.title("Parse negative DMS")
    def test_parse_negative(self):
        """
        Verify parsing of negative angles in DMS format.

        Negative angles are essential for southern declinations
        (below the celestial equator).
        """
        with allure.step("Parse '-45d30m00s'"):
            a = Angle.parse("-45d30m00s")
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, -45.5, rel_tol=1e-10)

    @allure.title("Invalid string raises ValueError")
    def test_parse_invalid(self):
        """
        Verify that invalid angle strings raise appropriate errors.

        Clear error messages help users correct malformed input rather
        than silently producing incorrect values.
        """
        with allure.step("Parse 'not an angle'"):
            with pytest.raises(ValueError, match="Cannot parse"):
                Angle.parse("not an angle")


# ═══════════════════════════════════════════════════════════════════════════════
#  ANGLE CONVERSIONS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Angle Conversions")
class TestAngleConversions:
    """
    Tests for converting angles between different unit systems.

    Seamless unit conversion is essential because different astronomical
    contexts require different units:

    - Trigonometric calculations need radians
    - Display to users typically uses degrees or HMS/DMS
    - Timing calculations may use hours
    - High-precision work uses arcseconds

    All conversions must maintain full precision to preserve
    the accuracy of astronomical calculations.
    """

    @allure.title("Convert to DMS")
    def test_to_dms(self):
        """
        Verify conversion to degrees-minutes-seconds tuple.

        The to_dms() method returns integer degrees and minutes with
        floating-point seconds, matching the traditional notation.
        """
        with allure.step("Create Angle(degrees=45.5)"):
            a = Angle(degrees=45.5)
        with allure.step("Convert to DMS"):
            d, m, s = a.to_dms()
        with allure.step(f"Result: {d}° {m}′ {s:.1f}″"):
            assert d == 45
            assert m == 30
            assert math.isclose(s, 0.0, abs_tol=1e-10)

    @allure.title("Convert negative angle to DMS")
    def test_to_dms_negative(self):
        """
        Verify DMS conversion preserves sign correctly.

        For negative angles, only the degrees component carries the sign.
        The minutes and seconds are always positive magnitudes.
        """
        with allure.step("Create Angle(degrees=-45.5)"):
            a = Angle(degrees=-45.5)
        with allure.step("Convert to DMS"):
            d, m, s = a.to_dms()
        with allure.step(f"Result: {d}° {m}′ {s:.1f}″"):
            assert d == -45
            assert m == 30  # Positive magnitude
            assert math.isclose(s, 0.0, abs_tol=1e-10)

    @allure.title("Convert to HMS")
    def test_to_hms(self):
        """
        Verify conversion to hours-minutes-seconds tuple.

        HMS format is standard for Right Ascension display and is
        essential for communicating celestial positions to observers.
        """
        with allure.step("Create Angle(hours=12.5)"):
            a = Angle(hours=12.5)
        with allure.step("Convert to HMS"):
            h, m, s = a.to_hms()
        with allure.step(f"Result: {h}h {m}m {s:.1f}s"):
            assert h == 12
            assert m == 30
            assert math.isclose(s, 0.0, abs_tol=1e-10)

    @allure.title("Radians property")
    def test_radians_property(self):
        """
        Verify the radians property for trigonometric calculations.

        Radians are required for math library functions like sin(), cos(),
        and tan(). The conversion must be exact: 180° = π radians.
        """
        with allure.step("Create Angle(degrees=180)"):
            a = Angle(degrees=180)
        with allure.step(f"Radians = {a.radians:.6f}"):
            assert math.isclose(a.radians, math.pi, rel_tol=1e-10)

    @allure.title("Hours property")
    def test_hours_property(self):
        """
        Verify the hours property for RA calculations.

        The conversion is: 360° = 24h, so 1h = 15°.
        180° = 12h (the meridian opposite the vernal equinox).
        """
        with allure.step("Create Angle(degrees=180)"):
            a = Angle(degrees=180)
        with allure.step(f"Hours = {a.hours}"):
            assert math.isclose(a.hours, 12.0, rel_tol=1e-10)

    @allure.title("Arcminutes property")
    def test_arcminutes_property(self):
        """
        Verify the arcminutes property for fine angular measurements.

        1° = 60 arcminutes. This unit is commonly used for:
        - Apparent sizes of extended objects (galaxies, nebulae)
        - Field of view specifications
        - Atmospheric seeing measurements
        """
        with allure.step("Create Angle(degrees=1)"):
            a = Angle(degrees=1)
        with allure.step(f"Arcminutes = {a.arcminutes}"):
            assert math.isclose(a.arcminutes, 60.0, rel_tol=1e-10)

    @allure.title("Arcseconds property")
    def test_arcseconds_property(self):
        """
        Verify the arcseconds property for precision measurements.

        1° = 3600 arcseconds. This unit is used for:
        - Stellar proper motions
        - Parallax measurements
        - Binary star separations
        - Telescope resolution limits
        """
        with allure.step("Create Angle(degrees=1)"):
            a = Angle(degrees=1)
        with allure.step(f"Arcseconds = {a.arcseconds}"):
            assert math.isclose(a.arcseconds, 3600.0, rel_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  ANGLE ARITHMETIC
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Angle Arithmetic")
class TestAngleArithmetic:
    """
    Tests for arithmetic operations on angles.

    Angle arithmetic is used throughout astronomical calculations:

    - Adding angles: hour angle = LST - RA
    - Subtracting angles: angular distance calculations
    - Scaling angles: coordinate transformations
    - Negation: finding opposite directions

    These operations form the foundation of positional astronomy.
    """

    @allure.title("Add angles")
    def test_add(self):
        """
        Verify angle addition.

        Addition is used for operations like:
        - Computing hour angle from sidereal time and RA
        - Applying proper motion corrections
        - Combining angular offsets
        """
        with allure.step("Create angles 45° and 30°"):
            a = Angle(degrees=45)
            b = Angle(degrees=30)
        with allure.step("Calculate 45° + 30°"):
            c = a + b
        with allure.step(f"Result: {c.degrees}°"):
            assert math.isclose(c.degrees, 75, rel_tol=1e-10)

    @allure.title("Subtract angles")
    def test_subtract(self):
        """
        Verify angle subtraction.

        Subtraction is fundamental for:
        - Hour angle calculation: HA = LST - RA
        - Angular separation approximations
        - Epoch transformations
        """
        with allure.step("Create angles 45° and 30°"):
            a = Angle(degrees=45)
            b = Angle(degrees=30)
        with allure.step("Calculate 45° - 30°"):
            c = a - b
        with allure.step(f"Result: {c.degrees}°"):
            assert math.isclose(c.degrees, 15, rel_tol=1e-10)

    @allure.title("Multiply angle by scalar")
    def test_multiply(self):
        """
        Verify angle multiplication by a scalar.

        Scaling is used in:
        - Coordinate transformations
        - Interpolation calculations
        - Rate computations (angular velocity)
        """
        with allure.step("Create Angle(degrees=45)"):
            a = Angle(degrees=45)
        with allure.step("Calculate 45° × 2"):
            c = a * 2
        with allure.step(f"Result: {c.degrees}°"):
            assert math.isclose(c.degrees, 90, rel_tol=1e-10)

    @allure.title("Right multiply angle by scalar")
    def test_rmultiply(self):
        """
        Verify that scalar × angle works (commutative multiplication).

        Both "angle * scalar" and "scalar * angle" should produce
        the same result for intuitive mathematical expressions.
        """
        with allure.step("Create Angle(degrees=45)"):
            a = Angle(degrees=45)
        with allure.step("Calculate 2 × 45°"):
            c = 2 * a
        with allure.step(f"Result: {c.degrees}°"):
            assert math.isclose(c.degrees, 90, rel_tol=1e-10)

    @allure.title("Divide angle by scalar")
    def test_divide(self):
        """
        Verify angle division by a scalar.

        Division is used for:
        - Finding midpoints between angles
        - Converting between angular units
        - Averaging angular measurements
        """
        with allure.step("Create Angle(degrees=90)"):
            a = Angle(degrees=90)
        with allure.step("Calculate 90° ÷ 2"):
            c = a / 2
        with allure.step(f"Result: {c.degrees}°"):
            assert math.isclose(c.degrees, 45, rel_tol=1e-10)

    @allure.title("Negate angle")
    def test_negate(self):
        """
        Verify angle negation.

        Negation finds the opposite direction, used for:
        - Reversing position angles
        - Computing reflex angles
        - Coordinate system transformations
        """
        with allure.step("Create Angle(degrees=45)"):
            a = Angle(degrees=45)
        with allure.step("Calculate -45°"):
            c = -a
        with allure.step(f"Result: {c.degrees}°"):
            assert math.isclose(c.degrees, -45, rel_tol=1e-10)

    @allure.title("Absolute value of angle")
    def test_abs(self):
        """
        Verify absolute value of angle.

        Absolute value gives the magnitude regardless of sign,
        useful for comparing angular distances.
        """
        with allure.step("Create Angle(degrees=-45)"):
            a = Angle(degrees=-45)
        with allure.step("Calculate |−45°|"):
            c = abs(a)
        with allure.step(f"Result: {c.degrees}°"):
            assert math.isclose(c.degrees, 45, rel_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  ANGLE NORMALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Angle Normalization")
class TestAngleNormalization:
    """
    Tests for angle normalization to standard ranges.

    Normalization constrains angles to a standard range, which is essential
    for comparing angles and displaying coordinates consistently.

    Common normalization ranges:
    - [0°, 360°): Standard for longitude, Right Ascension, azimuth
    - [-180°, +180°): Centered on zero, useful for differences
    - [-90°, +90°]: Required for latitude and declination
    """

    @allure.title("Normalize positive angle > 360°")
    def test_normalize_positive(self):
        """
        Verify normalization of angles exceeding 360°.

        Angles greater than 360° are reduced by removing complete
        rotations: 450° = 450° - 360° = 90°.
        """
        with allure.step("Create Angle(degrees=450)"):
            a = Angle(degrees=450)
        with allure.step("Normalize to [0, 360)"):
            n = a.normalize()
        with allure.step(f"Result: {n.degrees}°"):
            assert math.isclose(n.degrees, 90, rel_tol=1e-10)

    @allure.title("Normalize negative angle")
    def test_normalize_negative(self):
        """
        Verify normalization of negative angles.

        Negative angles are shifted into the positive range:
        -90° + 360° = 270° (equivalent position on the circle).
        """
        with allure.step("Create Angle(degrees=-90)"):
            a = Angle(degrees=-90)
        with allure.step("Normalize to [0, 360)"):
            n = a.normalize()
        with allure.step(f"Result: {n.degrees}°"):
            assert math.isclose(n.degrees, 270, rel_tol=1e-10)

    @allure.title("Normalize centered on zero")
    def test_normalize_centered_zero(self):
        """
        Verify normalization to [-180°, +180°) range.

        Zero-centered normalization is useful for angular differences
        where we want the smallest magnitude representation:
        270° normalized to center=0 becomes -90° (same direction).
        """
        with allure.step("Create Angle(degrees=270)"):
            a = Angle(degrees=270)
        with allure.step("Normalize centered on 0 [-180, 180)"):
            n = a.normalize(center=0)
        with allure.step(f"Result: {n.degrees}°"):
            assert math.isclose(n.degrees, -90, rel_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  TRIGONOMETRIC FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Trigonometric Functions")
class TestAngleTrig:
    """
    Tests for trigonometric functions on Angle objects.

    Trigonometry is fundamental to spherical astronomy. These functions
    are used in:

    - Coordinate transformations (equatorial ↔ horizontal ↔ galactic)
    - Great circle calculations (angular separation)
    - Parallax and proper motion corrections
    - Precession and nutation calculations

    The Angle class provides direct trig methods to avoid repeated
    degree-to-radian conversions in calculations.
    """

    @allure.title("sin(90°) = 1")
    def test_sin(self):
        """
        Verify sine function at 90°.

        sin(90°) = 1 is a fundamental identity. The sine function
        gives the y-coordinate on the unit circle, reaching its
        maximum at 90° (the top of the circle).
        """
        with allure.step("Create Angle(degrees=90)"):
            a = Angle(degrees=90)
        with allure.step(f"sin(90°) = {a.sin()}"):
            assert math.isclose(a.sin(), 1.0, rel_tol=1e-10)

    @allure.title("cos(0°) = 1")
    def test_cos(self):
        """
        Verify cosine function at 0°.

        cos(0°) = 1 is a fundamental identity. The cosine function
        gives the x-coordinate on the unit circle, which equals 1
        at 0° (the rightmost point of the circle).
        """
        with allure.step("Create Angle(degrees=0)"):
            a = Angle(degrees=0)
        with allure.step(f"cos(0°) = {a.cos()}"):
            assert math.isclose(a.cos(), 1.0, rel_tol=1e-10)

    @allure.title("tan(45°) = 1")
    def test_tan(self):
        """
        Verify tangent function at 45°.

        tan(45°) = 1 because at 45°, sine and cosine are equal.
        The tangent (sin/cos) is therefore 1. This is a useful
        reference point for verifying trigonometric calculations.
        """
        with allure.step("Create Angle(degrees=45)"):
            a = Angle(degrees=45)
        with allure.step(f"tan(45°) = {a.tan()}"):
            assert math.isclose(a.tan(), 1.0, rel_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  ANGULAR SEPARATION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Angular Separation")
class TestAngularSeparation:
    """
    Tests for computing the angular separation between two sky positions.

    Angular separation is the angle between two points on the celestial
    sphere, measured along the great circle connecting them. This is
    one of the most important calculations in observational astronomy:

    - Determining if objects fit in the same field of view
    - Checking moon/sun proximity to targets
    - Measuring binary star separations
    - Validating coordinate transformations

    The calculation uses the spherical law of cosines or the more
    numerically stable Vincenty formula for small angles.
    """

    @allure.title("Separation of same point = 0°")
    def test_same_point(self):
        """
        Verify that a point has zero separation from itself.

        This is a fundamental sanity check - any point on the
        celestial sphere should have exactly 0° separation from itself.
        """
        with allure.step("Create point at RA=12h, Dec=45°"):
            ra = Angle(hours=12)
            dec = Angle(degrees=45)
        with allure.step("Calculate separation from itself"):
            sep = angular_separation(ra, dec, ra, dec)
        with allure.step(f"Separation = {sep.degrees}°"):
            assert math.isclose(sep.degrees, 0, abs_tol=1e-10)

    @allure.title("North pole to South pole = 180°")
    def test_pole_to_pole(self):
        """
        Verify that celestial poles are exactly 180° apart.

        The North and South celestial poles are diametrically opposite
        points on the celestial sphere. The angular distance between
        any two antipodal points is exactly 180°.
        """
        with allure.step("Create North pole (+90°) and South pole (-90°)"):
            ra = Angle(hours=0)
        with allure.step("Calculate pole-to-pole separation"):
            sep = angular_separation(
                ra, Angle(degrees=90),
                ra, Angle(degrees=-90)
            )
        with allure.step(f"Separation = {sep.degrees}°"):
            assert math.isclose(sep.degrees, 180, rel_tol=1e-10)

    @allure.title("6 hours apart on equator = 90°")
    def test_equator_90_degrees(self):
        """
        Verify separation for points 6 hours apart on the equator.

        On the celestial equator (Dec=0°), the angular separation
        equals the RA difference directly:
        - 6 hours of RA = 90° of arc
        - 12 hours of RA = 180° of arc
        - 24 hours of RA = 360° (back to start)
        """
        with allure.step("Create two points 6h apart on equator"):
            dec = Angle(degrees=0)
        with allure.step("Calculate separation"):
            sep = angular_separation(
                Angle(hours=0), dec,
                Angle(hours=6), dec
            )
        with allure.step(f"Separation = {sep.degrees}°"):
            assert math.isclose(sep.degrees, 90, rel_tol=1e-10)

    @allure.title("Sirius to Betelgeuse ≈ 27°")
    def test_known_value_sirius_betelgeuse(self):
        """
        Verify angular separation against known star pair.

        Sirius (α CMa) and Betelgeuse (α Ori) are bright stars with
        well-known positions. Their separation of approximately 27°
        provides a real-world validation of the calculation.

        Sirius: RA 6h45m, Dec -16°43' (brightest star in the sky)
        Betelgeuse: RA 5h55m, Dec +7°24' (red supergiant in Orion)
        """
        with allure.step("Define Sirius: RA 6h45m, Dec -16°43'"):
            sirius_ra = Angle.from_hms(6, 45, 0)
            sirius_dec = Angle.from_dms(-16, 43, 0)
        with allure.step("Define Betelgeuse: RA 5h55m, Dec +7°24'"):
            betel_ra = Angle.from_hms(5, 55, 0)
            betel_dec = Angle.from_dms(7, 24, 0)
        with allure.step("Calculate separation"):
            sep = angular_separation(sirius_ra, sirius_dec, betel_ra, betel_dec)
        with allure.step(f"Separation = {sep.degrees:.1f}° (expected ~27°)"):
            assert 26 < sep.degrees < 28

    @allure.title("Verbose mode produces output")
    def test_verbose_output(self):
        """
        Verify that verbose mode captures calculation steps.

        Verbose output is valuable for educational purposes and
        debugging, showing the intermediate steps of the calculation.
        """
        with allure.step("Create verbose context"):
            ctx = VerboseContext()
        with allure.step("Calculate separation with verbose=True"):
            ra1, dec1 = Angle(hours=12), Angle(degrees=45)
            ra2, dec2 = Angle(hours=13), Angle(degrees=46)
            angular_separation(ra1, dec1, ra2, dec2, verbose=ctx)
        with allure.step(f"Verbose steps: {len(ctx.steps)}"):
            assert len(ctx.steps) > 0


# ═══════════════════════════════════════════════════════════════════════════════
#  POSITION ANGLE
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Position Angle")
class TestPositionAngle:
    """
    Tests for computing the position angle between two sky positions.

    Position angle (PA) measures the direction from one celestial object
    to another, expressed as an angle from celestial north through east:

    - 0° = North (toward celestial north pole)
    - 90° = East (increasing RA)
    - 180° = South (toward celestial south pole)
    - 270° = West (decreasing RA)

    Position angles are essential for:
    - Describing binary star orientations
    - Specifying galaxy axis directions
    - Guiding telescope slews
    - Aligning instrument position angles
    """

    @allure.title("Point due north → PA ≈ 0°")
    def test_north(self):
        """
        Verify position angle to a point due north is ~0°.

        A point with the same RA but higher declination lies
        toward the north celestial pole, giving PA ≈ 0°.
        """
        with allure.step("Create reference at RA=12h, Dec=45°"):
            ra = Angle(hours=12)
        with allure.step("Calculate PA to point 1° north"):
            pa = position_angle(
                ra, Angle(degrees=45),
                ra, Angle(degrees=46)
            )
        with allure.step(f"Position angle = {pa.degrees:.1f}°"):
            assert math.isclose(pa.degrees, 0, abs_tol=0.1)

    @allure.title("Point due south → PA ≈ 180°")
    def test_south(self):
        """
        Verify position angle to a point due south is ~180°.

        A point with the same RA but lower declination lies
        toward the south celestial pole, giving PA ≈ 180°.
        """
        with allure.step("Create reference at RA=12h, Dec=45°"):
            ra = Angle(hours=12)
        with allure.step("Calculate PA to point 1° south"):
            pa = position_angle(
                ra, Angle(degrees=45),
                ra, Angle(degrees=44)
            )
        with allure.step(f"Position angle = {pa.degrees:.1f}°"):
            assert math.isclose(pa.degrees, 180, abs_tol=0.1)

    @allure.title("Point due east → PA ≈ 90°")
    def test_east(self):
        """
        Verify position angle to a point due east is ~90°.

        On the celestial equator, increasing RA corresponds to
        moving eastward, giving PA ≈ 90°.
        """
        with allure.step("Create reference on equator at RA=12h"):
            dec = Angle(degrees=0)
        with allure.step("Calculate PA to point east"):
            pa = position_angle(
                Angle(hours=12), dec,
                Angle(hours=12.1), dec
            )
        with allure.step(f"Position angle = {pa.degrees:.1f}°"):
            assert math.isclose(pa.degrees, 90, abs_tol=1)

    @allure.title("Point due west → PA ≈ 270°")
    def test_west(self):
        """
        Verify position angle to a point due west is ~270°.

        On the celestial equator, decreasing RA corresponds to
        moving westward, giving PA ≈ 270°.
        """
        with allure.step("Create reference on equator at RA=12h"):
            dec = Angle(degrees=0)
        with allure.step("Calculate PA to point west"):
            pa = position_angle(
                Angle(hours=12), dec,
                Angle(hours=11.9), dec
            )
        with allure.step(f"Position angle = {pa.degrees:.1f}°"):
            assert math.isclose(pa.degrees, 270, abs_tol=1)
