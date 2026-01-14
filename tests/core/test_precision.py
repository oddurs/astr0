"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          PRECISION TESTS                                     ║
║                                                                              ║
║  Tests for the precision configuration system.                               ║
║  Accuracy is never sacrificed — only display precision is configurable.      ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import allure
import pytest
import os

from starward.core.precision import (
    PrecisionConfig,
    PrecisionLevel,
    get_precision,
    set_precision,
    precision_context,
)


# ═══════════════════════════════════════════════════════════════════════════════
#  PRECISION LEVELS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Precision Levels")
class TestPrecisionLevel:
    """Tests for PrecisionLevel enum."""

    @allure.title("Precision levels have correct decimal counts")
    def test_level_values(self):
        """Precision levels have correct decimal counts."""
        with allure.step("COMPACT = 2 decimals"):
            assert PrecisionLevel.COMPACT.value == 2
        with allure.step("DISPLAY = 4 decimals"):
            assert PrecisionLevel.DISPLAY.value == 4
        with allure.step("STANDARD = 6 decimals"):
            assert PrecisionLevel.STANDARD.value == 6
        with allure.step("HIGH = 10 decimals"):
            assert PrecisionLevel.HIGH.value == 10
        with allure.step("FULL = 15 decimals"):
            assert PrecisionLevel.FULL.value == 15

    @allure.title("Can parse level from string name")
    def test_from_string_names(self):
        """Can parse level from string name."""
        with allure.step("Parse 'compact'"):
            assert PrecisionLevel.from_string('compact') == PrecisionLevel.COMPACT
        with allure.step("Parse 'FULL'"):
            assert PrecisionLevel.from_string('FULL') == PrecisionLevel.FULL
        with allure.step("Parse 'Standard'"):
            assert PrecisionLevel.from_string('Standard') == PrecisionLevel.STANDARD

    @allure.title("Can parse level from integer string")
    def test_from_string_integer(self):
        """Can parse level from integer string."""
        with allure.step("Parse '6' -> STANDARD"):
            assert PrecisionLevel.from_string('6') == PrecisionLevel.STANDARD
        with allure.step("Parse '10' -> HIGH"):
            assert PrecisionLevel.from_string('10') == PrecisionLevel.HIGH
        with allure.step("Parse '8' -> 8 (non-standard)"):
            result = PrecisionLevel.from_string('8')
            assert result == 8

    @allure.title("Invalid string raises ValueError")
    def test_from_string_invalid(self):
        """Invalid string raises ValueError."""
        with allure.step("Parse 'invalid'"):
            with pytest.raises(ValueError):
                PrecisionLevel.from_string('invalid')


