"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                            OBSERVER TESTS                                    ║
║                                                                              ║
║  Tests for observer location management and geographic calculations.         ║
║  Where we stand shapes everything we see in the sky.                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import allure
import pytest

from starward.core.observer import Observer


# ═══════════════════════════════════════════════════════════════════════════════
#  OBSERVER CREATION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Observer Creation")
class TestObserverCreation:
    """Tests for creating Observer instances."""

    @allure.title("Create observer from decimal degrees")
    def test_from_degrees(self):
        """Create observer from decimal degrees."""
        with allure.step("Create Greenwich observer"):
            obs = Observer.from_degrees("Test", 51.4772, -0.0005, elevation=62.0)
        with allure.step(f"Name = {obs.name}"):
            assert obs.name == "Test"
        with allure.step(f"Lat = {obs.lat_deg:.4f}°"):
            assert obs.lat_deg == pytest.approx(51.4772, rel=1e-6)
        with allure.step(f"Lon = {obs.lon_deg:.4f}°"):
            assert obs.lon_deg == pytest.approx(-0.0005, rel=1e-6)
        with allure.step(f"Elevation = {obs.elevation}m"):
            assert obs.elevation == 62.0

    @allure.title("Create observer with timezone")
    def test_with_timezone(self):
        """Create observer with timezone."""
        with allure.step("Create LA observer with timezone"):
            obs = Observer.from_degrees(
                "LA", 34.05, -118.25,
                timezone="America/Los_Angeles"
            )
        with allure.step(f"Timezone = {obs.timezone}"):
            assert obs.timezone == "America/Los_Angeles"

    @allure.title("Default elevation is 0")
    def test_default_elevation(self):
        """Default elevation is 0."""
        with allure.step("Create observer without elevation"):
            obs = Observer.from_degrees("Test", 45.0, 0.0)
        with allure.step(f"Elevation = {obs.elevation}"):
            assert obs.elevation == 0.0

    @allure.title("High elevation observatories")
    def test_high_elevation(self):
        """High elevation observatories."""
        with allure.step("Create Mauna Kea observer"):
            obs = Observer.from_degrees("Mauna Kea", 19.82, -155.47, elevation=4207.0)
        with allure.step(f"Elevation = {obs.elevation}m"):
            assert obs.elevation == 4207.0


# ═══════════════════════════════════════════════════════════════════════════════
#  LATITUDE VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Latitude Validation")
class TestLatitudeValidation:
    """Tests for latitude bounds checking."""

    @allure.title("Latitude +90° is valid")
    def test_north_pole(self):
        """Latitude +90° is valid."""
        with allure.step("Create North Pole observer"):
            obs = Observer.from_degrees("North Pole", 90.0, 0.0)
        with allure.step(f"Lat = {obs.lat_deg}°"):
            assert obs.lat_deg == 90.0

    @allure.title("Latitude -90° is valid")
    def test_south_pole(self):
        """Latitude -90° is valid."""
        with allure.step("Create South Pole observer"):
            obs = Observer.from_degrees("South Pole", -90.0, 0.0)
        with allure.step(f"Lat = {obs.lat_deg}°"):
            assert obs.lat_deg == -90.0

    @allure.title("Latitude 0° is valid")
    def test_equator(self):
        """Latitude 0° is valid."""
        with allure.step("Create Equator observer"):
            obs = Observer.from_degrees("Equator", 0.0, 0.0)
        with allure.step(f"Lat = {obs.lat_deg}°"):
            assert obs.lat_deg == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
#  LONGITUDE HANDLING
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Longitude Handling")
class TestLongitudeHandling:
    """Tests for longitude storage and normalization."""

    @allure.title("Positive longitude = East")
    def test_positive_longitude_east(self):
        """Positive longitude = East."""
        with allure.step("Create Tokyo observer"):
            obs = Observer.from_degrees("Tokyo", 35.68, 139.77)
        with allure.step(f"Lon = {obs.lon_deg}° (East)"):
            assert obs.lon_deg == pytest.approx(139.77)

    @allure.title("Negative longitude = West")
    def test_negative_longitude_west(self):
        """Negative longitude = West."""
        with allure.step("Create NYC observer"):
            obs = Observer.from_degrees("NYC", 40.71, -74.01)
        with allure.step(f"Lon = {obs.lon_deg}° (West)"):
            assert obs.lon_deg == pytest.approx(-74.01)

    @allure.title("Longitude is stored without normalization")
    def test_longitude_stored_as_is(self):
        """Longitude is stored without normalization."""
        with allure.step("Create observer with lon=361°"):
            obs = Observer.from_degrees("Test", 0.0, 361.0)
        with allure.step(f"Lon = {obs.lon_deg}° (stored as-is)"):
            assert obs.lon_deg == 361.0


# ═══════════════════════════════════════════════════════════════════════════════
#  STRING REPRESENTATION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("String Representation")
class TestObserverString:
    """Tests for Observer string representation."""

    @allure.title("__str__ includes name")
    def test_str_includes_name(self):
        """__str__ includes name."""
        with allure.step("Create Greenwich observer"):
            obs = Observer.from_degrees("Greenwich", 51.4772, 0.0, elevation=62.0)
        with allure.step(f"str(obs) contains 'Greenwich'"):
            assert "Greenwich" in str(obs)

    @allure.title("__str__ includes coordinates")
    def test_str_includes_coordinates(self):
        """__str__ includes coordinates."""
        with allure.step("Create observer"):
            obs = Observer.from_degrees("Test", 51.4772, 0.0)
        s = str(obs)
        with allure.step(f"str contains coordinates: {s[:50]}"):
            assert "51.4772" in s or "51.48" in s

    @allure.title("__repr__ is informative")
    def test_repr(self):
        """__repr__ is informative."""
        with allure.step("Create observer"):
            obs = Observer.from_degrees("Test", 45.0, -90.0)
        r = repr(obs)
        with allure.step(f"repr = {r[:50]}"):
            assert "Observer" in r or "Test" in r


