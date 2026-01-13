# starward — Astronomy Calculation Toolkit

> *"Per aspera ad astra"* — Through hardships to the stars

A professional astronomy calculation toolkit with a soul. Built for astronomers, astrophysicists, and curious stargazers who appreciate precision, transparency, and the occasional cosmic pun.

---

## Vision

**"The astronomy toolkit that shows its work."**

starward exists to serve users who:
- Want to **understand** calculations, not just get results
- Need **quick CLI answers** without writing code
- Work in **restricted environments** without compiled dependencies
- Are **learning** astronomy and want inspectable algorithms
- Value **simplicity** over comprehensiveness

We complement the ecosystem—not compete with it. astropy is the industrial foundation; starward is the transparent teaching tool.

---

## Philosophy

- **Precision First**: Every calculation traceable, every assumption explicit
- **Show Your Work**: Verbose mode that would make your physics professor proud
- **Modular by Design**: Each module stands alone, plays well with others
- **Test Everything**: If it's not tested, it doesn't exist
- **Expand Gracefully**: Architecture that welcomes new features like old friends
- **Stay Independent**: No required dependencies on astropy/astroquery
- **Integrate Optionally**: Play nice with the ecosystem when users want it

---

## Completed Releases

### v0.1 — "First Light" ✅

The foundational release. Core infrastructure and essential calculations.

| Module | Description | Status |
|--------|-------------|--------|
| `time` | Julian dates, MJD, LST, epoch conversions | ✅ |
| `coords` | Coordinate transformations (ICRS, AltAz, Galactic, Ecliptic) | ✅ |
| `angles` | Angular separations, position angles, formatting | ✅ |
| `constants` | Astronomical constants with references | ✅ |

**Infrastructure**: CLI framework, verbose output, JSON export, >90% test coverage

---

### v0.2 — "Steady Tracking" ✅

Position calculations and solar system awareness.

| Module | Description | Status |
|--------|-------------|--------|
| `sun` | Solar position, sunrise/sunset, twilight | ✅ |
| `moon` | Lunar position, phases, illumination | ✅ |
| `observer` | Observer location management, horizon | ✅ |
| `visibility` | Object visibility, optimal viewing times | ✅ |

**Features**: Observer profiles, LaTeX output, rise/set/transit, airmass, twilight calculations

---

### v0.3 — "Planetary Motion" ✅

Solar system ephemerides and planetary positions.

| Module | Description | Status |
|--------|-------------|--------|
| `planets` | Planetary positions (Meeus algorithms) | ✅ |
| `messier` | Complete Messier catalog (110 objects) | ✅ |

**Features**: Mercury–Neptune positions, magnitudes, elongation, phase angles, rise/set/transit

---

## Upcoming Releases

### v0.4 — "Deep Sky" 📋

Catalogs and object databases. Native implementations—no network required.

| Module | Description | Priority |
|--------|-------------|----------|
| `ngc` | NGC catalog (~7,840 objects) | High |
| `ic` | IC catalog (~5,386 objects) | High |
| `stars` | Hipparcos bright stars (~120,000) | High |
| `caldwell` | Caldwell catalog (109 objects) | Medium |
| `finder` | Object search by criteria | Medium |

#### Features
- [ ] NGC/IC object lookup by number or name
- [ ] Hipparcos star data (position, magnitude, spectral type)
- [ ] Object filtering (by type, constellation, magnitude)
- [ ] Custom observation lists
- [ ] Session-scoped lazy loading for large catalogs

#### CLI Commands
```bash
starward ngc info 7000           # North America Nebula
starward ic info 434             # Horsehead Nebula
starward stars info "Vega"       # Star lookup
starward find galaxies --mag-max 10 --constellation UMa
starward list create "Tonight"   # Custom observation list
starward list add "Tonight" NGC7000 M31 "Vega"
```

#### Testing Milestones
- [ ] Property-based tests with Hypothesis for catalog queries
- [ ] Golden tests against SIMBAD reference data
- [ ] Session-scoped fixtures for catalog performance

