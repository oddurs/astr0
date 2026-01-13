"""
Messier catalog operations.

Provides access to all 110 Messier objects with coordinates, metadata,
and integration with visibility calculations.
"""

from __future__ import annotations

from typing import List, Optional

from starward.core.angles import Angle
from starward.core.catalog_db import get_catalog_db
from starward.core.coords import ICRSCoord
from starward.core.time import JulianDate, jd_now
from starward.core.observer import Observer
from starward.core.visibility import (
    target_altitude,
    target_rise_set,
    transit_time,
    transit_altitude_calc,
    airmass,
)
from starward.core.messier_data import MessierObject
from starward.verbose import VerboseContext, step


class MessierCatalog:
    """
    The Messier catalog of deep sky objects.

    Provides access to all 110 Messier objects with methods for
    lookup, searching, and filtering.

    Example:
        >>> from starward.core.messier import MESSIER
        >>> m31 = MESSIER.get(31)
        >>> print(m31.name)
        Andromeda Galaxy
        >>> galaxies = MESSIER.filter_by_type("galaxy")
    """

    def __init__(self) -> None:
        """Initialize the Messier catalog with database backend."""
        self._db = get_catalog_db()

    def get(self, number: int) -> MessierObject:
        """
        Get a Messier object by its catalog number.

        Args:
            number: Messier number (1-110)

        Returns:
            The MessierObject

        Raises:
            KeyError: If number is not in the catalog
        """
        data = self._db.get_messier(number)
        if data is None:
            raise KeyError(f"M{number} is not in the Messier catalog")
        return MessierObject.from_dict(data)

    def list_all(self) -> List[MessierObject]:
        """
        Get all Messier objects as a list.

        Returns:
            List of all 110 MessierObjects, sorted by number
        """
        data_list = self._db.list_messier()
        return [MessierObject.from_dict(d) for d in data_list]

    def search(self, query: str, limit: int = 50) -> List[MessierObject]:
        """
        Search Messier objects by name, type, constellation, or NGC designation.

        Args:
            query: Search string (case-insensitive)
            limit: Maximum number of results (default 50)

        Returns:
            List of matching MessierObjects
        """
        data_list = self._db.search_messier(query, limit=limit)
        return [MessierObject.from_dict(d) for d in data_list]

    def filter_by_type(self, object_type: str) -> List[MessierObject]:
        """
        Get all Messier objects of a specific type.

        Args:
            object_type: Type to filter by (e.g., "galaxy", "globular_cluster")

        Returns:
            List of matching MessierObjects
        """
        data_list = self._db.filter_messier(object_type=object_type)
        return [MessierObject.from_dict(d) for d in data_list]

    def filter_by_constellation(self, constellation: str) -> List[MessierObject]:
        """
        Get all Messier objects in a constellation.

        Args:
            constellation: Three-letter constellation abbreviation

        Returns:
            List of matching MessierObjects
        """
        data_list = self._db.filter_messier(constellation=constellation)
        return [MessierObject.from_dict(d) for d in data_list]

    def filter_by_magnitude(self, max_magnitude: float) -> List[MessierObject]:
        """
        Get all Messier objects brighter than a given magnitude.

        Args:
            max_magnitude: Maximum (faintest) magnitude

        Returns:
            List of MessierObjects brighter than max_magnitude
        """
        data_list = self._db.filter_messier(max_magnitude=max_magnitude)
        return [MessierObject.from_dict(d) for d in data_list]

    def __len__(self) -> int:
        return self._db.count_messier()

    def __iter__(self):
        return iter(self.list_all())

    def __contains__(self, number: int) -> bool:
        """Check if a Messier number exists in the catalog."""
        return self._db.get_messier(number) is not None


# Singleton instance
MESSIER = MessierCatalog()


def messier_coords(number: int) -> ICRSCoord:
    """
    Get ICRS coordinates for a Messier object.

    Args:
        number: Messier number (1-110)

    Returns:
        ICRSCoord for the object
    """
    obj = MESSIER.get(number)
    return ICRSCoord(
        ra=Angle(hours=obj.ra_hours),
        dec=Angle(degrees=obj.dec_degrees)
    )


