#!/usr/bin/env python3
"""Unit tests for AssetMapper."""

import sys
from pathlib import Path
from unittest.mock import patch

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bfportal.core.interfaces import MapContext, Team
from bfportal.mappers.asset_mapper import AssetMapper


class TestAssetMapperInitialization:
    """Test cases for AssetMapper initialization."""

    def test_init_loads_portal_assets(self, sample_portal_assets):
        """Test that initialization loads Portal assets correctly."""
        # Arrange
        assets = sample_portal_assets

        # Act
        mapper = AssetMapper(assets)

        # Assert
        assert len(mapper.portal_assets) == 6
        assert "Tree_Pine_Large" in mapper.portal_assets
        assert "Rock_Boulder_01" in mapper.portal_assets

    def test_init_loads_portal_asset_properties(self, sample_portal_assets):
        """Test that Portal asset properties are loaded correctly."""
        # Arrange
        assets = sample_portal_assets

        # Act
        mapper = AssetMapper(assets)

        # Assert
        tree_asset = mapper.portal_assets["Tree_Pine_Large"]
        assert tree_asset.type == "Tree_Pine_Large"
        assert tree_asset.directory == "Nature/Trees"
        assert tree_asset.level_restrictions == []

    def test_init_loads_level_restrictions(self, sample_portal_assets):
        """Test that level restrictions are loaded correctly."""
        # Arrange
        assets = sample_portal_assets

        # Act
        mapper = AssetMapper(assets)

        # Assert
        oak_asset = mapper.portal_assets["Tree_Oak_Medium"]
        assert oak_asset.level_restrictions == ["MP_Tungsten"]

    def test_init_with_fallback_keywords_loads_file(self, sample_portal_assets, tmp_path):
        """Test initialization loads fallback keywords from file when it exists."""
        # Arrange
        import json

        fake_module_path = tmp_path / "tools" / "bfportal" / "mappers" / "asset_mapper.py"
        fake_module_path.parent.mkdir(parents=True)
        fake_module_path.write_text("")

        keywords_file = tmp_path / "tools" / "asset_audit" / "asset_fallback_keywords.json"
        keywords_file.parent.mkdir(parents=True)
        keywords_data = {
            "type_categories": [
                {"source_keywords": ["tree", "pine"], "portal_keywords": ["tree", "pine"]},
                {"source_keywords": ["rock", "stone"], "portal_keywords": ["rock", "stone"]},
            ]
        }
        keywords_file.write_text(json.dumps(keywords_data))

        # Act
        with patch("bfportal.mappers.asset_mapper.__file__", str(fake_module_path)):
            mapper = AssetMapper(sample_portal_assets)

        # Assert
        assert len(mapper.fallback_keywords) == 2
        assert mapper.fallback_keywords[0]["source_keywords"] == ["tree", "pine"]
        assert mapper.fallback_keywords[1]["source_keywords"] == ["rock", "stone"]

    def test_init_without_fallback_keywords_file_uses_empty_list(
        self, sample_portal_assets, tmp_path
    ):
        """Test initialization gracefully handles missing fallback keywords file."""
        # Arrange
        fake_module_path = tmp_path / "tools" / "bfportal" / "mappers" / "asset_mapper.py"
        fake_module_path.parent.mkdir(parents=True)
        fake_module_path.write_text("")

        # Act
        with patch("bfportal.mappers.asset_mapper.__file__", str(fake_module_path)):
            mapper = AssetMapper(sample_portal_assets)

        # Assert
        assert mapper.fallback_keywords == []


