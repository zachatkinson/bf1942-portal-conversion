#!/usr/bin/env python3
"""Integration tests for BFPortal SDK conversion pipeline.

These tests validate end-to-end workflows combining multiple components:
- Asset mapping pipeline (config → mapper → validation)
- Transform pipeline (offset → terrain → bounds)
- Full conversion workflows
"""

import json

import pytest
from bfportal.core.exceptions import MappingError
from bfportal.core.game_config import ConfigLoader
from bfportal.core.interfaces import GameObject, MapContext, Rotation, Team, Transform, Vector3
from bfportal.mappers.asset_mapper import AssetMapper
from bfportal.transforms.coordinate_offset import CoordinateOffset
from bfportal.utils.tscn_utils import TscnTransformParser


class TestAssetMappingPipeline:
    """Integration tests for asset mapping pipeline: config → mapper → output."""

    def test_full_mapping_pipeline_success(
        self, sample_portal_assets, sample_bf1942_mappings, sample_map_context
    ):
        """Test complete asset mapping workflow with valid data.

        Pipeline: Load Portal assets → Load mappings → Map BF1942 asset → Validate
        """
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Act
        result = mapper.map_asset("treeline_pine_w", sample_map_context)

        # Assert
        assert result is not None
        assert result.type == "Tree_Pine_Large"
        assert result.directory == "Nature/Trees"
        assert len(result.level_restrictions) == 0  # Unrestricted

    def test_mapping_pipeline_with_level_restrictions(
        self, sample_portal_assets, sample_bf1942_mappings, tmp_path
    ):
        """Test mapping pipeline handles level restrictions correctly.

        Scenario: Asset restricted to MP_Tungsten, map to fallback when on MP_Battery
        """
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)
        battery_context = MapContext(
            target_base_map="MP_Battery",
            era="WW2",
            theme="urban",
            team=Team.NEUTRAL,
        )

        # Act
        result = mapper.map_asset("treeline_oak_w", battery_context)

        # Assert
        assert result is not None
        assert result.type == "Tree_Pine_Large"  # Fallback defined in conftest.py

    def test_mapping_pipeline_with_missing_asset(
        self, sample_portal_assets, sample_bf1942_mappings, sample_map_context
    ):
        """Test mapping pipeline handles missing Portal assets via fallback.

        Scenario: BF1942 asset maps to non-existent Portal asset, uses fallback
        """
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Act
        result = mapper.map_asset("building_nonexistent", sample_map_context)

        # Assert
        assert result is not None
        assert "Building" in result.type or "building" in result.type.lower()

    def test_mapping_pipeline_with_best_guess_fallback(
        self,
        sample_portal_assets,
        sample_bf1942_mappings,
        sample_fallback_keywords,
        sample_map_context,
    ):
        """Test mapping pipeline uses best-guess fallback for unmapped assets.

        Scenario: BF1942 asset not in mappings, use keyword-based fallback
        """
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)
        with open(sample_fallback_keywords) as f:
            data = json.load(f)
            mapper.fallback_keywords = data.get("type_categories", [])

        # Act
        result = mapper.map_asset("rock_large_01", sample_map_context)

        # Assert
        assert result is not None
        assert "Rock" in result.type or "rock" in result.type.lower()