# ═══════════════════════════════════════════════════════════════════════════════
#  SERIALIZATION
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Serialization")
class TestObserverSerialization:
    """Tests for Observer serialization to dict/TOML."""

    @allure.title("Observer converts to dictionary")
    def test_to_dict(self):
        """Observer converts to dictionary."""
        with allure.step("Create observer"):
            obs = Observer.from_degrees("Test", 34.05, -118.25, timezone="America/Los_Angeles")
        with allure.step("Convert to dict"):
            d = obs.to_dict()
        with allure.step(f"dict has expected fields"):
            assert d['name'] == "Test"
            assert d['latitude'] == pytest.approx(34.05)
            assert d['longitude'] == pytest.approx(-118.25)

    @allure.title("to_dict includes elevation")
    def test_to_dict_includes_elevation(self):
        """to_dict includes elevation."""
        with allure.step("Create observer with elevation"):
            obs = Observer.from_degrees("Test", 0.0, 0.0, elevation=100.0)
        d = obs.to_dict()
        with allure.step(f"elevation = {d.get('elevation')}"):
            assert d.get('elevation') == 100.0

    @allure.title("to_dict includes timezone if set")
    def test_to_dict_includes_timezone(self):
        """to_dict includes timezone if set."""
        with allure.step("Create observer with timezone"):
            obs = Observer.from_degrees("Test", 0.0, 0.0, timezone="UTC")
        d = obs.to_dict()
        with allure.step(f"timezone = {d.get('timezone')}"):
            assert 'timezone' in d or d.get('timezone') == 'UTC'


# ═══════════════════════════════════════════════════════════════════════════════
#  WELL-KNOWN LOCATIONS (FIXTURES)
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Well-Known Locations")
class TestKnownLocations:
    """Tests using well-known observatory locations."""

    @allure.title("Greenwich fixture is correctly defined")
    def test_greenwich_fixture(self, greenwich):
        """Greenwich fixture is correctly defined."""
        with allure.step(f"Name = {greenwich.name}"):
            assert greenwich.name == "Greenwich"
        with allure.step(f"Lat = {greenwich.lat_deg:.2f}° (51-52)"):
            assert 51 < greenwich.lat_deg < 52
        with allure.step(f"Lon = {greenwich.lon_deg:.4f}° (-1 to 1)"):
            assert -1 < greenwich.lon_deg < 1

    @allure.title("Mauna Kea fixture is correctly defined")
    def test_mauna_kea_fixture(self, mauna_kea):
        """Mauna Kea fixture is correctly defined."""
        with allure.step(f"Name = {mauna_kea.name}"):
            assert mauna_kea.name == "Mauna Kea"
        with allure.step(f"Elevation = {mauna_kea.elevation}m (> 4000)"):
            assert mauna_kea.elevation > 4000

    @allure.title("Paranal fixture is correctly defined")
    def test_paranal_fixture(self, paranal):
        """Paranal (Chile) fixture is correctly defined."""
        with allure.step(f"Name = {paranal.name}"):
            assert paranal.name == "Paranal"
        with allure.step(f"Lat = {paranal.lat_deg:.2f}° (southern)"):
            assert paranal.lat_deg < 0

    @allure.title("North Pole fixture is at +90° latitude")
    def test_north_pole_fixture(self, north_pole):
        """North Pole fixture is at +90° latitude."""
        with allure.step(f"Lat = {north_pole.lat_deg}°"):
            assert north_pole.lat_deg == 90.0

    @allure.title("Equator fixture is at 0° latitude")
    def test_equator_fixture(self, equator):
        """Equator fixture is at 0° latitude."""
        with allure.step(f"Lat = {equator.lat_deg}°"):
            assert equator.lat_deg == 0.0


# ═══════════════════════════════════════════════════════════════════════════════
#  EDGE CASES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Edge Cases")
class TestObserverEdgeCases:
    """Tests for edge cases in observer handling."""

    @pytest.mark.edge
    @allure.title("Observer at +180° longitude")
    def test_date_line_east(self):
        """Observer at +180° longitude."""
        with allure.step("Create observer at date line east"):
            obs = Observer.from_degrees("Date Line E", 0.0, 180.0)
        with allure.step(f"Lon = {obs.lon_deg}°"):
            assert obs.lon_deg == 180.0

    @pytest.mark.edge
    @allure.title("Observer at -180° longitude")
    def test_date_line_west(self):
        """Observer at -180° longitude."""
        with allure.step("Create observer at date line west"):
            obs = Observer.from_degrees("Date Line W", 0.0, -180.0)
        with allure.step(f"Lon = {obs.lon_deg}°"):
            assert obs.lon_deg == -180.0

    @pytest.mark.edge
    @allure.title("Observer with empty name")
    def test_empty_name(self):
        """Observer with empty name."""
        with allure.step("Create observer with empty name"):
            obs = Observer.from_degrees("", 0.0, 0.0)
        with allure.step(f"Name = '{obs.name}'"):
            assert obs.name == ""

    @pytest.mark.edge
    @allure.title("Observer with Unicode name")
    def test_unicode_name(self):
        """Observer with Unicode name."""
        with allure.step("Create observer with Unicode name"):
            obs = Observer.from_degrees("東京 🔭", 35.68, 139.77)
        with allure.step(f"Name contains '東京'"):
            assert "東京" in obs.name
