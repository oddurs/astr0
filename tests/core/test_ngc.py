"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                           NGC CATALOG TESTS                                  ║
║                                                                              ║
║  Tests for the New General Catalogue - lookups, searches, filtering,        ║
║  coordinates, and cross-references with Messier catalog.                    ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import allure
import pytest

from starward.core.ngc import (
    NGC,
    NGCCatalog,
    ngc_coords,
    ngc_altitude,
    ngc_transit_altitude,
)
from starward.core.ngc_types import NGCObject, NGC_OBJECT_TYPES
from starward.core.observer import Observer
from starward.core.time import JulianDate


# ═══════════════════════════════════════════════════════════════════════════════
#  CATALOG DATA
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Catalog Data")
class TestNGCData:
    """Tests for the NGC data completeness and accuracy."""

    @allure.title("Catalog has objects")
    def test_catalog_has_objects(self):
        """Catalog contains NGC objects."""
        with allure.step(f"Catalog size = {len(NGC)}"):
            assert len(NGC) > 0

    @allure.title("NGCObject is immutable")
    def test_ngc_object_is_frozen(self):
        """NGCObject is immutable."""
        obj = NGC.get(7000)
        with allure.step(f"Attempt to modify NGC {obj.number}"):
            with pytest.raises(AttributeError):
                obj.name = "Modified"

    @allure.title("All objects have required fields")
    def test_each_object_has_required_fields(self):
        """Each object has all required fields populated."""
        for obj in NGC.list_all():
            assert obj.number > 0
            assert obj.object_type in NGC_OBJECT_TYPES
            assert 0 <= obj.ra_hours < 24
            assert -90 <= obj.dec_degrees <= 90
            assert obj.constellation


# ═══════════════════════════════════════════════════════════════════════════════
#  CATALOG CLASS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Catalog Class")
class TestNGCCatalog:
    """Tests for the NGCCatalog class."""

    @allure.title("NGC is singleton instance")
    def test_singleton_instance(self):
        """NGC is the singleton catalog instance."""
        with allure.step(f"Type = {type(NGC).__name__}"):
            assert isinstance(NGC, NGCCatalog)

    @allure.title("get() returns correct object")
    def test_get_returns_correct_object(self):
        """get() returns the correct NGC object."""
        with allure.step("Get NGC 7000"):
            ngc7000 = NGC.get(7000)
        with allure.step(f"NGC 7000 = {ngc7000.name}"):
            assert ngc7000.number == 7000
            assert "North America" in ngc7000.name

    @allure.title("get() raises KeyError for invalid number")
    def test_get_invalid_number_raises(self):
        """get() raises KeyError for number not in catalog."""
        with allure.step("Get NGC 99999"):
            with pytest.raises(KeyError):
                NGC.get(99999)

    @allure.title("get(0) raises ValueError")
    def test_get_zero_raises_value_error(self):
        """get() raises ValueError for zero."""
        with allure.step("Get NGC 0"):
            with pytest.raises(ValueError):
                NGC.get(0)

    @allure.title("get(-1) raises ValueError")
    def test_get_negative_raises_value_error(self):
        """get() raises ValueError for negative numbers."""
        with allure.step("Get NGC -1"):
            with pytest.raises(ValueError):
                NGC.get(-1)
        with allure.step("Get NGC -100"):
            with pytest.raises(ValueError):
                NGC.get(-100)

    @allure.title("get() rejects non-integer input")
    def test_get_invalid_type_raises(self):
        """get() raises error for non-integer input."""
        with allure.step("Get 'not a number'"):
            with pytest.raises((ValueError, TypeError)):
                NGC.get("not a number")
        with allure.step("Get 3.14"):
            with pytest.raises((ValueError, TypeError)):
                NGC.get(3.14)

    @allure.title("list_all() returns objects")
    def test_list_all_returns_objects(self):
        """list_all() returns NGC objects."""
        objects = NGC.list_all()
        with allure.step(f"Count = {len(objects)}"):
            assert len(objects) > 0
            assert all(isinstance(o, NGCObject) for o in objects)

    @allure.title("list_all() sorted by number")
    def test_list_all_sorted_by_number(self):
        """list_all() returns objects sorted by number."""
        objects = NGC.list_all()
        numbers = [o.number for o in objects]
        with allure.step(f"First: NGC {numbers[0]}, Last: NGC {numbers[-1]}"):
            assert numbers == sorted(numbers)

    @allure.title("len(NGC) returns count")
    def test_len_returns_count(self):
        """len(NGC) returns object count."""
        with allure.step(f"len = {len(NGC)}"):
            assert len(NGC) > 0

    @allure.title("Catalog is iterable")
    def test_iteration(self):
        """Catalog is iterable."""
        count = 0
        for obj in NGC:
            assert isinstance(obj, NGCObject)
            count += 1
        with allure.step(f"Iterated over {count} objects"):
            assert count > 0

    @allure.title("Catalog supports 'in' operator")
    def test_contains(self):
        """Catalog supports 'in' operator."""
        with allure.step("7000 in NGC = True"):
            assert 7000 in NGC
        with allure.step("99999 in NGC = False"):
            assert 99999 not in NGC


