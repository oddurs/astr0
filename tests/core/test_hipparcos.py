"""
Tests for the Hipparcos star catalog module.

Tests catalog lookups, searches, filtering, and coordinate calculations.
"""

from __future__ import annotations

import pytest

from starward.core.hipparcos import (
    Hipparcos,
    HipparcosCatalog,
    star_coords,
    star_altitude,
    star_transit_altitude,
)
from starward.core.hipparcos_types import HIPStar, SPECTRAL_CLASSES
from starward.core.observer import Observer
from starward.core.time import JulianDate


# =============================================================================
#  CATALOG DATA
# =============================================================================

class TestHipparcosData:
    """Tests for the Hipparcos data completeness and accuracy."""

    def test_catalog_has_stars(self):
        """Catalog contains stars."""
        assert len(Hipparcos) > 0

    def test_hip_star_is_frozen(self):
        """HIPStar is immutable."""
        star = Hipparcos.get(32349)  # Sirius
        with pytest.raises(AttributeError):
            star.name = "Modified"

    def test_each_star_has_required_fields(self):
        """Each star has all required fields populated."""
        for star in Hipparcos.list_all():
            assert star.hip_number > 0
            assert 0 <= star.ra_hours < 24
            assert -90 <= star.dec_degrees <= 90
            assert star.magnitude is not None
            assert star.constellation


# =============================================================================
#  CATALOG CLASS
# =============================================================================

class TestHipparcosCatalog:
    """Tests for the HipparcosCatalog class."""

    def test_singleton_instance(self):
        """Hipparcos is the singleton catalog instance."""
        assert isinstance(Hipparcos, HipparcosCatalog)

    def test_get_returns_correct_star(self):
        """get() returns the correct star."""
        sirius = Hipparcos.get(32349)
        assert sirius.hip_number == 32349
        assert sirius.name == "Sirius"

    def test_get_invalid_number_raises(self):
        """get() raises KeyError for invalid number."""
        with pytest.raises(KeyError):
            Hipparcos.get(0)
        with pytest.raises(KeyError):
            Hipparcos.get(999999)

    def test_get_by_name(self):
        """get_by_name() finds stars by common name."""
        vega = Hipparcos.get_by_name("Vega")
        assert vega is not None
        assert vega.hip_number == 91262

    def test_get_by_name_case_insensitive(self):
        """get_by_name() is case-insensitive."""
        star1 = Hipparcos.get_by_name("SIRIUS")
        star2 = Hipparcos.get_by_name("sirius")
        star3 = Hipparcos.get_by_name("Sirius")
        assert star1 == star2 == star3

    def test_get_by_name_not_found(self):
        """get_by_name() returns None for unknown names."""
        result = Hipparcos.get_by_name("NonexistentStar")
        assert result is None

    def test_get_by_bayer(self):
        """get_by_bayer() finds stars by Bayer designation."""
        betelgeuse = Hipparcos.get_by_bayer("Alpha Orionis")
        assert betelgeuse is not None
        assert betelgeuse.name == "Betelgeuse"

    def test_list_all_returns_stars(self):
        """list_all() returns HIPStar instances."""
        stars = Hipparcos.list_all()
        assert len(stars) > 0
        assert all(isinstance(s, HIPStar) for s in stars)

    def test_list_all_sorted_by_magnitude(self):
        """list_all() returns stars sorted by magnitude by default."""
        stars = Hipparcos.list_all()
        mags = [s.magnitude for s in stars]
        assert mags == sorted(mags)

    def test_len_returns_count(self):
        """len(Hipparcos) returns star count."""
        assert len(Hipparcos) > 0

    def test_iteration(self):
        """Catalog is iterable."""
        count = 0
        for star in Hipparcos:
            assert isinstance(star, HIPStar)
            count += 1
        assert count > 0

    def test_contains(self):
        """Catalog supports 'in' operator."""
        assert 32349 in Hipparcos  # Sirius
        assert 999999 not in Hipparcos


# =============================================================================
#  SEARCH
# =============================================================================

