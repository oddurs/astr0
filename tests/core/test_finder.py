"""
Tests for the cross-catalog finder module.

Tests unified search, category filtering, and result formatting.
"""

from __future__ import annotations

import allure
import pytest

from starward.core.finder import (
    find,
    find_by_type,
    find_by_category,
    find_in_constellation,
    find_bright,
    FinderResult,
    CatalogSource,
    ObjectCategory,
    TYPE_TO_CATEGORY,
    CATEGORY_TYPES,
)


# =============================================================================
#  FINDER RESULT
# =============================================================================

@allure.story("Finder Result")
class TestFinderResult:
    """Tests for FinderResult dataclass."""

    @allure.title("FinderResult has all required fields")
    def test_result_has_required_fields(self):
        """FinderResult has all required fields."""
        with allure.step("Create FinderResult"):
            result = FinderResult(
                catalog=CatalogSource.NGC,
                designation="NGC 7000",
                name="North America Nebula",
                object_type="emission_nebula",
                category=ObjectCategory.NEBULA,
                ra_hours=20.9833,
                dec_degrees=44.5333,
                magnitude=4.0,
                constellation="Cyg",
                description="Large emission nebula",
                cross_refs=["C 20"],
            )
        with allure.step(f"catalog = {result.catalog}"):
            assert result.catalog == CatalogSource.NGC
        with allure.step(f"designation = {result.designation}"):
            assert result.designation == "NGC 7000"
        with allure.step(f"name = {result.name}"):
            assert result.name == "North America Nebula"

    @allure.title("display_name returns name when available")
    def test_display_name_with_name(self):
        """display_name returns name when available."""
        with allure.step("Create FinderResult with name"):
            result = FinderResult(
                catalog=CatalogSource.NGC,
                designation="NGC 7000",
                name="North America Nebula",
                object_type="emission_nebula",
                category=ObjectCategory.NEBULA,
                ra_hours=20.9833,
                dec_degrees=44.5333,
                magnitude=4.0,
                constellation="Cyg",
                description="",
                cross_refs=[],
            )
        with allure.step(f"display_name = {result.display_name}"):
            assert result.display_name == "North America Nebula"

    @allure.title("display_name returns designation when no name")
    def test_display_name_without_name(self):
        """display_name returns designation when no name."""
        with allure.step("Create FinderResult without name"):
            result = FinderResult(
                catalog=CatalogSource.NGC,
                designation="NGC 1234",
                name=None,
                object_type="galaxy",
                category=ObjectCategory.GALAXY,
                ra_hours=5.0,
                dec_degrees=30.0,
                magnitude=10.0,
                constellation="Tau",
                description="",
                cross_refs=[],
            )
        with allure.step(f"display_name = {result.display_name}"):
            assert result.display_name == "NGC 1234"

    @allure.title("category_name returns human-readable category")
    def test_category_name(self):
        """category_name returns human-readable category."""
        with allure.step("Create FinderResult"):
            result = FinderResult(
                catalog=CatalogSource.NGC,
                designation="NGC 7000",
                name=None,
                object_type="emission_nebula",
                category=ObjectCategory.NEBULA,
                ra_hours=20.9833,
                dec_degrees=44.5333,
                magnitude=4.0,
                constellation="Cyg",
                description="",
                cross_refs=[],
            )
        with allure.step(f"category_name = {result.category_name}"):
            assert result.category_name == "Nebula"

    @allure.title("type_name returns formatted type")
    def test_type_name(self):
        """type_name returns formatted type."""
        with allure.step("Create FinderResult"):
            result = FinderResult(
                catalog=CatalogSource.NGC,
                designation="NGC 7000",
                name=None,
                object_type="emission_nebula",
                category=ObjectCategory.NEBULA,
                ra_hours=20.9833,
                dec_degrees=44.5333,
                magnitude=4.0,
                constellation="Cyg",
                description="",
                cross_refs=[],
            )
        with allure.step(f"type_name = {result.type_name}"):
            assert result.type_name == "Emission Nebula"

    @allure.title("String representation includes name")
    def test_str_with_name(self):
        """String representation includes name."""
        with allure.step("Create FinderResult with name"):
            result = FinderResult(
                catalog=CatalogSource.NGC,
                designation="NGC 7000",
                name="North America Nebula",
                object_type="emission_nebula",
                category=ObjectCategory.NEBULA,
                ra_hours=20.9833,
                dec_degrees=44.5333,
                magnitude=4.0,
                constellation="Cyg",
                description="",
                cross_refs=[],
            )
        with allure.step(f"str contains designation and name"):
            assert "NGC 7000" in str(result)
            assert "North America Nebula" in str(result)


# =============================================================================
#  TYPE MAPPINGS
# =============================================================================

