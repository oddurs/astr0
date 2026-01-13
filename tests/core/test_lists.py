"""
Tests for the observation list module.

Tests list creation, item management, and database operations.
"""

from __future__ import annotations

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch
from datetime import datetime

from starward.core.lists import (
    ListManager,
    ObservationList,
    ListItem,
    parse_object_designation,
    resolve_object,
    get_user_db_path,
    ensure_user_db,
)


# =============================================================================
#  FIXTURES
# =============================================================================

@pytest.fixture
def temp_db_dir(tmp_path):
    """Create a temporary directory for user database."""
    starward_dir = tmp_path / '.starward'
    starward_dir.mkdir()
    return starward_dir


@pytest.fixture
def list_manager(temp_db_dir):
    """Create a ListManager with temporary database."""
    # Create a fresh manager for each test
    manager = ListManager()
    # Override the db path directly to the temp location
    manager._db_path = temp_db_dir / 'user.db'

    # Initialize the database at temp location
    import sqlite3
    conn = sqlite3.connect(str(manager._db_path))
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

    return manager


# =============================================================================
#  OBJECT PARSING
# =============================================================================

class TestParseObjectDesignation:
    """Tests for parse_object_designation function."""

    def test_parse_messier_m31(self):
        """Parse M31 format."""
        result = parse_object_designation("M31")
        assert result == ("messier", "M 31")

    def test_parse_messier_with_space(self):
        """Parse M 31 format with space."""
        result = parse_object_designation("M 31")
        assert result == ("messier", "M 31")

    def test_parse_messier_lowercase(self):
        """Parse lowercase messier."""
        result = parse_object_designation("m42")
        assert result == ("messier", "M 42")

    def test_parse_ngc(self):
        """Parse NGC format."""
        result = parse_object_designation("NGC7000")
        assert result == ("ngc", "NGC 7000")

    def test_parse_ngc_with_space(self):
        """Parse NGC with space."""
        result = parse_object_designation("NGC 224")
        assert result == ("ngc", "NGC 224")

    def test_parse_ngc_lowercase(self):
        """Parse lowercase NGC."""
        result = parse_object_designation("ngc224")
        assert result == ("ngc", "NGC 224")

    def test_parse_ic(self):
        """Parse IC format."""
        result = parse_object_designation("IC434")
        assert result == ("ic", "IC 434")

    def test_parse_ic_with_space(self):
        """Parse IC with space."""
        result = parse_object_designation("IC 1396")
        assert result == ("ic", "IC 1396")

    def test_parse_caldwell(self):
        """Parse Caldwell format."""
        result = parse_object_designation("C1")
        assert result == ("caldwell", "C 1")

    def test_parse_caldwell_full(self):
        """Parse full Caldwell format."""
        result = parse_object_designation("Caldwell 14")
        assert result == ("caldwell", "C 14")

    def test_parse_hipparcos(self):
        """Parse Hipparcos format."""
        result = parse_object_designation("HIP32349")
        assert result == ("hipparcos", "HIP 32349")

    def test_parse_hipparcos_with_space(self):
        """Parse Hipparcos with space."""
        result = parse_object_designation("HIP 91262")
        assert result == ("hipparcos", "HIP 91262")

    def test_parse_invalid(self):
        """Invalid designation returns None."""
        result = parse_object_designation("invalid")
        assert result is None

    def test_parse_empty(self):
        """Empty string returns None."""
        result = parse_object_designation("")
        assert result is None


# =============================================================================
#  RESOLVE OBJECT
# =============================================================================

class TestResolveObject:
    """Tests for resolve_object function."""

    def test_resolve_messier(self):
        """Resolve Messier object."""
        result = resolve_object("M31")
        assert result is not None
        assert "Andromeda" in result.name

    def test_resolve_ngc(self):
        """Resolve NGC object."""
        result = resolve_object("NGC224")
        assert result is not None

    def test_resolve_invalid(self):
        """Invalid object returns None."""
        result = resolve_object("XYZ999999")
        assert result is None


# =============================================================================
#  LIST MANAGER - LIST OPERATIONS
# =============================================================================

