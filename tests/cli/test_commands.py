"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                         CLI COMMAND TESTS                                    ║
║                                                                              ║
║  Integration tests for the starward command-line interface.                     ║
║  Verifying the bridge between algorithms and astronomers.                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import allure
import pytest
from click.testing import CliRunner

from starward.cli import main


# ═══════════════════════════════════════════════════════════════════════════════
#  TEST FIXTURES
# ═══════════════════════════════════════════════════════════════════════════════

@pytest.fixture
def runner():
    """Create a CLI test runner."""
    return CliRunner()


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN COMMAND
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Main Command")
class TestMainCommand:
    """Tests for the main starward command entry point."""

    @allure.title("--help displays usage information")
    def test_help(self, runner):
        """--help displays usage information."""
        with allure.step("Run 'starward --help'"):
            result = runner.invoke(main, ['--help'])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains usage info"):
            assert 'starward' in result.output.lower() or 'usage' in result.output.lower()

    @allure.title("--version displays version string")
    def test_version(self, runner):
        """--version displays version string."""
        with allure.step("Run 'starward --version'"):
            result = runner.invoke(main, ['--version'])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains version"):
            assert '0.' in result.output


# ═══════════════════════════════════════════════════════════════════════════════
#  TIME COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Time Commands")
class TestTimeCommands:
    """Tests for time-related CLI commands."""

    @allure.title("time now displays current time")
    def test_time_now(self, runner):
        """time now displays current time."""
        with allure.step("Run 'time now'"):
            result = runner.invoke(main, ['time', 'now'])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains JD or UTC"):
            assert 'JD' in result.output or 'UTC' in result.output

    @allure.title("time convert handles Julian Date")
    def test_time_convert_jd(self, runner):
        """time convert handles Julian Date."""
        with allure.step("Run 'time convert 2451545.0'"):
            result = runner.invoke(main, ['time', 'convert', '2451545.0'])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains 2000 (J2000.0)"):
            assert '2000' in result.output

    @pytest.mark.skip(reason="gmst command not implemented - use lst instead")
    @allure.title("time gmst calculates sidereal time")
    def test_time_gmst(self, runner):
        """time gmst calculates sidereal time."""
        result = runner.invoke(main, ['time', 'gmst', '2451545.0'])
        assert result.exit_code == 0

    @allure.title("time lst calculates local sidereal time")
    def test_time_lst(self, runner):
        """time lst calculates local sidereal time."""
        with allure.step("Run 'time lst --lon -75.0'"):
            result = runner.invoke(main, ['time', 'lst', '--', '-75.0'])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  ANGLE COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Angle Commands")
class TestAngleCommands:
    """Tests for angle-related CLI commands."""

    @allure.title("angle convert displays conversions")
    def test_angle_convert_degrees(self, runner):
        """angle convert displays conversions."""
        with allure.step("Run 'angle convert 45.5'"):
            result = runner.invoke(main, ['angle', 'convert', '45.5'])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains 45"):
            assert '45' in result.output

    @pytest.mark.skip(reason="DMS parsing not supported in angle convert - use numeric degrees")
    @allure.title("angle convert handles DMS input")
    def test_angle_convert_dms(self, runner):
        """angle convert handles DMS input."""
        result = runner.invoke(main, ['angle', 'convert', '45d30m00s'])
        assert result.exit_code == 0

    @pytest.mark.skip(reason="HMS parsing not supported in angle convert - use --unit hours")
    @allure.title("angle convert handles HMS input")
    def test_angle_convert_hms(self, runner):
        """angle convert handles HMS input."""
        result = runner.invoke(main, ['angle', 'convert', '12h30m00s'])
        assert result.exit_code == 0

    @allure.title("angle sep calculates angular separation")
    def test_angle_sep(self, runner):
        """angle sep calculates angular separation."""
        with allure.step("Run 'angle sep' with two coordinates"):
            result = runner.invoke(main, [
                'angle', 'sep',
                '10h00m00s +20d00m00s',
                '10h10m00s +21d00m00s'
            ])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  COORDINATE COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Coordinate Commands")
