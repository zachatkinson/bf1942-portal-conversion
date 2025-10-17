#!/usr/bin/env python3
"""Tests for AssetCatalog class.

Tests follow AAA pattern (Arrange-Act-Assert) and best practices from CLAUDE.md.

Author: Zach Atkinson
AI Assistant: Claude (Anthropic)
Date: 2025-10-17
"""

import json
import sys
from pathlib import Path

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from bfportal.validators.asset_catalog import AssetCatalog


class TestAssetCatalogInit:
    """Tests for AssetCatalog initialization."""

    def test_loads_catalog_from_default_path(self, tmp_path, monkeypatch):
        """Test AssetCatalog loads from default path when no path provided."""
        # Arrange
        catalog_data = {
            "AssetTypes": [
                {
                    "type": "TestAsset",
                    "directory": "Props/Test",
                    "levelRestrictions": ["MP_Tungsten"],
                    "constants": [],
                    "properties": [],
                }
            ]
        }
        catalog_file = tmp_path / "asset_types.json"
        catalog_file.write_text(json.dumps(catalog_data))

        # Mock get_asset_types_path to return our test file
        monkeypatch.setattr(
            "bfportal.validators.asset_catalog.get_asset_types_path",
            lambda: catalog_file,
        )

        # Act
        catalog = AssetCatalog()

        # Assert
        assert catalog.get_asset_count() == 1
        assert catalog.has_asset("TestAsset")

    def test_loads_catalog_from_custom_path(self, tmp_path):
        """Test AssetCatalog loads from custom path when provided."""
        # Arrange
        catalog_data = {
            "AssetTypes": [
                {
                    "type": "CustomAsset",
                    "directory": "Props/Custom",
                    "levelRestrictions": [],
                    "constants": [],
                    "properties": [],
                }
            ]
        }
        custom_catalog = tmp_path / "custom_catalog.json"
        custom_catalog.write_text(json.dumps(catalog_data))

        # Act
        catalog = AssetCatalog(catalog_path=custom_catalog)

        # Assert
        assert catalog.get_asset_count() == 1
        assert catalog.has_asset("CustomAsset")

    def test_raises_error_when_catalog_file_not_found(self, tmp_path):
        """Test AssetCatalog raises FileNotFoundError when catalog doesn't exist."""
        # Arrange
        nonexistent_path = tmp_path / "does_not_exist.json"

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Asset catalog not found"):
            AssetCatalog(catalog_path=nonexistent_path)

    def test_raises_error_when_catalog_has_invalid_json(self, tmp_path):
        """Test AssetCatalog raises JSONDecodeError for invalid JSON."""
        # Arrange
        invalid_json = tmp_path / "invalid.json"
        invalid_json.write_text("{invalid json content")

        # Act & Assert
        with pytest.raises(json.JSONDecodeError):
            AssetCatalog(catalog_path=invalid_json)

    def test_handles_empty_asset_types_list(self, tmp_path):
        """Test AssetCatalog handles empty AssetTypes array."""
        # Arrange
        catalog_data = {"AssetTypes": []}
        catalog_file = tmp_path / "empty_catalog.json"
        catalog_file.write_text(json.dumps(catalog_data))

        # Act
        catalog = AssetCatalog(catalog_path=catalog_file)

        # Assert
        assert catalog.get_asset_count() == 0
        assert catalog.get_all_asset_types() == []


