"""
IC catalog data types.

This module defines the ICObject dataclass for the Index Catalogue
of deep sky objects. IC uses the same object type classification
as NGC.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

# Reuse NGC object types - IC uses the same classification
from starward.core.ngc_types import NGC_OBJECT_TYPES, NGC_TYPE_NAMES


# IC uses the same object types as NGC
IC_OBJECT_TYPES = NGC_OBJECT_TYPES
IC_TYPE_NAMES = NGC_TYPE_NAMES


@dataclass(frozen=True)
class ICObject:
    """
    An IC (Index Catalogue) deep sky object.

    This immutable dataclass represents a single IC catalog entry
    with all associated metadata. IC is a supplement to the NGC
    catalog, containing ~5,386 additional objects.

    Attributes:
        number: IC catalog number (1-5386+)
        name: Common name (e.g., "Horsehead Nebula"), or None
        object_type: Type classification from IC_OBJECT_TYPES
        ra_hours: Right ascension in decimal hours (J2000, 0-24)
        dec_degrees: Declination in decimal degrees (J2000, -90 to +90)
        magnitude: Visual magnitude (V-band), or None if unknown
        size_arcmin: Angular size (major axis) in arcminutes, or None
        size_minor_arcmin: Minor axis in arcminutes, or None
        distance_kly: Distance in kilo-light-years, or None if unknown
        constellation: Three-letter IAU constellation abbreviation
        ngc_number: NGC catalog cross-reference if applicable, or None
        hubble_type: Hubble morphological classification for galaxies, or None
        description: Brief description of the object

    Example:
        >>> ic434 = ICObject(
        ...     number=434,
        ...     name="Horsehead Nebula",
        ...     object_type="dark_nebula",
        ...     ra_hours=5.6833,
        ...     dec_degrees=-2.4583,
        ...     magnitude=None,
        ...     size_arcmin=60.0,
        ...     size_minor_arcmin=10.0,
        ...     distance_kly=1.5,
        ...     constellation="Ori",
        ...     ngc_number=None,
        ...     hubble_type=None,
        ...     description="Famous dark nebula silhouetted against emission nebula"
        ... )
    """

    number: int
    name: Optional[str]
    object_type: str
    ra_hours: float
    dec_degrees: float
    magnitude: Optional[float]
    size_arcmin: Optional[float]
    size_minor_arcmin: Optional[float]
    distance_kly: Optional[float]
    constellation: str
    ngc_number: Optional[int]
    hubble_type: Optional[str]
    description: str

    def __repr__(self) -> str:
        """Return a concise string representation."""
        if self.name:
            return f"IC {self.number} ({self.name})"
        return f"IC {self.number}"

    def __str__(self) -> str:
        """Return a formatted string representation."""
        if self.name:
            return f"IC {self.number}: {self.name}"
        return f"IC {self.number}"

    @property
    def type_name(self) -> str:
        """Get the human-readable object type name."""
        return IC_TYPE_NAMES.get(self.object_type, self.object_type.replace("_", " ").title())

    @property
    def designation(self) -> str:
        """Get the catalog designation (e.g., 'IC 434')."""
        return f"IC {self.number}"

    @property
    def has_ngc_designation(self) -> bool:
        """Check if this object also has an NGC designation."""
        return self.ngc_number is not None

    @property
    def ngc_designation(self) -> Optional[str]:
        """Get the NGC designation if applicable (e.g., 'NGC 1234')."""
        if self.ngc_number is not None:
            return f"NGC {self.ngc_number}"
        return None

    @classmethod
    def from_dict(cls, data: dict) -> 'ICObject':
        """
        Create an ICObject from a dictionary.

        Args:
            data: Dictionary with object fields

        Returns:
            ICObject instance
        """
        return cls(
            number=data['number'],
            name=data.get('name'),
            object_type=data.get('object_type', 'unknown'),
            ra_hours=data['ra_hours'],
            dec_degrees=data['dec_degrees'],
            magnitude=data.get('magnitude'),
            size_arcmin=data.get('size_arcmin'),
            size_minor_arcmin=data.get('size_minor_arcmin'),
            distance_kly=data.get('distance_kly'),
            constellation=data.get('constellation', ''),
            ngc_number=data.get('ngc_number'),
            hubble_type=data.get('hubble_type'),
            description=data.get('description', ''),
        )