class TestCoordCommands:
    """Tests for coordinate-related CLI commands."""

    @allure.title("coord transform converts to Galactic")
    def test_coord_transform_to_galactic(self, runner):
        """coord transform converts to Galactic."""
        with allure.step("Run 'coord transform --to galactic'"):
            result = runner.invoke(main, [
                'coord', 'transform',
                '12h00m00s +45d00m00s',
                '--to', 'galactic'
            ])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains galactic coords"):
            assert 'l' in result.output.lower() or 'galactic' in result.output.lower()

    @allure.title("coord parse displays coordinate components")
    def test_coord_parse(self, runner):
        """coord parse displays coordinate components."""
        with allure.step("Run 'coord parse'"):
            result = runner.invoke(main, [
                'coord', 'parse',
                '12h00m00s +45d00m00s'
            ])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Constants Commands")
class TestConstantsCommands:
    """Tests for constants-related CLI commands."""

    @allure.title("const list displays all constants")
    def test_const_list(self, runner):
        """const list displays all constants."""
        with allure.step("Run 'const list'"):
            result = runner.invoke(main, ['const', 'list'])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains AU or Solar"):
            assert 'AU' in result.output or 'Solar' in result.output

    @allure.title("const search finds matching constants")
    def test_const_search(self, runner):
        """const search finds matching constants."""
        with allure.step("Run 'const search solar'"):
            result = runner.invoke(main, ['const', 'search', 'solar'])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  SUN COMMANDS (v0.2)
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Sun Commands")
class TestSunCommands:
    """Tests for Sun-related CLI commands."""

    @allure.title("sun position displays solar coordinates")
    def test_sun_position(self, runner):
        """sun position displays solar coordinates."""
        with allure.step("Run 'sun position'"):
            result = runner.invoke(main, ['sun', 'position'])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0

    @allure.title("sun rise calculates sunrise")
    def test_sun_rise(self, runner):
        """sun rise calculates sunrise."""
        with allure.step("Run 'sun rise' for Greenwich"):
            result = runner.invoke(main, [
                'sun', 'rise',
                '--lat', '51.5',
                '--lon', '0.0'
            ])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0

    @allure.title("sun set calculates sunset")
    def test_sun_set(self, runner):
        """sun set calculates sunset."""
        with allure.step("Run 'sun set' for Greenwich"):
            result = runner.invoke(main, [
                'sun', 'set',
                '--lat', '51.5',
                '--lon', '0.0'
            ])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  MOON COMMANDS (v0.2)
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Moon Commands")
class TestMoonCommands:
    """Tests for Moon-related CLI commands."""

    @allure.title("moon position displays lunar coordinates")
    def test_moon_position(self, runner):
        """moon position displays lunar coordinates."""
        with allure.step("Run 'moon position'"):
            result = runner.invoke(main, ['moon', 'position'])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0

    @allure.title("moon phase displays current phase")
    def test_moon_phase(self, runner):
        """moon phase displays current phase."""
        with allure.step("Run 'moon phase'"):
            result = runner.invoke(main, ['moon', 'phase'])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0

    @allure.title("moon next finds next phase")
    def test_moon_next(self, runner):
        """moon next finds next phase."""
        with allure.step("Run 'moon next full'"):
            result = runner.invoke(main, ['moon', 'next', 'full'])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  OBSERVER COMMANDS (v0.2)
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Observer Commands")
class TestObserverCommands:
    """Tests for observer management CLI commands."""

    @allure.title("observer list shows saved observers")
    def test_observer_list(self, runner):
        """observer list shows saved observers."""
        with allure.step("Run 'observer list'"):
            result = runner.invoke(main, ['observer', 'list'])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  VISIBILITY COMMANDS (v0.2)
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Visibility Commands")
class TestVisibilityCommands:
    """Tests for visibility-related CLI commands."""

    @allure.title("vis altitude calculates target altitude")
    def test_vis_altitude(self, runner):
        """vis altitude calculates target altitude."""
        with allure.step("Run 'vis altitude' for target"):
            result = runner.invoke(main, [
                'vis', 'altitude',
                '12h00m00s +45d00m00s',
                '--lat', '51.5',
                '--lon', '0.0'
            ])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0

    @allure.title("vis airmass calculates airmass")
    def test_vis_airmass(self, runner):
        """vis airmass calculates airmass."""
        with allure.step("Run 'vis airmass 45.0'"):
            result = runner.invoke(main, [
                'vis', 'airmass',
                '45.0'
            ])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  OUTPUT FORMAT OPTIONS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Output Formats")
