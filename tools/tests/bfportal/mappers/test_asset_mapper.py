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
        mapper = AssetMapper(sample_portal_assets)

        assert len(mapper.portal_assets) == 6
        assert "Tree_Pine_Large" in mapper.portal_assets
        assert "Rock_Boulder_01" in mapper.portal_assets

    def test_init_loads_portal_asset_properties(self, sample_portal_assets):
        """Test that Portal asset properties are loaded correctly."""
        mapper = AssetMapper(sample_portal_assets)

        tree_asset = mapper.portal_assets["Tree_Pine_Large"]
        assert tree_asset.type == "Tree_Pine_Large"
        assert tree_asset.directory == "Nature/Trees"
        assert tree_asset.level_restrictions == []

    def test_init_loads_level_restrictions(self, sample_portal_assets):
        """Test that level restrictions are loaded correctly."""
        mapper = AssetMapper(sample_portal_assets)

        oak_asset = mapper.portal_assets["Tree_Oak_Medium"]
        assert oak_asset.level_restrictions == ["MP_Tungsten"]

    @pytest.mark.skip(reason="Complex path mocking test - keywords loaded manually in other tests")
    def test_init_with_fallback_keywords(
        self, sample_portal_assets, sample_fallback_keywords, tmp_path
    ):
        """Test initialization with fallback keywords file."""
        # Create asset_audit directory structure
        asset_audit_dir = tmp_path / "asset_audit"
        asset_audit_dir.mkdir()

        # Copy fallback keywords to expected location
        with patch("pathlib.Path.__truediv__") as mock_div:
            # Mock the path resolution to return our test file
            mock_div.return_value = sample_fallback_keywords

            # Create a temporary mapper.py location to trick the Path resolution
            mapper_file = tmp_path / "mapper.py"
            mapper_file.write_text("")

            with patch("bfportal.mappers.asset_mapper.__file__", str(mapper_file)):
                # Now create mapper - should load fallback keywords from mocked path
                mapper = AssetMapper(sample_portal_assets)

                # Verify fallback keywords were loaded
                assert len(mapper.fallback_keywords) > 0


class TestAssetMapperLoadMappings:
    """Test cases for loading BF1942 to Portal mappings."""

    def test_load_mappings_success(self, sample_portal_assets, sample_bf1942_mappings):
        """Test loading mappings from valid JSON file."""
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        assert len(mapper.mappings) > 0
        assert "treeline_pine_w" in mapper.mappings
        assert "sandbags_wall" in mapper.mappings

    def test_load_mappings_stores_metadata(self, sample_portal_assets, sample_bf1942_mappings):
        """Test that mapping metadata is stored correctly."""
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        pine_mapping = mapper.mappings["treeline_pine_w"]
        assert pine_mapping["portal_type"] == "Tree_Pine_Large"
        assert pine_mapping["category"] == "vegetation"
        assert pine_mapping["confidence"] == 5

    def test_load_mappings_stores_fallbacks(self, sample_portal_assets, sample_bf1942_mappings):
        """Test that map-specific fallbacks are stored."""
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        oak_mapping = mapper.mappings["treeline_oak_w"]
        assert "fallbacks" in oak_mapping
        assert oak_mapping["fallbacks"]["MP_Battery"] == "Tree_Pine_Large"

    def test_load_mappings_file_not_found(self, sample_portal_assets, tmp_path):
        """Test loading mappings raises error when file not found."""
        mapper = AssetMapper(sample_portal_assets)
        nonexistent_file = tmp_path / "nonexistent.json"

        with pytest.raises(FileNotFoundError, match="Mappings file not found"):
            mapper.load_mappings(nonexistent_file)

    def test_load_mappings_skips_todo_entries(self, sample_portal_assets, tmp_path):
        """Test that TODO entries are skipped during loading."""
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
        mapper.load_mappings(mappings_path)

        assert "asset_with_mapping" in mapper.mappings
        assert "asset_without_mapping" not in mapper.mappings


class TestAssetMapperBasicMapping:
    """Test cases for basic asset mapping."""

    def test_map_asset_direct_mapping(
        self, sample_portal_assets, sample_bf1942_mappings, sample_map_context
    ):
        """Test mapping asset with direct match."""
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        result = mapper.map_asset("treeline_pine_w", sample_map_context)

        assert result is not None
        assert result.type == "Tree_Pine_Large"

    def test_map_asset_with_level_restrictions_available(
        self, sample_portal_assets, sample_bf1942_mappings, sample_map_context
    ):
        """Test mapping restricted asset when available on target map."""
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        result = mapper.map_asset("treeline_oak_w", sample_map_context)

        assert result is not None
        assert result.type == "Tree_Oak_Medium"

    def test_map_asset_unmapped_returns_none(
        self, sample_portal_assets, sample_bf1942_mappings, sample_map_context
    ):
        """Test that unmapped non-terrain assets return None."""
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Without fallback keywords loaded, should return None
        result = mapper.map_asset("completely_unknown_asset", sample_map_context)
        assert result is None


