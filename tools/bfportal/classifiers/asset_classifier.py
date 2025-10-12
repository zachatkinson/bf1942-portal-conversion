"""Asset classification system for distinguishing real assets from metadata.

This module follows SOLID principles:
- Single Responsibility: Each classifier handles one type of asset
- Open/Closed: Add new classifiers without modifying existing code
- Liskov Substitution: All classifiers implement the same interface
- Interface Segregation: Minimal interface for classifiers
- Dependency Inversion: Depend on classifier protocol, not concrete types
"""

from dataclasses import dataclass
from typing import Protocol

# ============================================================================
# Domain Models
# ============================================================================


@dataclass(frozen=True)
class AssetClassification:
    """Result of asset classification."""

    asset_name: str
    is_real_asset: bool
    category: str
    reason: str


# ============================================================================
# Classifier Protocol
# ============================================================================


class AssetClassifier(Protocol):
    """Protocol for asset classification strategies."""

    def classify(self, asset_name: str) -> AssetClassification | None:
        """Classify an asset, return None if this classifier doesn't handle it."""
        ...


# ============================================================================
# Concrete Classifiers (Strategy Pattern)
# ============================================================================


class SpawnPointClassifier:
    """Classifies spawn point instances (not real assets)."""

    SPAWN_KEYWORDS = [
        "SpawnPoint",
        "_spawn_",
        "Spawn_1",
        "Spawn_2",
        "Spawn_3",
        "Spawn_4",
        "Spawn_5",
        "Spawn_6",
        "Spawn_7",
    ]

    def classify(self, asset_name: str) -> AssetClassification | None:
        """Classify spawn point instances."""
        if any(kw in asset_name for kw in self.SPAWN_KEYWORDS):
            return AssetClassification(
                asset_name=asset_name,
                is_real_asset=False,
                category="spawn_point_instance",
                reason="Named spawn point location (not a physical asset)",
            )
        return None


class ControlPointClassifier:
    """Classifies control point instances (not real assets)."""

    CP_KEYWORDS = ["_Cpoint", "CONTROLPOINT_", "_BASE_", "BASE_Cpoint"]

    def classify(self, asset_name: str) -> AssetClassification | None:
        """Classify control point instances."""
        if any(kw in asset_name for kw in self.CP_KEYWORDS):
            return AssetClassification(
                asset_name=asset_name,
                is_real_asset=False,
                category="control_point_instance",
                reason="Named control point location (gameplay object)",
            )
        return None


class VehicleSpawnerClassifier:
    """Classifies vehicle spawners (real assets we need to map)."""

    SPAWNER_TYPES = [
        "Spawner",  # Generic spawner suffix
        "spawner",  # Lowercase variant
    ]

    # Exclude spawn point instances
    EXCLUDE_PATTERNS = ["SpawnPoint", "_spawn_"]

    def classify(self, asset_name: str) -> AssetClassification | None:
        """Classify vehicle spawners."""
        # Must have spawner suffix
        if not any(asset_name.endswith(s) for s in self.SPAWNER_TYPES):
            return None

        # Must not be a spawn point instance
        if any(ex in asset_name for ex in self.EXCLUDE_PATTERNS):
            return None

        return AssetClassification(
            asset_name=asset_name,
            is_real_asset=True,
            category="spawner",
            reason="Vehicle or object spawner (needs Portal mapping)",
        )


class VisualAssetClassifier:
    """Classifies visual assets (buildings, vegetation, props)."""

    VISUAL_PATTERNS = {
        "vegetation": ["tree", "bush", "plant", "grass", "vegetation", "palm", "pine", "oak"],
        "building": ["house", "building", "bunker", "tower", "barn", "church", "hangar"],
        "prop": ["rock", "stone", "barrel", "crate", "fence", "wall", "gate"],
        "vehicle": ["tank", "plane", "ship", "boat", "car", "truck", "jeep", "apc"],
    }

    def classify(self, asset_name: str) -> AssetClassification | None:
        """Classify visual assets."""
        asset_lower = asset_name.lower()

        for category, keywords in self.VISUAL_PATTERNS.items():
            if any(kw in asset_lower for kw in keywords):
                return AssetClassification(
                    asset_name=asset_name,
                    is_real_asset=True,
                    category=category,
                    reason=f"Visual asset ({category})",
                )

        return None


