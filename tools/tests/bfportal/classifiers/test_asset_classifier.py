#!/usr/bin/env python3
"""Tests for asset_classifier.py."""

import sys
from pathlib import Path

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from bfportal.classifiers.asset_classifier import (
    AmmoCrateClassifier,
    AssetClassification,
    CompositeAssetClassifier,
    ControlPointClassifier,
    SpawnPointClassifier,
    VehicleSpawnerClassifier,
    VisualAssetClassifier,
    WeaponClassifier,
)


class TestAssetClassification:
    """Tests for AssetClassification value object."""

    def test_asset_classification_with_all_fields_creates_valid_object(self):
        """Test creating AssetClassification with all fields."""
        # Arrange
        asset_name = "TestAsset"
        is_real = True
        category = "building"
        reason = "Test reason"

        # Act
        classification = AssetClassification(
            asset_name=asset_name,
            is_real_asset=is_real,
            category=category,
            reason=reason,
        )

        # Assert
        assert classification.asset_name == "TestAsset"
        assert classification.is_real_asset is True
        assert classification.category == "building"
        assert classification.reason == "Test reason"


class TestSpawnPointClassifier:
    """Tests for SpawnPointClassifier."""

    def test_classifies_spawn_point_with_keyword(self):
        """Test classifying asset with SpawnPoint keyword."""
        # Arrange
        classifier = SpawnPointClassifier()
        asset_name = "German_SpawnPoint_1"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is not None
        assert result.is_real_asset is False
        assert result.category == "spawn_point_instance"
        assert "spawn point location" in result.reason

    def test_classifies_spawn_with_underscore_pattern(self):
        """Test classifying asset with _spawn_ pattern."""
        # Arrange
        classifier = SpawnPointClassifier()
        asset_name = "axis_spawn_north"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is not None
        assert result.is_real_asset is False
        assert result.category == "spawn_point_instance"

    def test_classifies_numbered_spawn(self):
        """Test classifying numbered spawn point."""
        # Arrange
        classifier = SpawnPointClassifier()
        asset_name = "Spawn_1"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is not None
        assert result.is_real_asset is False

    def test_returns_none_for_non_spawn_asset(self):
        """Test returns None for non-spawn point asset."""
        # Arrange
        classifier = SpawnPointClassifier()
        asset_name = "Bunker_German_01"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is None


class TestControlPointClassifier:
    """Tests for ControlPointClassifier."""

    def test_classifies_control_point_with_cpoint(self):
        """Test classifying control point with _Cpoint keyword."""
        # Arrange
        classifier = ControlPointClassifier()
        asset_name = "North_Cpoint"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is not None
        assert result.is_real_asset is False
        assert result.category == "control_point_instance"

    def test_classifies_controlpoint_uppercase(self):
        """Test classifying CONTROLPOINT_ pattern."""
        # Arrange
        classifier = ControlPointClassifier()
        asset_name = "CONTROLPOINT_Alpha"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is not None
        assert result.is_real_asset is False

    def test_classifies_base_pattern(self):
        """Test classifying _BASE_ pattern."""
        # Arrange
        classifier = ControlPointClassifier()
        asset_name = "Axis_BASE_HQ"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is not None
        assert result.is_real_asset is False

    def test_returns_none_for_non_cp_asset(self):
        """Test returns None for non-control point asset."""
        # Arrange
        classifier = ControlPointClassifier()
        asset_name = "Tank_Tiger"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is None


class TestVehicleSpawnerClassifier:
    """Tests for VehicleSpawnerClassifier."""

    def test_classifies_vehicle_spawner(self):
        """Test classifying vehicle spawner with Spawner suffix."""
        # Arrange
        classifier = VehicleSpawnerClassifier()
        asset_name = "TankSpawner"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "spawner"
        assert "Vehicle or object spawner" in result.reason

    def test_classifies_lowercase_spawner(self):
        """Test classifying spawner with lowercase suffix."""
        # Arrange
        classifier = VehicleSpawnerClassifier()
        asset_name = "jeep_spawner"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "spawner"

    def test_excludes_spawn_point_instances(self):
        """Test excludes assets with SpawnPoint keyword."""
        # Arrange
        classifier = VehicleSpawnerClassifier()
        asset_name = "SpawnPoint_Spawner"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is None

    def test_returns_none_without_spawner_suffix(self):
        """Test returns None for asset without Spawner suffix."""
        # Arrange
        classifier = VehicleSpawnerClassifier()
        asset_name = "TankInstance"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is None


class TestVisualAssetClassifier:
    """Tests for VisualAssetClassifier."""

    def test_classifies_vegetation_asset(self):
        """Test classifying vegetation asset."""
        # Arrange
        classifier = VisualAssetClassifier()
        asset_name = "Tree_Pine_Large"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "vegetation"

    def test_classifies_building_asset(self):
        """Test classifying building asset."""
        # Arrange
        classifier = VisualAssetClassifier()
        asset_name = "Bunker_German_01"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "building"

    def test_classifies_prop_asset(self):
        """Test classifying prop asset."""
        # Arrange
        classifier = VisualAssetClassifier()
        asset_name = "Rock_Boulder_Large"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "prop"

    def test_classifies_vehicle_asset(self):
        """Test classifying vehicle asset."""
        # Arrange
        classifier = VisualAssetClassifier()
        asset_name = "Tank_Tiger"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "vehicle"

    def test_case_insensitive_matching(self):
        """Test classification is case insensitive."""
        # Arrange
        classifier = VisualAssetClassifier()
        asset_name = "TREE_OAK"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is not None
        assert result.category == "vegetation"

    def test_returns_none_for_unmatched_asset(self):
        """Test returns None for asset without visual patterns."""
        # Arrange
        classifier = VisualAssetClassifier()
        asset_name = "UnknownObject_123"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is None


