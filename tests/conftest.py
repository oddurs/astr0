"""
pytest configuration and shared fixtures for starward test suite.

This module provides common fixtures, test utilities, and configuration
that enable clean, modular, context-based testing across all starward modules.

Architecture:
    tests/
    ├── conftest.py              # This file - shared fixtures
    ├── core/                    # Core module tests
    │   ├── test_angles.py
    │   ├── test_coords.py
    │   ├── test_time.py
    │   ├── test_constants.py
    │   ├── test_sun.py
    │   ├── test_moon.py
    │   ├── test_observer.py
    │   └── test_visibility.py
    ├── cli/                     # CLI integration tests
    │   └── test_commands.py
    └── output/                  # Output formatter tests
        └── test_formatters.py
"""

from __future__ import annotations

import pytest
import platform
import shutil
from pathlib import Path
from datetime import datetime, timezone
from typing import Callable, Any

# Allure import (optional - graceful degradation if not installed)
try:
    import allure
    from allure_commons.types import Severity
    ALLURE_AVAILABLE = True
except ImportError:
    ALLURE_AVAILABLE = False


# =============================================================================
# Custom Test Output
# =============================================================================

def pytest_report_teststatus(report, config):
    """Customize test status characters for cleaner output."""
    if report.when == 'call':
        if report.passed:
            return 'passed', '✓', 'PASSED'
        elif report.failed:
            return 'failed', '✗', 'FAILED'
        elif report.skipped:
            return 'skipped', '○', 'SKIPPED'
    return None


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    """Add custom astronomy-themed summary at the end of test run."""
    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    skipped = len(terminalreporter.stats.get('skipped', []))
    errors = len(terminalreporter.stats.get('error', []))
    total = passed + failed + skipped + errors
    
    if total == 0:
        return
    
    # Calculate pass rate
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    # Build summary
    terminalreporter.write_line("")
    terminalreporter.write_line("─" * 60)
    terminalreporter.write_line("")
    
    terminalreporter.write_line(f"  {'Tests:':<12} {total:>6}")
    
    if passed > 0:
        terminalreporter.write_line(f"  {'Passed:':<12} {passed:>6}", green=True)
    if failed > 0:
        terminalreporter.write_line(f"  {'Failed:':<12} {failed:>6}", red=True)
    if skipped > 0:
        terminalreporter.write_line(f"  {'Skipped:':<12} {skipped:>6}", yellow=True)
    if errors > 0:
        terminalreporter.write_line(f"  {'Errors:':<12} {errors:>6}", red=True)
    
    terminalreporter.write_line(f"  {'Pass Rate:':<12} {pass_rate:>5.1f}%")
    terminalreporter.write_line("")


# =============================================================================
# Test Configuration
# =============================================================================

def pytest_configure(config):
    """Register custom markers for test categorization."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "golden: tests against known authoritative values")
    config.addinivalue_line("markers", "roundtrip: tests transform/inverse-transform identity")
    config.addinivalue_line("markers", "edge: tests edge cases and boundary conditions")
    config.addinivalue_line("markers", "verbose: tests verbose output functionality")


# =============================================================================
# Allure Report Integration
# =============================================================================

def pytest_collection_modifyitems(items):
    """Auto-apply Allure metadata based on test location and markers."""
    if not ALLURE_AVAILABLE:
        return

    for item in items:
        fspath = str(item.fspath)

        # Epic from test directory
        if "/core/" in fspath:
            item.add_marker(allure.epic("Core Library"))
        elif "/cli/" in fspath:
            item.add_marker(allure.epic("CLI Commands"))
        elif "/integration/" in fspath:
            item.add_marker(allure.epic("Integration"))
        elif "/output/" in fspath:
            item.add_marker(allure.epic("Output Formatting"))
        else:
            item.add_marker(allure.epic("Other"))

        # Feature from module name (test_angles.py -> "Angles")
        module_name = item.module.__name__.split(".")[-1]
        feature_name = module_name.replace("test_", "").replace("_", " ").title()
        item.add_marker(allure.feature(feature_name))

        # Story from test class name if present
        if item.cls:
            story_name = item.cls.__name__.replace("Test", "").replace("_", " ")
            item.add_marker(allure.story(story_name))

        # Map existing pytest markers to Allure severity
        if item.get_closest_marker("golden"):
            item.add_marker(allure.severity(Severity.CRITICAL))
        elif item.get_closest_marker("edge"):
            item.add_marker(allure.severity(Severity.NORMAL))
        elif item.get_closest_marker("roundtrip"):
            item.add_marker(allure.severity(Severity.NORMAL))
        elif item.get_closest_marker("slow"):
            item.add_marker(allure.severity(Severity.MINOR))
        elif item.get_closest_marker("verbose"):
            item.add_marker(allure.severity(Severity.TRIVIAL))


def pytest_sessionfinish(session, exitstatus):
    """Generate Allure environment and categories files after test run."""
    if not ALLURE_AVAILABLE:
        return

    allure_dir = Path("allure-results")
    if not allure_dir.exists():
        return

    # Generate environment.properties
    try:
        import starward
        starward_version = starward.__version__
    except Exception:
        starward_version = "unknown"

    env_content = f"""Python.Version={platform.python_version()}
