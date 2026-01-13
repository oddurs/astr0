"""
NGC (New General Catalogue) catalog module.

This module provides access to the NGC catalog of ~7,840 deep sky objects
including galaxies, nebulae, and star clusters.

Example:
    >>> from starward.core.ngc import NGC, ngc_coords
    >>> ngc7000 = NGC.get(7000)
    >>> print(ngc7000.name)
    North America Nebula
    >>> coords = ngc_coords(7000)
    >>> print(coords)
    20h59m00.0s +44d32m00s
"""

from __future__ import annotations

from typing import List, Optional

from starward.core.angles import Angle
from starward.core.catalog_db import get_catalog_db
from starward.core.coords import ICRSCoord
from starward.core.ngc_types import NGCObject, NGC_OBJECT_TYPES
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


class NGCCatalog:
    """
    The NGC (New General Catalogue) of deep sky objects.

    Provides access to ~7,840 NGC objects with methods for
    lookup, searching, and filtering.

    Example:
        >>> from starward.core.ngc import NGC
        >>> ngc7000 = NGC.get(7000)
        >>> print(ngc7000.name)
        North America Nebula

        >>> galaxies = NGC.filter_by_type("galaxy")
        >>> len(galaxies)
        5000+

        >>> results = NGC.search("orion")
        >>> for obj in results:
        ...     print(obj)
    """

    def __init__(self) -> None:
        """Initialize the NGC catalog."""
        self._db = get_catalog_db()

    def get(self, number: int) -> NGCObject:
        """
        Get an NGC object by its catalog number.

        Args:
            number: NGC catalog number (1-7840+)

        Returns:
            NGCObject with all metadata

        Raises:
            KeyError: If the NGC number is not in the catalog

        Example:
            >>> ngc7000 = NGC.get(7000)
            >>> print(ngc7000.name)
            North America Nebula
        """
        data = self._db.get_ngc(number)
        if data is None:
            raise KeyError(f"NGC {number} is not in the catalog")
        return NGCObject.from_dict(data)

    def get_by_messier(self, messier_number: int) -> Optional[NGCObject]:
        """
        Get an NGC object by its Messier cross-reference.

        Args:
            messier_number: Messier catalog number (1-110)

        Returns:
            NGCObject if found, None otherwise

        Example:
            >>> ngc = NGC.get_by_messier(31)  # M31 = NGC 224
            >>> print(ngc.number)
            224
        """
        data = self._db.get_ngc_by_messier(messier_number)
        if data is None:
            return None
        return NGCObject.from_dict(data)

    def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[NGCObject]:
        """
        Get all NGC objects, sorted by catalog number.

        Args:
            limit: Maximum number of objects to return (None for all)
            offset: Number of objects to skip (for pagination)

        Returns:
            List of NGCObject instances

        Example:
            >>> all_objects = NGC.list_all()
            >>> first_100 = NGC.list_all(limit=100)
            >>> next_100 = NGC.list_all(limit=100, offset=100)
        """
        data_list = self._db.list_ngc(limit=limit, offset=offset)
        return [NGCObject.from_dict(d) for d in data_list]

    def search(self, query: str, limit: int = 50) -> List[NGCObject]:
        """
        Search NGC objects by name, type, constellation, or description.

        The search is case-insensitive and matches partial strings.

        Args:
            query: Search string
            limit: Maximum number of results (default 50)

        Returns:
            List of matching NGCObject instances, sorted by number

        Example:
            >>> results = NGC.search("nebula")
            >>> results = NGC.search("orion")
            >>> results = NGC.search("spiral")
        """
        data_list = self._db.search_ngc(query, limit=limit)
        return [NGCObject.from_dict(d) for d in data_list]

    def filter_by_type(self, object_type: str) -> List[NGCObject]:
        """
        Get all NGC objects of a specific type.

        Args:
            object_type: Type from NGC_OBJECT_TYPES (e.g., "galaxy", "planetary_nebula")

        Returns:
            List of matching NGCObject instances

        Example:
            >>> galaxies = NGC.filter_by_type("galaxy")
            >>> planetary = NGC.filter_by_type("planetary_nebula")
        """
        data_list = self._db.filter_ngc(object_type=object_type)
        return [NGCObject.from_dict(d) for d in data_list]

    def filter_by_constellation(self, constellation: str) -> List[NGCObject]:
        """
        Get all NGC objects in a specific constellation.

        Args:
            constellation: Three-letter IAU constellation abbreviation

        Returns:
            List of matching NGCObject instances

        Example:
            >>> cygnus_objects = NGC.filter_by_constellation("Cyg")
            >>> orion_objects = NGC.filter_by_constellation("Ori")
        """
        data_list = self._db.filter_ngc(constellation=constellation)
        return [NGCObject.from_dict(d) for d in data_list]

    def filter_by_magnitude(self, max_magnitude: float) -> List[NGCObject]:
        """
        Get all NGC objects brighter than a given magnitude.

        Args:
            max_magnitude: Maximum (faintest) magnitude to include

        Returns:
            List of matching NGCObject instances

        Example:
            >>> bright_objects = NGC.filter_by_magnitude(8.0)
            >>> visible_objects = NGC.filter_by_magnitude(12.0)
        """
        data_list = self._db.filter_ngc(max_magnitude=max_magnitude)
        return [NGCObject.from_dict(d) for d in data_list]

    def filter_observable(
        self,
        max_magnitude: float = 12.0,
        has_name: bool = False,
        limit: Optional[int] = None,
    ) -> List[NGCObject]:
        """
        Get amateur-observable NGC objects.

        Args:
            max_magnitude: Maximum magnitude to include (default 12.0)
            has_name: Only return objects with common names
            limit: Maximum number of results

        Returns:
            List of matching NGCObject instances

        Example:
            >>> easy_targets = NGC.filter_observable(max_magnitude=10.0, has_name=True)
        """
        data_list = self._db.filter_ngc(
            max_magnitude=max_magnitude,
            has_name=has_name,
            limit=limit,
        )
        return [NGCObject.from_dict(d) for d in data_list]

    def stats(self) -> dict:
        """
        Get statistics about the NGC catalog.

        Returns:
            Dictionary with catalog statistics

        Example:
            >>> stats = NGC.stats()
            >>> print(stats['total'])
            7840
            >>> print(stats['by_type'])
            {'galaxy': 5000, 'open_cluster': 1000, ...}
        """
        return self._db.ngc_stats()

    def __len__(self) -> int:
        """Return the total number of NGC objects."""
        return self._db.count_ngc()

    def __iter__(self):
        """Iterate over all NGC objects."""
        return iter(self.list_all())

    def __contains__(self, number: int) -> bool:
        """Check if an NGC number exists in the catalog."""
        return self._db.get_ngc(number) is not None