class TestAssetCatalogGetAsset:
    """Tests for get_asset() method."""

    @pytest.fixture
    def catalog(self, tmp_path):
        """Provide AssetCatalog with test data."""
        catalog_data = {
            "AssetTypes": [
                {
                    "type": "MP_Tungsten_Bunker",
                    "directory": "Architecture/Buildings",
                    "levelRestrictions": ["MP_Tungsten", "MP_Battery"],
                    "constants": [{"name": "mesh", "type": "string", "value": "Bunker_01"}],
                    "properties": [{"name": "Health", "type": "int", "default": 1000}],
                },
                {
                    "type": "TreePine",
                    "directory": "Nature/Trees",
                    "levelRestrictions": [],
                    "constants": [],
                    "properties": [],
                },
            ]
        }
        catalog_file = tmp_path / "catalog.json"
        catalog_file.write_text(json.dumps(catalog_data))
        return AssetCatalog(catalog_path=catalog_file)

    def test_get_asset_returns_asset_data_when_exists(self, catalog):
        """Test get_asset returns asset data for existing asset."""
        # Act
        asset = catalog.get_asset("MP_Tungsten_Bunker")

        # Assert
        assert asset is not None
        assert asset["directory"] == "Architecture/Buildings"
        assert asset["level_restrictions"] == ["MP_Tungsten", "MP_Battery"]
        assert len(asset["constants"]) == 1
        assert len(asset["properties"]) == 1

    def test_get_asset_returns_none_when_not_exists(self, catalog):
        """Test get_asset returns None for non-existent asset."""
        # Act
        asset = catalog.get_asset("NonExistentAsset")

        # Assert
        assert asset is None

    def test_get_asset_returns_empty_lists_when_optional_fields_missing(self, catalog):
        """Test get_asset returns empty lists for missing optional fields."""
        # Act
        asset = catalog.get_asset("TreePine")

        # Assert
        assert asset is not None
        assert asset["level_restrictions"] == []
        assert asset["constants"] == []
        assert asset["properties"] == []


class TestAssetCatalogHasAsset:
    """Tests for has_asset() method."""

    @pytest.fixture
    def catalog(self, tmp_path):
        """Provide AssetCatalog with test data."""
        catalog_data = {
            "AssetTypes": [
                {"type": "AssetA", "directory": "Props", "levelRestrictions": []},
                {"type": "AssetB", "directory": "Props", "levelRestrictions": []},
            ]
        }
        catalog_file = tmp_path / "catalog.json"
        catalog_file.write_text(json.dumps(catalog_data))
        return AssetCatalog(catalog_path=catalog_file)

    def test_has_asset_returns_true_when_asset_exists(self, catalog):
        """Test has_asset returns True for existing asset."""
        # Act & Assert
        assert catalog.has_asset("AssetA") is True
        assert catalog.has_asset("AssetB") is True

    def test_has_asset_returns_false_when_asset_not_exists(self, catalog):
        """Test has_asset returns False for non-existent asset."""
        # Act & Assert
        assert catalog.has_asset("NonExistent") is False
        assert catalog.has_asset("") is False


class TestAssetCatalogLevelRestrictions:
    """Tests for level restriction methods."""

    @pytest.fixture
    def catalog(self, tmp_path):
        """Provide AssetCatalog with varied restriction scenarios."""
        catalog_data = {
            "AssetTypes": [
                {
                    "type": "RestrictedAsset",
                    "directory": "Props",
                    "levelRestrictions": ["MP_Tungsten", "MP_Battery"],
                },
                {
                    "type": "UnrestrictedAsset",
                    "directory": "Props",
                    "levelRestrictions": [],
                },
                {
                    "type": "SingleMapAsset",
                    "directory": "Props",
                    "levelRestrictions": ["MP_Tungsten"],
                },
            ]
        }
        catalog_file = tmp_path / "catalog.json"
        catalog_file.write_text(json.dumps(catalog_data))
        return AssetCatalog(catalog_path=catalog_file)

    def test_get_level_restrictions_returns_list_when_asset_has_restrictions(self, catalog):
        """Test get_level_restrictions returns restriction list for restricted asset."""
        # Act
        restrictions = catalog.get_level_restrictions("RestrictedAsset")

        # Assert
        assert restrictions == ["MP_Tungsten", "MP_Battery"]

    def test_get_level_restrictions_returns_empty_list_when_no_restrictions(self, catalog):
        """Test get_level_restrictions returns empty list for unrestricted asset."""
        # Act
        restrictions = catalog.get_level_restrictions("UnrestrictedAsset")

        # Assert
        assert restrictions == []

    def test_get_level_restrictions_returns_empty_list_when_asset_not_exists(self, catalog):
        """Test get_level_restrictions returns empty list for non-existent asset."""
        # Act
        restrictions = catalog.get_level_restrictions("NonExistent")

        # Assert
        assert restrictions == []

    def test_has_level_restrictions_returns_true_when_asset_restricted(self, catalog):
        """Test has_level_restrictions returns True for restricted assets."""
        # Act & Assert
        assert catalog.has_level_restrictions("RestrictedAsset") is True
        assert catalog.has_level_restrictions("SingleMapAsset") is True

    def test_has_level_restrictions_returns_false_when_no_restrictions(self, catalog):
        """Test has_level_restrictions returns False for unrestricted assets."""
        # Act & Assert
        assert catalog.has_level_restrictions("UnrestrictedAsset") is False

    def test_has_level_restrictions_returns_false_when_asset_not_exists(self, catalog):
        """Test has_level_restrictions returns False for non-existent asset."""
        # Act & Assert
        assert catalog.has_level_restrictions("NonExistent") is False