def messier_altitude(
    number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None
) -> Angle:
    """
    Calculate the current altitude of a Messier object.

    Args:
        number: Messier number (1-110)
        observer: Observer location
        jd: Julian Date (default: now)
        verbose: Optional verbose context

    Returns:
        Altitude angle
    """
    if jd is None:
        jd = jd_now()

    obj = MESSIER.get(number)
    coords = messier_coords(number)

    if verbose:
        step(verbose, "Object", f"M{number} - {obj.name}")
        step(verbose, "Coordinates", f"RA {coords.ra.format_hms()}  Dec {coords.dec.format_dms()}")

    return target_altitude(coords, observer, jd, verbose)


def messier_airmass(
    number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None
) -> Optional[float]:
    """
    Calculate the airmass for a Messier object.

    Args:
        number: Messier number (1-110)
        observer: Observer location
        jd: Julian Date (default: now)
        verbose: Optional verbose context

    Returns:
        Airmass value, or None if below horizon
    """
    alt = messier_altitude(number, observer, jd, verbose)
    return airmass(alt, verbose)


def messier_rise(
    number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None
) -> Optional[JulianDate]:
    """
    Calculate when a Messier object rises.

    Args:
        number: Messier number (1-110)
        observer: Observer location
        jd: Julian Date (default: now)
        verbose: Optional verbose context

    Returns:
        Rise time as JulianDate, or None if circumpolar/never rises
    """
    if jd is None:
        jd = jd_now()

    obj = MESSIER.get(number)
    coords = messier_coords(number)

    if verbose:
        step(verbose, "Object", f"M{number} - {obj.name}")

    rise, _ = target_rise_set(coords, observer, jd, verbose=verbose)
    return rise


def messier_set(
    number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None
) -> Optional[JulianDate]:
    """
    Calculate when a Messier object sets.

    Args:
        number: Messier number (1-110)
        observer: Observer location
        jd: Julian Date (default: now)
        verbose: Optional verbose context

    Returns:
        Set time as JulianDate, or None if circumpolar/never sets
    """
    if jd is None:
        jd = jd_now()

    obj = MESSIER.get(number)
    coords = messier_coords(number)

    if verbose:
        step(verbose, "Object", f"M{number} - {obj.name}")

    _, set_t = target_rise_set(coords, observer, jd, verbose=verbose)
    return set_t


def messier_transit(
    number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None
) -> JulianDate:
    """
    Calculate when a Messier object transits (crosses the meridian).

    Args:
        number: Messier number (1-110)
        observer: Observer location
        jd: Julian Date (default: now)
        verbose: Optional verbose context

    Returns:
        Transit time as JulianDate
    """
    if jd is None:
        jd = jd_now()

    obj = MESSIER.get(number)
    coords = messier_coords(number)

    if verbose:
        step(verbose, "Object", f"M{number} - {obj.name}")

    return transit_time(coords, observer, jd, verbose)


def messier_transit_altitude(
    number: int,
    observer: Observer,
    verbose: Optional[VerboseContext] = None
) -> Angle:
    """
    Calculate the maximum altitude a Messier object reaches at transit.

    Args:
        number: Messier number (1-110)
        observer: Observer location
        verbose: Optional verbose context

    Returns:
        Transit altitude
    """
    obj = MESSIER.get(number)
    coords = messier_coords(number)

    if verbose:
        step(verbose, "Object", f"M{number} - {obj.name}")

    return transit_altitude_calc(coords, observer, verbose)


# Object type constants for filtering
OBJECT_TYPES = [
    "galaxy",
    "globular_cluster",
    "open_cluster",
    "planetary_nebula",
    "emission_nebula",
    "reflection_nebula",
    "supernova_remnant",
    "star_cloud",
    "asterism",
    "double_star",
]
