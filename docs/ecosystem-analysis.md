# starward Ecosystem Analysis

> An analysis of starward's position in the Python astronomy ecosystem alongside astropy and astroquery.

---

## Executive Summary

starward occupies a unique niche in the Python astronomy ecosystem. While **astropy** serves as the comprehensive, enterprise-grade foundation and **astroquery** provides unified access to remote astronomical databases, starward focuses on **transparent, educational, pure-Python astronomical calculations** with a "show your work" philosophy.

| Aspect | astropy | astroquery | starward |
|--------|---------|------------|----------|
| **Primary Purpose** | Core astronomy infrastructure | Remote data access | Transparent calculations |
| **Philosophy** | Comprehensive & performant | Unified API for services | Educational & inspectable |
| **Dependencies** | NumPy, ERFA (C library) | astropy + requests | Pure Python (click, rich) |
| **Target User** | Professional astronomers | Data-driven researchers | Learners, educators, CLI users |
| **Complexity** | High (steep learning curve) | Medium | Low (immediate productivity) |

---

## The Ecosystem Players

### astropy (v7.2.0)

The **de facto standard** for Python astronomy. A community-driven project providing foundational infrastructure.

**Core Modules:**
- **Units & Quantities**: Physical units with automatic conversion
- **Coordinates**: Comprehensive coordinate frame transformations (ICRS, Galactic, AltAz, etc.)
- **Time**: High-precision time handling (dual 64-bit floats for nanosecond accuracy over Gyr)
- **Tables**: Astronomy-focused tabular data (like pandas but for FITS)
- **FITS I/O**: Reading/writing FITS files (images, tables, headers)
- **WCS**: World Coordinate System transformations
- **Modeling**: Mathematical model fitting framework
- **Cosmology**: Cosmological distance calculations

**Strengths:**
- Industry standard, widely adopted
- Extremely comprehensive
- High performance (C extensions via ERFA)
- Excellent documentation
- Large community and ecosystem

**Weaknesses:**
- Heavy dependency footprint
- Steep learning curve
- Opaque calculations (no "show your work")
- Overkill for simple tasks

