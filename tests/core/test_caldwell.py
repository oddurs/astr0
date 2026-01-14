"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                        CALDWELL CATALOG TESTS                                ║
║                                                                              ║
║  Tests for Sir Patrick Moore's Caldwell catalog - 109 deep sky objects      ║
║  complementing the Messier catalog with NGC cross-references.               ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import allure
import pytest

from starward.core.caldwell import (
    Caldwell,
    CaldwellCatalog,
    caldwell_coords,
    caldwell_altitude,
    caldwell_transit_altitude,
)
from starward.core.caldwell_types import CaldwellObject, CALDWELL_OBJECT_TYPES
from starward.core.observer import Observer
from starward.core.time import JulianDate


# ═══════════════════════════════════════════════════════════════════════════════
#  CATALOG DATA
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Catalog Data")
class TestCaldwellData:
    """Tests for the Caldwell data completeness and accuracy."""

    @allure.title("Catalog has objects")
    def test_catalog_has_objects(self):
        """Catalog contains objects."""
        with allure.step(f"Catalog size = {len(Caldwell)}"):
            assert len(Caldwell) > 0

    @allure.title("CaldwellObject is immutable")
    def test_caldwell_object_is_frozen(self):
        """CaldwellObject is immutable."""
        obj = Caldwell.get(65)  # Sculptor Galaxy
        with allure.step(f"Attempt to modify C{obj.number}"):
            with pytest.raises(AttributeError):
                obj.name = "Modified"

    @allure.title("All objects have required fields")
    def test_each_object_has_required_fields(self):
        """Each object has all required fields populated."""
        for obj in Caldwell.list_all():
            assert obj.number > 0
            assert 0 <= obj.ra_hours < 24
            assert -90 <= obj.dec_degrees <= 90
            assert obj.constellation


# ═══════════════════════════════════════════════════════════════════════════════
#  CATALOG CLASS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Catalog Class")
class TestCaldwellCatalog:
    """Tests for the CaldwellCatalog class."""

    @allure.title("Caldwell is singleton instance")
    def test_singleton_instance(self):
        """Caldwell is the singleton catalog instance."""
        with allure.step(f"Type = {type(Caldwell).__name__}"):
            assert isinstance(Caldwell, CaldwellCatalog)

    @allure.title("get() returns correct object")
    def test_get_returns_correct_object(self):
        """get() returns the correct object."""
        with allure.step("Get C54"):
            obj = Caldwell.get(54)
        with allure.step(f"C54 = {obj.name}"):
            assert obj.number == 54
            assert obj.name == "Sculptor Galaxy"

    @allure.title("get() raises KeyError for invalid number")
    def test_get_invalid_number_raises(self):
        """get() raises KeyError for number not in catalog."""
        with allure.step("Get C999"):
            with pytest.raises(KeyError):
                Caldwell.get(999)

    @allure.title("get(0) raises ValueError")
    def test_get_zero_raises_value_error(self):
        """get() raises ValueError for zero."""
        with allure.step("Get C0"):
            with pytest.raises(ValueError):
                Caldwell.get(0)

    @allure.title("get(-1) raises ValueError")
    def test_get_negative_raises_value_error(self):
        """get() raises ValueError for negative numbers."""
        with allure.step("Get C-1"):
            with pytest.raises(ValueError):
                Caldwell.get(-1)

    @allure.title("get() rejects non-integer input")
    def test_get_invalid_type_raises(self):
        """get() raises error for non-integer input."""
        with allure.step("Get 'not a number'"):
            with pytest.raises((ValueError, TypeError)):
                Caldwell.get("not a number")

    @allure.title("get_by_ngc finds Sculptor Galaxy")
    def test_get_by_ngc(self):
        """get_by_ngc() finds objects by NGC cross-reference."""
        with allure.step("Get Caldwell for NGC 253"):
            obj = Caldwell.get_by_ngc(253)
        with allure.step(f"NGC 253 = C{obj.number} ({obj.name})"):
            assert obj is not None
            assert obj.number == 54

    @allure.title("get_by_ngc returns None for not found")
    def test_get_by_ngc_not_found(self):
        """get_by_ngc() returns None for objects without NGC."""
        with allure.step("Get Caldwell for NGC 999999"):
            result = Caldwell.get_by_ngc(999999)
        with allure.step(f"Result = {result}"):
            assert result is None

    @allure.title("list_all() returns objects")
    def test_list_all_returns_objects(self):
        """list_all() returns CaldwellObject instances."""
        objects = Caldwell.list_all()
        with allure.step(f"Count = {len(objects)}"):
            assert len(objects) > 0
            assert all(isinstance(o, CaldwellObject) for o in objects)

    @allure.title("list_all() sorted by number")
    def test_list_all_sorted_by_number(self):
        """list_all() returns objects sorted by number by default."""
        objects = Caldwell.list_all()
        numbers = [o.number for o in objects]
        with allure.step(f"First: C{numbers[0]}, Last: C{numbers[-1]}"):
            assert numbers == sorted(numbers)

    @allure.title("len(Caldwell) = 109")
    def test_len_returns_count(self):
        """len(Caldwell) returns object count."""
        with allure.step(f"len = {len(Caldwell)}"):
            assert len(Caldwell) > 0
            assert len(Caldwell) == 109

    @allure.title("Catalog is iterable")
    def test_iteration(self):
        """Catalog is iterable."""
        count = 0
        for obj in Caldwell:
            assert isinstance(obj, CaldwellObject)
            count += 1
        with allure.step(f"Iterated over {count} objects"):
            assert count > 0

    @allure.title("Catalog supports 'in' operator")
    def test_contains(self):
        """Catalog supports 'in' operator."""
        with allure.step("65 in Caldwell = True"):
            assert 65 in Caldwell
        with allure.step("999 in Caldwell = False"):
            assert 999 not in Caldwell


