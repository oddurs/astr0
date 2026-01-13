"""
Caldwell Catalogue module.

This module provides access to the Caldwell Catalogue of 109 deep sky objects
compiled by Sir Patrick Moore to complement the Messier catalog.

Example:
    >>> from starward.core.caldwell import Caldwell, caldwell_coords
    >>> c65 = Caldwell.get(65)
    >>> print(c65.name)
    Sculptor Galaxy
    >>> coords = caldwell_coords(65)
    >>> print(coords)
    00h47m33.1s -25d17m18s
"""

from __future__ import annotations

from typing import List, Optional

from starward.core.angles import Angle
from starward.core.catalog_db import get_catalog_db
from starward.core.coords import ICRSCoord
from starward.core.caldwell_types import CaldwellObject, CALDWELL_OBJECT_TYPES
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


class CaldwellCatalog:
    """
    The Caldwell Catalogue of deep sky objects.

    The Caldwell Catalogue was compiled by Sir Patrick Moore in 1995 to
    complement the Messier catalog. It contains 109 deep sky objects
    visible from both hemispheres that are not in the Messier list.

    Example:
        >>> from starward.core.caldwell import Caldwell
        >>> c65 = Caldwell.get(65)
        >>> print(c65.name)
        Sculptor Galaxy

        >>> galaxies = Caldwell.filter_by_type("galaxy")
        >>> len(galaxies)
        35

        >>> results = Caldwell.search("sculptor")
        >>> for obj in results:
        ...     print(obj)
    """

    def __init__(self) -> None:
        """Initialize the Caldwell catalog."""
        self._db = get_catalog_db()

    def get(self, number: int) -> CaldwellObject:
        """
        Get a Caldwell object by its catalog number.

        Args:
            number: Caldwell catalog number (1-109)

        Returns:
            CaldwellObject with all metadata

        Raises:
            KeyError: If the Caldwell number is not in the catalog

        Example:
            >>> c65 = Caldwell.get(65)
            >>> print(c65.name)
            Sculptor Galaxy
        """
        data = self._db.get_caldwell(number)
        if data is None:
            raise KeyError(f"C {number} is not in the catalog")
        return CaldwellObject.from_dict(data)

    def get_by_ngc(self, ngc_number: int) -> Optional[CaldwellObject]:
        """
        Get a Caldwell object by its NGC cross-reference.

        Args:
            ngc_number: NGC catalog number

        Returns:
            CaldwellObject if found, None otherwise

        Example:
            >>> c = Caldwell.get_by_ngc(253)  # NGC 253 = C 65
            >>> print(c.number)
            65
        """
        data = self._db.get_caldwell_by_ngc(ngc_number)
        if data is None:
            return None
        return CaldwellObject.from_dict(data)

    def get_by_ic(self, ic_number: int) -> Optional[CaldwellObject]:
        """
        Get a Caldwell object by its IC cross-reference.

        Args:
            ic_number: IC catalog number

        Returns:
            CaldwellObject if found, None otherwise

        Example:
            >>> c = Caldwell.get_by_ic(1613)  # IC 1613 = C 51
            >>> print(c.number)
            51
        """
        data = self._db.get_caldwell_by_ic(ic_number)
        if data is None:
            return None
        return CaldwellObject.from_dict(data)

    def list_all(self, limit: Optional[int] = None, offset: int = 0) -> List[CaldwellObject]:
        """
        Get all Caldwell objects, sorted by catalog number.

        Args:
            limit: Maximum number of objects to return (None for all)
            offset: Number of objects to skip (for pagination)

        Returns:
            List of CaldwellObject instances

        Example:
            >>> all_objects = Caldwell.list_all()
            >>> first_10 = Caldwell.list_all(limit=10)
            >>> next_10 = Caldwell.list_all(limit=10, offset=10)
        """
        data_list = self._db.list_caldwell(limit=limit, offset=offset)
        return [CaldwellObject.from_dict(d) for d in data_list]

    def search(self, query: str, limit: int = 50) -> List[CaldwellObject]:
        """
        Search Caldwell objects by name, type, constellation, or description.

        The search is case-insensitive and matches partial strings.

        Args:
            query: Search string
            limit: Maximum number of results (default 50)

        Returns:
            List of matching CaldwellObject instances, sorted by number

        Example:
            >>> results = Caldwell.search("nebula")
            >>> results = Caldwell.search("sculptor")
            >>> results = Caldwell.search("galaxy")
        """
        data_list = self._db.search_caldwell(query, limit=limit)
        return [CaldwellObject.from_dict(d) for d in data_list]

    def filter_by_type(self, object_type: str) -> List[CaldwellObject]:
        """
        Get all Caldwell objects of a specific type.

        Args:
            object_type: Type from CALDWELL_OBJECT_TYPES (e.g., "galaxy", "planetary_nebula")

        Returns:
            List of matching CaldwellObject instances

        Example:
            >>> galaxies = Caldwell.filter_by_type("galaxy")
            >>> planetary = Caldwell.filter_by_type("planetary_nebula")
        """
        data_list = self._db.filter_caldwell(object_type=object_type)
        return [CaldwellObject.from_dict(d) for d in data_list]

    def filter_by_constellation(self, constellation: str) -> List[CaldwellObject]:
        """
        Get all Caldwell objects in a specific constellation.

        Args:
            constellation: Three-letter IAU constellation abbreviation

        Returns:
            List of matching CaldwellObject instances

        Example:
            >>> cygnus_objects = Caldwell.filter_by_constellation("Cyg")
            >>> sculptor_objects = Caldwell.filter_by_constellation("Scl")
        """
        data_list = self._db.filter_caldwell(constellation=constellation)
        return [CaldwellObject.from_dict(d) for d in data_list]

    def filter_by_magnitude(self, max_magnitude: float) -> List[CaldwellObject]:
        """
        Get all Caldwell objects brighter than a given magnitude.

        Args:
            max_magnitude: Maximum (faintest) magnitude to include

        Returns:
            List of matching CaldwellObject instances

        Example:
            >>> bright_objects = Caldwell.filter_by_magnitude(6.0)
            >>> easy_targets = Caldwell.filter_by_magnitude(8.0)
        """
        data_list = self._db.filter_caldwell(max_magnitude=max_magnitude)
        return [CaldwellObject.from_dict(d) for d in data_list]

    def filter_named(self) -> List[CaldwellObject]:
        """
        Get all Caldwell objects that have common names.

        Returns:
            List of CaldwellObject instances with common names

        Example:
            >>> named = Caldwell.filter_named()
            >>> for obj in named:
            ...     print(f"{obj.designation}: {obj.name}")
        """
        data_list = self._db.filter_caldwell(has_name=True)
        return [CaldwellObject.from_dict(d) for d in data_list]

    def stats(self) -> dict:
        """
        Get statistics about the Caldwell catalog.

        Returns:
            Dictionary with catalog statistics

        Example:
            >>> stats = Caldwell.stats()
            >>> print(stats['total'])
            109
            >>> print(stats['by_type'])
            {'galaxy': 35, 'open_cluster': 25, ...}
        """
        return self._db.caldwell_stats()

    def __len__(self) -> int:
        """Return the total number of Caldwell objects."""
        return self._db.count_caldwell()

    def __iter__(self):
        """Iterate over all Caldwell objects."""
        return iter(self.list_all())

    def __contains__(self, number: int) -> bool:
        """Check if a Caldwell number exists in the catalog."""
        return self._db.get_caldwell(number) is not None


