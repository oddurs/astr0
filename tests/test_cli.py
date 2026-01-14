"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                              CLI TESTS                                       ║
║                                                                              ║
║  Integration tests for the starward command-line interface.                  ║
║                                                                              ║
║  The CLI provides astronomers and students with quick access to              ║
║  astronomical calculations without writing code. It supports:                ║
║                                                                              ║
║  • Time calculations (Julian Date, sidereal time, conversions)               ║
║  • Coordinate parsing and transformations                                    ║
║  • Angular calculations (separation, position angle)                         ║
║  • Physical constants lookup                                                 ║
║                                                                              ║
║  Output formats include human-readable tables and JSON for scripting.        ║
║  Verbose mode shows calculation steps for educational purposes.              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import json
import allure
import pytest
from click.testing import CliRunner

from starward import __version__
from starward.cli import main


@pytest.fixture
def runner():
    """Create a CLI test runner for invoking commands."""
    return CliRunner()


# ═══════════════════════════════════════════════════════════════════════════════
#  CLI BASICS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("CLI Basics")
class TestCLIBasics:
    """
    Tests for basic CLI functionality and command structure.

    A well-designed CLI should:
    - Provide clear help documentation
    - Display version information
    - Follow Unix conventions for flags and arguments
    - Return appropriate exit codes
    """

    @allure.title("--help shows usage")
    def test_help(self, runner):
        """
        Verify --help displays usage information.

        The help output should explain available commands and options,
        following the convention that --help always succeeds (exit 0).
        """
        with allure.step("Run 'starward --help'"):
            result = runner.invoke(main, ['--help'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains 'starward'"):
            assert 'starward' in result.output.lower()

    @allure.title("--version shows version")
    def test_version(self, runner):
        """
        Verify --version displays the current version.

        Version information is essential for bug reports and ensuring
        users have compatible software versions.
        """
        with allure.step("Run 'starward --version'"):
            result = runner.invoke(main, ['--version'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step(f"Version: {__version__}"):
            assert __version__ in result.output

    @allure.title("about command shows info")
    def test_about(self, runner):
        """
        Verify the about command displays project information.

        The about command provides context about the tool's purpose
        and capabilities for new users.
        """
        with allure.step("Run 'starward about'"):
            result = runner.invoke(main, ['about'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output mentions astronomy"):
            assert 'Astronomy' in result.output or 'astronomy' in result.output.lower()


# ═══════════════════════════════════════════════════════════════════════════════
#  TIME COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Time Commands")
class TestTimeCommands:
    """
    Tests for time-related CLI commands.

    Astronomical time systems are complex but essential:

    - Julian Date (JD): Continuous day count since 4713 BCE
    - Modified Julian Date (MJD): JD - 2400000.5 (more manageable numbers)
    - Sidereal Time: Time measured by stellar positions, not the Sun
    - UTC: Coordinated Universal Time, the civil time standard

    The CLI makes these conversions accessible without calculation.
    """

    @allure.title("time now shows Julian Date")
    def test_time_now(self, runner):
        """
        Verify 'time now' displays the current Julian Date.

        The Julian Date is the standard time system in astronomy because
        it provides a continuous count without calendar irregularities.
        """
        with allure.step("Run 'starward time now'"):
            result = runner.invoke(main, ['time', 'now'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains Julian Date"):
            assert 'Julian Date' in result.output

    @allure.title("time now --json returns JSON")
    def test_time_now_json(self, runner):
        """
        Verify JSON output format for scripting integration.

        JSON output enables pipeline integration with other tools and
        programmatic processing of astronomical data.
        """
        with allure.step("Run 'starward -o json time now'"):
            result = runner.invoke(main, ['-o', 'json', 'time', 'now'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Parse JSON output"):
            data = json.loads(result.output)
        with allure.step(f"julian_date: {data.get('julian_date')}"):
            assert 'julian_date' in data
            assert 'utc' in data

    @allure.title("time convert converts JD to date")
    def test_time_convert(self, runner):
        """
        Verify Julian Date to calendar date conversion.

        JD 2451545.0 is the J2000.0 epoch (2000-01-01 12:00:00 UTC),
        a fundamental reference point in modern astronomy.
        """
        with allure.step("Run 'starward time convert 2451545.0'"):
            result = runner.invoke(main, ['time', 'convert', '2451545.0'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains 2000 (J2000.0)"):
            assert '2000' in result.output

    @allure.title("time jd converts date to JD")
    def test_time_jd(self, runner):
        """
        Verify calendar date to Julian Date conversion.

        Converting 2000-01-01 12:00:00 should yield JD 2451545.0,
        the standard J2000.0 epoch used as the reference for modern
        star catalogs and ephemerides.
        """
        with allure.step("Run 'starward time jd 2000 1 1 12 0 0'"):
            result = runner.invoke(main, ['time', 'jd', '2000', '1', '1', '12', '0', '0'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains 2451545 (J2000.0)"):
            assert '2451545' in result.output

    @allure.title("time lst shows Local Sidereal Time")
    def test_time_lst(self, runner):
        """
        Verify Local Sidereal Time calculation.

        LST is the Right Ascension currently on the meridian. Objects
        with RA equal to LST are at their highest altitude - the optimal
        time for observation.
        """
        with allure.step("Run 'starward time lst 0'"):
            result = runner.invoke(main, ['time', 'lst', '0'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains LST"):
            assert 'LST' in result.output

    @allure.title("'t' alias works for 'time'")
    def test_time_alias(self, runner):
        """
        Verify command alias for faster typing.

        Short aliases like 't' for 'time' improve usability for
        frequent command-line users.
        """
        with allure.step("Run 'starward t now'"):
            result = runner.invoke(main, ['t', 'now'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  COORDINATE COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Coords Commands")
class TestCoordsCommands:
    """
    Tests for coordinate parsing and transformation commands.

    Celestial coordinates come in several systems:

    - ICRS/Equatorial: Right Ascension and Declination (RA/Dec)
    - Galactic: Longitude and latitude relative to the Milky Way
    - Horizontal: Altitude and azimuth from observer's position

    The CLI handles parsing various input formats and transforming
    between coordinate systems, essential for observation planning.
    """

    @allure.title("coords parse parses coordinates")
    def test_coords_parse(self, runner):
        """
        Verify coordinate string parsing.

        The parser accepts multiple formats: HMS/DMS, decimal degrees,
        colon-separated, and space-separated notation.
        """
        with allure.step("Run 'starward coords parse 12h30m00s +45d30m00s'"):
            result = runner.invoke(main, ['coords', 'parse', '12h30m00s +45d30m00s'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains RA and Dec"):
            assert 'Right Ascension' in result.output
            assert 'Declination' in result.output

    @allure.title("coords transform to galactic")
    def test_coords_transform_galactic(self, runner):
        """
        Verify ICRS to Galactic coordinate transformation.

        Galactic coordinates are useful for studying the structure
        of the Milky Way, with the galactic center at l=0°, b=0°.
        """
        with allure.step("Run 'starward coords transform 12h30m +45d --to galactic'"):
            result = runner.invoke(main, ['coords', 'transform', '12h30m +45d', '--to', 'galactic'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains Galactic"):
            assert 'Galactic' in result.output

    @allure.title("coords transform to altaz requires location")
    def test_coords_transform_altaz_requires_location(self, runner):
        """
        Verify that alt-az transformation requires observer location.

        Horizontal coordinates (altitude/azimuth) are observer-specific
        and require knowing the observer's latitude and longitude.
        """
        with allure.step("Run 'starward coords transform 12h +45d --to altaz' (no location)"):
            result = runner.invoke(main, ['coords', 'transform', '12h +45d', '--to', 'altaz'])
        with allure.step(f"Exit code: {result.exit_code} (non-zero expected)"):
            assert result.exit_code != 0
        with allure.step("Error mentions lat/lon"):
            assert 'lat' in result.output.lower() or 'lon' in result.output.lower()

    @allure.title("coords transform to altaz with location")
    def test_coords_transform_altaz(self, runner):
        """
        Verify horizontal coordinate transformation with location.

        Given observer coordinates (lat=40°N, lon=75°W), the command
        computes the target's altitude above the horizon and azimuth
        (compass direction) at the current time.
        """
        with allure.step("Run 'starward coords transform 12h +45d --to altaz --lat 40 --lon -75'"):
            result = runner.invoke(main, [
                'coords', 'transform', '12h +45d',
                '--to', 'altaz',
                '--lat', '40',
                '--lon', '-75'
            ])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains Alt"):
            assert 'Alt' in result.output

    @allure.title("coords parse --json returns JSON")
    def test_coords_json(self, runner):
        """
        Verify JSON output for coordinate data.

        JSON format enables easy integration with other software
        and web applications.
        """
        with allure.step("Run 'starward -o json coords parse 12h +45d'"):
            result = runner.invoke(main, ['-o', 'json', 'coords', 'parse', '12h +45d'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Parse JSON output"):
            data = json.loads(result.output)
        with allure.step(f"ra: {data.get('ra')}, dec: {data.get('dec')}"):
            assert 'ra' in data
            assert 'dec' in data

    @allure.title("'c' alias works for 'coords'")
    def test_coords_alias(self, runner):
        """
        Verify short alias for coords command.

        The 'c' alias provides quick access to the frequently-used
        coordinate commands.
        """
        with allure.step("Run 'starward c parse 12h +45d'"):
            result = runner.invoke(main, ['c', 'parse', '12h +45d'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  ANGLE COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Angles Commands")
class TestAnglesCommands:
    """
    Tests for angle calculation commands.

    Angular calculations are fundamental to observational astronomy:

    - Separation: Angular distance between two objects
    - Position Angle: Direction from one object to another
    - Conversions: Between degrees, radians, HMS, and DMS

    These calculations answer practical questions like "Will both
    objects fit in my telescope's field of view?"
    """

    @allure.title("angles sep calculates separation")
    def test_angles_sep(self, runner):
        """
        Verify angular separation calculation.

        Separation is the great-circle distance between two points
        on the celestial sphere, essential for planning observations.
        """
        with allure.step("Run 'starward angles sep 12h +45d 12h30m +46d'"):
            result = runner.invoke(main, ['angles', 'sep', '12h +45d', '12h30m +46d'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains Separation"):
            assert 'Separation' in result.output

    @allure.title("angles pa calculates position angle")
    def test_angles_pa(self, runner):
        """
        Verify position angle calculation.

        Position angle indicates the direction from one object to
        another, measured from north through east. Essential for
        binary star observations and instrument alignment.
        """
        with allure.step("Run 'starward angles pa 12h +45d 12h30m +46d'"):
            result = runner.invoke(main, ['angles', 'pa', '12h +45d', '12h30m +46d'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains Position Angle"):
            assert 'Position Angle' in result.output

    @allure.title("angles convert converts degrees")
    def test_angles_convert(self, runner):
        """
        Verify angle unit conversion.

        Converts between degrees, radians, and sexagesimal formats,
        helping translate between different data sources.
        """
        with allure.step("Run 'starward angles convert 45.5'"):
            result = runner.invoke(main, ['angles', 'convert', '45.5'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains Degrees and Radians"):
            assert 'Degrees' in result.output
            assert 'Radians' in result.output

    @allure.title("angles convert from radians")
    def test_angles_convert_radians(self, runner):
        """
        Verify conversion from radian input.

        π/2 radians ≈ 1.5708 rad = 90°, demonstrating radian-to-degree
        conversion useful for working with mathematical software output.
        """
        with allure.step("Run 'starward angles convert 1.5708 --unit rad'"):
            result = runner.invoke(main, ['angles', 'convert', '1.5708', '--unit', 'rad'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains ~90° (π/2 rad)"):
            assert '90' in result.output

    @allure.title("angles convert --json returns JSON")
    def test_angles_json(self, runner):
        """
        Verify JSON output for angle conversions.

        JSON format provides all representations simultaneously for
        programmatic use.
        """
        with allure.step("Run 'starward -o json angles convert 45'"):
            result = runner.invoke(main, ['-o', 'json', 'angles', 'convert', '45'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Parse JSON output"):
            data = json.loads(result.output)
        with allure.step(f"degrees: {data.get('degrees')}, radians: {data.get('radians')}"):
            assert 'degrees' in data
            assert 'radians' in data

    @allure.title("'a' alias works for 'angles'")
    def test_angles_alias(self, runner):
        """
        Verify short alias for angles command.

        The 'a' alias enables quick angle calculations from the
        command line.
        """
        with allure.step("Run 'starward a convert 45'"):
            result = runner.invoke(main, ['a', 'convert', '45'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  CONSTANTS COMMANDS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Constants Commands")
class TestConstantsCommands:
    """
    Tests for astronomical constants lookup commands.

    Physical constants are fundamental to astronomical calculations:

    - c: Speed of light (299,792,458 m/s exactly)
    - AU: Astronomical Unit (Earth-Sun distance)
    - G: Gravitational constant
    - Solar/planetary parameters

    Having accurate, well-documented constants prevents errors
    from using outdated or incorrect values.
    """

    @allure.title("constants list shows all constants")
    def test_constants_list(self, runner):
        """
        Verify listing all available constants.

        The list provides an overview of what's available, with
        names, values, and units.
        """
        with allure.step("Run 'starward constants list'"):
            result = runner.invoke(main, ['constants', 'list'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains Speed of light"):
            assert 'Speed of light' in result.output

    @allure.title("constants search finds matches")
    def test_constants_search(self, runner):
        """
        Verify searching for constants by keyword.

        Search helps find relevant constants without knowing exact
        names, supporting partial matches and synonyms.
        """
        with allure.step("Run 'starward constants search solar'"):
            result = runner.invoke(main, ['constants', 'search', 'solar'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains Solar"):
            assert 'Solar' in result.output

    @allure.title("constants show displays constant")
    def test_constants_show(self, runner):
        """
        Verify displaying a specific constant's details.

        Shows the value, unit, uncertainty, and description for
        a named constant.
        """
        with allure.step("Run 'starward constants show AU'"):
            result = runner.invoke(main, ['constants', 'show', 'AU'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains Astronomical Unit"):
            assert 'Astronomical Unit' in result.output

    @allure.title("constants show --json returns JSON")
    def test_constants_json(self, runner):
        """
        Verify JSON output for constant values.

        JSON format provides the value in a machine-readable form
        for use in calculations and scripts.
        """
        with allure.step("Run 'starward -o json constants show AU'"):
            result = runner.invoke(main, ['-o', 'json', 'constants', 'show', 'AU'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Parse JSON output"):
            data = json.loads(result.output)
        with allure.step(f"value: {data.get('value')}"):
            assert 'value' in data

    @allure.title("'const' alias works for 'constants'")
    def test_constants_alias(self, runner):
        """
        Verify short alias for constants command.

        The 'const' alias provides quicker access to constant lookups.
        """
        with allure.step("Run 'starward const list'"):
            result = runner.invoke(main, ['const', 'list'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0


# ═══════════════════════════════════════════════════════════════════════════════
#  VERBOSE MODE
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Verbose Mode")
class TestVerboseMode:
    """
    Tests for verbose output mode.

    Verbose mode shows calculation steps, which serves two purposes:

    1. Educational: Students can see how calculations are performed
    2. Debugging: Users can verify intermediate values are correct

    This transparency is especially valuable in an educational tool,
    helping users understand rather than just use the calculations.
    """

    @allure.title("--verbose time now shows steps")
    def test_verbose_time(self, runner):
        """
        Verify verbose output for time calculations.

        Verbose mode reveals the steps in Julian Date calculation,
        including century calculations and component breakdowns.
        """
        with allure.step("Run 'starward --verbose time now'"):
            result = runner.invoke(main, ['--verbose', 'time', 'now'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains box drawing (verbose indicator)"):
            # Box drawing characters indicate formatted verbose output
            assert '─' in result.output

    @allure.title("--verbose coords transform shows steps")
    def test_verbose_coords(self, runner):
        """
        Verify verbose output for coordinate transformations.

        Shows the rotation matrices and intermediate coordinates
        during ICRS to Galactic transformation.
        """
        with allure.step("Run 'starward --verbose coords transform 12h +45d --to galactic'"):
            result = runner.invoke(main, ['--verbose', 'coords', 'transform', '12h +45d', '--to', 'galactic'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains box drawing (verbose indicator)"):
            assert '─' in result.output

    @allure.title("--verbose angles sep shows steps")
    def test_verbose_angles(self, runner):
        """
        Verify verbose output for angular separation.

        Shows the spherical trigonometry steps used to compute
        the great-circle distance between two points.
        """
        with allure.step("Run 'starward --verbose angles sep 12h +45d 13h +46d'"):
            result = runner.invoke(main, ['--verbose', 'angles', 'sep', '12h +45d', '13h +46d'])
        with allure.step(f"Exit code: {result.exit_code}"):
            assert result.exit_code == 0
        with allure.step("Output contains box drawing (verbose indicator)"):
            assert '─' in result.output
