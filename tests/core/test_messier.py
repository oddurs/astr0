"""
Tests for the Messier catalog module.

Tests catalog lookups, searches, filtering, and coordinate calculations.
"""

from __future__ import annotations

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


# =============================================================================
#  CATALOG DATA
# =============================================================================

class TestMessierData:
    """Tests for the Messier data completeness and accuracy."""

    def test_catalog_has_110_objects(self):
        """Catalog contains all 110 Messier objects."""
        assert len(MESSIER_DATA) == 110

    def test_all_numbers_present(self):
        """All Messier numbers from 1 to 110 are present."""
        for i in range(1, 111):
            assert i in MESSIER_DATA, f"M{i} missing from catalog"

    def test_messier_object_is_frozen(self):
        """MessierObject is immutable."""
        obj = MESSIER.get(1)
        with pytest.raises(AttributeError):
            obj.name = "Modified"

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


# =============================================================================
#  CATALOG CLASS
# =============================================================================

class TestMessierCatalog:
    """Tests for the MessierCatalog class."""

    def test_singleton_instance(self):
        """MESSIER is the singleton catalog instance."""
        assert isinstance(MESSIER, MessierCatalog)

    def test_get_returns_correct_object(self):
        """get() returns the correct Messier object."""
        m31 = MESSIER.get(31)
        assert m31.number == 31
        assert "Andromeda" in m31.name

    def test_get_invalid_number_raises(self):
        """get() raises KeyError for invalid number."""
        with pytest.raises(KeyError):
            MESSIER.get(0)
        with pytest.raises(KeyError):
            MESSIER.get(111)
        with pytest.raises(KeyError):
            MESSIER.get(999)

    def test_list_all_returns_all_objects(self):
        """list_all() returns all 110 objects."""
        objects = MESSIER.list_all()
        assert len(objects) == 110
        assert all(isinstance(o, MessierObject) for o in objects)

    def test_list_all_sorted_by_number(self):
        """list_all() returns objects sorted by number."""
        objects = MESSIER.list_all()
        numbers = [o.number for o in objects]
        assert numbers == list(range(1, 111))

    def test_len_returns_110(self):
        """len(MESSIER) returns 110."""
        assert len(MESSIER) == 110

    def test_iteration(self):
        """Catalog is iterable."""
        count = 0
        for obj in MESSIER:
            assert isinstance(obj, MessierObject)
            count += 1
        assert count == 110


# =============================================================================
#  SEARCH
# =============================================================================

class TestMessierSearch:
    """Tests for searching the Messier catalog."""

    def test_search_by_name(self):
        """Search finds objects by name."""
        results = MESSIER.search("Andromeda")
        assert len(results) >= 1
        assert any(o.number == 31 for o in results)

    def test_search_by_type(self):
        """Search finds objects by type."""
        results = MESSIER.search("galaxy")
        assert len(results) > 30  # Many galaxies in catalog

    def test_search_by_constellation(self):
        """Search finds objects by constellation."""
        results = MESSIER.search("Sgr")
        assert len(results) > 5  # Many objects in Sagittarius

    def test_search_case_insensitive(self):
        """Search is case-insensitive."""
        results1 = MESSIER.search("ORION")
        results2 = MESSIER.search("orion")
        results3 = MESSIER.search("Orion")
        assert len(results1) == len(results2) == len(results3)

    def test_search_by_ngc(self):
        """Search finds objects by NGC designation."""
        results = MESSIER.search("NGC 224")
        assert len(results) >= 1
        assert any(o.number == 31 for o in results)

    def test_search_no_match(self):
        """Search returns empty list for no matches."""
        results = MESSIER.search("xyznonexistent")
        assert len(results) == 0

    def test_search_results_sorted(self):
        """Search results are sorted by Messier number."""
        results = MESSIER.search("galaxy")
        numbers = [o.number for o in results]
        assert numbers == sorted(numbers)


# =============================================================================
#  FILTERS
# =============================================================================

class TestMessierFilters:
    """Tests for filtering Messier objects."""

    def test_filter_by_type_galaxy(self):
        """filter_by_type finds all galaxies."""
        galaxies = MESSIER.filter_by_type("galaxy")
        assert len(galaxies) > 30
        assert all(o.object_type == "galaxy" for o in galaxies)

    def test_filter_by_type_globular(self):
        """filter_by_type finds globular clusters."""
        globulars = MESSIER.filter_by_type("globular_cluster")
        assert len(globulars) > 20
        # M13 Hercules Globular should be in there
        assert any(o.number == 13 for o in globulars)

    def test_filter_by_type_case_insensitive(self):
        """filter_by_type is case-insensitive."""
        results1 = MESSIER.filter_by_type("GALAXY")
        results2 = MESSIER.filter_by_type("galaxy")
        assert len(results1) == len(results2)

    def test_filter_by_constellation(self):
        """filter_by_constellation finds objects in constellation."""
        virgo = MESSIER.filter_by_constellation("Vir")
        assert len(virgo) > 10  # Many Virgo Cluster galaxies

    def test_filter_by_magnitude(self):
        """filter_by_magnitude finds bright objects."""
        bright = MESSIER.filter_by_magnitude(5.0)
        assert len(bright) > 5
        assert all(o.magnitude <= 5.0 for o in bright)
        # Pleiades (M45) should be very bright
        assert any(o.number == 45 for o in bright)


