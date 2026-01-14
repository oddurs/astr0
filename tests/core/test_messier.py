"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        MESSIER CATALOG TESTS                                 ║
║                                                                              ║
║  Tests for catalog lookups, searches, filtering, and coordinate             ║
║  calculations for the 110 Messier deep sky objects.                         ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import allure
import pytest

from starward.core.messier import (
    MESSIER,
    MessierCatalog,
    OBJECT_TYPES,
    messier_coords,
    messier_altitude,
    messier_transit_altitude,
)
from starward.core.messier_data import MessierObject, MESSIER_DATA
from starward.core.observer import Observer
from starward.core.time import JulianDate


# ═══════════════════════════════════════════════════════════════════════════════
#  CATALOG DATA
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Catalog Data")
class TestMessierData:
    """Tests for the Messier data completeness and accuracy."""

    @allure.title("Catalog has 110 objects")
    def test_catalog_has_110_objects(self):
        """Catalog contains all 110 Messier objects."""
        with allure.step(f"Catalog size = {len(MESSIER_DATA)}"):
            assert len(MESSIER_DATA) == 110

    @allure.title("All Messier numbers 1-110 present")
    def test_all_numbers_present(self):
        """All Messier numbers from 1 to 110 are present."""
        missing = []
        for i in range(1, 111):
            if i not in MESSIER_DATA:
                missing.append(i)
        with allure.step(f"Missing numbers: {missing if missing else 'None'}"):
            assert len(missing) == 0, f"Missing: {missing}"

    @allure.title("MessierObject is immutable")
    def test_messier_object_is_frozen(self):
        """MessierObject is immutable."""
        obj = MESSIER.get(1)
        with allure.step(f"Attempt to modify M{obj.number}"):
            with pytest.raises(AttributeError):
                obj.name = "Modified"

    @allure.title("All objects have required fields")
    def test_each_object_has_required_fields(self):
        """Each object has all required fields populated."""
        for obj in MESSIER.list_all():
            assert obj.number > 0
            assert obj.name
            assert obj.object_type in OBJECT_TYPES
            assert 0 <= obj.ra_hours < 24
            assert -90 <= obj.dec_degrees <= 90
            assert obj.magnitude > 0
            assert obj.size_arcmin > 0
            assert obj.constellation


# ═══════════════════════════════════════════════════════════════════════════════
#  CATALOG CLASS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Catalog Class")
class TestMessierCatalog:
    """Tests for the MessierCatalog class."""

    @allure.title("MESSIER is singleton instance")
    def test_singleton_instance(self):
        """MESSIER is the singleton catalog instance."""
        with allure.step(f"Type = {type(MESSIER).__name__}"):
            assert isinstance(MESSIER, MessierCatalog)

    @allure.title("get() returns correct object")
    def test_get_returns_correct_object(self):
        """get() returns the correct Messier object."""
        with allure.step("Get M31"):
            m31 = MESSIER.get(31)
        with allure.step(f"M31 = {m31.name}"):
            assert m31.number == 31
            assert "Andromeda" in m31.name

    @allure.title("get() raises KeyError for invalid number")
    def test_get_invalid_number_raises(self):
        """get() raises KeyError for number not in catalog."""
        with allure.step("Get M111 (does not exist)"):
            with pytest.raises(KeyError):
                MESSIER.get(111)
        with allure.step("Get M999 (does not exist)"):
            with pytest.raises(KeyError):
                MESSIER.get(999)

    @allure.title("get(0) raises ValueError")
    def test_get_zero_raises_value_error(self):
        """get() raises ValueError for zero."""
        with allure.step("Get M0"):
            with pytest.raises(ValueError):
                MESSIER.get(0)

    @allure.title("get(-1) raises ValueError")
    def test_get_negative_raises_value_error(self):
        """get() raises ValueError for negative numbers."""
        with allure.step("Get M-1"):
            with pytest.raises(ValueError):
                MESSIER.get(-1)

    @allure.title("get() rejects non-integer input")
    def test_get_invalid_type_raises(self):
        """get() raises error for non-integer input."""
        with allure.step("Get 'not a number'"):
            with pytest.raises((ValueError, TypeError)):
                MESSIER.get("not a number")

    @allure.title("list_all() returns all 110 objects")
    def test_list_all_returns_all_objects(self):
        """list_all() returns all 110 objects."""
        objects = MESSIER.list_all()
        with allure.step(f"Count = {len(objects)}"):
            assert len(objects) == 110
            assert all(isinstance(o, MessierObject) for o in objects)

    @allure.title("list_all() sorted by number")
    def test_list_all_sorted_by_number(self):
        """list_all() returns objects sorted by number."""
        objects = MESSIER.list_all()
        numbers = [o.number for o in objects]
        with allure.step(f"First 5: M{numbers[0]}-M{numbers[4]}"):
            assert numbers == list(range(1, 111))

    @allure.title("len(MESSIER) = 110")
    def test_len_returns_110(self):
        """len(MESSIER) returns 110."""
        with allure.step(f"len = {len(MESSIER)}"):
            assert len(MESSIER) == 110

    @allure.title("Catalog is iterable")
    def test_iteration(self):
        """Catalog is iterable."""
        count = 0
        for obj in MESSIER:
            assert isinstance(obj, MessierObject)
            count += 1
        with allure.step(f"Iterated over {count} objects"):
            assert count == 110


