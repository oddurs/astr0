"""
Tests for the observation list module.

Tests list creation, item management, and database operations.
"""

from __future__ import annotations

import allure
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

@allure.story("Object Parsing")
class TestParseObjectDesignation:
    """Tests for parse_object_designation function."""

    @allure.title("Parse M31 format")
    def test_parse_messier_m31(self):
        """Parse M31 format."""
        with allure.step("Parse 'M31'"):
            result = parse_object_designation("M31")
        with allure.step(f"Result: {result}"):
            assert result == ("messier", "M 31")

    @allure.title("Parse M 31 format with space")
    def test_parse_messier_with_space(self):
        """Parse M 31 format with space."""
        with allure.step("Parse 'M 31'"):
            result = parse_object_designation("M 31")
        with allure.step(f"Result: {result}"):
            assert result == ("messier", "M 31")

    @allure.title("Parse lowercase messier")
    def test_parse_messier_lowercase(self):
        """Parse lowercase messier."""
        with allure.step("Parse 'm42'"):
            result = parse_object_designation("m42")
        with allure.step(f"Result: {result}"):
            assert result == ("messier", "M 42")

    @allure.title("Parse NGC format")
    def test_parse_ngc(self):
        """Parse NGC format."""
        with allure.step("Parse 'NGC7000'"):
            result = parse_object_designation("NGC7000")
        with allure.step(f"Result: {result}"):
            assert result == ("ngc", "NGC 7000")

    @allure.title("Parse NGC with space")
    def test_parse_ngc_with_space(self):
        """Parse NGC with space."""
        with allure.step("Parse 'NGC 224'"):
            result = parse_object_designation("NGC 224")
        with allure.step(f"Result: {result}"):
            assert result == ("ngc", "NGC 224")

    @allure.title("Parse lowercase NGC")
    def test_parse_ngc_lowercase(self):
        """Parse lowercase NGC."""
        with allure.step("Parse 'ngc224'"):
            result = parse_object_designation("ngc224")
        with allure.step(f"Result: {result}"):
            assert result == ("ngc", "NGC 224")

    @allure.title("Parse IC format")
    def test_parse_ic(self):
        """Parse IC format."""
        with allure.step("Parse 'IC434'"):
            result = parse_object_designation("IC434")
        with allure.step(f"Result: {result}"):
            assert result == ("ic", "IC 434")

    @allure.title("Parse IC with space")
    def test_parse_ic_with_space(self):
        """Parse IC with space."""
        with allure.step("Parse 'IC 1396'"):
            result = parse_object_designation("IC 1396")
        with allure.step(f"Result: {result}"):
            assert result == ("ic", "IC 1396")

    @allure.title("Parse Caldwell format")
    def test_parse_caldwell(self):
        """Parse Caldwell format."""
        with allure.step("Parse 'C1'"):
            result = parse_object_designation("C1")
        with allure.step(f"Result: {result}"):
            assert result == ("caldwell", "C 1")

    @allure.title("Parse full Caldwell format")
    def test_parse_caldwell_full(self):
        """Parse full Caldwell format."""
        with allure.step("Parse 'Caldwell 14'"):
            result = parse_object_designation("Caldwell 14")
        with allure.step(f"Result: {result}"):
            assert result == ("caldwell", "C 14")

    @allure.title("Parse Hipparcos format")
    def test_parse_hipparcos(self):
        """Parse Hipparcos format."""
        with allure.step("Parse 'HIP32349'"):
            result = parse_object_designation("HIP32349")
        with allure.step(f"Result: {result}"):
            assert result == ("hipparcos", "HIP 32349")

    @allure.title("Parse Hipparcos with space")
    def test_parse_hipparcos_with_space(self):
        """Parse Hipparcos with space."""
        with allure.step("Parse 'HIP 91262'"):
            result = parse_object_designation("HIP 91262")
        with allure.step(f"Result: {result}"):
            assert result == ("hipparcos", "HIP 91262")

    @allure.title("Invalid designation returns None")
    def test_parse_invalid(self):
        """Invalid designation returns None."""
        with allure.step("Parse 'invalid'"):
            result = parse_object_designation("invalid")
        with allure.step(f"Result: {result}"):
            assert result is None

    @allure.title("Empty string returns None")
    def test_parse_empty(self):
        """Empty string returns None."""
        with allure.step("Parse ''"):
            result = parse_object_designation("")
        with allure.step(f"Result: {result}"):
            assert result is None


