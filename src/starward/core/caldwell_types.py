"""
Caldwell catalog data types and constants.

This module defines the CaldwellObject dataclass and object type constants
for the Caldwell Catalogue of deep sky objects, compiled by Sir Patrick Moore.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# =============================================================================
# Object Type Constants (reuse from NGC types)
# =============================================================================

# Primary galaxy types
GALAXY = "galaxy"
GALAXY_PAIR = "galaxy_pair"
GALAXY_GROUP = "galaxy_group"

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

# Other
UNKNOWN = "unknown"

# All valid Caldwell object types
CALDWELL_OBJECT_TYPES = [
    GALAXY,
    GALAXY_PAIR,
    GALAXY_GROUP,
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
    UNKNOWN,
]

# Human-readable names for object types
CALDWELL_TYPE_NAMES = {
    GALAXY: "Galaxy",
    GALAXY_PAIR: "Galaxy Pair",
    GALAXY_GROUP: "Galaxy Group",
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
    UNKNOWN: "Unknown",
}


# =============================================================================
# Caldwell Object Dataclass
# =============================================================================

@dataclass(frozen=True)
class CaldwellObject:
    """
    A Caldwell Catalogue deep sky object.

    The Caldwell Catalogue is a collection of 109 deep-sky objects compiled
    by Sir Patrick Moore to complement the Messier catalogue. It includes
    objects visible from both hemispheres that are not in the Messier list.

    This immutable dataclass represents a single Caldwell catalog entry
    with all associated metadata.

    Attributes:
        number: Caldwell catalog number (1-109)
        name: Common name (e.g., "Sculptor Galaxy"), or None
        object_type: Type classification from CALDWELL_OBJECT_TYPES
        ra_hours: Right ascension in decimal hours (J2000, 0-24)
        dec_degrees: Declination in decimal degrees (J2000, -90 to +90)
        magnitude: Visual magnitude (V-band), or None if unknown
        size_arcmin: Angular size (major axis) in arcminutes, or None
        size_minor_arcmin: Minor axis in arcminutes, or None
        distance_kly: Distance in kilo-light-years, or None if unknown
        constellation: Three-letter IAU constellation abbreviation
        ngc_number: NGC catalog number if applicable, or None
        ic_number: IC catalog number if applicable, or None
        description: Brief description of the object

    Example:
        >>> c65 = CaldwellObject(
        ...     number=65,
        ...     name="Sculptor Galaxy",
        ...     object_type="galaxy",
        ...     ra_hours=0.8167,
        ...     dec_degrees=-33.8833,
        ...     magnitude=7.2,
        ...     size_arcmin=27.5,
        ...     size_minor_arcmin=6.8,
        ...     distance_kly=11900.0,
        ...     constellation="Scl",
        ...     ngc_number=253,
        ...     ic_number=None,
        ...     description="Large bright galaxy in Sculptor"
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
    ic_number: Optional[int]
    description: str

    def __repr__(self) -> str:
        """Return a concise string representation."""
        if self.name:
            return f"C {self.number} ({self.name})"
        return f"C {self.number}"

    def __str__(self) -> str:
        """Return a formatted string representation."""
        if self.name:
            return f"C {self.number}: {self.name}"
        return f"C {self.number}"

    @property
    def type_name(self) -> str:
        """Get the human-readable object type name."""
        return CALDWELL_TYPE_NAMES.get(self.object_type, self.object_type.replace("_", " ").title())

    @property
    def designation(self) -> str:
        """Get the catalog designation (e.g., 'C 65')."""
        return f"C {self.number}"

    @property
    def has_ngc_designation(self) -> bool:
        """Check if this object also has an NGC designation."""
        return self.ngc_number is not None

    @property
    def ngc_designation(self) -> Optional[str]:
        """Get the NGC designation if applicable (e.g., 'NGC 253')."""
        if self.ngc_number is not None:
            return f"NGC {self.ngc_number}"
        return None

    @property
    def has_ic_designation(self) -> bool:
        """Check if this object also has an IC designation."""
        return self.ic_number is not None

    @property
    def ic_designation(self) -> Optional[str]:
        """Get the IC designation if applicable (e.g., 'IC 1613')."""
        if self.ic_number is not None:
            return f"IC {self.ic_number}"
        return None

    @property
    def catalog_designations(self) -> list[str]:
        """Get all catalog designations for this object."""
        designations = [self.designation]
        if self.ngc_designation:
            designations.append(self.ngc_designation)
        if self.ic_designation:
            designations.append(self.ic_designation)
        return designations

    @classmethod
    def from_dict(cls, data: dict) -> 'CaldwellObject':
        """
        Create a CaldwellObject from a dictionary.

        Args:
            data: Dictionary with object fields

        Returns:
            CaldwellObject instance
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
            ngc_number=data.get('ngc_number'),
            ic_number=data.get('ic_number'),
            description=data.get('description', ''),
        )