class TestListManagerLists:
    """Tests for ListManager list operations."""

    def test_create_list(self, list_manager):
        """Create a new list."""
        obs_list = list_manager.create("Test List")
        assert obs_list.name == "Test List"
        assert obs_list.description is None
        assert len(obs_list) == 0

    def test_create_list_with_description(self, list_manager):
        """Create list with description."""
        obs_list = list_manager.create("Test List", "A test description")
        assert obs_list.description == "A test description"

    def test_create_duplicate_raises(self, list_manager):
        """Creating duplicate list raises ValueError."""
        list_manager.create("Test List")
        with pytest.raises(ValueError, match="already exists"):
            list_manager.create("Test List")

    def test_get_list(self, list_manager):
        """Get an existing list."""
        list_manager.create("Test List")
        obs_list = list_manager.get("Test List")
        assert obs_list is not None
        assert obs_list.name == "Test List"

    def test_get_nonexistent_list(self, list_manager):
        """Get nonexistent list returns None."""
        obs_list = list_manager.get("Nonexistent")
        assert obs_list is None

    def test_list_all_empty(self, list_manager):
        """list_all returns empty when no lists."""
        lists = list_manager.list_all()
        assert lists == []

    def test_list_all(self, list_manager):
        """list_all returns all lists."""
        list_manager.create("List 1")
        list_manager.create("List 2")
        lists = list_manager.list_all()
        assert len(lists) == 2
        names = {lst.name for lst in lists}
        assert names == {"List 1", "List 2"}

    def test_delete_list(self, list_manager):
        """Delete an existing list."""
        list_manager.create("Test List")
        result = list_manager.delete("Test List")
        assert result is True
        assert list_manager.get("Test List") is None

    def test_delete_nonexistent(self, list_manager):
        """Delete nonexistent list returns False."""
        result = list_manager.delete("Nonexistent")
        assert result is False

    def test_rename_list(self, list_manager):
        """Rename an existing list."""
        list_manager.create("Old Name")
        result = list_manager.rename("Old Name", "New Name")
        assert result is True
        assert list_manager.get("Old Name") is None
        assert list_manager.get("New Name") is not None

    def test_rename_to_existing_raises(self, list_manager):
        """Rename to existing name raises ValueError."""
        list_manager.create("List 1")
        list_manager.create("List 2")
        with pytest.raises(ValueError, match="already exists"):
            list_manager.rename("List 1", "List 2")

    def test_update_description(self, list_manager):
        """Update list description."""
        list_manager.create("Test List")
        result = list_manager.update_description("Test List", "New description")
        assert result is True
        obs_list = list_manager.get("Test List")
        assert obs_list.description == "New description"


# =============================================================================
#  LIST MANAGER - ITEM OPERATIONS
# =============================================================================

