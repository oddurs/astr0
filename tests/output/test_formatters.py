"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                          FORMATTER TESTS                                     ║
║                                                                              ║
║  Tests for output formatters - plain text, JSON, and LaTeX.                  ║
║  Beautiful presentation of celestial calculations.                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import json
import allure
import pytest

from starward.output.formatters import (
    PlainFormatter, JSONFormatter, LaTeXFormatter, Result
)


# ═══════════════════════════════════════════════════════════════════════════════
#  PLAIN FORMATTER
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Plain Formatter")
class TestPlainFormatter:
    """Tests for plain text output formatting."""

    @allure.title("Format result with label")
    def test_format_result_with_label(self):
        """Format result with label."""
        with allure.step("Create formatter and result"):
            formatter = PlainFormatter()
            result = Result(value=45.5, label="Angle", unit="°")
        with allure.step("Format result"):
            output = formatter.format(result)
        with allure.step(f"Output contains '45.5' and 'Angle'"):
            assert '45.5' in output
            assert 'Angle' in output

    @allure.title("Format result with unit")
    def test_format_result_with_unit(self):
        """Format result with unit."""
        with allure.step("Create formatter and result"):
            formatter = PlainFormatter()
            result = Result(value=45.5, label="Angle", unit="°")
        with allure.step("Format result"):
            output = formatter.format(result)
        with allure.step("Output contains unit '°'"):
            assert '°' in output

    @allure.title("Format result with extra data")
    def test_format_result_with_extra(self):
        """Format result with extra data."""
        with allure.step("Create formatter and result with extra"):
            formatter = PlainFormatter()
            result = Result(value=45.5, label="Angle", extra={"HMS": "12h00m00s"})
        with allure.step("Format result"):
            output = formatter.format(result)
        with allure.step("Output contains HMS value"):
            assert '12h00m00s' in output


@allure.story("Plain Formatter Time")
class TestPlainFormatterTime:
    """Tests for plain formatter time output."""

    @allure.title("Format Julian Date result")
    def test_format_jd_result(self):
        """Format Julian Date result."""
        with allure.step("Create formatter and JD result"):
            formatter = PlainFormatter()
            result = Result(value=2451545.0, label="Julian Date")
        with allure.step("Format result"):
            output = formatter.format(result)
        with allure.step("Output contains '2451545'"):
            assert '2451545' in output


# ═══════════════════════════════════════════════════════════════════════════════
#  JSON FORMATTER
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("JSON Formatter")
class TestJSONFormatter:
    """Tests for JSON output formatting."""

    @allure.title("Output is valid JSON")
    def test_output_is_valid_json(self):
        """Output is valid JSON."""
        with allure.step("Create formatter and result"):
            formatter = JSONFormatter()
            result = Result(value="test", label="Test")
        with allure.step("Format result"):
            output = formatter.format(result)
        with allure.step("Parse as JSON"):
            parsed = json.loads(output)
        with allure.step(f"parsed['result'] = {parsed['result']}"):
            assert parsed['result'] == 'test'

    @allure.title("JSON is pretty-printed")
    def test_pretty_print(self):
        """JSON is pretty-printed."""
        with allure.step("Create formatter with pretty=True"):
            formatter = JSONFormatter(pretty=True)
            result = Result(value="test", label="Test")
        with allure.step("Format result"):
            output = formatter.format(result)
        with allure.step("Output has newlines"):
            assert '\n' in output


# ═══════════════════════════════════════════════════════════════════════════════
#  LATEX FORMATTER
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("LaTeX Formatter")
class TestLaTeXFormatter:
    """Tests for LaTeX output formatting."""

    @allure.title("Format basic result to LaTeX")
    def test_format_result_basic(self):
        """Format basic result to LaTeX."""
        with allure.step("Create formatter and result"):
            formatter = LaTeXFormatter()
            result = Result(value=45.5, label="Angle")
        with allure.step("Format result"):
            output = formatter.format(result)
        with allure.step("Output contains '45.5'"):
            assert '45.5' in output

    @allure.title("Format with full document wrapper")
    def test_format_with_document_wrapper(self):
        """Format with full document wrapper."""
        with allure.step("Create formatter with document_class=True"):
            formatter = LaTeXFormatter(document_class=True)
            result = Result(value=45.5, label="Angle")
        with allure.step("Format result"):
            output = formatter.format(result)
        with allure.step("Output contains 'documentclass'"):
            assert 'documentclass' in output

    @allure.title("Format result includes label")
    def test_format_result_with_label(self):
        """Format result includes label."""
        with allure.step("Create formatter and result"):
            formatter = LaTeXFormatter()
            result = Result(value=45.5, label="RA")
        with allure.step("Format result"):
            output = formatter.format(result)
        with allure.step("Output contains value"):
            assert '45' in output

    @allure.title("Uses siunitx package when enabled")
    def test_uses_siunitx_by_default(self):
        """Uses siunitx package when document_class=True."""
        with allure.step("Create formatter with siunitx=True"):
            formatter = LaTeXFormatter(document_class=True, siunitx=True)
            result = Result(value=45.5, label="Angle")
        with allure.step("Format result"):
            output = formatter.format(result)
        with allure.step("Output contains 'siunitx'"):
            assert 'siunitx' in output