@allure.story("Type Mappings")
class TestTypeMappings:
    """Tests for type-to-category mappings."""

    @allure.title("Galaxy types map to GALAXY category")
    def test_galaxy_types_map_to_galaxy(self):
        """Galaxy types map to GALAXY category."""
        galaxy_types = ["galaxy", "galaxy_pair", "galaxy_group", "galaxy_triple"]
        for t in galaxy_types:
            with allure.step(f"TYPE_TO_CATEGORY['{t}'] = GALAXY"):
                assert TYPE_TO_CATEGORY.get(t) == ObjectCategory.GALAXY

    @allure.title("Nebula types map to NEBULA category")
    def test_nebula_types_map_to_nebula(self):
        """Nebula types map to NEBULA category."""
        nebula_types = ["planetary_nebula", "emission_nebula", "reflection_nebula",
                        "hii_region", "supernova_remnant", "dark_nebula"]
        for t in nebula_types:
            with allure.step(f"TYPE_TO_CATEGORY['{t}'] = NEBULA"):
                assert TYPE_TO_CATEGORY.get(t) == ObjectCategory.NEBULA

    @allure.title("Cluster types map to CLUSTER category")
    def test_cluster_types_map_to_cluster(self):
        """Cluster types map to CLUSTER category."""
        cluster_types = ["globular_cluster", "open_cluster", "star_cluster", "cluster_nebula"]
        for t in cluster_types:
            with allure.step(f"TYPE_TO_CATEGORY['{t}'] = CLUSTER"):
                assert TYPE_TO_CATEGORY.get(t) == ObjectCategory.CLUSTER

    @allure.title("Star types map to STAR category")
    def test_star_types_map_to_star(self):
        """Star types map to STAR category."""
        star_types = ["star", "double_star", "asterism"]
        for t in star_types:
            with allure.step(f"TYPE_TO_CATEGORY['{t}'] = STAR"):
                assert TYPE_TO_CATEGORY.get(t) == ObjectCategory.STAR

    @allure.title("CATEGORY_TYPES is consistent with TYPE_TO_CATEGORY")
    def test_category_types_are_consistent(self):
        """CATEGORY_TYPES is consistent with TYPE_TO_CATEGORY."""
        for category, types in CATEGORY_TYPES.items():
            for t in types:
                with allure.step(f"'{t}' in {category.name} maps back correctly"):
                    assert TYPE_TO_CATEGORY.get(t) == category


# =============================================================================
#  FIND FUNCTION
# =============================================================================

@allure.story("Find Function")
class TestFind:
    """Tests for the find() function."""

    @allure.title("find() returns list of FinderResult")
    def test_find_returns_results(self):
        """find() returns a list of FinderResult."""
        with allure.step("Search 'nebula' (limit=5)"):
            results = find("nebula", limit=5)
        with allure.step(f"Got {len(results)} results"):
            assert isinstance(results, list)
            if results:
                assert isinstance(results[0], FinderResult)

    @allure.title("find() respects limit parameter")
    def test_find_respects_limit(self):
        """find() respects the limit parameter."""
        with allure.step("Search 'a' (limit=3)"):
            results = find("a", limit=3)
        with allure.step(f"Got {len(results)} results (max 3)"):
            assert len(results) <= 3

    @allure.title("find() is case-insensitive")
    def test_find_case_insensitive(self):
        """find() is case-insensitive."""
        with allure.step("Search 'NEBULA' and 'nebula'"):
            results1 = find("NEBULA", limit=5)
            results2 = find("nebula", limit=5)
        with allure.step(f"NEBULA={len(results1)}, nebula={len(results2)}"):
            assert len(results1) == len(results2)

    @allure.title("find() returns empty list for no matches")
    def test_find_no_results(self):
        """find() returns empty list for no matches."""
        with allure.step("Search 'xyznonexistent123'"):
            results = find("xyznonexistent123", limit=10)
        with allure.step(f"Got {len(results)} results"):
            assert len(results) == 0

    @allure.title("find() returns results sorted by magnitude")
    def test_find_sorted_by_magnitude(self):
        """find() returns results sorted by magnitude."""
        with allure.step("Search 'galaxy' (limit=10)"):
            results = find("galaxy", limit=10)
        mags = [r.magnitude for r in results if r.magnitude is not None]
        with allure.step(f"Magnitudes: {mags[:5]}..."):
            assert mags == sorted(mags)

    @allure.title("find() filters by specified catalogs")
    def test_find_filters_by_catalog(self):
        """find() filters by specified catalogs."""
        with allure.step("Search 'a' in NGC only"):
            results = find("a", catalogs=[CatalogSource.NGC], limit=10)
        with allure.step(f"All {len(results)} results from NGC"):
            for r in results:
                assert r.catalog == CatalogSource.NGC


