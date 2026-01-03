"""
Astronomical constants with references and uncertainties.

All values sourced from IAU 2015 Resolution B3 and CODATA 2018 unless noted.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class Constant:
    """An astronomical constant with metadata."""
    
    name: str
    value: float
    unit: str
    uncertainty: Optional[float] = None
    reference: str = "IAU 2015"
    
    def __float__(self) -> float:
        return self.value
    
    def __repr__(self) -> str:
        if self.uncertainty:
            return f"{self.name} = {self.value} ± {self.uncertainty} {self.unit}"
        return f"{self.name} = {self.value} {self.unit}"


class AstronomicalConstants:
    """
    Collection of astronomical constants.
    
    Access constants as attributes:
        >>> from astr0.core.constants import CONSTANTS
        >>> CONSTANTS.c  # Speed of light
        >>> float(CONSTANTS.AU)  # Get numeric value
    """
    
    # Fundamental
    c = Constant(
        name="Speed of light",
        value=299_792_458.0,
        unit="m/s",
        uncertainty=0.0,  # Exact by definition
        reference="SI 2019 (exact)"
    )
    
    G = Constant(
        name="Gravitational constant",
        value=6.67430e-11,
        unit="m³/(kg·s²)",
        uncertainty=1.5e-15,
        reference="CODATA 2018"
    )
    
    # Solar System
    AU = Constant(
        name="Astronomical Unit",
        value=149_597_870_700.0,
        unit="m",
        uncertainty=0.0,  # Exact by definition since 2012
        reference="IAU 2012 (exact)"
    )
    
    # Time
    JD_J2000 = Constant(
        name="Julian Date of J2000.0",
        value=2_451_545.0,
        unit="days",
        reference="IAU (exact)"
    )
    
    MJD_OFFSET = Constant(
        name="Modified Julian Date offset",
        value=2_400_000.5,
        unit="days",
        reference="IAU (exact)"
    )
    
    JULIAN_YEAR = Constant(
        name="Julian year",
        value=365.25,
        unit="days",
        reference="IAU (exact)"
    )
    
    JULIAN_CENTURY = Constant(
        name="Julian century",
        value=36525.0,
        unit="days",
        reference="IAU (exact)"
    )
    
    # Angles
    ARCSEC_PER_RADIAN = Constant(
        name="Arcseconds per radian",
        value=206_264.806247096355,
        unit="arcsec/rad",
        reference="Derived (exact)"
    )
    
    # Earth
    EARTH_RADIUS_EQUATORIAL = Constant(
        name="Earth equatorial radius",
        value=6_378_137.0,
        unit="m",
        reference="WGS84"
    )
    
    EARTH_FLATTENING = Constant(
        name="Earth flattening",
        value=1 / 298.257223563,
        unit="",
        reference="WGS84"
    )
    
    EARTH_ROTATION_RATE = Constant(
        name="Earth rotation rate",
        value=7.292115e-5,
        unit="rad/s",
        reference="IERS"
    )
    
    # Obliquity
    OBLIQUITY_J2000 = Constant(
        name="Mean obliquity at J2000.0",
        value=23.439291111,
        unit="degrees",
        reference="IAU 2006"
    )
    
    # Galactic coordinates (ICRS)
    GALACTIC_POLE_RA = Constant(
        name="Galactic North Pole RA (ICRS)",
        value=192.859508333,
        unit="degrees",
        reference="IAU 1958, precessed to J2000"
    )
    
    GALACTIC_POLE_DEC = Constant(
        name="Galactic North Pole Dec (ICRS)",
        value=27.128336111,
        unit="degrees",
        reference="IAU 1958, precessed to J2000"
    )
    
    GALACTIC_LON_ASCENDING = Constant(
        name="Galactic longitude of ascending node",
        value=32.932,
        unit="degrees",
        reference="IAU 1958"
    )
    
    # Solar
    SOLAR_MASS = Constant(
        name="Solar mass",
        value=1.98841e30,
        unit="kg",
        uncertainty=4e25,
        reference="IAU 2015"
    )
    
    SOLAR_RADIUS = Constant(
        name="Solar radius",
        value=6.957e8,
        unit="m",
        uncertainty=0.0,  # Nominal value
        reference="IAU 2015 (nominal)"
    )
    
    SOLAR_LUMINOSITY = Constant(
        name="Solar luminosity",
        value=3.828e26,
        unit="W",
        uncertainty=0.0,  # Nominal value
        reference="IAU 2015 (nominal)"
    )
    
    # Solar position constants (Meeus Ch. 25)
    SOLAR_MEAN_ANOMALY_J2000 = Constant(
        name="Solar mean anomaly at J2000.0",
        value=357.5291092,
        unit="degrees",
        reference="Meeus, Astronomical Algorithms"
    )
    
    SOLAR_MEAN_LONGITUDE_J2000 = Constant(
        name="Solar mean longitude at J2000.0",
        value=280.46646,
        unit="degrees",
        reference="Meeus, Astronomical Algorithms"
    )
    
    SOLAR_ECCENTRICITY_J2000 = Constant(
        name="Earth orbit eccentricity at J2000.0",
        value=0.016708634,
        unit="",
        reference="Meeus, Astronomical Algorithms"
    )
    
    # Lunar constants
    LUNAR_MEAN_LONGITUDE_J2000 = Constant(
        name="Lunar mean longitude at J2000.0",
        value=218.3165,
        unit="degrees",
        reference="Meeus, Astronomical Algorithms"
    )
    
    LUNAR_MEAN_ANOMALY_J2000 = Constant(
        name="Lunar mean anomaly at J2000.0",
        value=134.9634,
        unit="degrees",
        reference="Meeus, Astronomical Algorithms"
    )
    
    LUNAR_MEAN_ELONGATION_J2000 = Constant(
        name="Lunar mean elongation at J2000.0",
        value=297.8502,
        unit="degrees",
        reference="Meeus, Astronomical Algorithms"
    )
    
    LUNAR_MEAN_DISTANCE = Constant(
        name="Lunar mean distance",
        value=384_400_000.0,
        unit="m",
        reference="IAU"
    )
    
    LUNAR_RADIUS = Constant(
        name="Lunar radius",
        value=1_737_400.0,
        unit="m",
        reference="IAU 2015"
    )
    
    SYNODIC_MONTH = Constant(
        name="Synodic month (new moon to new moon)",
        value=29.530588861,
        unit="days",
        reference="Meeus, Astronomical Algorithms"
    )
    
    # Rise/set constants
    SOLAR_APPARENT_RADIUS = Constant(
        name="Solar apparent radius (mean)",
        value=0.2666,
        unit="degrees",
        reference="Derived from mean distance"
    )
    
    ATMOSPHERIC_REFRACTION_HORIZON = Constant(
        name="Atmospheric refraction at horizon",
        value=0.5667,
        unit="degrees",
        reference="Meeus, Astronomical Algorithms"
    )
    
    # Standard altitude for rise/set (center of disk accounting for refraction)
    RISE_SET_ALTITUDE_SUN = Constant(
        name="Standard altitude for sunrise/sunset",
        value=-0.8333,
        unit="degrees",
        reference="Meeus (refraction + semidiameter)"
    )
    
    RISE_SET_ALTITUDE_MOON = Constant(
        name="Standard altitude for moonrise/moonset",
        value=0.125,
        unit="degrees",
        reference="Meeus (mean parallax - refraction - semidiameter)"
    )
    
    RISE_SET_ALTITUDE_STARS = Constant(
        name="Standard altitude for star rise/set",
        value=-0.5667,
        unit="degrees",
        reference="Meeus (refraction only)"
    )
    
    # Twilight altitudes
    CIVIL_TWILIGHT_ALTITUDE = Constant(
        name="Civil twilight altitude",
        value=-6.0,
        unit="degrees",
        reference="Standard definition"
    )
    
    NAUTICAL_TWILIGHT_ALTITUDE = Constant(
        name="Nautical twilight altitude",
        value=-12.0,
        unit="degrees",
        reference="Standard definition"
    )
    
    ASTRONOMICAL_TWILIGHT_ALTITUDE = Constant(
        name="Astronomical twilight altitude",
        value=-18.0,
        unit="degrees",
        reference="Standard definition"
    )
    
    def list_all(self) -> List[Constant]:
        """Return all constants as a list."""
        return [
            getattr(self, name) 
            for name in dir(self) 
            if isinstance(getattr(self, name), Constant)
        ]
    
    def search(self, query: str) -> List[Constant]:
        """Search constants by name."""
        query = query.lower()
        return [c for c in self.list_all() if query in c.name.lower()]


# Singleton instance
CONSTANTS = AstronomicalConstants()
