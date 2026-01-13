"""
Tests for the NGC catalog module.

Tests catalog lookups, searches, filtering, and coordinate calculations.
"""

from __future__ import annotations

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


# =============================================================================
#  CATALOG DATA
# =============================================================================

class TestNGCData:
    """Tests for the NGC data completeness and accuracy."""

    def test_catalog_has_objects(self):
        """Catalog contains NGC objects."""
        assert len(NGC) > 0

    def test_ngc_object_is_frozen(self):
        """NGCObject is immutable."""
        obj = NGC.get(7000)
        with pytest.raises(AttributeError):
            obj.name = "Modified"

    def test_each_object_has_required_fields(self):
        """Each object has all required fields populated."""
        for obj in NGC.list_all():
            assert obj.number > 0
            assert obj.object_type in NGC_OBJECT_TYPES
            assert 0 <= obj.ra_hours < 24
            assert -90 <= obj.dec_degrees <= 90
            assert obj.constellation


# =============================================================================
#  CATALOG CLASS
# =============================================================================

class TestNGCCatalog:
    """Tests for the NGCCatalog class."""

    def test_singleton_instance(self):
        """NGC is the singleton catalog instance."""
        assert isinstance(NGC, NGCCatalog)

    def test_get_returns_correct_object(self):
        """get() returns the correct NGC object."""
        ngc7000 = NGC.get(7000)
        assert ngc7000.number == 7000
        assert "North America" in ngc7000.name

    def test_get_invalid_number_raises(self):
        """get() raises KeyError for invalid number."""
        with pytest.raises(KeyError):
            NGC.get(0)
        with pytest.raises(KeyError):
            NGC.get(99999)

    def test_list_all_returns_objects(self):
        """list_all() returns NGC objects."""
        objects = NGC.list_all()
        assert len(objects) > 0
        assert all(isinstance(o, NGCObject) for o in objects)

    def test_list_all_sorted_by_number(self):
        """list_all() returns objects sorted by number."""
        objects = NGC.list_all()
        numbers = [o.number for o in objects]
        assert numbers == sorted(numbers)

    def test_len_returns_count(self):
        """len(NGC) returns object count."""
        assert len(NGC) > 0

    def test_iteration(self):
        """Catalog is iterable."""
        count = 0
        for obj in NGC:
            assert isinstance(obj, NGCObject)
            count += 1
        assert count > 0

    def test_contains(self):
        """Catalog supports 'in' operator."""
        assert 7000 in NGC
        assert 99999 not in NGC


# =============================================================================
#  SEARCH
# =============================================================================

class TestNGCSearch:
    """Tests for searching the NGC catalog."""

    def test_search_by_name(self):
        """Search finds objects by name."""
        results = NGC.search("North America")
        assert len(results) >= 1
        assert any(o.number == 7000 for o in results)

    def test_search_by_type(self):
        """Search finds objects by type."""
        results = NGC.search("nebula")
        assert len(results) > 0

    def test_search_by_constellation(self):
        """Search finds objects by constellation."""
        results = NGC.search("Cyg")
        assert len(results) > 0

    def test_search_case_insensitive(self):
        """Search is case-insensitive."""
        results1 = NGC.search("ORION")
        results2 = NGC.search("orion")
        results3 = NGC.search("Orion")
        assert len(results1) == len(results2) == len(results3)

    def test_search_no_match(self):
        """Search returns empty list for no matches."""
        results = NGC.search("xyznonexistent")
        assert len(results) == 0

    def test_search_results_sorted(self):
        """Search results are sorted by NGC number."""
        results = NGC.search("nebula")
        numbers = [o.number for o in results]
        assert numbers == sorted(numbers)

    def test_search_limit(self):
        """Search respects limit parameter."""
        results = NGC.search("a", limit=3)
        assert len(results) <= 3


# =============================================================================
#  FILTERS
# =============================================================================

class TestNGCFilters:
    """Tests for filtering NGC objects."""

    def test_filter_by_type_galaxy(self):
        """filter_by_type finds all galaxies."""
        galaxies = NGC.filter_by_type("galaxy")
        assert len(galaxies) > 0
        assert all(o.object_type == "galaxy" for o in galaxies)

    def test_filter_by_type_case_insensitive(self):
        """filter_by_type is case-insensitive."""
        results1 = NGC.filter_by_type("GALAXY")
        results2 = NGC.filter_by_type("galaxy")
        assert len(results1) == len(results2)

    def test_filter_by_constellation(self):
        """filter_by_constellation finds objects in constellation."""
        cyg_objects = NGC.filter_by_constellation("Cyg")
        assert len(cyg_objects) > 0
        assert all(o.constellation == "Cyg" for o in cyg_objects)

    def test_filter_by_magnitude(self):
        """filter_by_magnitude finds bright objects."""
        bright = NGC.filter_by_magnitude(5.0)
        assert len(bright) > 0
        assert all(o.magnitude <= 5.0 for o in bright)

    def test_get_by_messier(self):
        """get_by_messier finds NGC object by Messier number."""
        m31_ngc = NGC.get_by_messier(31)
        assert m31_ngc is not None
        assert m31_ngc.number == 224
        assert "Andromeda" in m31_ngc.name


