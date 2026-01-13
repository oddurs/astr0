"""
Database access layer for astronomical catalogs.

This module provides thread-safe access to the SQLite database
containing Messier, NGC, IC, and other catalog data.
"""

from __future__ import annotations

import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Optional

# Database file location - bundled with package
_DB_PATH: Optional[Path] = None


def _get_db_path() -> Path:
    """Get the path to the catalog database file."""
    global _DB_PATH
    if _DB_PATH is None:
        # Use importlib.resources for Python 3.9+
        try:
            from importlib.resources import files
            _DB_PATH = Path(str(files('starward.data').joinpath('catalogs.db')))
        except (ImportError, TypeError):
            # Fallback for older Python or development
            _DB_PATH = Path(__file__).parent.parent / 'data' / 'catalogs.db'
    return _DB_PATH


class CatalogDatabase:
    """
    Thread-safe access to the astronomical catalog database.

    This class provides methods to query Messier, NGC, and other
    catalogs stored in the bundled SQLite database.

    Example:
        >>> db = CatalogDatabase()
        >>> m31 = db.get_messier(31)
        >>> ngc7000 = db.get_ngc(7000)
        >>> galaxies = db.filter_ngc(object_type='galaxy', limit=10)
    """

    _instance: Optional['CatalogDatabase'] = None
    _lock = threading.Lock()

    def __new__(cls) -> 'CatalogDatabase':
        """Singleton pattern for database access."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return
        self._db_path = _get_db_path()
        self._local = threading.local()
        self._initialized = True

    @contextmanager
    def _get_connection(self) -> Iterator[sqlite3.Connection]:
        """Get a thread-local database connection."""
        if not hasattr(self._local, 'connection') or self._local.connection is None:
            self._local.connection = sqlite3.connect(
                str(self._db_path),
                check_same_thread=False
            )
            self._local.connection.row_factory = sqlite3.Row

        try:
            yield self._local.connection
        except Exception:
            # On error, close and clear connection
            if hasattr(self._local, 'connection') and self._local.connection:
                self._local.connection.close()
                self._local.connection = None
            raise

    def _row_to_dict(self, row: sqlite3.Row) -> dict[str, Any]:
        """Convert a database row to a dictionary."""
        return dict(row)

    # =========================================================================
    # Messier Catalog Methods
    # =========================================================================

    def get_messier(self, number: int) -> Optional[dict[str, Any]]:
        """
        Get a Messier object by its catalog number.

        Args:
            number: Messier catalog number (1-110)

        Returns:
            Dictionary with object data, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM messier WHERE number = ?",
                (number,)
            )
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None

    def list_messier(self) -> list[dict[str, Any]]:
        """Get all Messier objects, sorted by number."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM messier ORDER BY number"
            )
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def search_messier(self, query: str, limit: int = 50) -> list[dict[str, Any]]:
        """
        Search Messier objects by name, type, description, or NGC designation.

        Args:
            query: Search string (case-insensitive)
            limit: Maximum number of results

        Returns:
            List of matching objects, sorted by number
        """
        query_pattern = f"%{query}%"

        # Extract NGC number if query contains "NGC" pattern
        ngc_number = None
        query_upper = query.upper().strip()
        if query_upper.startswith("NGC"):
            try:
                ngc_number = int(query_upper.replace("NGC", "").strip())
            except ValueError:
                pass

        with self._get_connection() as conn:
            if ngc_number is not None:
                # Search includes exact NGC number match
                cursor = conn.execute(
                    """
                    SELECT * FROM messier
                    WHERE name LIKE ? COLLATE NOCASE
                       OR object_type LIKE ? COLLATE NOCASE
                       OR constellation LIKE ? COLLATE NOCASE
                       OR description LIKE ? COLLATE NOCASE
                       OR ngc_number = ?
                    ORDER BY number
                    LIMIT ?
                    """,
                    (query_pattern, query_pattern, query_pattern, query_pattern, ngc_number, limit)
                )
            else:
                cursor = conn.execute(
                    """
                    SELECT * FROM messier
                    WHERE name LIKE ? COLLATE NOCASE
                       OR object_type LIKE ? COLLATE NOCASE
                       OR constellation LIKE ? COLLATE NOCASE
                       OR description LIKE ? COLLATE NOCASE
                    ORDER BY number
                    LIMIT ?
                    """,
                    (query_pattern, query_pattern, query_pattern, query_pattern, limit)
                )
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def filter_messier(
        self,
        object_type: Optional[str] = None,
        constellation: Optional[str] = None,
        max_magnitude: Optional[float] = None,
    ) -> list[dict[str, Any]]:
        """
        Filter Messier objects by criteria.

        Args:
            object_type: Filter by object type (case-insensitive)
            constellation: Filter by constellation (3-letter code)
            max_magnitude: Filter by maximum magnitude (brighter than)

        Returns:
            List of matching objects, sorted by number
        """
        conditions = []
        params = []

        if object_type:
            conditions.append("object_type LIKE ? COLLATE NOCASE")
            params.append(object_type)

        if constellation:
            conditions.append("constellation LIKE ? COLLATE NOCASE")
            params.append(constellation)

        if max_magnitude is not None:
            conditions.append("magnitude <= ?")
            params.append(max_magnitude)

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        with self._get_connection() as conn:
            cursor = conn.execute(
                f"SELECT * FROM messier WHERE {where_clause} ORDER BY number",
                params
            )
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def count_messier(self) -> int:
        """Get the total count of Messier objects."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM messier")
            return cursor.fetchone()[0]

    # =========================================================================
    # NGC Catalog Methods
    # =========================================================================

    def get_ngc(self, number: int) -> Optional[dict[str, Any]]:
        """
        Get an NGC object by its catalog number.

        Args:
            number: NGC catalog number

        Returns:
            Dictionary with object data, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM ngc WHERE number = ?",
                (number,)
            )
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None

    def get_ngc_by_messier(self, messier_number: int) -> Optional[dict[str, Any]]:
        """
        Get an NGC object by its Messier cross-reference.

        Args:
            messier_number: Messier catalog number (1-110)

        Returns:
            Dictionary with object data, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM ngc WHERE messier_number = ?",
                (messier_number,)
            )
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None

    def list_ngc(
        self,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        Get NGC objects, sorted by number.

        Args:
            limit: Maximum number of results (None for all)
            offset: Number of results to skip

        Returns:
            List of NGC objects
        """
        with self._get_connection() as conn:
            if limit is not None:
                cursor = conn.execute(
                    "SELECT * FROM ngc ORDER BY number LIMIT ? OFFSET ?",
                    (limit, offset)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM ngc ORDER BY number"
                )
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def search_ngc(
        self,
        query: str,
        limit: int = 50
    ) -> list[dict[str, Any]]:
        """
        Search NGC objects by name, type, or description.

        Args:
            query: Search string (case-insensitive)
            limit: Maximum number of results

        Returns:
            List of matching objects, sorted by number
        """
        query_pattern = f"%{query}%"
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM ngc
                WHERE name LIKE ? COLLATE NOCASE
                   OR object_type LIKE ? COLLATE NOCASE
                   OR constellation LIKE ? COLLATE NOCASE
                   OR description LIKE ? COLLATE NOCASE
                   OR hubble_type LIKE ? COLLATE NOCASE
                ORDER BY number
                LIMIT ?
                """,
                (query_pattern, query_pattern, query_pattern,
                 query_pattern, query_pattern, limit)
            )
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def filter_ngc(
        self,
        object_type: Optional[str] = None,
        constellation: Optional[str] = None,
        max_magnitude: Optional[float] = None,
        has_name: bool = False,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        Filter NGC objects by criteria.

        Args:
            object_type: Filter by object type (case-insensitive)
            constellation: Filter by constellation (3-letter code)
            max_magnitude: Filter by maximum magnitude (brighter than)
            has_name: Only return objects with common names
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of matching objects, sorted by number
        """
        conditions = []
        params: list[Any] = []

        if object_type:
            conditions.append("object_type LIKE ? COLLATE NOCASE")
            params.append(object_type)

        if constellation:
            conditions.append("constellation LIKE ? COLLATE NOCASE")
            params.append(constellation)

        if max_magnitude is not None:
            conditions.append("magnitude IS NOT NULL AND magnitude <= ?")
            params.append(max_magnitude)

        if has_name:
            conditions.append("name IS NOT NULL AND name != ''")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"SELECT * FROM ngc WHERE {where_clause} ORDER BY number"

        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def count_ngc(self) -> int:
        """Get the total count of NGC objects."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM ngc")
            return cursor.fetchone()[0]

    def ngc_stats(self) -> dict[str, Any]:
        """
        Get statistics about the NGC catalog.

        Returns:
            Dictionary with counts by type, constellation, etc.
        """
        with self._get_connection() as conn:
            # Count by type
            cursor = conn.execute(
                """
                SELECT object_type, COUNT(*) as count
                FROM ngc
                GROUP BY object_type
                ORDER BY count DESC
                """
            )
            by_type = {row['object_type']: row['count'] for row in cursor.fetchall()}

            # Count by constellation
            cursor = conn.execute(
                """
                SELECT constellation, COUNT(*) as count
                FROM ngc
                GROUP BY constellation
                ORDER BY count DESC
                LIMIT 10
                """
            )
            by_constellation = {row['constellation']: row['count'] for row in cursor.fetchall()}

            # Count with names
            cursor = conn.execute(
                "SELECT COUNT(*) FROM ngc WHERE name IS NOT NULL AND name != ''"
            )
            named_count = cursor.fetchone()[0]

            # Count with Messier cross-reference
            cursor = conn.execute(
                "SELECT COUNT(*) FROM ngc WHERE messier_number IS NOT NULL"
            )
            messier_count = cursor.fetchone()[0]

            return {
                'total': self.count_ngc(),
                'by_type': by_type,
                'top_constellations': by_constellation,
                'with_common_name': named_count,
                'with_messier_designation': messier_count,
            }

    # =========================================================================
    # IC Catalog Methods
    # =========================================================================

    def get_ic(self, number: int) -> Optional[dict[str, Any]]:
        """
        Get an IC object by its catalog number.

        Args:
            number: IC catalog number

        Returns:
            Dictionary with object data, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM ic WHERE number = ?",
                (number,)
            )
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None

    def get_ic_by_ngc(self, ngc_number: int) -> Optional[dict[str, Any]]:
        """
        Get an IC object by its NGC cross-reference.

        Args:
            ngc_number: NGC catalog number

        Returns:
            Dictionary with object data, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM ic WHERE ngc_number = ?",
                (ngc_number,)
            )
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None

    def list_ic(
        self,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        Get IC objects, sorted by number.

        Args:
            limit: Maximum number of results (None for all)
            offset: Number of results to skip

        Returns:
            List of IC objects
        """
        with self._get_connection() as conn:
            if limit is not None:
                cursor = conn.execute(
                    "SELECT * FROM ic ORDER BY number LIMIT ? OFFSET ?",
                    (limit, offset)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM ic ORDER BY number"
                )
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def search_ic(
        self,
        query: str,
        limit: int = 50
    ) -> list[dict[str, Any]]:
        """
        Search IC objects by name, type, or description.

        Args:
            query: Search string (case-insensitive)
            limit: Maximum number of results

        Returns:
            List of matching objects, sorted by number
        """
        query_pattern = f"%{query}%"
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM ic
                WHERE name LIKE ? COLLATE NOCASE
                   OR object_type LIKE ? COLLATE NOCASE
                   OR constellation LIKE ? COLLATE NOCASE
                   OR description LIKE ? COLLATE NOCASE
                   OR hubble_type LIKE ? COLLATE NOCASE
                ORDER BY number
                LIMIT ?
                """,
                (query_pattern, query_pattern, query_pattern,
                 query_pattern, query_pattern, limit)
            )
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def filter_ic(
        self,
        object_type: Optional[str] = None,
        constellation: Optional[str] = None,
        max_magnitude: Optional[float] = None,
        has_name: bool = False,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        Filter IC objects by criteria.

        Args:
            object_type: Filter by object type (case-insensitive)
            constellation: Filter by constellation (3-letter code)
            max_magnitude: Filter by maximum magnitude (brighter than)
            has_name: Only return objects with common names
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of matching objects, sorted by number
        """
        conditions = []
        params: list[Any] = []

        if object_type:
            conditions.append("object_type LIKE ? COLLATE NOCASE")
            params.append(object_type)

        if constellation:
            conditions.append("constellation LIKE ? COLLATE NOCASE")
            params.append(constellation)

        if max_magnitude is not None:
            conditions.append("magnitude IS NOT NULL AND magnitude <= ?")
            params.append(max_magnitude)

        if has_name:
            conditions.append("name IS NOT NULL AND name != ''")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"SELECT * FROM ic WHERE {where_clause} ORDER BY number"

        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def count_ic(self) -> int:
        """Get the total count of IC objects."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM ic")
            return cursor.fetchone()[0]

    def ic_stats(self) -> dict[str, Any]:
        """
        Get statistics about the IC catalog.

        Returns:
            Dictionary with counts by type, constellation, etc.
        """
        with self._get_connection() as conn:
            # Count by type
            cursor = conn.execute(
                """
                SELECT object_type, COUNT(*) as count
                FROM ic
                GROUP BY object_type
                ORDER BY count DESC
                """
            )
            by_type = {row['object_type']: row['count'] for row in cursor.fetchall()}

            # Count by constellation
            cursor = conn.execute(
                """
                SELECT constellation, COUNT(*) as count
                FROM ic
                GROUP BY constellation
                ORDER BY count DESC
                LIMIT 10
                """
            )
            by_constellation = {row['constellation']: row['count'] for row in cursor.fetchall()}

            # Count with names
            cursor = conn.execute(
                "SELECT COUNT(*) FROM ic WHERE name IS NOT NULL AND name != ''"
            )
            named_count = cursor.fetchone()[0]

            # Count with NGC cross-reference
            cursor = conn.execute(
                "SELECT COUNT(*) FROM ic WHERE ngc_number IS NOT NULL"
            )
            ngc_count = cursor.fetchone()[0]

            return {
                'total': self.count_ic(),
                'by_type': by_type,
                'top_constellations': by_constellation,
                'with_common_name': named_count,
                'with_ngc_designation': ngc_count,
            }

    # =========================================================================
    # Hipparcos Catalog Methods
    # =========================================================================

    def get_hipparcos(self, hip_number: int) -> Optional[dict[str, Any]]:
        """
        Get a Hipparcos star by its catalog number.

        Args:
            hip_number: Hipparcos catalog number

        Returns:
            Dictionary with star data, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM hipparcos WHERE hip_number = ?",
                (hip_number,)
            )
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None

    def get_hipparcos_by_name(self, name: str) -> Optional[dict[str, Any]]:
        """
        Get a Hipparcos star by its common name.

        Args:
            name: Star name (case-insensitive)

        Returns:
            Dictionary with star data, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM hipparcos WHERE name LIKE ? COLLATE NOCASE",
                (name,)
            )
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None

    def get_hipparcos_by_bayer(self, bayer: str) -> Optional[dict[str, Any]]:
        """
        Get a Hipparcos star by its Bayer designation.

        Args:
            bayer: Bayer designation (e.g., "Alpha Orionis")

        Returns:
            Dictionary with star data, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM hipparcos WHERE bayer LIKE ? COLLATE NOCASE",
                (f"%{bayer}%",)
            )
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None

    def list_hipparcos(
        self,
        limit: Optional[int] = None,
        offset: int = 0,
        order_by: str = "magnitude"
    ) -> list[dict[str, Any]]:
        """
        Get Hipparcos stars, sorted by specified field.

        Args:
            limit: Maximum number of results (None for all)
            offset: Number of results to skip
            order_by: Field to sort by ("magnitude", "hip_number", "name")

        Returns:
            List of star dictionaries
        """
        # Validate order_by to prevent SQL injection
        valid_orders = {"magnitude", "hip_number", "name", "distance_ly"}
        if order_by not in valid_orders:
            order_by = "magnitude"

        with self._get_connection() as conn:
            if limit is not None:
                cursor = conn.execute(
                    f"SELECT * FROM hipparcos ORDER BY {order_by} LIMIT ? OFFSET ?",
                    (limit, offset)
                )
            else:
                cursor = conn.execute(
                    f"SELECT * FROM hipparcos ORDER BY {order_by}"
                )
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def search_hipparcos(
        self,
        query: str,
        limit: int = 50
    ) -> list[dict[str, Any]]:
        """
        Search Hipparcos stars by name, Bayer designation, or spectral type.

        Args:
            query: Search string (case-insensitive)
            limit: Maximum number of results

        Returns:
            List of matching stars, sorted by magnitude
        """
        query_pattern = f"%{query}%"
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM hipparcos
                WHERE name LIKE ? COLLATE NOCASE
                   OR bayer LIKE ? COLLATE NOCASE
                   OR spectral_type LIKE ? COLLATE NOCASE
                   OR constellation LIKE ? COLLATE NOCASE
                ORDER BY magnitude
                LIMIT ?
                """,
                (query_pattern, query_pattern, query_pattern,
                 query_pattern, limit)
            )
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def filter_hipparcos(
        self,
        constellation: Optional[str] = None,
        max_magnitude: Optional[float] = None,
        spectral_class: Optional[str] = None,
        has_name: bool = False,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        Filter Hipparcos stars by criteria.

        Args:
            constellation: Filter by constellation (3-letter code)
            max_magnitude: Filter by maximum magnitude (brighter than)
            spectral_class: Filter by spectral class prefix (e.g., "A", "K")
            has_name: Only return stars with common names
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of matching stars, sorted by magnitude
        """
        conditions = []
        params: list[Any] = []

        if constellation:
            conditions.append("constellation LIKE ? COLLATE NOCASE")
            params.append(constellation)

        if max_magnitude is not None:
            conditions.append("magnitude <= ?")
            params.append(max_magnitude)

        if spectral_class:
            conditions.append("spectral_type LIKE ? COLLATE NOCASE")
            params.append(f"{spectral_class}%")

        if has_name:
            conditions.append("name IS NOT NULL AND name != ''")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"SELECT * FROM hipparcos WHERE {where_clause} ORDER BY magnitude"

        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def count_hipparcos(self) -> int:
        """Get the total count of Hipparcos stars."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM hipparcos")
            return cursor.fetchone()[0]

    def hipparcos_stats(self) -> dict[str, Any]:
        """
        Get statistics about the Hipparcos catalog.

        Returns:
            Dictionary with counts by spectral class, constellation, etc.
        """
        with self._get_connection() as conn:
            # Count by spectral class (first letter)
            cursor = conn.execute(
                """
                SELECT SUBSTR(spectral_type, 1, 1) as spectral_class, COUNT(*) as count
                FROM hipparcos
                WHERE spectral_type IS NOT NULL
                GROUP BY spectral_class
                ORDER BY count DESC
                """
            )
            by_spectral = {row['spectral_class']: row['count'] for row in cursor.fetchall()}

            # Count by constellation
            cursor = conn.execute(
                """
                SELECT constellation, COUNT(*) as count
                FROM hipparcos
                GROUP BY constellation
                ORDER BY count DESC
                LIMIT 10
                """
            )
            by_constellation = {row['constellation']: row['count'] for row in cursor.fetchall()}

            # Count with names
            cursor = conn.execute(
                "SELECT COUNT(*) FROM hipparcos WHERE name IS NOT NULL AND name != ''"
            )
            named_count = cursor.fetchone()[0]

            # Brightest star
            cursor = conn.execute(
                "SELECT name, magnitude FROM hipparcos ORDER BY magnitude LIMIT 1"
            )
            brightest = cursor.fetchone()
            brightest_info = {
                'name': brightest['name'],
                'magnitude': brightest['magnitude']
            } if brightest else None

            # Magnitude ranges
            cursor = conn.execute(
                """
                SELECT
                    MIN(magnitude) as min_mag,
                    MAX(magnitude) as max_mag,
                    AVG(magnitude) as avg_mag
                FROM hipparcos
                """
            )
            mag_stats = cursor.fetchone()

            return {
                'total': self.count_hipparcos(),
                'by_spectral_class': by_spectral,
                'top_constellations': by_constellation,
                'with_common_name': named_count,
                'brightest': brightest_info,
                'magnitude_range': {
                    'min': mag_stats['min_mag'],
                    'max': mag_stats['max_mag'],
                    'average': round(mag_stats['avg_mag'], 2) if mag_stats['avg_mag'] else None,
                },
            }

    # =========================================================================
    # Caldwell Catalog Methods
    # =========================================================================

    def get_caldwell(self, number: int) -> Optional[dict[str, Any]]:
        """
        Get a Caldwell object by its catalog number.

        Args:
            number: Caldwell catalog number (1-109)

        Returns:
            Dictionary with object data, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM caldwell WHERE number = ?",
                (number,)
            )
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None

    def get_caldwell_by_ngc(self, ngc_number: int) -> Optional[dict[str, Any]]:
        """
        Get a Caldwell object by its NGC cross-reference.

        Args:
            ngc_number: NGC catalog number

        Returns:
            Dictionary with object data, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM caldwell WHERE ngc_number = ?",
                (ngc_number,)
            )
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None

    def get_caldwell_by_ic(self, ic_number: int) -> Optional[dict[str, Any]]:
        """
        Get a Caldwell object by its IC cross-reference.

        Args:
            ic_number: IC catalog number

        Returns:
            Dictionary with object data, or None if not found
        """
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM caldwell WHERE ic_number = ?",
                (ic_number,)
            )
            row = cursor.fetchone()
            return self._row_to_dict(row) if row else None

    def list_caldwell(
        self,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        Get Caldwell objects, sorted by number.

        Args:
            limit: Maximum number of results (None for all)
            offset: Number of results to skip

        Returns:
            List of Caldwell objects
        """
        with self._get_connection() as conn:
            if limit is not None:
                cursor = conn.execute(
                    "SELECT * FROM caldwell ORDER BY number LIMIT ? OFFSET ?",
                    (limit, offset)
                )
            else:
                cursor = conn.execute(
                    "SELECT * FROM caldwell ORDER BY number"
                )
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def search_caldwell(
        self,
        query: str,
        limit: int = 50
    ) -> list[dict[str, Any]]:
        """
        Search Caldwell objects by name, type, or description.

        Args:
            query: Search string (case-insensitive)
            limit: Maximum number of results

        Returns:
            List of matching objects, sorted by number
        """
        query_pattern = f"%{query}%"
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM caldwell
                WHERE name LIKE ? COLLATE NOCASE
                   OR object_type LIKE ? COLLATE NOCASE
                   OR constellation LIKE ? COLLATE NOCASE
                   OR description LIKE ? COLLATE NOCASE
                ORDER BY number
                LIMIT ?
                """,
                (query_pattern, query_pattern, query_pattern,
                 query_pattern, limit)
            )
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def filter_caldwell(
        self,
        object_type: Optional[str] = None,
        constellation: Optional[str] = None,
        max_magnitude: Optional[float] = None,
        has_name: bool = False,
        limit: Optional[int] = None,
        offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        Filter Caldwell objects by criteria.

        Args:
            object_type: Filter by object type (case-insensitive)
            constellation: Filter by constellation (3-letter code)
            max_magnitude: Filter by maximum magnitude (brighter than)
            has_name: Only return objects with common names
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of matching objects, sorted by number
        """
        conditions = []
        params: list[Any] = []

        if object_type:
            conditions.append("object_type LIKE ? COLLATE NOCASE")
            params.append(object_type)

        if constellation:
            conditions.append("constellation LIKE ? COLLATE NOCASE")
            params.append(constellation)

        if max_magnitude is not None:
            conditions.append("magnitude IS NOT NULL AND magnitude <= ?")
            params.append(max_magnitude)

        if has_name:
            conditions.append("name IS NOT NULL AND name != ''")

        where_clause = " AND ".join(conditions) if conditions else "1=1"

        query = f"SELECT * FROM caldwell WHERE {where_clause} ORDER BY number"

        if limit is not None:
            query += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])

        with self._get_connection() as conn:
            cursor = conn.execute(query, params)
            return [self._row_to_dict(row) for row in cursor.fetchall()]

    def count_caldwell(self) -> int:
        """Get the total count of Caldwell objects."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM caldwell")
            return cursor.fetchone()[0]

    def caldwell_stats(self) -> dict[str, Any]:
        """
        Get statistics about the Caldwell catalog.

        Returns:
            Dictionary with counts by type, constellation, etc.
        """
        with self._get_connection() as conn:
            # Count by type
            cursor = conn.execute(
                """
                SELECT object_type, COUNT(*) as count
                FROM caldwell
                GROUP BY object_type
                ORDER BY count DESC
                """
            )
            by_type = {row['object_type']: row['count'] for row in cursor.fetchall()}

            # Count by constellation
            cursor = conn.execute(
                """
                SELECT constellation, COUNT(*) as count
                FROM caldwell
                GROUP BY constellation
                ORDER BY count DESC
                LIMIT 10
                """
            )
            by_constellation = {row['constellation']: row['count'] for row in cursor.fetchall()}

            # Count with names
            cursor = conn.execute(
                "SELECT COUNT(*) FROM caldwell WHERE name IS NOT NULL AND name != ''"
            )
            named_count = cursor.fetchone()[0]

            # Count with NGC cross-reference
            cursor = conn.execute(
                "SELECT COUNT(*) FROM caldwell WHERE ngc_number IS NOT NULL"
            )
            ngc_count = cursor.fetchone()[0]

            # Count with IC cross-reference
            cursor = conn.execute(
                "SELECT COUNT(*) FROM caldwell WHERE ic_number IS NOT NULL"
            )
            ic_count = cursor.fetchone()[0]

            return {
                'total': self.count_caldwell(),
                'by_type': by_type,
                'top_constellations': by_constellation,
                'with_common_name': named_count,
                'with_ngc_designation': ngc_count,
                'with_ic_designation': ic_count,
            }

    # =========================================================================
    # Database Management
    # =========================================================================

    def close(self) -> None:
        """Close the database connection for the current thread."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None

    def database_exists(self) -> bool:
        """Check if the database file exists."""
        return self._db_path.exists()

    @property
    def database_path(self) -> Path:
        """Get the path to the database file."""
        return self._db_path


# Singleton instance
_db: Optional[CatalogDatabase] = None


def get_catalog_db() -> CatalogDatabase:
    """Get the singleton catalog database instance."""
    global _db
    if _db is None:
        _db = CatalogDatabase()
    return _db
