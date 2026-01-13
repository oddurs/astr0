"""
IC (Index Catalogue) catalog module.

This module provides access to the IC catalog of ~5,386 deep sky objects
including galaxies, nebulae, and star clusters. IC is a supplement to
the NGC catalog.

Example:
    >>> from starward.core.ic import IC, ic_coords
    >>> ic434 = IC.get(434)
    >>> print(ic434.name)
    Horsehead Nebula
    >>> coords = ic_coords(434)
    >>> print(coords)
    05h40m59.88s -02d27m29.88s
"""

from __future__ import annotations

from typing import List, Optional

from starward.core.angles import Angle
from starward.core.catalog_db import get_catalog_db
from starward.core.coords import ICRSCoord
from starward.core.ic_types import ICObject, IC_OBJECT_TYPES
from starward.core.observer import Observer
from starward.core.time import JulianDate, jd_now
from starward.core.visibility import (
    airmass,
    target_altitude,
    target_rise_set,
    transit_altitude_calc,
    transit_time,
)
from starward.verbose import VerboseContext


class ICCatalog:
    """
    The IC (Index Catalogue) of deep sky objects.

    Provides access to ~5,386 IC objects with methods for
    lookup, searching, and filtering.

    Example:
        >>> from starward.core.ic import IC
        >>> ic434 = IC.get(434)
        >>> print(ic434.name)
        Horsehead Nebula

        >>> nebulae = IC.filter_by_type("emission_nebula")
        >>> len(nebulae)
        100+

        >>> results = IC.search("horsehead")
        >>> for obj in results:
        ...     print(obj)
    """

    def __init__(self) -> None:
        """Initialize the IC catalog."""
        self._db = get_catalog_db()

    def get(self, number: int) -> ICObject:
        """
        Get an IC object by its catalog number.

        Args:
            number: IC catalog number (1-5386+)

        Returns:
            ICObject with all metadata

        Raises:
            KeyError: If the IC number is not in the catalog

        Example:
            >>> ic434 = IC.get(434)
            >>> print(ic434.name)
            Horsehead Nebula
        """
        data = self._db.get_ic(number)
        if data is None:
            raise KeyError(f"IC {number} is not in the catalog")
        return ICObject.from_dict(data)

    def get_by_ngc(self, ngc_number: int) -> Optional[ICObject]:
        """
        Get an IC object by its NGC cross-reference.

        Args:
            ngc_number: NGC catalog number

        Returns:
            ICObject if found, None otherwise

        Example:
            >>> ic = IC.get_by_ngc(1234)
            >>> if ic:
            ...     print(ic.number)
        """
        data = self._db.get_ic_by_ngc(ngc_number)
        if data is None:
            return None
        return ICObject.from_dict(data)

    def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[ICObject]:
        """
        Get all IC objects, sorted by catalog number.

        Args:
            limit: Maximum number of objects to return (None for all)
            offset: Number of objects to skip (for pagination)

        Returns:
            List of ICObject instances

        Example:
            >>> all_objects = IC.list_all()
            >>> first_100 = IC.list_all(limit=100)
            >>> next_100 = IC.list_all(limit=100, offset=100)
        """
        data_list = self._db.list_ic(limit=limit, offset=offset)
        return [ICObject.from_dict(d) for d in data_list]

    def search(self, query: str, limit: int = 50) -> List[ICObject]:
        """
        Search IC objects by name, type, constellation, or description.

        The search is case-insensitive and matches partial strings.

        Args:
            query: Search string
            limit: Maximum number of results (default 50)

        Returns:
            List of matching ICObject instances, sorted by number

        Example:
            >>> results = IC.search("nebula")
            >>> results = IC.search("horsehead")
            >>> results = IC.search("galaxy")
        """
        data_list = self._db.search_ic(query, limit=limit)
        return [ICObject.from_dict(d) for d in data_list]

    def filter_by_type(self, object_type: str) -> List[ICObject]:
        """
        Get all IC objects of a specific type.

        Args:
            object_type: Type from IC_OBJECT_TYPES (e.g., "galaxy", "emission_nebula")

        Returns:
            List of matching ICObject instances

        Example:
            >>> galaxies = IC.filter_by_type("galaxy")
            >>> dark_nebulae = IC.filter_by_type("dark_nebula")
        """
        data_list = self._db.filter_ic(object_type=object_type)
        return [ICObject.from_dict(d) for d in data_list]

    def filter_by_constellation(self, constellation: str) -> List[ICObject]:
        """
        Get all IC objects in a specific constellation.

        Args:
            constellation: Three-letter IAU constellation abbreviation

        Returns:
            List of matching ICObject instances

        Example:
            >>> orion_objects = IC.filter_by_constellation("Ori")
            >>> cas_objects = IC.filter_by_constellation("Cas")
        """
        data_list = self._db.filter_ic(constellation=constellation)
        return [ICObject.from_dict(d) for d in data_list]

    def filter_by_magnitude(self, max_magnitude: float) -> List[ICObject]:
        """
        Get all IC objects brighter than a given magnitude.

        Args:
            max_magnitude: Maximum (faintest) magnitude to include

        Returns:
            List of matching ICObject instances

        Example:
            >>> bright_objects = IC.filter_by_magnitude(8.0)
            >>> visible_objects = IC.filter_by_magnitude(12.0)
        """
        data_list = self._db.filter_ic(max_magnitude=max_magnitude)
        return [ICObject.from_dict(d) for d in data_list]

    def filter_observable(
        self,
        max_magnitude: float = 12.0,
        has_name: bool = False,
        limit: Optional[int] = None,
    ) -> List[ICObject]:
        """
        Get amateur-observable IC objects.

        Args:
            max_magnitude: Maximum magnitude to include (default 12.0)
            has_name: Only return objects with common names
            limit: Maximum number of results

        Returns:
            List of matching ICObject instances

        Example:
            >>> easy_targets = IC.filter_observable(max_magnitude=10.0, has_name=True)
        """
        data_list = self._db.filter_ic(
            max_magnitude=max_magnitude,
            has_name=has_name,
            limit=limit,
        )
        return [ICObject.from_dict(d) for d in data_list]

    def stats(self) -> dict:
        """
        Get statistics about the IC catalog.

        Returns:
            Dictionary with catalog statistics

        Example:
            >>> stats = IC.stats()
            >>> print(stats['total'])
            5386
            >>> print(stats['by_type'])
            {'galaxy': 3000, 'emission_nebula': 500, ...}
        """
        return self._db.ic_stats()

    def __len__(self) -> int:
        """Return the total number of IC objects."""
        return self._db.count_ic()

    def __iter__(self):
        """Iterate over all IC objects."""
        return iter(self.list_all())

    def __contains__(self, number: int) -> bool:
        """Check if an IC number exists in the catalog."""
        return self._db.get_ic(number) is not None