# =============================================================================
#  RESOLVE OBJECT
# =============================================================================

@allure.story("Resolve Object")
class TestResolveObject:
    """Tests for resolve_object function."""

    @allure.title("Resolve Messier object")
    def test_resolve_messier(self):
        """Resolve Messier object."""
        with allure.step("Resolve 'M31'"):
            result = resolve_object("M31")
        with allure.step(f"Result: {result is not None}"):
            assert result is not None
        with allure.step(f"Name contains 'Andromeda'"):
            assert "Andromeda" in result.name

    @allure.title("Resolve NGC object")
    def test_resolve_ngc(self):
        """Resolve NGC object."""
        with allure.step("Resolve 'NGC224'"):
            result = resolve_object("NGC224")
        with allure.step(f"Result: {result is not None}"):
            assert result is not None

    @allure.title("Invalid object returns None")
    def test_resolve_invalid(self):
        """Invalid object returns None."""
        with allure.step("Resolve 'XYZ999999'"):
            result = resolve_object("XYZ999999")
        with allure.step(f"Result: {result}"):
            assert result is None


# =============================================================================
#  LIST MANAGER - LIST OPERATIONS
# =============================================================================

@allure.story("List Manager - Lists")
class TestListManagerLists:
    """Tests for ListManager list operations."""

    @allure.title("Create a new list")
    def test_create_list(self, list_manager):
        """Create a new list."""
        with allure.step("Create 'Test List'"):
            obs_list = list_manager.create("Test List")
        with allure.step(f"Name = {obs_list.name}"):
            assert obs_list.name == "Test List"
        with allure.step(f"Description = {obs_list.description}"):
            assert obs_list.description is None
        with allure.step(f"Length = {len(obs_list)}"):
            assert len(obs_list) == 0

    @allure.title("Create list with description")
    def test_create_list_with_description(self, list_manager):
        """Create list with description."""
        with allure.step("Create 'Test List' with description"):
            obs_list = list_manager.create("Test List", "A test description")
        with allure.step(f"Description = {obs_list.description}"):
            assert obs_list.description == "A test description"

    @allure.title("Creating duplicate list raises ValueError")
    def test_create_duplicate_raises(self, list_manager):
        """Creating duplicate list raises ValueError."""
        with allure.step("Create 'Test List'"):
            list_manager.create("Test List")
        with allure.step("Create duplicate 'Test List'"):
            with pytest.raises(ValueError, match="already exists"):
                list_manager.create("Test List")

    @allure.title("Get an existing list")
    def test_get_list(self, list_manager):
        """Get an existing list."""
        with allure.step("Create 'Test List'"):
            list_manager.create("Test List")
        with allure.step("Get 'Test List'"):
            obs_list = list_manager.get("Test List")
        with allure.step(f"Result: {obs_list is not None}"):
            assert obs_list is not None
            assert obs_list.name == "Test List"

    @allure.title("Get nonexistent list returns None")
    def test_get_nonexistent_list(self, list_manager):
        """Get nonexistent list returns None."""
        with allure.step("Get 'Nonexistent'"):
            obs_list = list_manager.get("Nonexistent")
        with allure.step(f"Result: {obs_list}"):
            assert obs_list is None

    @allure.title("list_all returns empty when no lists")
    def test_list_all_empty(self, list_manager):
        """list_all returns empty when no lists."""
        with allure.step("Get all lists"):
            lists = list_manager.list_all()
        with allure.step(f"Count: {len(lists)}"):
            assert lists == []

    @allure.title("list_all returns all lists")
    def test_list_all(self, list_manager):
        """list_all returns all lists."""
        with allure.step("Create 'List 1' and 'List 2'"):
            list_manager.create("List 1")
            list_manager.create("List 2")
        with allure.step("Get all lists"):
            lists = list_manager.list_all()
        with allure.step(f"Count: {len(lists)}"):
            assert len(lists) == 2
        names = {lst.name for lst in lists}
        with allure.step(f"Names: {names}"):
            assert names == {"List 1", "List 2"}

    @allure.title("Delete an existing list")
    def test_delete_list(self, list_manager):
        """Delete an existing list."""
        with allure.step("Create 'Test List'"):
            list_manager.create("Test List")
        with allure.step("Delete 'Test List'"):
            result = list_manager.delete("Test List")
        with allure.step(f"Result: {result}"):
            assert result is True
            assert list_manager.get("Test List") is None

    @allure.title("Delete nonexistent list returns False")
    def test_delete_nonexistent(self, list_manager):
        """Delete nonexistent list returns False."""
        with allure.step("Delete 'Nonexistent'"):
            result = list_manager.delete("Nonexistent")
        with allure.step(f"Result: {result}"):
            assert result is False

    @allure.title("Rename an existing list")
    def test_rename_list(self, list_manager):
        """Rename an existing list."""
        with allure.step("Create 'Old Name'"):
            list_manager.create("Old Name")
        with allure.step("Rename to 'New Name'"):
            result = list_manager.rename("Old Name", "New Name")
        with allure.step(f"Result: {result}"):
            assert result is True
            assert list_manager.get("Old Name") is None
            assert list_manager.get("New Name") is not None

    @allure.title("Rename to existing name raises ValueError")
    def test_rename_to_existing_raises(self, list_manager):
        """Rename to existing name raises ValueError."""
        with allure.step("Create 'List 1' and 'List 2'"):
            list_manager.create("List 1")
            list_manager.create("List 2")
        with allure.step("Rename 'List 1' to 'List 2'"):
            with pytest.raises(ValueError, match="already exists"):
                list_manager.rename("List 1", "List 2")

    @allure.title("Update list description")
    def test_update_description(self, list_manager):
        """Update list description."""
        with allure.step("Create 'Test List'"):
            list_manager.create("Test List")
        with allure.step("Update description"):
            result = list_manager.update_description("Test List", "New description")
        with allure.step(f"Result: {result}"):
            assert result is True
        obs_list = list_manager.get("Test List")
        with allure.step(f"Description: {obs_list.description}"):
            assert obs_list.description == "New description"