Platform={platform.system()} {platform.release()}
Starward.Version={starward_version}
Pytest.Version={pytest.__version__}
"""
    (allure_dir / "environment.properties").write_text(env_content)

    # Copy categories.json if it exists
    categories_src = Path(__file__).parent / "allure" / "categories.json"
    if categories_src.exists():
        shutil.copy(categories_src, allure_dir / "categories.json")


# =============================================================================
# Allure Fixture Decorator Helper
# =============================================================================

def allure_title(title: str):
    """Apply allure.title decorator if allure is available, otherwise no-op."""
    if ALLURE_AVAILABLE:
        return allure.title(title)
    return lambda f: f


# =============================================================================
# Tolerance Fixtures
# =============================================================================

@pytest.fixture
@allure_title("Angle Tolerance (0.1 arcsec)")
def angle_tolerance():
    """Tolerance for angle comparisons (arcseconds)."""
    return 0.1  # 0.1 arcsecond

@pytest.fixture
@allure_title("Time Tolerance (1.0 sec)")
def time_tolerance():
    """Tolerance for time comparisons (seconds)."""
    return 1.0  # 1 second

@pytest.fixture
@allure_title("Position Tolerance (0.01 deg)")
def position_tolerance():
    """Tolerance for position comparisons (degrees)."""
    return 0.01  # ~36 arcseconds

@pytest.fixture
@allure_title("Distance Tolerance (0.1%)")
def distance_tolerance():
    """Tolerance for distance comparisons (relative)."""
    return 0.001  # 0.1%


# =============================================================================
# Angle Fixtures
# =============================================================================

@pytest.fixture
def sample_angles():
    """Common test angles."""
    from starward.core.angles import Angle
    return {
        'zero': Angle(degrees=0),
        'right': Angle(degrees=90),
        'straight': Angle(degrees=180),
        'reflex': Angle(degrees=270),
        'full': Angle(degrees=360),
        'small': Angle(arcseconds=1),
        'negative': Angle(degrees=-45),
        'ra_12h': Angle(hours=12),
        'dec_pole': Angle(degrees=90),
    }


# =============================================================================
# Coordinate Fixtures
# =============================================================================

@pytest.fixture
def galactic_center():
    """Galactic center coordinates."""
    from starward.core.coords import ICRSCoord
    # Sgr A* - ICRS J2000
    return ICRSCoord.from_degrees(266.4168, -29.0078)

@pytest.fixture
def north_celestial_pole():
    """North Celestial Pole."""
    from starward.core.coords import ICRSCoord
    return ICRSCoord.from_degrees(0.0, 90.0)

@pytest.fixture
def vernal_equinox():
    """Vernal equinox point."""
    from starward.core.coords import ICRSCoord
    return ICRSCoord.from_degrees(0.0, 0.0)

@pytest.fixture
def famous_stars():
    """Well-known stars with accurate coordinates."""
    from starward.core.coords import ICRSCoord
    return {
        'sirius': ICRSCoord.parse("06h45m08.9s -16d42m58s"),
        'vega': ICRSCoord.parse("18h36m56.3s +38d47m01s"),
        'polaris': ICRSCoord.parse("02h31m49.1s +89d15m51s"),
        'betelgeuse': ICRSCoord.parse("05h55m10.3s +07d24m25s"),
        'rigel': ICRSCoord.parse("05h14m32.3s -08d12m06s"),
    }

@pytest.fixture
def messier_objects():
    """Messier objects with accurate coordinates."""
    from starward.core.coords import ICRSCoord
    return {
        'M31': ICRSCoord.parse("00h42m44.3s +41d16m09s"),  # Andromeda
        'M42': ICRSCoord.parse("05h35m17.3s -05d23m28s"),  # Orion Nebula
        'M45': ICRSCoord.parse("03h47m00s +24d07m00s"),    # Pleiades
        'M1': ICRSCoord.parse("05h34m31.9s +22d00m52s"),   # Crab Nebula
        'M13': ICRSCoord.parse("16h41m41.6s +36d27m41s"),  # Hercules Cluster
    }


# =============================================================================
# Time Fixtures
# =============================================================================

@pytest.fixture
@allure_title("J2000.0 Epoch")
def j2000_epoch():
    """J2000.0 epoch."""
    from starward.core.time import JulianDate
    return JulianDate(2451545.0)

@pytest.fixture
@allure_title("Historical Reference Dates")
def known_dates():
    """Well-known dates for testing."""
    from starward.core.time import JulianDate
    return {
        'j2000': JulianDate(2451545.0),           # 2000-01-01 12:00 TT
        'unix_epoch': JulianDate(2440587.5),      # 1970-01-01 00:00 UTC
        'mjd_epoch': JulianDate(2400000.5),       # MJD = 0
        'sputnik': JulianDate(2436116.31),        # 1957-10-04
        'apollo11': JulianDate(2440423.5),        # 1969-07-20
    }


# =============================================================================
# Observer Fixtures
# =============================================================================

@pytest.fixture
@allure_title("Greenwich Observatory")
def greenwich():
    """Royal Observatory Greenwich."""
    from starward.core.observer import Observer
    return Observer.from_degrees(
        name="Greenwich",
        latitude=51.4772,
        longitude=-0.0005,
        elevation=62.0,
        timezone="Europe/London"
    )

@pytest.fixture
@allure_title("Mauna Kea Observatory")
def mauna_kea():
    """Mauna Kea Observatory, Hawaii."""
    from starward.core.observer import Observer
    return Observer.from_degrees(
        name="Mauna Kea",
        latitude=19.8208,
        longitude=-155.4681,
        elevation=4207.0,
        timezone="Pacific/Honolulu"
    )

@pytest.fixture
@allure_title("Paranal Observatory")
def paranal():
    """ESO Paranal Observatory, Chile."""
    from starward.core.observer import Observer
    return Observer.from_degrees(
        name="Paranal",
        latitude=-24.6253,
        longitude=-70.4043,
        elevation=2635.0,
        timezone="America/Santiago"
    )

@pytest.fixture
@allure_title("North Pole Observer")
def north_pole():
    """North Pole observer."""
    from starward.core.observer import Observer
    return Observer.from_degrees(
        name="North Pole",
        latitude=90.0,
        longitude=0.0,
        elevation=0.0
    )

@pytest.fixture
@allure_title("Equator Observer")
def equator():
    """Observer on the equator."""
    from starward.core.observer import Observer
    return Observer.from_degrees(
        name="Equator",
        latitude=0.0,
        longitude=0.0,
        elevation=0.0
    )


# =============================================================================
# Verbose Context Fixtures
# =============================================================================

@pytest.fixture
def verbose_context():
    """Create a verbose context for testing."""
    from starward.verbose import VerboseContext
    return VerboseContext()


# =============================================================================
# Assertion Helpers
# =============================================================================

@pytest.fixture
def assert_angle_close():
    """Assert two angles are close within tolerance."""
    def _assert(angle1, angle2, atol_arcsec=0.1, msg=""):
        from starward.core.angles import Angle
        if isinstance(angle1, Angle):
            angle1 = angle1.degrees
        if isinstance(angle2, Angle):
            angle2 = angle2.degrees
        atol_deg = atol_arcsec / 3600.0
        assert abs(angle1 - angle2) < atol_deg, f"{msg}: {angle1}° != {angle2}° (tol: {atol_arcsec}\")"
    return _assert

@pytest.fixture
def assert_coord_close():
    """Assert two coordinates are close."""
    def _assert(coord1, coord2, atol_arcsec=1.0, msg=""):
        from starward.core.angles import angular_separation
        sep = angular_separation(coord1.ra, coord1.dec, coord2.ra, coord2.dec)
        atol_deg = atol_arcsec / 3600.0
        assert sep.degrees < atol_deg, f"{msg}: separation {sep.degrees*3600:.2f}\" > {atol_arcsec}\""
    return _assert


# =============================================================================
# Parameterized Test Data
# =============================================================================

# Standard angles for comprehensive testing
STANDARD_ANGLES = [
    0, 1, 30, 45, 60, 89.9, 90, 90.1, 120, 135, 150, 179.9, 180,
    180.1, 225, 270, 315, 359.9, 360, -1, -30, -45, -90, -180, -360
]

# Standard latitudes for observer tests
STANDARD_LATITUDES = [-90, -66.5, -45, -23.5, 0, 23.5, 45, 66.5, 90]

# Standard longitudes
STANDARD_LONGITUDES = [-180, -120, -60, 0, 60, 120, 180]


# =============================================================================
# CLI Test Fixtures
# =============================================================================

@pytest.fixture
def cli_runner():
    """Click CLI test runner."""
    from click.testing import CliRunner
    return CliRunner()

@pytest.fixture
def cli_main():
    """Main CLI entry point."""
    from starward.cli import main
    return main