class TestListManagerItems:
    """Tests for ListManager item operations."""

    def test_add_item(self, list_manager):
        """Add item to list."""
        list_manager.create("Test List")
        item = list_manager.add_item("Test List", "M31")
        assert item.designation == "M 31"
        assert item.catalog == "messier"

    def test_add_item_with_notes(self, list_manager):
        """Add item with notes."""
        list_manager.create("Test List")
        item = list_manager.add_item("Test List", "M31", notes="Best target")
        assert item.notes == "Best target"

    def test_add_item_to_nonexistent_list(self, list_manager):
        """Add item to nonexistent list raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            list_manager.add_item("Nonexistent", "M31")

    def test_add_invalid_object(self, list_manager):
        """Add invalid object raises ValueError."""
        list_manager.create("Test List")
        with pytest.raises(ValueError, match="Invalid object"):
            list_manager.add_item("Test List", "invalid")

    def test_add_duplicate_item(self, list_manager):
        """Add duplicate item raises ValueError."""
        list_manager.create("Test List")
        list_manager.add_item("Test List", "M31")
        with pytest.raises(ValueError, match="already in list"):
            list_manager.add_item("Test List", "M31")

    def test_remove_item(self, list_manager):
        """Remove item from list."""
        list_manager.create("Test List")
        list_manager.add_item("Test List", "M31")
        result = list_manager.remove_item("Test List", "M31")
        assert result is True
        obs_list = list_manager.get("Test List")
        assert len(obs_list) == 0

    def test_remove_nonexistent_item(self, list_manager):
        """Remove nonexistent item returns False."""
        list_manager.create("Test List")
        result = list_manager.remove_item("Test List", "M42")
        assert result is False

    def test_clear_list(self, list_manager):
        """Clear all items from list."""
        list_manager.create("Test List")
        list_manager.add_item("Test List", "M31")
        list_manager.add_item("Test List", "M42")
        count = list_manager.clear("Test List")
        assert count == 2
        obs_list = list_manager.get("Test List")
        assert len(obs_list) == 0

    def test_update_item_notes(self, list_manager):
        """Update notes for item."""
        list_manager.create("Test List")
        list_manager.add_item("Test List", "M31")
        result = list_manager.update_item_notes("Test List", "M31", "Updated notes")
        assert result is True
        obs_list = list_manager.get("Test List")
        assert obs_list.items[0].notes == "Updated notes"

    def test_clear_item_notes(self, list_manager):
        """Clear notes for item."""
        list_manager.create("Test List")
        list_manager.add_item("Test List", "M31", notes="Some notes")
        result = list_manager.update_item_notes("Test List", "M31", None)
        assert result is True
        obs_list = list_manager.get("Test List")
        assert obs_list.items[0].notes is None


# =============================================================================
#  LIST ITEM ORDERING
# =============================================================================

class TestListItemOrdering:
    """Tests for list item ordering."""

    def test_items_ordered_by_add_time(self, list_manager):
        """Items maintain add order."""
        list_manager.create("Test List")
        list_manager.add_item("Test List", "M31")
        list_manager.add_item("Test List", "M42")
        list_manager.add_item("Test List", "M45")

        obs_list = list_manager.get("Test List")
        designations = [item.designation for item in obs_list.items]
        assert designations == ["M 31", "M 42", "M 45"]


# =============================================================================
#  OBSERVATION LIST DATA CLASS
# =============================================================================

class TestObservationList:
    """Tests for ObservationList dataclass."""

    def test_list_len(self, list_manager):
        """List length matches item count."""
        list_manager.create("Test List")
        list_manager.add_item("Test List", "M31")
        list_manager.add_item("Test List", "M42")
        obs_list = list_manager.get("Test List")
        assert len(obs_list) == 2

    def test_list_str(self, list_manager):
        """String representation includes name and count."""
        list_manager.create("My List")
        list_manager.add_item("My List", "M31")
        obs_list = list_manager.get("My List")
        s = str(obs_list)
        assert "My List" in s
        assert "1" in s


# =============================================================================
#  LIST ITEM DATA CLASS
# =============================================================================

class TestListItem:
    """Tests for ListItem dataclass."""

    def test_item_str_with_name(self, list_manager):
        """String representation includes display name."""
        list_manager.create("Test List")
        list_manager.add_item("Test List", "M31")
        obs_list = list_manager.get("Test List")
        item = obs_list.items[0]
        s = str(item)
        assert "M 31" in s
        if item.display_name:
            assert item.display_name in s

    def test_full_designation(self, list_manager):
        """full_designation returns designation."""
        list_manager.create("Test List")
        list_manager.add_item("Test List", "M31")
        obs_list = list_manager.get("Test List")
        item = obs_list.items[0]
        assert item.full_designation == "M 31"


# =============================================================================
#  MULTIPLE CATALOGS
# =============================================================================

class TestMultipleCatalogs:
    """Tests for items from different catalogs."""

    def test_add_ngc_object(self, list_manager):
        """Add NGC object to list."""
        list_manager.create("Test List")
        item = list_manager.add_item("Test List", "NGC224")
        assert item.catalog == "ngc"
        assert item.designation == "NGC 224"

    def test_add_ic_object(self, list_manager):
        """Add IC object to list."""
        list_manager.create("Test List")
        item = list_manager.add_item("Test List", "IC434")
        assert item.catalog == "ic"
        assert item.designation == "IC 434"

    def test_add_caldwell_object(self, list_manager):
        """Add Caldwell object to list."""
        list_manager.create("Test List")
        item = list_manager.add_item("Test List", "C14")
        assert item.catalog == "caldwell"
        assert item.designation == "C 14"

    def test_add_hipparcos_object(self, list_manager):
        """Add Hipparcos star to list."""
        list_manager.create("Test List")
        item = list_manager.add_item("Test List", "HIP91262")
        assert item.catalog == "hipparcos"
        assert item.designation == "HIP 91262"

    def test_mixed_catalog_list(self, list_manager):
        """List can contain objects from multiple catalogs."""
        list_manager.create("Mixed List")
        list_manager.add_item("Mixed List", "M31")
        list_manager.add_item("Mixed List", "NGC7000")
        list_manager.add_item("Mixed List", "C14")

        obs_list = list_manager.get("Mixed List")
        catalogs = {item.catalog for item in obs_list.items}
        assert catalogs == {"messier", "ngc", "caldwell"}
