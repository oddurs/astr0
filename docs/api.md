# Python API Reference

While astr0 is primarily a CLI tool, all functionality is available as a Python library. This guide covers the programmatic API.

---

## Installation

```bash
pip install astr0
```

Or for development:

```bash
pip install -e ".[dev]"
```

---

## Quick Start

```python
from astr0.core.time import JulianDate, jd_now
from astr0.core.coords import ICRSCoord, GalacticCoord
from astr0.core.angles import Angle, angular_separation
from astr0.core.constants import AstronomicalConstants

# Current Julian Date
jd = jd_now()
print(f"JD: {jd.jd}, GMST: {jd.gmst():.4f}h")

# Parse coordinates
coord = ICRSCoord.from_string("12h30m +45d")
print(f"RA: {coord.ra.degrees}°, Dec: {coord.dec.degrees}°")

# Transform to Galactic
gal = coord.to_galactic()
print(f"l: {gal.l.degrees}°, b: {gal.b.degrees}°")

# Angular separation
c1 = ICRSCoord.from_string("10h +30d")
c2 = ICRSCoord.from_string("11h +31d")
sep = angular_separation(c1.ra, c1.dec, c2.ra, c2.dec)
print(f"Separation: {sep.degrees}°")

# Constants
const = AstronomicalConstants()
print(f"Speed of light: {const.c.value} {const.c.unit}")
```

---

## astr0.core.angles

### Angle Class

Immutable angle representation with automatic unit conversion.

#### Creating Angles

```python
from astr0.core.angles import Angle

# From various units (use exactly ONE keyword argument)
a1 = Angle(degrees=45.5)
a2 = Angle(radians=0.7854)
a3 = Angle(hours=3.0333)
a4 = Angle(arcminutes=2730)
a5 = Angle(arcseconds=163800)

# From components
a6 = Angle.from_dms(45, 30, 0)        # 45° 30' 00"
a7 = Angle.from_dms(-45, 30, 15.5)    # -45° 30' 15.5"
a8 = Angle.from_hms(12, 30, 45)       # 12h 30m 45s

# From string
a9 = Angle.parse("45d30m15s")
a10 = Angle.parse("12h30m45s")
a11 = Angle.parse("45:30:15")
a12 = Angle.parse("45.5")
```

#### Accessing Values

```python
a = Angle(degrees=45.5)

# Different units
a.degrees      # 45.5
a.radians      # 0.7941...
a.hours        # 3.0333...
a.arcminutes   # 2730.0
a.arcseconds   # 163800.0
```

#### Converting to Components

```python
a = Angle(degrees=45.504306)

# DMS components
d, m, s = a.to_dms_components()  # (45, 30, 15.5)

# HMS components  
h, m, s = a.to_hms_components()  # (3, 2, 1.03...)
```

#### Formatting

```python
a = Angle(degrees=45.504306)

a.to_dms()                    # "45° 30′ 15.50″"
a.to_dms(precision=0)         # "45° 30′ 16″"
a.to_hms()                    # "03ʰ 02ᵐ 01.03ˢ"
str(a)                        # "45.504306°"
```

#### Arithmetic

```python
a = Angle(degrees=45)
b = Angle(degrees=30)

a + b         # Angle(degrees=75)
a - b         # Angle(degrees=15)
a * 2         # Angle(degrees=90)
a / 3         # Angle(degrees=15)
-a            # Angle(degrees=-45)
abs(a)        # Angle(degrees=45)
```

#### Comparison

```python
a = Angle(degrees=45)
b = Angle(degrees=30)

a > b         # True
a >= b        # True
a < b         # False
a == b        # False
a != b        # True
```

#### Trigonometry

```python
a = Angle(degrees=30)

a.sin()       # 0.5
a.cos()       # 0.866...
a.tan()       # 0.577...
```

#### Normalization

```python
a = Angle(degrees=370)

a.normalize()              # Angle(degrees=10) — centered on 180, range [0, 360)
a.normalize(center=0)      # Angle(degrees=10) — range [-180, 180)
a.normalize(center=180)    # Angle(degrees=10) — range [0, 360)
```

---

### angular_separation()

Calculate the angular separation between two points using the Vincenty formula.

