"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              ANGLE TESTS                                     ║
║                                                                              ║
║  Tests for angular arithmetic, parsing, conversions, and trigonometry.       ║
║  Angles are the fundamental building block of celestial mechanics.           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import math
import allure
import pytest
from hypothesis import given, strategies as st, settings

from starward.core.angles import Angle, angular_separation, position_angle
from starward.verbose import VerboseContext


# ═══════════════════════════════════════════════════════════════════════════════
#  CONSTRUCTION & INITIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Angle Construction")
class TestAngleConstruction:
    """
    Tests for creating Angle instances from various units.

    An Angle can be constructed from:
      - degrees (default astronomical unit)
      - radians (mathematical standard)
      - hours (right ascension, 24h = 360°)
      - arcminutes (1° = 60')
      - arcseconds (1° = 3600")
    """

    # ─── From Degrees ───────────────────────────────────────────────────────

    @allure.title("Create angle from positive degrees")
    def test_from_degrees_positive(self):
        """Create angle from positive degrees."""
        with allure.step("Create Angle(degrees=45.5)"):
            a = Angle(degrees=45.5)
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)

    @allure.title("Create angle from negative degrees")
    def test_from_degrees_negative(self):
        """Create angle from negative degrees."""
        with allure.step("Create Angle(degrees=-45.5)"):
            a = Angle(degrees=-45.5)
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, -45.5, rel_tol=1e-10)

    @allure.title("Create zero angle")
    def test_from_degrees_zero(self):
        """Create zero angle."""
        with allure.step("Create Angle(degrees=0)"):
            a = Angle(degrees=0)
        with allure.step(f"Result: {a.degrees}°"):
            assert a.degrees == 0

    @pytest.mark.edge
    @allure.title("Create angle larger than 360°")
    def test_from_degrees_large(self):
        """Create angle larger than 360°."""
        with allure.step("Create Angle(degrees=720.5)"):
            a = Angle(degrees=720.5)
        with allure.step(f"Result: {a.degrees}° (stored as-is)"):
            assert math.isclose(a.degrees, 720.5, rel_tol=1e-10)

    # ─── From Radians ───────────────────────────────────────────────────────

    @allure.title("Create angle from radians")
    def test_from_radians(self):
        """Create angle from radians."""
        with allure.step("Create Angle(radians=π/4)"):
            a = Angle(radians=math.pi / 4)
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 45.0, rel_tol=1e-10)

    @allure.title("π radians = 180°")
    def test_from_radians_pi(self):
        """π radians = 180°."""
        with allure.step("Create Angle(radians=π)"):
            a = Angle(radians=math.pi)
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 180.0, rel_tol=1e-10)

    @allure.title("2π radians = 360°")
    def test_from_radians_2pi(self):
        """2π radians = 360°."""
        with allure.step("Create Angle(radians=2π)"):
            a = Angle(radians=2 * math.pi)
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 360.0, rel_tol=1e-10)

    # ─── From Hours (Right Ascension) ───────────────────────────────────────

    @allure.title("Create angle from hours (12h = 180°)")
    def test_from_hours(self):
        """Create angle from hours."""
        with allure.step("Create Angle(hours=12.0)"):
            a = Angle(hours=12.0)
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 180.0, rel_tol=1e-10)

    @allure.title("24 hours = 360°")
    def test_from_hours_24(self):
        """24 hours = 360°."""
        with allure.step("Create Angle(hours=24.0)"):
            a = Angle(hours=24.0)
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 360.0, rel_tol=1e-10)

    @allure.title("6 hours = 90°")
    def test_from_hours_6(self):
        """6 hours = 90°."""
        with allure.step("Create Angle(hours=6.0)"):
            a = Angle(hours=6.0)
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 90.0, rel_tol=1e-10)

    # ─── From Arcminutes ────────────────────────────────────────────────────

    @allure.title("Create angle from arcminutes (60' = 1°)")
    def test_from_arcminutes(self):
        """Create angle from arcminutes."""
        with allure.step("Create Angle(arcminutes=60.0)"):
            a = Angle(arcminutes=60.0)
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 1.0, rel_tol=1e-10)

    @allure.title("90 arcminutes = 1.5°")
    def test_from_arcminutes_90(self):
        """90 arcminutes = 1.5°."""
        with allure.step("Create Angle(arcminutes=90.0)"):
            a = Angle(arcminutes=90.0)
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 1.5, rel_tol=1e-10)

    # ─── From Arcseconds ────────────────────────────────────────────────────

    @allure.title("Create angle from arcseconds (3600\" = 1°)")
    def test_from_arcseconds(self):
        """Create angle from arcseconds."""
        with allure.step("Create Angle(arcseconds=3600.0)"):
            a = Angle(arcseconds=3600.0)
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 1.0, rel_tol=1e-10)

    @allure.title("Very small angle: 1 arcsecond")
    def test_from_arcseconds_small(self):
        """Very small angle: 1 arcsecond."""
        with allure.step("Create Angle(arcseconds=1.0)"):
            a = Angle(arcseconds=1.0)
        with allure.step(f"Result: {a.degrees}° = 1/3600°"):
            assert math.isclose(a.degrees, 1.0 / 3600.0, rel_tol=1e-10)

    # ─── From DMS (Degrees, Minutes, Seconds) ───────────────────────────────

    @allure.title("Create angle from d°m′s″")
    def test_from_dms(self):
        """Create angle from d°m′s″."""
        with allure.step("Create Angle.from_dms(45, 30, 0)"):
            a = Angle.from_dms(45, 30, 0)
        with allure.step(f"Result: {a.degrees}° (45°30'0\")"):
            assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)

    @allure.title("Create angle with non-zero seconds")
    def test_from_dms_with_seconds(self):
        """Create angle with non-zero seconds."""
        with allure.step("Create Angle.from_dms(45, 30, 30)"):
            a = Angle.from_dms(45, 30, 30)
        expected = 45 + 30/60 + 30/3600
        with allure.step(f"Result: {a.degrees}° ≈ {expected}°"):
            assert math.isclose(a.degrees, expected, rel_tol=1e-10)

    @allure.title("Create negative angle from DMS")
    def test_from_dms_negative(self):
        """Create negative angle from DMS."""
        with allure.step("Create Angle.from_dms(-45, 30, 0)"):
            a = Angle.from_dms(-45, 30, 0)
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, -45.5, rel_tol=1e-10)

    @pytest.mark.edge
    @allure.title("Edge case: negative angle with zero degrees")
    def test_from_dms_edge_zero_degrees(self):
        """Edge case: negative angle with zero degrees component."""
        with allure.step("Create Angle.from_dms(0, -30, 0)"):
            a = Angle.from_dms(0, -30, 0)  # -0°30'
        with allure.step(f"Result: {a.degrees}° (should be -0.5°)"):
            assert math.isclose(a.degrees, -0.5, rel_tol=1e-10)

    # ─── From HMS (Hours, Minutes, Seconds) ─────────────────────────────────

    @allure.title("Create angle from h:m:s")
    def test_from_hms(self):
        """Create angle from h:m:s."""
        with allure.step("Create Angle.from_hms(12, 30, 0)"):
            a = Angle.from_hms(12, 30, 0)
        with allure.step(f"Result: {a.hours}h"):
            assert math.isclose(a.hours, 12.5, rel_tol=1e-10)

    @allure.title("24h = 360°")
    def test_from_hms_sidereal_day(self):
        """24h = 360°."""
        with allure.step("Create Angle.from_hms(24, 0, 0)"):
            a = Angle.from_hms(24, 0, 0)
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 360.0, rel_tol=1e-10)

    # ─── Validation ─────────────────────────────────────────────────────────

    @allure.title("Must specify exactly one unit")
    def test_requires_exactly_one_unit(self):
        """Must specify exactly one unit."""
        with allure.step("Create Angle() with no arguments"):
            with pytest.raises(ValueError, match="Exactly one"):
                Angle()

    @allure.title("Cannot specify multiple units")
    def test_rejects_multiple_units(self):
        """Cannot specify multiple units."""
        with allure.step("Create Angle(degrees=45, radians=0.5)"):
            with pytest.raises(ValueError, match="Exactly one"):
                Angle(degrees=45, radians=0.5)