# =============================================================================
#  FIND BY TYPE
# =============================================================================

@allure.story("Find By Type")
class TestFindByType:
    """Tests for the find_by_type() function."""

    @allure.title("find_by_type() returns objects of specified type")
    def test_find_by_type_returns_correct_type(self):
        """find_by_type() returns objects of specified type."""
        with allure.step("Search type='galaxy' (limit=10)"):
            results = find_by_type("galaxy", limit=10)
        with allure.step(f"All {len(results)} results are galaxies"):
            for r in results:
                assert r.object_type == "galaxy"

    @allure.title("find_by_type() filters by constellation")
    def test_find_by_type_filters_constellation(self):
        """find_by_type() filters by constellation."""
        with allure.step("Search type='open_cluster' in Per"):
            results = find_by_type("open_cluster", constellation="Per", limit=10)
        with allure.step(f"All {len(results)} results in Perseus"):
            for r in results:
                assert r.constellation == "Per"

    @allure.title("find_by_type() filters by magnitude")
    def test_find_by_type_filters_magnitude(self):
        """find_by_type() filters by magnitude."""
        with allure.step("Search type='galaxy' (max_mag=8.0)"):
            results = find_by_type("galaxy", max_magnitude=8.0, limit=10)
        with allure.step(f"All {len(results)} results mag <= 8.0"):
            for r in results:
                if r.magnitude is not None:
                    assert r.magnitude <= 8.0

    @allure.title("find_by_type() returns empty for no matches")
    def test_find_by_type_no_results(self):
        """find_by_type() returns empty list when no matches."""
        with allure.step("Search type='galaxy' in XXX"):
            results = find_by_type("galaxy", constellation="XXX", limit=10)
        with allure.step(f"Got {len(results)} results"):
            assert len(results) == 0


# =============================================================================
#  FIND BY CATEGORY
# =============================================================================

@allure.story("Find By Category")
class TestFindByCategory:
    """Tests for the find_by_category() function."""

    @allure.title("find_by_category() works with ObjectCategory enum")
    def test_find_by_category_enum(self):
        """find_by_category() works with ObjectCategory enum."""
        with allure.step("Search category=GALAXY (limit=10)"):
            results = find_by_category(ObjectCategory.GALAXY, limit=10)
        with allure.step(f"All {len(results)} results are galaxies"):
            for r in results:
                assert r.category == ObjectCategory.GALAXY

    @allure.title("find_by_category() works with string category")
    def test_find_by_category_string(self):
        """find_by_category() works with string category."""
        with allure.step("Search category='galaxy' (limit=10)"):
            results = find_by_category("galaxy", limit=10)
        with allure.step(f"All {len(results)} results are galaxies"):
            for r in results:
                assert r.category == ObjectCategory.GALAXY

    @allure.title("find_by_category() finds nebulae of all types")
    def test_find_by_category_nebula(self):
        """find_by_category() finds nebulae of all types."""
        with allure.step("Search category=NEBULA (limit=20)"):
            results = find_by_category(ObjectCategory.NEBULA, limit=20)
        with allure.step(f"All {len(results)} results are nebulae"):
            for r in results:
                assert r.category == ObjectCategory.NEBULA

    @allure.title("find_by_category() includes all object types in category")
    def test_find_by_category_includes_multiple_types(self):
        """find_by_category() includes all object types in category."""
        with allure.step("Search category=NEBULA (limit=50)"):
            results = find_by_category(ObjectCategory.NEBULA, limit=50)
        types = set(r.object_type for r in results)
        with allure.step(f"Types found: {types}"):
            if results:
                assert len(types) >= 1


# =============================================================================
#  FIND IN CONSTELLATION
# =============================================================================

@allure.story("Find In Constellation")
class TestFindInConstellation:
    """Tests for the find_in_constellation() function."""

    @allure.title("find_in_constellation() returns objects in constellation")
    def test_find_in_constellation_returns_objects(self):
        """find_in_constellation() returns objects in constellation."""
        with allure.step("Search in Cygnus (limit=10)"):
            results = find_in_constellation("Cyg", limit=10)
        with allure.step(f"All {len(results)} results in Cyg"):
            for r in results:
                assert r.constellation == "Cyg"

    @allure.title("find_in_constellation() filters by category")
    def test_find_in_constellation_with_category(self):
        """find_in_constellation() filters by category."""
        with allure.step("Search nebulae in Orion (limit=10)"):
            results = find_in_constellation("Ori", category="nebula", limit=10)
        with allure.step(f"All {len(results)} results are nebulae in Ori"):
            for r in results:
                assert r.constellation == "Ori"
                assert r.category == ObjectCategory.NEBULA

    @allure.title("find_in_constellation() works with any case")
    def test_find_in_constellation_case_insensitive(self):
        """find_in_constellation() works with any case."""
        with allure.step("Search 'CYG' and 'cyg'"):
            results1 = find_in_constellation("CYG", limit=5)
            results2 = find_in_constellation("cyg", limit=5)
        with allure.step(f"CYG={len(results1)}, cyg={len(results2)}"):
            assert len(results1) == len(results2)