---

### v0.5 — "Cosmological" 📋

Extragalactic and cosmological calculations.

| Module | Description | Priority |
|--------|-------------|----------|
| `cosmo` | Cosmological distances, redshift | High |
| `extinction` | Galactic extinction (Schlegel, Planck) | High |
| `magnitudes` | Absolute/apparent magnitude conversions | Medium |
| `luminosity` | Flux, luminosity, surface brightness | Medium |

#### Features
- [ ] Hubble law calculations
- [ ] Luminosity distance, angular diameter distance
- [ ] Comoving distance, lookback time
- [ ] Multiple cosmology models (Planck 2018, WMAP9)
- [ ] Galactic extinction from dust maps (built-in)
- [ ] K-corrections (basic)
- [ ] Distance modulus calculations

#### CLI Commands
```bash
starward cosmo distance --z 0.1           # Distance at redshift
starward cosmo lookback --z 1.0           # Lookback time
starward extinction --coords "10h30m +20d"  # Galactic extinction
starward mag absolute -12.5 --distance 10   # Absolute magnitude
```

---

### v0.6 — "Precision+" 📋

Improved accuracy and calculation foundations.

| Module | Description | Priority |
|--------|-------------|----------|
| `precession` | IAU 2006 precession/nutation | High |
| `refraction` | Atmospheric refraction models | High |
| `aberration` | Annual/diurnal aberration | Medium |
| `parallax` | Stellar parallax corrections | Medium |

#### Features
- [ ] Full IAU 2006/2000A precession-nutation model
- [ ] Atmospheric refraction (Bennett, Meeus formulas)
- [ ] Apparent place calculations
- [ ] Proper motion corrections
- [ ] Improved rise/set accuracy with refraction

#### Accuracy Targets
| Calculation | Current | Target |
|-------------|---------|--------|
| Coordinate transforms | ~1" | <0.1" |
| Rise/set times | ~2 min | <30 sec |
| Planetary positions | ~1' | <10" |

---

### v0.7 — "Observatory Ready" 📋

Professional observatory and imaging support.

| Module | Description | Priority |
|--------|-------------|----------|
| `optics` | Telescope/camera calculations | High |
| `imaging` | FOV, pixel scale, SNR | High |
| `scheduler` | Observation scheduling | Medium |
| `airmass` | Enhanced airmass models | Medium |

#### Features
- [ ] Telescope focal length, f-ratio calculations
- [ ] Camera field of view, pixel scale
- [ ] Signal-to-noise estimation
- [ ] Exposure time calculator
- [ ] Observation priority scheduling
- [ ] Mosaic planning
- [ ] Young's airmass model

#### CLI Commands
```bash
starward optics fov --focal 1000 --sensor 36x24
starward imaging snr --mag 15 --exp 300 --aperture 200
starward schedule tonight --targets list.txt --observer home
```

---

## Integration Releases

### v0.8 — "Bridge Builder" 📋

Optional integration with the astronomy ecosystem.

| Module | Description | Dependency |
|--------|-------------|------------|
| `compat` | Optional dependency detection | None |
| `interop.astropy` | astropy SkyCoord/Time conversion | astropy (optional) |
| `interop.remote` | Object name resolution | astroquery (optional) |

#### Features
- [ ] `starward.compat` module with `HAS_ASTROPY`, `HAS_ASTROQUERY` flags
- [ ] `ICRSCoord.to_skycoord()` → astropy SkyCoord
- [ ] `ICRSCoord.from_skycoord()` ← astropy SkyCoord
- [ ] `JulianDate.to_astropy()` → astropy Time
- [ ] `resolve_object("M31")` via SIMBAD (optional)
- [ ] Results cacheable for offline use

#### Installation
```bash
pip install starward                    # Core only
pip install starward[astropy]           # + astropy interop
pip install starward[remote]            # + astroquery
pip install starward[full]              # Everything
```

