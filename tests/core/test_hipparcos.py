"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       HIPPARCOS CATALOG TESTS                                ║
║                                                                              ║
║  Tests for the Hipparcos star catalog - bright stars with precise           ║
║  astrometry, names, spectral types, and visibility calculations.            ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

from __future__ import annotations

import allure
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


# ═══════════════════════════════════════════════════════════════════════════════
#  CATALOG DATA
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Catalog Data")
class TestHipparcosData:
    """Tests for the Hipparcos data completeness and accuracy."""

    @allure.title("Catalog has stars")
    def test_catalog_has_stars(self):
        """Catalog contains stars."""
        with allure.step(f"Catalog size = {len(Hipparcos)}"):
            assert len(Hipparcos) > 0

    @allure.title("HIPStar is immutable")
    def test_hip_star_is_frozen(self):
        """HIPStar is immutable."""
        star = Hipparcos.get(32349)  # Sirius
        with allure.step(f"Attempt to modify HIP {star.hip_number}"):
            with pytest.raises(AttributeError):
                star.name = "Modified"

    @allure.title("All stars have required fields")
    def test_each_star_has_required_fields(self):
        """Each star has all required fields populated."""
        for star in Hipparcos.list_all():
            assert star.hip_number > 0
            assert 0 <= star.ra_hours < 24
            assert -90 <= star.dec_degrees <= 90
            assert star.magnitude is not None
            assert star.constellation


# ═══════════════════════════════════════════════════════════════════════════════
#  CATALOG CLASS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Catalog Class")
class TestHipparcosCatalog:
    """Tests for the HipparcosCatalog class."""

    @allure.title("Hipparcos is singleton instance")
    def test_singleton_instance(self):
        """Hipparcos is the singleton catalog instance."""
        with allure.step(f"Type = {type(Hipparcos).__name__}"):
            assert isinstance(Hipparcos, HipparcosCatalog)

    @allure.title("get() returns correct star")
    def test_get_returns_correct_star(self):
        """get() returns the correct star."""
        with allure.step("Get HIP 32349"):
            sirius = Hipparcos.get(32349)
        with allure.step(f"HIP 32349 = {sirius.name}"):
            assert sirius.hip_number == 32349
            assert sirius.name == "Sirius"

    @allure.title("get() raises KeyError for invalid number")
    def test_get_invalid_number_raises(self):
        """get() raises KeyError for number not in catalog."""
        with allure.step("Get HIP 999999"):
            with pytest.raises(KeyError):
                Hipparcos.get(999999)

    @allure.title("get(0) raises ValueError")
    def test_get_zero_raises_value_error(self):
        """get() raises ValueError for zero."""
        with allure.step("Get HIP 0"):
            with pytest.raises(ValueError):
                Hipparcos.get(0)

    @allure.title("get(-1) raises ValueError")
    def test_get_negative_raises_value_error(self):
        """get() raises ValueError for negative numbers."""
        with allure.step("Get HIP -1"):
            with pytest.raises(ValueError):
                Hipparcos.get(-1)

    @allure.title("get() rejects non-integer input")
    def test_get_invalid_type_raises(self):
        """get() raises error for non-integer input."""
        with allure.step("Get 'not a number'"):
            with pytest.raises((ValueError, TypeError)):
                Hipparcos.get("not a number")

    @allure.title("get_by_name finds Vega")
    def test_get_by_name(self):
        """get_by_name() finds stars by common name."""
        with allure.step("Get star by name 'Vega'"):
            vega = Hipparcos.get_by_name("Vega")
        with allure.step(f"Vega = HIP {vega.hip_number}"):
            assert vega is not None
            assert vega.hip_number == 91262

    @allure.title("get_by_name is case-insensitive")
    def test_get_by_name_case_insensitive(self):
        """get_by_name() is case-insensitive."""
        star1 = Hipparcos.get_by_name("SIRIUS")
        star2 = Hipparcos.get_by_name("sirius")
        star3 = Hipparcos.get_by_name("Sirius")
        with allure.step(f"SIRIUS=HIP{star1.hip_number}, sirius=HIP{star2.hip_number}, Sirius=HIP{star3.hip_number}"):
            assert star1 == star2 == star3

    @allure.title("get_by_name returns None for unknown")
    def test_get_by_name_not_found(self):
        """get_by_name() returns None for unknown names."""
        with allure.step("Get 'NonexistentStar'"):
            result = Hipparcos.get_by_name("NonexistentStar")
        with allure.step(f"Result = {result}"):
            assert result is None

    @allure.title("get_by_bayer finds Betelgeuse")
    def test_get_by_bayer(self):
        """get_by_bayer() finds stars by Bayer designation."""
        with allure.step("Get star by Bayer 'Alpha Orionis'"):
            betelgeuse = Hipparcos.get_by_bayer("Alpha Orionis")
        with allure.step(f"Alpha Orionis = {betelgeuse.name}"):
            assert betelgeuse is not None
            assert betelgeuse.name == "Betelgeuse"

    @allure.title("list_all() returns stars")
    def test_list_all_returns_stars(self):
        """list_all() returns HIPStar instances."""
        stars = Hipparcos.list_all()
        with allure.step(f"Count = {len(stars)}"):
            assert len(stars) > 0
            assert all(isinstance(s, HIPStar) for s in stars)

    @allure.title("list_all() sorted by magnitude")
    def test_list_all_sorted_by_magnitude(self):
        """list_all() returns stars sorted by magnitude by default."""
        stars = Hipparcos.list_all()
        mags = [s.magnitude for s in stars]
        with allure.step(f"Brightest = {mags[0]:.2f}, Dimmest = {mags[-1]:.2f}"):
            assert mags == sorted(mags)

    @allure.title("len(Hipparcos) returns count")
    def test_len_returns_count(self):
        """len(Hipparcos) returns star count."""
        with allure.step(f"len = {len(Hipparcos)}"):
            assert len(Hipparcos) > 0

    @allure.title("Catalog is iterable")
    def test_iteration(self):
        """Catalog is iterable."""
        count = 0
        for star in Hipparcos:
            assert isinstance(star, HIPStar)
            count += 1
        with allure.step(f"Iterated over {count} stars"):
            assert count > 0

    @allure.title("Catalog supports 'in' operator")
    def test_contains(self):
        """Catalog supports 'in' operator."""
        with allure.step("32349 in Hipparcos = True (Sirius)"):
            assert 32349 in Hipparcos
        with allure.step("999999 in Hipparcos = False"):
            assert 999999 not in Hipparcos


