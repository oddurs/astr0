"""
Hipparcos Bright Star Catalog module.

This module provides access to the Hipparcos catalog of bright stars
with precise positions, proper motions, and photometric data.

Example:
    >>> from starward.core.hipparcos import Hipparcos, star_coords
    >>> sirius = Hipparcos.get(32349)
    >>> print(sirius.name)
    Sirius
    >>> coords = star_coords(32349)
    >>> print(coords)
    06h45m08.92s -16d42m58.02s
"""

from __future__ import annotations

from typing import List, Optional

from starward.core.angles import Angle
from starward.core.catalog_db import get_catalog_db
from starward.core.coords import ICRSCoord
from starward.core.hipparcos_types import HIPStar
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


class HipparcosCatalog:
    """
    The Hipparcos Bright Star Catalog.

    Provides access to bright stars with precise astrometric data including
    positions, proper motions, parallaxes, and photometry.

    Example:
        >>> from starward.core.hipparcos import Hipparcos
        >>> sirius = Hipparcos.get(32349)
        >>> print(sirius.name)
        Sirius

        >>> bright_stars = Hipparcos.filter_by_magnitude(1.0)
        >>> for star in bright_stars:
        ...     print(star.name, star.magnitude)

        >>> vega = Hipparcos.get_by_name("Vega")
        >>> print(vega.spectral_type)
        A0V
    """

    def __init__(self) -> None:
        """Initialize the Hipparcos catalog."""
        self._db = get_catalog_db()

    def get(self, hip_number: int) -> HIPStar:
        """
        Get a star by its Hipparcos catalog number.

        Args:
            hip_number: Hipparcos catalog number

        Returns:
            HIPStar with all metadata

        Raises:
            KeyError: If the HIP number is not in the catalog

        Example:
            >>> sirius = Hipparcos.get(32349)
            >>> print(sirius.name)
            Sirius
        """
        data = self._db.get_hipparcos(hip_number)
        if data is None:
            raise KeyError(f"HIP {hip_number} is not in the catalog")
        return HIPStar.from_dict(data)

    def get_by_name(self, name: str) -> Optional[HIPStar]:
        """
        Get a star by its common name.

        Args:
            name: Star name (case-insensitive)

        Returns:
            HIPStar if found, None otherwise

        Example:
            >>> vega = Hipparcos.get_by_name("Vega")
            >>> if vega:
            ...     print(vega.hip_number)
            91262
        """
        data = self._db.get_hipparcos_by_name(name)
        if data is None:
            return None
        return HIPStar.from_dict(data)

    def get_by_bayer(self, bayer: str) -> Optional[HIPStar]:
        """
        Get a star by its Bayer designation.

        Args:
            bayer: Bayer designation (e.g., "Alpha Orionis")

        Returns:
            HIPStar if found, None otherwise

        Example:
            >>> betelgeuse = Hipparcos.get_by_bayer("Alpha Orionis")
            >>> if betelgeuse:
            ...     print(betelgeuse.name)
            Betelgeuse
        """
        data = self._db.get_hipparcos_by_bayer(bayer)
        if data is None:
            return None
        return HIPStar.from_dict(data)

    def list_all(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        order_by: str = "magnitude"
    ) -> List[HIPStar]:
        """
        Get stars sorted by specified field.

        Args:
            limit: Maximum number of stars to return (None for all)
            offset: Number of stars to skip (for pagination)
            order_by: Sort field ("magnitude", "hip_number", "name", "distance_ly")

        Returns:
            List of HIPStar instances

        Example:
            >>> brightest = Hipparcos.list_all(limit=10)
            >>> for star in brightest:
            ...     print(f"{star.name}: {star.magnitude}")
        """
        data_list = self._db.list_hipparcos(limit=limit, offset=offset, order_by=order_by)
        return [HIPStar.from_dict(d) for d in data_list]

    def search(self, query: str, limit: int = 50) -> List[HIPStar]:
        """
        Search stars by name, Bayer designation, spectral type, or constellation.

        The search is case-insensitive and matches partial strings.

        Args:
            query: Search string
            limit: Maximum number of results (default 50)

        Returns:
            List of matching HIPStar instances, sorted by magnitude

        Example:
            >>> results = Hipparcos.search("alpha")
            >>> results = Hipparcos.search("orion")
            >>> results = Hipparcos.search("A0V")
        """
        data_list = self._db.search_hipparcos(query, limit=limit)
        return [HIPStar.from_dict(d) for d in data_list]

    def filter_by_constellation(self, constellation: str) -> List[HIPStar]:
        """
        Get all stars in a specific constellation.

        Args:
            constellation: Three-letter IAU constellation abbreviation

        Returns:
            List of matching HIPStar instances, sorted by magnitude

        Example:
            >>> orion_stars = Hipparcos.filter_by_constellation("Ori")
            >>> for star in orion_stars:
            ...     print(star.name)
        """
        data_list = self._db.filter_hipparcos(constellation=constellation)
        return [HIPStar.from_dict(d) for d in data_list]

    def filter_by_magnitude(self, max_magnitude: float) -> List[HIPStar]:
        """
        Get all stars brighter than a given magnitude.

        Args:
            max_magnitude: Maximum (faintest) magnitude to include

        Returns:
            List of matching HIPStar instances, sorted by magnitude

        Example:
            >>> naked_eye = Hipparcos.filter_by_magnitude(6.0)
            >>> first_mag = Hipparcos.filter_by_magnitude(1.0)
        """
        data_list = self._db.filter_hipparcos(max_magnitude=max_magnitude)
        return [HIPStar.from_dict(d) for d in data_list]

    def filter_by_spectral_class(self, spectral_class: str) -> List[HIPStar]:
        """
        Get all stars of a specific spectral class.

        Args:
            spectral_class: Spectral class prefix (e.g., "O", "B", "A", "G", "K", "M")

        Returns:
            List of matching HIPStar instances, sorted by magnitude

        Example:
            >>> blue_stars = Hipparcos.filter_by_spectral_class("B")
            >>> red_giants = Hipparcos.filter_by_spectral_class("K")
        """
        data_list = self._db.filter_hipparcos(spectral_class=spectral_class)
        return [HIPStar.from_dict(d) for d in data_list]

    def filter_named(
        self,
        max_magnitude: Optional[float] = None,
        limit: Optional[int] = None,
    ) -> List[HIPStar]:
        """
        Get stars that have common names.

        Args:
            max_magnitude: Maximum magnitude to include (optional)
            limit: Maximum number of results

        Returns:
            List of named HIPStar instances, sorted by magnitude

        Example:
            >>> named_stars = Hipparcos.filter_named(max_magnitude=3.0)
            >>> for star in named_stars:
            ...     print(f"{star.name} ({star.bayer})")
        """
        data_list = self._db.filter_hipparcos(
            max_magnitude=max_magnitude,
            has_name=True,
            limit=limit,
        )
        return [HIPStar.from_dict(d) for d in data_list]

    def stats(self) -> dict:
        """
        Get statistics about the Hipparcos catalog.

        Returns:
            Dictionary with catalog statistics

        Example:
            >>> stats = Hipparcos.stats()
            >>> print(stats['total'])
            >>> print(stats['brightest'])
        """
        return self._db.hipparcos_stats()

    def __len__(self) -> int:
        """Return the total number of Hipparcos stars."""
        return self._db.count_hipparcos()

    def __iter__(self):
        """Iterate over all stars (sorted by magnitude)."""
        return iter(self.list_all())

    def __contains__(self, hip_number: int) -> bool:
        """Check if a HIP number exists in the catalog."""
        return self._db.get_hipparcos(hip_number) is not None