class TestTransformPipeline:
    """Integration tests for transform pipeline: offset → terrain → validation."""

    def test_offset_calculation_and_application(self):
        """Test offset calculation followed by application to transforms."""
        # Arrange
        offset_calc = CoordinateOffset()
        objects = [
            GameObject(
                name="Obj1",
                asset_type="Tree",
                transform=Transform(Vector3(100, 10, 100), Rotation(0, 0, 0)),
                team=Team.NEUTRAL,
                properties={},
            ),
            GameObject(
                name="Obj2",
                asset_type="Tree",
                transform=Transform(Vector3(200, 10, 200), Rotation(0, 0, 0)),
                team=Team.NEUTRAL,
                properties={},
            ),
            GameObject(
                name="Obj3",
                asset_type="Tree",
                transform=Transform(Vector3(300, 10, 300), Rotation(0, 0, 0)),
                team=Team.NEUTRAL,
                properties={},
            ),
        ]

        # Act - Step 1: Calculate centroid
        centroid = offset_calc.calculate_centroid(objects)

        # Assert - Step 1
        assert centroid.x == pytest.approx(200.0, abs=0.1)
        assert centroid.z == pytest.approx(200.0, abs=0.1)

        # Act - Step 2: Calculate offset to origin
        target = Vector3(0, 0, 0)
        offset = offset_calc.calculate_offset(centroid, target)

        # Assert - Step 2
        assert offset.x == pytest.approx(-200.0, abs=0.1)
        assert offset.z == pytest.approx(-200.0, abs=0.1)

        # Act - Step 3: Apply offset to first object
        new_transform = offset_calc.apply_offset(objects[0].transform, offset)

        # Assert - Step 3
        assert new_transform.position.x == pytest.approx(-100.0, abs=0.1)
        assert new_transform.position.z == pytest.approx(-100.0, abs=0.1)

    def test_scale_transform_preserves_rotation(self):
        """Test scaling preserves rotation and only affects position."""
        # Arrange
        offset_calc = CoordinateOffset()
        original = Transform(
            Vector3(100, 50, 100),
            Rotation(0, 45, 0),  # 45° yaw rotation
        )

        # Act
        scaled = offset_calc.apply_scale(original, 0.5)

        # Assert
        assert scaled.position.x == pytest.approx(50.0, abs=0.1)
        assert scaled.position.y == pytest.approx(50.0, abs=0.1)  # Height unchanged
        assert scaled.position.z == pytest.approx(50.0, abs=0.1)
        assert scaled.rotation.yaw == pytest.approx(45.0, abs=0.1)


class TestConfigLoadingAndUsage:
    """Integration tests for config loading → pipeline usage."""

    def test_game_config_loads_and_used_in_context(self, sample_game_config):
        """Test GameConfig loading followed by MapContext creation."""
        # Arrange
        config = ConfigLoader.load_game_config(sample_game_config)

        # Act - Step 1: Verify config loaded correctly
        config_loaded = (
            config.name == "BF1942" and config.engine == "Refractor 1.0" and config.era == "WW2"
        )

        # Assert - Step 1
        assert config_loaded
        assert config.name == "BF1942"
        assert config.engine == "Refractor 1.0"
        assert config.era == "WW2"

        # Act - Step 2: Use config data to create context
        context = MapContext(
            target_base_map="MP_Tungsten",
            era=config.era,
            theme="open_terrain",
            team=Team.NEUTRAL,
        )

        # Assert - Step 2
        assert context.era == "WW2"

    def test_map_config_to_conversion_workflow(self, sample_map_config):
        """Test loading map config and using it for conversion parameters."""
        # Arrange
        with open(sample_map_config) as f:
            map_data = json.load(f)

        # Act - Step 1: Extract conversion parameters
        recommended_terrain = map_data["recommended_base_terrain"]
        theme = map_data["theme"]
        dimensions = map_data["dimensions"]

        # Assert - Step 1
        assert recommended_terrain == "MP_Tungsten"
        assert theme == "open_terrain"
        assert dimensions["width"] == 2000.0

        # Act - Step 2: Create context from config
        context = MapContext(
            target_base_map=recommended_terrain,
            era="WW2",
            theme=theme,
            team=Team.NEUTRAL,
        )

        # Assert - Step 2
        assert context.target_base_map == "MP_Tungsten"
        assert context.theme == "open_terrain"