# =============================================================================
#  LIST MANAGER - ITEM OPERATIONS
# =============================================================================

@allure.story("List Manager - Items")
class TestListManagerItems:
    """Tests for ListManager item operations."""

    @allure.title("Add item to list")
    def test_add_item(self, list_manager):
        """Add item to list."""
        with allure.step("Create 'Test List'"):
            list_manager.create("Test List")
        with allure.step("Add 'M31'"):
            item = list_manager.add_item("Test List", "M31")
        with allure.step(f"Designation: {item.designation}"):
            assert item.designation == "M 31"
        with allure.step(f"Catalog: {item.catalog}"):
            assert item.catalog == "messier"

    @allure.title("Add item with notes")
    def test_add_item_with_notes(self, list_manager):
        """Add item with notes."""
        with allure.step("Create 'Test List'"):
            list_manager.create("Test List")
        with allure.step("Add 'M31' with notes"):
            item = list_manager.add_item("Test List", "M31", notes="Best target")
        with allure.step(f"Notes: {item.notes}"):
            assert item.notes == "Best target"

    @allure.title("Add item to nonexistent list raises ValueError")
    def test_add_item_to_nonexistent_list(self, list_manager):
        """Add item to nonexistent list raises ValueError."""
        with allure.step("Add 'M31' to 'Nonexistent'"):
            with pytest.raises(ValueError, match="not found"):
                list_manager.add_item("Nonexistent", "M31")

    @allure.title("Add invalid object raises ValueError")
    def test_add_invalid_object(self, list_manager):
        """Add invalid object raises ValueError."""
        with allure.step("Create 'Test List'"):
            list_manager.create("Test List")
        with allure.step("Add 'invalid'"):
            with pytest.raises(ValueError, match="Invalid object"):
                list_manager.add_item("Test List", "invalid")

    @allure.title("Add duplicate item raises ValueError")
    def test_add_duplicate_item(self, list_manager):
        """Add duplicate item raises ValueError."""
        with allure.step("Create 'Test List'"):
            list_manager.create("Test List")
        with allure.step("Add 'M31'"):
            list_manager.add_item("Test List", "M31")
        with allure.step("Add duplicate 'M31'"):
            with pytest.raises(ValueError, match="already in list"):
                list_manager.add_item("Test List", "M31")

    @allure.title("Remove item from list")
    def test_remove_item(self, list_manager):
        """Remove item from list."""
        with allure.step("Create 'Test List' and add 'M31'"):
            list_manager.create("Test List")
            list_manager.add_item("Test List", "M31")
        with allure.step("Remove 'M31'"):
            result = list_manager.remove_item("Test List", "M31")
        with allure.step(f"Result: {result}"):
            assert result is True
        obs_list = list_manager.get("Test List")
        with allure.step(f"List length: {len(obs_list)}"):
            assert len(obs_list) == 0

    @allure.title("Remove nonexistent item returns False")
    def test_remove_nonexistent_item(self, list_manager):
        """Remove nonexistent item returns False."""
        with allure.step("Create 'Test List'"):
            list_manager.create("Test List")
        with allure.step("Remove 'M42' (not in list)"):
            result = list_manager.remove_item("Test List", "M42")
        with allure.step(f"Result: {result}"):
            assert result is False

    @allure.title("Clear all items from list")
    def test_clear_list(self, list_manager):
        """Clear all items from list."""
        with allure.step("Create 'Test List' and add items"):
            list_manager.create("Test List")
            list_manager.add_item("Test List", "M31")
            list_manager.add_item("Test List", "M42")
        with allure.step("Clear list"):
            count = list_manager.clear("Test List")
        with allure.step(f"Cleared {count} items"):
            assert count == 2
        obs_list = list_manager.get("Test List")
        with allure.step(f"List length: {len(obs_list)}"):
            assert len(obs_list) == 0

    @allure.title("Update notes for item")
    def test_update_item_notes(self, list_manager):
        """Update notes for item."""
        with allure.step("Create 'Test List' and add 'M31'"):
            list_manager.create("Test List")
            list_manager.add_item("Test List", "M31")
        with allure.step("Update notes"):
            result = list_manager.update_item_notes("Test List", "M31", "Updated notes")
        with allure.step(f"Result: {result}"):
            assert result is True
        obs_list = list_manager.get("Test List")
        with allure.step(f"Notes: {obs_list.items[0].notes}"):
            assert obs_list.items[0].notes == "Updated notes"

    @allure.title("Clear notes for item")
    def test_clear_item_notes(self, list_manager):
        """Clear notes for item."""
        with allure.step("Create 'Test List' and add 'M31' with notes"):
            list_manager.create("Test List")
            list_manager.add_item("Test List", "M31", notes="Some notes")
        with allure.step("Clear notes"):
            result = list_manager.update_item_notes("Test List", "M31", None)
        with allure.step(f"Result: {result}"):
            assert result is True
        obs_list = list_manager.get("Test List")
        with allure.step(f"Notes: {obs_list.items[0].notes}"):
            assert obs_list.items[0].notes is None