# Singleton instance
Hipparcos = HipparcosCatalog()


# =============================================================================
# Coordinate Functions
# =============================================================================

def star_coords(hip_number: int) -> ICRSCoord:
    """
    Get ICRS coordinates for a Hipparcos star.

    Args:
        hip_number: Hipparcos catalog number

    Returns:
        ICRSCoord with RA and Dec

    Raises:
        KeyError: If the HIP number is not in the catalog

    Example:
        >>> coords = star_coords(32349)  # Sirius
        >>> print(coords.ra.format_hms())
        06h45m08.91s
    """
    star = Hipparcos.get(hip_number)
    # Convert RA from hours to degrees (hours * 15 = degrees)
    ra_degrees = star.ra_hours * 15.0
    return ICRSCoord.from_degrees(ra_degrees, star.dec_degrees)


# =============================================================================
# Visibility Functions
# =============================================================================

def star_altitude(
    hip_number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None,
) -> Angle:
    """
    Calculate the current altitude of a Hipparcos star.

    Args:
        hip_number: Hipparcos catalog number
        observer: Observer location
        jd: Julian Date for calculation (default: now)
        verbose: Optional verbose context for step-by-step output

    Returns:
        Altitude as an Angle

    Example:
        >>> from starward.core.observer import Observer
        >>> obs = Observer.from_degrees("Home", 40.7, -74.0)
        >>> alt = star_altitude(32349, obs)  # Sirius
        >>> print(f"{alt.degrees:.1f} degrees")
    """
    if jd is None:
        jd = jd_now()

    coords = star_coords(hip_number)
    return target_altitude(coords, observer, jd, verbose=verbose)


