#!/usr/bin/env python3
"""
Build the starward catalog database.

This script creates the SQLite database containing Messier, NGC, and other
astronomical catalog data. Run this script when updating catalog data.

Usage:
    python scripts/build_catalog_db.py

The database will be created at: src/starward/data/catalogs.db
"""

from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

# Add src to path for imports
SRC_PATH = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(SRC_PATH))

from starward.core.messier_data import MESSIER_DATA


# Database output path
DB_PATH = SRC_PATH / "starward" / "data" / "catalogs.db"


def create_schema(conn: sqlite3.Connection) -> None:
    """Create the database schema."""
    print("Creating database schema...")

    # Messier table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS messier (
            number INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            object_type TEXT NOT NULL,
            ra_hours REAL NOT NULL,
            dec_degrees REAL NOT NULL,
            magnitude REAL,
            size_arcmin REAL,
            distance_kly REAL,
            constellation TEXT NOT NULL,
            ngc_number INTEGER,
            description TEXT
        )
    """)

    # NGC table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ngc (
            number INTEGER PRIMARY KEY,
            name TEXT,
            object_type TEXT NOT NULL,
            ra_hours REAL NOT NULL,
            dec_degrees REAL NOT NULL,
            magnitude REAL,
            size_arcmin REAL,
            size_minor_arcmin REAL,
            distance_kly REAL,
            constellation TEXT NOT NULL,
            messier_number INTEGER,
            hubble_type TEXT,
            description TEXT
        )
    """)

    # Indexes for NGC
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ngc_type ON ngc(object_type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ngc_constellation ON ngc(constellation)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ngc_magnitude ON ngc(magnitude)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ngc_messier ON ngc(messier_number)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ngc_name ON ngc(name)")

    # IC table (same schema as NGC)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS ic (
            number INTEGER PRIMARY KEY,
            name TEXT,
            object_type TEXT NOT NULL,
            ra_hours REAL NOT NULL,
            dec_degrees REAL NOT NULL,
            magnitude REAL,
            size_arcmin REAL,
            size_minor_arcmin REAL,
            distance_kly REAL,
            constellation TEXT NOT NULL,
            ngc_number INTEGER,
            hubble_type TEXT,
            description TEXT
        )
    """)

    # Indexes for IC
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ic_type ON ic(object_type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ic_constellation ON ic(constellation)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ic_magnitude ON ic(magnitude)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ic_ngc ON ic(ngc_number)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_ic_name ON ic(name)")

    # Hipparcos star catalog table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS hipparcos (
            hip_number INTEGER PRIMARY KEY,
            name TEXT,
            bayer TEXT,
            flamsteed INTEGER,
            ra_hours REAL NOT NULL,
            dec_degrees REAL NOT NULL,
            magnitude REAL NOT NULL,
            bv_color REAL,
            spectral_type TEXT,
            parallax REAL,
            distance_ly REAL,
            proper_motion_ra REAL,
            proper_motion_dec REAL,
            radial_velocity REAL,
            constellation TEXT NOT NULL
        )
    """)

    # Indexes for Hipparcos
    conn.execute("CREATE INDEX IF NOT EXISTS idx_hip_magnitude ON hipparcos(magnitude)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_hip_constellation ON hipparcos(constellation)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_hip_name ON hipparcos(name)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_hip_spectral ON hipparcos(spectral_type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_hip_bayer ON hipparcos(bayer)")

    # Caldwell catalog table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS caldwell (
            number INTEGER PRIMARY KEY,
            name TEXT,
            object_type TEXT NOT NULL,
            ra_hours REAL NOT NULL,
            dec_degrees REAL NOT NULL,
            magnitude REAL,
            size_arcmin REAL,
            size_minor_arcmin REAL,
            distance_kly REAL,
            constellation TEXT NOT NULL,
            ngc_number INTEGER,
            ic_number INTEGER,
            description TEXT
        )
    """)

    # Indexes for Caldwell
    conn.execute("CREATE INDEX IF NOT EXISTS idx_caldwell_type ON caldwell(object_type)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_caldwell_constellation ON caldwell(constellation)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_caldwell_magnitude ON caldwell(magnitude)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_caldwell_ngc ON caldwell(ngc_number)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_caldwell_ic ON caldwell(ic_number)")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_caldwell_name ON caldwell(name)")

    conn.commit()
    print("  Schema created successfully")


def extract_ngc_number(ngc_str: str | None) -> int | None:
    """Extract NGC number from string like 'NGC 1952'."""
    if not ngc_str:
        return None
    try:
        # Handle formats like "NGC 1952", "NGC1952", "NGC 224"
        ngc_str = ngc_str.upper().replace("NGC", "").strip()
        return int(ngc_str)
    except (ValueError, AttributeError):
        return None


def import_messier_data(conn: sqlite3.Connection) -> None:
    """Import Messier catalog data."""
    print("Importing Messier catalog...")

    count = 0
    for number, obj in MESSIER_DATA.items():
        ngc_number = extract_ngc_number(obj.ngc)

        conn.execute(
            """
            INSERT OR REPLACE INTO messier
            (number, name, object_type, ra_hours, dec_degrees, magnitude,
             size_arcmin, distance_kly, constellation, ngc_number, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                obj.number,
                obj.name,
                obj.object_type,
                obj.ra_hours,
                obj.dec_degrees,
                obj.magnitude,
                obj.size_arcmin,
                obj.distance_kly,
                obj.constellation,
                ngc_number,
                obj.description,
            )
        )
        count += 1

    conn.commit()
    print(f"  Imported {count} Messier objects")