# ═══════════════════════════════════════════════════════════════════════════════
#  SEARCH
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Search")
class TestMessierSearch:
    """Tests for searching the Messier catalog."""

    @allure.title("Search by name: 'Andromeda'")
    def test_search_by_name(self):
        """Search finds objects by name."""
        with allure.step("Search 'Andromeda'"):
            results = MESSIER.search("Andromeda")
        with allure.step(f"Found {len(results)} result(s)"):
            assert len(results) >= 1
            assert any(o.number == 31 for o in results)

    @allure.title("Search by type: 'galaxy'")
    def test_search_by_type(self):
        """Search finds objects by type."""
        with allure.step("Search 'galaxy'"):
            results = MESSIER.search("galaxy")
        with allure.step(f"Found {len(results)} galaxies"):
            assert len(results) > 30

    @allure.title("Search by constellation: 'Sgr'")
    def test_search_by_constellation(self):
        """Search finds objects by constellation."""
        with allure.step("Search 'Sgr'"):
            results = MESSIER.search("Sgr")
        with allure.step(f"Found {len(results)} in Sagittarius"):
            assert len(results) > 5

    @allure.title("Search is case-insensitive")
    def test_search_case_insensitive(self):
        """Search is case-insensitive."""
        results1 = MESSIER.search("ORION")
        results2 = MESSIER.search("orion")
        results3 = MESSIER.search("Orion")
        with allure.step(f"ORION={len(results1)}, orion={len(results2)}, Orion={len(results3)}"):
            assert len(results1) == len(results2) == len(results3)

    @allure.title("Search by NGC: 'NGC 224'")
    def test_search_by_ngc(self):
        """Search finds objects by NGC designation."""
        with allure.step("Search 'NGC 224'"):
            results = MESSIER.search("NGC 224")
        with allure.step(f"Found M31 = {any(o.number == 31 for o in results)}"):
            assert len(results) >= 1
            assert any(o.number == 31 for o in results)

    @allure.title("Search returns empty for no match")
    def test_search_no_match(self):
        """Search returns empty list for no matches."""
        with allure.step("Search 'xyznonexistent'"):
            results = MESSIER.search("xyznonexistent")
        with allure.step(f"Results = {len(results)}"):
            assert len(results) == 0

    @allure.title("Search results sorted by number")
    def test_search_results_sorted(self):
        """Search results are sorted by Messier number."""
        results = MESSIER.search("galaxy")
        numbers = [o.number for o in results]
        with allure.step(f"First 3: M{numbers[0]}, M{numbers[1]}, M{numbers[2]}"):
            assert numbers == sorted(numbers)


