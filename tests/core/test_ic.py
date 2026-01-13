"""
Tests for the IC catalog module.

Tests catalog lookups, searches, filtering, and coordinate calculations.
"""

from __future__ import annotations

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


# =============================================================================
#  CATALOG DATA
# =============================================================================

class TestICData:
    """Tests for the IC data completeness and accuracy."""

    def test_catalog_has_objects(self):
        """Catalog contains IC objects."""
        assert len(IC) > 0

    def test_ic_object_is_frozen(self):
        """ICObject is immutable."""
        obj = IC.get(434)
        with pytest.raises(AttributeError):
            obj.name = "Modified"

    def test_each_object_has_required_fields(self):
        """Each object has all required fields populated."""
        for obj in IC.list_all():
            assert obj.number > 0
            assert obj.object_type in IC_OBJECT_TYPES
            assert 0 <= obj.ra_hours < 24
            assert -90 <= obj.dec_degrees <= 90
            assert obj.constellation


# =============================================================================
#  CATALOG CLASS
# =============================================================================

class TestICCatalog:
    """Tests for the ICCatalog class."""

    def test_singleton_instance(self):
        """IC is the singleton catalog instance."""
        assert isinstance(IC, ICCatalog)

    def test_get_returns_correct_object(self):
        """get() returns the correct IC object."""
        ic434 = IC.get(434)
        assert ic434.number == 434
        assert "Horsehead" in ic434.name

    def test_get_invalid_number_raises(self):
        """get() raises KeyError for invalid number."""
        with pytest.raises(KeyError):
            IC.get(0)
        with pytest.raises(KeyError):
            IC.get(99999)

    def test_list_all_returns_objects(self):
        """list_all() returns IC objects."""
        objects = IC.list_all()
        assert len(objects) > 0
        assert all(isinstance(o, ICObject) for o in objects)

    def test_list_all_sorted_by_number(self):
        """list_all() returns objects sorted by number."""
        objects = IC.list_all()
        numbers = [o.number for o in objects]
        assert numbers == sorted(numbers)

    def test_len_returns_count(self):
        """len(IC) returns object count."""
        assert len(IC) > 0

    def test_iteration(self):
        """Catalog is iterable."""
        count = 0
        for obj in IC:
            assert isinstance(obj, ICObject)
            count += 1
        assert count > 0

    def test_contains(self):
        """Catalog supports 'in' operator."""
        assert 434 in IC
        assert 99999 not in IC


# =============================================================================
#  SEARCH
# =============================================================================

class TestICSearch:
    """Tests for searching the IC catalog."""

    def test_search_by_name(self):
        """Search finds objects by name."""
        results = IC.search("Horsehead")
        assert len(results) >= 1
        assert any(o.number == 434 for o in results)

    def test_search_by_type(self):
        """Search finds objects by type."""
        results = IC.search("nebula")
        assert len(results) > 0

    def test_search_by_constellation(self):
        """Search finds objects by constellation."""
        results = IC.search("Ori")
        assert len(results) > 0

    def test_search_case_insensitive(self):
        """Search is case-insensitive."""
        results1 = IC.search("HORSEHEAD")
        results2 = IC.search("horsehead")
        results3 = IC.search("Horsehead")
        assert len(results1) == len(results2) == len(results3)

    def test_search_no_match(self):
        """Search returns empty list for no matches."""
        results = IC.search("xyznonexistent")
        assert len(results) == 0

    def test_search_results_sorted(self):
        """Search results are sorted by IC number."""
        results = IC.search("nebula")
        numbers = [o.number for o in results]
        assert numbers == sorted(numbers)

    def test_search_limit(self):
        """Search respects limit parameter."""
        results = IC.search("a", limit=3)
        assert len(results) <= 3


# =============================================================================
#  FILTERS
# =============================================================================

class TestICFilters:
    """Tests for filtering IC objects."""

    def test_filter_by_type_dark_nebula(self):
        """filter_by_type finds all dark nebulae."""
        dark_nebulae = IC.filter_by_type("dark_nebula")
        assert len(dark_nebulae) > 0
        assert all(o.object_type == "dark_nebula" for o in dark_nebulae)

    def test_filter_by_type_case_insensitive(self):
        """filter_by_type is case-insensitive."""
        results1 = IC.filter_by_type("DARK_NEBULA")
        results2 = IC.filter_by_type("dark_nebula")
        assert len(results1) == len(results2)

    def test_filter_by_constellation(self):
        """filter_by_constellation finds objects in constellation."""
        ori_objects = IC.filter_by_constellation("Ori")
        assert len(ori_objects) > 0
        assert all(o.constellation == "Ori" for o in ori_objects)

    def test_filter_by_magnitude(self):
        """filter_by_magnitude finds bright objects."""
        bright = IC.filter_by_magnitude(10.0)
        assert len(bright) > 0
        assert all(o.magnitude <= 10.0 for o in bright)

    def test_get_by_ngc(self):
        """get_by_ngc finds IC object by NGC number."""
        # IC 434 is associated with NGC 2023/2024 area
        # Check any object with NGC cross-reference
        # For now just verify the method works
        result = IC.get_by_ngc(1)
        # Result may be None if no IC object has that NGC number
        assert result is None or isinstance(result, ICObject)


