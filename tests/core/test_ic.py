"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                            IC CATALOG TESTS                                  ║
║                                                                              ║
║  Tests for the Index Catalogue - lookups, searches, filtering,              ║
║  coordinates, and visibility for deep sky objects.                          ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import allure
import pytest

from starward.core.ic import (
    IC,
    ICCatalog,
    ic_coords,
    ic_altitude,
    ic_transit_altitude,
)
from starward.core.ic_types import ICObject, IC_OBJECT_TYPES
from starward.core.observer import Observer
from starward.core.time import JulianDate


# ═══════════════════════════════════════════════════════════════════════════════
#  CATALOG DATA
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Catalog Data")
class TestICData:
    """Tests for the IC data completeness and accuracy."""

    @allure.title("Catalog has objects")
    def test_catalog_has_objects(self):
        """Catalog contains IC objects."""
        with allure.step(f"Catalog size = {len(IC)}"):
            assert len(IC) > 0

    @allure.title("ICObject is immutable")
    def test_ic_object_is_frozen(self):
        """ICObject is immutable."""
        obj = IC.get(434)
        with allure.step(f"Attempt to modify IC {obj.number}"):
            with pytest.raises(AttributeError):
                obj.name = "Modified"

    @allure.title("All objects have required fields")
    def test_each_object_has_required_fields(self):
        """Each object has all required fields populated."""
        for obj in IC.list_all():
            assert obj.number > 0
            assert obj.object_type in IC_OBJECT_TYPES
            assert 0 <= obj.ra_hours < 24
            assert -90 <= obj.dec_degrees <= 90
            assert obj.constellation


# ═══════════════════════════════════════════════════════════════════════════════
#  CATALOG CLASS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Catalog Class")
class TestICCatalog:
    """Tests for the ICCatalog class."""

    @allure.title("IC is singleton instance")
    def test_singleton_instance(self):
        """IC is the singleton catalog instance."""
        with allure.step(f"Type = {type(IC).__name__}"):
            assert isinstance(IC, ICCatalog)

    @allure.title("get() returns correct object")
    def test_get_returns_correct_object(self):
        """get() returns the correct IC object."""
        with allure.step("Get IC 434"):
            ic434 = IC.get(434)
        with allure.step(f"IC 434 = {ic434.name}"):
            assert ic434.number == 434
            assert "Horsehead" in ic434.name

    @allure.title("get() raises KeyError for invalid number")
    def test_get_invalid_number_raises(self):
        """get() raises KeyError for number not in catalog."""
        with allure.step("Get IC 99999"):
            with pytest.raises(KeyError):
                IC.get(99999)

    @allure.title("get(0) raises ValueError")
    def test_get_zero_raises_value_error(self):
        """get() raises ValueError for zero."""
        with allure.step("Get IC 0"):
            with pytest.raises(ValueError):
                IC.get(0)

    @allure.title("get(-1) raises ValueError")
    def test_get_negative_raises_value_error(self):
        """get() raises ValueError for negative numbers."""
        with allure.step("Get IC -1"):
            with pytest.raises(ValueError):
                IC.get(-1)

    @allure.title("get() rejects non-integer input")
    def test_get_invalid_type_raises(self):
        """get() raises error for non-integer input."""
        with allure.step("Get 'not a number'"):
            with pytest.raises((ValueError, TypeError)):
                IC.get("not a number")

    @allure.title("list_all() returns objects")
    def test_list_all_returns_objects(self):
        """list_all() returns IC objects."""
        objects = IC.list_all()
        with allure.step(f"Count = {len(objects)}"):
            assert len(objects) > 0
            assert all(isinstance(o, ICObject) for o in objects)

    @allure.title("list_all() sorted by number")
    def test_list_all_sorted_by_number(self):
        """list_all() returns objects sorted by number."""
        objects = IC.list_all()
        numbers = [o.number for o in objects]
        with allure.step(f"First: IC {numbers[0]}, Last: IC {numbers[-1]}"):
            assert numbers == sorted(numbers)

    @allure.title("len(IC) returns count")
    def test_len_returns_count(self):
        """len(IC) returns object count."""
        with allure.step(f"len = {len(IC)}"):
            assert len(IC) > 0

    @allure.title("Catalog is iterable")
    def test_iteration(self):
        """Catalog is iterable."""
        count = 0
        for obj in IC:
            assert isinstance(obj, ICObject)
            count += 1
        with allure.step(f"Iterated over {count} objects"):
            assert count > 0

    @allure.title("Catalog supports 'in' operator")
    def test_contains(self):
        """Catalog supports 'in' operator."""
        with allure.step("434 in IC = True"):
            assert 434 in IC
        with allure.step("99999 in IC = False"):
            assert 99999 not in IC