# ═══════════════════════════════════════════════════════════════════════════════
#  FILTERS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Filters")
class TestMessierFilters:
    """Tests for filtering Messier objects."""

    @allure.title("Filter by type: galaxy")
    def test_filter_by_type_galaxy(self):
        """filter_by_type finds all galaxies."""
        with allure.step("Filter by type 'galaxy'"):
            galaxies = MESSIER.filter_by_type("galaxy")
        with allure.step(f"Found {len(galaxies)} galaxies"):
            assert len(galaxies) > 30
            assert all(o.object_type == "galaxy" for o in galaxies)

    @allure.title("Filter by type: globular_cluster")
    def test_filter_by_type_globular(self):
        """filter_by_type finds globular clusters."""
        with allure.step("Filter by type 'globular_cluster'"):
            globulars = MESSIER.filter_by_type("globular_cluster")
        with allure.step(f"Found {len(globulars)} globulars (includes M13 = {any(o.number == 13 for o in globulars)})"):
            assert len(globulars) > 20
            assert any(o.number == 13 for o in globulars)

    @allure.title("Filter by type is case-insensitive")
    def test_filter_by_type_case_insensitive(self):
        """filter_by_type is case-insensitive."""
        results1 = MESSIER.filter_by_type("GALAXY")
        results2 = MESSIER.filter_by_type("galaxy")
        with allure.step(f"GALAXY={len(results1)}, galaxy={len(results2)}"):
            assert len(results1) == len(results2)

    @allure.title("Filter by constellation: Vir")
    def test_filter_by_constellation(self):
        """filter_by_constellation finds objects in constellation."""
        with allure.step("Filter by constellation 'Vir'"):
            virgo = MESSIER.filter_by_constellation("Vir")
        with allure.step(f"Found {len(virgo)} in Virgo"):
            assert len(virgo) > 10

    @allure.title("Filter by magnitude ≤ 5.0")
    def test_filter_by_magnitude(self):
        """filter_by_magnitude finds bright objects."""
        with allure.step("Filter by magnitude ≤ 5.0"):
            bright = MESSIER.filter_by_magnitude(5.0)
        with allure.step(f"Found {len(bright)} bright objects (includes M45 = {any(o.number == 45 for o in bright)})"):
            assert len(bright) > 5
            assert all(o.magnitude <= 5.0 for o in bright)
            assert any(o.number == 45 for o in bright)