#### API
```python
from starward.core.coords import ICRSCoord
from starward.compat import HAS_ASTROPY

coord = ICRSCoord.parse("00h42m44s +41d16m09s")

if HAS_ASTROPY:
    skycoord = coord.to_skycoord()  # astropy.coordinates.SkyCoord
```

---

## Major Releases

### v1.0 — "Stable Orbit" 🎯

The stable API release. Production-ready with guaranteed backwards compatibility.

#### API Stability
- [ ] Public API freeze (semver from here)
- [ ] Deprecation policy documented
- [ ] Migration guides for breaking changes
- [ ] Long-term support (LTS) commitment

#### Quality Gates
- [ ] 95%+ test coverage
- [ ] Multi-platform CI (Linux, macOS, Windows)
- [ ] Python 3.10, 3.11, 3.12, 3.13 support
- [ ] Full doctest coverage
- [ ] Type hints throughout (mypy strict)
- [ ] Performance benchmarks documented

#### Documentation
- [ ] Complete API reference
- [ ] Tutorial series ("Astronomy with starward")
- [ ] Algorithm documentation with references
- [ ] Comparison guides (vs astropy, etc.)

#### Ecosystem
- [ ] PyPI package with wheels
- [ ] conda-forge package
- [ ] Homebrew formula
- [ ] Docker image

---

### v1.x — "Extended Mission"

Post-1.0 feature additions maintaining API stability.

| Version | Focus | Key Features |
|---------|-------|--------------|
| v1.1 | Minor planets | Asteroid/comet ephemerides |
| v1.2 | Eclipses | Solar/lunar eclipse predictions |
| v1.3 | Satellites | Earth satellite visibility (TLE) |
| v1.4 | Spectroscopy | Basic spectral line calculations |

---

### v2.0 — "New Horizons" 🔮

The next generation. Breaking changes allowed for major improvements.

#### Potential Directions
- **Web Interface**: Browser-based calculator (WASM?)
- **Interactive Mode**: REPL with history and completion
- **Plugin System**: Community-contributed modules
- **Real-time Feeds**: Alerts, transient events
- **GPU Acceleration**: For heavy ephemeris work
- **Async Support**: Non-blocking calculations

#### Research Areas
- Machine learning for observation scheduling
- Integration with observatory control systems
- Virtual observatory (VO) protocol support
- Citizen science data pipelines

---

## Architecture Evolution

### Current (v0.3)
```
starward/
├── src/starward/
│   ├── cli/           # Click-based CLI commands
│   ├── core/          # Core calculation modules
│   ├── output/        # Formatters (plain, json, latex)
│   └── verbose/       # "Show your work" engine
└── tests/
```

### Target (v1.0)
```
starward/
├── src/starward/
│   ├── cli/           # CLI commands
│   ├── core/          # Core calculations
│   │   ├── base.py    # BaseCalculation class
│   │   └── ...
│   ├── catalogs/      # NGC, IC, Hipparcos (lazy-loaded)
│   ├── compat/        # Optional dependency detection
│   ├── interop/       # astropy/astroquery bridges
│   ├── output/        # Formatters
│   └── verbose/       # Verbose engine
├── tests/
│   ├── data/          # Golden test data (JSON)
│   ├── core/
│   ├── catalogs/
│   └── interop/
└── benchmarks/        # Performance tests
```

### Key Architectural Additions

#### BaseCalculation Pattern
```python
class BaseCalculation:
    """Base for calculations supporting verbose output."""

    def __init__(self, verbose: VerboseContext | None = None):
        self.verbose = verbose

    def step(self, name: str, formula: str, result: Any) -> Any:
        if self.verbose:
            self.verbose.add_step(name, formula, result)
        return result
```

#### Lazy Catalog Loading
```python
# starward/catalogs/__init__.py
_ngc_catalog = None

def get_ngc():
    global _ngc_catalog
    if _ngc_catalog is None:
        from .ngc_data import load_ngc
        _ngc_catalog = load_ngc()
    return _ngc_catalog
```

---

## Testing Strategy