class TestOutputFormats:
    """Tests for output format options."""

    @allure.title("--json outputs JSON format")
    def test_json_output(self, runner):
        """--json outputs JSON format."""
        with allure.step("Run '--json time now'"):
            result = runner.invoke(main, ['--json', 'time', 'now'])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output is JSON"):
            assert '{' in result.output

    @allure.title("--verbose shows calculation steps")
    def test_verbose_output(self, runner):
        """--verbose shows calculation steps."""
        with allure.step("Run '--verbose angle sep'"):
            result = runner.invoke(main, ['--verbose', 'angle', 'sep',
                '10h00m00s +20d00m00s',
                '10h10m00s +21d00m00s'
            ])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0

    @allure.title("--precision compact shows fewer decimals")
    def test_precision_compact(self, runner):
        """--precision compact shows fewer decimals."""
        with allure.step("Run '-p compact time now'"):
            result = runner.invoke(main, ['-p', 'compact', 'time', 'now'])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output has decimal numbers"):
            assert result.output.count('.') > 0

    @allure.title("--precision full shows maximum decimals")
    def test_precision_full(self, runner):
        """--precision full shows maximum decimals."""
        with allure.step("Run '-p full time now'"):
            result = runner.invoke(main, ['-p', 'full', 'time', 'now'])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output has decimal numbers"):
            assert result.output.count('.') > 0

    @allure.title("All precision levels are valid")
    def test_precision_options(self, runner):
        """All precision levels are valid."""
        for level in ['compact', 'display', 'standard', 'high', 'full']:
            with allure.step(f"Run '--precision {level}'"):
                result = runner.invoke(main, ['--precision', level, 'time', 'now'])
            with allure.step(f"Precision {level}: exit code = {result.exit_code}"):
                assert result.exit_code == 0, f"Precision {level} failed"


# ═══════════════════════════════════════════════════════════════════════════════
#  COMMAND ALIASES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Command Aliases")
class TestCommandAliases:
    """Tests for command shorthand aliases."""

    @allure.title("'t' is alias for 'time'")
    def test_t_alias_for_time(self, runner):
        """'t' is alias for 'time'."""
        with allure.step("Run 't now'"):
            result = runner.invoke(main, ['t', 'now'])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0

    @allure.title("'a' is alias for 'angle'")
    def test_a_alias_for_angle(self, runner):
        """'a' is alias for 'angle'."""
        with allure.step("Run 'a convert 45'"):
            result = runner.invoke(main, ['a', 'convert', '45'])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0

    @allure.title("'c' is alias for 'coord'")
    def test_c_alias_for_coord(self, runner):
        """'c' is alias for 'coord'."""
        with allure.step("Run 'c parse 12h00m +45d'"):
            result = runner.invoke(main, ['c', 'parse', '12h00m +45d'])
        with allure.step(f"Exit code = {result.exit_code}"):
            assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  ERROR HANDLING
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Error Handling")
class TestErrorHandling:
    """Tests for CLI error handling."""

    @allure.title("Invalid angle input shows error")
    def test_invalid_angle(self, runner):
        """Invalid angle input shows error."""
        with allure.step("Run 'angle convert not_an_angle'"):
            result = runner.invoke(main, ['angle', 'convert', 'not_an_angle'])
        with allure.step(f"Exit code = {result.exit_code} or error in output"):
            assert result.exit_code != 0 or 'error' in result.output.lower()

    @allure.title("Unknown command shows error")
    def test_unknown_command(self, runner):
        """Unknown command shows error."""
        with allure.step("Run 'nonexistent'"):
            result = runner.invoke(main, ['nonexistent'])
        with allure.step(f"Exit code = {result.exit_code} (non-zero)"):
            assert result.exit_code != 0

    @allure.title("Missing argument shows error")
    def test_missing_argument(self, runner):
        """Missing required argument shows error."""
        with allure.step("Run 'angle sep' with only one coord"):
            result = runner.invoke(main, ['angle', 'sep', '10h00m00s'])
        with allure.step(f"Exit code = {result.exit_code} (non-zero)"):
            assert result.exit_code != 0