# Singleton instance
Caldwell = CaldwellCatalog()


# =============================================================================
# Coordinate Functions
# =============================================================================

def caldwell_coords(number: int) -> ICRSCoord:
    """
    Get ICRS coordinates for a Caldwell object.

    Args:
        number: Caldwell catalog number

    Returns:
        ICRSCoord with RA and Dec

    Raises:
        KeyError: If the Caldwell number is not in the catalog

    Example:
        >>> coords = caldwell_coords(65)
        >>> print(coords.ra.format_hms())
        00h47m33.1s
    """
    obj = Caldwell.get(number)
    # Convert RA from hours to degrees (hours * 15 = degrees)
    ra_degrees = obj.ra_hours * 15.0
    return ICRSCoord.from_degrees(ra_degrees, obj.dec_degrees)


# =============================================================================
# Visibility Functions
# =============================================================================

def caldwell_altitude(
    number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None,
) -> Angle:
    """
    Calculate the current altitude of a Caldwell object.

    Args:
        number: Caldwell catalog number
        observer: Observer location
        jd: Julian Date for calculation (default: now)
        verbose: Optional verbose context for step-by-step output

    Returns:
        Altitude as an Angle

    Example:
        >>> from starward.core.observer import Observer
        >>> obs = Observer.from_degrees("Home", 40.7, -74.0)
        >>> alt = caldwell_altitude(65, obs)
        >>> print(f"{alt.degrees:.1f} degrees")
    """
    if jd is None:
        jd = jd_now()

    coords = caldwell_coords(number)
    return target_altitude(coords, observer, jd, verbose=verbose)