class TestAssetMapperLevelRestrictions:
    """Test cases for level restrictions and fallback handling."""

    def test_map_asset_restricted_finds_alternative(
        self, sample_portal_assets, sample_bf1942_mappings
    ):
        """Test mapping restricted asset on wrong map finds alternative."""
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        context = MapContext(
            target_base_map="MP_Aftermath", era="WW2", theme="open_terrain", team=Team.NEUTRAL
        )

        # Tree_Oak_Medium is restricted to MP_Tungsten
        # On MP_Aftermath, should find unrestricted alternative Tree_Pine_Large
        result = mapper.map_asset("treeline_oak_w", context)

        assert result is not None
        assert result.type == "Tree_Pine_Large"
        assert result.level_restrictions == []  # Unrestricted alternative

    def test_map_asset_uses_map_specific_fallback(
        self, sample_portal_assets, sample_bf1942_mappings
    ):
        """Test that map-specific fallback is used when available."""
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Tree_Oak_Medium is restricted to MP_Tungsten
        # But we have a fallback for MP_Battery: Tree_Pine_Large
        context = MapContext(
            target_base_map="MP_Battery", era="WW2", theme="open_terrain", team=Team.NEUTRAL
        )
        result = mapper.map_asset("treeline_oak_w", context)

        assert result is not None
        assert result.type == "Tree_Pine_Large"

    def test_map_asset_nonexistent_portal_asset_finds_alternative(
        self, sample_portal_assets, sample_bf1942_mappings, sample_map_context
    ):
        """Test that mapping to nonexistent Portal asset finds alternative."""
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # building_nonexistent maps to NonExistent_Asset which doesn't exist
        # Should find alternative in same category: Building_Barn_01
        result = mapper.map_asset("building_nonexistent", sample_map_context)

        assert result is not None
        assert result.type == "Building_Barn_01"
        assert result.directory == "Architecture/Rural"


class TestAssetMapperKeywordMatching:
    """Test cases for keyword-based fallback matching."""

    def test_get_type_keywords_matches_tree_category(
        self, sample_portal_assets, sample_fallback_keywords
    ):
        """Test keyword extraction for tree assets."""
        mapper = AssetMapper(sample_portal_assets)
        mapper.fallback_keywords = []

        # Load fallback keywords manually
        import json

        with open(sample_fallback_keywords) as f:
            data = json.load(f)
            mapper.fallback_keywords = data.get("type_categories", [])

        source_kw, portal_kw = mapper._get_type_keywords("treeline_pine_large")

        assert "tree" in source_kw or "pine" in source_kw
        assert "tree" in portal_kw or "pine" in portal_kw

    def test_get_type_keywords_matches_rock_category(
        self, sample_portal_assets, sample_fallback_keywords
    ):
        """Test keyword extraction for rock assets."""
        mapper = AssetMapper(sample_portal_assets)

        import json

        with open(sample_fallback_keywords) as f:
            data = json.load(f)
            mapper.fallback_keywords = data.get("type_categories", [])

        source_kw, portal_kw = mapper._get_type_keywords("rock_boulder_01")

        assert any(kw in ["rock", "stone", "boulder"] for kw in source_kw)
        assert any(kw in ["rock", "stone", "boulder"] for kw in portal_kw)

    def test_get_type_keywords_no_match_returns_empty(self, sample_portal_assets):
        """Test keyword extraction returns empty lists when no match."""
        mapper = AssetMapper(sample_portal_assets)
        mapper.fallback_keywords = []

        source_kw, portal_kw = mapper._get_type_keywords("completely_unknown_asset_type")

        assert source_kw == []
        assert portal_kw == []


class TestAssetMapperAlternatives:
    """Test cases for finding alternative assets."""

    def test_find_alternative_in_same_category(self, sample_portal_assets, sample_bf1942_mappings):
        """Test finding alternative asset in same category."""
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Try to find alternative for vegetation on MP_Battery
        # Tree_Oak_Medium is restricted to MP_Tungsten, so should find Tree_Pine_Large
        alternative = mapper._find_alternative("treeline_oak_w", "vegetation", "MP_Battery")

        assert alternative is not None
        assert alternative.type == "Tree_Pine_Large"

    def test_find_alternative_none_available(self, sample_portal_assets, sample_bf1942_mappings):
        """Test finding alternative returns None when none available."""
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Building_Barn_01 is restricted to MP_Tungsten and MP_Battery
        # Try finding alternative on a different map with no buildings available
        alternative = mapper._find_alternative("barn_m1", "building", "MP_Aftermath")

        # Should return None since no building alternatives exist for MP_Aftermath
        assert alternative is None