class TestWeaponClassifier:
    """Tests for WeaponClassifier."""

    def test_classifies_rifle(self):
        """Test classifying rifle weapon."""
        # Arrange
        classifier = WeaponClassifier()
        asset_name = "Kar98_Rifle"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "weapon"

    def test_classifies_machine_gun(self):
        """Test classifying MG weapon."""
        # Arrange
        classifier = WeaponClassifier()
        asset_name = "MG42"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "weapon"

    def test_classifies_grenade(self):
        """Test classifying grenade."""
        # Arrange
        classifier = WeaponClassifier()
        asset_name = "Grenade_German"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "weapon"

    def test_returns_none_for_non_weapon(self):
        """Test returns None for non-weapon asset."""
        # Arrange
        classifier = WeaponClassifier()
        asset_name = "SomethingElse"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is None


class TestAmmoCrateClassifier:
    """Tests for AmmoCrateClassifier."""

    def test_classifies_ammo_crate(self):
        """Test classifying ammo crate."""
        # Arrange
        classifier = AmmoCrateClassifier()
        asset_name = "AmmoBox_German"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "ammo_crate"

    def test_classifies_supply_crate(self):
        """Test classifying supply crate."""
        # Arrange
        classifier = AmmoCrateClassifier()
        asset_name = "SupplyCrate"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "ammo_crate"

    def test_returns_none_for_non_ammo_asset(self):
        """Test returns None for non-ammo asset."""
        # Arrange
        classifier = AmmoCrateClassifier()
        asset_name = "RandomObject"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result is None


class TestCompositeAssetClassifier:
    """Tests for CompositeAssetClassifier."""

    def test_composite_initialization_with_no_args_creates_six_classifiers(self):
        """Test composite classifier initializes with default chain."""
        # Arrange
        # No setup needed

        # Act
        classifier = CompositeAssetClassifier()

        # Assert
        assert len(classifier.classifiers) == 6

    def test_composite_add_classifier_with_new_classifier_extends_chain(self):
        """Test adding custom classifier to chain."""
        # Arrange
        classifier = CompositeAssetClassifier()
        initial_count = len(classifier.classifiers)
        new_classifier = WeaponClassifier()

        # Act
        classifier.add_classifier(new_classifier)

        # Assert
        assert len(classifier.classifiers) == initial_count + 1

    def test_classify_uses_first_matching_classifier(self):
        """Test classification stops at first match."""
        # Arrange
        classifier = CompositeAssetClassifier()
        asset_name = "German_SpawnPoint_1"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result.category == "spawn_point_instance"
        assert result.is_real_asset is False

    def test_classify_returns_unknown_for_unmatched_asset(self):
        """Test unknown classification for unmatched asset."""
        # Arrange
        classifier = CompositeAssetClassifier()
        asset_name = "CompletelyUnknownAsset_XYZ"

        # Act
        result = classifier.classify(asset_name)

        # Assert
        assert result.category == "unknown"
        assert result.is_real_asset is True  # Err on side of inclusion
        assert "manual review" in result.reason

    def test_composite_classify_many_with_assets_returns_dict(self):
        """Test classifying multiple assets returns dict."""
        # Arrange
        classifier = CompositeAssetClassifier()
        assets = ["SpawnPoint_1", "Tank_Tiger", "Tree_Pine"]

        # Act
        result = classifier.classify_many(assets)

        # Assert
        assert len(result) == 3
        assert "SpawnPoint_1" in result
        assert result["SpawnPoint_1"].is_real_asset is False
        assert result["Tank_Tiger"].is_real_asset is True
        assert result["Tree_Pine"].is_real_asset is True

    def test_filter_real_assets_excludes_metadata(self):
        """Test filtering to only real assets."""
        # Arrange
        classifier = CompositeAssetClassifier()
        assets = [
            "SpawnPoint_1",
            "North_Cpoint",
            "Tank_Tiger",
            "Tree_Pine",
            "AmmoBox",
        ]

        # Act
        result = classifier.filter_real_assets(assets)

        # Assert
        assert len(result) == 3
        assert "Tank_Tiger" in result
        assert "Tree_Pine" in result
        assert "AmmoBox" in result
        assert "SpawnPoint_1" not in result
        assert "North_Cpoint" not in result

    def test_composite_get_statistics_with_assets_returns_category_counts(self):
        """Test getting classification statistics."""
        # Arrange
        classifier = CompositeAssetClassifier()
        assets = [
            "SpawnPoint_1",
            "SpawnPoint_2",
            "Tank_Tiger",
            "Tree_Pine",
            "Tree_Oak",
        ]

        # Act
        stats = classifier.get_statistics(assets)

        # Assert
        assert stats["_total"] == 5
        assert stats["_total_real_assets"] == 3
        assert stats["_total_metadata"] == 2
        assert stats["spawn_point_instance"] == 2
        assert stats["vehicle"] == 1
        assert stats["vegetation"] == 2

    def test_get_statistics_handles_empty_list(self):
        """Test statistics for empty asset list."""
        # Arrange
        classifier = CompositeAssetClassifier()
        assets: list[str] = []

        # Act
        stats = classifier.get_statistics(assets)

        # Assert
        assert stats["_total"] == 0
        assert stats["_total_real_assets"] == 0
        assert stats["_total_metadata"] == 0