# ═══════════════════════════════════════════════════════════════════════════════
#  SEARCH
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Search")
class TestICSearch:
    """Tests for searching the IC catalog."""

    @allure.title("Search by name: 'Horsehead'")
    def test_search_by_name(self):
        """Search finds objects by name."""
        with allure.step("Search 'Horsehead'"):
            results = IC.search("Horsehead")
        with allure.step(f"Found {len(results)} result(s), includes IC 434 = {any(o.number == 434 for o in results)}"):
            assert len(results) >= 1
            assert any(o.number == 434 for o in results)

    @allure.title("Search by type: 'nebula'")
    def test_search_by_type(self):
        """Search finds objects by type."""
        with allure.step("Search 'nebula'"):
            results = IC.search("nebula")
        with allure.step(f"Found {len(results)} nebulae"):
            assert len(results) > 0

    @allure.title("Search by constellation: 'Ori'")
    def test_search_by_constellation(self):
        """Search finds objects by constellation."""
        with allure.step("Search 'Ori'"):
            results = IC.search("Ori")
        with allure.step(f"Found {len(results)} in Orion"):
            assert len(results) > 0

    @allure.title("Search is case-insensitive")
    def test_search_case_insensitive(self):
        """Search is case-insensitive."""
        results1 = IC.search("HORSEHEAD")
        results2 = IC.search("horsehead")
        results3 = IC.search("Horsehead")
        with allure.step(f"HORSEHEAD={len(results1)}, horsehead={len(results2)}, Horsehead={len(results3)}"):
            assert len(results1) == len(results2) == len(results3)

    @allure.title("Search returns empty for no match")
    def test_search_no_match(self):
        """Search returns empty list for no matches."""
        with allure.step("Search 'xyznonexistent'"):
            results = IC.search("xyznonexistent")
        with allure.step(f"Results = {len(results)}"):
            assert len(results) == 0

    @allure.title("Search results sorted by number")
    def test_search_results_sorted(self):
        """Search results are sorted by IC number."""
        results = IC.search("nebula")
        numbers = [o.number for o in results]
        with allure.step(f"Sorted = {numbers == sorted(numbers)}"):
            assert numbers == sorted(numbers)

    @allure.title("Search respects limit parameter")
    def test_search_limit(self):
        """Search respects limit parameter."""
        with allure.step("Search 'a' with limit=3"):
            results = IC.search("a", limit=3)
        with allure.step(f"Results = {len(results)} (≤ 3)"):
            assert len(results) <= 3


# ═══════════════════════════════════════════════════════════════════════════════
#  FILTERS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Filters")
class TestICFilters:
    """Tests for filtering IC objects."""

    @allure.title("Filter by type: dark_nebula")
    def test_filter_by_type_dark_nebula(self):
        """filter_by_type finds all dark nebulae."""
        with allure.step("Filter by type 'dark_nebula'"):
            dark_nebulae = IC.filter_by_type("dark_nebula")
        with allure.step(f"Found {len(dark_nebulae)} dark nebulae"):
            assert len(dark_nebulae) > 0
            assert all(o.object_type == "dark_nebula" for o in dark_nebulae)

    @allure.title("Filter by type is case-insensitive")
    def test_filter_by_type_case_insensitive(self):
        """filter_by_type is case-insensitive."""
        results1 = IC.filter_by_type("DARK_NEBULA")
        results2 = IC.filter_by_type("dark_nebula")
        with allure.step(f"DARK_NEBULA={len(results1)}, dark_nebula={len(results2)}"):
            assert len(results1) == len(results2)

    @allure.title("Filter by constellation: Ori")
    def test_filter_by_constellation(self):
        """filter_by_constellation finds objects in constellation."""
        with allure.step("Filter by constellation 'Ori'"):
            ori_objects = IC.filter_by_constellation("Ori")
        with allure.step(f"Found {len(ori_objects)} in Orion"):
            assert len(ori_objects) > 0
            assert all(o.constellation == "Ori" for o in ori_objects)

    @allure.title("Filter by magnitude ≤ 10.0")
    def test_filter_by_magnitude(self):
        """filter_by_magnitude finds bright objects."""
        with allure.step("Filter by magnitude ≤ 10.0"):
            bright = IC.filter_by_magnitude(10.0)
        with allure.step(f"Found {len(bright)} bright objects"):
            assert len(bright) > 0
            assert all(o.magnitude <= 10.0 for o in bright)

    @allure.title("get_by_ngc returns ICObject or None")
    def test_get_by_ngc(self):
        """get_by_ngc finds IC object by NGC number."""
        with allure.step("Get IC for NGC 1"):
            result = IC.get_by_ngc(1)
        with allure.step(f"Result = {type(result).__name__ if result else None}"):
            assert result is None or isinstance(result, ICObject)