class TestAssetMapperLoadMappings:
    """Test cases for loading BF1942 to Portal mappings."""

    def test_load_mappings_success(self, sample_portal_assets, sample_bf1942_mappings):
        """Test loading mappings from valid JSON file."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)

        # Act
        mapper.load_mappings(sample_bf1942_mappings)

        # Assert
        assert len(mapper.mappings) > 0
        assert "treeline_pine_w" in mapper.mappings
        assert "sandbags_wall" in mapper.mappings

    def test_load_mappings_stores_metadata(self, sample_portal_assets, sample_bf1942_mappings):
        """Test that mapping metadata is stored correctly."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)

        # Act
        mapper.load_mappings(sample_bf1942_mappings)

        # Assert
        pine_mapping = mapper.mappings["treeline_pine_w"]
        assert pine_mapping["portal_type"] == "Tree_Pine_Large"
        assert pine_mapping["category"] == "vegetation"
        assert pine_mapping["confidence"] == 5

    def test_load_mappings_stores_fallbacks(self, sample_portal_assets, sample_bf1942_mappings):
        """Test that map-specific fallbacks are stored."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)

        # Act
        mapper.load_mappings(sample_bf1942_mappings)

        # Assert
        oak_mapping = mapper.mappings["treeline_oak_w"]
        assert "fallbacks" in oak_mapping
        assert oak_mapping["fallbacks"]["MP_Battery"] == "Tree_Pine_Large"

    def test_load_mappings_file_not_found(self, sample_portal_assets, tmp_path):
        """Test loading mappings raises error when file not found."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        nonexistent_file = tmp_path / "nonexistent.json"

        # Act/Assert
        with pytest.raises(FileNotFoundError, match="Mappings file not found"):
            mapper.load_mappings(nonexistent_file)

    def test_load_mappings_skips_todo_entries(self, sample_portal_assets, tmp_path):
        """Test that TODO entries are skipped during loading."""
        # Arrange
        mappings_data = {
            "props": {
                "asset_with_mapping": {
                    "portal_equivalent": "Prop_Sandbag_Wall",
                    "category": "prop",
                    "confidence_score": 5,
                },
                "asset_without_mapping": {
                    "portal_equivalent": "TODO",
                    "category": "prop",
                    "confidence_score": 0,
                },
            }
        }

        mappings_path = tmp_path / "mappings.json"
        import json

        with open(mappings_path, "w") as f:
            json.dump(mappings_data, f)

        mapper = AssetMapper(sample_portal_assets)

        # Act
        mapper.load_mappings(mappings_path)

        # Assert
        assert "asset_with_mapping" in mapper.mappings
        assert "asset_without_mapping" not in mapper.mappings


class TestAssetMapperBasicMapping:
    """Test cases for basic asset mapping."""

    def test_map_asset_direct_mapping(
        self, sample_portal_assets, sample_bf1942_mappings, sample_map_context
    ):
        """Test mapping asset with direct match."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Act
        result = mapper.map_asset("treeline_pine_w", sample_map_context)

        # Assert
        assert result is not None
        assert result.type == "Tree_Pine_Large"

    def test_map_asset_with_level_restrictions_available(
        self, sample_portal_assets, sample_bf1942_mappings, sample_map_context
    ):
        """Test mapping restricted asset when available on target map."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Act
        result = mapper.map_asset("treeline_oak_w", sample_map_context)

        # Assert
        assert result is not None
        assert result.type == "Tree_Oak_Medium"

    def test_map_asset_unmapped_returns_none(
        self, sample_portal_assets, sample_bf1942_mappings, sample_map_context
    ):
        """Test that unmapped non-terrain assets return None."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Act
        result = mapper.map_asset("completely_unknown_asset", sample_map_context)

        # Assert
        assert result is None


class TestAssetMapperLevelRestrictions:
    """Test cases for level restrictions and fallback handling."""

    def test_map_asset_restricted_finds_alternative(
        self, sample_portal_assets, sample_bf1942_mappings
    ):
        """Test mapping restricted asset on wrong map finds alternative."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        context = MapContext(
            target_base_map="MP_Aftermath", era="WW2", theme="open_terrain", team=Team.NEUTRAL
        )

        # Act
        result = mapper.map_asset("treeline_oak_w", context)

        # Assert
        assert result is not None
        assert result.type == "Tree_Pine_Large"
        assert result.level_restrictions == []

    def test_map_asset_uses_map_specific_fallback(
        self, sample_portal_assets, sample_bf1942_mappings
    ):
        """Test that map-specific fallback is used when available."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        context = MapContext(
            target_base_map="MP_Battery", era="WW2", theme="open_terrain", team=Team.NEUTRAL
        )

        # Act
        result = mapper.map_asset("treeline_oak_w", context)

        # Assert
        assert result is not None
        assert result.type == "Tree_Pine_Large"

    def test_map_asset_nonexistent_portal_asset_finds_alternative(
        self, sample_portal_assets, sample_bf1942_mappings, sample_map_context
    ):
        """Test that mapping to nonexistent Portal asset finds alternative."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Act
        result = mapper.map_asset("building_nonexistent", sample_map_context)

        # Assert
        assert result is not None
        assert result.type == "Building_Barn_01"
        assert result.directory == "Architecture/Rural"


