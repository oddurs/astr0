# astr0 Documentation

> *"The cosmos is within us. We are made of star-stuff."* — Carl Sagan

Welcome to **astr0**, an educational astronomy calculation toolkit designed to help you understand the mathematics behind astronomical computations. Whether you're a student learning celestial mechanics, an amateur astronomer planning observations, or a researcher needing quick calculations, astr0 is built to be your companion.

## What Makes astr0 Different?

**Show Your Work** — Every calculation can be displayed step-by-step using `--verbose` mode. We believe that understanding *how* a result is computed is just as important as the result itself.

```bash
astr0 --verbose angles sep "10h +30d" "11h +31d"
```

This philosophy makes astr0 not just a tool, but a **learning resource**.

---

## Documentation Modules

| Module | Description |
|--------|-------------|
| [Getting Started](getting-started.md) | Installation and your first calculations |
| [Time & Julian Dates](time.md) | Understanding astronomical time systems |
| [Coordinate Systems](coords.md) | Celestial coordinate systems and transformations |
| [Angular Calculations](angles.md) | Working with angles, separations, and position angles |
| [Astronomical Constants](constants.md) | Reference values used in calculations |
| [Verbose Mode](verbose.md) | The "show your work" system |
| [CLI Reference](cli-reference.md) | Complete command-line reference |
| [Python API](api.md) | Using astr0 as a Python library |

---

## Quick Examples

### What time is it, astronomically?

```bash
astr0 time now
```

```
╭────────────────────────────────────────────╮
│  Current Astronomical Time                 │
├────────────────────────────────────────────┤
│  UTC:                 2026-01-03 00:15:00 │
│  Julian Date:              2461043.510417 │
│  Modified JD:                61043.010417 │
│  T (J2000):                  0.2600550411 │
│  GMST:                     07h 05m 34.60s │
╰────────────────────────────────────────────╯
```

### Where is that star in Galactic coordinates?

```bash
astr0 coords transform "18h36m56s -26d54m32s" --to galactic
```

### How far apart are these two objects?

```bash
astr0 angles sep "M31" "M33"  # Coming in v0.4!
# For now, use coordinates:
astr0 angles sep "00h42m44s +41d16m09s" "01h33m51s +30d39m37s"
```

---

## Design Philosophy

1. **Precision First** — Every calculation uses full double precision
2. **Show Your Work** — Verbose mode explains every step
3. **Test Everything** — 150+ tests validate against authoritative sources
4. **Expand Gracefully** — Modular architecture for future features

---

## Version

You're reading the documentation for **astr0 v0.1.0 "First Light"**.

See the [Roadmap](../ROADMAP.md) for upcoming features including Sun/Moon calculations, planetary ephemerides, and catalog lookups.

---

*Per aspera ad astra* — Through hardships to the stars ✦