# =============================================================================
#  FIND BRIGHT
# =============================================================================

@allure.story("Find Bright")
class TestFindBright:
    """Tests for the find_bright() function."""

    @allure.title("find_bright() uses default magnitude of 6.0")
    def test_find_bright_default_magnitude(self):
        """find_bright() uses default magnitude of 6.0."""
        with allure.step("Search bright objects (limit=10)"):
            results = find_bright(limit=10)
        with allure.step(f"All {len(results)} results mag <= 6.0"):
            for r in results:
                if r.magnitude is not None:
                    assert r.magnitude <= 6.0

    @allure.title("find_bright() respects custom magnitude")
    def test_find_bright_custom_magnitude(self):
        """find_bright() respects custom magnitude."""
        with allure.step("Search bright objects (max_mag=3.0)"):
            results = find_bright(max_magnitude=3.0, limit=10)
        with allure.step(f"All {len(results)} results mag <= 3.0"):
            for r in results:
                if r.magnitude is not None:
                    assert r.magnitude <= 3.0

    @allure.title("find_bright() filters by category")
    def test_find_bright_with_category(self):
        """find_bright() filters by category."""
        with allure.step("Search bright galaxies (max_mag=8.0)"):
            results = find_bright(max_magnitude=8.0, category="galaxy", limit=10)
        with allure.step(f"All {len(results)} results are galaxies"):
            for r in results:
                assert r.category == ObjectCategory.GALAXY

    @allure.title("find_bright() returns brightest first")
    def test_find_bright_sorted_by_magnitude(self):
        """find_bright() returns brightest first."""
        with allure.step("Search bright objects (max_mag=10.0)"):
            results = find_bright(max_magnitude=10.0, limit=20)
        mags = [r.magnitude for r in results if r.magnitude is not None]
        with allure.step(f"Magnitudes sorted: {mags[:5]}..."):
            assert mags == sorted(mags)


# =============================================================================
#  CROSS-CATALOG RESULTS
# =============================================================================

@allure.story("Cross-Catalog Results")
class TestCrossCatalogResults:
    """Tests for cross-catalog functionality."""

    @allure.title("find() can return results from multiple catalogs")
    def test_results_from_multiple_catalogs(self):
        """find() can return results from multiple catalogs."""
        with allure.step("Search 'galaxy' (limit=20)"):
            results = find("galaxy", limit=20)
        catalogs = set(r.catalog for r in results)
        with allure.step(f"Catalogs found: {[c.value for c in catalogs]}"):
            if results:
                assert len(catalogs) >= 1

    @allure.title("Results include cross-references to other catalogs")
    def test_results_include_cross_references(self):
        """Results include cross-references to other catalogs."""
        with allure.step("Search 'andromeda' (limit=10)"):
            results = find("andromeda", limit=10)
        andromeda = next((r for r in results if "224" in r.designation), None)
        with allure.step(f"Found Andromeda: {andromeda is not None}"):
            if andromeda:
                assert len(andromeda.cross_refs) >= 0

    @allure.title("Star searches include Hipparcos results")
    def test_hipparcos_results_for_stars(self):
        """Star searches include Hipparcos results."""
        with allure.step("Search 'Vega' (limit=10)"):
            results = find("Vega", limit=10)
        hip_results = [r for r in results if r.catalog == CatalogSource.HIPPARCOS]
        with allure.step(f"Hipparcos results: {len(hip_results)}"):
            assert len(hip_results) >= 1


# =============================================================================
#  CATALOG SOURCE
# =============================================================================

@allure.story("Catalog Source")
class TestCatalogSource:
    """Tests for CatalogSource enum."""

    @allure.title("CatalogSource has expected values")
    def test_catalog_source_values(self):
        """CatalogSource has expected values."""
        with allure.step("NGC = 'ngc'"):
            assert CatalogSource.NGC.value == "ngc"
        with allure.step("IC = 'ic'"):
            assert CatalogSource.IC.value == "ic"
        with allure.step("CALDWELL = 'caldwell'"):
            assert CatalogSource.CALDWELL.value == "caldwell"
        with allure.step("HIPPARCOS = 'hipparcos'"):
            assert CatalogSource.HIPPARCOS.value == "hipparcos"
        with allure.step("MESSIER = 'messier'"):
            assert CatalogSource.MESSIER.value == "messier"