# ═══════════════════════════════════════════════════════════════════════════════
#  SEARCH
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Search")
class TestNGCSearch:
    """Tests for searching the NGC catalog."""

    @allure.title("Search by name: 'North America'")
    def test_search_by_name(self):
        """Search finds objects by name."""
        with allure.step("Search 'North America'"):
            results = NGC.search("North America")
        with allure.step(f"Found {len(results)} result(s), includes NGC 7000 = {any(o.number == 7000 for o in results)}"):
            assert len(results) >= 1
            assert any(o.number == 7000 for o in results)

    @allure.title("Search by type: 'nebula'")
    def test_search_by_type(self):
        """Search finds objects by type."""
        with allure.step("Search 'nebula'"):
            results = NGC.search("nebula")
        with allure.step(f"Found {len(results)} nebulae"):
            assert len(results) > 0

    @allure.title("Search by constellation: 'Cyg'")
    def test_search_by_constellation(self):
        """Search finds objects by constellation."""
        with allure.step("Search 'Cyg'"):
            results = NGC.search("Cyg")
        with allure.step(f"Found {len(results)} in Cygnus"):
            assert len(results) > 0

    @allure.title("Search is case-insensitive")
    def test_search_case_insensitive(self):
        """Search is case-insensitive."""
        results1 = NGC.search("ORION")
        results2 = NGC.search("orion")
        results3 = NGC.search("Orion")
        with allure.step(f"ORION={len(results1)}, orion={len(results2)}, Orion={len(results3)}"):
            assert len(results1) == len(results2) == len(results3)

    @allure.title("Search returns empty for no match")
    def test_search_no_match(self):
        """Search returns empty list for no matches."""
        with allure.step("Search 'xyznonexistent'"):
            results = NGC.search("xyznonexistent")
        with allure.step(f"Results = {len(results)}"):
            assert len(results) == 0

    @allure.title("Search results sorted by number")
    def test_search_results_sorted(self):
        """Search results are sorted by NGC number."""
        results = NGC.search("nebula")
        numbers = [o.number for o in results]
        with allure.step(f"Sorted = {numbers == sorted(numbers)}"):
            assert numbers == sorted(numbers)

    @allure.title("Search respects limit parameter")
    def test_search_limit(self):
        """Search respects limit parameter."""
        with allure.step("Search 'a' with limit=3"):
            results = NGC.search("a", limit=3)
        with allure.step(f"Results = {len(results)} (≤ 3)"):
            assert len(results) <= 3


