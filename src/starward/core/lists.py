"""
Custom observation lists for starward.

Allows users to create, manage, and organize lists of astronomical objects
for observation planning.
"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Tuple
import re

from starward.core.observer import get_config_dir, ensure_config_dir
from starward.core.finder import find, FinderResult, CatalogSource, ObjectCategory, TYPE_TO_CATEGORY


# =============================================================================
#  DATABASE PATH
# =============================================================================

def get_user_db_path() -> Path:
    """Get the path to the user database file."""
    return get_config_dir() / 'user.db'


def ensure_user_db() -> Path:
    """Ensure user database exists and has correct schema."""
    ensure_config_dir()
    db_path = get_user_db_path()

    conn = sqlite3.connect(str(db_path))
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS lists (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE NOT NULL,
                description TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS list_items (
                id INTEGER PRIMARY KEY,
                list_id INTEGER NOT NULL,
                catalog TEXT NOT NULL,
                designation TEXT NOT NULL,
                display_name TEXT,
                notes TEXT,
                added_at TEXT NOT NULL,
                sort_order INTEGER,
                FOREIGN KEY (list_id) REFERENCES lists(id) ON DELETE CASCADE,
                UNIQUE(list_id, catalog, designation)
            );

            CREATE INDEX IF NOT EXISTS idx_list_items_list
                ON list_items(list_id);
        """)
        conn.commit()
    finally:
        conn.close()

    return db_path


# =============================================================================
#  DATA CLASSES
# =============================================================================

@dataclass
class ListItem:
    """An item in an observation list."""
    id: int
    catalog: str
    designation: str
    display_name: Optional[str]
    notes: Optional[str]
    added_at: datetime
    sort_order: int

    @property
    def full_designation(self) -> str:
        """Get full designation with catalog prefix."""
        return self.designation

    def __str__(self) -> str:
        if self.display_name:
            return f"{self.designation} ({self.display_name})"
        return self.designation


@dataclass
class ObservationList:
    """A custom observation list."""
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    items: List[ListItem] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.items)

    def __str__(self) -> str:
        return f"{self.name} ({len(self.items)} objects)"


# =============================================================================
#  OBJECT PARSING
# =============================================================================

# Patterns for parsing object designations
_PATTERNS = [
    # Messier: M31, M 31, m31
    (r'^[Mm]\s*(\d+)$', 'messier', lambda m: f"M {m.group(1)}"),
    # NGC: NGC7000, NGC 7000, ngc7000
    (r'^[Nn][Gg][Cc]\s*(\d+)$', 'ngc', lambda m: f"NGC {m.group(1)}"),
    # IC: IC434, IC 434, ic434
    (r'^[Ii][Cc]\s*(\d+)$', 'ic', lambda m: f"IC {m.group(1)}"),
    # Caldwell: C1, C 1, Caldwell 1
    (r'^[Cc]\s*(\d+)$', 'caldwell', lambda m: f"C {m.group(1)}"),
    (r'^[Cc]aldwell\s*(\d+)$', 'caldwell', lambda m: f"C {m.group(1)}"),
    # Hipparcos: HIP32349, HIP 32349, hip32349
    (r'^[Hh][Ii][Pp]\s*(\d+)$', 'hipparcos', lambda m: f"HIP {m.group(1)}"),
]


def parse_object_designation(text: str) -> Optional[Tuple[str, str]]:
    """
    Parse an object designation string.

    Args:
        text: Object designation like "M31", "NGC 7000", "HIP 32349"

    Returns:
        Tuple of (catalog, normalized_designation) or None if invalid
    """
    text = text.strip()

    for pattern, catalog, normalizer in _PATTERNS:
        match = re.match(pattern, text)
        if match:
            return (catalog, normalizer(match))

    return None


