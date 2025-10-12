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
        # Setup
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Execute mapping
        result = mapper.map_asset("treeline_pine_w", sample_map_context)

        # Verify
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
        # Setup mapper
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Create context for restricted map
        battery_context = MapContext(
            target_base_map="MP_Battery",
            era="WW2",
            theme="urban",
            team=Team.NEUTRAL,
        )

        # Execute mapping - should use fallback from mappings
        result = mapper.map_asset("treeline_oak_w", battery_context)

        # Verify - should get fallback from mappings.json
        assert result is not None
        assert result.type == "Tree_Pine_Large"  # Fallback defined in conftest.py

    def test_mapping_pipeline_with_missing_asset(
        self, sample_portal_assets, sample_bf1942_mappings, sample_map_context
    ):
        """Test mapping pipeline handles missing Portal assets via fallback.

        Scenario: BF1942 asset maps to non-existent Portal asset, uses fallback
        """
        # Setup
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Execute - mapped asset doesn't exist in Portal catalog
        # Should use fallback mechanism instead of raising error
        result = mapper.map_asset("building_nonexistent", sample_map_context)

        # Verify fallback was used
        assert result is not None
        # The fallback should be a building asset available on the map
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
        # Setup mapper with keywords
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Load fallback keywords
        with open(sample_fallback_keywords) as f:
            data = json.load(f)
            mapper.fallback_keywords = data.get("type_categories", [])

        # Execute - asset not in mappings, but contains "rock" keyword
        result = mapper.map_asset("rock_large_01", sample_map_context)

        # Verify - should find Rock_Boulder_01 via keyword matching
        assert result is not None
        assert "Rock" in result.type or "rock" in result.type.lower()


class TestTransformPipeline:
    """Integration tests for transform pipeline: offset → terrain → validation."""

    def test_offset_calculation_and_application(self):
        """Test offset calculation followed by application to transforms."""
        # Setup
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

        # Calculate centroid
        centroid = offset_calc.calculate_centroid(objects)
        assert centroid.x == pytest.approx(200.0, abs=0.1)
        assert centroid.z == pytest.approx(200.0, abs=0.1)

        # Calculate offset to origin
        target = Vector3(0, 0, 0)
        offset = offset_calc.calculate_offset(centroid, target)
        assert offset.x == pytest.approx(-200.0, abs=0.1)
        assert offset.z == pytest.approx(-200.0, abs=0.1)

        # Apply offset to first object
        new_transform = offset_calc.apply_offset(objects[0].transform, offset)
        assert new_transform.position.x == pytest.approx(-100.0, abs=0.1)
        assert new_transform.position.z == pytest.approx(-100.0, abs=0.1)

    def test_scale_transform_preserves_rotation(self):
        """Test scaling preserves rotation and only affects position."""
        # Setup
        offset_calc = CoordinateOffset()
        original = Transform(
            Vector3(100, 50, 100),
            Rotation(0, 45, 0),  # 45° yaw rotation
        )

        # Scale by 0.5
        scaled = offset_calc.apply_scale(original, 0.5)

        # Verify position scaled, rotation preserved
        assert scaled.position.x == pytest.approx(50.0, abs=0.1)
        assert scaled.position.y == pytest.approx(50.0, abs=0.1)  # Height unchanged
        assert scaled.position.z == pytest.approx(50.0, abs=0.1)
        assert scaled.rotation.yaw == pytest.approx(45.0, abs=0.1)


