"""Asset classification system for distinguishing real assets from metadata."""

from .asset_classifier import (
    AmmoCrateClassifier,
    AssetClassification,
    AssetClassifier,
    CompositeAssetClassifier,
    ControlPointClassifier,
    SpawnPointClassifier,
    VehicleSpawnerClassifier,
    VisualAssetClassifier,
    WeaponClassifier,
)

__all__ = [
    "AssetClassification",
    "AssetClassifier",
    "CompositeAssetClassifier",
    "SpawnPointClassifier",
    "ControlPointClassifier",
    "VehicleSpawnerClassifier",
    "VisualAssetClassifier",
    "WeaponClassifier",
    "AmmoCrateClassifier",
]