# ═══════════════════════════════════════════════════════════════════════════════
#  WELL-KNOWN OBJECTS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Well-Known Objects")
class TestWellKnownObjects:
    """Tests for specific well-known Messier objects."""

    @pytest.mark.golden
    @allure.title("M1 - Crab Nebula")
    @allure.description("""
    Verifies M1 is the Crab Nebula supernova remnant in Taurus.
    The Crab is the remnant of the 1054 AD supernova.
    """)
    def test_m1_crab_nebula(self):
        """M1 is the Crab Nebula supernova remnant."""
        with allure.step("Get M1"):
            m1 = MESSIER.get(1)
        with allure.step(f"Name = {m1.name}"):
            assert "Crab" in m1.name
        with allure.step(f"Type = {m1.object_type}"):
            assert m1.object_type == "supernova_remnant"
        with allure.step(f"Constellation = {m1.constellation}"):
            assert m1.constellation == "Tau"

    @pytest.mark.golden
    @allure.title("M31 - Andromeda Galaxy")
    @allure.description("""
    Verifies M31 is the Andromeda Galaxy, our nearest large neighbor.
    Visible to naked eye at magnitude ~3.4.
    """)
    def test_m31_andromeda(self):
        """M31 is the Andromeda Galaxy."""
        with allure.step("Get M31"):
            m31 = MESSIER.get(31)
        with allure.step(f"Name = {m31.name}"):
            assert "Andromeda" in m31.name
        with allure.step(f"Type = {m31.object_type}"):
            assert m31.object_type == "galaxy"
        with allure.step(f"Constellation = {m31.constellation}"):
            assert m31.constellation == "And"
        with allure.step(f"Magnitude = {m31.magnitude:.1f} (expected 3.0-4.0)"):
            assert 3.0 < m31.magnitude < 4.0

    @pytest.mark.golden
    @allure.title("M42 - Orion Nebula")
    @allure.description("""
    Verifies M42 is the Orion Nebula, the famous emission nebula
    visible in Orion's sword.
    """)
    def test_m42_orion_nebula(self):
        """M42 is the Orion Nebula."""
        with allure.step("Get M42"):
            m42 = MESSIER.get(42)
        with allure.step(f"Name = {m42.name}"):
            assert "Orion" in m42.name
        with allure.step(f"Type = {m42.object_type}"):
            assert m42.object_type == "emission_nebula"
        with allure.step(f"Constellation = {m42.constellation}"):
            assert m42.constellation == "Ori"

    @pytest.mark.golden
    @allure.title("M45 - Pleiades")
    @allure.description("""
    Verifies M45 is the Pleiades (Seven Sisters), a very bright
    open cluster in Taurus visible to naked eye.
    """)
    def test_m45_pleiades(self):
        """M45 is the Pleiades open cluster."""
        with allure.step("Get M45"):
            m45 = MESSIER.get(45)
        with allure.step(f"Name = {m45.name}"):
            assert "Pleiades" in m45.name
        with allure.step(f"Type = {m45.object_type}"):
            assert m45.object_type == "open_cluster"
        with allure.step(f"Constellation = {m45.constellation}"):
            assert m45.constellation == "Tau"
        with allure.step(f"Magnitude = {m45.magnitude:.1f} (very bright, < 2.0)"):
            assert m45.magnitude < 2.0

    @pytest.mark.golden
    @allure.title("M57 - Ring Nebula")
    @allure.description("""
    Verifies M57 is the Ring Nebula in Lyra, a classic planetary nebula.
    """)
    def test_m57_ring_nebula(self):
        """M57 is the Ring Nebula."""
        with allure.step("Get M57"):
            m57 = MESSIER.get(57)
        with allure.step(f"Name = {m57.name}"):
            assert "Ring" in m57.name
        with allure.step(f"Type = {m57.object_type}"):
            assert m57.object_type == "planetary_nebula"
        with allure.step(f"Constellation = {m57.constellation}"):
            assert m57.constellation == "Lyr"

    @pytest.mark.golden
    @allure.title("M104 - Sombrero Galaxy")
    @allure.description("""
    Verifies M104 is the Sombrero Galaxy, named for its distinctive
    hat-like shape with prominent dust lane.
    """)
    def test_m104_sombrero(self):
        """M104 is the Sombrero Galaxy."""
        with allure.step("Get M104"):
            m104 = MESSIER.get(104)
        with allure.step(f"Name = {m104.name}"):
            assert "Sombrero" in m104.name
        with allure.step(f"Type = {m104.object_type}"):
            assert m104.object_type == "galaxy"


# ═══════════════════════════════════════════════════════════════════════════════
#  COORDINATES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Coordinates")
class TestMessierCoordinates:
    """Tests for Messier coordinate functions."""

    @allure.title("messier_coords returns ICRSCoord")
    def test_messier_coords_returns_icrs(self):
        """messier_coords returns ICRSCoord."""
        from starward.core.coords import ICRSCoord
        with allure.step("Get coords for M31"):
            coords = messier_coords(31)
        with allure.step(f"Type = {type(coords).__name__}"):
            assert isinstance(coords, ICRSCoord)

    @allure.title("M31 coordinates: RA ~00h42m, Dec ~+41°")
    def test_m31_coordinates(self):
        """M31 coordinates are approximately correct."""
        with allure.step("Get M31 coordinates"):
            coords = messier_coords(31)
        with allure.step(f"RA = {coords.ra.hours:.2f}h (expected 0.0-1.5)"):
            assert 0.0 < coords.ra.hours < 1.5
        with allure.step(f"Dec = {coords.dec.degrees:.1f}° (expected 40-43)"):
            assert 40.0 < coords.dec.degrees < 43.0

    @allure.title("M42 coordinates: RA ~05h35m, Dec ~-05°")
    def test_m42_coordinates(self):
        """M42 coordinates are approximately correct."""
        with allure.step("Get M42 coordinates"):
            coords = messier_coords(42)
        with allure.step(f"RA = {coords.ra.hours:.2f}h (expected 5.0-6.0)"):
            assert 5.0 < coords.ra.hours < 6.0
        with allure.step(f"Dec = {coords.dec.degrees:.1f}° (expected -6 to -4)"):
            assert -6.0 < coords.dec.degrees < -4.0