class TestAssetCatalogIsAllowedOnMap:
    """Tests for is_allowed_on_map() method."""

    @pytest.fixture
    def catalog(self, tmp_path):
        """Provide AssetCatalog with restriction scenarios."""
        catalog_data = {
            "AssetTypes": [
                {
                    "type": "TungstenOnly",
                    "directory": "Props",
                    "levelRestrictions": ["MP_Tungsten"],
                },
                {
                    "type": "TungstenAndBattery",
                    "directory": "Props",
                    "levelRestrictions": ["MP_Tungsten", "MP_Battery"],
                },
                {
                    "type": "Unrestricted",
                    "directory": "Props",
                    "levelRestrictions": [],
                },
            ]
        }
        catalog_file = tmp_path / "catalog.json"
        catalog_file.write_text(json.dumps(catalog_data))
        return AssetCatalog(catalog_path=catalog_file)

    def test_is_allowed_on_map_returns_true_when_map_in_restrictions(self, catalog):
        """Test is_allowed_on_map returns True when map is in restriction list."""
        # Act & Assert
        assert catalog.is_allowed_on_map("TungstenOnly", "MP_Tungsten") is True
        assert catalog.is_allowed_on_map("TungstenAndBattery", "MP_Tungsten") is True
        assert catalog.is_allowed_on_map("TungstenAndBattery", "MP_Battery") is True

    def test_is_allowed_on_map_returns_false_when_map_not_in_restrictions(self, catalog):
        """Test is_allowed_on_map returns False when map not in restriction list."""
        # Act & Assert
        assert catalog.is_allowed_on_map("TungstenOnly", "MP_Battery") is False
        assert catalog.is_allowed_on_map("TungstenOnly", "MP_FireStorm") is False

    def test_is_allowed_on_map_returns_true_when_no_restrictions(self, catalog):
        """Test is_allowed_on_map returns True for unrestricted assets on any map."""
        # Act & Assert
        assert catalog.is_allowed_on_map("Unrestricted", "MP_Tungsten") is True
        assert catalog.is_allowed_on_map("Unrestricted", "MP_Battery") is True
        assert catalog.is_allowed_on_map("Unrestricted", "MP_FireStorm") is True
        assert catalog.is_allowed_on_map("Unrestricted", "AnyMap") is True

    def test_is_allowed_on_map_returns_true_when_asset_not_exists(self, catalog):
        """Test is_allowed_on_map returns True for non-existent asset (no restrictions)."""
        # Act & Assert
        # Non-existent assets are treated as unrestricted (no restrictions = allowed everywhere)
        assert catalog.is_allowed_on_map("NonExistent", "MP_Tungsten") is True


