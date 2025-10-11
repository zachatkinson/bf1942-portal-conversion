#!/usr/bin/env python3
"""Kursk .tscn Generator.

Generates a complete Kursk.tscn file from extracted BF1942 data and mapping database.

This is the main conversion tool that:
1. Loads extracted Kursk data (kursk_extracted_data.json)
2. Loads object mapping database (object_mapping_database.json)
3. Converts BF1942 objects to BF6 Portal equivalents
4. Generates complete .tscn scene file

Usage:
    python tools/generate_kursk_tscn.py

Output:
    GodotProject/levels/Kursk.tscn - Complete map scene file
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

# Import coordinate transformation utilities
from coordinate_transform import (
    convert_bf1942_to_godot,
    convert_control_point,
    convert_spawn_point,
    format_identity_transform
)


@dataclass
class ExtResource:
    """External resource reference in .tscn file."""
    id: int
    resource_type: str
    path: str

    def format(self) -> str:
        """Format as .tscn ExtResource line."""
        return f'[ext_resource type="{self.resource_type}" path="{self.path}" id="{self.id}"]'


class TscnGenerator:
    """Generates .tscn scene files from BF1942 data."""

    def __init__(self, kursk_data_path: str, mapping_db_path: str):
        """Initialize generator.

        Args:
            kursk_data_path: Path to kursk_extracted_data.json
            mapping_db_path: Path to object_mapping_database.json
        """
        self.kursk_data_path = Path(kursk_data_path)
        self.mapping_db_path = Path(mapping_db_path)

        self.kursk_data: Dict = {}
        self.mapping_db: Dict = {}
        self.ext_resources: List[ExtResource] = []
        self.next_ext_resource_id = 1
        self.next_obj_id = 1

    def load_data(self) -> None:
        """Load kursk data and mapping database.

        Raises:
            FileNotFoundError: If data files don't exist
        """
        if not self.kursk_data_path.exists():
            raise FileNotFoundError(f"Kursk data not found: {self.kursk_data_path}")

        if not self.mapping_db_path.exists():
            raise FileNotFoundError(f"Mapping database not found: {self.mapping_db_path}")

        with open(self.kursk_data_path, 'r') as f:
            self.kursk_data = json.load(f)

        with open(self.mapping_db_path, 'r') as f:
            self.mapping_db = json.load(f)

        print(f"✅ Loaded Kursk data: {len(self.kursk_data['control_points'])} control points, "
              f"{len(self.kursk_data['vehicle_spawners'])} vehicle spawners")
        print(f"✅ Loaded mapping database: {len(self.mapping_db['vehicle_spawners'])} vehicle mappings")

    def add_ext_resource(self, resource_type: str, path: str) -> int:
        """Add external resource and return its ID.

        Args:
            resource_type: Resource type (e.g., "PackedScene")
            path: Resource path (e.g., "res://objects/HQ_PlayerSpawner.tscn")

        Returns:
            Resource ID
        """
        # Check if already added
        for res in self.ext_resources:
            if res.path == path and res.resource_type == resource_type:
                return res.id

        # Add new resource
        resource_id = self.next_ext_resource_id
        self.ext_resources.append(ExtResource(resource_id, resource_type, path))
        self.next_ext_resource_id += 1
        return resource_id

    def get_next_obj_id(self) -> int:
        """Get next unique ObjId.

        Returns:
            Next available ObjId
        """
        obj_id = self.next_obj_id
        self.next_obj_id += 1
        return obj_id

    def generate_header(self) -> str:
        """Generate .tscn file header.

        Returns:
            Header section as string
        """
        lines = [
            f'[gd_scene load_steps={len(self.ext_resources) + 1} format=3]',
            ''
        ]

        # Add external resources
        for res in self.ext_resources:
            lines.append(res.format())

        lines.append('')
        return '\n'.join(lines)

    def generate_root_node(self) -> str:
        """Generate root node.

        Returns:
            Root node section as string
        """
        return '[node name="Kursk" type="Node3D"]'

    def generate_team_hq(self, team: int, base_position: Tuple[float, float, float]) -> str:
        """Generate team HQ with spawn points.

        Args:
            team: Team number (1 or 2)
            base_position: HQ center position (x, y, z)

        Returns:
            HQ node section with spawn points
        """
        # Add HQ resource
        hq_res_id = self.add_ext_resource("PackedScene", "res://objects/HQ_PlayerSpawner.tscn")
        spawn_res_id = self.add_ext_resource("PackedScene", "res://objects/SpawnPoint.tscn")

        obj_id = self.get_next_obj_id()

        # Generate spawn point paths
        spawn_paths = []
        for i in range(8):  # 8 spawn points per team
            spawn_paths.append(f'NodePath("SpawnPoint_{team}_{i+1}")')

        spawn_paths_str = ', '.join(spawn_paths)

        # HQ transform (identity rotation)
        hq_transform = format_identity_transform(base_position)

        lines = [
            f'[node name="TEAM_{team}_HQ" parent="." node_paths=PackedStringArray("HQArea", "InfantrySpawns") instance=ExtResource("{hq_res_id}")]',
            f'transform = {hq_transform}',
            f'Team = {team}',
            'AltTeam = 0',
            f'ObjId = {obj_id}',
            f'HQArea = NodePath("HQ_Team{team}")',
            f'InfantrySpawns = [{spawn_paths_str}]',
            ''
        ]

        # Generate spawn points in a circle around HQ
        radius = 10.0  # 10 meters radius
        for i in range(8):
            angle = (360.0 / 8) * i  # Evenly spaced around circle

            # Calculate relative position
            import math
            rel_x = radius * math.cos(math.radians(angle))
            rel_z = radius * math.sin(math.radians(angle))
            rel_pos = (rel_x, 0, rel_z)

            # Face outward from center
            facing_angle = angle

            spawn_transform = convert_spawn_point(rel_pos, facing_angle)

            lines.extend([
                f'[node name="SpawnPoint_{team}_{i+1}" parent="TEAM_{team}_HQ" instance=ExtResource("{spawn_res_id}")]',
                f'transform = {spawn_transform}',
                ''
            ])

        return '\n'.join(lines)

    def generate_capture_points(self) -> str:
        """Generate all capture points.

        Returns:
            Capture point nodes as string
        """
        cp_res_id = self.add_ext_resource("PackedScene", "res://objects/CapturePoint.tscn")

        lines = []

        for idx, cp_data in enumerate(self.kursk_data['control_points'], 1):
            obj_id = 100 + idx  # Control points start at 100

            pos = cp_data['position']
            position = (pos['x'], pos['y'], pos['z'])
            transform = convert_control_point(position)

            # Determine team (0 = neutral, 1 = axis, 2 = allies)
            team = cp_data.get('team') or 0

            lines.extend([
                f'[node name="CapturePoint_{idx}" parent="." instance=ExtResource("{cp_res_id}")]',
                f'transform = {transform}',
                f'Team = {team}',
                f'ObjId = {obj_id}',
                ''
            ])

        return '\n'.join(lines)

    def generate_vehicle_spawners(self) -> str:
        """Generate all vehicle spawners.

        Returns:
            Vehicle spawner nodes as string
        """
        vehicle_res_id = self.add_ext_resource("PackedScene", "res://objects/VehicleSpawner.tscn")

        lines = []

        for idx, spawner_data in enumerate(self.kursk_data['vehicle_spawners'], 1):
            bf1942_type = spawner_data['bf1942_type']

            # Look up mapping
            mapping = self.mapping_db['vehicle_spawners'].get(bf1942_type)
            if not mapping:
                print(f"⚠️  WARNING: No mapping found for {bf1942_type}, skipping")
                continue

            # Determine BF6 vehicle template based on team
            team = spawner_data.get('team')

            if 'bf6_vehicle_template_axis' in mapping and 'bf6_vehicle_template_allies' in mapping:
                # Team-specific vehicle (tanks)
                if team == 1:
                    vehicle_template = mapping['bf6_vehicle_template_axis']
                elif team == 2:
                    vehicle_template = mapping['bf6_vehicle_template_allies']
                else:
                    vehicle_template = mapping['bf6_vehicle_template_axis']  # Default to axis
            else:
                # Generic vehicle
                vehicle_template = mapping['bf6_vehicle_template']

            # Convert position and rotation
            pos = spawner_data['position']
            position = (pos['x'], pos['y'], pos['z'])

            if spawner_data.get('rotation'):
                rot = spawner_data['rotation']
                rotation = (rot['pitch'], rot['yaw'], rot['roll'])
                transform = convert_bf1942_to_godot(position, rotation)
            else:
                transform = format_identity_transform(position)

            obj_id = 1000 + idx  # Vehicle spawners start at 1000

            lines.extend([
                f'[node name="VehicleSpawner_{idx}" parent="." instance=ExtResource("{vehicle_res_id}")]',
                f'transform = {transform}',
                f'Team = {team if team is not None else 0}',
                f'ObjId = {obj_id}',
                f'VehicleTemplate = "{vehicle_template}"',
                ''
            ])

        return '\n'.join(lines)

    def generate_combat_area(self) -> str:
        """Generate combat area boundary.

        Returns:
            Combat area node as string
        """
        combat_area_res_id = self.add_ext_resource("PackedScene", "res://objects/CombatArea.tscn")

        # Calculate map bounds from Kursk data
        all_positions = []

        # Add control points
        for cp in self.kursk_data['control_points']:
            pos = cp['position']
            all_positions.append((pos['x'], pos['z']))

        # Add vehicle spawners
        for spawner in self.kursk_data['vehicle_spawners']:
            pos = spawner['position']
            all_positions.append((pos['x'], pos['z']))

        # Calculate bounds
        x_coords = [p[0] for p in all_positions]
        z_coords = [p[1] for p in all_positions]

        min_x = min(x_coords)
        max_x = max(x_coords)
        min_z = min(z_coords)
        max_z = max(z_coords)

        # Add 50m buffer
        buffer = 50.0
        min_x -= buffer
        max_x += buffer
        min_z -= buffer
        max_z += buffer

        # Center point
        center_x = (min_x + max_x) / 2
        center_y = 80.0  # Approximate average Y from data
        center_z = (min_z + max_z) / 2

        center_transform = format_identity_transform((center_x, center_y, center_z))

        # Create rectangular boundary
        # Points are relative to center
        half_width = (max_x - min_x) / 2
        half_depth = (max_z - min_z) / 2

        points = [
            (-half_width, -half_depth),
            (half_width, -half_depth),
            (half_width, half_depth),
            (-half_width, half_depth)
        ]

        points_str = ', '.join(f'{p[0]}, {p[1]}' for p in points)

        lines = [
            f'[node name="CombatArea" parent="." node_paths=PackedStringArray("CombatVolume") instance=ExtResource("{combat_area_res_id}")]',
            f'transform = {center_transform}',
            'CombatVolume = NodePath("CollisionPolygon3D")',
            '',
            '[node name="CollisionPolygon3D" type="Area3D" parent="CombatArea"]',
            'height = 200.0',
            f'points = PackedVector2Array({points_str})',
            ''
        ]

        return '\n'.join(lines)

    def generate_static_layer(self) -> str:
        """Generate static terrain layer.

        Returns:
            Static layer node as string
        """
        # Use MP_Outskirts terrain as recommended in Phase 2
        terrain_res_id = self.add_ext_resource("PackedScene", "res://static/MP_Outskirts_Terrain.tscn")
        assets_res_id = self.add_ext_resource("PackedScene", "res://static/MP_Outskirts_Assets.tscn")

        lines = [
            '[node name="Static" type="Node3D" parent="."]',
            '',
            f'[node name="MP_Outskirts_Terrain" parent="Static" instance=ExtResource("{terrain_res_id}")]',
            '',
            f'[node name="MP_Outskirts_Assets" parent="Static" instance=ExtResource("{assets_res_id}")]',
            ''
        ]

        return '\n'.join(lines)

    def generate_tscn(self, output_path: str) -> None:
        """Generate complete .tscn file.

        Args:
            output_path: Output file path
        """
        print("\n🔧 Generating Kursk.tscn...")

        # Pre-calculate map center for HQs
        axis_base = None
        allies_base = None

        for cp in self.kursk_data['control_points']:
            if 'Axis' in cp['name']:
                pos = cp['position']
                axis_base = (pos['x'], pos['y'], pos['z'])
            elif 'Allies' in cp['name']:
                pos = cp['position']
                allies_base = (pos['x'], pos['y'], pos['z'])

        if not axis_base or not allies_base:
            print("⚠️  WARNING: Could not find Axis/Allies base positions, using defaults")
            axis_base = (437.315, 77.8547, 238.39)
            allies_base = (568.058, 76.6406, 849.956)

        # Generate all sections
        sections = []

        # 1. Root node
        sections.append(self.generate_root_node())
        sections.append('')

        # 2. Team HQs
        print("  → Generating Team 1 HQ (Axis)...")
        sections.append(self.generate_team_hq(1, axis_base))

        print("  → Generating Team 2 HQ (Allies)...")
        sections.append(self.generate_team_hq(2, allies_base))

        # 3. Capture Points
        print(f"  → Generating {len(self.kursk_data['control_points'])} capture points...")
        sections.append(self.generate_capture_points())

        # 4. Vehicle Spawners
        print(f"  → Generating {len(self.kursk_data['vehicle_spawners'])} vehicle spawners...")
        sections.append(self.generate_vehicle_spawners())

        # 5. Combat Area
        print("  → Generating combat area boundary...")
        sections.append(self.generate_combat_area())

        # 6. Static Layer
        print("  → Generating static terrain layer...")
        sections.append(self.generate_static_layer())

        # Combine all sections with header
        full_content = self.generate_header() + '\n'.join(sections)

        # Write to file
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_content)

        print(f"\n✅ Generated {output_path}")
        print(f"   File size: {output_path.stat().st_size} bytes")
        print(f"   External resources: {len(self.ext_resources)}")


def main():
    """Main entry point."""
    # Paths
    project_root = Path(__file__).parent.parent
    kursk_data_path = project_root / 'tools' / 'kursk_extracted_data.json'

    # Allow custom mapping database via command line argument
    # This enables future multi-era support (WW2, Vietnam, etc.)
    if len(sys.argv) > 1 and sys.argv[1] == '--mapping':
        mapping_db_path = Path(sys.argv[2])
        print(f"Using custom mapping database: {mapping_db_path}")
    else:
        mapping_db_path = project_root / 'tools' / 'object_mapping_database.json'

    # Allow custom output path
    if '--output' in sys.argv:
        output_idx = sys.argv.index('--output')
        output_path = Path(sys.argv[output_idx + 1])
        print(f"Using custom output path: {output_path}")
    else:
        output_path = project_root / 'GodotProject' / 'levels' / 'Kursk.tscn'

    print("=" * 70)
    print("Kursk .tscn Generator")
    print("=" * 70)

    # Validate input files
    if not kursk_data_path.exists():
        print(f"❌ ERROR: Kursk data not found: {kursk_data_path}")
        print("   Run: python tools/parse_kursk_data.py")
        sys.exit(1)

    if not mapping_db_path.exists():
        print(f"❌ ERROR: Mapping database not found: {mapping_db_path}")
        sys.exit(1)

    # Generate
    generator = TscnGenerator(str(kursk_data_path), str(mapping_db_path))

    try:
        generator.load_data()
        generator.generate_tscn(str(output_path))

        print("\n" + "=" * 70)
        print("✅ Kursk.tscn generation complete!")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Open GodotProject in Godot 4")
        print("  2. Load levels/Kursk.tscn")
        print("  3. Verify object placements")
        print("  4. Manual refinements as needed")
        print("  5. Export via BFPortal panel")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