# ═══════════════════════════════════════════════════════════════════════════════
#  SEARCH
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Search")
class TestCaldwellSearch:
    """Tests for searching the Caldwell catalog."""

    @allure.title("Search by name: 'Sculptor'")
    def test_search_by_name(self):
        """Search finds objects by name."""
        with allure.step("Search 'Sculptor'"):
            results = Caldwell.search("Sculptor")
        with allure.step(f"Found {len(results)} result(s), includes C65 = {any(o.number == 65 for o in results)}"):
            assert len(results) >= 1
            assert any(o.number == 65 for o in results)

    @allure.title("Search by constellation: 'Cep'")
    def test_search_by_constellation(self):
        """Search finds objects by constellation."""
        with allure.step("Search 'Cep'"):
            results = Caldwell.search("Cep")
        with allure.step(f"Found {len(results)} in Cepheus"):
            assert len(results) > 0
            assert any(o.constellation == "Cep" for o in results)

    @allure.title("Search is case-insensitive")
    def test_search_case_insensitive(self):
        """Search is case-insensitive."""
        results1 = Caldwell.search("SCULPTOR")
        results2 = Caldwell.search("sculptor")
        results3 = Caldwell.search("Sculptor")
        with allure.step(f"SCULPTOR={len(results1)}, sculptor={len(results2)}, Sculptor={len(results3)}"):
            assert len(results1) == len(results2) == len(results3)

    @allure.title("Search returns empty for no match")
    def test_search_no_match(self):
        """Search returns empty list for no matches."""
        with allure.step("Search 'xyznonexistent'"):
            results = Caldwell.search("xyznonexistent")
        with allure.step(f"Results = {len(results)}"):
            assert len(results) == 0

    @allure.title("Search respects limit parameter")
    def test_search_limit(self):
        """Search respects limit parameter."""
        with allure.step("Search 'a' with limit=3"):
            results = Caldwell.search("a", limit=3)
        with allure.step(f"Results = {len(results)} (≤ 3)"):
            assert len(results) <= 3


# ═══════════════════════════════════════════════════════════════════════════════
#  FILTERS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Filters")
class TestCaldwellFilters:
    """Tests for filtering Caldwell objects."""

    @allure.title("Filter by constellation: Cep")
    def test_filter_by_constellation(self):
        """filter_by_constellation finds objects in constellation."""
        with allure.step("Filter by constellation 'Cep'"):
            cep_objects = Caldwell.filter_by_constellation("Cep")
        with allure.step(f"Found {len(cep_objects)} in Cepheus"):
            assert len(cep_objects) > 0
            assert all(o.constellation == "Cep" for o in cep_objects)

    @allure.title("Filter by magnitude ≤ 6.0")
    def test_filter_by_magnitude(self):
        """filter_by_magnitude finds bright objects."""
        with allure.step("Filter by magnitude ≤ 6.0"):
            bright = Caldwell.filter_by_magnitude(6.0)
        with allure.step(f"Found {len(bright)} bright objects"):
            assert len(bright) > 0
            assert all(o.magnitude <= 6.0 for o in bright if o.magnitude is not None)

    @allure.title("Filter by type: galaxy")
    def test_filter_by_type(self):
        """filter_by_type finds objects by type."""
        with allure.step("Filter by type 'galaxy'"):
            galaxies = Caldwell.filter_by_type("galaxy")
        with allure.step(f"Found {len(galaxies)} galaxies"):
            assert len(galaxies) > 0
            assert all(o.object_type == "galaxy" for o in galaxies)

    @allure.title("filter_named returns only named objects")
    def test_filter_named(self):
        """filter_named returns only named objects."""
        with allure.step("Filter named objects"):
            named_objects = Caldwell.filter_named()
        with allure.step(f"Found {len(named_objects)} named objects"):
            assert len(named_objects) > 0
            assert all(o.name is not None for o in named_objects)


