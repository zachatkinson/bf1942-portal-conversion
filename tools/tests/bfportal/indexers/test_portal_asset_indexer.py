#!/usr/bin/env python3
"""Tests for portal_asset_indexer.py."""

import json
import sys
from pathlib import Path
from typing import Any

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from bfportal.indexers.portal_asset_indexer import (
    AvailabilityIndexer,
    CategoryIndexer,
    JSONIndexWriter,
    MarkdownCatalogWriter,
    PortalAsset,
    PortalAssetIndexerFacade,
    PortalSDKAssetReader,
    ThemeIndexer,
)


class TestPortalAsset:
    """Tests for PortalAsset value object."""

    def test_creates_asset_with_all_fields(self):
        """Test creating PortalAsset with all fields."""
        # Arrange & Act
        asset = PortalAsset(
            asset_type="TestAsset",
            directory="Category/Subcategory",
            category="spatial",
            level_restrictions=["MP_Tungsten"],
            physics_cost=5,
            mesh="test_mesh.glb",
        )

        # Assert
        assert asset.asset_type == "TestAsset"
        assert asset.directory == "Category/Subcategory"
        assert asset.category == "spatial"
        assert asset.level_restrictions == ["MP_Tungsten"]
        assert asset.physics_cost == 5
        assert asset.mesh == "test_mesh.glb"

    def test_is_unrestricted_with_empty_restrictions(self):
        """Test is_unrestricted property with no level restrictions."""
        # Arrange
        asset = PortalAsset(
            asset_type="TestAsset",
            directory="Category",
            category="spatial",
            level_restrictions=[],
            physics_cost=5,
        )

        # Act
        result = asset.is_unrestricted

        # Assert
        assert result is True

    def test_is_unrestricted_with_restrictions(self):
        """Test is_unrestricted property with level restrictions."""
        # Arrange
        asset = PortalAsset(
            asset_type="TestAsset",
            directory="Category",
            category="spatial",
            level_restrictions=["MP_Tungsten", "MP_Outskirts"],
            physics_cost=5,
        )

        # Act
        result = asset.is_unrestricted

        # Assert
        assert result is False

    def test_primary_category_from_nested_directory(self):
        """Test primary_category extraction from nested directory."""
        # Arrange
        asset = PortalAsset(
            asset_type="TestAsset",
            directory="Architecture/Buildings",
            category="spatial",
            level_restrictions=[],
            physics_cost=5,
        )

        # Act
        result = asset.primary_category

        # Assert
        assert result == "Architecture"

    def test_primary_category_from_flat_directory(self):
        """Test primary_category with single-level directory."""
        # Arrange
        asset = PortalAsset(
            asset_type="TestAsset",
            directory="Props",
            category="spatial",
            level_restrictions=[],
            physics_cost=5,
        )

        # Act
        result = asset.primary_category

        # Assert
        assert result == "Props"