class TestHipparcosSearch:
    """Tests for searching the Hipparcos catalog."""

    def test_search_by_name(self):
        """Search finds stars by name."""
        results = Hipparcos.search("Sirius")
        assert len(results) >= 1
        assert any(s.hip_number == 32349 for s in results)

    def test_search_by_constellation(self):
        """Search finds stars by constellation."""
        results = Hipparcos.search("Ori")
        assert len(results) > 0
        # Search is general text search, just verify we get Orion stars in results
        assert any(s.constellation == "Ori" for s in results)

    def test_search_by_spectral_type(self):
        """Search finds stars by spectral type."""
        results = Hipparcos.search("A0V")
        assert len(results) > 0

    def test_search_case_insensitive(self):
        """Search is case-insensitive."""
        results1 = Hipparcos.search("VEGA")
        results2 = Hipparcos.search("vega")
        results3 = Hipparcos.search("Vega")
        assert len(results1) == len(results2) == len(results3)

    def test_search_no_match(self):
        """Search returns empty list for no matches."""
        results = Hipparcos.search("xyznonexistent")
        assert len(results) == 0

    def test_search_results_sorted_by_magnitude(self):
        """Search results are sorted by magnitude."""
        results = Hipparcos.search("Alpha")
        if len(results) > 1:
            mags = [s.magnitude for s in results]
            assert mags == sorted(mags)

    def test_search_limit(self):
        """Search respects limit parameter."""
        results = Hipparcos.search("a", limit=3)
        assert len(results) <= 3


# =============================================================================
#  FILTERS
# =============================================================================

class TestHipparcosFilters:
    """Tests for filtering Hipparcos stars."""

    def test_filter_by_constellation(self):
        """filter_by_constellation finds stars in constellation."""
        orion_stars = Hipparcos.filter_by_constellation("Ori")
        assert len(orion_stars) > 0
        assert all(s.constellation == "Ori" for s in orion_stars)

    def test_filter_by_magnitude(self):
        """filter_by_magnitude finds bright stars."""
        bright = Hipparcos.filter_by_magnitude(1.0)
        assert len(bright) > 0
        assert all(s.magnitude <= 1.0 for s in bright)

    def test_filter_by_spectral_class(self):
        """filter_by_spectral_class finds stars by spectral type."""
        a_stars = Hipparcos.filter_by_spectral_class("A")
        assert len(a_stars) > 0
        assert all(s.spectral_type and s.spectral_type.startswith("A") for s in a_stars)

    def test_filter_named(self):
        """filter_named returns only named stars."""
        named_stars = Hipparcos.filter_named()
        assert len(named_stars) > 0
        assert all(s.name is not None for s in named_stars)


# =============================================================================
#  WELL-KNOWN STARS
# =============================================================================

class TestWellKnownStars:
    """Tests for specific well-known stars."""

    @pytest.mark.golden
    def test_sirius_brightest_star(self):
        """Sirius is the brightest star (HIP 32349)."""
        sirius = Hipparcos.get(32349)
        assert sirius.name == "Sirius"
        assert sirius.bayer == "Alpha Canis Majoris"
        assert sirius.magnitude < 0  # Brightest
        assert sirius.constellation == "CMa"
        assert sirius.spectral_type == "A1V"

    @pytest.mark.golden
    def test_vega_standard_star(self):
        """Vega is a standard star (HIP 91262)."""
        vega = Hipparcos.get(91262)
        assert vega.name == "Vega"
        assert vega.bayer == "Alpha Lyrae"
        assert vega.spectral_type == "A0V"
        assert vega.constellation == "Lyr"

    @pytest.mark.golden
    def test_polaris_north_star(self):
        """Polaris is near the north celestial pole (HIP 11767)."""
        polaris = Hipparcos.get(11767)
        assert polaris.name == "Polaris"
        assert polaris.bayer == "Alpha Ursae Minoris"
        assert polaris.dec_degrees > 89  # Very close to NCP
        assert polaris.constellation == "UMi"

    @pytest.mark.golden
    def test_betelgeuse_red_supergiant(self):
        """Betelgeuse is a red supergiant (HIP 27989)."""
        betelgeuse = Hipparcos.get(27989)
        assert betelgeuse.name == "Betelgeuse"
        assert "M" in betelgeuse.spectral_type  # M-type (red)
        assert betelgeuse.bv_color > 1.5  # Very red


# =============================================================================
#  COORDINATES
# =============================================================================

class TestHipparcosCoordinates:
    """Tests for Hipparcos coordinate functions."""

    def test_star_coords_returns_icrs(self):
        """star_coords returns ICRSCoord."""
        from starward.core.coords import ICRSCoord
        coords = star_coords(32349)  # Sirius
        assert isinstance(coords, ICRSCoord)

    def test_sirius_coordinates(self):
        """Sirius coordinates are approximately correct."""
        coords = star_coords(32349)
        # Sirius: RA ~06h 45m, Dec ~-16° 43'
        assert 6.0 < coords.ra.hours < 7.0
        assert -18.0 < coords.dec.degrees < -15.0

    def test_polaris_coordinates(self):
        """Polaris coordinates are approximately correct."""
        coords = star_coords(11767)
        # Polaris: RA ~02h 32m, Dec ~+89° 16'
        assert 2.0 < coords.ra.hours < 3.0
        assert coords.dec.degrees > 89  # Very close to pole