# ═══════════════════════════════════════════════════════════════════════════════
#  WELL-KNOWN OBJECTS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Well-Known Objects")
class TestWellKnownIC:
    """Tests for specific well-known IC objects."""

    @pytest.mark.golden
    @allure.title("IC 434 - Horsehead Nebula")
    @allure.description("""
    Verifies IC 434 is the Horsehead Nebula region in Orion.
    Famous dark nebula silhouetted against emission nebula.
    """)
    def test_ic434_horsehead(self):
        """IC 434 is the Horsehead Nebula region."""
        with allure.step("Get IC 434"):
            ic434 = IC.get(434)
        with allure.step(f"Name = {ic434.name}"):
            assert "Horsehead" in ic434.name
        with allure.step(f"Type = {ic434.object_type}"):
            assert ic434.object_type == "dark_nebula"
        with allure.step(f"Constellation = {ic434.constellation}"):
            assert ic434.constellation == "Ori"

    @pytest.mark.golden
    @allure.title("IC 1805 - Heart Nebula")
    @allure.description("""
    Verifies IC 1805 is the Heart Nebula in Cassiopeia.
    Named for its heart-like shape.
    """)
    def test_ic1805_heart_nebula(self):
        """IC 1805 is the Heart Nebula."""
        with allure.step("Get IC 1805"):
            ic1805 = IC.get(1805)
        with allure.step(f"Name = {ic1805.name}"):
            assert "Heart" in ic1805.name
        with allure.step(f"Type = {ic1805.object_type}"):
            assert ic1805.object_type == "emission_nebula"
        with allure.step(f"Constellation = {ic1805.constellation}"):
            assert ic1805.constellation == "Cas"

    @pytest.mark.golden
    @allure.title("IC 1848 - Soul Nebula")
    @allure.description("""
    Verifies IC 1848 is the Soul Nebula in Cassiopeia.
    Located next to the Heart Nebula (IC 1805).
    """)
    def test_ic1848_soul_nebula(self):
        """IC 1848 is the Soul Nebula."""
        with allure.step("Get IC 1848"):
            ic1848 = IC.get(1848)
        with allure.step(f"Name = {ic1848.name}"):
            assert "Soul" in ic1848.name
        with allure.step(f"Type = {ic1848.object_type}"):
            assert ic1848.object_type == "emission_nebula"
        with allure.step(f"Constellation = {ic1848.constellation}"):
            assert ic1848.constellation == "Cas"


# ═══════════════════════════════════════════════════════════════════════════════
#  COORDINATES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Coordinates")
class TestICCoordinates:
    """Tests for IC coordinate functions."""

    @allure.title("ic_coords returns ICRSCoord")
    def test_ic_coords_returns_icrs(self):
        """ic_coords returns ICRSCoord."""
        from starward.core.coords import ICRSCoord
        with allure.step("Get coords for IC 434"):
            coords = ic_coords(434)
        with allure.step(f"Type = {type(coords).__name__}"):
            assert isinstance(coords, ICRSCoord)

    @allure.title("IC 434 coordinates: RA ~05h41m, Dec ~-02°")
    def test_ic434_coordinates(self):
        """IC 434 coordinates are approximately correct."""
        with allure.step("Get IC 434 coordinates"):
            coords = ic_coords(434)
        with allure.step(f"RA = {coords.ra.hours:.2f}h (expected 5-6)"):
            assert 5.0 < coords.ra.hours < 6.0
        with allure.step(f"Dec = {coords.dec.degrees:.1f}° (expected -4 to 0)"):
            assert -4.0 < coords.dec.degrees < 0.0

    @allure.title("IC 1805 coordinates: RA ~02h32m, Dec ~+61°")
    def test_ic1805_coordinates(self):
        """IC 1805 (Heart Nebula) coordinates are approximately correct."""
        with allure.step("Get IC 1805 coordinates"):
            coords = ic_coords(1805)
        with allure.step(f"RA = {coords.ra.hours:.2f}h (expected 2-3)"):
            assert 2.0 < coords.ra.hours < 3.0
        with allure.step(f"Dec = {coords.dec.degrees:.1f}° (expected 60-63)"):
            assert 60.0 < coords.dec.degrees < 63.0