class TestConfigLoadingAndUsage:
    """Integration tests for config loading → pipeline usage."""

    def test_game_config_loads_and_used_in_context(self, sample_game_config):
        """Test GameConfig loading followed by MapContext creation."""
        # Load config
        config = ConfigLoader.load_game_config(sample_game_config)

        # Verify config loaded correctly
        assert config.name == "BF1942"
        assert config.engine == "Refractor 1.0"
        assert config.era == "WW2"

        # Use config data to create context
        context = MapContext(
            target_base_map="MP_Tungsten",
            era=config.era,
            theme="open_terrain",
            team=Team.NEUTRAL,
        )

        # Verify context uses config data
        assert context.era == "WW2"

    def test_map_config_to_conversion_workflow(self, sample_map_config):
        """Test loading map config and using it for conversion parameters."""
        # Load map config
        with open(sample_map_config) as f:
            map_data = json.load(f)

        # Extract conversion parameters
        recommended_terrain = map_data["recommended_base_terrain"]
        theme = map_data["theme"]
        dimensions = map_data["dimensions"]

        # Verify data is usable
        assert recommended_terrain == "MP_Tungsten"
        assert theme == "open_terrain"
        assert dimensions["width"] == 2000.0

        # Create context from config
        context = MapContext(
            target_base_map=recommended_terrain,
            era="WW2",
            theme=theme,
            team=Team.NEUTRAL,
        )

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
        # Step 1: Setup mapper
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Step 2: Map BF1942 assets
        bf1942_objects = [
            ("treeline_pine_w", Vector3(100, 5, 100)),
            ("treeline_pine_w", Vector3(200, 5, 200)),
            ("barn_m1", Vector3(150, 10, 150)),
        ]

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

        assert len(portal_objects) == 3

        # Step 3: Calculate offset
        offset_calc = CoordinateOffset()
        centroid = offset_calc.calculate_centroid(portal_objects)

        # Step 4: Re-center to origin
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

        # Step 5: Format transforms for .tscn
        parser = TscnTransformParser()
        for obj in recentered_objects:
            # Create rotation matrix (identity for simplicity)
            rotation = [1, 0, 0, 0, 1, 0, 0, 0, 1]
            position = [
                obj.transform.position.x,
                obj.transform.position.y,
                obj.transform.position.z,
            ]
            matrix_str = parser.format(rotation, position)
            assert "Transform3D(" in matrix_str
            # Verify it's a valid transform string
            assert matrix_str.count(",") == 11  # 12 values, 11 commas

    def test_error_propagation_through_pipeline(self, sample_portal_assets, sample_bf1942_mappings):
        """Test that errors propagate correctly through conversion pipeline.

        Scenario: Invalid map context → MappingError
        """
        # Setup
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Create context for non-existent map (will cause restrictions to fail)
        invalid_context = MapContext(
            target_base_map="MP_NonExistent",
            era="WW2",
            theme="unknown",
            team=Team.NEUTRAL,
        )

        # Map restricted asset on invalid map - should fail
        with pytest.raises(MappingError):
            # This asset is restricted to MP_Tungsten/MP_Battery only
            mapper.map_asset("barn_m1", invalid_context)


class TestTscnOutputFormatting:
    """Integration tests for formatting output data for .tscn files."""

    def test_transform_matrix_formatting(self):
        """Test Transform3D matrix formatting for Godot .tscn files."""
        parser = TscnTransformParser()

        # Create rotation matrix (identity) and position
        rotation = [1, 0, 0, 0, 1, 0, 0, 0, 1]
        position = [100.5, 50.25, 200.75]

        # Format for .tscn
        result = parser.format(rotation, position)

        # Verify format
        assert result.startswith("Transform3D(")
        assert result.endswith(")")
        # Check it has 12 numeric values
        values_str = result[len("Transform3D(") : -1]
        values = [float(v.strip()) for v in values_str.split(",")]
        assert len(values) == 12

        # Verify position values are at end (indices 9, 10, 11)
        assert values[9] == pytest.approx(100.5, abs=0.01)
        assert values[10] == pytest.approx(50.25, abs=0.01)
        assert values[11] == pytest.approx(200.75, abs=0.01)

    def test_transform_parse_and_format_roundtrip(self):
        """Test parsing and formatting Transform3D strings preserves data."""
        parser = TscnTransformParser()

        original = "Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 100, 50, 200)"

        # Parse
        rotation, position = parser.parse(original)

        # Format back
        reconstructed = parser.format(rotation, position)

        # Parse again
        rotation2, position2 = parser.parse(reconstructed)

        # Verify data preserved
        assert rotation == rotation2
        assert position == position2


class TestStatisticsAggregation:
    """Integration tests for statistics collection across conversion."""

    def test_mapper_statistics_collection(
        self, sample_portal_assets, sample_bf1942_mappings, sample_map_context
    ):
        """Test that mapper correctly tracks statistics during conversion."""
        # Setup
        mapper = AssetMapper(sample_portal_assets)
        mapper.load_mappings(sample_bf1942_mappings)

        # Get initial stats
        stats = mapper.get_stats()
        initial_mappings = stats["total_mappings"]
        assert initial_mappings > 0

        # Perform several mappings
        test_assets = ["treeline_pine_w", "barn_m1", "sandbags_wall"]
        mapped_count = 0

        for asset in test_assets:
            try:
                result = mapper.map_asset(asset, sample_map_context)
                if result:
                    mapped_count += 1
            except MappingError:
                pass  # Expected for some assets

        # Verify at least some mapped successfully
        assert mapped_count >= 2

        # Stats should remain consistent
        final_stats = mapper.get_stats()
        assert final_stats["total_mappings"] == initial_mappings
        assert "by_category" in final_stats
        assert "portal_assets_available" in final_stats