# Singleton instance
NGC = NGCCatalog()


# =============================================================================
# Coordinate Functions
# =============================================================================

def ngc_coords(number: int) -> ICRSCoord:
    """
    Get ICRS coordinates for an NGC object.

    Args:
        number: NGC catalog number

    Returns:
        ICRSCoord with RA and Dec

    Raises:
        KeyError: If the NGC number is not in the catalog

    Example:
        >>> coords = ngc_coords(7000)
        >>> print(coords.ra.format_hms())
        20h59m00.0s
    """
    obj = NGC.get(number)
    # Convert RA from hours to degrees (hours * 15 = degrees)
    ra_degrees = obj.ra_hours * 15.0
    return ICRSCoord.from_degrees(ra_degrees, obj.dec_degrees)


# =============================================================================
# Visibility Functions
# =============================================================================

def ngc_altitude(
    number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None,
) -> Angle:
    """
    Calculate the current altitude of an NGC object.

    Args:
        number: NGC catalog number
        observer: Observer location
        jd: Julian Date for calculation (default: now)
        verbose: Optional verbose context for step-by-step output

    Returns:
        Altitude as an Angle

    Example:
        >>> from starward.core.observer import Observer
        >>> obs = Observer.from_degrees("Home", 40.7, -74.0)
        >>> alt = ngc_altitude(7000, obs)
        >>> print(f"{alt.degrees:.1f} degrees")
    """
    if jd is None:
        jd = jd_now()

    coords = ngc_coords(number)
    return target_altitude(coords, observer, jd, verbose=verbose)


