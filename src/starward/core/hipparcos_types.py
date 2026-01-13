"""
Hipparcos catalog types and data structures.

This module defines the HIPStar dataclass and spectral type constants
for working with Hipparcos catalog data.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


# Spectral type classifications
SPECTRAL_CLASSES = ["O", "B", "A", "F", "G", "K", "M", "L", "T", "Y"]

# Luminosity classes
LUMINOSITY_CLASSES = {
    "Ia-0": "Hypergiant",
    "Ia": "Luminous supergiant",
    "Iab": "Intermediate supergiant",
    "Ib": "Less luminous supergiant",
    "II": "Bright giant",
    "III": "Giant",
    "IV": "Subgiant",
    "V": "Main sequence (dwarf)",
    "VI": "Subdwarf",
    "VII": "White dwarf",
}


@dataclass(frozen=True)
class HIPStar:
    """
    A star from the Hipparcos catalog.

    Attributes:
        hip_number: Hipparcos catalog number (primary identifier)
        name: Common name (e.g., "Sirius", "Vega")
        bayer: Bayer designation (e.g., "Alpha Canis Majoris")
        flamsteed: Flamsteed number within constellation
        ra_hours: Right Ascension in decimal hours (J2000)
        dec_degrees: Declination in decimal degrees (J2000)
        magnitude: Visual (V-band) magnitude
        bv_color: B-V color index
        spectral_type: Spectral classification (e.g., "A1V", "K5III")
        parallax: Parallax in milliarcseconds
        distance_ly: Distance in light-years
        proper_motion_ra: Proper motion in RA (mas/yr)
        proper_motion_dec: Proper motion in Dec (mas/yr)
        radial_velocity: Radial velocity in km/s
        constellation: IAU 3-letter constellation abbreviation

    Example:
        >>> sirius = HIPStar(
        ...     hip_number=32349,
        ...     name="Sirius",
        ...     bayer="Alpha Canis Majoris",
        ...     magnitude=-1.46,
        ...     spectral_type="A1V",
        ...     ...
        ... )
    """

    hip_number: int
    name: Optional[str]
    bayer: Optional[str]
    flamsteed: Optional[int]
    ra_hours: float
    dec_degrees: float
    magnitude: float
    bv_color: Optional[float]
    spectral_type: Optional[str]
    parallax: Optional[float]
    distance_ly: Optional[float]
    proper_motion_ra: Optional[float]
    proper_motion_dec: Optional[float]
    radial_velocity: Optional[float]
    constellation: str

    @classmethod
    def from_dict(cls, data: dict) -> "HIPStar":
        """
        Create a HIPStar from a dictionary (database row).

        Args:
            data: Dictionary with star data

        Returns:
            HIPStar instance
        """
        return cls(
            hip_number=data["hip_number"],
            name=data.get("name"),
            bayer=data.get("bayer"),
            flamsteed=data.get("flamsteed"),
            ra_hours=data["ra_hours"],
            dec_degrees=data["dec_degrees"],
            magnitude=data["magnitude"],
            bv_color=data.get("bv_color"),
            spectral_type=data.get("spectral_type"),
            parallax=data.get("parallax"),
            distance_ly=data.get("distance_ly"),
            proper_motion_ra=data.get("proper_motion_ra"),
            proper_motion_dec=data.get("proper_motion_dec"),
            radial_velocity=data.get("radial_velocity"),
            constellation=data["constellation"],
        )

    @property
    def designation(self) -> str:
        """Get the primary designation for this star."""
        if self.name:
            return self.name
        if self.bayer:
            return self.bayer
        if self.flamsteed and self.constellation:
            return f"{self.flamsteed} {self.constellation}"
        return f"HIP {self.hip_number}"

    @property
    def spectral_class(self) -> Optional[str]:
        """Get just the spectral class letter (O, B, A, F, G, K, M)."""
        if not self.spectral_type:
            return None
        for cls in SPECTRAL_CLASSES:
            if self.spectral_type.startswith(cls):
                return cls
        return None

    def __str__(self) -> str:
        """Return string representation."""
        mag_str = f"mag {self.magnitude:.2f}"
        if self.name:
            return f"HIP {self.hip_number} ({self.name}) - {mag_str}"
        elif self.bayer:
            return f"HIP {self.hip_number} ({self.bayer}) - {mag_str}"
        return f"HIP {self.hip_number} - {mag_str}"