class WeaponClassifier:
    """Classifies weapon templates (real assets)."""

    WEAPON_PATTERNS = [
        "Rifle",
        "Gun",
        "Bazooka",
        "Panzerschreck",
        "Grenade",
        "Mine",
        "Knife",
        "Pistol",
        "MG",
        "LMG",
    ]

    def classify(self, asset_name: str) -> AssetClassification | None:
        """Classify weapon templates."""
        if any(w in asset_name for w in self.WEAPON_PATTERNS):
            return AssetClassification(
                asset_name=asset_name,
                is_real_asset=True,
                category="weapon",
                reason="Weapon template (real asset)",
            )
        return None


class AmmoCrateClassifier:
    """Classifies ammo/supply crates (real assets)."""

    AMMO_PATTERNS = ["Ammo", "AmmoBox", "SupplyCrate"]

    def classify(self, asset_name: str) -> AssetClassification | None:
        """Classify ammo crates."""
        if any(a in asset_name for a in self.AMMO_PATTERNS):
            return AssetClassification(
                asset_name=asset_name,
                is_real_asset=True,
                category="ammo_crate",
                reason="Ammo/supply crate (real asset)",
            )
        return None


# ============================================================================
# Composite Classifier (Chain of Responsibility Pattern)
# ============================================================================


class CompositeAssetClassifier:
    """Coordinates multiple classifiers using chain of responsibility.

    Single Responsibility: Orchestrate classification pipeline.
    Open/Closed: Add new classifiers without modifying this class.
    """

    def __init__(self) -> None:
        """Initialize with default classifier chain."""
        # Order matters: more specific classifiers first
        self.classifiers: list[AssetClassifier] = [
            SpawnPointClassifier(),
            ControlPointClassifier(),
            VehicleSpawnerClassifier(),
            WeaponClassifier(),
            AmmoCrateClassifier(),
            VisualAssetClassifier(),
        ]

    def add_classifier(self, classifier: AssetClassifier) -> None:
        """Add a new classifier to the chain."""
        self.classifiers.append(classifier)

    def classify(self, asset_name: str) -> AssetClassification:
        """Classify an asset using the classifier chain.

        Returns:
            Classification result (defaults to 'unknown' if no classifier matched)
        """
        for classifier in self.classifiers:
            result = classifier.classify(asset_name)
            if result is not None:
                return result

        # Default: unknown asset (potentially real, needs manual review)
        return AssetClassification(
            asset_name=asset_name,
            is_real_asset=True,  # Err on the side of including it
            category="unknown",
            reason="Unknown asset type (needs manual review)",
        )

    def classify_many(self, asset_names: list[str]) -> dict[str, AssetClassification]:
        """Classify multiple assets.

        Returns:
            Dict mapping asset names to their classifications
        """
        return {name: self.classify(name) for name in asset_names}

    def filter_real_assets(self, asset_names: list[str]) -> list[str]:
        """Filter list to only real assets (exclude spawn points, etc.)."""
        classifications = self.classify_many(asset_names)
        return [
            name for name, classification in classifications.items() if classification.is_real_asset
        ]

    def get_statistics(self, asset_names: list[str]) -> dict[str, int]:
        """Get classification statistics for a list of assets."""
        classifications = self.classify_many(asset_names)

        stats: dict[str, int] = {}
        real_count = 0
        metadata_count = 0

        for classification in classifications.values():
            category = classification.category
            stats[category] = stats.get(category, 0) + 1

            if classification.is_real_asset:
                real_count += 1
            else:
                metadata_count += 1

        stats["_total_real_assets"] = real_count
        stats["_total_metadata"] = metadata_count
        stats["_total"] = len(asset_names)

        return stats