def star_airmass(
    hip_number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None,
) -> Optional[float]:
    """
    Calculate the airmass for a Hipparcos star.

    Args:
        hip_number: Hipparcos catalog number
        observer: Observer location
        jd: Julian Date for calculation (default: now)
        verbose: Optional verbose context for step-by-step output

    Returns:
        Airmass value, or None if star is below horizon

    Example:
        >>> X = star_airmass(32349, observer)  # Sirius
        >>> if X:
        ...     print(f"Airmass: {X:.2f}")
    """
    if jd is None:
        jd = jd_now()

    coords = star_coords(hip_number)
    alt = target_altitude(coords, observer, jd, verbose=verbose)
    return airmass(alt, verbose=verbose)


def star_rise(
    hip_number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None,
) -> Optional[JulianDate]:
    """
    Calculate when a Hipparcos star rises.

    Args:
        hip_number: Hipparcos catalog number
        observer: Observer location
        jd: Julian Date to start search (default: now)
        verbose: Optional verbose context for step-by-step output

    Returns:
        JulianDate of rise, or None if circumpolar/never rises

    Example:
        >>> rise_time = star_rise(32349, observer)  # Sirius
        >>> if rise_time:
        ...     print(rise_time.to_utc())
    """
    if jd is None:
        jd = jd_now()

    coords = star_coords(hip_number)
    rise, _ = target_rise_set(coords, observer, jd, verbose=verbose)
    return rise


def star_set(
    hip_number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None,
) -> Optional[JulianDate]:
    """
    Calculate when a Hipparcos star sets.

    Args:
        hip_number: Hipparcos catalog number
        observer: Observer location
        jd: Julian Date to start search (default: now)
        verbose: Optional verbose context for step-by-step output

    Returns:
        JulianDate of set, or None if circumpolar/never sets

    Example:
        >>> set_time = star_set(32349, observer)  # Sirius
        >>> if set_time:
        ...     print(set_time.to_utc())
    """
    if jd is None:
        jd = jd_now()

    coords = star_coords(hip_number)
    _, set_time = target_rise_set(coords, observer, jd, verbose=verbose)
    return set_time


def star_transit(
    hip_number: int,
    observer: Observer,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None,
) -> JulianDate:
    """
    Calculate when a Hipparcos star transits the meridian.

    Args:
        hip_number: Hipparcos catalog number
        observer: Observer location
        jd: Julian Date to start search (default: now)
        verbose: Optional verbose context for step-by-step output

    Returns:
        JulianDate of transit

    Example:
        >>> transit_jd = star_transit(32349, observer)  # Sirius
        >>> print(transit_jd.to_utc())
    """
    if jd is None:
        jd = jd_now()

    coords = star_coords(hip_number)
    return transit_time(coords, observer, jd, verbose=verbose)


def star_transit_altitude(
    hip_number: int,
    observer: Observer,
    verbose: Optional[VerboseContext] = None,
) -> Angle:
    """
    Calculate the maximum altitude a star reaches at transit.

    Args:
        hip_number: Hipparcos catalog number
        observer: Observer location
        verbose: Optional verbose context for step-by-step output

    Returns:
        Maximum altitude as an Angle

    Example:
        >>> max_alt = star_transit_altitude(32349, observer)  # Sirius
        >>> print(f"Max altitude: {max_alt.degrees:.1f} degrees")
    """
    coords = star_coords(hip_number)
    return transit_altitude_calc(coords, observer, verbose=verbose)