# ═══════════════════════════════════════════════════════════════════════════════
#  VISIBILITY
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Visibility")
class TestMessierVisibility:
    """Tests for Messier visibility calculations."""

    @pytest.fixture
    def greenwich(self):
        """Greenwich Observatory observer."""
        return Observer.from_degrees("Greenwich", 51.4772, -0.0005)

    @pytest.fixture
    def j2000(self):
        """J2000.0 epoch."""
        return JulianDate(2451545.0)

    @allure.title("messier_altitude returns Angle")
    def test_altitude_returns_angle(self):
        """messier_altitude returns an Angle."""
        from starward.core.angles import Angle
        observer = Observer.from_degrees("Test", 40.0, -74.0)
        jd = JulianDate(2451545.0)
        with allure.step("Calculate M31 altitude"):
            alt = messier_altitude(31, observer, jd)
        with allure.step(f"Type = {type(alt).__name__}, value = {alt.degrees:.1f}°"):
            assert isinstance(alt, Angle)

    @allure.title("M31 transit altitude from Greenwich ~80°")
    def test_transit_altitude_reasonable(self, greenwich):
        """Transit altitude is reasonable for location."""
        with allure.step("Calculate M31 transit altitude from Greenwich"):
            trans_alt = messier_transit_altitude(31, greenwich)
        with allure.step(f"Transit altitude = {trans_alt.degrees:.1f}° (expected 75-85)"):
            assert 75.0 < trans_alt.degrees < 85.0

    @allure.title("High-dec object transit altitude")
    def test_circumpolar_object_high_transit(self):
        """High declination objects have high transit altitude."""
        north_observer = Observer.from_degrees("North", 60.0, 0.0)
        with allure.step("Calculate M81 transit from lat 60°N"):
            trans_alt = messier_transit_altitude(81, north_observer)
        with allure.step(f"Transit altitude = {trans_alt.degrees:.1f}° (expected > 60)"):
            assert trans_alt.degrees > 60.0


# ═══════════════════════════════════════════════════════════════════════════════
#  OBJECT TYPE COVERAGE
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Object Type Coverage")
class TestObjectTypeCoverage:
    """Tests to ensure all object types are represented."""

    @allure.title("Catalog has galaxies")
    def test_has_galaxies(self):
        """Catalog contains galaxies."""
        galaxies = MESSIER.filter_by_type("galaxy")
        with allure.step(f"Galaxy count = {len(galaxies)}"):
            assert len(galaxies) > 0

    @allure.title("Catalog has globular clusters")
    def test_has_globular_clusters(self):
        """Catalog contains globular clusters."""
        clusters = MESSIER.filter_by_type("globular_cluster")
        with allure.step(f"Globular cluster count = {len(clusters)}"):
            assert len(clusters) > 0

    @allure.title("Catalog has open clusters")
    def test_has_open_clusters(self):
        """Catalog contains open clusters."""
        clusters = MESSIER.filter_by_type("open_cluster")
        with allure.step(f"Open cluster count = {len(clusters)}"):
            assert len(clusters) > 0

    @allure.title("Catalog has planetary nebulae")
    def test_has_planetary_nebulae(self):
        """Catalog contains planetary nebulae."""
        nebulae = MESSIER.filter_by_type("planetary_nebula")
        with allure.step(f"Planetary nebula count = {len(nebulae)}"):
            assert len(nebulae) > 0

    @allure.title("Catalog has emission nebulae")
    def test_has_emission_nebulae(self):
        """Catalog contains emission nebulae."""
        nebulae = MESSIER.filter_by_type("emission_nebula")
        with allure.step(f"Emission nebula count = {len(nebulae)}"):
            assert len(nebulae) > 0