### Current Approach
- **Unit Tests**: Every function, every edge case
- **Golden Tests**: Validated against USNO, JPL Horizons, Meeus
- **Roundtrip Tests**: Transform → inverse = identity
- **CLI Tests**: Every command, every flag

### Enhanced Approach (v0.4+)

#### Property-Based Testing
```python
from hypothesis import given, strategies as st

@given(st.floats(min_value=0, max_value=360, allow_nan=False))
def test_angle_normalize_idempotent(deg):
    angle = Angle(degrees=deg).normalize()
    assert angle.normalize().degrees == pytest.approx(angle.degrees)
```

#### Golden Test Documentation
```python
@pytest.mark.golden
def test_mars_j2000():
    """
    Mars heliocentric position at J2000.0

    Source: JPL Horizons
    Retrieved: 2024-01-15
    Target: Mars (499)
    Center: Sun (body center)
    """
    ...
```

#### Test Markers
```python
@pytest.mark.slow       # Long-running
@pytest.mark.golden     # Known authoritative values
@pytest.mark.roundtrip  # Transform/inverse identity
@pytest.mark.edge       # Edge cases
@pytest.mark.verbose    # Verbose output tests
@pytest.mark.remote     # Requires network (future)
@pytest.mark.catalog    # Requires large catalogs
```

### CI/CD Pipeline

```yaml
# .github/workflows/test.yml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, windows-latest]
    python-version: ['3.10', '3.11', '3.12']

steps:
  - name: Run tests
    run: pytest --cov=starward --cov-report=xml

  - name: Upload coverage
    uses: codecov/codecov-action@v4
    with:
      fail_ci_if_error: true

  - name: Build docs
    run: cd website && npm run build
```

---

## Version History

| Version | Codename | Status | Highlights |
|---------|----------|--------|------------|
| v0.1 | First Light | ✅ Complete | Time, coords, angles, constants |
| v0.2 | Steady Tracking | ✅ Complete | Sun, moon, observer, visibility |
| v0.3 | Planetary Motion | ✅ Complete | Planets, Messier catalog |
| v0.4 | Deep Sky | 📋 Planned | NGC, IC, Hipparcos catalogs |
| v0.5 | Cosmological | 📋 Planned | Redshift, extinction, distances |
| v0.6 | Precision+ | 📋 Planned | Precession, refraction, aberration |
| v0.7 | Observatory Ready | 📋 Planned | Optics, imaging, scheduling |
| v0.8 | Bridge Builder | 📋 Planned | astropy/astroquery integration |
| v1.0 | Stable Orbit | 🎯 Target | API freeze, LTS, full docs |
| v2.0 | New Horizons | 🔮 Future | Web UI, plugins, real-time |

---

## Ecosystem Positioning

```
┌─────────────────────────────────────────────────────────────┐
│                    Python Astronomy Ecosystem                │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐    │
│   │  astropy    │    │ astroquery  │    │  starward   │    │
│   │             │    │             │    │             │    │
│   │ Foundation  │    │ Data Access │    │ Transparent │    │
│   │ Heavy-duty  │    │ Remote DBs  │    │ Educational │    │
│   │ Enterprise  │    │ Archives    │    │ CLI-first   │    │
│   └─────────────┘    └─────────────┘    └─────────────┘    │
│         │                  │                  │             │
│         │                  │                  │             │
│         └──────────────────┼──────────────────┘             │
│                            │                                │
│                   ┌────────▼────────┐                       │
│                   │  User's Code    │                       │
│                   └─────────────────┘                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**starward's niche**: The toolkit for understanding, learning, and quick answers.

---

## Contributing

We welcome contributions! Key areas:

- **New catalogs**: NGC, IC, specialized object lists
- **Algorithm improvements**: Better accuracy, new methods
- **Documentation**: Tutorials, examples, translations
- **Testing**: Golden tests, property tests, edge cases

See `CONTRIBUTING.md` for guidelines (coming in v0.4).

---

*Built with precision and curiosity for those who look up*