# =============================================================================
#  LIST ITEM ORDERING
# =============================================================================

@allure.story("List Item Ordering")
class TestListItemOrdering:
    """Tests for list item ordering."""

    @allure.title("Items maintain add order")
    def test_items_ordered_by_add_time(self, list_manager):
        """Items maintain add order."""
        with allure.step("Create 'Test List'"):
            list_manager.create("Test List")
        with allure.step("Add M31, M42, M45 in order"):
            list_manager.add_item("Test List", "M31")
            list_manager.add_item("Test List", "M42")
            list_manager.add_item("Test List", "M45")

        obs_list = list_manager.get("Test List")
        designations = [item.designation for item in obs_list.items]
        with allure.step(f"Order: {designations}"):
            assert designations == ["M 31", "M 42", "M 45"]


# =============================================================================
#  OBSERVATION LIST DATA CLASS
# =============================================================================

@allure.story("Observation List")
class TestObservationList:
    """Tests for ObservationList dataclass."""

    @allure.title("List length matches item count")
    def test_list_len(self, list_manager):
        """List length matches item count."""
        with allure.step("Create 'Test List' and add 2 items"):
            list_manager.create("Test List")
            list_manager.add_item("Test List", "M31")
            list_manager.add_item("Test List", "M42")
        obs_list = list_manager.get("Test List")
        with allure.step(f"len(list) = {len(obs_list)}"):
            assert len(obs_list) == 2

    @allure.title("String representation includes name and count")
    def test_list_str(self, list_manager):
        """String representation includes name and count."""
        with allure.step("Create 'My List' and add item"):
            list_manager.create("My List")
            list_manager.add_item("My List", "M31")
        obs_list = list_manager.get("My List")
        s = str(obs_list)
        with allure.step(f"str = {s}"):
            assert "My List" in s
            assert "1" in s