# ═══════════════════════════════════════════════════════════════════════════════
#  SEARCH
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Search")
class TestHipparcosSearch:
    """Tests for searching the Hipparcos catalog."""

    @allure.title("Search by name: 'Sirius'")
    def test_search_by_name(self):
        """Search finds stars by name."""
        with allure.step("Search 'Sirius'"):
            results = Hipparcos.search("Sirius")
        with allure.step(f"Found {len(results)} result(s), includes HIP 32349 = {any(s.hip_number == 32349 for s in results)}"):
            assert len(results) >= 1
            assert any(s.hip_number == 32349 for s in results)

    @allure.title("Search by constellation: 'Ori'")
    def test_search_by_constellation(self):
        """Search finds stars by constellation."""
        with allure.step("Search 'Ori'"):
            results = Hipparcos.search("Ori")
        with allure.step(f"Found {len(results)} in Orion"):
            assert len(results) > 0
            assert any(s.constellation == "Ori" for s in results)

    @allure.title("Search by spectral type: 'A0V'")
    def test_search_by_spectral_type(self):
        """Search finds stars by spectral type."""
        with allure.step("Search 'A0V'"):
            results = Hipparcos.search("A0V")
        with allure.step(f"Found {len(results)} A0V stars"):
            assert len(results) > 0

    @allure.title("Search is case-insensitive")
    def test_search_case_insensitive(self):
        """Search is case-insensitive."""
        results1 = Hipparcos.search("VEGA")
        results2 = Hipparcos.search("vega")
        results3 = Hipparcos.search("Vega")
        with allure.step(f"VEGA={len(results1)}, vega={len(results2)}, Vega={len(results3)}"):
            assert len(results1) == len(results2) == len(results3)

    @allure.title("Search returns empty for no match")
    def test_search_no_match(self):
        """Search returns empty list for no matches."""
        with allure.step("Search 'xyznonexistent'"):
            results = Hipparcos.search("xyznonexistent")
        with allure.step(f"Results = {len(results)}"):
            assert len(results) == 0

    @allure.title("Search results sorted by magnitude")
    def test_search_results_sorted_by_magnitude(self):
        """Search results are sorted by magnitude."""
        results = Hipparcos.search("Alpha")
        if len(results) > 1:
            mags = [s.magnitude for s in results]
            with allure.step(f"Sorted = {mags == sorted(mags)}"):
                assert mags == sorted(mags)

    @allure.title("Search respects limit parameter")
    def test_search_limit(self):
        """Search respects limit parameter."""
        with allure.step("Search 'a' with limit=3"):
            results = Hipparcos.search("a", limit=3)
        with allure.step(f"Results = {len(results)} (≤ 3)"):
            assert len(results) <= 3