# ═══════════════════════════════════════════════════════════════════════════════
#  WELL-KNOWN OBJECTS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Well-Known Objects")
class TestWellKnownCaldwell:
    """Tests for specific well-known Caldwell objects."""

    @pytest.mark.golden
    @allure.title("C54 - Sculptor Galaxy (NGC 253)")
    @allure.description("""
    Verifies C54 is the Sculptor Galaxy (NGC 253).
    One of the brightest galaxies outside our Local Group.
    """)
    def test_c54_sculptor_galaxy(self):
        """C 54 is the Sculptor Galaxy (NGC 253)."""
        with allure.step("Get C54"):
            obj = Caldwell.get(54)
        with allure.step(f"Name = {obj.name}"):
            assert obj.name == "Sculptor Galaxy"
        with allure.step(f"NGC = {obj.ngc_number}"):
            assert obj.ngc_number == 253
        with allure.step(f"Type = {obj.object_type}"):
            assert obj.object_type == "galaxy"
        with allure.step(f"Constellation = {obj.constellation}"):
            assert obj.constellation == "Scl"

    @pytest.mark.golden
    @allure.title("C14 - Double Cluster (NGC 869)")
    @allure.description("""
    Verifies C14 is the Double Cluster (NGC 869 + 884).
    Famous naked-eye double open cluster in Perseus.
    """)
    def test_c14_double_cluster(self):
        """C 14 is the Double Cluster (NGC 869 + 884)."""
        with allure.step("Get C14"):
            obj = Caldwell.get(14)
        with allure.step(f"Name = {obj.name}"):
            assert obj.name == "Double Cluster"
        with allure.step(f"NGC = {obj.ngc_number}"):
            assert obj.ngc_number == 869
        with allure.step(f"Type = {obj.object_type}"):
            assert obj.object_type == "open_cluster"
        with allure.step(f"Constellation = {obj.constellation}"):
            assert obj.constellation == "Per"

    @pytest.mark.golden
    @allure.title("C34 - West Veil Nebula (NGC 6960)")
    @allure.description("""
    Verifies C34 is the West Veil Nebula (NGC 6960).
    Part of the Cygnus Loop supernova remnant.
    """)
    def test_c34_veil_nebula(self):
        """C 34 is the West Veil Nebula (NGC 6960)."""
        with allure.step("Get C34"):
            obj = Caldwell.get(34)
        with allure.step(f"Name = {obj.name}"):
            assert obj.name == "West Veil Nebula"
        with allure.step(f"NGC = {obj.ngc_number}"):
            assert obj.ngc_number == 6960
        with allure.step(f"Type = {obj.object_type}"):
            assert obj.object_type == "supernova_remnant"
        with allure.step(f"Constellation = {obj.constellation}"):
            assert obj.constellation == "Cyg"

    @pytest.mark.golden
    @allure.title("C55 - Saturn Nebula (NGC 7009)")
    @allure.description("""
    Verifies C55 is the Saturn Nebula (NGC 7009).
    Named for its resemblance to Saturn with ring-like extensions.
    """)
    def test_c55_saturn_nebula(self):
        """C 55 is the Saturn Nebula (NGC 7009)."""
        with allure.step("Get C55"):
            obj = Caldwell.get(55)
        with allure.step(f"Name = {obj.name}"):
            assert obj.name == "Saturn Nebula"
        with allure.step(f"NGC = {obj.ngc_number}"):
            assert obj.ngc_number == 7009
        with allure.step(f"Type = {obj.object_type}"):
            assert obj.object_type == "planetary_nebula"
        with allure.step(f"Constellation = {obj.constellation}"):
            assert obj.constellation == "Aqr"


# ═══════════════════════════════════════════════════════════════════════════════
#  COORDINATES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Coordinates")
class TestCaldwellCoordinates:
    """Tests for Caldwell coordinate functions."""

    @allure.title("caldwell_coords returns ICRSCoord")
    def test_caldwell_coords_returns_icrs(self):
        """caldwell_coords returns ICRSCoord."""
        from starward.core.coords import ICRSCoord
        with allure.step("Get coords for C54"):
            coords = caldwell_coords(54)
        with allure.step(f"Type = {type(coords).__name__}"):
            assert isinstance(coords, ICRSCoord)

    @allure.title("Sculptor Galaxy coords: RA ~00h47m, Dec ~-25°")
    def test_sculptor_galaxy_coordinates(self):
        """Sculptor Galaxy coordinates are approximately correct."""
        with allure.step("Get C54 coordinates"):
            coords = caldwell_coords(54)
        with allure.step(f"RA = {coords.ra.hours:.2f}h (expected 0-2)"):
            assert 0.0 < coords.ra.hours < 2.0
        with allure.step(f"Dec = {coords.dec.degrees:.1f}° (expected -30 to -20)"):
            assert -30.0 < coords.dec.degrees < -20.0