class TestPortalSDKAssetReader:
    """Tests for PortalSDKAssetReader."""

    def test_read_parses_valid_asset_file(self, tmp_path: Path):
        """Test reading and parsing valid asset_types.json."""
        # Arrange
        asset_data = {
            "AssetTypes": [
                {
                    "type": "TestAsset",
                    "directory": "Category/Sub",
                    "constants": [
                        {"name": "category", "type": "string", "value": "spatial"},
                        {"name": "physicsCost", "type": "int", "value": 10},
                        {"name": "mesh", "type": "string", "value": "test.glb"},
                    ],
                    "levelRestrictions": ["MP_Tungsten"],
                }
            ]
        }
        asset_file = tmp_path / "asset_types.json"
        asset_file.write_text(json.dumps(asset_data))
        reader = PortalSDKAssetReader(asset_file)

        # Act
        assets = reader.read()

        # Assert
        assert len(assets) == 1
        assert assets[0].asset_type == "TestAsset"
        assert assets[0].directory == "Category/Sub"
        assert assets[0].category == "spatial"
        assert assets[0].physics_cost == 10
        assert assets[0].mesh == "test.glb"
        assert assets[0].level_restrictions == ["MP_Tungsten"]

    def test_read_raises_error_when_file_missing(self, tmp_path: Path):
        """Test error raised when asset_types.json doesn't exist."""
        # Arrange
        missing_file = tmp_path / "nonexistent.json"
        reader = PortalSDKAssetReader(missing_file)

        # Act & Assert
        with pytest.raises(FileNotFoundError, match="Portal SDK asset file not found"):
            reader.read()

    def test_read_handles_empty_asset_types(self, tmp_path: Path):
        """Test reading file with empty AssetTypes array."""
        # Arrange
        asset_data: dict[str, list[Any]] = {"AssetTypes": []}
        asset_file = tmp_path / "asset_types.json"
        asset_file.write_text(json.dumps(asset_data))
        reader = PortalSDKAssetReader(asset_file)

        # Act
        assets = reader.read()

        # Assert
        assert len(assets) == 0

    def test_parse_asset_with_missing_fields(self, tmp_path: Path):
        """Test parsing asset with missing optional fields."""
        # Arrange
        asset_data = {"AssetTypes": [{"type": "MinimalAsset"}]}
        asset_file = tmp_path / "asset_types.json"
        asset_file.write_text(json.dumps(asset_data))
        reader = PortalSDKAssetReader(asset_file)

        # Act
        assets = reader.read()

        # Assert
        assert len(assets) == 1
        assert assets[0].asset_type == "MinimalAsset"
        assert assets[0].directory == "Uncategorized"
        assert assets[0].category == "unknown"
        assert assets[0].physics_cost == 0
        assert assets[0].mesh is None
        assert assets[0].level_restrictions == []


class TestCategoryIndexer:
    """Tests for CategoryIndexer."""

    def test_index_groups_assets_by_primary_category(self):
        """Test indexing assets by primary category."""
        # Arrange
        assets = [
            PortalAsset("Asset1", "Architecture/Buildings", "spatial", [], 5),
            PortalAsset("Asset2", "Architecture/Walls", "spatial", [], 3),
            PortalAsset("Asset3", "Props/Furniture", "spatial", [], 2),
        ]
        indexer = CategoryIndexer()

        # Act
        result = indexer.index(assets)

        # Assert
        assert "Architecture" in result
        assert "Props" in result
        assert len(result["Architecture"]) == 2
        assert len(result["Props"]) == 1

    def test_index_sorts_assets_within_categories(self):
        """Test assets are sorted alphabetically within categories."""
        # Arrange
        assets = [
            PortalAsset("ZAsset", "Category", "spatial", [], 5),
            PortalAsset("AAsset", "Category", "spatial", [], 3),
            PortalAsset("MAsset", "Category", "spatial", [], 2),
        ]
        indexer = CategoryIndexer()

        # Act
        result = indexer.index(assets)

        # Assert
        category_assets = result["Category"]
        assert category_assets[0]["type"] == "AAsset"
        assert category_assets[1]["type"] == "MAsset"
        assert category_assets[2]["type"] == "ZAsset"

    def test_index_includes_unrestricted_flag(self):
        """Test index includes unrestricted flag for assets."""
        # Arrange
        assets = [
            PortalAsset("Unrestricted", "Category", "spatial", [], 5),
            PortalAsset("Restricted", "Category", "spatial", ["MP_Tungsten"], 5),
        ]
        indexer = CategoryIndexer()

        # Act
        result = indexer.index(assets)

        # Assert
        assets_list = result["Category"]
        unrestricted: dict[str, Any] = next(a for a in assets_list if a["type"] == "Unrestricted")
        restricted: dict[str, Any] = next(a for a in assets_list if a["type"] == "Restricted")
        assert unrestricted["unrestricted"] is True
        assert restricted["unrestricted"] is False