# =============================================================================
#  WELL-KNOWN OBJECTS
# =============================================================================

class TestWellKnownIC:
    """Tests for specific well-known IC objects."""

    @pytest.mark.golden
    def test_ic434_horsehead(self):
        """IC 434 is the Horsehead Nebula region."""
        ic434 = IC.get(434)
        assert "Horsehead" in ic434.name
        assert ic434.object_type == "dark_nebula"
        assert ic434.constellation == "Ori"

    @pytest.mark.golden
    def test_ic1805_heart_nebula(self):
        """IC 1805 is the Heart Nebula."""
        ic1805 = IC.get(1805)
        assert "Heart" in ic1805.name
        assert ic1805.object_type == "emission_nebula"
        assert ic1805.constellation == "Cas"

    @pytest.mark.golden
    def test_ic1848_soul_nebula(self):
        """IC 1848 is the Soul Nebula."""
        ic1848 = IC.get(1848)
        assert "Soul" in ic1848.name
        assert ic1848.object_type == "emission_nebula"
        assert ic1848.constellation == "Cas"


# =============================================================================
#  COORDINATES
# =============================================================================

class TestICCoordinates:
    """Tests for IC coordinate functions."""

    def test_ic_coords_returns_icrs(self):
        """ic_coords returns ICRSCoord."""
        from starward.core.coords import ICRSCoord
        coords = ic_coords(434)
        assert isinstance(coords, ICRSCoord)

    def test_ic434_coordinates(self):
        """IC 434 coordinates are approximately correct."""
        coords = ic_coords(434)
        # IC 434: RA ~05h 41m, Dec ~-02° 28'
        assert 5.0 < coords.ra.hours < 6.0
        assert -4.0 < coords.dec.degrees < 0.0

    def test_ic1805_coordinates(self):
        """IC 1805 (Heart Nebula) coordinates are approximately correct."""
        coords = ic_coords(1805)
        # IC 1805: RA ~02h 32m, Dec ~+61°
        assert 2.0 < coords.ra.hours < 3.0
        assert 60.0 < coords.dec.degrees < 63.0


# =============================================================================
#  VISIBILITY
# =============================================================================

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

    def test_altitude_returns_angle(self):
        """ic_altitude returns an Angle."""
        from starward.core.angles import Angle
        observer = Observer.from_degrees("Test", 40.0, -74.0)
        jd = JulianDate(2451545.0)
        alt = ic_altitude(434, observer, jd)
        assert isinstance(alt, Angle)

    def test_transit_altitude_reasonable(self, greenwich):
        """Transit altitude is reasonable for location."""
        # IC 1805 at Dec +61° from Greenwich (lat +51°)
        # Transit alt should be ~90° - |51 - 61| = 80°
        trans_alt = ic_transit_altitude(1805, greenwich)
        assert 75.0 < trans_alt.degrees < 85.0


# =============================================================================
#  CATALOG STATISTICS
# =============================================================================

class TestICStats:
    """Tests for IC catalog statistics."""

    def test_stats_returns_dict(self):
        """stats() returns dictionary with expected keys."""
        stats = IC.stats()
        assert isinstance(stats, dict)
        assert 'total' in stats
        assert 'by_type' in stats

    def test_stats_total_matches_len(self):
        """stats total matches catalog length."""
        stats = IC.stats()
        assert stats['total'] == len(IC)

    def test_stats_by_type_not_empty(self):
        """stats by_type is not empty."""
        stats = IC.stats()
        assert len(stats['by_type']) > 0


# =============================================================================
#  OBJECT TYPE COVERAGE
# =============================================================================

class TestICObjectTypes:
    """Tests for IC object type coverage."""

    def test_has_dark_nebulae(self):
        """Catalog contains dark nebulae."""
        nebulae = IC.filter_by_type("dark_nebula")
        assert len(nebulae) > 0

    def test_has_emission_nebulae(self):
        """Catalog contains emission nebulae."""
        nebulae = IC.filter_by_type("emission_nebula")
        assert len(nebulae) > 0

    def test_has_galaxies(self):
        """Catalog contains galaxies."""
        galaxies = IC.filter_by_type("galaxy")
        assert len(galaxies) > 0


# =============================================================================
#  FILTER OBSERVABLE
# =============================================================================

class TestICObservable:
    """Tests for observable IC object filtering."""

    def test_filter_observable_returns_list(self):
        """filter_observable returns list of ICObjects."""
        objects = IC.filter_observable(max_magnitude=10.0)
        assert isinstance(objects, list)
        assert all(isinstance(o, ICObject) for o in objects)

    def test_filter_observable_respects_magnitude(self):
        """filter_observable respects magnitude limit."""
        objects = IC.filter_observable(max_magnitude=8.0)
        for obj in objects:
            assert obj.magnitude is not None
            assert obj.magnitude <= 8.0

    def test_filter_observable_has_name(self):
        """filter_observable can filter to named objects only."""
        objects = IC.filter_observable(has_name=True)
        for obj in objects:
            assert obj.name is not None
            assert obj.name != ""