class TestFullConversionWorkflow:
    """End-to-end integration tests simulating complete conversion workflows."""

    def test_bf1942_to_portal_mini_workflow(
        self,
        sample_portal_assets,
        sample_bf1942_mappings,
        sample_map_context,
    ):
        """Test minimal BF1942 → Portal conversion workflow.

        Steps:
        1. Load Portal assets
        2. Load BF1942 mappings
        3. Map several BF1942 assets
        4. Calculate centroid and offset
        5. Apply transforms
        6. Format for .tscn output
        """
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)
        bf1942_objects = [
            ("treeline_pine_w", Vector3(100, 5, 100)),
            ("treeline_pine_w", Vector3(200, 5, 200)),
            ("barn_m1", Vector3(150, 10, 150)),
        ]

        # Act - Step 1: Map BF1942 assets to Portal objects
        portal_objects = []
        for bf_type, position in bf1942_objects:
            portal_asset = mapper.map_asset(bf_type, sample_map_context)
            if portal_asset:
                portal_objects.append(
                    GameObject(
                        name=f"{portal_asset.type}_001",
                        asset_type=portal_asset.type,
                        transform=Transform(position, Rotation(0, 0, 0)),
                        team=Team.NEUTRAL,
                        properties={},
                    )
                )

        # Assert - Step 1
        assert len(portal_objects) == 3

        # Act - Step 2: Calculate offset and re-center to origin
        offset_calc = CoordinateOffset()
        centroid = offset_calc.calculate_centroid(portal_objects)
        target_center = Vector3(0, 0, 0)
        offset = offset_calc.calculate_offset(centroid, target_center)
        recentered_objects = []
        for obj in portal_objects:
            new_transform = offset_calc.apply_offset(obj.transform, offset)
            recentered_objects.append(
                GameObject(
                    name=obj.name,
                    asset_type=obj.asset_type,
                    transform=new_transform,
                    team=obj.team,
                    properties=obj.properties,
                )
            )

        # Act - Step 3: Format transforms for .tscn
        parser = TscnTransformParser()
        formatted_transforms = []
        for obj in recentered_objects:
            rotation = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
            position_list: list[float] = [
                obj.transform.position.x,
                obj.transform.position.y,
                obj.transform.position.z,
            ]
            matrix_str = parser.format(rotation, position_list)
            formatted_transforms.append(matrix_str)

        # Assert - Step 3
        for matrix_str in formatted_transforms:
            assert "Transform3D(" in matrix_str
            assert matrix_str.count(",") == 11  # 12 values, 11 commas

    def test_error_propagation_through_pipeline(self, sample_portal_assets, sample_bf1942_mappings):
        """Test that errors propagate correctly through conversion pipeline.

        Scenario: Invalid map context → MappingError
        """
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)
        invalid_context = MapContext(
            target_base_map="MP_NonExistent",
            era="WW2",
            theme="unknown",
            team=Team.NEUTRAL,
        )

        # Act & Assert
        with pytest.raises(MappingError):
            mapper.map_asset("barn_m1", invalid_context)


class TestTscnOutputFormatting:
    """Integration tests for formatting output data for .tscn files."""

    def test_transform_matrix_formatting(self):
        """Test Transform3D matrix formatting for Godot .tscn files."""
        # Arrange
        parser = TscnTransformParser()
        rotation = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 0.0, 1.0]
        position = [100.5, 50.25, 200.75]

        # Act
        result = parser.format(rotation, position)

        # Assert
        assert result.startswith("Transform3D(")
        assert result.endswith(")")
        values_str = result[len("Transform3D(") : -1]
        values = [float(v.strip()) for v in values_str.split(",")]
        assert len(values) == 12
        assert values[9] == pytest.approx(100.5, abs=0.01)
        assert values[10] == pytest.approx(50.25, abs=0.01)
        assert values[11] == pytest.approx(200.75, abs=0.01)

    def test_transform_parse_and_format_roundtrip(self):
        """Test parsing and formatting Transform3D strings preserves data."""
        # Arrange
        parser = TscnTransformParser()
        original = "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 50, 200)"

        # Act - Step 1: Parse original
        rotation, position = parser.parse(original)

        # Act - Step 2: Format back
        reconstructed = parser.format(rotation, position)

        # Act - Step 3: Parse again
        rotation2, position2 = parser.parse(reconstructed)

        # Assert
        assert rotation == rotation2
        assert position == position2


class TestStatisticsAggregation:
    """Integration tests for statistics collection across conversion."""

    def test_mapper_statistics_collection(
        self, sample_portal_assets, sample_bf1942_mappings, sample_map_context
    ):
        """Test that mapper correctly tracks statistics during conversion."""
        # Arrange
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)
        stats = mapper.get_stats()
        initial_mappings = stats["total_mappings"]

        # Act - Step 1: Verify initial stats
        assert initial_mappings > 0

        # Act - Step 2: Perform several mappings
        test_assets = ["treeline_pine_w", "barn_m1", "sandbags_wall"]
        mapped_count = 0
        for asset in test_assets:
            try:
                result = mapper.map_asset(asset, sample_map_context)
                if result:
                    mapped_count += 1
            except MappingError:
                pass  # Expected for some assets

        # Assert - Step 2
        assert mapped_count >= 2

        # Act - Step 3: Get final stats
        final_stats = mapper.get_stats()

        # Assert - Step 3
        assert final_stats["total_mappings"] == initial_mappings
        assert "by_category" in final_stats
        assert "portal_assets_available" in final_stats