```python
from astr0.core.angles import Angle, angular_separation

ra1 = Angle(hours=10)
dec1 = Angle(degrees=30)
ra2 = Angle(hours=11)
dec2 = Angle(degrees=31)

sep = angular_separation(ra1, dec1, ra2, dec2)
print(f"Separation: {sep.to_dms()}")

# With verbose output
from astr0.verbose import VerboseContext
ctx = VerboseContext()
sep = angular_separation(ra1, dec1, ra2, dec2, verbose=ctx)
ctx.print_steps()
```

**Signature**:
```python
def angular_separation(
    ra1: Angle, dec1: Angle,
    ra2: Angle, dec2: Angle,
    verbose: Optional[VerboseContext] = None
) -> Angle
```

---

### position_angle()

Calculate the position angle from point 1 to point 2.

```python
from astr0.core.angles import Angle, position_angle

ra1 = Angle(hours=10)
dec1 = Angle(degrees=30)
ra2 = Angle(hours=10.5)
dec2 = Angle(degrees=31)

pa = position_angle(ra1, dec1, ra2, dec2)
print(f"PA: {pa.degrees}°")  # Measured N through E
```

**Signature**:
```python
def position_angle(
    ra1: Angle, dec1: Angle,
    ra2: Angle, dec2: Angle,
    verbose: Optional[VerboseContext] = None
) -> Angle
```

---

## astr0.core.time

### JulianDate Class

Immutable Julian Date representation.

#### Creating JulianDates

```python
from astr0.core.time import JulianDate, jd_now

# Direct from JD value
jd = JulianDate(2460000.5)

# Current time
jd = jd_now()

# From components
jd = JulianDate.from_calendar(2024, 7, 4, 12, 0, 0)  # July 4, 2024 12:00 UTC

# From datetime
from datetime import datetime, timezone
dt = datetime(2024, 7, 4, 12, 0, 0, tzinfo=timezone.utc)
jd = JulianDate.from_datetime(dt)

# From MJD
jd = JulianDate.from_mjd(60000.0)

# J2000.0 epoch
jd = JulianDate.j2000()  # JD 2451545.0
```

#### Properties

```python
jd = JulianDate(2460000.5)

jd.jd           # 2460000.5 — Julian Date
jd.mjd          # 60000.0 — Modified Julian Date
jd.t_j2000      # -0.0423... — Julian centuries since J2000.0
jd.days_j2000   # -1544.5 — Days since J2000.0
```

#### Methods

```python
jd = JulianDate(2460000.5)

# To datetime
dt = jd.to_datetime()  # datetime object (UTC)

# Sidereal time
gmst = jd.gmst()       # Greenwich Mean Sidereal Time (hours)
lst = jd.lst(-118.25)  # Local Sidereal Time for longitude (hours)

# With verbose output
from astr0.verbose import VerboseContext
ctx = VerboseContext()
gmst = jd.gmst(verbose=ctx)
ctx.print_steps()
```

#### Arithmetic

```python
jd1 = JulianDate(2460000.5)
jd2 = JulianDate(2460010.5)

# Add/subtract days
jd_later = jd1 + 10     # JulianDate(2460010.5)
jd_earlier = jd1 - 5    # JulianDate(2459995.5)

# Difference between JDs (returns days)
diff = jd2 - jd1        # 10.0

# Comparison
jd1 < jd2               # True
jd1 == jd2              # False
```

---

### Convenience Functions

```python
from astr0.core.time import (
    jd_now,
    calendar_to_jd,
    jd_to_datetime,
    mjd_to_jd,
    jd_to_mjd
)

# Current JD
jd = jd_now()

# Calendar to JD
jd_val = calendar_to_jd(2024, 7, 4, 12, 0, 0)

# JD to datetime
dt = jd_to_datetime(2460000.5)

# MJD conversions
jd_val = mjd_to_jd(60000.0)  # 2460000.5
mjd_val = jd_to_mjd(2460000.5)  # 60000.0
```

---

## astr0.core.coords

### ICRSCoord Class

ICRS (J2000 equatorial) coordinates.

#### Creating

```python
from astr0.core.coords import ICRSCoord
from astr0.core.angles import Angle

# From Angle objects
coord = ICRSCoord(
    ra=Angle(hours=12.5),
    dec=Angle(degrees=45.0)
)

# From degrees
coord = ICRSCoord.from_degrees(ra=187.5, dec=45.0)

# From string (most flexible)
coord = ICRSCoord.from_string("12h30m +45d")
coord = ICRSCoord.from_string("12h30m45s +45d30m15s")
coord = ICRSCoord.from_string("187.5 45.0")
```