def import_sample_ngc_data(conn: sqlite3.Connection) -> None:
    """Import sample NGC data for testing.

    This imports a handful of well-known NGC objects.
    Full NGC import will come from OpenNGC data.
    """
    print("Importing sample NGC data...")

    # Sample NGC objects for testing
    # These are well-known objects with Messier cross-references
    sample_objects = [
        # NGC 224 = M31 Andromeda Galaxy
        (224, "Andromeda Galaxy", "galaxy", 0.7123, 41.2689, 3.4, 190.0, 55.0, 2500.0, "And", 31, "SA(s)b", "Large spiral galaxy, nearest major galaxy to Milky Way"),
        # NGC 598 = M33 Triangulum Galaxy
        (598, "Triangulum Galaxy", "galaxy", 1.5642, 30.6603, 5.7, 73.0, 45.0, 2730.0, "Tri", 33, "SA(s)cd", "Third largest galaxy in Local Group"),
        # NGC 1952 = M1 Crab Nebula
        (1952, "Crab Nebula", "supernova_remnant", 5.5753, 22.0145, 8.4, 6.0, 4.0, 6.5, "Tau", 1, None, "Supernova remnant from 1054 AD"),
        # NGC 1976 = M42 Orion Nebula
        (1976, "Orion Nebula", "emission_nebula", 5.5908, -5.3911, 4.0, 85.0, 60.0, 1.344, "Ori", 42, None, "Brightest diffuse nebula in the sky"),
        # NGC 5194 = M51 Whirlpool Galaxy
        (5194, "Whirlpool Galaxy", "galaxy", 13.4981, 47.1953, 8.4, 11.0, 7.0, 23000.0, "CVn", 51, "SA(s)bc", "Classic face-on spiral galaxy"),
        # NGC 6611 = M16 Eagle Nebula
        (6611, "Eagle Nebula", "cluster_nebula", 18.3133, -13.7867, 6.0, 7.0, None, 7.0, "Ser", 16, None, "Star-forming region, home of Pillars of Creation"),
        # NGC 6720 = M57 Ring Nebula
        (6720, "Ring Nebula", "planetary_nebula", 18.8933, 33.0286, 8.8, 1.4, 1.0, 2.3, "Lyr", 57, None, "Classic planetary nebula"),
        # NGC 6853 = M27 Dumbbell Nebula
        (6853, "Dumbbell Nebula", "planetary_nebula", 19.9933, 22.7211, 7.5, 8.0, 5.7, 1.36, "Vul", 27, None, "Large bright planetary nebula"),
        # NGC 7000 North America Nebula (no Messier)
        (7000, "North America Nebula", "emission_nebula", 20.9833, 44.5333, 4.0, 120.0, 100.0, 2.0, "Cyg", None, None, "Large emission nebula resembling North America"),
        # NGC 7293 Helix Nebula (no Messier)
        (7293, "Helix Nebula", "planetary_nebula", 22.4933, -20.8372, 7.6, 16.0, 12.0, 0.65, "Aqr", None, None, "Nearest bright planetary nebula to Earth"),
        # NGC 869 h Persei - Double Cluster
        (869, "h Persei", "open_cluster", 2.3200, 57.1333, 4.3, 30.0, None, 7.1, "Per", None, None, "Western half of the Double Cluster"),
        # NGC 884 Chi Persei - Double Cluster
        (884, "Chi Persei", "open_cluster", 2.3733, 57.1500, 4.4, 30.0, None, 7.5, "Per", None, None, "Eastern half of the Double Cluster"),
        # NGC 457 Owl Cluster
        (457, "Owl Cluster", "open_cluster", 1.3267, 58.2833, 6.4, 13.0, None, 7.9, "Cas", None, None, "Open cluster with distinctive owl-like pattern"),
        # NGC 2237 Rosette Nebula
        (2237, "Rosette Nebula", "emission_nebula", 6.5333, 5.0333, 9.0, 80.0, 60.0, 5.2, "Mon", None, None, "Large circular emission nebula"),
        # NGC 6992 Eastern Veil Nebula
        (6992, "Eastern Veil Nebula", "supernova_remnant", 20.9400, 31.7167, 7.0, 60.0, 8.0, 2.4, "Cyg", None, None, "Part of the Cygnus Loop supernova remnant"),
    ]

    for obj in sample_objects:
        conn.execute(
            """
            INSERT OR REPLACE INTO ngc
            (number, name, object_type, ra_hours, dec_degrees, magnitude,
             size_arcmin, size_minor_arcmin, distance_kly, constellation,
             messier_number, hubble_type, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            obj
        )

    conn.commit()
    print(f"  Imported {len(sample_objects)} sample NGC objects")


def import_sample_ic_data(conn: sqlite3.Connection) -> None:
    """Import sample IC data for testing.

    This imports a handful of well-known IC objects.
    Full IC import will come from OpenNGC data.
    """
    print("Importing sample IC data...")

    # Sample IC objects for testing
    # Format: (number, name, object_type, ra_hours, dec_degrees, magnitude,
    #          size_arcmin, size_minor_arcmin, distance_kly, constellation,
    #          ngc_number, hubble_type, description)
    sample_objects = [
        # IC 434 - Horsehead Nebula region
        (434, "Horsehead Nebula", "dark_nebula", 5.6833, -2.4583, None, 60.0, 10.0, 1.5, "Ori", None, None, "Famous dark nebula silhouetted against emission nebula"),
        # IC 1396 - Elephant Trunk Nebula
        (1396, "Elephant Trunk Nebula", "emission_nebula", 21.6500, 57.5000, 3.5, 170.0, 140.0, 2.4, "Cep", None, None, "Large emission nebula with dark globule"),
        # IC 405 - Flaming Star Nebula
        (405, "Flaming Star Nebula", "emission_nebula", 5.2733, 34.2667, 6.0, 30.0, 19.0, 1.5, "Aur", None, None, "Emission/reflection nebula around AE Aurigae"),
        # IC 1805 - Heart Nebula
        (1805, "Heart Nebula", "emission_nebula", 2.5500, 61.4667, 6.5, 60.0, 60.0, 7.5, "Cas", None, None, "Large emission nebula shaped like a heart"),
        # IC 1848 - Soul Nebula
        (1848, "Soul Nebula", "emission_nebula", 2.8500, 60.4333, 6.5, 60.0, 30.0, 7.5, "Cas", None, None, "Emission nebula adjacent to Heart Nebula"),
        # IC 2118 - Witch Head Nebula
        (2118, "Witch Head Nebula", "reflection_nebula", 5.0333, -7.2000, None, 180.0, 60.0, 0.9, "Eri", None, None, "Faint reflection nebula illuminated by Rigel"),
        # IC 1101 - Largest known galaxy
        (1101, None, "galaxy", 15.1775, 5.7447, 14.7, 1.2, 0.6, 1045000.0, "Vir", None, "cD", "One of the largest known galaxies"),
        # IC 10 - Irregular galaxy
        (10, None, "galaxy", 0.3433, 59.2942, 10.4, 6.8, 5.9, 2200.0, "Cas", None, "dIrr", "Starburst irregular galaxy in Local Group"),
        # IC 342 - Hidden Galaxy
        (342, "Hidden Galaxy", "galaxy", 3.7786, 68.0964, 8.4, 21.4, 20.9, 10800.0, "Cam", None, "SAB(rs)cd", "Large spiral galaxy obscured by Milky Way dust"),
        # IC 4665 - Open cluster in Ophiuchus
        (4665, None, "open_cluster", 17.7633, 5.7167, 4.2, 41.0, None, 1.1, "Oph", None, None, "Large scattered open cluster"),
        # IC 2602 - Southern Pleiades
        (2602, "Southern Pleiades", "open_cluster", 10.7167, -64.4000, 1.9, 50.0, None, 0.479, "Car", None, None, "Bright open cluster visible to naked eye"),
        # IC 4756 - Open cluster in Serpens
        (4756, None, "open_cluster", 18.6500, 5.4333, 4.6, 52.0, None, 1.5, "Ser", None, None, "Large open cluster near Milky Way"),
        # IC 5146 - Cocoon Nebula
        (5146, "Cocoon Nebula", "cluster_nebula", 21.8933, 47.2667, 7.2, 12.0, 12.0, 4.0, "Cyg", None, None, "Reflection/emission nebula with embedded cluster"),
        # IC 443 - Jellyfish Nebula
        (443, "Jellyfish Nebula", "supernova_remnant", 6.2833, 22.5333, None, 50.0, None, 5.0, "Gem", None, None, "Supernova remnant with complex filaments"),
        # IC 2944 - Running Chicken Nebula
        (2944, "Running Chicken Nebula", "cluster_nebula", 11.6167, -63.0333, 4.5, 75.0, None, 5.9, "Cen", None, None, "Emission nebula with Thackeray's Globules"),
    ]

    for obj in sample_objects:
        conn.execute(
            """
            INSERT OR REPLACE INTO ic
            (number, name, object_type, ra_hours, dec_degrees, magnitude,
             size_arcmin, size_minor_arcmin, distance_kly, constellation,
             ngc_number, hubble_type, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            obj
        )

    conn.commit()
    print(f"  Imported {len(sample_objects)} sample IC objects")


def import_sample_hipparcos_data(conn: sqlite3.Connection) -> None:
    """Import sample Hipparcos star data for testing.

    This imports well-known bright stars with accurate data.
    Full Hipparcos import would include ~120,000 stars.
    """
    print("Importing sample Hipparcos data...")

    # Sample bright stars
    # Format: (hip_number, name, bayer, flamsteed, ra_hours, dec_degrees, magnitude,
    #          bv_color, spectral_type, parallax, distance_ly, proper_motion_ra,
    #          proper_motion_dec, radial_velocity, constellation)
    sample_stars = [
        # Sirius - brightest star
        (32349, "Sirius", "Alpha Canis Majoris", 9, 6.7525, -16.7161, -1.46, 0.00, "A1V", 379.21, 8.6, -546.01, -1223.07, -5.5, "CMa"),
        # Canopus - 2nd brightest
        (30438, "Canopus", "Alpha Carinae", None, 6.3992, -52.6956, -0.74, 0.15, "A9II", 10.55, 310.0, 19.99, 23.67, 20.3, "Car"),
        # Arcturus - 4th brightest
        (69673, "Arcturus", "Alpha Bootis", 16, 14.2610, 19.1824, -0.05, 1.23, "K1.5IIIpe", 88.83, 36.7, -1093.45, -1999.40, -5.2, "Boo"),
        # Vega - 5th brightest
        (91262, "Vega", "Alpha Lyrae", 3, 18.6156, 38.7836, 0.03, 0.00, "A0V", 130.23, 25.0, 200.94, 286.23, -13.9, "Lyr"),
        # Capella - 6th brightest
        (24608, "Capella", "Alpha Aurigae", 13, 5.2782, 45.9980, 0.08, 0.80, "G5IIIe+G0III", 77.29, 42.2, 75.52, -427.11, 30.2, "Aur"),
        # Rigel - 7th brightest
        (24436, "Rigel", "Beta Orionis", 19, 5.2423, -8.2016, 0.13, -0.03, "B8Ia", 3.78, 860.0, 1.87, -0.56, 20.7, "Ori"),
        # Procyon - 8th brightest
        (37279, "Procyon", "Alpha Canis Minoris", 10, 7.6553, 5.2250, 0.34, 0.42, "F5IV-V", 284.56, 11.5, -716.57, -1034.58, -3.2, "CMi"),
        # Betelgeuse - 9th brightest
        (27989, "Betelgeuse", "Alpha Orionis", 58, 5.9195, 7.4070, 0.42, 1.85, "M1-2Ia-Iab", 4.51, 700.0, 27.33, 10.86, 21.9, "Ori"),
        # Achernar - 10th brightest
        (7588, "Achernar", "Alpha Eridani", None, 1.6285, -57.2367, 0.46, -0.16, "B6Vep", 22.68, 144.0, 88.02, -40.08, 16.0, "Eri"),
        # Hadar - Beta Centauri
        (68702, "Hadar", "Beta Centauri", None, 14.0637, -60.3730, 0.61, -0.22, "B1III", 8.32, 390.0, -33.27, -23.16, 5.9, "Cen"),
        # Altair
        (97649, "Altair", "Alpha Aquilae", 53, 19.8464, 8.8683, 0.76, 0.22, "A7V", 194.95, 16.7, 536.23, 385.29, -26.1, "Aql"),
        # Aldebaran
        (21421, "Aldebaran", "Alpha Tauri", 87, 4.5987, 16.5093, 0.85, 1.54, "K5III", 50.09, 65.3, 62.78, -189.35, 54.3, "Tau"),
        # Antares
        (80763, "Antares", "Alpha Scorpii", 21, 16.4901, -26.4320, 0.96, 1.83, "M1.5Iab-Ib", 5.40, 600.0, -12.11, -23.30, -3.4, "Sco"),
        # Spica
        (65474, "Spica", "Alpha Virginis", 67, 13.4199, -11.1614, 0.97, -0.23, "B1III-IV+B2V", 13.06, 250.0, -42.50, -31.73, 1.0, "Vir"),
        # Pollux
        (37826, "Pollux", "Beta Geminorum", 78, 7.7553, 28.0262, 1.14, 1.00, "K0IIIb", 96.54, 33.8, -625.69, -45.95, 3.2, "Gem"),
        # Fomalhaut
        (113368, "Fomalhaut", "Alpha Piscis Austrini", 24, 22.9608, -29.6222, 1.16, 0.09, "A4V", 130.08, 25.1, 329.22, -164.22, 6.5, "PsA"),
        # Deneb
        (102098, "Deneb", "Alpha Cygni", 50, 20.6905, 45.2803, 1.25, 0.09, "A2Ia", 2.31, 1400.0, 1.56, 1.55, -4.5, "Cyg"),
        # Mimosa - Beta Crucis
        (62434, "Mimosa", "Beta Crucis", None, 12.7953, -59.6886, 1.25, -0.23, "B0.5IV", 9.25, 350.0, -48.24, -12.82, 15.6, "Cru"),
        # Regulus
        (49669, "Regulus", "Alpha Leonis", 32, 10.1395, 11.9672, 1.35, -0.11, "B8IVn", 41.13, 79.3, -248.73, 5.59, 5.9, "Leo"),
        # Acrux - Alpha Crucis
        (60718, "Acrux", "Alpha Crucis", None, 12.4433, -63.0991, 0.76, -0.24, "B0.5IV+B1V", 10.17, 320.0, -35.37, -14.73, -11.2, "Cru"),
        # Castor
        (36850, "Castor", "Alpha Geminorum", 66, 7.5767, 31.8886, 1.58, 0.03, "A1V+A2Vm", 64.12, 50.9, -191.45, -145.19, 5.4, "Gem"),
        # Polaris - North Star
        (11767, "Polaris", "Alpha Ursae Minoris", 1, 2.5302, 89.2641, 1.98, 0.60, "F7Ib", 7.54, 430.0, 44.22, -11.74, -17.0, "UMi"),
        # Alphard
        (46390, "Alphard", "Alpha Hydrae", 30, 9.4598, -8.6586, 1.98, 1.44, "K3II-III", 18.40, 177.0, -14.49, 33.25, -4.3, "Hya"),
        # Dubhe - Alpha UMa (Big Dipper)
        (54061, "Dubhe", "Alpha Ursae Majoris", 50, 11.0621, 61.7510, 1.79, 1.07, "K0IIIa", 26.54, 123.0, -136.46, -35.25, -9.0, "UMa"),
        # Merak - Beta UMa (Big Dipper)
        (53910, "Merak", "Beta Ursae Majoris", 48, 11.0306, 56.3824, 2.37, 0.03, "A1IVps", 40.90, 79.7, 81.66, 33.74, -12.0, "UMa"),
        # Alioth - Epsilon UMa (Big Dipper)
        (62956, "Alioth", "Epsilon Ursae Majoris", 77, 12.9004, 55.9598, 1.77, -0.02, "A1III-IVpkB9", 40.30, 80.9, 111.74, -8.99, -9.3, "UMa"),
        # Mizar - Zeta UMa (Big Dipper)
        (65378, "Mizar", "Zeta Ursae Majoris", 79, 13.3988, 54.9254, 2.27, 0.02, "A2V", 41.73, 78.2, 121.23, -22.01, -6.0, "UMa"),
        # Alkaid - Eta UMa (Big Dipper)
        (67301, "Alkaid", "Eta Ursae Majoris", 85, 13.7924, 49.3133, 1.86, -0.19, "B3V", 31.38, 104.0, -121.23, -15.56, -11.0, "UMa"),
        # Bellatrix
        (25336, "Bellatrix", "Gamma Orionis", 24, 5.4185, 6.3497, 1.64, -0.22, "B2III", 12.92, 250.0, -8.75, -13.28, 18.2, "Ori"),
        # Alnilam - Epsilon Orionis (Orion's Belt)
        (26311, "Alnilam", "Epsilon Orionis", 46, 5.6036, -1.2019, 1.70, -0.18, "B0Ia", 1.65, 2000.0, 1.49, -1.06, 25.9, "Ori"),
        # Alnitak - Zeta Orionis (Orion's Belt)
        (26727, "Alnitak", "Zeta Orionis", 50, 5.6796, -1.9425, 1.77, -0.21, "O9.5Ib+B1IV", 4.43, 740.0, 3.99, 2.54, 18.5, "Ori"),
        # Mintaka - Delta Orionis (Orion's Belt)
        (25930, "Mintaka", "Delta Orionis", 34, 5.5334, -0.2991, 2.23, -0.22, "O9.5II+B0.5III", 4.71, 690.0, 1.67, -0.56, 16.0, "Ori"),
        # Saiph
        (27366, "Saiph", "Kappa Orionis", 53, 5.7959, -9.6696, 2.06, -0.18, "B0.5Ia", 5.04, 650.0, 1.55, -1.20, 20.5, "Ori"),
    ]

    for star in sample_stars:
        conn.execute(
            """
            INSERT OR REPLACE INTO hipparcos
            (hip_number, name, bayer, flamsteed, ra_hours, dec_degrees, magnitude,
             bv_color, spectral_type, parallax, distance_ly, proper_motion_ra,
             proper_motion_dec, radial_velocity, constellation)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            star
        )

    conn.commit()
    print(f"  Imported {len(sample_stars)} sample Hipparcos stars")


def import_caldwell_data(conn: sqlite3.Connection) -> None:
    """Import Caldwell catalog data.

    The Caldwell catalog contains 109 deep-sky objects selected by
    Sir Patrick Moore, complementing the Messier catalog.
    """
    print("Importing Caldwell catalog...")

    # Full Caldwell catalog (109 objects)
    # Format: (number, name, object_type, ra_hours, dec_degrees, magnitude,
    #          size_arcmin, size_minor_arcmin, distance_kly, constellation,
    #          ngc_number, ic_number, description)
    caldwell_objects = [
        # C1-C10
        (1, "Bow-Tie Nebula", "planetary_nebula", 0.2200, 51.5667, 9.2, 0.4, None, 4.5, "Cep", 188, None, "Faint planetary nebula"),
        (2, None, "planetary_nebula", 0.7703, 72.5250, 11.6, 0.6, None, 3.0, "Cep", 40, None, "Small planetary nebula"),
        (3, None, "open_cluster", 1.0678, 60.6583, 5.7, 6.0, None, 7.0, "Cas", 4236, None, "Open cluster in Cassiopeia"),
        (4, "Iris Nebula", "reflection_nebula", 21.0267, 68.1700, 6.8, 18.0, None, 1.3, "Cep", 7023, None, "Beautiful reflection nebula"),
        (5, "Owl Cluster", "open_cluster", 21.5333, 58.7667, 7.1, 13.0, None, 9.0, "Cas", 7789, None, "Rich open cluster"),
        (6, "Cat's Eye Nebula", "planetary_nebula", 17.9764, 66.6328, 8.1, 0.3, None, 3.3, "Dra", 6543, None, "Complex planetary nebula"),
        (7, None, "galaxy", 0.1142, 61.3500, 11.8, 6.0, 2.5, 5600.0, "Cas", 2403, None, "Edge-on spiral galaxy"),
        (8, None, "galaxy", 0.3228, 35.6000, 11.0, 3.3, 1.8, 7000.0, "Peg", 559, None, "Spiral galaxy"),
        (9, "Cave Nebula", "emission_nebula", 22.9567, 62.5167, 7.7, 50.0, 30.0, 2.4, "Cep", None, None, "Large emission nebula (Sh2-155)"),
        (10, None, "galaxy", 0.4894, 35.4333, 10.8, 5.1, 2.2, 4200.0, "Cas", 663, None, "Spiral galaxy"),
        # C11-C20
        (11, "Bubble Nebula", "emission_nebula", 23.3467, 61.2000, 10.0, 15.0, 8.0, 7.1, "Cas", 7635, None, "Emission nebula with bubble structure"),
        (12, "Fireworks Galaxy", "galaxy", 23.9531, 68.1767, 8.5, 11.5, 9.8, 10000.0, "Cep", 6946, None, "Face-on spiral galaxy"),
        (13, "Owl Cluster", "open_cluster", 1.3300, 58.3333, 6.4, 13.0, None, 7.9, "Cas", 457, None, "Open cluster with owl pattern"),
        (14, "Double Cluster", "open_cluster", 2.3500, 57.1333, 4.3, 60.0, None, 7.3, "Per", 869, None, "Famous double cluster - h Persei"),
        (15, "Blinking Planetary", "planetary_nebula", 19.7333, 30.9167, 8.8, 0.7, None, 2.2, "Cyg", 6826, None, "Planetary appears to blink"),
        (16, None, "open_cluster", 0.5350, 61.8333, 5.6, 5.0, None, 5.1, "Cas", 7243, None, "Loose open cluster"),
        (17, None, "open_cluster", 0.8767, 61.1333, 5.1, 29.0, None, 6.4, "Cas", 147, None, "Large open cluster"),
        (18, None, "open_cluster", 2.0067, 56.8500, 5.5, 18.0, None, 4.1, "Cas", 185, None, "Open cluster near Double Cluster"),
        (19, "Cocoon Nebula", "cluster_nebula", 21.8933, 47.2667, 7.2, 12.0, None, 4.0, "Cyg", None, 5146, "Reflection/emission nebula"),
        (20, "North America Nebula", "emission_nebula", 20.9833, 44.5333, 4.0, 120.0, 100.0, 2.0, "Cyg", 7000, None, "Large nebula shaped like continent"),
        # C21-C30
        (21, None, "open_cluster", 1.3333, 57.1333, 4.4, 30.0, None, 7.5, "Per", 884, None, "Double Cluster - Chi Persei"),
        (22, "Blue Snowball", "planetary_nebula", 1.5167, 42.5333, 8.3, 0.5, None, 5.6, "And", 7662, None, "Bright planetary nebula"),
        (23, None, "galaxy", 0.1375, 50.7167, 10.0, 19.6, 4.4, 8000.0, "And", 891, None, "Edge-on spiral galaxy"),
        (24, "Perseus A", "galaxy", 3.3303, 41.5117, 11.6, 2.5, 1.0, 230000.0, "Per", 1275, None, "Radio galaxy in Perseus cluster"),
        (25, None, "galaxy", 3.2014, 41.8667, 11.0, 3.5, 2.5, 230000.0, "Per", 2419, None, "Galaxy in Perseus cluster"),
        (26, None, "galaxy", 12.0000, 47.4833, 8.4, 21.4, 9.8, 12000.0, "CVn", 4244, None, "Edge-on spiral galaxy"),
        (27, "Crescent Nebula", "emission_nebula", 20.2022, 38.3500, 7.4, 18.0, 12.0, 5.0, "Cyg", 6888, None, "Wolf-Rayet nebula"),
        (28, None, "open_cluster", 2.5567, 60.6500, 6.1, 14.0, None, 5.0, "Cas", 752, None, "Rich open cluster"),
        (29, None, "open_cluster", 3.2400, 44.8833, 6.9, 7.0, None, 3.5, "Per", 5005, None, "Small open cluster"),
        (30, None, "galaxy", 12.0889, 43.9333, 9.3, 8.4, 4.1, 35000.0, "CVn", 4631, None, "Whale Galaxy - edge-on spiral"),
        # C31-C40
        (31, "Flaming Star Nebula", "emission_nebula", 5.2733, 34.2667, 6.0, 30.0, 19.0, 1.5, "Aur", None, 405, "Emission/reflection nebula"),
        (32, "Whale Galaxy", "galaxy", 12.7236, 32.5417, 9.0, 15.5, 2.7, 25000.0, "CVn", 4631, None, "Edge-on spiral with tidal tail"),
        (33, "East Veil Nebula", "supernova_remnant", 20.9400, 31.7167, 7.0, 60.0, 8.0, 2.4, "Cyg", 6992, None, "Part of Cygnus Loop"),
        (34, "West Veil Nebula", "supernova_remnant", 20.7600, 30.7167, 7.0, 70.0, None, 2.4, "Cyg", 6960, None, "Witch's Broom Nebula"),
        (35, None, "galaxy", 14.0522, 54.3500, 9.7, 6.6, 3.2, 25000.0, "UMa", 4889, None, "Spiral galaxy"),
        (36, None, "galaxy", 12.3364, 25.9833, 9.8, 5.4, 1.1, 32000.0, "Com", 4559, None, "Spiral galaxy"),
        (37, None, "galaxy", 12.7903, 26.0167, 10.2, 10.2, 4.5, 55000.0, "Com", 6885, None, "Spiral galaxy"),
        (38, "Needle Galaxy", "galaxy", 12.6042, 25.9833, 9.3, 16.2, 2.8, 42000.0, "Com", 4565, None, "Famous edge-on spiral"),
        (39, "Eskimo Nebula", "planetary_nebula", 7.4867, 20.9117, 9.2, 0.8, None, 2.9, "Gem", 2392, None, "Bright planetary with double shell"),
        (40, None, "galaxy", 12.4342, 9.9333, 10.4, 8.1, 5.2, 50000.0, "Vir", 3626, None, "Lenticular galaxy"),
        # C41-C50
        (41, "Hyades", "open_cluster", 4.4500, 15.8667, 0.5, 330.0, None, 0.151, "Tau", None, None, "Nearest open cluster"),
        (42, None, "galaxy", 12.7222, 11.5500, 8.6, 5.0, 3.7, 60000.0, "Vir", 4697, None, "Elliptical galaxy"),
        (43, "Little Sombrero", "galaxy", 12.4356, 11.6500, 10.9, 4.2, 1.6, 40000.0, "Vir", 4274, None, "Spiral galaxy"),
        (44, None, "galaxy", 12.4853, 12.3333, 10.4, 5.1, 3.1, 45000.0, "Vir", 4314, None, "Ringed barred spiral"),
        (45, None, "galaxy", 12.6103, 11.1833, 10.6, 4.3, 2.3, 52000.0, "Vir", 4526, None, "Lenticular galaxy"),
        (46, "Hubble's Variable Nebula", "reflection_nebula", 6.6500, 8.7333, 9.0, 2.0, None, 2.5, "Mon", 2261, None, "Fan-shaped reflection nebula"),
        (47, None, "galaxy", 10.3958, 12.9917, 8.9, 9.8, 4.6, 35000.0, "Leo", 6633, None, "Elliptical galaxy"),
        (48, None, "galaxy", 10.0850, 20.5833, 9.8, 8.1, 5.8, 31000.0, "Leo", 2775, None, "Spiral galaxy"),
        (49, "Rosette Nebula", "emission_nebula", 6.5333, 5.0333, 9.0, 80.0, 60.0, 5.2, "Mon", 2237, None, "Large circular emission nebula"),
        (50, "Satellite Nebula", "emission_nebula", 21.0533, 47.2667, 9.0, 3.5, None, 5.0, "Cyg", None, 5146, "Part of Cocoon region"),
        # C51-C60
        (51, "Pinwheel Galaxy", "galaxy", 1.5703, 60.7167, 9.3, 2.2, 2.0, 35000.0, "Cas", None, 342, "Face-on spiral"),
        (52, None, "galaxy", 12.9531, -5.8000, 10.5, 4.7, 3.0, 65000.0, "Vir", 4697, None, "Elliptical galaxy"),
        (53, "Spindle Galaxy", "galaxy", 10.0867, -7.7167, 9.1, 10.5, 3.0, 31000.0, "Sex", 3115, None, "Edge-on lenticular"),
        (54, "Sculptor Galaxy", "galaxy", 0.7856, -25.2883, 7.2, 27.5, 6.8, 11400.0, "Scl", 253, None, "Large edge-on spiral"),
        (55, "Saturn Nebula", "planetary_nebula", 21.0700, -11.3667, 8.0, 0.4, None, 5.2, "Aqr", 7009, None, "Planetary with ansae"),
        (56, None, "galaxy", 0.3125, -37.6833, 8.5, 31.5, 17.0, 7200.0, "Scl", 300, None, "Large spiral galaxy"),
        (57, "Barnard's Galaxy", "galaxy", 19.7500, -14.8167, 8.8, 15.5, 13.5, 1600.0, "Sgr", 6822, None, "Irregular galaxy in Local Group"),
        (58, "Caroline's Cluster", "open_cluster", 7.5767, -14.4833, 6.4, 15.0, None, 3.9, "CMa", 2360, None, "Rich open cluster"),
        (59, "Ghost of Jupiter", "planetary_nebula", 10.4117, -18.6333, 7.8, 0.8, None, 1.4, "Hya", 3242, None, "Bright planetary nebula"),
        (60, "Antennae Galaxies", "galaxy", 12.0308, -18.8667, 10.5, 5.2, 3.1, 45000.0, "Crv", 4038, None, "Famous interacting pair"),
        # C61-C70
        (61, None, "galaxy", 13.2611, -17.5333, 10.2, 7.6, 2.1, 52000.0, "Crv", 4995, None, "Barred spiral"),
        (62, None, "galaxy", 12.3597, -26.7500, 9.0, 4.6, 4.0, 12000.0, "Cen", 247, None, "Spiral galaxy"),
        (63, "Helix Nebula", "planetary_nebula", 22.4933, -20.8372, 7.6, 16.0, None, 0.65, "Aqr", 7293, None, "Nearest bright planetary"),
        (64, None, "galaxy", 1.2650, -43.3833, 9.3, 9.0, 3.0, 13000.0, "Scl", 362, None, "Spiral galaxy"),
        (65, "Sculptor Dwarf", "galaxy", 1.0000, -33.7167, 8.8, 39.8, 30.9, 280.0, "Scl", None, None, "Local Group dwarf spheroidal"),
        (66, None, "galaxy", 2.6714, -30.2750, 10.0, 4.2, 3.4, 86000.0, "For", 1097, None, "Barred spiral"),
        (67, None, "galaxy", 2.6250, -35.9917, 9.2, 6.0, 2.5, 56000.0, "For", 1049, None, "Elliptical galaxy"),
        (68, None, "galaxy", 13.4447, -31.9667, 8.6, 4.8, 3.4, 44000.0, "Hya", 5139, None, "Spiral galaxy"),
        (69, "Bug Nebula", "planetary_nebula", 17.2267, -37.1000, 9.6, 2.5, None, 5.1, "Sco", 6302, None, "Bipolar planetary nebula"),
        (70, None, "globular_cluster", 18.1103, -32.3000, 7.9, 7.8, None, 29.4, "Sgr", 6681, None, "Globular cluster"),
        # C71-C80
        (71, None, "open_cluster", 3.6167, -36.1333, 5.8, 12.0, None, 2.3, "Pup", 2477, None, "Rich open cluster"),
        (72, None, "galaxy", 0.8000, -39.1833, 8.2, 7.5, 6.5, 14000.0, "Scl", 55, None, "Spiral galaxy"),
        (73, None, "globular_cluster", 21.4900, -12.5333, 7.7, 4.0, None, 61.0, "Aqr", 6994, None, "Small asterism"),
        (74, "Eight-Burst Nebula", "planetary_nebula", 11.4017, -40.4333, 7.9, 1.4, None, 2.0, "Vel", 3132, None, "Bright southern planetary"),
        (75, None, "galaxy", 13.4167, -43.0167, 7.4, 13.0, 2.5, 12900.0, "Cen", 5128, None, "Centaurus A - radio galaxy"),
        (76, None, "open_cluster", 7.9500, -40.6667, 4.5, 95.0, None, 2.5, "Vel", None, 2391, "Large open cluster"),
        (77, "Centaurus A", "galaxy", 13.4250, -43.0167, 7.0, 25.7, 20.0, 12900.0, "Cen", 5128, None, "Famous radio galaxy"),
        (78, "NGC 6541", "globular_cluster", 18.1342, -43.7000, 6.6, 15.0, None, 22.8, "CrA", 6541, None, "Bright globular"),
        (79, None, "globular_cluster", 3.2033, -24.5250, 7.7, 9.6, None, 42.1, "Lep", 1904, None, "Globular cluster"),
        (80, "Omega Centauri", "globular_cluster", 13.4478, -47.4794, 3.7, 55.0, None, 15.8, "Cen", 5139, None, "Largest Milky Way globular"),
        # C81-C90
        (81, None, "globular_cluster", 19.7000, -30.4833, 7.5, 3.2, None, 41.0, "Sgr", 6352, None, "Globular cluster"),
        (82, None, "globular_cluster", 19.1667, -37.1000, 8.1, 2.9, None, 75.0, "CrA", 6388, None, "Dense globular cluster"),
        (83, None, "globular_cluster", 13.0667, -46.4167, 6.2, 17.0, None, 34.0, "Cen", 4945, None, "Globular cluster"),
        (84, "Centaurus Cluster", "galaxy", 12.8833, -41.3333, 7.8, 26.2, 6.2, 12000.0, "Cen", 4976, None, "Elliptical galaxy"),
        (85, "Omicron Velorum Cluster", "open_cluster", 8.6667, -52.9167, 2.5, 50.0, None, 0.5, "Vel", None, 2391, "Bright naked-eye cluster"),
        (86, None, "globular_cluster", 17.6917, -48.1333, 5.6, 14.1, None, 11.0, "Ara", 6397, None, "Nearby globular"),
        (87, None, "globular_cluster", 18.3417, -50.0500, 5.8, 18.0, None, 8.6, "Tel", 6584, None, "Globular cluster"),
        (88, None, "globular_cluster", 7.4833, -52.2167, 8.0, 4.7, None, 32.6, "Cir", 2808, None, "Globular cluster"),
        (89, None, "open_cluster", 10.7167, -64.4000, 1.9, 50.0, None, 0.479, "Car", None, 2602, "Southern Pleiades"),
        (90, "Carina Nebula", "emission_nebula", 10.7333, -59.8667, 1.0, 120.0, None, 7.5, "Car", 3372, None, "Bright emission nebula"),
        # C91-C100
        (91, None, "open_cluster", 11.1000, -58.6333, 3.0, 8.0, None, 8.5, "Car", 3532, None, "Open cluster"),
        (92, "Eta Carinae Nebula", "emission_nebula", 10.7500, -59.8667, 3.0, 120.0, 120.0, 7.5, "Car", 3372, None, "Contains Eta Carinae star"),
        (93, None, "globular_cluster", 12.4333, -70.8833, 5.4, 13.0, None, 17.9, "Mus", 4833, None, "Globular cluster"),
        (94, "Jewel Box", "open_cluster", 12.8933, -60.3667, 4.2, 10.0, None, 6.4, "Cru", 4755, None, "Colorful open cluster"),
        (95, None, "globular_cluster", 10.4333, -64.8667, 7.3, 2.7, None, 38.8, "Car", 3201, None, "Globular cluster"),
        (96, "Westerlund 2", "open_cluster", 10.4000, -57.7667, 6.7, 8.0, None, 20.0, "Car", 3293, None, "Young open cluster"),
        (97, "Tarantula Nebula", "emission_nebula", 5.6417, -69.1000, 5.0, 40.0, 25.0, 160.0, "Dor", 2070, None, "Largest known emission nebula (in LMC)"),
        (98, None, "open_cluster", 12.4333, -80.2000, 4.9, 12.0, None, 6.5, "Cru", 4609, None, "Open cluster near Coal Sack"),
        (99, "Coalsack Nebula", "dark_nebula", 12.5000, -63.0000, None, 420.0, 300.0, 0.6, "Cru", None, None, "Famous dark nebula"),
        (100, "Lambda Centauri Nebula", "emission_nebula", 11.5967, -63.0167, 5.0, 75.0, None, 6.0, "Cen", None, 2944, "Running Chicken Nebula"),
        # C101-C109
        (101, None, "galaxy", 1.0472, -44.0500, 9.4, 7.0, 3.4, 11800.0, "Phe", 6744, None, "Spiral galaxy"),
        (102, "Southern Pinwheel", "galaxy", 1.6200, -55.2500, 7.0, 12.9, 11.5, 14700.0, "Dor", None, 5236, "Face-on spiral - M83 analog"),
        (103, "Toby Jug Nebula", "emission_nebula", 11.2383, -59.5500, 9.7, 1.7, None, 3.5, "Car", None, 2867, "Unusual planetary nebula"),
        (104, "NGC 362", "globular_cluster", 1.0539, -70.8483, 6.4, 14.0, None, 27.8, "Tuc", 362, None, "Bright globular near SMC"),
        (105, "NGC 4833", "globular_cluster", 12.9933, -70.8750, 7.8, 14.0, None, 19.5, "Mus", 4833, None, "Southern globular"),
        (106, "47 Tucanae", "globular_cluster", 0.4028, -72.0811, 4.0, 50.0, None, 13.4, "Tuc", 104, None, "2nd brightest globular"),
        (107, None, "globular_cluster", 16.4333, -55.3000, 6.6, 10.0, None, 17.3, "Nor", 6101, None, "Globular cluster"),
        (108, None, "globular_cluster", 18.5667, -70.1167, 8.4, 6.0, None, 45.0, "Pav", 6752, None, "Globular cluster"),
        (109, "NGC 6744", "galaxy", 19.1600, -63.8500, 8.3, 20.0, 12.9, 30000.0, "Pav", 6744, None, "Large spiral galaxy"),
    ]

    for obj in caldwell_objects:
        conn.execute(
            """
            INSERT OR REPLACE INTO caldwell
            (number, name, object_type, ra_hours, dec_degrees, magnitude,
             size_arcmin, size_minor_arcmin, distance_kly, constellation,
             ngc_number, ic_number, description)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            obj
        )

    conn.commit()
    print(f"  Imported {len(caldwell_objects)} Caldwell objects")


def verify_database(conn: sqlite3.Connection) -> None:
    """Verify database integrity."""
    print("Verifying database...")

    # Check Messier count
    cursor = conn.execute("SELECT COUNT(*) FROM messier")
    messier_count = cursor.fetchone()[0]
    print(f"  Messier objects: {messier_count}")

    if messier_count != 110:
        print(f"  WARNING: Expected 110 Messier objects, found {messier_count}")

    # Check NGC count
    cursor = conn.execute("SELECT COUNT(*) FROM ngc")
    ngc_count = cursor.fetchone()[0]
    print(f"  NGC objects: {ngc_count}")

    # Verify coordinate ranges
    cursor = conn.execute("""
        SELECT COUNT(*) FROM messier
        WHERE ra_hours < 0 OR ra_hours >= 24
           OR dec_degrees < -90 OR dec_degrees > 90
    """)
    invalid_messier = cursor.fetchone()[0]
    if invalid_messier > 0:
        print(f"  WARNING: {invalid_messier} Messier objects have invalid coordinates")

    cursor = conn.execute("""
        SELECT COUNT(*) FROM ngc
        WHERE ra_hours < 0 OR ra_hours >= 24
           OR dec_degrees < -90 OR dec_degrees > 90
    """)
    invalid_ngc = cursor.fetchone()[0]
    if invalid_ngc > 0:
        print(f"  WARNING: {invalid_ngc} NGC objects have invalid coordinates")

    # Check IC count
    cursor = conn.execute("SELECT COUNT(*) FROM ic")
    ic_count = cursor.fetchone()[0]
    print(f"  IC objects: {ic_count}")

    cursor = conn.execute("""
        SELECT COUNT(*) FROM ic
        WHERE ra_hours < 0 OR ra_hours >= 24
           OR dec_degrees < -90 OR dec_degrees > 90
    """)
    invalid_ic = cursor.fetchone()[0]
    if invalid_ic > 0:
        print(f"  WARNING: {invalid_ic} IC objects have invalid coordinates")

    # Check Hipparcos count
    cursor = conn.execute("SELECT COUNT(*) FROM hipparcos")
    hip_count = cursor.fetchone()[0]
    print(f"  Hipparcos stars: {hip_count}")

    cursor = conn.execute("""
        SELECT COUNT(*) FROM hipparcos
        WHERE ra_hours < 0 OR ra_hours >= 24
           OR dec_degrees < -90 OR dec_degrees > 90
    """)
    invalid_hip = cursor.fetchone()[0]
    if invalid_hip > 0:
        print(f"  WARNING: {invalid_hip} Hipparcos stars have invalid coordinates")

    # Check Caldwell count
    cursor = conn.execute("SELECT COUNT(*) FROM caldwell")
    caldwell_count = cursor.fetchone()[0]
    print(f"  Caldwell objects: {caldwell_count}")

    if caldwell_count != 109:
        print(f"  WARNING: Expected 109 Caldwell objects, found {caldwell_count}")

    cursor = conn.execute("""
        SELECT COUNT(*) FROM caldwell
        WHERE ra_hours < 0 OR ra_hours >= 24
           OR dec_degrees < -90 OR dec_degrees > 90
    """)
    invalid_caldwell = cursor.fetchone()[0]
    if invalid_caldwell > 0:
        print(f"  WARNING: {invalid_caldwell} Caldwell objects have invalid coordinates")

    print("  Verification complete")


def main() -> None:
    """Build the catalog database."""
    print(f"Building catalog database: {DB_PATH}")
    print()

    # Ensure parent directory exists
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    # Remove existing database
    if DB_PATH.exists():
        print(f"Removing existing database...")
        DB_PATH.unlink()

    # Create new database
    conn = sqlite3.connect(str(DB_PATH))

    try:
        create_schema(conn)
        import_messier_data(conn)
        import_sample_ngc_data(conn)
        import_sample_ic_data(conn)
        import_sample_hipparcos_data(conn)
        import_caldwell_data(conn)
        verify_database(conn)

        print()
        print(f"Database created successfully: {DB_PATH}")
        print(f"Size: {DB_PATH.stat().st_size / 1024:.1f} KB")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