class TestAvailabilityIndexer:
    """Tests for AvailabilityIndexer."""

    def test_index_separates_unrestricted_assets(self):
        """Test unrestricted assets are indexed separately."""
        # Arrange
        assets = [
            PortalAsset("Asset1", "Category", "spatial", [], 5),
            PortalAsset("Asset2", "Category", "spatial", [], 5),
        ]
        indexer = AvailabilityIndexer()

        # Act
        result = indexer.index(assets)

        # Assert
        assert "unrestricted" in result
        assert len(result["unrestricted"]) == 2
        assert "Asset1" in result["unrestricted"]
        assert "Asset2" in result["unrestricted"]

    def test_index_groups_assets_by_map(self):
        """Test restricted assets are grouped by map name."""
        # Arrange
        assets = [
            PortalAsset("Asset1", "Category", "spatial", ["MP_Tungsten"], 5),
            PortalAsset("Asset2", "Category", "spatial", ["MP_Tungsten", "MP_Outskirts"], 5),
            PortalAsset("Asset3", "Category", "spatial", ["MP_Outskirts"], 5),
        ]
        indexer = AvailabilityIndexer()

        # Act
        result = indexer.index(assets)

        # Assert
        assert "MP_Tungsten" in result
        assert "MP_Outskirts" in result
        assert len(result["MP_Tungsten"]) == 2
        assert len(result["MP_Outskirts"]) == 2

    def test_index_sorts_asset_lists(self):
        """Test asset lists are sorted alphabetically."""
        # Arrange
        assets = [
            PortalAsset("ZAsset", "Category", "spatial", [], 5),
            PortalAsset("AAsset", "Category", "spatial", [], 5),
        ]
        indexer = AvailabilityIndexer()

        # Act
        result = indexer.index(assets)

        # Assert
        assert result["unrestricted"][0] == "AAsset"
        assert result["unrestricted"][1] == "ZAsset"


class TestThemeIndexer:
    """Tests for ThemeIndexer."""

    def test_index_classifies_military_assets(self):
        """Test military theme classification."""
        # Arrange
        assets = [
            PortalAsset("Military_Bunker", "Architecture", "spatial", [], 5),
            PortalAsset("Tank_Barrier", "Props", "spatial", [], 5),
        ]
        indexer = ThemeIndexer()

        # Act
        result = indexer.index(assets)

        # Assert
        assert "military" in result
        assert "Military_Bunker" in result["military"]
        assert "Tank_Barrier" in result["military"]

    def test_index_classifies_natural_assets(self):
        """Test natural theme classification."""
        # Arrange
        assets = [
            PortalAsset("Tree_Pine", "Nature", "spatial", [], 5),
            PortalAsset("Rock_Boulder", "Nature", "spatial", [], 5),
        ]
        indexer = ThemeIndexer()

        # Act
        result = indexer.index(assets)

        # Assert
        assert "natural" in result
        assert "Tree_Pine" in result["natural"]
        assert "Rock_Boulder" in result["natural"]

    def test_index_matches_keywords_in_directory(self):
        """Test theme matching in directory path."""
        # Arrange
        assets = [PortalAsset("GenericAsset", "Industrial/Factory", "spatial", [], 5)]
        indexer = ThemeIndexer()

        # Act
        result = indexer.index(assets)

        # Assert
        assert "industrial" in result
        assert "GenericAsset" in result["industrial"]

    def test_index_asset_can_match_multiple_themes(self):
        """Test asset can be classified under multiple themes."""
        # Arrange
        assets = [PortalAsset("Military_Building", "Architecture", "spatial", [], 5)]
        indexer = ThemeIndexer()

        # Act
        result = indexer.index(assets)

        # Assert
        # Should match both military (from name) and urban (from building keyword)
        assert "military" in result
        assert "urban" in result
        assert "Military_Building" in result["military"]
        assert "Military_Building" in result["urban"]


class TestJSONIndexWriter:
    """Tests for JSONIndexWriter."""

    def test_write_creates_json_file(self, tmp_path: Path):
        """Test writing index data to JSON file."""
        # Arrange
        output_file = tmp_path / "output" / "index.json"
        writer = JSONIndexWriter(output_file)
        index_data = {"test_key": "test_value", "count": 42}

        # Act
        writer.write(index_data)

        # Assert
        assert output_file.exists()
        written_data = json.loads(output_file.read_text())
        assert written_data["test_key"] == "test_value"
        assert written_data["count"] == 42

    def test_write_creates_parent_directories(self, tmp_path: Path):
        """Test write creates parent directories if they don't exist."""
        # Arrange
        output_file = tmp_path / "nested" / "deep" / "index.json"
        writer = JSONIndexWriter(output_file)
        index_data = {"test": "data"}

        # Act
        writer.write(index_data)

        # Assert
        assert output_file.parent.exists()
        assert output_file.exists()