# ═══════════════════════════════════════════════════════════════════════════════
#  FILTERS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Filters")
class TestNGCFilters:
    """Tests for filtering NGC objects."""

    @allure.title("Filter by type: galaxy")
    def test_filter_by_type_galaxy(self):
        """filter_by_type finds all galaxies."""
        with allure.step("Filter by type 'galaxy'"):
            galaxies = NGC.filter_by_type("galaxy")
        with allure.step(f"Found {len(galaxies)} galaxies"):
            assert len(galaxies) > 0
            assert all(o.object_type == "galaxy" for o in galaxies)

    @allure.title("Filter by type is case-insensitive")
    def test_filter_by_type_case_insensitive(self):
        """filter_by_type is case-insensitive."""
        results1 = NGC.filter_by_type("GALAXY")
        results2 = NGC.filter_by_type("galaxy")
        with allure.step(f"GALAXY={len(results1)}, galaxy={len(results2)}"):
            assert len(results1) == len(results2)

    @allure.title("Filter by constellation: Cyg")
    def test_filter_by_constellation(self):
        """filter_by_constellation finds objects in constellation."""
        with allure.step("Filter by constellation 'Cyg'"):
            cyg_objects = NGC.filter_by_constellation("Cyg")
        with allure.step(f"Found {len(cyg_objects)} in Cygnus"):
            assert len(cyg_objects) > 0
            assert all(o.constellation == "Cyg" for o in cyg_objects)

    @allure.title("Filter by magnitude ≤ 5.0")
    def test_filter_by_magnitude(self):
        """filter_by_magnitude finds bright objects."""
        with allure.step("Filter by magnitude ≤ 5.0"):
            bright = NGC.filter_by_magnitude(5.0)
        with allure.step(f"Found {len(bright)} bright objects"):
            assert len(bright) > 0
            assert all(o.magnitude <= 5.0 for o in bright)

    @allure.title("get_by_messier finds NGC for M31")
    def test_get_by_messier(self):
        """get_by_messier finds NGC object by Messier number."""
        with allure.step("Get NGC for M31"):
            m31_ngc = NGC.get_by_messier(31)
        with allure.step(f"M31 = NGC {m31_ngc.number} ({m31_ngc.name})"):
            assert m31_ngc is not None
            assert m31_ngc.number == 224
            assert "Andromeda" in m31_ngc.name


# ═══════════════════════════════════════════════════════════════════════════════
#  WELL-KNOWN OBJECTS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Well-Known Objects")
class TestWellKnownNGC:
    """Tests for specific well-known NGC objects."""

    @pytest.mark.golden
    @allure.title("NGC 7000 - North America Nebula")
    @allure.description("""
    Verifies NGC 7000 is the North America Nebula in Cygnus.
    Named for its resemblance to the North American continent.
    """)
    def test_ngc7000_north_america(self):
        """NGC 7000 is the North America Nebula."""
        with allure.step("Get NGC 7000"):
            ngc7000 = NGC.get(7000)
        with allure.step(f"Name = {ngc7000.name}"):
            assert "North America" in ngc7000.name
        with allure.step(f"Type = {ngc7000.object_type}"):
            assert ngc7000.object_type == "emission_nebula"
        with allure.step(f"Constellation = {ngc7000.constellation}"):
            assert ngc7000.constellation == "Cyg"

    @pytest.mark.golden
    @allure.title("NGC 224 = M31 Andromeda")
    @allure.description("""
    Verifies NGC 224 is M31 the Andromeda Galaxy.
    Cross-reference between NGC and Messier catalogs.
    """)
    def test_ngc224_is_m31(self):
        """NGC 224 is M31 Andromeda Galaxy."""
        with allure.step("Get NGC 224"):
            ngc224 = NGC.get(224)
        with allure.step(f"Name = {ngc224.name}"):
            assert "Andromeda" in ngc224.name
        with allure.step(f"Type = {ngc224.object_type}"):
            assert ngc224.object_type == "galaxy"
        with allure.step(f"Messier = M{ngc224.messier_number}"):
            assert ngc224.messier_number == 31

    @pytest.mark.golden
    @allure.title("NGC 869 - Double Cluster (h Persei)")
    @allure.description("""
    Verifies NGC 869 is h Persei, part of the famous Double Cluster
    in Perseus visible to naked eye.
    """)
    def test_ngc869_double_cluster(self):
        """NGC 869 is h Persei (Double Cluster)."""
        with allure.step("Get NGC 869"):
            ngc869 = NGC.get(869)
        with allure.step(f"Name = {ngc869.name}"):
            assert "Persei" in ngc869.name or "h Per" in ngc869.name
        with allure.step(f"Type = {ngc869.object_type}"):
            assert ngc869.object_type == "open_cluster"
        with allure.step(f"Constellation = {ngc869.constellation}"):
            assert ngc869.constellation == "Per"


