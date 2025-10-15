#!/usr/bin/env python3
"""Scene validator for .tscn files.

Single Responsibility: Validate generated .tscn structure.
"""

from pathlib import Path


class SceneValidator:
    """Validates generated Godot .tscn files for Portal compatibility.

    Checks for required nodes, proper structure, and common issues.
    """

    # Required nodes for Portal maps
    REQUIRED_NODES = [
        "TEAM_1_HQ",
        "TEAM_2_HQ",
        "CombatArea",
        "Static",
    ]

    # Required ExtResources
    REQUIRED_RESOURCES = [
        "HQ_PlayerSpawner.tscn",
        "SpawnPoint.tscn",
        "CombatArea.tscn",
    ]

    def validate(self, tscn_path: Path) -> list[str]:
        """Validate a .tscn file for Portal compatibility.

        Args:
            tscn_path: Path to .tscn file to validate

        Returns:
            List of error messages (empty if valid)

        Note:
            This performs structural validation only. Full validation
            requires opening the scene in Godot.
        """
        errors = []

        # Check file exists
        if not tscn_path.exists():
            errors.append(f"File not found: {tscn_path}")
            return errors

        # Read file content
        try:
            with open(tscn_path) as f:
                content = f.read()
        except Exception as e:
            errors.append(f"Failed to read file: {e}")
            return errors

        # Validate required nodes
        for node_name in self.REQUIRED_NODES:
            if node_name not in content:
                errors.append(f"Missing required node: {node_name}")

        # Validate required resources
        for resource in self.REQUIRED_RESOURCES:
            if resource not in content:
                errors.append(f"Missing required resource: {resource}")

        # Check for HQ spawn points
        if "InfantrySpawns" not in content:
            errors.append("Missing InfantrySpawns property on HQ nodes")

        # Check for spawn point nodes
        if "SpawnPoint_1_" not in content:
            errors.append("Missing Team 1 spawn points (SpawnPoint_1_*)")
        if "SpawnPoint_2_" not in content:
            errors.append("Missing Team 2 spawn points (SpawnPoint_2_*)")

        # Validate spawn point counts (minimum 4 per team)
        team1_spawns = content.count('[node name="SpawnPoint_1_')
        team2_spawns = content.count('[node name="SpawnPoint_2_')

        if team1_spawns < 4:
            errors.append(f"Team 1 has only {team1_spawns} spawn points (minimum 4 required)")
        if team2_spawns < 4:
            errors.append(f"Team 2 has only {team2_spawns} spawn points (minimum 4 required)")

        # Check for combat area polygon
        if "CombatVolume" not in content:
            errors.append("Missing CombatVolume property on CombatArea node")
        if "points = PackedVector2Array" not in content:
            errors.append("Missing combat area polygon definition")

        return errors

    def validate_and_report(self, tscn_path: Path) -> bool:
        """Validate and print a formatted report.

        Args:
            tscn_path: Path to .tscn file

        Returns:
            True if valid, False if errors found
        """
        errors = self.validate(tscn_path)

        if not errors:
            print(f"✅ Validation passed: {tscn_path.name}")
            return True

        print(f"❌ Validation failed: {tscn_path.name}")
        print(f"   Found {len(errors)} error(s):")
        for error in errors:
            print(f"   • {error}")
        return False

    def get_scene_stats(self, tscn_path: Path) -> dict:
        """Get statistics about a .tscn file.

        Args:
            tscn_path: Path to .tscn file

        Returns:
            Dict with node counts and metadata

        Note:
            Useful for debugging and verification.
        """
        if not tscn_path.exists():
            return {"error": "File not found"}

        try:
            with open(tscn_path) as f:
                content = f.read()

            return {
                "file_size": tscn_path.stat().st_size,
                "total_nodes": content.count('[node name="'),
                "ext_resources": content.count("[ext_resource"),
                "team1_spawns": content.count('[node name="SpawnPoint_1_'),
                "team2_spawns": content.count('[node name="SpawnPoint_2_'),
                "capture_points": content.count('[node name="CapturePoint_'),
                "vehicle_spawners": content.count('[node name="VehicleSpawner_'),
                "static_objects": content.count('parent="Static"'),
            }
        except Exception as e:
            return {"error": str(e)}