class TestMarkdownCatalogWriter:
    """Tests for MarkdownCatalogWriter."""

    def test_write_creates_markdown_file(self, tmp_path: Path):
        """Test writing catalog to markdown file."""
        # Arrange
        output_file = tmp_path / "catalog.md"
        writer = MarkdownCatalogWriter(output_file)
        index_data = {
            "_metadata": {
                "total_assets": 100,
                "generated_date": "2025-01-01",
                "source_file": "asset_types.json",
                "unrestricted_count": 50,
                "categories": {"Props": 30, "Architecture": 70},
            },
            "by_category": {},
            "by_availability": {},
            "by_theme": {},
        }

        # Act
        writer.write(index_data)

        # Assert
        assert output_file.exists()
        content = output_file.read_text()
        assert "# Portal Asset Catalog" in content
        assert "Total Assets:** 100" in content
        assert "2025-01-01" in content

    def test_write_includes_category_summary(self, tmp_path: Path):
        """Test markdown includes category breakdown."""
        # Arrange
        output_file = tmp_path / "catalog.md"
        writer = MarkdownCatalogWriter(output_file)
        index_data = {
            "_metadata": {
                "total_assets": 10,
                "generated_date": "2025-01-01",
                "source_file": "test.json",
                "unrestricted_count": 5,
                "categories": {"Props": 3, "Architecture": 7},
            },
            "by_category": {},
            "by_availability": {},
            "by_theme": {},
        }

        # Act
        writer.write(index_data)

        # Assert
        content = output_file.read_text()
        assert "Props:** 3 assets" in content
        assert "Architecture:** 7 assets" in content


class TestPortalAssetIndexerFacade:
    """Tests for PortalAssetIndexerFacade."""

    def test_facade_initializes_all_components(self, tmp_path: Path):
        """Test facade initializes reader, writers, and indexers."""
        # Arrange
        asset_file = tmp_path / "asset_types.json"
        json_output = tmp_path / "index.json"
        md_output = tmp_path / "catalog.md"
        asset_file.write_text(json.dumps({"AssetTypes": []}))

        # Act
        facade = PortalAssetIndexerFacade(asset_file, json_output, md_output)

        # Assert
        assert facade.reader is not None
        assert facade.json_writer is not None
        assert facade.markdown_writer is not None
        assert facade.category_indexer is not None
        assert facade.availability_indexer is not None
        assert facade.theme_indexer is not None

    def test_generate_indexes_creates_complete_structure(self, tmp_path: Path):
        """Test generate_indexes creates complete index structure."""
        # Arrange
        asset_data = {
            "AssetTypes": [
                {
                    "type": "TestAsset",
                    "directory": "Category",
                    "constants": [{"name": "category", "type": "string", "value": "spatial"}],
                    "levelRestrictions": [],
                }
            ]
        }
        asset_file = tmp_path / "asset_types.json"
        asset_file.write_text(json.dumps(asset_data))
        json_output = tmp_path / "index.json"
        md_output = tmp_path / "catalog.md"
        facade = PortalAssetIndexerFacade(asset_file, json_output, md_output)

        # Act
        result = facade.generate_indexes()

        # Assert
        assert "_metadata" in result
        assert "by_category" in result
        assert "by_availability" in result
        assert "by_theme" in result
        assert result["_metadata"]["total_assets"] == 1

    def test_generate_indexes_writes_both_outputs(self, tmp_path: Path):
        """Test generate_indexes writes both JSON and markdown files."""
        # Arrange
        asset_data = {"AssetTypes": [{"type": "TestAsset", "directory": "Category"}]}
        asset_file = tmp_path / "asset_types.json"
        asset_file.write_text(json.dumps(asset_data))
        json_output = tmp_path / "index.json"
        md_output = tmp_path / "catalog.md"
        facade = PortalAssetIndexerFacade(asset_file, json_output, md_output)

        # Act
        facade.generate_indexes()

        # Assert
        assert json_output.exists()
        assert md_output.exists()