# ═══════════════════════════════════════════════════════════════════════════════
#  COORDINATES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Coordinates")
class TestNGCCoordinates:
    """Tests for NGC coordinate functions."""

    @allure.title("ngc_coords returns ICRSCoord")
    def test_ngc_coords_returns_icrs(self):
        """ngc_coords returns ICRSCoord."""
        from starward.core.coords import ICRSCoord
        with allure.step("Get coords for NGC 7000"):
            coords = ngc_coords(7000)
        with allure.step(f"Type = {type(coords).__name__}"):
            assert isinstance(coords, ICRSCoord)

    @allure.title("NGC 7000 coordinates: RA ~20h59m, Dec ~+44°")
    def test_ngc7000_coordinates(self):
        """NGC 7000 coordinates are approximately correct."""
        with allure.step("Get NGC 7000 coordinates"):
            coords = ngc_coords(7000)
        with allure.step(f"RA = {coords.ra.hours:.2f}h (expected 20-22)"):
            assert 20.0 < coords.ra.hours < 22.0
        with allure.step(f"Dec = {coords.dec.degrees:.1f}° (expected 43-46)"):
            assert 43.0 < coords.dec.degrees < 46.0

    @allure.title("NGC 224 coordinates: RA ~00h42m, Dec ~+41°")
    def test_ngc224_coordinates(self):
        """NGC 224 (M31) coordinates are approximately correct."""
        with allure.step("Get NGC 224 coordinates"):
            coords = ngc_coords(224)
        with allure.step(f"RA = {coords.ra.hours:.2f}h (expected 0-1.5)"):
            assert 0.0 < coords.ra.hours < 1.5
        with allure.step(f"Dec = {coords.dec.degrees:.1f}° (expected 40-43)"):
            assert 40.0 < coords.dec.degrees < 43.0


# ═══════════════════════════════════════════════════════════════════════════════
#  VISIBILITY
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Visibility")
class TestNGCVisibility:
    """Tests for NGC visibility calculations."""

    @pytest.fixture
    def greenwich(self):
        """Greenwich Observatory observer."""
        return Observer.from_degrees("Greenwich", 51.4772, -0.0005)

    @pytest.fixture
    def j2000(self):
        """J2000.0 epoch."""
        return JulianDate(2451545.0)

    @allure.title("ngc_altitude returns Angle")
    def test_altitude_returns_angle(self):
        """ngc_altitude returns an Angle."""
        from starward.core.angles import Angle
        observer = Observer.from_degrees("Test", 40.0, -74.0)
        jd = JulianDate(2451545.0)
        with allure.step("Calculate NGC 7000 altitude"):
            alt = ngc_altitude(7000, observer, jd)
        with allure.step(f"Type = {type(alt).__name__}, value = {alt.degrees:.1f}°"):
            assert isinstance(alt, Angle)

    @allure.title("NGC 7000 transit altitude from Greenwich ~83°")
    def test_transit_altitude_reasonable(self, greenwich):
        """Transit altitude is reasonable for location."""
        with allure.step("Calculate NGC 7000 transit altitude from Greenwich"):
            trans_alt = ngc_transit_altitude(7000, greenwich)
        with allure.step(f"Transit altitude = {trans_alt.degrees:.1f}° (expected 78-88)"):
            assert 78.0 < trans_alt.degrees < 88.0


