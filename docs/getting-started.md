# Getting Started with astr0

Welcome! This guide will have you making astronomical calculations in minutes.

---

## Installation

### From PyPI (Recommended)

```bash
pip install astr0
```

### For Development

If you want to contribute or explore the source code:

```bash
git clone https://github.com/yourusername/astr0
cd astr0
pip install -e ".[dev]"
```

This installs astr0 in "editable" mode along with development tools (pytest, mypy, ruff).

### Using Pipenv

```bash
git clone https://github.com/yourusername/astr0
cd astr0
pipenv install
pipenv shell
```

---

## Verify Installation

```bash
astr0 --version
```

You should see:

```
astr0, version 0.1.0
```

Try the about command to see the full banner:

```bash
astr0 about
```

---

## Your First Calculations

### 1. Current Astronomical Time

Let's start simple. What's the current Julian Date?

```bash
astr0 time now
```

This shows you:
- **UTC** — Coordinated Universal Time
- **Julian Date** — Days since noon on January 1, 4713 BCE
- **Modified JD** — JD - 2400000.5 (more compact)
- **T (J2000)** — Julian centuries since J2000.0
- **GMST** — Greenwich Mean Sidereal Time

### 2. Coordinate Transformation

The Galactic Center is located at RA 17h45m40s, Dec -29°00'28". Where is that in Galactic coordinates? (Hint: it should be near l=0°, b=0°!)

```bash
astr0 coords transform "17h45m40s -29d00m28s" --to galactic
```

### 3. Angular Separation

How far apart are Betelgeuse and Rigel in Orion?

- Betelgeuse: RA 05h55m10s, Dec +07°24'25"
- Rigel: RA 05h14m32s, Dec -08°12'06"

```bash
astr0 angles sep "05h55m10s +07d24m25s" "05h14m32s -08d12m06s"
```

Answer: About 18.7° apart.

---

## Understanding Verbose Mode

Here's where astr0 shines as an educational tool. Add `--verbose` (or `-v`) **before** the command to see every calculation step:

```bash
astr0 --verbose angles sep "05h55m10s +07d24m25s" "05h14m32s -08d12m06s"
```

You'll see the Vincenty formula broken down step by step:

```
┌─ Input coordinates
│  Point 1: RA = 05ʰ 55ᵐ 10.00ˢ, Dec = 07° 24′ 25.00″
│  Point 2: RA = 05ʰ 14ᵐ 32.00ˢ, Dec = -08° 12′ 06.00″
└────────────────────────────────────────
┌─ RA difference
│  Δλ = 10.158333°
└────────────────────────────────────────
┌─ Trigonometric values
│  sin(φ₁) = 0.1290..., cos(φ₁) = 0.9916...
│  ...
└────────────────────────────────────────
```

This makes astr0 perfect for:
- **Learning** — See exactly how astronomical formulas work
- **Teaching** — Show students the math behind the results
- **Debugging** — Verify your own implementations
- **Documentation** — Generate worked examples

---

## Output Formats

### Plain Text (Default)

Human-readable output with nice formatting:

```bash
astr0 time now
```

### JSON

Machine-readable output for scripting and pipelines:

```bash
astr0 --output json time now
```

```json
{
  "utc": "2026-01-03T00:15:00.000000+00:00",
  "julian_date": 2461043.5104166665,
  "modified_jd": 61043.01041666651,
  "j2000_centuries": 0.26005504109589043,
  "gmst_hours": 7.093055555555556
}
```

This is great for:
- Piping to `jq` for processing
- Integration with other tools
- Automated workflows

---

## Command Aliases

For power users, astr0 supports short aliases:

| Full Command | Alias |
|--------------|-------|
| `time` | `t` |
| `coords` | `c` or `coord` |
| `angles` | `a` or `angle` |
| `constants` | `const` |

So you can type:

```bash
astr0 t now
astr0 c transform "12h +45d" --to galactic
astr0 a sep "10h +30d" "11h +31d"
```

---

## Getting Help

Every command has built-in help:

```bash
astr0 --help                    # Main help
astr0 time --help               # Time command group
astr0 time convert --help       # Specific command
```

---

## Next Steps

Now that you're set up, explore the detailed guides:

- **[Time & Julian Dates](time.md)** — Understand astronomical time
- **[Coordinate Systems](coords.md)** — Navigate the celestial sphere
- **[Angular Calculations](angles.md)** — Measure the sky
- **[Astronomical Constants](constants.md)** — The numbers behind it all

---

*Questions? Issues? Open an issue on GitHub!*