# ═══════════════════════════════════════════════════════════════════════════════
#  VISIBILITY
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Visibility")
class TestICVisibility:
    """Tests for IC visibility calculations."""

    @pytest.fixture
    def greenwich(self):
        """Greenwich Observatory observer."""
        return Observer.from_degrees("Greenwich", 51.4772, -0.0005)

    @pytest.fixture
    def j2000(self):
        """J2000.0 epoch."""
        return JulianDate(2451545.0)

    @allure.title("ic_altitude returns Angle")
    def test_altitude_returns_angle(self):
        """ic_altitude returns an Angle."""
        from starward.core.angles import Angle
        observer = Observer.from_degrees("Test", 40.0, -74.0)
        jd = JulianDate(2451545.0)
        with allure.step("Calculate IC 434 altitude"):
            alt = ic_altitude(434, observer, jd)
        with allure.step(f"Type = {type(alt).__name__}, value = {alt.degrees:.1f}°"):
            assert isinstance(alt, Angle)

    @allure.title("IC 1805 transit altitude from Greenwich ~80°")
    def test_transit_altitude_reasonable(self, greenwich):
        """Transit altitude is reasonable for location."""
        with allure.step("Calculate IC 1805 transit altitude from Greenwich"):
            trans_alt = ic_transit_altitude(1805, greenwich)
        with allure.step(f"Transit altitude = {trans_alt.degrees:.1f}° (expected 75-85)"):
            assert 75.0 < trans_alt.degrees < 85.0


# ═══════════════════════════════════════════════════════════════════════════════
#  CATALOG STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Catalog Statistics")
class TestICStats:
    """Tests for IC catalog statistics."""

    @allure.title("stats() returns dict with expected keys")
    def test_stats_returns_dict(self):
        """stats() returns dictionary with expected keys."""
        with allure.step("Get catalog stats"):
            stats = IC.stats()
        with allure.step(f"Keys = {list(stats.keys())}"):
            assert isinstance(stats, dict)
            assert 'total' in stats
            assert 'by_type' in stats

    @allure.title("stats total matches len(IC)")
    def test_stats_total_matches_len(self):
        """stats total matches catalog length."""
        stats = IC.stats()
        with allure.step(f"stats.total = {stats['total']}, len(IC) = {len(IC)}"):
            assert stats['total'] == len(IC)

    @allure.title("stats by_type is not empty")
    def test_stats_by_type_not_empty(self):
        """stats by_type is not empty."""
        stats = IC.stats()
        with allure.step(f"Object types = {len(stats['by_type'])}"):
            assert len(stats['by_type']) > 0


# ═══════════════════════════════════════════════════════════════════════════════
#  OBJECT TYPE COVERAGE
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Object Type Coverage")
class TestICObjectTypes:
    """Tests for IC object type coverage."""

    @allure.title("Catalog has dark nebulae")
    def test_has_dark_nebulae(self):
        """Catalog contains dark nebulae."""
        nebulae = IC.filter_by_type("dark_nebula")
        with allure.step(f"Dark nebula count = {len(nebulae)}"):
            assert len(nebulae) > 0

    @allure.title("Catalog has emission nebulae")
    def test_has_emission_nebulae(self):
        """Catalog contains emission nebulae."""
        nebulae = IC.filter_by_type("emission_nebula")
        with allure.step(f"Emission nebula count = {len(nebulae)}"):
            assert len(nebulae) > 0

    @allure.title("Catalog has galaxies")
    def test_has_galaxies(self):
        """Catalog contains galaxies."""
        galaxies = IC.filter_by_type("galaxy")
        with allure.step(f"Galaxy count = {len(galaxies)}"):
            assert len(galaxies) > 0


# ═══════════════════════════════════════════════════════════════════════════════
#  FILTER OBSERVABLE
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Observable Filter")
class TestICObservable:
    """Tests for observable IC object filtering."""

    @allure.title("filter_observable returns list of ICObjects")
    def test_filter_observable_returns_list(self):
        """filter_observable returns list of ICObjects."""
        with allure.step("Filter observable with max_magnitude=10.0"):
            objects = IC.filter_observable(max_magnitude=10.0)
        with allure.step(f"Count = {len(objects)}"):
            assert isinstance(objects, list)
            assert all(isinstance(o, ICObject) for o in objects)

    @allure.title("filter_observable respects magnitude limit")
    def test_filter_observable_respects_magnitude(self):
        """filter_observable respects magnitude limit."""
        with allure.step("Filter observable with max_magnitude=8.0"):
            objects = IC.filter_observable(max_magnitude=8.0)
        with allure.step(f"All magnitudes ≤ 8.0: {all(o.magnitude <= 8.0 for o in objects if o.magnitude)}"):
            for obj in objects:
                assert obj.magnitude is not None
                assert obj.magnitude <= 8.0

    @allure.title("filter_observable has_name=True")
    def test_filter_observable_has_name(self):
        """filter_observable can filter to named objects only."""
        with allure.step("Filter observable with has_name=True"):
            objects = IC.filter_observable(has_name=True)
        with allure.step(f"Count = {len(objects)}, all named: {all(o.name for o in objects)}"):
            for obj in objects:
                assert obj.name is not None
                assert obj.name != ""
