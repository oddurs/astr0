"""
Messier catalog operations.

Provides access to all 110 Messier objects with coordinates, metadata,
and integration with visibility calculations.
"""

from __future__ import annotations

from typing import Dict, List, Optional

from starward.core.angles import Angle
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
from starward.core.messier_data import MessierObject, MESSIER_DATA
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
        self._data = MESSIER_DATA

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
        if number not in self._data:
            raise KeyError(f"M{number} is not in the Messier catalog")
        return self._data[number]

    def list_all(self) -> List[MessierObject]:
        """
        Get all Messier objects as a list.

        Returns:
            List of all 110 MessierObjects, sorted by number
        """
        return [self._data[i] for i in sorted(self._data.keys())]

    def search(self, query: str) -> List[MessierObject]:
        """
        Search Messier objects by name, type, constellation, or NGC designation.

        Args:
            query: Search string (case-insensitive)

        Returns:
            List of matching MessierObjects
        """
        query = query.lower()
        results = []

        for obj in self._data.values():
            if (
                query in obj.name.lower()
                or query in obj.object_type.lower()
                or query in obj.constellation.lower()
                or query in obj.description.lower()
                or (obj.ngc and query in obj.ngc.lower())
            ):
                results.append(obj)

        return sorted(results, key=lambda x: x.number)

    def filter_by_type(self, object_type: str) -> List[MessierObject]:
        """
        Get all Messier objects of a specific type.

        Args:
            object_type: Type to filter by (e.g., "galaxy", "globular_cluster")

        Returns:
            List of matching MessierObjects
        """
        object_type = object_type.lower()
        return [
            obj for obj in self._data.values()
            if obj.object_type.lower() == object_type
        ]

    def filter_by_constellation(self, constellation: str) -> List[MessierObject]:
        """
        Get all Messier objects in a constellation.

        Args:
            constellation: Three-letter constellation abbreviation

        Returns:
            List of matching MessierObjects
        """
        constellation = constellation.lower()
        return [
            obj for obj in self._data.values()
            if obj.constellation.lower() == constellation
        ]

    def filter_by_magnitude(self, max_magnitude: float) -> List[MessierObject]:
        """
        Get all Messier objects brighter than a given magnitude.

        Args:
            max_magnitude: Maximum (faintest) magnitude

        Returns:
            List of MessierObjects brighter than max_magnitude
        """
        return [
            obj for obj in self._data.values()
            if obj.magnitude <= max_magnitude
        ]

    def __len__(self) -> int:
        return len(self._data)

    def __iter__(self):
        return iter(self.list_all())


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