def caldwell_airmass(
    number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None,
) -> Optional[float]:
    """
    Calculate the airmass for a Caldwell object.

    Args:
        number: Caldwell catalog number
        observer: Observer location
        jd: Julian Date for calculation (default: now)
        verbose: Optional verbose context for step-by-step output

    Returns:
        Airmass value, or None if object is below horizon

    Example:
        >>> X = caldwell_airmass(65, observer)
        >>> if X:
        ...     print(f"Airmass: {X:.2f}")
    """
    if jd is None:
        jd = jd_now()

    coords = caldwell_coords(number)
    alt = target_altitude(coords, observer, jd, verbose=verbose)
    return airmass(alt, verbose=verbose)


def caldwell_rise(
    number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None,
) -> Optional[JulianDate]:
    """
    Calculate when a Caldwell object rises.

    Args:
        number: Caldwell catalog number
        observer: Observer location
        jd: Julian Date to start search (default: now)
        verbose: Optional verbose context for step-by-step output

    Returns:
        JulianDate of rise, or None if circumpolar/never rises

    Example:
        >>> rise_time = caldwell_rise(65, observer)
        >>> if rise_time:
        ...     print(rise_time.to_utc())
    """
    if jd is None:
        jd = jd_now()

    coords = caldwell_coords(number)
    rise, _ = target_rise_set(coords, observer, jd, verbose=verbose)
    return rise


def caldwell_set(
    number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None,
) -> Optional[JulianDate]:
    """
    Calculate when a Caldwell object sets.

    Args:
        number: Caldwell catalog number
        observer: Observer location
        jd: Julian Date to start search (default: now)
        verbose: Optional verbose context for step-by-step output

    Returns:
        JulianDate of set, or None if circumpolar/never sets

    Example:
        >>> set_time = caldwell_set(65, observer)
        >>> if set_time:
        ...     print(set_time.to_utc())
    """
    if jd is None:
        jd = jd_now()

    coords = caldwell_coords(number)
    _, set_time = target_rise_set(coords, observer, jd, verbose=verbose)
    return set_time


def caldwell_transit(
    number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None,
) -> JulianDate:
    """
    Calculate when a Caldwell object transits the meridian.

    Args:
        number: Caldwell catalog number
        observer: Observer location
        jd: Julian Date to start search (default: now)
        verbose: Optional verbose context for step-by-step output

    Returns:
        JulianDate of transit

    Example:
        >>> transit_jd = caldwell_transit(65, observer)
        >>> print(transit_jd.to_utc())
    """
    if jd is None:
        jd = jd_now()

    coords = caldwell_coords(number)
    return transit_time(coords, observer, jd, verbose=verbose)


def caldwell_transit_altitude(
    number: int,
    observer: Observer,
    verbose: Optional[VerboseContext] = None,
) -> Angle:
    """
    Calculate the maximum altitude a Caldwell object reaches at transit.

    Args:
        number: Caldwell catalog number
        observer: Observer location
        verbose: Optional verbose context for step-by-step output

    Returns:
        Maximum altitude as an Angle

    Example:
        >>> max_alt = caldwell_transit_altitude(65, observer)
        >>> print(f"Max altitude: {max_alt.degrees:.1f} degrees")
    """
    coords = caldwell_coords(number)
    return transit_altitude_calc(coords, observer, verbose=verbose)