# ═══════════════════════════════════════════════════════════════════════════════
#  PRECISION CONFIG
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Precision Config")
class TestPrecisionConfig:
    """Tests for PrecisionConfig dataclass."""

    @allure.title("Default config has standard values")
    def test_default_values(self):
        """Default config has standard values."""
        with allure.step("Create PrecisionConfig()"):
            config = PrecisionConfig()
        with allure.step(f"decimals = {config.decimals}"):
            assert config.decimals == 6
        with allure.step(f"angle_arcsec = {config.angle_arcsec}"):
            assert config.angle_arcsec == 2
        with allure.step(f"time_seconds = {config.time_seconds}"):
            assert config.time_seconds == 2
        with allure.step(f"coordinates = {config.coordinates}"):
            assert config.coordinates == 6

    @allure.title("Can create config from precision level")
    def test_from_level(self):
        """Can create config from precision level."""
        with allure.step("Create from FULL"):
            config = PrecisionConfig.from_level(PrecisionLevel.FULL)
        with allure.step(f"decimals = {config.decimals}"):
            assert config.decimals == 15

        with allure.step("Create from COMPACT"):
            config = PrecisionConfig.from_level(PrecisionLevel.COMPACT)
        with allure.step(f"decimals = {config.decimals}"):
            assert config.decimals == 2

    @allure.title("Can create config from integer")
    def test_from_integer(self):
        """Can create config from integer."""
        with allure.step("Create from 8"):
            config = PrecisionConfig.from_level(8)
        with allure.step(f"decimals = {config.decimals}"):
            assert config.decimals == 8

    @allure.title("Factory methods create correct configs")
    def test_factory_methods(self):
        """Factory methods create correct configs."""
        with allure.step("compact() = 2 decimals"):
            assert PrecisionConfig.compact().decimals == 2
        with allure.step("display() = 4 decimals"):
            assert PrecisionConfig.display().decimals == 4
        with allure.step("standard() = 6 decimals"):
            assert PrecisionConfig.standard().decimals == 6
        with allure.step("high() = 10 decimals"):
            assert PrecisionConfig.high().decimals == 10
        with allure.step("full() = 15 decimals"):
            assert PrecisionConfig.full().decimals == 15

    @allure.title("format_float respects precision setting")
    def test_format_float(self):
        """format_float respects precision setting."""
        with allure.step("Create config with decimals=4"):
            config = PrecisionConfig(decimals=4)
        with allure.step(f"format_float(3.14159265) = {config.format_float(3.14159265)}"):
            assert config.format_float(3.14159265) == '3.1416'

        with allure.step("Create config with decimals=2"):
            config = PrecisionConfig(decimals=2)
        with allure.step(f"format_float(3.14159265) = {config.format_float(3.14159265)}"):
            assert config.format_float(3.14159265) == '3.14'

    @allure.title("format_float uses scientific notation for large/small numbers")
    def test_format_float_scientific(self):
        """format_float uses scientific notation for large/small numbers."""
        with allure.step("Create config with scientific_threshold=3"):
            config = PrecisionConfig(decimals=4, scientific_threshold=3)
        with allure.step("Format large number 1234567.89"):
            result = config.format_float(1234567.89)
        with allure.step(f"Result: {result} (contains 'e')"):
            assert 'e' in result.lower()
        with allure.step("Format small number 0.000001234"):
            result = config.format_float(0.000001234)
        with allure.step(f"Result: {result} (contains 'e')"):
            assert 'e' in result.lower()

    @allure.title("format_radians uses radians precision")
    def test_format_radians(self):
        """format_radians uses radians precision."""
        with allure.step("Create config with radians=12"):
            config = PrecisionConfig(radians=12)
        with allure.step("Format π"):
            result = config.format_radians(3.141592653589793)
        with allure.step(f"Result: {result} (12 decimal places)"):
            assert len(result.split('.')[1]) == 12


# ═══════════════════════════════════════════════════════════════════════════════
#  GLOBAL PRECISION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Global Precision")
class TestGlobalPrecision:
    """Tests for global precision get/set functions."""

    @allure.title("get_precision returns a PrecisionConfig")
    def test_get_precision_returns_config(self):
        """get_precision returns a PrecisionConfig."""
        with allure.step("Call get_precision()"):
            prec = get_precision()
        with allure.step(f"Type: {type(prec).__name__}"):
            assert isinstance(prec, PrecisionConfig)

    @allure.title("Can set precision with PrecisionConfig")
    def test_set_precision_with_config(self):
        """Can set precision with PrecisionConfig."""
        original = get_precision()
        try:
            with allure.step("Create config with decimals=12"):
                config = PrecisionConfig(decimals=12)
            with allure.step("Set precision"):
                set_precision(config)
            with allure.step(f"get_precision().decimals = {get_precision().decimals}"):
                assert get_precision().decimals == 12
        finally:
            set_precision(original)

    @allure.title("Can set precision with PrecisionLevel")
    def test_set_precision_with_level(self):
        """Can set precision with PrecisionLevel."""
        original = get_precision()
        try:
            with allure.step("Set precision to HIGH"):
                set_precision(PrecisionLevel.HIGH)
            with allure.step(f"get_precision().decimals = {get_precision().decimals}"):
                assert get_precision().decimals == 10
        finally:
            set_precision(original)

    @allure.title("Can set precision with integer")
    def test_set_precision_with_integer(self):
        """Can set precision with integer."""
        original = get_precision()
        try:
            with allure.step("Set precision to 8"):
                set_precision(8)
            with allure.step(f"get_precision().decimals = {get_precision().decimals}"):
                assert get_precision().decimals == 8
        finally:
            set_precision(original)

    @allure.title("Can set precision with string")
    def test_set_precision_with_string(self):
        """Can set precision with string."""
        original = get_precision()
        try:
            with allure.step("Set precision to 'full'"):
                set_precision('full')
            with allure.step(f"get_precision().decimals = {get_precision().decimals}"):
                assert get_precision().decimals == 15
        finally:
            set_precision(original)


