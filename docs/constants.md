# Astronomical Constants

Astronomy relies on precisely measured physical constants and defined reference values. This guide explains the constants available in astr0 and their significance.

---

## Why Constants Matter

Every astronomical calculation depends on physical constants and conventional reference values. Using outdated or inconsistent constants leads to systematic errors. astr0 uses the most recent authoritative values from:

- **IAU** — International Astronomical Union (astronomical definitions)
- **CODATA** — Committee on Data for Science and Technology (physical constants)
- **IERS** — International Earth Rotation Service (Earth parameters)
- **SI** — International System of Units (fundamental definitions)

---

## Viewing Constants

### List All Constants

```bash
astr0 constants list
```

### Search for Constants

```bash
astr0 constants search solar
```

### Show a Specific Constant

```bash
astr0 constants show c
```

---

## Fundamental Physical Constants

### Speed of Light (c)

| Property | Value |
|----------|-------|
| Value | 299,792,458 m/s |
| Uncertainty | Exact (defined) |
| Reference | SI 2019 |

Since 2019, the meter is defined such that light travels exactly 299,792,458 meters per second. This makes c an exact constant by definition.

**In astronomy**: Light travel time is often more practical than distance. "The Sun is 8.3 light-minutes away."

---

### Gravitational Constant (G)

| Property | Value |
|----------|-------|
| Value | 6.67430 × 10⁻¹¹ m³/(kg·s²) |
| Uncertainty | ±0.00015 × 10⁻¹¹ |
| Reference | CODATA 2018 |

G is notoriously difficult to measure precisely. It's the least precisely known fundamental constant!

**In astronomy**: Appears in Kepler's third law, orbital mechanics, and gravitational physics.

$$M = \frac{4\pi^2 a^3}{G P^2}$$

---

## Astronomical Distance Units

### The Astronomical Unit (AU)

| Property | Value |
|----------|-------|
| Value | 149,597,870,700 m |
| Uncertainty | Exact (defined) |
| Reference | IAU 2012 |

The AU was historically the Earth-Sun distance, but since 2012 it's a defined constant. It's approximately the mean distance from Earth to Sun.

**Use**: Solar system distances. Jupiter is ~5.2 AU from the Sun.

**Light-time**: 1 AU ≈ 499 seconds ≈ 8.3 minutes

---

## Time Constants

### Julian Date of J2000.0

| Property | Value |
|----------|-------|
| Value | 2,451,545.0 days |
| Reference | IAU (exact) |

The standard astronomical epoch: January 1, 2000 at 12:00:00 TT.

---

### Julian Year

| Property | Value |
|----------|-------|
| Value | 365.25 days |
| Reference | IAU (exact) |

A defined unit of time, not the actual tropical or sidereal year (which vary).

---

### Julian Century

| Property | Value |
|----------|-------|
| Value | 36,525 days |
| Reference | IAU (exact) |

100 Julian years. Used in precession and nutation calculations.

---

### Modified Julian Date Offset

| Property | Value |
|----------|-------|
| Value | 2,400,000.5 days |
| Reference | IAU (exact) |

MJD = JD - 2,400,000.5

---

## Angular Constants

### Arcseconds per Radian

| Property | Value |
|----------|-------|
| Value | 206,264.806247... |
| Reference | Derived (exact) |