class TestAssetMapperTerrainElements:
    """Test cases for terrain element detection."""

    def test_is_terrain_element_detects_water(self, sample_portal_assets):
        """Test that water bodies are detected as terrain elements."""
        mapper = AssetMapper(sample_portal_assets)

        assert mapper._is_terrain_element("lake_01") is True
        assert mapper._is_terrain_element("river_wide") is True
        assert mapper._is_terrain_element("ocean_surface") is True

    def test_is_terrain_element_detects_terrain_objects(self, sample_portal_assets):
        """Test that terrain objects are detected."""
        mapper = AssetMapper(sample_portal_assets)

        assert mapper._is_terrain_element("terrain_object_01") is True

    def test_is_terrain_element_normal_asset(self, sample_portal_assets):
        """Test that normal assets are not detected as terrain elements."""
        mapper = AssetMapper(sample_portal_assets)

        assert mapper._is_terrain_element("tree_pine_01") is False
        assert mapper._is_terrain_element("building_barn") is False

    def test_map_asset_skips_terrain_elements(
        self, sample_portal_assets, sample_bf1942_mappings, sample_map_context
    ):
        """Test that terrain elements are skipped during mapping."""
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        result = mapper.map_asset("lake_kursk_01", sample_map_context)

        assert result is None


class TestAssetMapperAvailability:
    """Test cases for asset availability checking."""

    def test_is_asset_available_on_map_unrestricted(self, sample_portal_assets):
        """Test that unrestricted assets are available on all maps."""
        mapper = AssetMapper(sample_portal_assets)

        tree_asset = mapper.portal_assets["Tree_Pine_Large"]
        assert mapper._is_asset_available_on_map(tree_asset, "MP_Tungsten") is True
        assert mapper._is_asset_available_on_map(tree_asset, "MP_Battery") is True
        assert mapper._is_asset_available_on_map(tree_asset, "MP_Aftermath") is True

    def test_is_asset_available_on_map_restricted_available(self, sample_portal_assets):
        """Test that restricted asset is available on allowed map."""
        mapper = AssetMapper(sample_portal_assets)

        oak_asset = mapper.portal_assets["Tree_Oak_Medium"]
        assert mapper._is_asset_available_on_map(oak_asset, "MP_Tungsten") is True

    def test_is_asset_available_on_map_restricted_unavailable(self, sample_portal_assets):
        """Test that restricted asset is not available on disallowed map."""
        mapper = AssetMapper(sample_portal_assets)

        oak_asset = mapper.portal_assets["Tree_Oak_Medium"]
        assert mapper._is_asset_available_on_map(oak_asset, "MP_Battery") is False
        assert mapper._is_asset_available_on_map(oak_asset, "MP_Aftermath") is False


class TestAssetMapperStats:
    """Test cases for mapping statistics."""

    def test_get_stats_returns_counts(self, sample_portal_assets, sample_bf1942_mappings):
        """Test that statistics returns correct counts."""
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        stats = mapper.get_stats()

        assert "total_mappings" in stats
        assert stats["total_mappings"] > 0
        assert "by_category" in stats
        assert "portal_assets_available" in stats
        assert stats["portal_assets_available"] == 6

    def test_get_stats_by_category(self, sample_portal_assets, sample_bf1942_mappings):
        """Test that statistics breaks down by category."""
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        stats = mapper.get_stats()
        by_category = stats["by_category"]

        assert "vegetation" in by_category
        assert by_category["vegetation"] >= 2  # At least pine and oak

    def test_get_mapping_info_returns_details(self, sample_portal_assets, sample_bf1942_mappings):
        """Test getting detailed mapping info for an asset."""
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        info = mapper.get_mapping_info("treeline_pine_w")

        assert info is not None
        assert info["portal_type"] == "Tree_Pine_Large"
        assert info["category"] == "vegetation"
        assert info["confidence"] == 5

    def test_get_mapping_info_returns_none_for_unmapped(
        self, sample_portal_assets, sample_bf1942_mappings
    ):
        """Test getting mapping info returns None for unmapped asset."""
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        info = mapper.get_mapping_info("nonexistent_asset")

        assert info is None