# =============================================================================
#  LIST ITEM DATA CLASS
# =============================================================================

@allure.story("List Item")
class TestListItem:
    """Tests for ListItem dataclass."""

    @allure.title("String representation includes display name")
    def test_item_str_with_name(self, list_manager):
        """String representation includes display name."""
        with allure.step("Create 'Test List' and add 'M31'"):
            list_manager.create("Test List")
            list_manager.add_item("Test List", "M31")
        obs_list = list_manager.get("Test List")
        item = obs_list.items[0]
        s = str(item)
        with allure.step(f"str = {s}"):
            assert "M 31" in s
            if item.display_name:
                assert item.display_name in s

    @allure.title("full_designation returns designation")
    def test_full_designation(self, list_manager):
        """full_designation returns designation."""
        with allure.step("Create 'Test List' and add 'M31'"):
            list_manager.create("Test List")
            list_manager.add_item("Test List", "M31")
        obs_list = list_manager.get("Test List")
        item = obs_list.items[0]
        with allure.step(f"full_designation = {item.full_designation}"):
            assert item.full_designation == "M 31"


# =============================================================================
#  MULTIPLE CATALOGS
# =============================================================================

@allure.story("Multiple Catalogs")
class TestMultipleCatalogs:
    """Tests for items from different catalogs."""

    @allure.title("Add NGC object to list")
    def test_add_ngc_object(self, list_manager):
        """Add NGC object to list."""
        with allure.step("Create 'Test List'"):
            list_manager.create("Test List")
        with allure.step("Add 'NGC224'"):
            item = list_manager.add_item("Test List", "NGC224")
        with allure.step(f"Catalog: {item.catalog}, Designation: {item.designation}"):
            assert item.catalog == "ngc"
            assert item.designation == "NGC 224"

    @allure.title("Add IC object to list")
    def test_add_ic_object(self, list_manager):
        """Add IC object to list."""
        with allure.step("Create 'Test List'"):
            list_manager.create("Test List")
        with allure.step("Add 'IC434'"):
            item = list_manager.add_item("Test List", "IC434")
        with allure.step(f"Catalog: {item.catalog}, Designation: {item.designation}"):
            assert item.catalog == "ic"
            assert item.designation == "IC 434"

    @allure.title("Add Caldwell object to list")
    def test_add_caldwell_object(self, list_manager):
        """Add Caldwell object to list."""
        with allure.step("Create 'Test List'"):
            list_manager.create("Test List")
        with allure.step("Add 'C14'"):
            item = list_manager.add_item("Test List", "C14")
        with allure.step(f"Catalog: {item.catalog}, Designation: {item.designation}"):
            assert item.catalog == "caldwell"
            assert item.designation == "C 14"

    @allure.title("Add Hipparcos star to list")
    def test_add_hipparcos_object(self, list_manager):
        """Add Hipparcos star to list."""
        with allure.step("Create 'Test List'"):
            list_manager.create("Test List")
        with allure.step("Add 'HIP91262'"):
            item = list_manager.add_item("Test List", "HIP91262")
        with allure.step(f"Catalog: {item.catalog}, Designation: {item.designation}"):
            assert item.catalog == "hipparcos"
            assert item.designation == "HIP 91262"

    @allure.title("List can contain objects from multiple catalogs")
    def test_mixed_catalog_list(self, list_manager):
        """List can contain objects from multiple catalogs."""
        with allure.step("Create 'Mixed List'"):
            list_manager.create("Mixed List")
        with allure.step("Add M31, NGC7000, C14"):
            list_manager.add_item("Mixed List", "M31")
            list_manager.add_item("Mixed List", "NGC7000")
            list_manager.add_item("Mixed List", "C14")

        obs_list = list_manager.get("Mixed List")
        catalogs = {item.catalog for item in obs_list.items}
        with allure.step(f"Catalogs: {catalogs}"):
            assert catalogs == {"messier", "ngc", "caldwell"}
