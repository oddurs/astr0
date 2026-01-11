"""
astr0 — Astronomy Calculation Toolkit

A professional astronomy calculation toolkit with a soul.
"""

__version__ = "0.2.1"
__author__ = "astr0 contributors"

# Convenient imports for library usage
from astr0.core.angles import Angle, angular_separation, position_angle
from astr0.core.time import JulianDate, jd_now, utc_to_jd, jd_to_utc
from astr0.core.coords import (
    ICRSCoord,
    GalacticCoord,
    HorizontalCoord,
    transform_coords,
)
from astr0.core.constants import CONSTANTS
from astr0.core.precision import (
    PrecisionConfig,
    PrecisionLevel,
    get_precision,
    set_precision,
    precision_context,
)

__all__ = [
    # Version
    "__version__",
    # Angles
    "Angle",
    "angular_separation",
    "position_angle",
    # Time
    "JulianDate",
    "jd_now",
    "utc_to_jd",
    "jd_to_utc",
    # Coordinates
    "ICRSCoord",
    "GalacticCoord",
    "HorizontalCoord",
    "transform_coords",
    # Constants
    "CONSTANTS",
    # Precision
    "PrecisionConfig",
    "PrecisionLevel",
    "get_precision",
    "set_precision",
    "precision_context",
]
