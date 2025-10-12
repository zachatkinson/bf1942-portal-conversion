#!/usr/bin/env python3
"""
Export a Godot .tscn map to complete Battlefield 6 Portal experience format.

This tool:
1. Exports the .tscn file to .spatial.json (via gdconverter)
2. Creates a complete experience.json file with the spatial data embedded
3. Ready to import directly into the Portal web builder

Usage:
    python3 tools/export_to_portal.py <map_name> [options]

Examples:
    python3 tools/export_to_portal.py Kursk
    python3 tools/export_to_portal.py Kursk --base-map MP_Tungsten --max-players 64
"""

import argparse
import base64
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional


def export_tscn_to_spatial(
    tscn_path: Path,
    asset_dir: Path,
    output_dir: Path
) -> Path:
    """
    Export a .tscn file to .spatial.json using gdconverter.

    Args:
        tscn_path: Path to the .tscn file
        asset_dir: Path to FbExportData directory
        output_dir: Path to output directory for .spatial.json

    Returns:
        Path to the generated .spatial.json file

    Raises:
        RuntimeError: If export fails
    """
    export_script = Path("code/gdconverter/src/gdconverter/export_tscn.py")

    if not export_script.exists():
        raise RuntimeError(f"Export script not found: {export_script}")

    print(f"Exporting {tscn_path.name} to .spatial.json...")

    result = subprocess.run(
        [sys.executable, str(export_script), str(tscn_path), str(asset_dir), str(output_dir)],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(f"Export failed: {result.stderr}")

    # The spatial.json will have the same name as the .tscn
    spatial_path = output_dir / f"{tscn_path.stem}.spatial.json"

    if not spatial_path.exists():
        raise RuntimeError(f"Expected output file not created: {spatial_path}")

    print(f"✅ Created {spatial_path}")
    return spatial_path


def create_experience_file(
    map_name: str,
    spatial_path: Path,
    base_map: str,
    max_players_per_team: int,
    game_mode: str,
    description: Optional[str] = None
) -> Path:
    """
    Create a complete Portal experience file with embedded spatial data.

    Args:
        map_name: Name of the map (e.g., "Kursk")
        spatial_path: Path to the .spatial.json file
        base_map: Base map ID (e.g., "MP_Tungsten")
        max_players_per_team: Maximum players per team (16, 32, 64, etc.)
        game_mode: Game mode (Conquest, Rush, TeamDeathmatch, etc.)
        description: Optional custom description

    Returns:
        Path to the generated experience file
    """
    # Read the spatial.json file
    with open(spatial_path, 'r', encoding='utf-8') as f:
        spatial_data = f.read()

    # Base64 encode the spatial data
    spatial_base64 = base64.b64encode(spatial_data.encode('utf-8')).decode('utf-8')

    # Create default description if none provided
    if description is None:
        description = (
            f"A custom recreation of {map_name} from Battlefield 1942. "
            f"Features authentic spawn points, vehicle spawners, and gameplay objects."
        )

    # Create the complete experience structure following the official pattern
    experience = {
        "mutators": {
            "MaxPlayerCount_PerTeam": max_players_per_team,
            "AiMaxCount_PerTeam": 0,
            "AiSpawnType": 2,
            "CQ_iModeTime": 60 if game_mode == "Conquest" else 30,
            "AimAssistSnapCapsuleRadiusMultiplier": 1,
            "FriendlyFireDamageReflectionMaxTeamKills": 2,
            "SpawnBalancing_GamemodeStartTimer": 0,
            "SpawnBalancing_GamemodePlayerCountRatio": 0.75
        },
        "assetRestrictions": {},
        "name": f"{map_name} - BF1942 Classic",
        "description": description,
        "mapRotation": [
            {
                # IMPORTANT: Must follow pattern MP_<MapName>-ModBuilderCustom0
                "id": f"{base_map}-ModBuilderCustom0",
                "spatialAttachment": {
                    "id": f"{map_name.lower()}-bf1942-spatial",
                    "filename": f"{map_name}.spatial.json",
                    "metadata": "mapIdx=0",
                    "version": "1",
                    "isProcessable": True,
                    "processingStatus": 2,
                    "attachmentData": {
                        "original": spatial_base64
                    },
                    "attachmentType": "application/json",
                    "errors": []
                }
            }
        ],
        "workspace": {},
        "teamComposition": [
            [1, {"humanCapacity": max_players_per_team, "aiCapacity": 0, "aiType": 0}],
            [2, {"humanCapacity": max_players_per_team, "aiCapacity": 0, "aiType": 0}]
        ],
        "gameMode": game_mode,
        "attachments": []
    }

    # Write the experience file
    output_file = Path(f"{map_name}_Experience.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(experience, f, indent=2)

    print(f"✅ Created {output_file}")
    print(f"   Base map: {base_map}")
    print(f"   Game mode: {game_mode}")
    print(f"   Max players: {max_players_per_team * 2}")
    print(f"   Spatial data: {len(spatial_data):,} bytes")
    print(f"   Experience file: {output_file.stat().st_size:,} bytes")

    return output_file


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Export Godot map to complete Portal experience format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Export Kursk with default settings:
    %(prog)s Kursk

  Export with custom base map and player count:
    %(prog)s Kursk --base-map MP_Outskirts --max-players 32

  Export with custom description:
    %(prog)s Kursk --description "Epic tank battle on the Eastern Front"

Available base maps (choose terrain similar to your map):
  - MP_Tungsten (Tajikistan - mountains/valleys)
  - MP_Outskirts (Cairo - desert/urban)
  - MP_Battery (Gibraltar - rocky terrain)
  - MP_Capstone (Tajikistan - mountains)
  - MP_Abbasid (Cairo - urban)
  - MP_Aftermath (Brooklyn - urban ruins)
  - MP_Dumbo (Brooklyn - urban)
  - MP_FireStorm (Turkmenistan - desert)
  - MP_Limestone (Gibraltar - coastal)
        """
    )

    parser.add_argument(
        "map_name",
        help="Name of the map to export (e.g., Kursk, El_Alamein)"
    )

    parser.add_argument(
        "--base-map",
        default="MP_Tungsten",
        help="Base map to use for terrain (default: MP_Tungsten)"
    )

    parser.add_argument(
        "--max-players",
        type=int,
        default=32,
        choices=[16, 32, 64],
        help="Maximum players per team (default: 32, total 64 players)"
    )

    parser.add_argument(
        "--game-mode",
        default="Conquest",
        choices=["Conquest", "Rush", "TeamDeathmatch", "Breakthrough"],
        help="Game mode (default: Conquest)"
    )

    parser.add_argument(
        "--description",
        help="Custom description for the experience"
    )

    parser.add_argument(
        "--tscn-path",
        type=Path,
        help="Custom path to .tscn file (default: GodotProject/levels/<map_name>.tscn)"
    )

    args = parser.parse_args()

    # Determine paths
    project_root = Path.cwd()

    if args.tscn_path:
        tscn_path = args.tscn_path
    else:
        tscn_path = project_root / "GodotProject" / "levels" / f"{args.map_name}.tscn"

    if not tscn_path.exists():
        print(f"❌ Error: Map file not found: {tscn_path}", file=sys.stderr)
        print(f"\nAvailable maps:", file=sys.stderr)
        levels_dir = project_root / "GodotProject" / "levels"
        if levels_dir.exists():
            for tscn in sorted(levels_dir.glob("*.tscn")):
                print(f"  - {tscn.stem}", file=sys.stderr)
        return 1

    asset_dir = project_root / "FbExportData"
    output_dir = project_root / "FbExportData" / "levels"

    if not asset_dir.exists():
        print(f"❌ Error: FbExportData directory not found: {asset_dir}", file=sys.stderr)
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        # Step 1: Export .tscn to .spatial.json
        print(f"\n{'='*60}")
        print(f"Step 1: Exporting {args.map_name}.tscn to .spatial.json")
        print(f"{'='*60}\n")

        spatial_path = export_tscn_to_spatial(tscn_path, asset_dir, output_dir)

        # Step 2: Create complete experience file
        print(f"\n{'='*60}")
        print(f"Step 2: Creating Portal experience file")
        print(f"{'='*60}\n")

        experience_path = create_experience_file(
            map_name=args.map_name,
            spatial_path=spatial_path,
            base_map=args.base_map,
            max_players_per_team=args.max_players,
            game_mode=args.game_mode,
            description=args.description
        )

        # Success!
        print(f"\n{'='*60}")
        print(f"✅ SUCCESS! Ready to import to Portal")
        print(f"{'='*60}\n")
        print(f"Import file: {experience_path}")
        print(f"\nNext steps:")
        print(f"1. Go to portal.battlefield.com")
        print(f"2. Click the 'IMPORT' button")
        print(f"3. Select: {experience_path}")
        print(f"4. Your map will appear in Map Rotation!")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