# ═══════════════════════════════════════════════════════════════════════════════
#  FILTERS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Filters")
class TestHipparcosFilters:
    """Tests for filtering Hipparcos stars."""

    @allure.title("Filter by constellation: Ori")
    def test_filter_by_constellation(self):
        """filter_by_constellation finds stars in constellation."""
        with allure.step("Filter by constellation 'Ori'"):
            orion_stars = Hipparcos.filter_by_constellation("Ori")
        with allure.step(f"Found {len(orion_stars)} in Orion"):
            assert len(orion_stars) > 0
            assert all(s.constellation == "Ori" for s in orion_stars)

    @allure.title("Filter by magnitude ≤ 1.0")
    def test_filter_by_magnitude(self):
        """filter_by_magnitude finds bright stars."""
        with allure.step("Filter by magnitude ≤ 1.0"):
            bright = Hipparcos.filter_by_magnitude(1.0)
        with allure.step(f"Found {len(bright)} bright stars"):
            assert len(bright) > 0
            assert all(s.magnitude <= 1.0 for s in bright)

    @allure.title("Filter by spectral class: A")
    def test_filter_by_spectral_class(self):
        """filter_by_spectral_class finds stars by spectral type."""
        with allure.step("Filter by spectral class 'A'"):
            a_stars = Hipparcos.filter_by_spectral_class("A")
        with allure.step(f"Found {len(a_stars)} A-type stars"):
            assert len(a_stars) > 0
            assert all(s.spectral_type and s.spectral_type.startswith("A") for s in a_stars)

    @allure.title("filter_named returns only named stars")
    def test_filter_named(self):
        """filter_named returns only named stars."""
        with allure.step("Filter named stars"):
            named_stars = Hipparcos.filter_named()
        with allure.step(f"Found {len(named_stars)} named stars"):
            assert len(named_stars) > 0
            assert all(s.name is not None for s in named_stars)


# ═══════════════════════════════════════════════════════════════════════════════
#  WELL-KNOWN STARS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Well-Known Stars")
class TestWellKnownStars:
    """Tests for specific well-known stars."""

    @pytest.mark.golden
    @allure.title("Sirius - Brightest star (HIP 32349)")
    @allure.description("""
    Verifies Sirius (Alpha Canis Majoris) is the brightest star.
    A1V spectral type, magnitude -1.46, in Canis Major.
    """)
    def test_sirius_brightest_star(self):
        """Sirius is the brightest star (HIP 32349)."""
        with allure.step("Get HIP 32349"):
            sirius = Hipparcos.get(32349)
        with allure.step(f"Name = {sirius.name}"):
            assert sirius.name == "Sirius"
        with allure.step(f"Bayer = {sirius.bayer}"):
            assert sirius.bayer == "Alpha Canis Majoris"
        with allure.step(f"Magnitude = {sirius.magnitude:.2f} (brightest)"):
            assert sirius.magnitude < 0
        with allure.step(f"Constellation = {sirius.constellation}"):
            assert sirius.constellation == "CMa"
        with allure.step(f"Spectral type = {sirius.spectral_type}"):
            assert sirius.spectral_type == "A1V"

    @pytest.mark.golden
    @allure.title("Vega - Standard star (HIP 91262)")
    @allure.description("""
    Verifies Vega (Alpha Lyrae) as a standard star.
    A0V spectral type used as magnitude zero reference.
    """)
    def test_vega_standard_star(self):
        """Vega is a standard star (HIP 91262)."""
        with allure.step("Get HIP 91262"):
            vega = Hipparcos.get(91262)
        with allure.step(f"Name = {vega.name}"):
            assert vega.name == "Vega"
        with allure.step(f"Bayer = {vega.bayer}"):
            assert vega.bayer == "Alpha Lyrae"
        with allure.step(f"Spectral type = {vega.spectral_type}"):
            assert vega.spectral_type == "A0V"
        with allure.step(f"Constellation = {vega.constellation}"):
            assert vega.constellation == "Lyr"

    @pytest.mark.golden
    @allure.title("Polaris - North Star (HIP 11767)")
    @allure.description("""
    Verifies Polaris (Alpha Ursae Minoris) is near the north celestial pole.
    Dec > 89° makes it circumpolar from most northern latitudes.
    """)
    def test_polaris_north_star(self):
        """Polaris is near the north celestial pole (HIP 11767)."""
        with allure.step("Get HIP 11767"):
            polaris = Hipparcos.get(11767)
        with allure.step(f"Name = {polaris.name}"):
            assert polaris.name == "Polaris"
        with allure.step(f"Bayer = {polaris.bayer}"):
            assert polaris.bayer == "Alpha Ursae Minoris"
        with allure.step(f"Dec = {polaris.dec_degrees:.1f}° (near NCP)"):
            assert polaris.dec_degrees > 89
        with allure.step(f"Constellation = {polaris.constellation}"):
            assert polaris.constellation == "UMi"

    @pytest.mark.golden
    @allure.title("Betelgeuse - Red supergiant (HIP 27989)")
    @allure.description("""
    Verifies Betelgeuse (Alpha Orionis) is a red supergiant.
    M-type spectral class with very red B-V color index.
    """)
    def test_betelgeuse_red_supergiant(self):
        """Betelgeuse is a red supergiant (HIP 27989)."""
        with allure.step("Get HIP 27989"):
            betelgeuse = Hipparcos.get(27989)
        with allure.step(f"Name = {betelgeuse.name}"):
            assert betelgeuse.name == "Betelgeuse"
        with allure.step(f"Spectral type = {betelgeuse.spectral_type} (M-type red)"):
            assert "M" in betelgeuse.spectral_type
        with allure.step(f"B-V color = {betelgeuse.bv_color:.2f} (very red, > 1.5)"):
            assert betelgeuse.bv_color > 1.5