# =============================================================================
#  VISIBILITY
# =============================================================================

class TestHipparcosVisibility:
    """Tests for Hipparcos visibility calculations."""

    @pytest.fixture
    def greenwich(self):
        """Greenwich Observatory observer."""
        return Observer.from_degrees("Greenwich", 51.4772, -0.0005)

    @pytest.fixture
    def j2000(self):
        """J2000.0 epoch."""
        return JulianDate(2451545.0)

    def test_altitude_returns_angle(self):
        """star_altitude returns an Angle."""
        from starward.core.angles import Angle
        observer = Observer.from_degrees("Test", 40.0, -74.0)
        jd = JulianDate(2451545.0)
        alt = star_altitude(32349, observer, jd)  # Sirius
        assert isinstance(alt, Angle)

    def test_transit_altitude_reasonable(self, greenwich):
        """Transit altitude is reasonable for location."""
        # Sirius at Dec -16.7° from Greenwich (lat +51.5°)
        # Transit alt should be ~90° - |51.5 - (-16.7)| = 21.8°
        trans_alt = star_transit_altitude(32349, greenwich)
        assert 15.0 < trans_alt.degrees < 30.0

    def test_polaris_transit_from_north(self, greenwich):
        """Polaris transit altitude from Greenwich."""
        # Polaris at Dec ~+89° from Greenwich (lat ~+51.5°)
        # Transit alt = 90° - |lat - dec| = 90° - |51.5 - 89| = 90° - 37.5 = 52.5°
        trans_alt = star_transit_altitude(11767, greenwich)
        assert 50.0 < trans_alt.degrees < 55.0


# =============================================================================
#  CATALOG STATISTICS
# =============================================================================

class TestHipparcosStats:
    """Tests for Hipparcos catalog statistics."""

    def test_stats_returns_dict(self):
        """stats() returns dictionary with expected keys."""
        stats = Hipparcos.stats()
        assert isinstance(stats, dict)
        assert 'total' in stats
        assert 'by_spectral_class' in stats
        assert 'brightest' in stats

    def test_stats_total_matches_len(self):
        """stats total matches catalog length."""
        stats = Hipparcos.stats()
        assert stats['total'] == len(Hipparcos)

    def test_stats_has_brightest_star(self):
        """stats includes brightest star info."""
        stats = Hipparcos.stats()
        brightest = stats.get('brightest')
        assert brightest is not None
        assert 'name' in brightest
        assert 'magnitude' in brightest
        assert brightest['name'] == "Sirius"  # Should be Sirius

    def test_stats_by_spectral_not_empty(self):
        """stats by_spectral_class is not empty."""
        stats = Hipparcos.stats()
        assert len(stats['by_spectral_class']) > 0


# =============================================================================
#  STAR PROPERTIES
# =============================================================================

class TestStarProperties:
    """Tests for HIPStar properties and methods."""

    def test_designation_with_name(self):
        """designation property returns name when available."""
        sirius = Hipparcos.get(32349)
        assert sirius.designation == "Sirius"

    def test_spectral_class_property(self):
        """spectral_class property extracts class letter."""
        sirius = Hipparcos.get(32349)
        assert sirius.spectral_class == "A"

        betelgeuse = Hipparcos.get(27989)
        assert betelgeuse.spectral_class == "M"

    def test_str_representation(self):
        """String representation is readable."""
        sirius = Hipparcos.get(32349)
        str_repr = str(sirius)
        assert "HIP 32349" in str_repr
        assert "Sirius" in str_repr
        assert "-1.46" in str_repr


# =============================================================================
#  SPECTRAL TYPE COVERAGE
# =============================================================================

class TestSpectralTypeCoverage:
    """Tests for spectral type coverage in catalog."""

    def test_has_a_type_stars(self):
        """Catalog contains A-type stars."""
        a_stars = Hipparcos.filter_by_spectral_class("A")
        assert len(a_stars) > 0

    def test_has_b_type_stars(self):
        """Catalog contains B-type stars."""
        b_stars = Hipparcos.filter_by_spectral_class("B")
        assert len(b_stars) > 0

    def test_has_k_type_stars(self):
        """Catalog contains K-type stars."""
        k_stars = Hipparcos.filter_by_spectral_class("K")
        assert len(k_stars) > 0

    def test_has_m_type_stars(self):
        """Catalog contains M-type stars."""
        m_stars = Hipparcos.filter_by_spectral_class("M")
        assert len(m_stars) > 0