# Singleton instance
IC = ICCatalog()


# =============================================================================
# Coordinate Functions
# =============================================================================

def ic_coords(number: int) -> ICRSCoord:
    """
    Get ICRS coordinates for an IC object.

    Args:
        number: IC catalog number

    Returns:
        ICRSCoord with RA and Dec

    Raises:
        KeyError: If the IC number is not in the catalog

    Example:
        >>> coords = ic_coords(434)
        >>> print(coords.ra.format_hms())
        05h40m59.88s
    """
    obj = IC.get(number)
    # Convert RA from hours to degrees (hours * 15 = degrees)
    ra_degrees = obj.ra_hours * 15.0
    return ICRSCoord.from_degrees(ra_degrees, obj.dec_degrees)


# =============================================================================
# Visibility Functions
# =============================================================================

def ic_altitude(
    number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None,
) -> Angle:
    """
    Calculate the current altitude of an IC object.

    Args:
        number: IC catalog number
        observer: Observer location
        jd: Julian Date for calculation (default: now)
        verbose: Optional verbose context for step-by-step output

    Returns:
        Altitude as an Angle

    Example:
        >>> from starward.core.observer import Observer
        >>> obs = Observer.from_degrees("Home", 40.7, -74.0)
        >>> alt = ic_altitude(434, obs)
        >>> print(f"{alt.degrees:.1f} degrees")
    """
    if jd is None:
        jd = jd_now()

    coords = ic_coords(number)
    return target_altitude(coords, observer, jd, verbose=verbose)


def ic_airmass(
    number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None,
) -> Optional[float]:
    """
    Calculate the airmass for an IC object.

    Args:
        number: IC catalog number
        observer: Observer location
        jd: Julian Date for calculation (default: now)
        verbose: Optional verbose context for step-by-step output

    Returns:
        Airmass value, or None if object is below horizon

    Example:
        >>> X = ic_airmass(434, observer)
        >>> if X:
        ...     print(f"Airmass: {X:.2f}")
    """
    if jd is None:
        jd = jd_now()

    coords = ic_coords(number)
    alt = target_altitude(coords, observer, jd, verbose=verbose)
    return airmass(alt, verbose=verbose)


def ic_rise(
    number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None,
) -> Optional[JulianDate]:
    """
    Calculate when an IC object rises.

    Args:
        number: IC catalog number
        observer: Observer location
        jd: Julian Date to start search (default: now)
        verbose: Optional verbose context for step-by-step output

    Returns:
        JulianDate of rise, or None if circumpolar/never rises

    Example:
        >>> rise_time = ic_rise(434, observer)
        >>> if rise_time:
        ...     print(rise_time.to_utc())
    """
    if jd is None:
        jd = jd_now()

    coords = ic_coords(number)
    rise, _ = target_rise_set(coords, observer, jd, verbose=verbose)
    return rise


def ic_set(
    number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None,
) -> Optional[JulianDate]:
    """
    Calculate when an IC object sets.

    Args:
        number: IC catalog number
        observer: Observer location
        jd: Julian Date to start search (default: now)
        verbose: Optional verbose context for step-by-step output

    Returns:
        JulianDate of set, or None if circumpolar/never sets

    Example:
        >>> set_time = ic_set(434, observer)
        >>> if set_time:
        ...     print(set_time.to_utc())
    """
    if jd is None:
        jd = jd_now()

    coords = ic_coords(number)
    _, set_time = target_rise_set(coords, observer, jd, verbose=verbose)
    return set_time


def ic_transit(
    number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None,
) -> JulianDate:
    """
    Calculate when an IC object transits the meridian.

    Args:
        number: IC catalog number
        observer: Observer location
        jd: Julian Date to start search (default: now)
        verbose: Optional verbose context for step-by-step output

    Returns:
        JulianDate of transit

    Example:
        >>> transit_jd = ic_transit(434, observer)
        >>> print(transit_jd.to_utc())
    """
    if jd is None:
        jd = jd_now()

    coords = ic_coords(number)
    return transit_time(coords, observer, jd, verbose=verbose)


def ic_transit_altitude(
    number: int,
    observer: Observer,
    verbose: Optional[VerboseContext] = None,
) -> Angle:
    """
    Calculate the maximum altitude an IC object reaches at transit.

    Args:
        number: IC catalog number
        observer: Observer location
        verbose: Optional verbose context for step-by-step output

    Returns:
        Maximum altitude as an Angle

    Example:
        >>> max_alt = ic_transit_altitude(434, observer)
        >>> print(f"Max altitude: {max_alt.degrees:.1f} degrees")
    """
    coords = ic_coords(number)
    return transit_altitude_calc(coords, observer, verbose=verbose)