# ═══════════════════════════════════════════════════════════════════════════════
#  PARSING
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Angle Parsing")
class TestAngleParsing:
    """
    Tests for parsing angle strings in various formats.

    Supported formats:
      - Decimal: "45.5", "45.5d"
      - DMS: "45d30m00s", "45°30′00″", "45:30:00"
      - HMS: "12h30m00s"
      - Space-separated: "45 30 00"
    """

    # ─── Decimal Formats ────────────────────────────────────────────────────

    @allure.title("Parse plain decimal degrees")
    def test_parse_decimal_plain(self):
        """Parse plain decimal degrees."""
        with allure.step("Parse '45.5'"):
            a = Angle.parse("45.5")
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)

    @allure.title("Parse decimal with 'd' suffix")
    def test_parse_decimal_with_d(self):
        """Parse decimal with 'd' suffix."""
        with allure.step("Parse '45.5d'"):
            a = Angle.parse("45.5d")
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)

    @allure.title("Parse integer degrees")
    def test_parse_integer(self):
        """Parse integer degrees."""
        with allure.step("Parse '45'"):
            a = Angle.parse("45")
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 45.0, rel_tol=1e-10)

    @allure.title("Parse negative decimal degrees")
    def test_parse_negative_decimal(self):
        """Parse negative decimal degrees."""
        with allure.step("Parse '-45.5'"):
            a = Angle.parse("-45.5")
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, -45.5, rel_tol=1e-10)

    # ─── DMS Formats ────────────────────────────────────────────────────────

    @allure.title("Parse DMS with letter separators")
    def test_parse_dms_letters(self):
        """Parse DMS with letter separators."""
        with allure.step("Parse '45d30m00s'"):
            a = Angle.parse("45d30m00s")
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)

    @allure.title("Parse DMS with Unicode symbols")
    def test_parse_dms_unicode(self):
        """Parse DMS with Unicode symbols."""
        with allure.step("Parse '45°30′00″'"):
            a = Angle.parse("45°30′00″")
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)

    @allure.title("Parse DMS with colon separators")
    def test_parse_dms_colons(self):
        """Parse DMS with colon separators."""
        with allure.step("Parse '45:30:00'"):
            a = Angle.parse("45:30:00")
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)

    @allure.title("Parse DMS with space separators")
    def test_parse_dms_spaces(self):
        """Parse DMS with space separators."""
        with allure.step("Parse '45 30 00'"):
            a = Angle.parse("45 30 00")
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, 45.5, rel_tol=1e-10)

    @allure.title("Parse negative DMS")
    def test_parse_dms_negative(self):
        """Parse negative DMS."""
        with allure.step("Parse '-45d30m00s'"):
            a = Angle.parse("-45d30m00s")
        with allure.step(f"Result: {a.degrees}°"):
            assert math.isclose(a.degrees, -45.5, rel_tol=1e-10)

    # ─── HMS Formats ────────────────────────────────────────────────────────

    @allure.title("Parse HMS format")
    def test_parse_hms(self):
        """Parse HMS format."""
        with allure.step("Parse '12h30m00s'"):
            a = Angle.parse("12h30m00s")
        with allure.step(f"Result: {a.hours}h"):
            assert math.isclose(a.hours, 12.5, rel_tol=1e-10)

    # ─── Error Handling ─────────────────────────────────────────────────────

    @allure.title("Invalid string raises ValueError")
    def test_parse_invalid_raises(self):
        """Invalid string raises ValueError."""
        with allure.step("Parse 'not an angle'"):
            with pytest.raises(ValueError, match="Cannot parse"):
                Angle.parse("not an angle")

    @allure.title("Empty string raises ValueError")
    def test_parse_empty_raises(self):
        """Empty string raises ValueError."""
        with allure.step("Parse empty string"):
            with pytest.raises(ValueError):
                Angle.parse("")


