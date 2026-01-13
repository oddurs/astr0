"""
NGC catalog data types and constants.

This module defines the NGCObject dataclass and object type constants
for the New General Catalogue of deep sky objects.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# =============================================================================
# Object Type Constants
# =============================================================================

# Primary galaxy types
GALAXY = "galaxy"
GALAXY_PAIR = "galaxy_pair"
GALAXY_GROUP = "galaxy_group"
GALAXY_TRIPLE = "galaxy_triple"

# Star clusters
GLOBULAR_CLUSTER = "globular_cluster"
OPEN_CLUSTER = "open_cluster"
STAR_CLUSTER = "star_cluster"
CLUSTER_NEBULA = "cluster_nebula"

# Nebulae
PLANETARY_NEBULA = "planetary_nebula"
EMISSION_NEBULA = "emission_nebula"
REFLECTION_NEBULA = "reflection_nebula"
HII_REGION = "hii_region"
SUPERNOVA_REMNANT = "supernova_remnant"
DARK_NEBULA = "dark_nebula"

# Stellar objects
ASTERISM = "asterism"
DOUBLE_STAR = "double_star"
STAR = "star"

# Other
QUASAR = "quasar"
NONEXISTENT = "nonexistent"
DUPLICATE = "duplicate"
UNKNOWN = "unknown"

# All valid NGC object types
NGC_OBJECT_TYPES = [
    GALAXY,
    GALAXY_PAIR,
    GALAXY_GROUP,
    GALAXY_TRIPLE,
    GLOBULAR_CLUSTER,
    OPEN_CLUSTER,
    STAR_CLUSTER,
    CLUSTER_NEBULA,
    PLANETARY_NEBULA,
    EMISSION_NEBULA,
    REFLECTION_NEBULA,
    HII_REGION,
    SUPERNOVA_REMNANT,
    DARK_NEBULA,
    ASTERISM,
    DOUBLE_STAR,
    STAR,
    QUASAR,
    NONEXISTENT,
    DUPLICATE,
    UNKNOWN,
]

# Human-readable names for object types
NGC_TYPE_NAMES = {
    GALAXY: "Galaxy",
    GALAXY_PAIR: "Galaxy Pair",
    GALAXY_GROUP: "Galaxy Group",
    GALAXY_TRIPLE: "Galaxy Triple",
    GLOBULAR_CLUSTER: "Globular Cluster",
    OPEN_CLUSTER: "Open Cluster",
    STAR_CLUSTER: "Star Cluster",
    CLUSTER_NEBULA: "Cluster + Nebula",
    PLANETARY_NEBULA: "Planetary Nebula",
    EMISSION_NEBULA: "Emission Nebula",
    REFLECTION_NEBULA: "Reflection Nebula",
    HII_REGION: "HII Region",
    SUPERNOVA_REMNANT: "Supernova Remnant",
    DARK_NEBULA: "Dark Nebula",
    ASTERISM: "Asterism",
    DOUBLE_STAR: "Double Star",
    STAR: "Star",
    QUASAR: "Quasar",
    NONEXISTENT: "Non-existent",
    DUPLICATE: "Duplicate Entry",
    UNKNOWN: "Unknown",
}


# =============================================================================
# NGC Object Dataclass
# =============================================================================

@dataclass(frozen=True)
class NGCObject:
    """
    An NGC (New General Catalogue) deep sky object.

    This immutable dataclass represents a single NGC catalog entry
    with all associated metadata.

    Attributes:
        number: NGC catalog number (1-7840+)
        name: Common name (e.g., "North America Nebula"), or None
        object_type: Type classification from NGC_OBJECT_TYPES
        ra_hours: Right ascension in decimal hours (J2000, 0-24)
        dec_degrees: Declination in decimal degrees (J2000, -90 to +90)
        magnitude: Visual magnitude (V-band), or None if unknown
        size_arcmin: Angular size (major axis) in arcminutes, or None
        size_minor_arcmin: Minor axis in arcminutes, or None
        distance_kly: Distance in kilo-light-years, or None if unknown
        constellation: Three-letter IAU constellation abbreviation
        messier_number: Messier catalog number if applicable (1-110), or None
        hubble_type: Hubble morphological classification for galaxies, or None
        description: Brief description of the object

    Example:
        >>> ngc7000 = NGCObject(
        ...     number=7000,
        ...     name="North America Nebula",
        ...     object_type="emission_nebula",
        ...     ra_hours=20.9833,
        ...     dec_degrees=44.5333,
        ...     magnitude=4.0,
        ...     size_arcmin=120.0,
        ...     size_minor_arcmin=100.0,
        ...     distance_kly=2.0,
        ...     constellation="Cyg",
        ...     messier_number=None,
        ...     hubble_type=None,
        ...     description="Large emission nebula resembling North America"
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
    messier_number: Optional[int]
    hubble_type: Optional[str]
    description: str

    def __repr__(self) -> str:
        """Return a concise string representation."""
        if self.name:
            return f"NGC {self.number} ({self.name})"
        return f"NGC {self.number}"

    def __str__(self) -> str:
        """Return a formatted string representation."""
        if self.name:
            return f"NGC {self.number}: {self.name}"
        return f"NGC {self.number}"

    @property
    def type_name(self) -> str:
        """Get the human-readable object type name."""
        return NGC_TYPE_NAMES.get(self.object_type, self.object_type.replace("_", " ").title())

    @property
    def designation(self) -> str:
        """Get the catalog designation (e.g., 'NGC 7000')."""
        return f"NGC {self.number}"

    @property
    def has_messier_designation(self) -> bool:
        """Check if this object also has a Messier designation."""
        return self.messier_number is not None

    @property
    def messier_designation(self) -> Optional[str]:
        """Get the Messier designation if applicable (e.g., 'M 31')."""
        if self.messier_number is not None:
            return f"M {self.messier_number}"
        return None

    @classmethod
    def from_dict(cls, data: dict) -> 'NGCObject':
        """
        Create an NGCObject from a dictionary.

        Args:
            data: Dictionary with object fields

        Returns:
            NGCObject instance
        """
        return cls(
            number=data['number'],
            name=data.get('name'),
            object_type=data.get('object_type', UNKNOWN),
            ra_hours=data['ra_hours'],
            dec_degrees=data['dec_degrees'],
            magnitude=data.get('magnitude'),
            size_arcmin=data.get('size_arcmin'),
            size_minor_arcmin=data.get('size_minor_arcmin'),
            distance_kly=data.get('distance_kly'),
            constellation=data.get('constellation', ''),
            messier_number=data.get('messier_number'),
            hubble_type=data.get('hubble_type'),
            description=data.get('description', ''),
        )