# ═══════════════════════════════════════════════════════════════════════════════
#  COORDINATES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Coordinates")
class TestHipparcosCoordinates:
    """Tests for Hipparcos coordinate functions."""

    @allure.title("star_coords returns ICRSCoord")
    def test_star_coords_returns_icrs(self):
        """star_coords returns ICRSCoord."""
        from starward.core.coords import ICRSCoord
        with allure.step("Get coords for HIP 32349 (Sirius)"):
            coords = star_coords(32349)
        with allure.step(f"Type = {type(coords).__name__}"):
            assert isinstance(coords, ICRSCoord)

    @allure.title("Sirius coordinates: RA ~06h45m, Dec ~-16°43'")
    def test_sirius_coordinates(self):
        """Sirius coordinates are approximately correct."""
        with allure.step("Get Sirius coordinates"):
            coords = star_coords(32349)
        with allure.step(f"RA = {coords.ra.hours:.2f}h (expected 6-7)"):
            assert 6.0 < coords.ra.hours < 7.0
        with allure.step(f"Dec = {coords.dec.degrees:.1f}° (expected -18 to -15)"):
            assert -18.0 < coords.dec.degrees < -15.0

    @allure.title("Polaris coordinates: RA ~02h32m, Dec ~+89°16'")
    def test_polaris_coordinates(self):
        """Polaris coordinates are approximately correct."""
        with allure.step("Get Polaris coordinates"):
            coords = star_coords(11767)
        with allure.step(f"RA = {coords.ra.hours:.2f}h (expected 2-3)"):
            assert 2.0 < coords.ra.hours < 3.0
        with allure.step(f"Dec = {coords.dec.degrees:.1f}° (very close to pole, > 89)"):
            assert coords.dec.degrees > 89


# ═══════════════════════════════════════════════════════════════════════════════
#  VISIBILITY
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Visibility")
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

    @allure.title("star_altitude returns Angle")
    def test_altitude_returns_angle(self):
        """star_altitude returns an Angle."""
        from starward.core.angles import Angle
        observer = Observer.from_degrees("Test", 40.0, -74.0)
        jd = JulianDate(2451545.0)
        with allure.step("Calculate Sirius altitude"):
            alt = star_altitude(32349, observer, jd)
        with allure.step(f"Type = {type(alt).__name__}, value = {alt.degrees:.1f}°"):
            assert isinstance(alt, Angle)

    @allure.title("Sirius transit altitude from Greenwich ~21.8°")
    def test_transit_altitude_reasonable(self, greenwich):
        """Transit altitude is reasonable for location."""
        with allure.step("Calculate Sirius transit altitude from Greenwich"):
            trans_alt = star_transit_altitude(32349, greenwich)
        with allure.step(f"Transit altitude = {trans_alt.degrees:.1f}° (expected 15-30)"):
            assert 15.0 < trans_alt.degrees < 30.0

    @allure.title("Polaris transit altitude from Greenwich ~52.5°")
    def test_polaris_transit_from_north(self, greenwich):
        """Polaris transit altitude from Greenwich."""
        with allure.step("Calculate Polaris transit altitude from Greenwich"):
            trans_alt = star_transit_altitude(11767, greenwich)
        with allure.step(f"Transit altitude = {trans_alt.degrees:.1f}° (expected 50-55)"):
            assert 50.0 < trans_alt.degrees < 55.0