def ngc_airmass(
    number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None,
) -> Optional[float]:
    """
    Calculate the airmass for an NGC object.

    Args:
        number: NGC catalog number
        observer: Observer location
        jd: Julian Date for calculation (default: now)
        verbose: Optional verbose context for step-by-step output

    Returns:
        Airmass value, or None if object is below horizon

    Example:
        >>> X = ngc_airmass(7000, observer)
        >>> if X:
        ...     print(f"Airmass: {X:.2f}")
    """
    if jd is None:
        jd = jd_now()

    coords = ngc_coords(number)
    alt = target_altitude(coords, observer, jd, verbose=verbose)
    return airmass(alt, verbose=verbose)


def ngc_rise(
    number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None,
) -> Optional[JulianDate]:
    """
    Calculate when an NGC object rises.

    Args:
        number: NGC catalog number
        observer: Observer location
        jd: Julian Date to start search (default: now)
        verbose: Optional verbose context for step-by-step output

    Returns:
        JulianDate of rise, or None if circumpolar/never rises

    Example:
        >>> rise_time = ngc_rise(7000, observer)
        >>> if rise_time:
        ...     print(rise_time.to_utc())
    """
    if jd is None:
        jd = jd_now()

    coords = ngc_coords(number)
    rise, _ = target_rise_set(coords, observer, jd, verbose=verbose)
    return rise


def ngc_set(
    number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None,
) -> Optional[JulianDate]:
    """
    Calculate when an NGC object sets.

    Args:
        number: NGC catalog number
        observer: Observer location
        jd: Julian Date to start search (default: now)
        verbose: Optional verbose context for step-by-step output

    Returns:
        JulianDate of set, or None if circumpolar/never sets

    Example:
        >>> set_time = ngc_set(7000, observer)
        >>> if set_time:
        ...     print(set_time.to_utc())
    """
    if jd is None:
        jd = jd_now()

    coords = ngc_coords(number)
    _, set_time = target_rise_set(coords, observer, jd, verbose=verbose)
    return set_time


def ngc_transit(
    number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None,
) -> JulianDate:
    """
    Calculate when an NGC object transits the meridian.

    Args:
        number: NGC catalog number
        observer: Observer location
        jd: Julian Date to start search (default: now)
        verbose: Optional verbose context for step-by-step output

    Returns:
        JulianDate of transit

    Example:
        >>> transit_jd = ngc_transit(7000, observer)
        >>> print(transit_jd.to_utc())
    """
    if jd is None:
        jd = jd_now()

    coords = ngc_coords(number)
    return transit_time(coords, observer, jd, verbose=verbose)


def ngc_transit_altitude(
    number: int,
    observer: Observer,
    verbose: Optional[VerboseContext] = None,
) -> Angle:
    """
    Calculate the maximum altitude an NGC object reaches at transit.

    Args:
        number: NGC catalog number
        observer: Observer location
        verbose: Optional verbose context for step-by-step output

    Returns:
        Maximum altitude as an Angle

    Example:
        >>> max_alt = ngc_transit_altitude(7000, observer)
        >>> print(f"Max altitude: {max_alt.degrees:.1f} degrees")
    """
    coords = ngc_coords(number)
    return transit_altitude_calc(coords, observer, verbose=verbose)