# ═══════════════════════════════════════════════════════════════════════════════
#  VISIBILITY
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Visibility")
class TestCaldwellVisibility:
    """Tests for Caldwell visibility calculations."""

    @pytest.fixture
    def greenwich(self):
        """Greenwich Observatory observer."""
        return Observer.from_degrees("Greenwich", 51.4772, -0.0005)

    @pytest.fixture
    def j2000(self):
        """J2000.0 epoch."""
        return JulianDate(2451545.0)

    @allure.title("caldwell_altitude returns Angle")
    def test_altitude_returns_angle(self):
        """caldwell_altitude returns an Angle."""
        from starward.core.angles import Angle
        observer = Observer.from_degrees("Test", 40.0, -74.0)
        jd = JulianDate(2451545.0)
        with allure.step("Calculate C54 altitude"):
            alt = caldwell_altitude(54, observer, jd)
        with allure.step(f"Type = {type(alt).__name__}, value = {alt.degrees:.1f}°"):
            assert isinstance(alt, Angle)

    @allure.title("Sculptor Galaxy transit altitude from Greenwich ~13.5°")
    def test_transit_altitude_reasonable(self, greenwich):
        """Transit altitude is reasonable for location."""
        with allure.step("Calculate C54 transit altitude from Greenwich"):
            trans_alt = caldwell_transit_altitude(54, greenwich)
        with allure.step(f"Transit altitude = {trans_alt.degrees:.1f}° (expected 10-20)"):
            assert 10.0 < trans_alt.degrees < 20.0


# ═══════════════════════════════════════════════════════════════════════════════
#  CATALOG STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Catalog Statistics")
class TestCaldwellStats:
    """Tests for Caldwell catalog statistics."""

    @allure.title("stats() returns dict with expected keys")
    def test_stats_returns_dict(self):
        """stats() returns dictionary with expected keys."""
        with allure.step("Get catalog stats"):
            stats = Caldwell.stats()
        with allure.step(f"Keys = {list(stats.keys())}"):
            assert isinstance(stats, dict)
            assert 'total' in stats
            assert 'by_type' in stats
            assert 'with_ngc_designation' in stats

    @allure.title("stats total matches len(Caldwell)")
    def test_stats_total_matches_len(self):
        """stats total matches catalog length."""
        stats = Caldwell.stats()
        with allure.step(f"stats.total = {stats['total']}, len(Caldwell) = {len(Caldwell)}"):
            assert stats['total'] == len(Caldwell)

    @allure.title("stats by_type is not empty")
    def test_stats_by_type_not_empty(self):
        """stats by_type is not empty."""
        stats = Caldwell.stats()
        with allure.step(f"Object types = {len(stats['by_type'])}"):
            assert len(stats['by_type']) > 0


# ═══════════════════════════════════════════════════════════════════════════════
#  OBJECT PROPERTIES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Object Properties")
class TestObjectProperties:
    """Tests for CaldwellObject properties and methods."""

    @allure.title("designation property returns 'C 54'")
    def test_designation_with_name(self):
        """designation property returns C number."""
        obj = Caldwell.get(54)
        with allure.step(f"Designation = {obj.designation}"):
            assert obj.designation == "C 54"

    @allure.title("ngc_designation property returns 'NGC 253'")
    def test_ngc_designation_property(self):
        """ngc_designation property returns NGC number when available."""
        obj = Caldwell.get(54)
        with allure.step(f"NGC designation = {obj.ngc_designation}"):
            assert obj.ngc_designation == "NGC 253"

    @allure.title("catalog_designations includes both C and NGC")
    def test_catalog_designations_property(self):
        """catalog_designations returns all designations."""
        obj = Caldwell.get(54)
        designations = obj.catalog_designations
        with allure.step(f"Designations = {designations}"):
            assert "C 54" in designations
            assert "NGC 253" in designations

    @allure.title("String representation is readable")
    def test_str_representation(self):
        """String representation is readable."""
        obj = Caldwell.get(54)
        str_repr = str(obj)
        with allure.step(f"str = {str_repr[:50]}..."):
            assert "C 54" in str_repr
            assert "Sculptor Galaxy" in str_repr