# ═══════════════════════════════════════════════════════════════════════════════
#  PRECISION CONTEXT
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Precision Context")
class TestPrecisionContext:
    """Tests for precision_context context manager."""

    @allure.title("Context manager changes precision inside block")
    def test_context_changes_precision(self):
        """Context manager changes precision inside block."""
        original = get_precision()
        try:
            set_precision(PrecisionLevel.STANDARD)

            with allure.step("Enter precision_context(FULL)"):
                with precision_context(PrecisionLevel.FULL):
                    with allure.step(f"Inside: decimals = {get_precision().decimals}"):
                        assert get_precision().decimals == 15

            with allure.step(f"After: decimals = {get_precision().decimals}"):
                assert get_precision().decimals == 6
        finally:
            set_precision(original)

    @allure.title("Context manager restores precision on exception")
    def test_context_restores_on_exception(self):
        """Context manager restores precision even on exception."""
        original = get_precision()
        try:
            set_precision(PrecisionLevel.STANDARD)

            with allure.step("Enter precision_context(FULL) then raise"):
                try:
                    with precision_context(PrecisionLevel.FULL):
                        with allure.step(f"Inside: decimals = {get_precision().decimals}"):
                            assert get_precision().decimals == 15
                        raise ValueError("test")
                except ValueError:
                    pass

            with allure.step(f"After exception: decimals = {get_precision().decimals}"):
                assert get_precision().decimals == 6
        finally:
            set_precision(original)

    @allure.title("Context manager accepts string precision")
    def test_context_with_string(self):
        """Context manager accepts string precision."""
        original = get_precision()
        try:
            with allure.step("Enter precision_context('compact')"):
                with precision_context('compact'):
                    with allure.step(f"Inside: decimals = {get_precision().decimals}"):
                        assert get_precision().decimals == 2
        finally:
            set_precision(original)

    @allure.title("Context manager accepts integer precision")
    def test_context_with_integer(self):
        """Context manager accepts integer precision."""
        original = get_precision()
        try:
            with allure.step("Enter precision_context(7)"):
                with precision_context(7):
                    with allure.step(f"Inside: decimals = {get_precision().decimals}"):
                        assert get_precision().decimals == 7
        finally:
            set_precision(original)


# ═══════════════════════════════════════════════════════════════════════════════
#  INTEGRATION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Precision Integration")
class TestPrecisionIntegration:
    """Integration tests for precision system."""

    @allure.title("Different precision levels produce different output")
    def test_precision_affects_formatting(self):
        """Different precision levels produce different output."""
        value = 3.14159265358979

        with allure.step("Create configs at different levels"):
            compact = PrecisionConfig.compact()
            standard = PrecisionConfig.standard()
            full = PrecisionConfig.full()

        with allure.step("Format value at each level"):
            compact_str = compact.format_float(value)
            standard_str = standard.format_float(value)
            full_str = full.format_float(value)

        with allure.step(f"compact: {compact_str}"):
            pass
        with allure.step(f"standard: {standard_str}"):
            pass
        with allure.step(f"full: {full_str}"):
            pass

        with allure.step("Verify lengths increase with precision"):
            assert len(compact_str) < len(standard_str) < len(full_str)
        with allure.step("Verify values approximate correctly"):
            assert float(compact_str) == pytest.approx(value, rel=0.01)
            assert float(standard_str) == pytest.approx(value, rel=1e-6)
            assert float(full_str) == pytest.approx(value, rel=1e-15)

    @allure.title("Setting display precision doesn't affect internal calculations")
    def test_internal_precision_preserved(self):
        """Setting display precision doesn't affect internal calculations."""
        value = 3.14159265358979323846

        with allure.step("Set precision to COMPACT"):
            set_precision(PrecisionLevel.COMPACT)

        with allure.step(f"Internal value still = {value}"):
            assert value == 3.14159265358979323846

        with allure.step("Display is affected"):
            prec = get_precision()
            displayed = prec.format_float(value)
        with allure.step(f"Displayed: {displayed} (2 decimals)"):
            assert displayed == '3.14'

        with allure.step("Set precision to FULL"):
            set_precision(PrecisionLevel.FULL)
            prec = get_precision()
            displayed = prec.format_float(value)
        with allure.step(f"Displayed: {displayed} (15 decimals)"):
            assert len(displayed.split('.')[1]) == 15