#### Properties

```python
coord = ICRSCoord.from_string("12h30m +45d")

coord.ra           # Angle — Right Ascension
coord.dec          # Angle — Declination
coord.ra.degrees   # 187.5
coord.dec.degrees  # 45.0
```

#### Transformations

```python
from astr0.core.coords import ICRSCoord
from astr0.core.angles import Angle
from astr0.core.time import jd_now

coord = ICRSCoord.from_string("12h30m +45d")

# To Galactic
gal = coord.to_galactic()
print(f"l={gal.l.degrees}°, b={gal.b.degrees}°")

# To Horizontal (requires observer location and time)
horiz = coord.to_horizontal(
    latitude=Angle(degrees=34.05),
    longitude=Angle(degrees=-118.25),
    jd=jd_now()
)
print(f"Alt={horiz.alt.degrees}°, Az={horiz.az.degrees}°")

# to_icrs returns self
same = coord.to_icrs()
```

---

### GalacticCoord Class

Galactic coordinates.

#### Creating

```python
from astr0.core.coords import GalacticCoord
from astr0.core.angles import Angle

# From Angle objects
coord = GalacticCoord(
    l=Angle(degrees=135.0),
    b=Angle(degrees=71.6)
)

# From degrees
coord = GalacticCoord.from_degrees(l=0, b=0)  # Galactic Center

# From ICRS
from astr0.core.coords import ICRSCoord
icrs = ICRSCoord.from_string("12h30m +45d")
gal = GalacticCoord.from_icrs(icrs)
```

#### Transformations

```python
gal = GalacticCoord.from_degrees(l=0, b=0)

# To ICRS
icrs = gal.to_icrs()
print(f"RA={icrs.ra.to_hms()}, Dec={icrs.dec.to_dms()}")

# to_galactic returns self
same = gal.to_galactic()
```

---

### HorizontalCoord Class

Horizontal (Alt/Az) coordinates.

#### Creating

```python
from astr0.core.coords import HorizontalCoord
from astr0.core.angles import Angle

# From Angle objects
coord = HorizontalCoord(
    alt=Angle(degrees=45.0),
    az=Angle(degrees=180.0)
)

# From degrees
coord = HorizontalCoord.from_degrees(alt=45.0, az=180.0)

# From ICRS (requires location and time)
from astr0.core.coords import ICRSCoord
from astr0.core.time import jd_now

icrs = ICRSCoord.from_string("12h30m +45d")
horiz = HorizontalCoord.from_icrs(
    icrs,
    latitude=Angle(degrees=34.05),
    longitude=Angle(degrees=-118.25),
    jd=jd_now()
)
```

#### Properties

```python
horiz = HorizontalCoord.from_degrees(alt=45.0, az=180.0)

horiz.alt       # Angle — Altitude
horiz.az        # Angle — Azimuth
horiz.zenith    # Angle — Zenith distance (90° - alt)
horiz.airmass   # float — Atmospheric airmass (Pickering 2002)
```

---

### transform_coords()

Generic coordinate transformation function.

```python
from astr0.core.coords import ICRSCoord, transform_coords
from astr0.core.angles import Angle
from astr0.core.time import jd_now

coord = ICRSCoord.from_string("12h30m +45d")

# Transform to Galactic
gal = transform_coords(coord, 'galactic')

# Transform to Horizontal
horiz = transform_coords(
    coord, 
    'horizontal',
    latitude=Angle(degrees=34.05),
    longitude=Angle(degrees=-118.25),
    jd=jd_now()
)
```

**Signature**:
```python
def transform_coords(
    coord: BaseCoord,
    to_system: str,  # 'icrs', 'galactic', 'horizontal', 'altaz'
    latitude: Optional[Angle] = None,
    longitude: Optional[Angle] = None,
    jd: Optional[JulianDate] = None,
    verbose: Optional[VerboseContext] = None
) -> BaseCoord
```

---

## astr0.core.constants

### AstronomicalConstants Class

Singleton providing access to astronomical constants.

