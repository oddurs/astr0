"""
Cross-catalog object finder.

This module provides unified search across all astronomical catalogs
(NGC, IC, Messier, Caldwell, Hipparcos) with filtering by type,
constellation, magnitude, and other criteria.

Why Multiple Catalogs?
    Astronomical objects have accumulated different designations over centuries:

    - MESSIER (M): 110 objects, best showpieces visible from France
    - NGC: ~7,840 objects, the professional standard since 1888
    - IC: ~5,386 objects, two supplements to NGC (1895, 1908)
    - CALDWELL: 109 objects, southern sky additions to Messier
    - HIPPARCOS: ~118,000 stars with precise positions

    The same object may appear in multiple catalogs:
    - M31 = NGC 224 = Andromeda Galaxy
    - M1 = NGC 1952 = Crab Nebula
    - NGC 869/884 = C14 = Double Cluster

Magnitude System:
    Brightness is measured on a logarithmic scale where LOWER = BRIGHTER.
    Each magnitude step is a factor of ~2.512 in brightness.

    - Sirius (brightest star): -1.46
    - Naked-eye limit: ~6.0
    - Binocular limit: ~10.0
    - Small telescope: ~13.0
    - Large amateur scope: ~15-16

Example:
    >>> from starward.core.finder import find, find_by_type
    >>> results = find("orion", limit=10)
    >>> galaxies = find_by_type("galaxy", max_magnitude=10.0)
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Union

from starward.core.catalog_db import get_catalog_db
from starward.core.ngc import NGC
from starward.core.ngc_types import NGCObject
from starward.core.ic import IC
from starward.core.ic_types import ICObject
from starward.core.caldwell import Caldwell
from starward.core.caldwell_types import CaldwellObject
from starward.core.hipparcos import Hipparcos
from starward.core.hipparcos_types import HIPStar


class CatalogSource(Enum):
    """Catalog source identifier."""
    MESSIER = "messier"
    NGC = "ngc"
    IC = "ic"
    CALDWELL = "caldwell"
    HIPPARCOS = "hipparcos"


class ObjectCategory(Enum):
    """High-level object categories for filtering."""
    GALAXY = "galaxy"
    NEBULA = "nebula"
    CLUSTER = "cluster"
    STAR = "star"
    OTHER = "other"


# Mapping of specific object types to categories
TYPE_TO_CATEGORY = {
    # Galaxies
    "galaxy": ObjectCategory.GALAXY,
    "galaxy_pair": ObjectCategory.GALAXY,
    "galaxy_group": ObjectCategory.GALAXY,
    "galaxy_triple": ObjectCategory.GALAXY,
    # Nebulae
    "planetary_nebula": ObjectCategory.NEBULA,
    "emission_nebula": ObjectCategory.NEBULA,
    "reflection_nebula": ObjectCategory.NEBULA,
    "hii_region": ObjectCategory.NEBULA,
    "supernova_remnant": ObjectCategory.NEBULA,
    "dark_nebula": ObjectCategory.NEBULA,
    # Clusters
    "globular_cluster": ObjectCategory.CLUSTER,
    "open_cluster": ObjectCategory.CLUSTER,
    "star_cluster": ObjectCategory.CLUSTER,
    "cluster_nebula": ObjectCategory.CLUSTER,
    # Stars
    "star": ObjectCategory.STAR,
    "double_star": ObjectCategory.STAR,
    "asterism": ObjectCategory.STAR,
    # Other
    "quasar": ObjectCategory.OTHER,
    "nonexistent": ObjectCategory.OTHER,
    "duplicate": ObjectCategory.OTHER,
    "unknown": ObjectCategory.OTHER,
}

# Category display names
CATEGORY_NAMES = {
    ObjectCategory.GALAXY: "Galaxy",
    ObjectCategory.NEBULA: "Nebula",
    ObjectCategory.CLUSTER: "Cluster",
    ObjectCategory.STAR: "Star",
    ObjectCategory.OTHER: "Other",
}

# Object types within each category
CATEGORY_TYPES = {
    ObjectCategory.GALAXY: ["galaxy", "galaxy_pair", "galaxy_group", "galaxy_triple"],
    ObjectCategory.NEBULA: ["planetary_nebula", "emission_nebula", "reflection_nebula",
                            "hii_region", "supernova_remnant", "dark_nebula"],
    ObjectCategory.CLUSTER: ["globular_cluster", "open_cluster", "star_cluster", "cluster_nebula"],
    ObjectCategory.STAR: ["star", "double_star", "asterism"],
    ObjectCategory.OTHER: ["quasar", "nonexistent", "duplicate", "unknown"],
}


@dataclass
class FinderResult:
    """
    A unified search result from any catalog.

    Provides a common interface for objects from NGC, IC, Messier,
    Caldwell, and Hipparcos catalogs.

    Attributes:
        catalog: Source catalog (NGC, IC, Messier, Caldwell, Hipparcos)
        designation: Primary catalog designation (e.g., "NGC 7000", "HIP 91262")
        name: Common name if available
        object_type: Specific object type (e.g., "galaxy", "planetary_nebula")
        category: High-level category (galaxy, nebula, cluster, star, other)
        ra_hours: Right ascension in decimal hours
        dec_degrees: Declination in decimal degrees
        magnitude: Visual magnitude (may be None)
        constellation: Three-letter IAU constellation abbreviation
        description: Brief description
        cross_refs: List of cross-references to other catalogs
    """
    catalog: CatalogSource
    designation: str
    name: Optional[str]
    object_type: str
    category: ObjectCategory
    ra_hours: float
    dec_degrees: float
    magnitude: Optional[float]
    constellation: str
    description: str
    cross_refs: List[str]

    @property
    def category_name(self) -> str:
        """Get human-readable category name."""
        return CATEGORY_NAMES.get(self.category, "Unknown")

    @property
    def type_name(self) -> str:
        """Get human-readable object type name."""
        return self.object_type.replace("_", " ").title()

    @property
    def display_name(self) -> str:
        """Get display name (common name or designation)."""
        return self.name if self.name else self.designation

    def __str__(self) -> str:
        if self.name:
            return f"{self.designation} ({self.name})"
        return self.designation


def _ngc_to_result(obj: NGCObject) -> FinderResult:
    """Convert NGCObject to FinderResult."""
    cross_refs = []
    if obj.messier_number:
        cross_refs.append(f"M {obj.messier_number}")

    return FinderResult(
        catalog=CatalogSource.NGC,
        designation=f"NGC {obj.number}",
        name=obj.name,
        object_type=obj.object_type,
        category=TYPE_TO_CATEGORY.get(obj.object_type, ObjectCategory.OTHER),
        ra_hours=obj.ra_hours,
        dec_degrees=obj.dec_degrees,
        magnitude=obj.magnitude,
        constellation=obj.constellation,
        description=obj.description,
        cross_refs=cross_refs,
    )


def _ic_to_result(obj: ICObject) -> FinderResult:
    """Convert ICObject to FinderResult."""
    cross_refs = []
    if obj.ngc_number:
        cross_refs.append(f"NGC {obj.ngc_number}")

    return FinderResult(
        catalog=CatalogSource.IC,
        designation=f"IC {obj.number}",
        name=obj.name,
        object_type=obj.object_type,
        category=TYPE_TO_CATEGORY.get(obj.object_type, ObjectCategory.OTHER),
        ra_hours=obj.ra_hours,
        dec_degrees=obj.dec_degrees,
        magnitude=obj.magnitude,
        constellation=obj.constellation,
        description=obj.description,
        cross_refs=cross_refs,
    )


def _caldwell_to_result(obj: CaldwellObject) -> FinderResult:
    """Convert CaldwellObject to FinderResult."""
    cross_refs = []
    if obj.ngc_number:
        cross_refs.append(f"NGC {obj.ngc_number}")
    if obj.ic_number:
        cross_refs.append(f"IC {obj.ic_number}")

    return FinderResult(
        catalog=CatalogSource.CALDWELL,
        designation=f"C {obj.number}",
        name=obj.name,
        object_type=obj.object_type,
        category=TYPE_TO_CATEGORY.get(obj.object_type, ObjectCategory.OTHER),
        ra_hours=obj.ra_hours,
        dec_degrees=obj.dec_degrees,
        magnitude=obj.magnitude,
        constellation=obj.constellation,
        description=obj.description,
        cross_refs=cross_refs,
    )


def _hipparcos_to_result(star: HIPStar) -> FinderResult:
    """Convert HIPStar to FinderResult."""
    cross_refs = []
    if star.bayer:
        cross_refs.append(star.bayer)
    if star.flamsteed:
        cross_refs.append(star.flamsteed)

    # Build description from spectral type
    desc = f"Spectral type {star.spectral_type}" if star.spectral_type else ""

    return FinderResult(
        catalog=CatalogSource.HIPPARCOS,
        designation=f"HIP {star.hip_number}",
        name=star.name,
        object_type="star",
        category=ObjectCategory.STAR,
        ra_hours=star.ra_hours,
        dec_degrees=star.dec_degrees,
        magnitude=star.magnitude,
        constellation=star.constellation,
        description=desc,
        cross_refs=cross_refs,
    )


def find(
    query: str,
    catalogs: Optional[List[CatalogSource]] = None,
    limit: int = 50,
) -> List[FinderResult]:
    """
    Search for objects across all catalogs by name or description.

    Args:
        query: Search string (case-insensitive, matches partial strings)
        catalogs: List of catalogs to search (default: all)
        limit: Maximum total results

    Returns:
        List of FinderResult objects, sorted by magnitude

    Example:
        >>> results = find("orion")
        >>> results = find("nebula", catalogs=[CatalogSource.NGC, CatalogSource.IC])
    """
    if catalogs is None:
        catalogs = list(CatalogSource)

    results: List[FinderResult] = []

    # Search each catalog
    if CatalogSource.NGC in catalogs:
        for obj in NGC.search(query, limit=limit):
            results.append(_ngc_to_result(obj))

    if CatalogSource.IC in catalogs:
        for obj in IC.search(query, limit=limit):
            results.append(_ic_to_result(obj))

    if CatalogSource.CALDWELL in catalogs:
        for obj in Caldwell.search(query, limit=limit):
            results.append(_caldwell_to_result(obj))

    if CatalogSource.HIPPARCOS in catalogs:
        for star in Hipparcos.search(query, limit=limit):
            results.append(_hipparcos_to_result(star))

    # Sort by magnitude (brightest first), None values last
    results.sort(key=lambda r: (r.magnitude is None, r.magnitude or 999))

    return results[:limit]


def find_by_type(
    object_type: str,
    constellation: Optional[str] = None,
    max_magnitude: Optional[float] = None,
    catalogs: Optional[List[CatalogSource]] = None,
    limit: int = 50,
) -> List[FinderResult]:
    """
    Find objects by specific type.

    Args:
        object_type: Object type (e.g., "galaxy", "planetary_nebula", "open_cluster")
        constellation: Filter by constellation (3-letter code)
        max_magnitude: Maximum (faintest) magnitude
        catalogs: Catalogs to search (default: NGC, IC, Caldwell)
        limit: Maximum results

    Returns:
        List of FinderResult objects, sorted by magnitude

    Example:
        >>> galaxies = find_by_type("galaxy", max_magnitude=10.0)
        >>> pn = find_by_type("planetary_nebula", constellation="Cyg")
    """
    if catalogs is None:
        # Stars module doesn't have object_type filtering in the same way
        catalogs = [CatalogSource.NGC, CatalogSource.IC, CatalogSource.CALDWELL]

    results: List[FinderResult] = []
    db = get_catalog_db()

    if CatalogSource.NGC in catalogs:
        filter_kwargs = {"object_type": object_type, "limit": limit}
        if constellation:
            filter_kwargs["constellation"] = constellation
        if max_magnitude is not None:
            filter_kwargs["max_magnitude"] = max_magnitude

        for data in db.filter_ngc(**filter_kwargs):
            obj = NGCObject.from_dict(data)
            results.append(_ngc_to_result(obj))

    if CatalogSource.IC in catalogs:
        filter_kwargs = {"object_type": object_type, "limit": limit}
        if constellation:
            filter_kwargs["constellation"] = constellation
        if max_magnitude is not None:
            filter_kwargs["max_magnitude"] = max_magnitude

        for data in db.filter_ic(**filter_kwargs):
            obj = ICObject.from_dict(data)
            results.append(_ic_to_result(obj))

    if CatalogSource.CALDWELL in catalogs:
        filter_kwargs = {"object_type": object_type, "limit": limit}
        if constellation:
            filter_kwargs["constellation"] = constellation
        if max_magnitude is not None:
            filter_kwargs["max_magnitude"] = max_magnitude

        for data in db.filter_caldwell(**filter_kwargs):
            obj = CaldwellObject.from_dict(data)
            results.append(_caldwell_to_result(obj))

    # Sort by magnitude
    results.sort(key=lambda r: (r.magnitude is None, r.magnitude or 999))

    return results[:limit]


def find_by_category(
    category: Union[ObjectCategory, str],
    constellation: Optional[str] = None,
    max_magnitude: Optional[float] = None,
    catalogs: Optional[List[CatalogSource]] = None,
    limit: int = 50,
) -> List[FinderResult]:
    """
    Find objects by high-level category.

    Args:
        category: Category (galaxy, nebula, cluster, star) or ObjectCategory enum
        constellation: Filter by constellation (3-letter code)
        max_magnitude: Maximum (faintest) magnitude
        catalogs: Catalogs to search
        limit: Maximum results

    Returns:
        List of FinderResult objects, sorted by magnitude

    Example:
        >>> galaxies = find_by_category("galaxy", max_magnitude=10.0)
        >>> nebulae = find_by_category(ObjectCategory.NEBULA, constellation="Cyg")
    """
    # Convert string to enum if needed
    if isinstance(category, str):
        category = ObjectCategory(category.lower())

    # Get all types in this category
    types = CATEGORY_TYPES.get(category, [])

    # For stars, include Hipparcos
    if category == ObjectCategory.STAR:
        if catalogs is None:
            catalogs = list(CatalogSource)
    else:
        if catalogs is None:
            catalogs = [CatalogSource.NGC, CatalogSource.IC, CatalogSource.CALDWELL]

    results: List[FinderResult] = []

    # Search for each type in category
    for obj_type in types:
        type_results = find_by_type(
            obj_type,
            constellation=constellation,
            max_magnitude=max_magnitude,
            catalogs=[c for c in catalogs if c != CatalogSource.HIPPARCOS],
            limit=limit,
        )
        results.extend(type_results)

    # Add Hipparcos stars if searching for stars
    if category == ObjectCategory.STAR and CatalogSource.HIPPARCOS in catalogs:
        db = get_catalog_db()
        filter_kwargs = {"limit": limit}
        if constellation:
            filter_kwargs["constellation"] = constellation
        if max_magnitude is not None:
            filter_kwargs["max_magnitude"] = max_magnitude

        for data in db.filter_hipparcos(**filter_kwargs):
            star = HIPStar.from_dict(data)
            results.append(_hipparcos_to_result(star))

    # Sort by magnitude and limit
    results.sort(key=lambda r: (r.magnitude is None, r.magnitude or 999))

    return results[:limit]


def find_in_constellation(
    constellation: str,
    category: Optional[Union[ObjectCategory, str]] = None,
    max_magnitude: Optional[float] = None,
    catalogs: Optional[List[CatalogSource]] = None,
    limit: int = 50,
) -> List[FinderResult]:
    """
    Find all objects in a constellation.

    Args:
        constellation: Three-letter IAU constellation abbreviation
        category: Optional category filter (galaxy, nebula, cluster, star)
        max_magnitude: Maximum (faintest) magnitude
        catalogs: Catalogs to search (default: all)
        limit: Maximum results

    Returns:
        List of FinderResult objects, sorted by magnitude

    Example:
        >>> orion_objects = find_in_constellation("Ori")
        >>> cyg_nebulae = find_in_constellation("Cyg", category="nebula")
    """
    if category is not None:
        return find_by_category(
            category,
            constellation=constellation,
            max_magnitude=max_magnitude,
            catalogs=catalogs,
            limit=limit,
        )

    if catalogs is None:
        catalogs = list(CatalogSource)

    results: List[FinderResult] = []
    db = get_catalog_db()

    # Search each catalog
    if CatalogSource.NGC in catalogs:
        filter_kwargs = {"constellation": constellation, "limit": limit}
        if max_magnitude is not None:
            filter_kwargs["max_magnitude"] = max_magnitude
        for data in db.filter_ngc(**filter_kwargs):
            results.append(_ngc_to_result(NGCObject.from_dict(data)))

    if CatalogSource.IC in catalogs:
        filter_kwargs = {"constellation": constellation, "limit": limit}
        if max_magnitude is not None:
            filter_kwargs["max_magnitude"] = max_magnitude
        for data in db.filter_ic(**filter_kwargs):
            results.append(_ic_to_result(ICObject.from_dict(data)))

    if CatalogSource.CALDWELL in catalogs:
        filter_kwargs = {"constellation": constellation, "limit": limit}
        if max_magnitude is not None:
            filter_kwargs["max_magnitude"] = max_magnitude
        for data in db.filter_caldwell(**filter_kwargs):
            results.append(_caldwell_to_result(CaldwellObject.from_dict(data)))

    if CatalogSource.HIPPARCOS in catalogs:
        filter_kwargs = {"constellation": constellation, "limit": limit}
        if max_magnitude is not None:
            filter_kwargs["max_magnitude"] = max_magnitude
        for data in db.filter_hipparcos(**filter_kwargs):
            results.append(_hipparcos_to_result(HIPStar.from_dict(data)))

    # Sort by magnitude
    results.sort(key=lambda r: (r.magnitude is None, r.magnitude or 999))

    return results[:limit]


def find_bright(
    max_magnitude: float = 6.0,
    category: Optional[Union[ObjectCategory, str]] = None,
    catalogs: Optional[List[CatalogSource]] = None,
    limit: int = 50,
) -> List[FinderResult]:
    """
    Find bright objects visible to the naked eye or binoculars.

    Args:
        max_magnitude: Maximum magnitude (default 6.0 for naked eye)
        category: Optional category filter
        catalogs: Catalogs to search (default: all)
        limit: Maximum results

    Returns:
        List of FinderResult objects, sorted by magnitude (brightest first)

    Example:
        >>> naked_eye = find_bright(max_magnitude=6.0)
        >>> binocular_galaxies = find_bright(max_magnitude=8.0, category="galaxy")
    """
    if category is not None:
        return find_by_category(
            category,
            max_magnitude=max_magnitude,
            catalogs=catalogs,
            limit=limit,
        )

    if catalogs is None:
        catalogs = list(CatalogSource)

    results: List[FinderResult] = []
    db = get_catalog_db()

    if CatalogSource.NGC in catalogs:
        for data in db.filter_ngc(max_magnitude=max_magnitude, limit=limit):
            results.append(_ngc_to_result(NGCObject.from_dict(data)))

    if CatalogSource.IC in catalogs:
        for data in db.filter_ic(max_magnitude=max_magnitude, limit=limit):
            results.append(_ic_to_result(ICObject.from_dict(data)))

    if CatalogSource.CALDWELL in catalogs:
        for data in db.filter_caldwell(max_magnitude=max_magnitude, limit=limit):
            results.append(_caldwell_to_result(CaldwellObject.from_dict(data)))

    if CatalogSource.HIPPARCOS in catalogs:
        for data in db.filter_hipparcos(max_magnitude=max_magnitude, limit=limit):
            results.append(_hipparcos_to_result(HIPStar.from_dict(data)))

    # Sort by magnitude (brightest first)
    results.sort(key=lambda r: (r.magnitude is None, r.magnitude or 999))

    return results[:limit]
