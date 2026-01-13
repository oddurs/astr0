"""
Tests for the Caldwell catalog module.

Tests catalog lookups, searches, filtering, and coordinate calculations.
"""

from __future__ import annotations

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


# =============================================================================
#  CATALOG DATA
# =============================================================================

class TestCaldwellData:
    """Tests for the Caldwell data completeness and accuracy."""

    def test_catalog_has_objects(self):
        """Catalog contains objects."""
        assert len(Caldwell) > 0

    def test_caldwell_object_is_frozen(self):
        """CaldwellObject is immutable."""
        obj = Caldwell.get(65)  # Sculptor Galaxy
        with pytest.raises(AttributeError):
            obj.name = "Modified"

    def test_each_object_has_required_fields(self):
        """Each object has all required fields populated."""
        for obj in Caldwell.list_all():
            assert obj.number > 0
            assert 0 <= obj.ra_hours < 24
            assert -90 <= obj.dec_degrees <= 90
            assert obj.constellation


# =============================================================================
#  CATALOG CLASS
# =============================================================================

class TestCaldwellCatalog:
    """Tests for the CaldwellCatalog class."""

    def test_singleton_instance(self):
        """Caldwell is the singleton catalog instance."""
        assert isinstance(Caldwell, CaldwellCatalog)

    def test_get_returns_correct_object(self):
        """get() returns the correct object."""
        obj = Caldwell.get(54)
        assert obj.number == 54
        assert obj.name == "Sculptor Galaxy"

    def test_get_invalid_number_raises(self):
        """get() raises KeyError for invalid number."""
        with pytest.raises(KeyError):
            Caldwell.get(0)
        with pytest.raises(KeyError):
            Caldwell.get(999)

    def test_get_by_ngc(self):
        """get_by_ngc() finds objects by NGC cross-reference."""
        obj = Caldwell.get_by_ngc(253)  # Sculptor Galaxy
        assert obj is not None
        assert obj.number == 54

    def test_get_by_ngc_not_found(self):
        """get_by_ngc() returns None for objects without NGC."""
        result = Caldwell.get_by_ngc(999999)
        assert result is None

    def test_list_all_returns_objects(self):
        """list_all() returns CaldwellObject instances."""
        objects = Caldwell.list_all()
        assert len(objects) > 0
        assert all(isinstance(o, CaldwellObject) for o in objects)

    def test_list_all_sorted_by_number(self):
        """list_all() returns objects sorted by number by default."""
        objects = Caldwell.list_all()
        numbers = [o.number for o in objects]
        assert numbers == sorted(numbers)

    def test_len_returns_count(self):
        """len(Caldwell) returns object count."""
        assert len(Caldwell) > 0
        assert len(Caldwell) == 109

    def test_iteration(self):
        """Catalog is iterable."""
        count = 0
        for obj in Caldwell:
            assert isinstance(obj, CaldwellObject)
            count += 1
        assert count > 0

    def test_contains(self):
        """Catalog supports 'in' operator."""
        assert 65 in Caldwell  # Sculptor Galaxy
        assert 999 not in Caldwell


# =============================================================================
#  SEARCH
# =============================================================================

class TestCaldwellSearch:
    """Tests for searching the Caldwell catalog."""

    def test_search_by_name(self):
        """Search finds objects by name."""
        results = Caldwell.search("Sculptor")
        assert len(results) >= 1
        assert any(o.number == 65 for o in results)

    def test_search_by_constellation(self):
        """Search finds objects by constellation."""
        results = Caldwell.search("Cep")
        assert len(results) > 0
        assert any(o.constellation == "Cep" for o in results)

    def test_search_case_insensitive(self):
        """Search is case-insensitive."""
        results1 = Caldwell.search("SCULPTOR")
        results2 = Caldwell.search("sculptor")
        results3 = Caldwell.search("Sculptor")
        assert len(results1) == len(results2) == len(results3)

    def test_search_no_match(self):
        """Search returns empty list for no matches."""
        results = Caldwell.search("xyznonexistent")
        assert len(results) == 0

    def test_search_limit(self):
        """Search respects limit parameter."""
        results = Caldwell.search("a", limit=3)
        assert len(results) <= 3


# =============================================================================
#  FILTERS
# =============================================================================

class TestCaldwellFilters:
    """Tests for filtering Caldwell objects."""

    def test_filter_by_constellation(self):
        """filter_by_constellation finds objects in constellation."""
        cep_objects = Caldwell.filter_by_constellation("Cep")
        assert len(cep_objects) > 0
        assert all(o.constellation == "Cep" for o in cep_objects)

    def test_filter_by_magnitude(self):
        """filter_by_magnitude finds bright objects."""
        bright = Caldwell.filter_by_magnitude(6.0)
        assert len(bright) > 0
        assert all(o.magnitude <= 6.0 for o in bright if o.magnitude is not None)

    def test_filter_by_type(self):
        """filter_by_type finds objects by type."""
        galaxies = Caldwell.filter_by_type("galaxy")
        assert len(galaxies) > 0
        assert all(o.object_type == "galaxy" for o in galaxies)

    def test_filter_named(self):
        """filter_named returns only named objects."""
        named_objects = Caldwell.filter_named()
        assert len(named_objects) > 0
        assert all(o.name is not None for o in named_objects)