class TestAssetCatalogUtilityMethods:
    """Tests for utility methods."""

    @pytest.fixture
    def catalog(self, tmp_path):
        """Provide AssetCatalog with multiple assets."""
        catalog_data = {
            "AssetTypes": [
                {"type": "Asset1", "directory": "Props", "levelRestrictions": []},
                {"type": "Asset2", "directory": "Props", "levelRestrictions": []},
                {"type": "Asset3", "directory": "Props", "levelRestrictions": []},
            ]
        }
        catalog_file = tmp_path / "catalog.json"
        catalog_file.write_text(json.dumps(catalog_data))
        return AssetCatalog(catalog_path=catalog_file)

    def test_get_asset_count_returns_correct_count(self, catalog):
        """Test get_asset_count returns correct number of assets."""
        # Act
        count = catalog.get_asset_count()

        # Assert
        assert count == 3

    def test_get_all_asset_types_returns_all_type_names(self, catalog):
        """Test get_all_asset_types returns list of all asset type names."""
        # Act
        types = catalog.get_all_asset_types()

        # Assert
        assert len(types) == 3
        assert "Asset1" in types
        assert "Asset2" in types
        assert "Asset3" in types

    def test_get_all_asset_types_returns_empty_list_for_empty_catalog(self, tmp_path):
        """Test get_all_asset_types returns empty list when catalog is empty."""
        # Arrange
        catalog_data = {"AssetTypes": []}
        catalog_file = tmp_path / "empty.json"
        catalog_file.write_text(json.dumps(catalog_data))
        catalog = AssetCatalog(catalog_path=catalog_file)

        # Act
        types = catalog.get_all_asset_types()

        # Assert
        assert types == []


class TestAssetCatalogEdgeCases:
    """Tests for edge cases and error scenarios."""

    def test_handles_asset_without_type_field(self, tmp_path):
        """Test AssetCatalog skips assets without 'type' field."""
        # Arrange
        catalog_data = {
            "AssetTypes": [
                {"directory": "Props", "levelRestrictions": []},  # Missing 'type'
                {"type": "ValidAsset", "directory": "Props", "levelRestrictions": []},
            ]
        }
        catalog_file = tmp_path / "catalog.json"
        catalog_file.write_text(json.dumps(catalog_data))

        # Act
        catalog = AssetCatalog(catalog_path=catalog_file)

        # Assert - Only valid asset is loaded
        assert catalog.get_asset_count() == 1
        assert catalog.has_asset("ValidAsset")

    def test_handles_missing_optional_fields_gracefully(self, tmp_path):
        """Test AssetCatalog provides defaults for missing optional fields."""
        # Arrange
        catalog_data = {
            "AssetTypes": [
                {
                    "type": "MinimalAsset",
                    # Missing: directory, levelRestrictions, constants, properties
                }
            ]
        }
        catalog_file = tmp_path / "catalog.json"
        catalog_file.write_text(json.dumps(catalog_data))

        # Act
        catalog = AssetCatalog(catalog_path=catalog_file)
        asset = catalog.get_asset("MinimalAsset")

        # Assert
        assert asset is not None
        assert asset["directory"] == ""  # Default empty string
        assert asset["level_restrictions"] == []  # Default empty list
        assert asset["constants"] == []
        assert asset["properties"] == []

    def test_handles_duplicate_asset_types_by_using_last(self, tmp_path):
        """Test AssetCatalog handles duplicate asset types (last one wins)."""
        # Arrange
        catalog_data = {
            "AssetTypes": [
                {
                    "type": "DuplicateAsset",
                    "directory": "Props/First",
                    "levelRestrictions": ["MP_Tungsten"],
                },
                {
                    "type": "DuplicateAsset",
                    "directory": "Props/Second",
                    "levelRestrictions": ["MP_Battery"],
                },
            ]
        }
        catalog_file = tmp_path / "catalog.json"
        catalog_file.write_text(json.dumps(catalog_data))

        # Act
        catalog = AssetCatalog(catalog_path=catalog_file)
        asset = catalog.get_asset("DuplicateAsset")

        # Assert - Last entry wins
        assert catalog.get_asset_count() == 1  # Only one unique asset type
        assert asset["directory"] == "Props/Second"
        assert asset["level_restrictions"] == ["MP_Battery"]
