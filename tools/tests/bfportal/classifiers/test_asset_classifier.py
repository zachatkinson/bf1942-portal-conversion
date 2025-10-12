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

    def test_creates_classification_with_all_fields(self):
        """Test creating AssetClassification with all fields."""
        # Arrange & Act
        classification = AssetClassification(
            asset_name="TestAsset",
            is_real_asset=True,
            category="building",
            reason="Test reason",
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

        # Act
        result = classifier.classify("German_SpawnPoint_1")

        # Assert
        assert result is not None
        assert result.is_real_asset is False
        assert result.category == "spawn_point_instance"
        assert "spawn point location" in result.reason

    def test_classifies_spawn_with_underscore_pattern(self):
        """Test classifying asset with _spawn_ pattern."""
        # Arrange
        classifier = SpawnPointClassifier()

        # Act
        result = classifier.classify("axis_spawn_north")

        # Assert
        assert result is not None
        assert result.is_real_asset is False
        assert result.category == "spawn_point_instance"

    def test_classifies_numbered_spawn(self):
        """Test classifying numbered spawn point."""
        # Arrange
        classifier = SpawnPointClassifier()

        # Act
        result = classifier.classify("Spawn_1")

        # Assert
        assert result is not None
        assert result.is_real_asset is False

    def test_returns_none_for_non_spawn_asset(self):
        """Test returns None for non-spawn point asset."""
        # Arrange
        classifier = SpawnPointClassifier()

        # Act
        result = classifier.classify("Bunker_German_01")

        # Assert
        assert result is None


class TestControlPointClassifier:
    """Tests for ControlPointClassifier."""

    def test_classifies_control_point_with_cpoint(self):
        """Test classifying control point with _Cpoint keyword."""
        # Arrange
        classifier = ControlPointClassifier()

        # Act
        result = classifier.classify("North_Cpoint")

        # Assert
        assert result is not None
        assert result.is_real_asset is False
        assert result.category == "control_point_instance"

    def test_classifies_controlpoint_uppercase(self):
        """Test classifying CONTROLPOINT_ pattern."""
        # Arrange
        classifier = ControlPointClassifier()

        # Act
        result = classifier.classify("CONTROLPOINT_Alpha")

        # Assert
        assert result is not None
        assert result.is_real_asset is False

    def test_classifies_base_pattern(self):
        """Test classifying _BASE_ pattern."""
        # Arrange
        classifier = ControlPointClassifier()

        # Act
        result = classifier.classify("Axis_BASE_HQ")

        # Assert
        assert result is not None
        assert result.is_real_asset is False

    def test_returns_none_for_non_cp_asset(self):
        """Test returns None for non-control point asset."""
        # Arrange
        classifier = ControlPointClassifier()

        # Act
        result = classifier.classify("Tank_Tiger")

        # Assert
        assert result is None


class TestVehicleSpawnerClassifier:
    """Tests for VehicleSpawnerClassifier."""

    def test_classifies_vehicle_spawner(self):
        """Test classifying vehicle spawner with Spawner suffix."""
        # Arrange
        classifier = VehicleSpawnerClassifier()

        # Act
        result = classifier.classify("TankSpawner")

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "spawner"
        assert "Vehicle or object spawner" in result.reason

    def test_classifies_lowercase_spawner(self):
        """Test classifying spawner with lowercase suffix."""
        # Arrange
        classifier = VehicleSpawnerClassifier()

        # Act
        result = classifier.classify("jeep_spawner")

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "spawner"

    def test_excludes_spawn_point_instances(self):
        """Test excludes assets with SpawnPoint keyword."""
        # Arrange
        classifier = VehicleSpawnerClassifier()

        # Act
        result = classifier.classify("SpawnPoint_Spawner")

        # Assert
        assert result is None

    def test_returns_none_without_spawner_suffix(self):
        """Test returns None for asset without Spawner suffix."""
        # Arrange
        classifier = VehicleSpawnerClassifier()

        # Act
        result = classifier.classify("TankInstance")

        # Assert
        assert result is None


class TestVisualAssetClassifier:
    """Tests for VisualAssetClassifier."""

    def test_classifies_vegetation_asset(self):
        """Test classifying vegetation asset."""
        # Arrange
        classifier = VisualAssetClassifier()

        # Act
        result = classifier.classify("Tree_Pine_Large")

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "vegetation"

    def test_classifies_building_asset(self):
        """Test classifying building asset."""
        # Arrange
        classifier = VisualAssetClassifier()

        # Act
        result = classifier.classify("Bunker_German_01")

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "building"

    def test_classifies_prop_asset(self):
        """Test classifying prop asset."""
        # Arrange
        classifier = VisualAssetClassifier()

        # Act
        result = classifier.classify("Rock_Boulder_Large")

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "prop"

    def test_classifies_vehicle_asset(self):
        """Test classifying vehicle asset."""
        # Arrange
        classifier = VisualAssetClassifier()

        # Act
        result = classifier.classify("Tank_Tiger")

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "vehicle"

    def test_case_insensitive_matching(self):
        """Test classification is case insensitive."""
        # Arrange
        classifier = VisualAssetClassifier()

        # Act
        result = classifier.classify("TREE_OAK")

        # Assert
        assert result is not None
        assert result.category == "vegetation"

    def test_returns_none_for_unmatched_asset(self):
        """Test returns None for asset without visual patterns."""
        # Arrange
        classifier = VisualAssetClassifier()

        # Act
        result = classifier.classify("UnknownObject_123")

        # Assert
        assert result is None


class TestWeaponClassifier:
    """Tests for WeaponClassifier."""

    def test_classifies_rifle(self):
        """Test classifying rifle weapon."""
        # Arrange
        classifier = WeaponClassifier()

        # Act
        result = classifier.classify("Kar98_Rifle")

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "weapon"

    def test_classifies_machine_gun(self):
        """Test classifying MG weapon."""
        # Arrange
        classifier = WeaponClassifier()

        # Act
        result = classifier.classify("MG42")

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "weapon"

    def test_classifies_grenade(self):
        """Test classifying grenade."""
        # Arrange
        classifier = WeaponClassifier()

        # Act
        result = classifier.classify("Grenade_German")

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "weapon"

    def test_returns_none_for_non_weapon(self):
        """Test returns None for non-weapon asset."""
        # Arrange
        classifier = WeaponClassifier()

        # Act
        result = classifier.classify("SomethingElse")

        # Assert
        assert result is None


class TestAmmoCrateClassifier:
    """Tests for AmmoCrateClassifier."""

    def test_classifies_ammo_crate(self):
        """Test classifying ammo crate."""
        # Arrange
        classifier = AmmoCrateClassifier()

        # Act
        result = classifier.classify("AmmoBox_German")

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "ammo_crate"

    def test_classifies_supply_crate(self):
        """Test classifying supply crate."""
        # Arrange
        classifier = AmmoCrateClassifier()

        # Act
        result = classifier.classify("SupplyCrate")

        # Assert
        assert result is not None
        assert result.is_real_asset is True
        assert result.category == "ammo_crate"

    def test_returns_none_for_non_ammo_asset(self):
        """Test returns None for non-ammo asset."""
        # Arrange
        classifier = AmmoCrateClassifier()

        # Act
        result = classifier.classify("RandomObject")

        # Assert
        assert result is None


class TestCompositeAssetClassifier:
    """Tests for CompositeAssetClassifier."""

    def test_initializes_with_default_classifiers(self):
        """Test composite classifier initializes with default chain."""
        # Arrange & Act
        classifier = CompositeAssetClassifier()

        # Assert
        assert len(classifier.classifiers) == 6

    def test_add_classifier_extends_chain(self):
        """Test adding custom classifier to chain."""
        # Arrange
        classifier = CompositeAssetClassifier()
        initial_count = len(classifier.classifiers)

        # Act
        classifier.add_classifier(WeaponClassifier())

        # Assert
        assert len(classifier.classifiers) == initial_count + 1

    def test_classify_uses_first_matching_classifier(self):
        """Test classification stops at first match."""
        # Arrange
        classifier = CompositeAssetClassifier()

        # Act
        result = classifier.classify("German_SpawnPoint_1")

        # Assert
        assert result.category == "spawn_point_instance"
        assert result.is_real_asset is False

    def test_classify_returns_unknown_for_unmatched_asset(self):
        """Test unknown classification for unmatched asset."""
        # Arrange
        classifier = CompositeAssetClassifier()

        # Act
        result = classifier.classify("CompletelyUnknownAsset_XYZ")

        # Assert
        assert result.category == "unknown"
        assert result.is_real_asset is True  # Err on side of inclusion
        assert "manual review" in result.reason

    def test_classify_many_returns_dict(self):
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

    def test_get_statistics_counts_categories(self):
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

        # Act
        stats = classifier.get_statistics([])

        # Assert
        assert stats["_total"] == 0
        assert stats["_total_real_assets"] == 0
        assert stats["_total_metadata"] == 0