# =============================================================================
#  WELL-KNOWN OBJECTS
# =============================================================================

class TestWellKnownNGC:
    """Tests for specific well-known NGC objects."""

    @pytest.mark.golden
    def test_ngc7000_north_america(self):
        """NGC 7000 is the North America Nebula."""
        ngc7000 = NGC.get(7000)
        assert "North America" in ngc7000.name
        assert ngc7000.object_type == "emission_nebula"
        assert ngc7000.constellation == "Cyg"

    @pytest.mark.golden
    def test_ngc224_is_m31(self):
        """NGC 224 is M31 Andromeda Galaxy."""
        ngc224 = NGC.get(224)
        assert "Andromeda" in ngc224.name
        assert ngc224.object_type == "galaxy"
        assert ngc224.messier_number == 31

    @pytest.mark.golden
    def test_ngc869_double_cluster(self):
        """NGC 869 is h Persei (Double Cluster)."""
        ngc869 = NGC.get(869)
        assert "Persei" in ngc869.name or "h Per" in ngc869.name
        assert ngc869.object_type == "open_cluster"
        assert ngc869.constellation == "Per"


# =============================================================================
#  COORDINATES
# =============================================================================

class TestNGCCoordinates:
    """Tests for NGC coordinate functions."""

    def test_ngc_coords_returns_icrs(self):
        """ngc_coords returns ICRSCoord."""
        from starward.core.coords import ICRSCoord
        coords = ngc_coords(7000)
        assert isinstance(coords, ICRSCoord)

    def test_ngc7000_coordinates(self):
        """NGC 7000 coordinates are approximately correct."""
        coords = ngc_coords(7000)
        # NGC 7000: RA ~20h 59m, Dec ~+44°
        assert 20.0 < coords.ra.hours < 22.0
        assert 43.0 < coords.dec.degrees < 46.0

    def test_ngc224_coordinates(self):
        """NGC 224 (M31) coordinates are approximately correct."""
        coords = ngc_coords(224)
        # NGC 224: RA ~00h 42m, Dec ~+41°
        assert 0.0 < coords.ra.hours < 1.5
        assert 40.0 < coords.dec.degrees < 43.0


# =============================================================================
#  VISIBILITY
# =============================================================================

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

    def test_altitude_returns_angle(self):
        """ngc_altitude returns an Angle."""
        from starward.core.angles import Angle
        observer = Observer.from_degrees("Test", 40.0, -74.0)
        jd = JulianDate(2451545.0)
        alt = ngc_altitude(7000, observer, jd)
        assert isinstance(alt, Angle)

    def test_transit_altitude_reasonable(self, greenwich):
        """Transit altitude is reasonable for location."""
        # NGC 7000 at Dec +44° from Greenwich (lat +51°)
        # Transit alt should be ~90° - |51 - 44| = 83°
        trans_alt = ngc_transit_altitude(7000, greenwich)
        assert 78.0 < trans_alt.degrees < 88.0


# =============================================================================
#  CATALOG STATISTICS
# =============================================================================

class TestNGCStats:
    """Tests for NGC catalog statistics."""

    def test_stats_returns_dict(self):
        """stats() returns dictionary with expected keys."""
        stats = NGC.stats()
        assert isinstance(stats, dict)
        assert 'total' in stats
        assert 'by_type' in stats

    def test_stats_total_matches_len(self):
        """stats total matches catalog length."""
        stats = NGC.stats()
        assert stats['total'] == len(NGC)

    def test_stats_by_type_not_empty(self):
        """stats by_type is not empty."""
        stats = NGC.stats()
        assert len(stats['by_type']) > 0


# =============================================================================
#  MESSIER CROSS-REFERENCE
# =============================================================================

class TestMessierCrossReference:
    """Tests for Messier-NGC cross-references."""

    def test_m31_has_ngc_number(self):
        """M31 has NGC designation 224."""
        ngc = NGC.get_by_messier(31)
        assert ngc is not None
        assert ngc.number == 224

    def test_m42_has_ngc_number(self):
        """M42 has NGC designation 1976."""
        ngc = NGC.get_by_messier(42)
        assert ngc is not None
        assert ngc.number == 1976

    def test_invalid_messier_returns_none(self):
        """Invalid Messier number returns None."""
        ngc = NGC.get_by_messier(999)
        assert ngc is None


# =============================================================================
#  OBJECT TYPE COVERAGE
# =============================================================================

class TestNGCObjectTypes:
    """Tests for NGC object type coverage."""

    def test_has_galaxies(self):
        """Catalog contains galaxies."""
        galaxies = NGC.filter_by_type("galaxy")
        assert len(galaxies) > 0

    def test_has_open_clusters(self):
        """Catalog contains open clusters."""
        clusters = NGC.filter_by_type("open_cluster")
        assert len(clusters) > 0

    def test_has_planetary_nebulae(self):
        """Catalog contains planetary nebulae."""
        nebulae = NGC.filter_by_type("planetary_nebula")
        assert len(nebulae) > 0

    def test_has_emission_nebulae(self):
        """Catalog contains emission nebulae."""
        nebulae = NGC.filter_by_type("emission_nebula")
        assert len(nebulae) > 0