# =============================================================================
#  WELL-KNOWN OBJECTS
# =============================================================================

class TestWellKnownObjects:
    """Tests for specific well-known Messier objects."""

    @pytest.mark.golden
    def test_m1_crab_nebula(self):
        """M1 is the Crab Nebula supernova remnant."""
        m1 = MESSIER.get(1)
        assert "Crab" in m1.name
        assert m1.object_type == "supernova_remnant"
        assert m1.constellation == "Tau"

    @pytest.mark.golden
    def test_m31_andromeda(self):
        """M31 is the Andromeda Galaxy."""
        m31 = MESSIER.get(31)
        assert "Andromeda" in m31.name
        assert m31.object_type == "galaxy"
        assert m31.constellation == "And"
        # Magnitude around 3.4
        assert 3.0 < m31.magnitude < 4.0

    @pytest.mark.golden
    def test_m42_orion_nebula(self):
        """M42 is the Orion Nebula."""
        m42 = MESSIER.get(42)
        assert "Orion" in m42.name
        assert m42.object_type == "emission_nebula"
        assert m42.constellation == "Ori"

    @pytest.mark.golden
    def test_m45_pleiades(self):
        """M45 is the Pleiades open cluster."""
        m45 = MESSIER.get(45)
        assert "Pleiades" in m45.name
        assert m45.object_type == "open_cluster"
        assert m45.constellation == "Tau"
        # Very bright
        assert m45.magnitude < 2.0

    @pytest.mark.golden
    def test_m57_ring_nebula(self):
        """M57 is the Ring Nebula."""
        m57 = MESSIER.get(57)
        assert "Ring" in m57.name
        assert m57.object_type == "planetary_nebula"
        assert m57.constellation == "Lyr"

    @pytest.mark.golden
    def test_m104_sombrero(self):
        """M104 is the Sombrero Galaxy."""
        m104 = MESSIER.get(104)
        assert "Sombrero" in m104.name
        assert m104.object_type == "galaxy"


# =============================================================================
#  COORDINATES
# =============================================================================

class TestMessierCoordinates:
    """Tests for Messier coordinate functions."""

    def test_messier_coords_returns_icrs(self):
        """messier_coords returns ICRSCoord."""
        from starward.core.coords import ICRSCoord
        coords = messier_coords(31)
        assert isinstance(coords, ICRSCoord)

    def test_m31_coordinates(self):
        """M31 coordinates are approximately correct."""
        coords = messier_coords(31)
        # M31: RA ~00h 42m, Dec ~+41°
        assert 0.0 < coords.ra.hours < 1.5
        assert 40.0 < coords.dec.degrees < 43.0

    def test_m42_coordinates(self):
        """M42 coordinates are approximately correct."""
        coords = messier_coords(42)
        # M42: RA ~05h 35m, Dec ~-05°
        assert 5.0 < coords.ra.hours < 6.0
        assert -6.0 < coords.dec.degrees < -4.0


# =============================================================================
#  VISIBILITY
# =============================================================================

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

    def test_altitude_returns_angle(self):
        """messier_altitude returns an Angle."""
        from starward.core.angles import Angle
        observer = Observer.from_degrees("Test", 40.0, -74.0)
        jd = JulianDate(2451545.0)
        alt = messier_altitude(31, observer, jd)
        assert isinstance(alt, Angle)

    def test_transit_altitude_reasonable(self, greenwich):
        """Transit altitude is reasonable for location."""
        # M31 at Dec +41° from Greenwich (lat +51°)
        # Transit alt should be ~90° - |51 - 41| = 80°
        trans_alt = messier_transit_altitude(31, greenwich)
        assert 75.0 < trans_alt.degrees < 85.0

    def test_circumpolar_object_high_transit(self):
        """High declination objects have high transit altitude."""
        # From high latitude, M81/M82 (Dec ~+69°) should transit high
        north_observer = Observer.from_degrees("North", 60.0, 0.0)
        trans_alt = messier_transit_altitude(81, north_observer)
        assert trans_alt.degrees > 60.0


# =============================================================================
#  OBJECT TYPE COVERAGE
# =============================================================================

class TestObjectTypeCoverage:
    """Tests to ensure all object types are represented."""

    def test_has_galaxies(self):
        """Catalog contains galaxies."""
        galaxies = MESSIER.filter_by_type("galaxy")
        assert len(galaxies) > 0

    def test_has_globular_clusters(self):
        """Catalog contains globular clusters."""
        clusters = MESSIER.filter_by_type("globular_cluster")
        assert len(clusters) > 0

    def test_has_open_clusters(self):
        """Catalog contains open clusters."""
        clusters = MESSIER.filter_by_type("open_cluster")
        assert len(clusters) > 0

    def test_has_planetary_nebulae(self):
        """Catalog contains planetary nebulae."""
        nebulae = MESSIER.filter_by_type("planetary_nebula")
        assert len(nebulae) > 0

    def test_has_emission_nebulae(self):
        """Catalog contains emission nebulae."""
        nebulae = MESSIER.filter_by_type("emission_nebula")
        assert len(nebulae) > 0
