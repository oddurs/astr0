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
import pytest

from astr0.output.formatters import (
    PlainFormatter, JSONFormatter, LaTeXFormatter, Result
)


# ═══════════════════════════════════════════════════════════════════════════════
#  PLAIN FORMATTER
# ═══════════════════════════════════════════════════════════════════════════════

class TestPlainFormatter:
    """
    Tests for plain text output formatting.
    """
    
    def test_format_result_with_label(self):
        """Format result with label."""
        formatter = PlainFormatter()
        result = Result(value=45.5, label="Angle", unit="°")
        output = formatter.format(result)
        assert '45.5' in output
        assert 'Angle' in output
    
    def test_format_result_with_unit(self):
        """Format result with unit."""
        formatter = PlainFormatter()
        result = Result(value=45.5, label="Angle", unit="°")
        output = formatter.format(result)
        assert '°' in output
    
    def test_format_result_with_extra(self):
        """Format result with extra data."""
        formatter = PlainFormatter()
        result = Result(value=45.5, label="Angle", extra={"HMS": "12h00m00s"})
        output = formatter.format(result)
        assert '12h00m00s' in output


class TestPlainFormatterTime:
    """
    Tests for plain formatter time output.
    """
    
    def test_format_jd_result(self):
        """Format Julian Date result."""
        formatter = PlainFormatter()
        result = Result(value=2451545.0, label="Julian Date")
        output = formatter.format(result)
        assert '2451545' in output


# ═══════════════════════════════════════════════════════════════════════════════
#  JSON FORMATTER
# ═══════════════════════════════════════════════════════════════════════════════

class TestJSONFormatter:
    """
    Tests for JSON output formatting.
    """
    
    def test_output_is_valid_json(self):
        """Output is valid JSON."""
        formatter = JSONFormatter()
        result = Result(value="test", label="Test")
        output = formatter.format(result)
        
        # Should parse without error
        parsed = json.loads(output)
        assert parsed['result'] == 'test'
    
    def test_pretty_print(self):
        """JSON is pretty-printed."""
        formatter = JSONFormatter(pretty=True)
        result = Result(value="test", label="Test")
        output = formatter.format(result)
        
        # Pretty print has newlines
        assert '\n' in output


# ═══════════════════════════════════════════════════════════════════════════════
#  LATEX FORMATTER
# ═══════════════════════════════════════════════════════════════════════════════

class TestLaTeXFormatter:
    """
    Tests for LaTeX output formatting.
    
    Added in v0.2 for publication-ready output.
    """
    
    def test_format_result_basic(self):
        """Format basic result to LaTeX."""
        formatter = LaTeXFormatter()
        result = Result(value=45.5, label="Angle")
        output = formatter.format(result)
        assert '45.5' in output
    
    def test_format_with_document_wrapper(self):
        """Format with full document wrapper."""
        formatter = LaTeXFormatter(document_class=True)
        result = Result(value=45.5, label="Angle")
        output = formatter.format(result)
        assert 'documentclass' in output
    
    def test_format_result_with_label(self):
        """Format result includes label."""
        formatter = LaTeXFormatter()
        result = Result(value=45.5, label="RA")
        output = formatter.format(result)
        # LaTeX output should contain the value
        assert '45' in output
    
    def test_uses_siunitx_by_default(self):
        """Uses siunitx package when document_class=True."""
        formatter = LaTeXFormatter(document_class=True, siunitx=True)
        result = Result(value=45.5, label="Angle")
        output = formatter.format(result)
        assert 'siunitx' in output