# ═══════════════════════════════════════════════════════════════════════════════
#  CATALOG STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Catalog Statistics")
class TestNGCStats:
    """Tests for NGC catalog statistics."""

    @allure.title("stats() returns dict with expected keys")
    def test_stats_returns_dict(self):
        """stats() returns dictionary with expected keys."""
        with allure.step("Get catalog stats"):
            stats = NGC.stats()
        with allure.step(f"Keys = {list(stats.keys())}"):
            assert isinstance(stats, dict)
            assert 'total' in stats
            assert 'by_type' in stats

    @allure.title("stats total matches len(NGC)")
    def test_stats_total_matches_len(self):
        """stats total matches catalog length."""
        stats = NGC.stats()
        with allure.step(f"stats.total = {stats['total']}, len(NGC) = {len(NGC)}"):
            assert stats['total'] == len(NGC)

    @allure.title("stats by_type is not empty")
    def test_stats_by_type_not_empty(self):
        """stats by_type is not empty."""
        stats = NGC.stats()
        with allure.step(f"Object types = {len(stats['by_type'])}"):
            assert len(stats['by_type']) > 0


# ═══════════════════════════════════════════════════════════════════════════════
#  MESSIER CROSS-REFERENCE
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Messier Cross-Reference")
class TestMessierCrossReference:
    """Tests for Messier-NGC cross-references."""

    @allure.title("M31 = NGC 224")
    def test_m31_has_ngc_number(self):
        """M31 has NGC designation 224."""
        with allure.step("Get NGC for M31"):
            ngc = NGC.get_by_messier(31)
        with allure.step(f"M31 = NGC {ngc.number}"):
            assert ngc is not None
            assert ngc.number == 224

    @allure.title("M42 = NGC 1976")
    def test_m42_has_ngc_number(self):
        """M42 has NGC designation 1976."""
        with allure.step("Get NGC for M42"):
            ngc = NGC.get_by_messier(42)
        with allure.step(f"M42 = NGC {ngc.number}"):
            assert ngc is not None
            assert ngc.number == 1976

    @allure.title("Invalid Messier returns None")
    def test_invalid_messier_returns_none(self):
        """Invalid Messier number returns None."""
        with allure.step("Get NGC for M999"):
            ngc = NGC.get_by_messier(999)
        with allure.step(f"Result = {ngc}"):
            assert ngc is None


# ═══════════════════════════════════════════════════════════════════════════════
#  OBJECT TYPE COVERAGE
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Object Type Coverage")
class TestNGCObjectTypes:
    """Tests for NGC object type coverage."""

    @allure.title("Catalog has galaxies")
    def test_has_galaxies(self):
        """Catalog contains galaxies."""
        galaxies = NGC.filter_by_type("galaxy")
        with allure.step(f"Galaxy count = {len(galaxies)}"):
            assert len(galaxies) > 0

    @allure.title("Catalog has open clusters")
    def test_has_open_clusters(self):
        """Catalog contains open clusters."""
        clusters = NGC.filter_by_type("open_cluster")
        with allure.step(f"Open cluster count = {len(clusters)}"):
            assert len(clusters) > 0

    @allure.title("Catalog has planetary nebulae")
    def test_has_planetary_nebulae(self):
        """Catalog contains planetary nebulae."""
        nebulae = NGC.filter_by_type("planetary_nebula")
        with allure.step(f"Planetary nebula count = {len(nebulae)}"):
            assert len(nebulae) > 0

    @allure.title("Catalog has emission nebulae")
    def test_has_emission_nebulae(self):
        """Catalog contains emission nebulae."""
        nebulae = NGC.filter_by_type("emission_nebula")
        with allure.step(f"Emission nebula count = {len(nebulae)}"):
            assert len(nebulae) > 0