# =============================================================================
#  WELL-KNOWN OBJECTS
# =============================================================================

class TestWellKnownCaldwell:
    """Tests for specific well-known Caldwell objects."""

    @pytest.mark.golden
    def test_c54_sculptor_galaxy(self):
        """C 54 is the Sculptor Galaxy (NGC 253)."""
        obj = Caldwell.get(54)
        assert obj.name == "Sculptor Galaxy"
        assert obj.ngc_number == 253
        assert obj.object_type == "galaxy"
        assert obj.constellation == "Scl"

    @pytest.mark.golden
    def test_c14_double_cluster(self):
        """C 14 is the Double Cluster (NGC 869 + 884)."""
        obj = Caldwell.get(14)
        assert obj.name == "Double Cluster"
        assert obj.ngc_number == 869
        assert obj.object_type == "open_cluster"
        assert obj.constellation == "Per"

    @pytest.mark.golden
    def test_c34_veil_nebula(self):
        """C 34 is the West Veil Nebula (NGC 6960)."""
        obj = Caldwell.get(34)
        assert obj.name == "West Veil Nebula"
        assert obj.ngc_number == 6960
        assert obj.object_type == "supernova_remnant"
        assert obj.constellation == "Cyg"

    @pytest.mark.golden
    def test_c55_saturn_nebula(self):
        """C 55 is the Saturn Nebula (NGC 7009)."""
        obj = Caldwell.get(55)
        assert obj.name == "Saturn Nebula"
        assert obj.ngc_number == 7009
        assert obj.object_type == "planetary_nebula"
        assert obj.constellation == "Aqr"


# =============================================================================
#  COORDINATES
# =============================================================================

class TestCaldwellCoordinates:
    """Tests for Caldwell coordinate functions."""

    def test_caldwell_coords_returns_icrs(self):
        """caldwell_coords returns ICRSCoord."""
        from starward.core.coords import ICRSCoord
        coords = caldwell_coords(54)  # Sculptor Galaxy
        assert isinstance(coords, ICRSCoord)

    def test_sculptor_galaxy_coordinates(self):
        """Sculptor Galaxy coordinates are approximately correct."""
        coords = caldwell_coords(54)
        # Sculptor Galaxy: RA ~00h 47m, Dec ~-25° 17'
        assert 0.0 < coords.ra.hours < 2.0
        assert -30.0 < coords.dec.degrees < -20.0


# =============================================================================
#  VISIBILITY
# =============================================================================

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

    def test_altitude_returns_angle(self):
        """caldwell_altitude returns an Angle."""
        from starward.core.angles import Angle
        observer = Observer.from_degrees("Test", 40.0, -74.0)
        jd = JulianDate(2451545.0)
        alt = caldwell_altitude(54, observer, jd)  # Sculptor Galaxy
        assert isinstance(alt, Angle)

    def test_transit_altitude_reasonable(self, greenwich):
        """Transit altitude is reasonable for location."""
        # Sculptor Galaxy at Dec -25° from Greenwich (lat +51.5°)
        # Transit alt should be ~90° - |51.5 - (-25)| = 13.5°
        trans_alt = caldwell_transit_altitude(54, greenwich)
        assert 10.0 < trans_alt.degrees < 20.0


# =============================================================================
#  CATALOG STATISTICS
# =============================================================================

class TestCaldwellStats:
    """Tests for Caldwell catalog statistics."""

    def test_stats_returns_dict(self):
        """stats() returns dictionary with expected keys."""
        stats = Caldwell.stats()
        assert isinstance(stats, dict)
        assert 'total' in stats
        assert 'by_type' in stats
        assert 'with_ngc_designation' in stats

    def test_stats_total_matches_len(self):
        """stats total matches catalog length."""
        stats = Caldwell.stats()
        assert stats['total'] == len(Caldwell)

    def test_stats_by_type_not_empty(self):
        """stats by_type is not empty."""
        stats = Caldwell.stats()
        assert len(stats['by_type']) > 0


# =============================================================================
#  OBJECT PROPERTIES
# =============================================================================

class TestObjectProperties:
    """Tests for CaldwellObject properties and methods."""

    def test_designation_with_name(self):
        """designation property returns C number."""
        obj = Caldwell.get(54)
        assert obj.designation == "C 54"

    def test_ngc_designation_property(self):
        """ngc_designation property returns NGC number when available."""
        obj = Caldwell.get(54)
        assert obj.ngc_designation == "NGC 253"

    def test_catalog_designations_property(self):
        """catalog_designations returns all designations."""
        obj = Caldwell.get(54)
        designations = obj.catalog_designations
        assert "C 54" in designations
        assert "NGC 253" in designations

    def test_str_representation(self):
        """String representation is readable."""
        obj = Caldwell.get(54)
        str_repr = str(obj)
        assert "C 54" in str_repr
        assert "Sculptor Galaxy" in str_repr