# ═══════════════════════════════════════════════════════════════════════════════
#  CATALOG STATISTICS
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Catalog Statistics")
class TestHipparcosStats:
    """Tests for Hipparcos catalog statistics."""

    @allure.title("stats() returns dict with expected keys")
    def test_stats_returns_dict(self):
        """stats() returns dictionary with expected keys."""
        with allure.step("Get catalog stats"):
            stats = Hipparcos.stats()
        with allure.step(f"Keys = {list(stats.keys())}"):
            assert isinstance(stats, dict)
            assert 'total' in stats
            assert 'by_spectral_class' in stats
            assert 'brightest' in stats

    @allure.title("stats total matches len(Hipparcos)")
    def test_stats_total_matches_len(self):
        """stats total matches catalog length."""
        stats = Hipparcos.stats()
        with allure.step(f"stats.total = {stats['total']}, len(Hipparcos) = {len(Hipparcos)}"):
            assert stats['total'] == len(Hipparcos)

    @allure.title("stats brightest is Sirius")
    def test_stats_has_brightest_star(self):
        """stats includes brightest star info."""
        stats = Hipparcos.stats()
        brightest = stats.get('brightest')
        with allure.step(f"Brightest = {brightest['name']} (mag {brightest['magnitude']})"):
            assert brightest is not None
            assert 'name' in brightest
            assert 'magnitude' in brightest
            assert brightest['name'] == "Sirius"

    @allure.title("stats by_spectral_class is not empty")
    def test_stats_by_spectral_not_empty(self):
        """stats by_spectral_class is not empty."""
        stats = Hipparcos.stats()
        with allure.step(f"Spectral classes = {len(stats['by_spectral_class'])}"):
            assert len(stats['by_spectral_class']) > 0


# ═══════════════════════════════════════════════════════════════════════════════
#  STAR PROPERTIES
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Star Properties")
class TestStarProperties:
    """Tests for HIPStar properties and methods."""

    @allure.title("designation property returns name")
    def test_designation_with_name(self):
        """designation property returns name when available."""
        sirius = Hipparcos.get(32349)
        with allure.step(f"Designation = {sirius.designation}"):
            assert sirius.designation == "Sirius"

    @allure.title("spectral_class extracts class letter")
    def test_spectral_class_property(self):
        """spectral_class property extracts class letter."""
        sirius = Hipparcos.get(32349)
        with allure.step(f"Sirius spectral_class = {sirius.spectral_class}"):
            assert sirius.spectral_class == "A"

        betelgeuse = Hipparcos.get(27989)
        with allure.step(f"Betelgeuse spectral_class = {betelgeuse.spectral_class}"):
            assert betelgeuse.spectral_class == "M"

    @allure.title("String representation is readable")
    def test_str_representation(self):
        """String representation is readable."""
        sirius = Hipparcos.get(32349)
        str_repr = str(sirius)
        with allure.step(f"str = {str_repr[:50]}..."):
            assert "HIP 32349" in str_repr
            assert "Sirius" in str_repr
            assert "-1.46" in str_repr


# ═══════════════════════════════════════════════════════════════════════════════
#  SPECTRAL TYPE COVERAGE
# ═══════════════════════════════════════════════════════════════════════════════

@allure.story("Spectral Type Coverage")
class TestSpectralTypeCoverage:
    """Tests for spectral type coverage in catalog."""

    @allure.title("Catalog has A-type stars")
    def test_has_a_type_stars(self):
        """Catalog contains A-type stars."""
        a_stars = Hipparcos.filter_by_spectral_class("A")
        with allure.step(f"A-type count = {len(a_stars)}"):
            assert len(a_stars) > 0

    @allure.title("Catalog has B-type stars")
    def test_has_b_type_stars(self):
        """Catalog contains B-type stars."""
        b_stars = Hipparcos.filter_by_spectral_class("B")
        with allure.step(f"B-type count = {len(b_stars)}"):
            assert len(b_stars) > 0

    @allure.title("Catalog has K-type stars")
    def test_has_k_type_stars(self):
        """Catalog contains K-type stars."""
        k_stars = Hipparcos.filter_by_spectral_class("K")
        with allure.step(f"K-type count = {len(k_stars)}"):
            assert len(k_stars) > 0

    @allure.title("Catalog has M-type stars")
    def test_has_m_type_stars(self):
        """Catalog contains M-type stars."""
        m_stars = Hipparcos.filter_by_spectral_class("M")
        with allure.step(f"M-type count = {len(m_stars)}"):
            assert len(m_stars) > 0