```python
from astr0.core.constants import AstronomicalConstants

const = AstronomicalConstants()

# Access constants as attributes
const.c          # Constant object for speed of light
const.c.value    # 299792458
const.c.unit     # "m/s"
const.c.reference  # "SI 2019 (exact)"
const.c.uncertainty  # None (exact)

# Available constants
const.c              # Speed of light
const.G              # Gravitational constant
const.AU             # Astronomical Unit
const.JD_J2000       # Julian Date of J2000.0
const.MJD_OFFSET     # Modified JD offset
const.julian_year    # Julian year (days)
const.julian_century # Julian century (days)
const.arcsec_per_rad # Arcseconds per radian
const.earth_radius_eq   # Earth equatorial radius
const.earth_flattening  # Earth flattening
const.earth_rotation_rate  # Earth rotation rate
const.obliquity_j2000   # Mean obliquity at J2000.0
const.ra_ngp         # RA of North Galactic Pole
const.dec_ngp        # Dec of North Galactic Pole
const.l_ncp          # Galactic lon of North Celestial Pole
const.M_sun          # Solar mass
const.R_sun          # Solar radius
const.L_sun          # Solar luminosity
```

### Methods

```python
const = AstronomicalConstants()

# List all constants
for c in const.all():
    print(f"{c.name}: {c.value} {c.unit or ''}")

# Search by name
for c in const.search("solar"):
    print(c.name, c.value)
```

---

## astr0.verbose

### VerboseContext Class

Collect calculation steps for educational output.

```python
from astr0.verbose import VerboseContext, step

# Create context
ctx = VerboseContext()

# Pass to calculations
from astr0.core.angles import angular_separation, Angle
ra1, dec1 = Angle(hours=10), Angle(degrees=30)
ra2, dec2 = Angle(hours=11), Angle(degrees=31)
sep = angular_separation(ra1, dec1, ra2, dec2, verbose=ctx)

# Display steps
ctx.print_steps()

# Or get as string
output = ctx.format_steps()

# Or get as dict (for JSON)
data = ctx.to_dict()

# Clear and reuse
ctx.clear()
```

### Adding Steps in Custom Code

```python
from astr0.verbose import VerboseContext, step

def my_calculation(x, y, verbose=None):
    """Custom calculation with verbose support."""
    
    step(verbose, "Input", f"x = {x}, y = {y}")
    
    result = x * y
    step(verbose, "Multiply", f"x × y = {result}")
    
    return result

# Use it
ctx = VerboseContext()
result = my_calculation(3, 4, verbose=ctx)
ctx.print_steps()
```

---

## Complete Example

```python
"""
Calculate when M31 is highest in the sky from a given location.
"""

from astr0.core.coords import ICRSCoord, HorizontalCoord
from astr0.core.time import JulianDate, jd_now
from astr0.core.angles import Angle
from astr0.verbose import VerboseContext

# M31 coordinates
m31 = ICRSCoord.from_string("00h42m44s +41d16m09s")

# Observer: New York City
lat = Angle(degrees=40.7128)
lon = Angle(degrees=-74.0060)

# Current position
jd = jd_now()
ctx = VerboseContext()

horiz = m31.to_horizontal(lat, lon, jd, verbose=ctx)

print(f"M31 from NYC at JD {jd.jd:.2f}:")
print(f"  Altitude: {horiz.alt.to_dms()}")
print(f"  Azimuth:  {horiz.az.degrees:.1f}°")
print(f"  Airmass:  {horiz.airmass:.2f}")

if horiz.alt.degrees > 0:
    print("  Status: VISIBLE")
else:
    print("  Status: Below horizon")

# Show the math
print("\n--- Calculation Steps ---")
ctx.print_steps()
```

---

## Type Hints

All astr0 functions have full type hints:

```python
from astr0.core.angles import Angle, angular_separation
from astr0.core.time import JulianDate
from astr0.verbose import VerboseContext
from typing import Optional

def angular_separation(
    ra1: Angle,
    dec1: Angle, 
    ra2: Angle,
    dec2: Angle,
    verbose: Optional[VerboseContext] = None
) -> Angle: ...
```

This enables IDE autocompletion and static type checking with mypy.

---

## Error Handling

astr0 uses standard Python exceptions:

```python
from astr0.core.angles import Angle

try:
    # Invalid: multiple units specified
    a = Angle(degrees=45, hours=3)
except ValueError as e:
    print(f"Error: {e}")

try:
    # Invalid: unparseable string
    a = Angle.parse("not an angle")
except ValueError as e:
    print(f"Parse error: {e}")
```

---

*For more information, see the [source code](https://github.com/yourusername/astr0) or open an issue!*