class TestAssetMapperKeywordMatching:
    """Test cases for keyword-based fallback matching."""

    def test_get_type_keywords_matches_tree_category(
        self, sample_portal_assets, sample_fallback_keywords
    ):
        """Test keyword extraction for tree assets."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.fallback_keywords = []

        import json

        with open(sample_fallback_keywords) as f:
            data = json.load(f)
            mapper.fallback_keywords = data.get("type_categories", [])

        # Act
        source_kw, portal_kw = mapper._get_type_keywords("treeline_pine_large")

        # Assert
        assert "tree" in source_kw or "pine" in source_kw
        assert "tree" in portal_kw or "pine" in portal_kw

    def test_get_type_keywords_matches_rock_category(
        self, sample_portal_assets, sample_fallback_keywords
    ):
        """Test keyword extraction for rock assets."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)

        import json

        with open(sample_fallback_keywords) as f:
            data = json.load(f)
            mapper.fallback_keywords = data.get("type_categories", [])

        # Act
        source_kw, portal_kw = mapper._get_type_keywords("rock_boulder_01")

        # Assert
        assert any(kw in ["rock", "stone", "boulder"] for kw in source_kw)
        assert any(kw in ["rock", "stone", "boulder"] for kw in portal_kw)

    def test_get_type_keywords_no_match_returns_empty(self, sample_portal_assets):
        """Test keyword extraction returns empty lists when no match."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.fallback_keywords = []

        # Act
        source_kw, portal_kw = mapper._get_type_keywords("completely_unknown_asset_type")

        # Assert
        assert source_kw == []
        assert portal_kw == []


class TestAssetMapperAlternatives:
    """Test cases for finding alternative assets."""

    def test_find_alternative_in_same_category(self, sample_portal_assets, sample_bf1942_mappings):
        """Test finding alternative asset in same category."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Act
        alternative = mapper._find_alternative("treeline_oak_w", "vegetation", "MP_Battery")

        # Assert
        assert alternative is not None
        assert alternative.type == "Tree_Pine_Large"

    def test_find_alternative_none_available(self, sample_portal_assets, sample_bf1942_mappings):
        """Test finding alternative returns None when none available."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Act
        alternative = mapper._find_alternative("barn_m1", "building", "MP_Aftermath")

        # Assert
        assert alternative is None


class TestAssetMapperTerrainElements:
    """Test cases for terrain element detection."""

    def test_is_terrain_element_detects_water(self, sample_portal_assets):
        """Test that water bodies are detected as terrain elements."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)

        # Act
        result_lake = mapper._is_terrain_element("lake_01")
        result_river = mapper._is_terrain_element("river_wide")
        result_ocean = mapper._is_terrain_element("ocean_surface")

        # Assert
        assert result_lake is True
        assert result_river is True
        assert result_ocean is True

    def test_is_terrain_element_detects_terrain_objects(self, sample_portal_assets):
        """Test that terrain objects are detected."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)

        # Act
        result = mapper._is_terrain_element("terrain_object_01")

        # Assert
        assert result is True

    def test_is_terrain_element_normal_asset(self, sample_portal_assets):
        """Test that normal assets are not detected as terrain elements."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)

        # Act
        result_tree = mapper._is_terrain_element("tree_pine_01")
        result_building = mapper._is_terrain_element("building_barn")

        # Assert
        assert result_tree is False
        assert result_building is False

    def test_map_asset_skips_terrain_elements(
        self, sample_portal_assets, sample_bf1942_mappings, sample_map_context
    ):
        """Test that terrain elements are skipped during mapping."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Act
        result = mapper.map_asset("lake_kursk_01", sample_map_context)

        # Assert
        assert result is None


class TestAssetMapperAvailability:
    """Test cases for asset availability checking."""

    def test_is_asset_available_on_map_unrestricted(self, sample_portal_assets):
        """Test that unrestricted assets are available on all maps."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        tree_asset = mapper.portal_assets["Tree_Pine_Large"]

        # Act
        result_tungsten = mapper._is_asset_available_on_map(tree_asset, "MP_Tungsten")
        result_battery = mapper._is_asset_available_on_map(tree_asset, "MP_Battery")
        result_aftermath = mapper._is_asset_available_on_map(tree_asset, "MP_Aftermath")

        # Assert
        assert result_tungsten is True
        assert result_battery is True
        assert result_aftermath is True

    def test_is_asset_available_on_map_restricted_available(self, sample_portal_assets):
        """Test that restricted asset is available on allowed map."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        oak_asset = mapper.portal_assets["Tree_Oak_Medium"]

        # Act
        result = mapper._is_asset_available_on_map(oak_asset, "MP_Tungsten")

        # Assert
        assert result is True

    def test_is_asset_available_on_map_restricted_unavailable(self, sample_portal_assets):
        """Test that restricted asset is not available on disallowed map."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        oak_asset = mapper.portal_assets["Tree_Oak_Medium"]

        # Act
        result_battery = mapper._is_asset_available_on_map(oak_asset, "MP_Battery")
        result_aftermath = mapper._is_asset_available_on_map(oak_asset, "MP_Aftermath")

        # Assert
        assert result_battery is False
        assert result_aftermath is False


