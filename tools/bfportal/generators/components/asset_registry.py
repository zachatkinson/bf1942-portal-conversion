#!/usr/bin/env python3
"""Asset registry for managing Godot ExtResource references.

Single Responsibility: ExtResource ID assignment and lookup.
"""


class AssetRegistry:
    """Manages ExtResource registration and ID assignment for .tscn generation.

    This class maintains a registry of all assets used in a scene,
    assigns unique ExtResource IDs, and provides lookup functionality.

    DRY Principle: Centralizes all ExtResource management logic.
    """

    def __init__(self, starting_id: int = 1):
        """Initialize registry.

        Args:
            starting_id: First ExtResource ID to use (default 1)
        """
        self.ext_resources: list[dict] = []
        self.next_id = starting_id
        self.asset_to_id: dict[str, str] = {}  # asset_type -> ext_resource_id

    def register_gameplay_assets(self, base_terrain: str) -> None:
        """Register standard Portal gameplay assets.

        Args:
            base_terrain: Base terrain name (e.g., "MP_Tungsten")

        Note:
            These are the core Portal SDK assets needed for every map.
        """
        gameplay_assets = [
            {
                "id": str(self.next_id),
                "type": "PackedScene",
                "path": "res://objects/Gameplay/Common/HQ_PlayerSpawner.tscn",
            },
            {
                "id": str(self.next_id + 1),
                "type": "PackedScene",
                "path": "res://objects/entities/SpawnPoint.tscn",
            },
            {
                "id": str(self.next_id + 2),
                "type": "PackedScene",
                "path": "res://objects/Gameplay/Conquest/CapturePoint.tscn",
            },
            {
                "id": str(self.next_id + 3),
                "type": "PackedScene",
                "path": "res://objects/Gameplay/Common/VehicleSpawner.tscn",
            },
            {
                "id": str(self.next_id + 4),
                "type": "PackedScene",
                "path": "res://objects/Gameplay/Common/CombatArea.tscn",
            },
            {
                "id": str(self.next_id + 5),
                "type": "PackedScene",
                "path": f"res://static/{base_terrain}_Terrain.tscn",
            },
        ]

        self.ext_resources.extend(gameplay_assets)
        self.next_id += len(gameplay_assets)

    def register_asset(self, asset_type: str, scene_path: str) -> str:
        """Register an asset and get its ExtResource ID.

        Args:
            asset_type: Asset type name (e.g., "Birch_01_L")
            scene_path: Path to .tscn file (e.g., "res://objects/.../Birch_01_L.tscn")

        Returns:
            ExtResource ID for this asset

        Note:
            If asset is already registered, returns existing ID (DRY).
        """
        # Check if already registered
        if asset_type in self.asset_to_id:
            return self.asset_to_id[asset_type]

        # Register new asset
        ext_id = str(self.next_id)
        self.ext_resources.append(
            {
                "id": ext_id,
                "type": "PackedScene",
                "path": scene_path,
            }
        )
        self.asset_to_id[asset_type] = ext_id
        self.next_id += 1

        return ext_id

    def get_id(self, asset_type: str) -> str | None:
        """Get ExtResource ID for a registered asset.

        Args:
            asset_type: Asset type name

        Returns:
            ExtResource ID if registered, None otherwise
        """
        return self.asset_to_id.get(asset_type)

    def has_asset(self, asset_type: str) -> bool:
        """Check if an asset is registered.

        Args:
            asset_type: Asset type name

        Returns:
            True if asset is registered
        """
        return asset_type in self.asset_to_id

    def get_all_resources(self) -> list[dict]:
        """Get all registered ExtResources.

        Returns:
            List of ExtResource dicts with id, type, and path
        """
        return self.ext_resources.copy()

    def format_ext_resource_lines(self) -> list[str]:
        """Format all ExtResources as .tscn lines.

        Returns:
            List of formatted ExtResource lines for .tscn file
        """
        lines = []
        for resource in self.ext_resources:
            lines.append(
                f'[ext_resource type="{resource["type"]}" '
                f'path="{resource["path"]}" id="{resource["id"]}"]'
            )
        return lines

    def get_stats(self) -> dict:
        """Get registry statistics.

        Returns:
            Dict with resource counts and metadata
        """
        return {
            "total_resources": len(self.ext_resources),
            "gameplay_resources": 6,  # Fixed count of gameplay assets
            "static_resources": len(self.ext_resources) - 6,
            "next_available_id": self.next_id,
        }