$$\frac{180° \times 3600"}{\pi} = \frac{648000}{\pi} \approx 206264.806$$

Essential for small-angle conversions.

---

### Mean Obliquity at J2000.0

| Property | Value |
|----------|-------|
| Value | 23.439291111° |
| Reference | IAU 2006 |

The angle between Earth's equator and the ecliptic plane at J2000.0. This value slowly changes due to precession and nutation.

**Also known as**: ε₀ (epsilon-naught)

---

## Earth Parameters

### Earth Equatorial Radius

| Property | Value |
|----------|-------|
| Value | 6,378,137 m |
| Reference | WGS84 |

The semi-major axis of the WGS84 reference ellipsoid.

---

### Earth Flattening

| Property | Value |
|----------|-------|
| Value | 1/298.257223563 |
| Reference | WGS84 |

Earth is an oblate spheroid—the equatorial radius exceeds the polar radius by about 21 km.

$$f = \frac{a - b}{a}$$

Where a is equatorial radius and b is polar radius.

---

### Earth Rotation Rate

| Property | Value |
|----------|-------|
| Value | 7.292115 × 10⁻⁵ rad/s |
| Reference | IERS |

Angular velocity of Earth's rotation.

$$\omega = \frac{2\pi}{86164.1} \text{ rad/s}$$

(86,164.1 seconds is a sidereal day)

---

## Galactic Reference Frame

### North Galactic Pole (ICRS)

| Coordinate | Value |
|------------|-------|
| RA | 192.859508333° = 12h 51m 26.28s |
| Dec | +27.128336111° = +27° 07' 42" |
| Reference | IAU 1958, precessed to J2000 |

The direction perpendicular to the Galactic plane, in the northern hemisphere.

---

### Galactic Longitude of Ascending Node

| Property | Value |
|----------|-------|
| Value | 32.932° |
| Reference | IAU 1958 |

The galactic longitude where the Galactic plane crosses the celestial equator heading north. Used in coordinate transformations.

---

## Solar Constants

### Solar Mass (M☉)

| Property | Value |
|----------|-------|
| Value | 1.98841 × 10³⁰ kg |
| Uncertainty | ±4 × 10²⁵ kg |
| Reference | IAU 2015 |

The Sun contains 99.86% of the Solar System's mass. Stellar masses are typically expressed in solar masses (M☉).

**Note**: The product GM☉ is known much more precisely than M☉ or G individually!

---

### Solar Radius (R☉)

| Property | Value |
|----------|-------|
| Value | 695,700,000 m |
| Uncertainty | Nominal (defined) |
| Reference | IAU 2015 |

The IAU nominal solar radius, used as a reference for other stars.

---

### Solar Luminosity (L☉)

| Property | Value |
|----------|-------|
| Value | 3.828 × 10²⁶ W |
| Uncertainty | Nominal (defined) |
| Reference | IAU 2015 |

Total electromagnetic power output of the Sun. Stellar luminosities are expressed in L☉.

---

## Using Constants in Calculations

### Example: How long for light to reach us from the Sun?

$$t = \frac{AU}{c} = \frac{149597870700 \text{ m}}{299792458 \text{ m/s}} = 499.0 \text{ s} \approx 8.3 \text{ min}$$

### Example: Earth's orbital velocity

$$v = \frac{2\pi \times AU}{P} \approx \frac{2\pi \times 1.496 \times 10^{11}}{365.25 \times 86400} \approx 29.8 \text{ km/s}$$

### Example: Solar angular diameter

$$\theta = 2 \times \arctan\left(\frac{R_☉}{AU}\right) \approx \frac{2 \times 695700000}{149597870700} \times 206264.8 \approx 1919" \approx 32'$$

---

## Python API

```python
from astr0.core.constants import AstronomicalConstants

# Get the singleton
const = AstronomicalConstants()

# Access individual constants
print(f"Speed of light: {const.c.value} {const.c.unit}")
print(f"Reference: {const.c.reference}")

# Access as attributes
print(f"AU = {const.AU.value} m")
print(f"Solar mass = {const.M_sun.value} kg")
print(f"J2000.0 = JD {const.JD_J2000.value}")

# List all constants
for c in const.all():
    print(f"{c.name}: {c.value} {c.unit or ''}")

# Search constants
for c in const.search("solar"):
    print(f"{c.name}: {c.value}")
```

---

## Complete Constants Reference

| Name | Symbol | Value | Unit | Source |
|------|--------|-------|------|--------|
| Speed of light | c | 299,792,458 | m/s | SI 2019 |
| Gravitational constant | G | 6.67430×10⁻¹¹ | m³/(kg·s²) | CODATA 2018 |
| Astronomical Unit | AU | 1.495978707×10¹¹ | m | IAU 2012 |
| Julian Date J2000.0 | JD₀ | 2,451,545.0 | days | IAU |
| Modified JD offset | MJD₀ | 2,400,000.5 | days | IAU |
| Julian year | — | 365.25 | days | IAU |
| Julian century | — | 36,525 | days | IAU |
| Arcsec per radian | ρ | 206,264.806 | ″/rad | Derived |
| Mean obliquity (J2000) | ε₀ | 23.4393° | — | IAU 2006 |
| Earth equatorial radius | a | 6,378,137 | m | WGS84 |
| Earth flattening | f | 1/298.257 | — | WGS84 |
| Earth rotation rate | ω | 7.292115×10⁻⁵ | rad/s | IERS |
| North Galactic Pole RA | α_NGP | 192.8595° | — | IAU 1958 |
| North Galactic Pole Dec | δ_NGP | 27.1283° | — | IAU 1958 |
| Galactic lon. asc. node | l_Ω | 32.932° | — | IAU 1958 |
| Solar mass | M☉ | 1.98841×10³⁰ | kg | IAU 2015 |
| Solar radius | R☉ | 6.957×10⁸ | m | IAU 2015 |
| Solar luminosity | L☉ | 3.828×10²⁶ | W | IAU 2015 |

---

## References

- IAU NSFA: [Nominal Solar and Planetary Values](https://www.iau.org/static/resolutions/IAU2015_English.pdf)
- CODATA: [Fundamental Physical Constants](https://physics.nist.gov/cuu/Constants/)
- IERS: [IERS Conventions](https://www.iers.org/IERS/EN/Publications/TechnicalNotes/tn36.html)
- Explanatory Supplement to the Astronomical Almanac, 3rd ed.

---

*Next: [Verbose Mode](verbose.md) — The "show your work" system*