class TestAssetMapperStats:
    """Test cases for mapping statistics."""

    def test_get_stats_returns_counts(self, sample_portal_assets, sample_bf1942_mappings):
        """Test that statistics returns correct counts."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Act
        stats = mapper.get_stats()

        # Assert
        assert "total_mappings" in stats
        assert stats["total_mappings"] > 0
        assert "by_category" in stats
        assert "portal_assets_available" in stats
        assert stats["portal_assets_available"] == 6

    def test_get_stats_by_category(self, sample_portal_assets, sample_bf1942_mappings):
        """Test that statistics breaks down by category."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Act
        stats = mapper.get_stats()
        by_category = stats["by_category"]

        # Assert
        assert "vegetation" in by_category
        assert by_category["vegetation"] >= 2

    def test_get_mapping_info_returns_details(self, sample_portal_assets, sample_bf1942_mappings):
        """Test getting detailed mapping info for an asset."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Act
        info = mapper.get_mapping_info("treeline_pine_w")

        # Assert
        assert info is not None
        assert info["portal_type"] == "Tree_Pine_Large"
        assert info["category"] == "vegetation"
        assert info["confidence"] == 5

    def test_get_mapping_info_returns_none_for_unmapped(
        self, sample_portal_assets, sample_bf1942_mappings
    ):
        """Test getting mapping info returns None for unmapped asset."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Act
        info = mapper.get_mapping_info("nonexistent_asset")

        # Assert
        assert info is None