def resolve_object(designation: str) -> Optional[FinderResult]:
    """
    Resolve an object designation to catalog data.

    Args:
        designation: Object designation like "M31", "NGC 7000"

    Returns:
        FinderResult if found, None otherwise
    """
    parsed = parse_object_designation(designation)
    if not parsed:
        return None

    catalog, normalized = parsed

    # Extract the number from the normalized designation
    import re
    match = re.search(r'\d+', normalized)
    if not match:
        return None
    number = int(match.group())

    # Direct lookup by catalog
    try:
        if catalog == 'messier':
            from starward.core.messier import MESSIER
            obj = MESSIER.get(number)
            if obj:
                return FinderResult(
                    catalog=CatalogSource.MESSIER,
                    designation=f"M {number}",
                    name=obj.name,
                    object_type=obj.object_type,
                    category=TYPE_TO_CATEGORY.get(obj.object_type, ObjectCategory.OTHER),
                    ra_hours=obj.ra_hours,
                    dec_degrees=obj.dec_degrees,
                    magnitude=obj.magnitude,
                    constellation=obj.constellation,
                    description=obj.description,
                    cross_refs=[f"NGC {obj.ngc}"] if obj.ngc else [],
                )
        elif catalog == 'ngc':
            from starward.core.ngc import NGC
            obj = NGC.get(number)
            if obj:
                cross_refs = []
                if obj.messier_number:
                    cross_refs.append(f"M {obj.messier_number}")
                return FinderResult(
                    catalog=CatalogSource.NGC,
                    designation=f"NGC {number}",
                    name=obj.name,
                    object_type=obj.object_type,
                    category=TYPE_TO_CATEGORY.get(obj.object_type, ObjectCategory.OTHER),
                    ra_hours=obj.ra_hours,
                    dec_degrees=obj.dec_degrees,
                    magnitude=obj.magnitude,
                    constellation=obj.constellation,
                    description=obj.description,
                    cross_refs=cross_refs,
                )
        elif catalog == 'ic':
            from starward.core.ic import IC
            obj = IC.get(number)
            if obj:
                cross_refs = []
                if obj.ngc_number:
                    cross_refs.append(f"NGC {obj.ngc_number}")
                return FinderResult(
                    catalog=CatalogSource.IC,
                    designation=f"IC {number}",
                    name=obj.name,
                    object_type=obj.object_type,
                    category=TYPE_TO_CATEGORY.get(obj.object_type, ObjectCategory.OTHER),
                    ra_hours=obj.ra_hours,
                    dec_degrees=obj.dec_degrees,
                    magnitude=obj.magnitude,
                    constellation=obj.constellation,
                    description=obj.description,
                    cross_refs=cross_refs,
                )
        elif catalog == 'caldwell':
            from starward.core.caldwell import Caldwell
            obj = Caldwell.get(number)
            if obj:
                cross_refs = []
                if obj.ngc_number:
                    cross_refs.append(f"NGC {obj.ngc_number}")
                if obj.ic_number:
                    cross_refs.append(f"IC {obj.ic_number}")
                return FinderResult(
                    catalog=CatalogSource.CALDWELL,
                    designation=f"C {number}",
                    name=obj.name,
                    object_type=obj.object_type,
                    category=TYPE_TO_CATEGORY.get(obj.object_type, ObjectCategory.OTHER),
                    ra_hours=obj.ra_hours,
                    dec_degrees=obj.dec_degrees,
                    magnitude=obj.magnitude,
                    constellation=obj.constellation,
                    description=obj.description,
                    cross_refs=cross_refs,
                )
        elif catalog == 'hipparcos':
            from starward.core.hipparcos import Hipparcos
            star = Hipparcos.get(number)
            if star:
                cross_refs = []
                if star.bayer:
                    cross_refs.append(star.bayer)
                return FinderResult(
                    catalog=CatalogSource.HIPPARCOS,
                    designation=f"HIP {number}",
                    name=star.name,
                    object_type="star",
                    category=ObjectCategory.STAR,
                    ra_hours=star.ra_hours,
                    dec_degrees=star.dec_degrees,
                    magnitude=star.magnitude,
                    constellation=star.constellation,
                    description=star.spectral_type or "",
                    cross_refs=cross_refs,
                )
    except (KeyError, ValueError):
        pass

    return None


# =============================================================================
#  LIST MANAGER
# =============================================================================