**Sources:** [astropy.org](https://www.astropy.org/), [docs](https://docs.astropy.org/en/stable/index.html), [PyPI](https://pypi.org/project/astropy/)

---

### astroquery (v0.4.11)

A **unified interface** to astronomical databases and archives. An astropy affiliated package.

**Supported Services (40+):**
- **Catalogs**: SIMBAD, VizieR, NED, SDSS, GAMA, UKIDSS
- **Space Archives**: MAST (HST, JWST), ESO, Gemini, ALMA, Gaia, XMM-Newton
- **Spectroscopy**: HITRAN, JPL Spectroscopy, Splatalogue, NIST
- **Solar System**: JPL Horizons, Minor Planet Center
- **Other**: NASA ADS, Astrometry.net, SkyView image cutouts

**Strengths:**
- Unified API across all services
- Continuous deployment model
- Reproducible data workflows
- Handles authentication for proprietary data

**Weaknesses:**
- Requires astropy
- Network-dependent
- API changes with upstream services
- No offline capability

**Sources:** [astroquery docs](https://astroquery.readthedocs.io/), [PyPI](https://pypi.org/project/astroquery/), [GitHub](https://github.com/astropy/astroquery)

---

### starward (v0.3.0)

A **transparent, educational astronomy toolkit** with CLI-first design.

**Core Modules:**
- **Time**: Julian dates, MJD, LST, GMST (IAU 2006)
- **Coordinates**: ICRS, Galactic, Horizontal, Ecliptic transformations
- **Angles**: Separation (Vincenty), position angle, parsing/formatting
- **Constants**: 30+ IAU/CODATA constants with references
- **Sun**: Position, rise/set, twilight (civil/nautical/astronomical)
- **Moon**: Position, phases, illumination, age
- **Planets**: Mercury-Neptune positions (Meeus algorithms)
- **Visibility**: Airmass (Pickering 2002), transit, rise/set
- **Observer**: Location management with TOML persistence
- **Messier**: Complete 110-object catalog

**Strengths:**
- Pure Python (no compiled dependencies)
- "Show your work" verbose mode
- Immediate CLI productivity
- Lightweight and portable
- Educational focus with explicit algorithms
- Immutable, thread-safe results

**Weaknesses:**
- Smaller feature set
- No FITS I/O
- No remote data access
- Less precise than ERFA-backed calculations

---

## Compatibility & Integration Analysis

### starward + astropy

**Current State:** No integration. starward is fully independent.

**Integration Opportunities:**

| Feature | Approach | Benefit |
|---------|----------|---------|
| **Coordinate interop** | Accept/return `astropy.coordinates.SkyCoord` | Seamless data exchange |
| **Time interop** | Accept/return `astropy.time.Time` | Use astropy's precision when needed |
| **Units awareness** | Support `astropy.units.Quantity` | Unit safety at boundaries |
| **Table output** | Return `astropy.table.Table` | Direct pipeline integration |

**Recommended Strategy:**
```python
# Optional astropy interop (don't require it)
def to_skycoord(self) -> "SkyCoord":
    """Convert to astropy SkyCoord if available."""
    try:
        from astropy.coordinates import SkyCoord
        import astropy.units as u
        return SkyCoord(ra=self.ra.degrees*u.deg, dec=self.dec.degrees*u.deg)
    except ImportError:
        raise ImportError("astropy required for SkyCoord conversion")
```

**Key Principle:** astropy should be an **optional** enhancement, never a requirement.

---

### starward + astroquery

**Current State:** No integration.

**Integration Opportunities:**

| Use Case | Implementation |
|----------|----------------|
| **Object lookup** | Use SIMBAD/NED to resolve names to coordinates |
| **Catalog enrichment** | Pull NGC/IC data from VizieR |
| **Ephemeris validation** | Cross-check against JPL Horizons |
| **Image overlays** | Fetch DSS/SkyView cutouts for targets |

**Recommended Strategy:**
- Keep core starward calculations offline-capable
- Add optional `starward.remote` module for astroquery integration
- Cache remote lookups locally

```python
# Optional remote module
# starward/remote/simbad.py
def resolve_object(name: str) -> ICRSCoord:
    """Resolve object name via SIMBAD."""
    from astroquery.simbad import Simbad
    result = Simbad.query_object(name)
    # ... convert to starward.ICRSCoord
```

---

## How starward Differentiates

### 1. Transparency ("Show Your Work")

**astropy:**
```python
from astropy.coordinates import SkyCoord
coord = SkyCoord("10h20m30s", "+40d50m60s", frame='icrs')
altaz = coord.transform_to(AltAz(obstime=time, location=loc))
# Result appears; calculation is opaque
```

**starward:**
```bash
$ starward --verbose coords convert "10h20m30s +40d50m60s" --to horizontal
═══ Coordinate Transformation ═══
Input: ICRS 10h20m30.00s +40°51'00.0"
Target: Horizontal (Alt/Az)

Step 1: Convert RA to degrees
  RA = 10h 20m 30s = (10 + 20/60 + 30/3600) × 15 = 155.125°

Step 2: Calculate Local Sidereal Time
  GMST = 280.46061837 + 360.98564736629 × (JD - 2451545.0)
  ...

Step 3: Hour Angle
  HA = LST - RA = ...
```

This transparency is **invaluable for education** and **debugging**.

---

### 2. Zero Compiled Dependencies

| Package | Binary Dependencies |
|---------|---------------------|
| astropy | NumPy, ERFA (C library), possibly SciPy |
| astroquery | astropy + all its dependencies |
| starward | None (pure Python) |

**Benefits:**
- Runs anywhere Python runs (including restricted environments)
- Source is fully inspectable
- No build failures on obscure platforms
- Easy to embed in other applications

---

### 3. CLI-First Design

starward is designed as a **command-line tool first**, library second.

```bash
# Quick answers without writing code
$ starward sun rise --observer greenwich
Sunrise: 07:42:15 UTC

$ starward moon phase
Waxing Gibbous (78% illuminated)

$ starward planets all --observer home
┌─────────┬────────────┬────────────┬───────┬───────────┐
│ Planet  │ RA         │ Dec        │ Mag   │ Distance  │
├─────────┼────────────┼────────────┼───────┼───────────┤
│ Mercury │ 18h42m12s  │ -24°15'32" │ -0.3  │ 0.92 AU   │
...
```

astropy requires writing Python code for even simple queries.

---

### 4. Educational Focus

starward algorithms are:
- Explicitly documented with source references (Meeus, IAU, USNO)
- Implemented readably rather than for maximum performance
- Testable against authoritative sources
- Designed to teach, not just compute

---

## Feature Comparison Matrix

| Feature | astropy | astroquery | starward |
|---------|:-------:|:----------:|:--------:|
| Julian Date conversion | ✅ | — | ✅ |
| Coordinate transforms | ✅ | — | ✅ |
| Solar position | ✅ | — | ✅ |
| Lunar position/phase | ✅ | — | ✅ |
| Planetary ephemerides | ✅ (via jplephem) | ✅ (Horizons) | ✅ (Meeus) |
| Rise/set/transit | ✅ | — | ✅ |
| Airmass | ✅ | — | ✅ |
| FITS I/O | ✅ | — | ❌ |
| WCS | ✅ | — | ❌ |
| Units system | ✅ | — | ❌ |
| Remote catalogs | — | ✅ | ❌ |
| Image queries | — | ✅ | ❌ |
| Spectral lines | — | ✅ | ❌ |
| Verbose mode | ❌ | ❌ | ✅ |
| CLI interface | ❌ | ❌ | ✅ |
| Zero dependencies | ❌ | ❌ | ✅ |
| Messier catalog | ❌ | ✅ (VizieR) | ✅ (built-in) |

---

## Strategic Recommendations

### 1. Embrace the Niche

starward should **not** try to be astropy. Instead, lean into:
- **Education**: The best tool for learning astronomical calculations
- **Transparency**: The only tool that shows its work
- **Simplicity**: Immediate answers without boilerplate
- **Portability**: Runs anywhere, no compilation needed

### 2. Optional Integration, Not Dependency

```python
# Good: Optional interop
extras_require = {
    "astropy": ["astropy>=5.0"],
    "remote": ["astroquery>=0.4"],
}

# Bad: Hard dependency
install_requires = ["astropy>=5.0"]  # Don't do this
```

### 3. Features to Implement Natively

These should be in starward core (no external dependencies):

| Feature | Rationale |
|---------|-----------|
| **NGC/IC catalogs** | Essential DSO data, static dataset |
| **Hipparcos bright stars** | Core star catalog, static dataset |
| **Precession/nutation** | Fundamental calculation |
| **Refraction corrections** | Needed for accurate rise/set |
| **Extinction (basic)** | Galactic extinction models |
| **Cosmological distances** | Hubble law, luminosity distance |

### 4. Features to Delegate to astroquery

These require network access and change frequently:

| Feature | Why Delegate |
|---------|--------------|
| **SIMBAD lookups** | Live database, name resolution |
| **VizieR queries** | Massive catalog access |
| **JPL Horizons** | Authoritative ephemerides |
| **MAST archives** | HST/JWST data access |

### 5. Features to NOT Implement

Leave these to astropy (not worth duplicating):

| Feature | Why Skip |
|---------|----------|
| **FITS I/O** | Complex, well-solved by astropy |
| **WCS** | Requires WCSLIB, astropy does it right |
| **Full units system** | Massive undertaking, astropy's is excellent |
| **Model fitting** | scipy/astropy territory |

---

## Proposed Integration Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Application                      │
└─────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        ▼                   ▼                   ▼
┌───────────────┐   ┌───────────────┐   ┌───────────────┐
│   starward    │   │   starward    │   │   starward    │
│   (core)      │   │   .astropy    │   │   .remote     │
│               │   │   (optional)  │   │   (optional)  │
│ Pure Python   │   │ Interop layer │   │ Query layer   │
│ calculations  │   │               │   │               │
└───────────────┘   └───────┬───────┘   └───────┬───────┘
                            │                   │
                            ▼                   ▼
                    ┌───────────────┐   ┌───────────────┐
                    │    astropy    │   │  astroquery   │
                    └───────────────┘   └───────────────┘
```

---

## Versioning Strategy

| Version | Focus | astropy/astroquery Integration |
|---------|-------|-------------------------------|
| v0.4 | Deep Sky catalogs (NGC, IC, Hipparcos) | None (native implementation) |
| v0.5 | Cosmology, extinction | None (native implementation) |
| v0.6 | Observatory tools | Consider optional astropy interop |
| v1.0 | Stable API | Optional `starward.astropy` module |
| v1.1+ | Remote data | Optional `starward.remote` module |

---

## Conclusion

starward's value proposition is clear:

> **"The astronomy toolkit that shows its work."**

It serves users who:
- Want to **understand** calculations, not just get results
- Need **quick CLI answers** without writing code
- Work in **restricted environments** without compiled dependencies
- Are **learning** astronomy and want inspectable algorithms
- Value **simplicity** over comprehensiveness

The path forward is to:
1. Stay independent (no hard dependencies on astropy/astroquery)
2. Offer optional integration for power users
3. Implement core catalogs natively (Messier ✅, NGC, IC, Hipparcos)
4. Delegate live data access to astroquery when needed
5. Never compromise the "show your work" philosophy

---

## Architectural Lessons from astropy/astroquery

### 1. Module Organization Pattern

**astropy's approach:**
```
astropy/
├── coordinates/     # Each subpackage is self-contained
│   ├── __init__.py  # Public API exports
│   ├── core.py      # Core implementation
│   ├── tests/       # Tests live with the module
│   └── data/        # Module-specific data files
├── time/
├── units/
└── ...
```

**astroquery's template pattern:**
Every service module follows an identical structure:
```
astroquery/
├── simbad/
│   ├── __init__.py
│   ├── core.py      # Inherits from BaseQuery
│   └── tests/
├── vizier/
└── template/        # Copy this for new modules
```

**Lesson for starward:**
- ✅ Already follows this pattern (`core/`, `cli/`, `output/`)
- Consider adding a `template/` module for contributors
- Keep tests alongside modules (currently in separate `tests/` tree—both approaches are valid)

### 2. Base Class Pattern (astroquery)

astroquery uses `BaseQuery` that all service classes inherit:

```python
from astroquery.query import BaseQuery

class SimbadClass(BaseQuery):
    """All queries inherit common functionality."""

    def query_object(self, object_name):
        # Delegates to async version
        ...

    def query_object_async(self, object_name):
        # Actual HTTP request
        response = self._request('GET', url, params=params)
        return self._parse_result(response)
```

**Lesson for starward:**
Consider a `BaseCalculation` pattern for verbose output:

```python
class BaseCalculation:
    """Base for calculations that support verbose output."""

    def __init__(self, verbose_context=None):
        self.verbose = verbose_context

    def step(self, name, formula, result):
        """Record a calculation step."""
        if self.verbose:
            self.verbose.add_step(name, formula, result)
        return result
```

### 3. Lazy Import Strategy

**astropy's approach:**
Core package is importable with minimal dependencies. Heavy subpackages load on demand:

```python
# Fast: only loads core
import astropy

# Slow: loads coordinates machinery
from astropy.coordinates import SkyCoord
```

**Lesson for starward:**
- ✅ Already doing this with Click's lazy command loading
- Consider lazy loading for heavy data (NGC catalog, star catalogs)

```python
# starward/core/catalogs/__init__.py
def get_ngc():
    """Load NGC catalog on first access."""
    from .ngc_data import NGC_CATALOG
    return NGC_CATALOG
```

### 4. Optional Dependencies Pattern

**astropy's approach:**
```python
# astropy/utils/compat/optional_deps.py
try:
    import scipy
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

# In tests
@pytest.mark.skipif(not HAS_SCIPY, reason='scipy required')
def test_that_uses_scipy():
    ...
```

**Lesson for starward:**
Prepare for optional astropy/astroquery integration:

```python
# starward/compat.py
try:
    from astropy.coordinates import SkyCoord
    HAS_ASTROPY = True
except ImportError:
    HAS_ASTROPY = False

try:
    from astroquery.simbad import Simbad
    HAS_ASTROQUERY = True
except ImportError:
    HAS_ASTROQUERY = False
```

---

## Testing Lessons from astropy

### 1. Test Categories (Markers)

**astropy's markers:**
```python
@pytest.mark.slow           # Long-running tests
@pytest.mark.remote_data    # Requires network
@pytest.mark.filterwarnings # Expected warnings
```

**starward's current markers:**
```python
@pytest.mark.slow      # ✅ Already have
@pytest.mark.golden    # ✅ Tests against known values
@pytest.mark.roundtrip # ✅ Transform/inverse identity
@pytest.mark.edge      # ✅ Edge cases
@pytest.mark.verbose   # ✅ Verbose output tests
```

**Additional markers to consider:**
```python
@pytest.mark.remote    # For future astroquery integration tests
@pytest.mark.catalog   # Tests requiring large catalog data
```

### 2. Golden Test Pattern

**astropy validates against:**
- JPL Horizons ephemerides
- IAU SOFA reference implementations
- USNO almanac data

**starward should:**
- ✅ Already validates against JPL Horizons, USNO, Meeus
- Document the golden values with sources
- Add date stamps to golden tests (values can change with new data)

```python
@pytest.mark.golden
def test_mars_position_j2000():
    """
    Golden test: Mars position at J2000.0
    Source: JPL Horizons, retrieved 2024-01-15
    Target: Mars (499), Observer: @sun
    """
    jd = JulianDate(2451545.0)
    pos = planet_position(Planet.MARS, jd)

    # Expected from JPL Horizons
    assert abs(pos.helio_longitude.degrees - 327.832) < 0.01
```

### 3. Parametrized Testing

**astropy uses extensively:**
```python
@pytest.mark.parametrize('frame', ['icrs', 'galactic', 'fk5'])
@pytest.mark.parametrize('angle', [0, 90, 180, 270])
def test_coordinate_transforms(frame, angle):
    ...
```

**starward's conftest.py provides:**
```python
STANDARD_ANGLES = [0, 1, 30, 45, 60, 89.9, 90, ...]
STANDARD_LATITUDES = [-90, -66.5, -45, -23.5, 0, ...]
```

**Expand to:**
```python
STANDARD_JULIAN_DATES = [
    2451545.0,    # J2000.0
    2440587.5,    # Unix epoch
    2459580.5,    # Recent date
]

STANDARD_PLANETS = list(Planet)

@pytest.mark.parametrize('jd', STANDARD_JULIAN_DATES)
@pytest.mark.parametrize('planet', STANDARD_PLANETS)
def test_planet_positions_valid(jd, planet):
    """All planets return valid positions for all test dates."""
    pos = planet_position(planet, JulianDate(jd))
    assert 0 <= pos.ra.degrees < 360
    assert -90 <= pos.dec.degrees <= 90
```

### 4. Property-Based Testing (Hypothesis)

**astropy uses Hypothesis for:**
- Numerical stability across random inputs
- Edge case discovery
- Invariant verification

**Lesson for starward:**
```python
from hypothesis import given, strategies as st

@given(st.floats(min_value=0, max_value=360))
def test_angle_normalization_idempotent(deg):
    """Normalizing a normalized angle returns the same value."""
    angle = Angle(degrees=deg).normalize()
    assert angle.normalize().degrees == angle.degrees

@given(st.floats(min_value=2400000, max_value=2500000))
def test_jd_roundtrip(jd_value):
    """JD → UTC → JD roundtrip preserves value."""
    jd = JulianDate(jd_value)
    utc = jd.to_utc()
    jd2 = JulianDate.from_utc(utc)
    assert abs(jd.jd - jd2.jd) < 1e-9
```

### 5. Doctest Integration

**astropy embeds examples in docstrings:**
```python
def angular_separation(ra1, dec1, ra2, dec2):
    """
    Calculate angular separation.

    Examples
    --------
    >>> from starward.core.angles import angular_separation, Angle
    >>> sep = angular_separation(
    ...     Angle(degrees=0), Angle(degrees=0),
    ...     Angle(degrees=1), Angle(degrees=0)
    ... )
    >>> abs(sep.degrees - 1.0) < 0.0001
    True
    """
```

**Enable in pytest:**
```ini
# pyproject.toml
[tool.pytest.ini_options]
addopts = "--doctest-modules"
```

### 6. Fixture Organization (starward already excellent)

starward's `conftest.py` demonstrates best practices:
- **Tolerance fixtures**: `angle_tolerance`, `time_tolerance`
- **Domain fixtures**: `greenwich`, `mauna_kea`, `famous_stars`
- **Assertion helpers**: `assert_angle_close`, `assert_coord_close`
- **Parameterized data**: `STANDARD_ANGLES`, `STANDARD_LATITUDES`

**Additional patterns to adopt:**
```python
@pytest.fixture(scope="session")
def ngc_catalog():
    """Load NGC catalog once per test session."""
    from starward.core.catalogs import load_ngc
    return load_ngc()

@pytest.fixture
def tmp_observer_config(tmp_path):
    """Temporary observer config for isolation."""
    config_file = tmp_path / "observers.toml"
    yield config_file
    # Cleanup happens automatically
```

### 7. Test Data Management

**astropy's approach:**
- `get_pkg_data_filename()` - finds test data files
- Remote data cached locally with MD5 verification
- `@pytest.mark.remote_data` for network tests

**Lesson for starward:**
```python
# starward/tests/data/
#   golden_values.json      # Known-good values
#   jpl_horizons_mars.json  # JPL reference data

def get_test_data(filename):
    """Load test data file."""
    import json
    from pathlib import Path
    data_dir = Path(__file__).parent / "data"
    with open(data_dir / filename) as f:
        return json.load(f)

# Usage
def test_mars_against_jpl():
    jpl_data = get_test_data("jpl_horizons_mars.json")
    ...
```

---

## CI/CD Lessons

### 1. Multi-Platform Testing

**astropy tests on:**
- Linux (Ubuntu)
- macOS
- Windows
- Multiple Python versions (3.10, 3.11, 3.12)

**Recommendation for starward:**
```yaml
# .github/workflows/test.yml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    python-version: ['3.10', '3.11', '3.12']
```

### 2. Coverage Enforcement

**astropy tracks coverage per subpackage.**

**Recommendation:**
```yaml
- name: Upload coverage
  uses: codecov/codecov-action@v4
  with:
    fail_ci_if_error: true
    threshold: 90%
```

### 3. Documentation Testing

**astropy builds docs in CI and fails on warnings.**

**Recommendation:**
```yaml
- name: Build docs
  run: |
    cd website
    npm run build
  # Fail on broken links, missing refs
```

---

## Summary: What to Adopt

| Pattern | Priority | Effort | Value |
|---------|----------|--------|-------|
| Property-based testing (Hypothesis) | High | Low | Catches edge cases |
| Golden test documentation | High | Low | Traceability |
| Parametrized test expansion | Medium | Low | Coverage |
| Optional dependency pattern | High | Medium | Future integration |
| Doctest integration | Medium | Low | Living docs |
| Multi-platform CI | High | Medium | Reliability |
| Session-scoped fixtures for catalogs | Medium | Low | Test speed |
| `@pytest.mark.remote` for future | Low | Low | Preparation |

**Sources:**
- [astropy Testing Guide](https://docs.astropy.org/en/stable/development/testguide.html)
- [astroquery Template Module](https://astroquery.readthedocs.io/en/latest/template.html)
- [astroquery Contributing Guide](https://github.com/astropy/astroquery/blob/main/CONTRIBUTING.rst)
- [Astropy Affiliated Packages](https://www.astropy.org/affiliated/)

---

*Analysis prepared for starward v0.3.0 ecosystem positioning*