# ═══════════════════════════════════════════════════════════════════════════════
#  UNIT CONVERSIONS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Angle Conversions")
class TestAngleConversions:
    """
    Tests for converting between angle units.

    All conversions should be mathematically exact and
    round-trip back to the original value.
    """

    # ─── To DMS ─────────────────────────────────────────────────────────────

    @allure.title("Convert positive angle to DMS")
    def test_to_dms_positive(self):
        """Convert positive angle to DMS."""
        with allure.step("Create Angle(degrees=45.5)"):
            a = Angle(degrees=45.5)
        with allure.step("Convert to DMS"):
            d, m, s = a.to_dms()
        with allure.step(f"Result: {d}°{m}'{s:.1f}\""):
            assert d == 45
            assert m == 30
            assert math.isclose(s, 0.0, abs_tol=1e-10)

    @allure.title("Convert negative angle to DMS")
    def test_to_dms_negative(self):
        """Convert negative angle to DMS."""
        with allure.step("Create Angle(degrees=-45.5)"):
            a = Angle(degrees=-45.5)
        with allure.step("Convert to DMS"):
            d, m, s = a.to_dms()
        with allure.step(f"Result: {d}°{m}'{s:.1f}\""):
            assert d == -45
            assert m == 30
            assert math.isclose(s, 0.0, abs_tol=1e-10)

    @allure.title("Convert angle with fractional minutes")
    def test_to_dms_with_seconds(self):
        """Convert angle with fractional minutes."""
        with allure.step("Create Angle(degrees=45.5083333)"):
            a = Angle(degrees=45.5083333)  # 45°30'30"
        with allure.step("Convert to DMS"):
            d, m, s = a.to_dms()
        with allure.step(f"Result: {d}°{m}'{s:.1f}\""):
            assert d == 45
            assert m == 30
            assert math.isclose(s, 30.0, abs_tol=0.01)

    # ─── To HMS ─────────────────────────────────────────────────────────────

    @allure.title("Convert angle to HMS")
    def test_to_hms(self):
        """Convert angle to HMS."""
        with allure.step("Create Angle(hours=12.5)"):
            a = Angle(hours=12.5)
        with allure.step("Convert to HMS"):
            h, m, s = a.to_hms()
        with allure.step(f"Result: {h}h{m}m{s:.1f}s"):
            assert h == 12
            assert m == 30
            assert math.isclose(s, 0.0, abs_tol=1e-10)

    # ─── Property Accessors ─────────────────────────────────────────────────

    @allure.title("Radians accessor (180° = π)")
    def test_radians_property(self):
        """Radians accessor."""
        with allure.step("Create Angle(degrees=180)"):
            a = Angle(degrees=180)
        with allure.step(f"Result: {a.radians} rad ≈ π"):
            assert math.isclose(a.radians, math.pi, rel_tol=1e-10)

    @allure.title("Hours accessor (180° = 12h)")
    def test_hours_property(self):
        """Hours accessor."""
        with allure.step("Create Angle(degrees=180)"):
            a = Angle(degrees=180)
        with allure.step(f"Result: {a.hours}h"):
            assert math.isclose(a.hours, 12.0, rel_tol=1e-10)

    @allure.title("Arcminutes accessor (1° = 60')")
    def test_arcminutes_property(self):
        """Arcminutes accessor."""
        with allure.step("Create Angle(degrees=1)"):
            a = Angle(degrees=1)
        with allure.step(f"Result: {a.arcminutes}'"):
            assert math.isclose(a.arcminutes, 60.0, rel_tol=1e-10)

    @allure.title("Arcseconds accessor (1° = 3600\")")
    def test_arcseconds_property(self):
        """Arcseconds accessor."""
        with allure.step("Create Angle(degrees=1)"):
            a = Angle(degrees=1)
        with allure.step(f"Result: {a.arcseconds}\""):
            assert math.isclose(a.arcseconds, 3600.0, rel_tol=1e-10)

    # ─── Round-Trip Conversions ─────────────────────────────────────────────

    @pytest.mark.roundtrip
    @allure.title("degrees → radians → degrees roundtrip")
    @given(st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_degrees_radians_roundtrip(self, deg):
        """degrees → radians → degrees is identity."""
        a = Angle(degrees=deg)
        b = Angle(radians=a.radians)
        assert math.isclose(a.degrees, b.degrees, rel_tol=1e-10)

    @pytest.mark.roundtrip
    @allure.title("degrees → hours → degrees roundtrip")
    @given(st.floats(min_value=-1000, max_value=1000, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_degrees_hours_roundtrip(self, deg):
        """degrees → hours → degrees is identity."""
        a = Angle(degrees=deg)
        b = Angle(hours=a.hours)
        assert math.isclose(a.degrees, b.degrees, rel_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  ARITHMETIC OPERATIONS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Angle Arithmetic")
class TestAngleArithmetic:
    """
    Tests for angle arithmetic operations.

    Angles support standard arithmetic:
      - Addition (Angle + Angle)
      - Subtraction (Angle - Angle)
      - Multiplication (Angle * scalar)
      - Division (Angle / scalar)
      - Negation (-Angle)
      - Absolute value (abs(Angle))
    """

    # ─── Addition ───────────────────────────────────────────────────────────

    @allure.title("Add two angles")
    def test_add_angles(self):
        """Add two angles."""
        with allure.step("Create 45° + 30°"):
            a = Angle(degrees=45)
            b = Angle(degrees=30)
            c = a + b
        with allure.step(f"Result: {c.degrees}°"):
            assert math.isclose(c.degrees, 75, rel_tol=1e-10)

    @allure.title("Add a negative angle")
    def test_add_negative(self):
        """Add a negative angle."""
        with allure.step("Create 45° + (-30°)"):
            a = Angle(degrees=45)
            b = Angle(degrees=-30)
            c = a + b
        with allure.step(f"Result: {c.degrees}°"):
            assert math.isclose(c.degrees, 15, rel_tol=1e-10)

    # ─── Subtraction ────────────────────────────────────────────────────────

    @allure.title("Subtract two angles")
    def test_subtract_angles(self):
        """Subtract two angles."""
        with allure.step("Create 45° - 30°"):
            a = Angle(degrees=45)
            b = Angle(degrees=30)
            c = a - b
        with allure.step(f"Result: {c.degrees}°"):
            assert math.isclose(c.degrees, 15, rel_tol=1e-10)

    @allure.title("Subtraction resulting in negative angle")
    def test_subtract_to_negative(self):
        """Subtraction resulting in negative angle."""
        with allure.step("Create 30° - 45°"):
            a = Angle(degrees=30)
            b = Angle(degrees=45)
            c = a - b
        with allure.step(f"Result: {c.degrees}°"):
            assert math.isclose(c.degrees, -15, rel_tol=1e-10)

    # ─── Multiplication ─────────────────────────────────────────────────────

    @allure.title("Multiply angle by scalar")
    def test_multiply_by_scalar(self):
        """Multiply angle by scalar."""
        with allure.step("Create 45° × 2"):
            a = Angle(degrees=45)
            c = a * 2
        with allure.step(f"Result: {c.degrees}°"):
            assert math.isclose(c.degrees, 90, rel_tol=1e-10)

    @allure.title("Multiply scalar by angle (reverse)")
    def test_multiply_scalar_by_angle(self):
        """Multiply scalar by angle (reverse)."""
        with allure.step("Create 2 × 45°"):
            a = Angle(degrees=45)
            c = 2 * a
        with allure.step(f"Result: {c.degrees}°"):
            assert math.isclose(c.degrees, 90, rel_tol=1e-10)

    @allure.title("Multiply by fraction")
    def test_multiply_by_fraction(self):
        """Multiply by fraction."""
        with allure.step("Create 90° × 0.5"):
            a = Angle(degrees=90)
            c = a * 0.5
        with allure.step(f"Result: {c.degrees}°"):
            assert math.isclose(c.degrees, 45, rel_tol=1e-10)

    # ─── Division ───────────────────────────────────────────────────────────

    @allure.title("Divide angle by scalar")
    def test_divide_by_scalar(self):
        """Divide angle by scalar."""
        with allure.step("Create 90° ÷ 2"):
            a = Angle(degrees=90)
            c = a / 2
        with allure.step(f"Result: {c.degrees}°"):
            assert math.isclose(c.degrees, 45, rel_tol=1e-10)

    @pytest.mark.edge
    @allure.title("Division by zero raises")
    def test_divide_by_zero(self):
        """Division by zero raises."""
        with allure.step("Create 90° ÷ 0"):
            a = Angle(degrees=90)
            with pytest.raises(ZeroDivisionError):
                _ = a / 0

    # ─── Negation ───────────────────────────────────────────────────────────

    @allure.title("Negate angle")
    def test_negate(self):
        """Negate angle."""
        with allure.step("Create -45°"):
            a = Angle(degrees=45)
            c = -a
        with allure.step(f"Result: {c.degrees}°"):
            assert math.isclose(c.degrees, -45, rel_tol=1e-10)

    @allure.title("Negate negative angle")
    def test_negate_negative(self):
        """Negate negative angle."""
        with allure.step("Create -(-45°)"):
            a = Angle(degrees=-45)
            c = -a
        with allure.step(f"Result: {c.degrees}°"):
            assert math.isclose(c.degrees, 45, rel_tol=1e-10)

    # ─── Absolute Value ─────────────────────────────────────────────────────

    @allure.title("Absolute value of negative angle")
    def test_abs_negative(self):
        """Absolute value of negative angle."""
        with allure.step("Create abs(-45°)"):
            a = Angle(degrees=-45)
            c = abs(a)
        with allure.step(f"Result: {c.degrees}°"):
            assert math.isclose(c.degrees, 45, rel_tol=1e-10)

    @allure.title("Absolute value of positive angle")
    def test_abs_positive(self):
        """Absolute value of positive angle."""
        with allure.step("Create abs(45°)"):
            a = Angle(degrees=45)
            c = abs(a)
        with allure.step(f"Result: {c.degrees}°"):
            assert math.isclose(c.degrees, 45, rel_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  NORMALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Angle Normalization")
class TestAngleNormalization:
    """
    Tests for angle normalization to standard ranges.

    Default normalization: [0°, 360°)
    Centered at 0: (-180°, 180°]
    """

    @allure.title("Normalize angle > 360°")
    def test_normalize_positive_overflow(self):
        """Normalize angle > 360°."""
        with allure.step("Create 450° and normalize"):
            a = Angle(degrees=450)
            n = a.normalize()
        with allure.step(f"Result: {n.degrees}°"):
            assert math.isclose(n.degrees, 90, rel_tol=1e-10)

    @allure.title("Normalize negative angle to [0, 360)")
    def test_normalize_negative(self):
        """Normalize negative angle to [0, 360)."""
        with allure.step("Create -90° and normalize"):
            a = Angle(degrees=-90)
            n = a.normalize()
        with allure.step(f"Result: {n.degrees}°"):
            assert math.isclose(n.degrees, 270, rel_tol=1e-10)

    @allure.title("Normalize very negative angle")
    def test_normalize_large_negative(self):
        """Normalize very negative angle."""
        with allure.step("Create -450° and normalize"):
            a = Angle(degrees=-450)
            n = a.normalize()
        with allure.step(f"Result: {n.degrees}°"):
            assert math.isclose(n.degrees, 270, rel_tol=1e-10)

    @allure.title("Normalize to (-180, 180] - positive case")
    def test_normalize_centered_positive(self):
        """Normalize to (-180, 180] - positive case."""
        with allure.step("Create 270° and normalize(center=0)"):
            a = Angle(degrees=270)
            n = a.normalize(center=0)
        with allure.step(f"Result: {n.degrees}°"):
            assert math.isclose(n.degrees, -90, rel_tol=1e-10)

    @allure.title("180° stays at 180° when centered at 0")
    def test_normalize_centered_at_180(self):
        """180° stays at 180° when centered at 0."""
        with allure.step("Create 180° and normalize(center=0)"):
            a = Angle(degrees=180)
            n = a.normalize(center=0)
        with allure.step(f"Result: {n.degrees}° (|n| = 180)"):
            assert math.isclose(abs(n.degrees), 180, rel_tol=1e-10)

    @pytest.mark.edge
    @allure.title("Normalization at exact boundary")
    def test_normalize_at_boundary(self):
        """Test normalization at exact boundary."""
        with allure.step("Create 360° and normalize"):
            a = Angle(degrees=360)
            n = a.normalize()
        with allure.step(f"Result: {n.degrees}°"):
            assert math.isclose(n.degrees, 0, abs_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  TRIGONOMETRY
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Angle Trigonometry")
class TestAngleTrigonometry:
    """
    Tests for trigonometric functions on angles.

    These methods work directly on the angle's value,
    converting to radians internally.
    """

    # ─── Sine ───────────────────────────────────────────────────────────────

    @allure.title("sin(90°) = 1")
    def test_sin_90(self):
        """sin(90°) = 1."""
        with allure.step("Calculate sin(90°)"):
            a = Angle(degrees=90)
            result = a.sin()
        with allure.step(f"Result: {result}"):
            assert math.isclose(result, 1.0, rel_tol=1e-10)

    @allure.title("sin(0°) = 0")
    def test_sin_0(self):
        """sin(0°) = 0."""
        with allure.step("Calculate sin(0°)"):
            a = Angle(degrees=0)
            result = a.sin()
        with allure.step(f"Result: {result}"):
            assert math.isclose(result, 0.0, abs_tol=1e-10)

    @allure.title("sin(30°) = 0.5")
    def test_sin_30(self):
        """sin(30°) = 0.5."""
        with allure.step("Calculate sin(30°)"):
            a = Angle(degrees=30)
            result = a.sin()
        with allure.step(f"Result: {result}"):
            assert math.isclose(result, 0.5, rel_tol=1e-10)

    # ─── Cosine ─────────────────────────────────────────────────────────────

    @allure.title("cos(0°) = 1")
    def test_cos_0(self):
        """cos(0°) = 1."""
        with allure.step("Calculate cos(0°)"):
            a = Angle(degrees=0)
            result = a.cos()
        with allure.step(f"Result: {result}"):
            assert math.isclose(result, 1.0, rel_tol=1e-10)

    @allure.title("cos(90°) = 0")
    def test_cos_90(self):
        """cos(90°) = 0."""
        with allure.step("Calculate cos(90°)"):
            a = Angle(degrees=90)
            result = a.cos()
        with allure.step(f"Result: {result}"):
            assert math.isclose(result, 0.0, abs_tol=1e-10)

    @allure.title("cos(60°) = 0.5")
    def test_cos_60(self):
        """cos(60°) = 0.5."""
        with allure.step("Calculate cos(60°)"):
            a = Angle(degrees=60)
            result = a.cos()
        with allure.step(f"Result: {result}"):
            assert math.isclose(result, 0.5, rel_tol=1e-10)

    # ─── Tangent ────────────────────────────────────────────────────────────

    @allure.title("tan(45°) = 1")
    def test_tan_45(self):
        """tan(45°) = 1."""
        with allure.step("Calculate tan(45°)"):
            a = Angle(degrees=45)
            result = a.tan()
        with allure.step(f"Result: {result}"):
            assert math.isclose(result, 1.0, rel_tol=1e-10)

    @allure.title("tan(0°) = 0")
    def test_tan_0(self):
        """tan(0°) = 0."""
        with allure.step("Calculate tan(0°)"):
            a = Angle(degrees=0)
            result = a.tan()
        with allure.step(f"Result: {result}"):
            assert math.isclose(result, 0.0, abs_tol=1e-10)


# ═══════════════════════════════════════════════════════════════════════════════
#  ANGULAR SEPARATION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Angular Separation")
class TestAngularSeparation:
    """
    Tests for calculating angular separation between celestial coordinates.

    Uses the Vincenty formula for numerical stability at all separations.
    """

    @allure.title("Separation of point with itself is zero")
    def test_same_point_zero_separation(self):
        """Separation of a point with itself is zero."""
        with allure.step("Create point (RA=12h, Dec=45°)"):
            ra = Angle(hours=12)
            dec = Angle(degrees=45)
        with allure.step("Calculate separation with itself"):
            sep = angular_separation(ra, dec, ra, dec)
        with allure.step(f"Result: {sep.degrees}°"):
            assert math.isclose(sep.degrees, 0, abs_tol=1e-10)

    @allure.title("North to South pole is 180°")
    def test_pole_to_pole_180_degrees(self):
        """North to South pole is 180°."""
        with allure.step("Calculate separation NP to SP"):
            ra = Angle(hours=0)
            sep = angular_separation(
                ra, Angle(degrees=90),
                ra, Angle(degrees=-90)
            )
        with allure.step(f"Result: {sep.degrees}°"):
            assert math.isclose(sep.degrees, 180, rel_tol=1e-10)

    @allure.title("6 hours apart on equator is 90°")
    def test_equator_90_degrees_apart(self):
        """6 hours apart on equator is 90°."""
        with allure.step("Calculate separation on equator (0h to 6h)"):
            dec = Angle(degrees=0)
            sep = angular_separation(
                Angle(hours=0), dec,
                Angle(hours=6), dec
            )
        with allure.step(f"Result: {sep.degrees}°"):
            assert math.isclose(sep.degrees, 90, rel_tol=1e-10)

    @allure.title("12 hours apart on equator is 180°")
    def test_equator_180_degrees_apart(self):
        """12 hours apart on equator is 180°."""
        with allure.step("Calculate separation on equator (0h to 12h)"):
            dec = Angle(degrees=0)
            sep = angular_separation(
                Angle(hours=0), dec,
                Angle(hours=12), dec
            )
        with allure.step(f"Result: {sep.degrees}°"):
            assert math.isclose(sep.degrees, 180, rel_tol=1e-10)

    @pytest.mark.golden
    @allure.title("Sirius to Betelgeuse separation ≈ 27°")
    @allure.description("""
    Known separation: Sirius to Betelgeuse ≈ 27°.

    Sirius: RA 6h45m, Dec -16°43'
    Betelgeuse: RA 5h55m, Dec +7°24'
    """)
    def test_sirius_betelgeuse_separation(self):
        """Known separation: Sirius to Betelgeuse ≈ 27°."""
        with allure.step("Set Sirius: RA 6h45m, Dec -16°43'"):
            sirius_ra = Angle.from_hms(6, 45, 0)
            sirius_dec = Angle.from_dms(-16, 43, 0)
        with allure.step("Set Betelgeuse: RA 5h55m, Dec +7°24'"):
            betel_ra = Angle.from_hms(5, 55, 0)
            betel_dec = Angle.from_dms(7, 24, 0)
        with allure.step("Calculate separation"):
            sep = angular_separation(sirius_ra, sirius_dec, betel_ra, betel_dec)
        with allure.step(f"Result: {sep.degrees:.1f}° (expected 26-28°)"):
            assert 26 < sep.degrees < 28

    @pytest.mark.verbose
    @allure.title("Verbose mode produces calculation steps")
    def test_verbose_output(self):
        """Verbose mode produces calculation steps."""
        with allure.step("Create verbose context"):
            ctx = VerboseContext()
        with allure.step("Calculate separation with verbose=ctx"):
            angular_separation(
                Angle(hours=12), Angle(degrees=45),
                Angle(hours=13), Angle(degrees=46),
                verbose=ctx
            )
        with allure.step(f"Steps recorded: {len(ctx.steps)}"):
            assert len(ctx.steps) > 0


# ═══════════════════════════════════════════════════════════════════════════════
#  POSITION ANGLE
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Position Angle")
class TestPositionAngle:
    """
    Tests for calculating position angle between celestial coordinates.

    Position angle is measured N through E:
      - 0° = North
      - 90° = East
      - 180° = South
      - 270° = West
    """

    @allure.title("Point due north has PA = 0°")
    def test_due_north_is_0(self):
        """Point due north has PA = 0°."""
        with allure.step("Calculate PA to point 1° north"):
            ra = Angle(hours=12)
            pa = position_angle(
                ra, Angle(degrees=45),
                ra, Angle(degrees=46)
            )
        with allure.step(f"Result: {pa.degrees}°"):
            assert math.isclose(pa.degrees, 0, abs_tol=0.1)

    @allure.title("Point due south has PA = 180°")
    def test_due_south_is_180(self):
        """Point due south has PA = 180°."""
        with allure.step("Calculate PA to point 1° south"):
            ra = Angle(hours=12)
            pa = position_angle(
                ra, Angle(degrees=45),
                ra, Angle(degrees=44)
            )
        with allure.step(f"Result: {pa.degrees}°"):
            assert math.isclose(pa.degrees, 180, abs_tol=0.1)

    @allure.title("Point due east has PA ≈ 90°")
    def test_due_east_is_90(self):
        """Point due east has PA ≈ 90°."""
        with allure.step("Calculate PA to point east on equator"):
            dec = Angle(degrees=0)
            pa = position_angle(
                Angle(hours=12), dec,
                Angle(hours=12.1), dec
            )
        with allure.step(f"Result: {pa.degrees}°"):
            assert math.isclose(pa.degrees, 90, abs_tol=1)

    @allure.title("Point due west has PA ≈ 270°")
    def test_due_west_is_270(self):
        """Point due west has PA ≈ 270°."""
        with allure.step("Calculate PA to point west on equator"):
            dec = Angle(degrees=0)
            pa = position_angle(
                Angle(hours=12), dec,
                Angle(hours=11.9), dec
            )
        with allure.step(f"Result: {pa.degrees}°"):
            assert math.isclose(pa.degrees, 270, abs_tol=1)


# ═══════════════════════════════════════════════════════════════════════════════
#  PROPERTY-BASED TESTS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Angle Properties (Hypothesis)")
class TestAngleProperties:
    """
    Property-based tests using Hypothesis.

    These tests verify invariants that should hold for all angles.
    """

    @allure.title("Normalized angle always in [0, 360)")
    @given(st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False))
    @settings(max_examples=200)
    def test_normalize_always_in_range(self, deg):
        """Normalized angle is always in [0, 360)."""
        a = Angle(degrees=deg)
        n = a.normalize()
        assert 0 <= n.degrees < 360

    @allure.title("sin²(θ) + cos²(θ) = 1")
    @given(st.floats(min_value=-1e6, max_value=1e6, allow_nan=False, allow_infinity=False))
    @settings(max_examples=200)
    def test_sin_squared_plus_cos_squared_is_one(self, deg):
        """sin²(θ) + cos²(θ) = 1."""
        a = Angle(degrees=deg)
        identity = a.sin()**2 + a.cos()**2
        assert math.isclose(identity, 1.0, rel_tol=1e-10)

    @allure.title("Addition is commutative: a + b = b + a")
    @given(st.floats(min_value=-10000, max_value=10000, allow_nan=False, allow_infinity=False),
           st.floats(min_value=-10000, max_value=10000, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100)
    def test_add_is_commutative(self, deg1, deg2):
        """a + b = b + a."""
        a = Angle(degrees=deg1)
        b = Angle(degrees=deg2)
        assert math.isclose((a + b).degrees, (b + a).degrees, rel_tol=1e-10)