class ListManager:
    """Manages observation lists stored in user database."""

    def __init__(self):
        self._db_path: Optional[Path] = None

    def _ensure_db(self) -> Path:
        """Ensure database exists."""
        if self._db_path is None:
            self._db_path = ensure_user_db()
        return self._db_path

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection."""
        self._ensure_db()
        conn = sqlite3.connect(str(self._db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        return conn

    # -------------------------------------------------------------------------
    # List CRUD
    # -------------------------------------------------------------------------

    def create(self, name: str, description: Optional[str] = None) -> ObservationList:
        """
        Create a new observation list.

        Args:
            name: Name for the list
            description: Optional description

        Returns:
            The created ObservationList

        Raises:
            ValueError: If list with name already exists
        """
        now = datetime.now().isoformat()

        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                INSERT INTO lists (name, description, created_at, updated_at)
                VALUES (?, ?, ?, ?)
                """,
                (name, description, now, now)
            )
            conn.commit()

            return ObservationList(
                id=cursor.lastrowid,
                name=name,
                description=description,
                created_at=datetime.fromisoformat(now),
                updated_at=datetime.fromisoformat(now),
                items=[]
            )
        except sqlite3.IntegrityError:
            raise ValueError(f"List '{name}' already exists")
        finally:
            conn.close()

    def get(self, name: str) -> Optional[ObservationList]:
        """
        Get an observation list by name.

        Args:
            name: Name of the list

        Returns:
            ObservationList or None if not found
        """
        conn = self._get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM lists WHERE name = ?",
                (name,)
            ).fetchone()

            if not row:
                return None

            # Get items
            items_rows = conn.execute(
                """
                SELECT * FROM list_items
                WHERE list_id = ?
                ORDER BY sort_order, added_at
                """,
                (row['id'],)
            ).fetchall()

            items = [
                ListItem(
                    id=r['id'],
                    catalog=r['catalog'],
                    designation=r['designation'],
                    display_name=r['display_name'],
                    notes=r['notes'],
                    added_at=datetime.fromisoformat(r['added_at']),
                    sort_order=r['sort_order'] or 0
                )
                for r in items_rows
            ]

            return ObservationList(
                id=row['id'],
                name=row['name'],
                description=row['description'],
                created_at=datetime.fromisoformat(row['created_at']),
                updated_at=datetime.fromisoformat(row['updated_at']),
                items=items
            )
        finally:
            conn.close()

    def list_all(self) -> List[ObservationList]:
        """
        Get all observation lists.

        Returns:
            List of ObservationList (without items loaded)
        """
        conn = self._get_connection()
        try:
            rows = conn.execute(
                "SELECT * FROM lists ORDER BY name"
            ).fetchall()

            # Get item counts
            counts = {}
            for row in conn.execute(
                "SELECT list_id, COUNT(*) as count FROM list_items GROUP BY list_id"
            ).fetchall():
                counts[row['list_id']] = row['count']

            return [
                ObservationList(
                    id=r['id'],
                    name=r['name'],
                    description=r['description'],
                    created_at=datetime.fromisoformat(r['created_at']),
                    updated_at=datetime.fromisoformat(r['updated_at']),
                    items=[ListItem(0, '', '', None, None, datetime.now(), 0)] * counts.get(r['id'], 0)
                )
                for r in rows
            ]
        finally:
            conn.close()

    def delete(self, name: str) -> bool:
        """
        Delete an observation list.

        Args:
            name: Name of the list to delete

        Returns:
            True if deleted, False if not found
        """
        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "DELETE FROM lists WHERE name = ?",
                (name,)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    def rename(self, old_name: str, new_name: str) -> bool:
        """
        Rename an observation list.

        Args:
            old_name: Current name
            new_name: New name

        Returns:
            True if renamed, False if not found

        Raises:
            ValueError: If new_name already exists
        """
        now = datetime.now().isoformat()

        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                UPDATE lists
                SET name = ?, updated_at = ?
                WHERE name = ?
                """,
                (new_name, now, old_name)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError:
            raise ValueError(f"List '{new_name}' already exists")
        finally:
            conn.close()

    def update_description(self, name: str, description: Optional[str]) -> bool:
        """
        Update list description.

        Args:
            name: List name
            description: New description

        Returns:
            True if updated, False if not found
        """
        now = datetime.now().isoformat()

        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                UPDATE lists
                SET description = ?, updated_at = ?
                WHERE name = ?
                """,
                (description, now, name)
            )
            conn.commit()
            return cursor.rowcount > 0
        finally:
            conn.close()

    # -------------------------------------------------------------------------
    # Item Management
    # -------------------------------------------------------------------------

    def add_item(
        self,
        list_name: str,
        designation: str,
        notes: Optional[str] = None
    ) -> ListItem:
        """
        Add an object to a list.

        Args:
            list_name: Name of the list
            designation: Object designation (e.g., "M31", "NGC 7000")
            notes: Optional notes about this object

        Returns:
            The added ListItem

        Raises:
            ValueError: If list not found or object invalid/duplicate
        """
        # Parse and validate the designation
        parsed = parse_object_designation(designation)
        if not parsed:
            raise ValueError(f"Invalid object designation: {designation}")

        catalog, normalized = parsed

        # Resolve to get display name
        result = resolve_object(designation)
        display_name = result.name if result else None

        # Get the list
        obs_list = self.get(list_name)
        if obs_list is None:
            raise ValueError(f"List '{list_name}' not found")

        now = datetime.now().isoformat()

        # Get max sort order
        conn = self._get_connection()
        try:
            max_order = conn.execute(
                "SELECT MAX(sort_order) FROM list_items WHERE list_id = ?",
                (obs_list.id,)
            ).fetchone()[0] or 0

            cursor = conn.execute(
                """
                INSERT INTO list_items
                    (list_id, catalog, designation, display_name, notes, added_at, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (obs_list.id, catalog, normalized, display_name, notes, now, max_order + 1)
            )

            # Update list's updated_at
            conn.execute(
                "UPDATE lists SET updated_at = ? WHERE id = ?",
                (now, obs_list.id)
            )

            conn.commit()

            return ListItem(
                id=cursor.lastrowid,
                catalog=catalog,
                designation=normalized,
                display_name=display_name,
                notes=notes,
                added_at=datetime.fromisoformat(now),
                sort_order=max_order + 1
            )
        except sqlite3.IntegrityError:
            raise ValueError(f"Object '{normalized}' already in list '{list_name}'")
        finally:
            conn.close()

    def remove_item(self, list_name: str, designation: str) -> bool:
        """
        Remove an object from a list.

        Args:
            list_name: Name of the list
            designation: Object designation

        Returns:
            True if removed, False if not found
        """
        # Parse the designation
        parsed = parse_object_designation(designation)
        if not parsed:
            return False

        catalog, normalized = parsed

        # Get the list
        obs_list = self.get(list_name)
        if obs_list is None:
            return False

        now = datetime.now().isoformat()

        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                DELETE FROM list_items
                WHERE list_id = ? AND catalog = ? AND designation = ?
                """,
                (obs_list.id, catalog, normalized)
            )

            if cursor.rowcount > 0:
                # Update list's updated_at
                conn.execute(
                    "UPDATE lists SET updated_at = ? WHERE id = ?",
                    (now, obs_list.id)
                )
                conn.commit()
                return True

            return False
        finally:
            conn.close()

    def clear(self, list_name: str) -> int:
        """
        Remove all items from a list.

        Args:
            list_name: Name of the list

        Returns:
            Number of items removed
        """
        obs_list = self.get(list_name)
        if obs_list is None:
            return 0

        now = datetime.now().isoformat()

        conn = self._get_connection()
        try:
            cursor = conn.execute(
                "DELETE FROM list_items WHERE list_id = ?",
                (obs_list.id,)
            )

            # Update list's updated_at
            conn.execute(
                "UPDATE lists SET updated_at = ? WHERE id = ?",
                (now, obs_list.id)
            )

            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    def update_item_notes(
        self,
        list_name: str,
        designation: str,
        notes: Optional[str]
    ) -> bool:
        """
        Update notes for an item in a list.

        Args:
            list_name: Name of the list
            designation: Object designation
            notes: New notes (None to clear)

        Returns:
            True if updated, False if not found
        """
        parsed = parse_object_designation(designation)
        if not parsed:
            return False

        catalog, normalized = parsed

        obs_list = self.get(list_name)
        if obs_list is None:
            return False

        now = datetime.now().isoformat()

        conn = self._get_connection()
        try:
            cursor = conn.execute(
                """
                UPDATE list_items
                SET notes = ?
                WHERE list_id = ? AND catalog = ? AND designation = ?
                """,
                (notes, obs_list.id, catalog, normalized)
            )

            if cursor.rowcount > 0:
                conn.execute(
                    "UPDATE lists SET updated_at = ? WHERE id = ?",
                    (now, obs_list.id)
                )
                conn.commit()
                return True

            return False
        finally:
            conn.close()


# Singleton instance
Lists = ListManager()
