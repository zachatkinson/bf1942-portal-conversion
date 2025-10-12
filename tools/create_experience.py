#!/usr/bin/env python3
"""
Create a complete Battlefield 6 Portal experience file from a .spatial.json map.

This tool takes an existing .spatial.json file and wraps it in a complete
experience format ready for import into the Portal web builder.

Usage:
    python3 tools/create_experience.py <map_name> [options]

Examples:
    python3 tools/create_experience.py Kursk
    python3 tools/create_experience.py Kursk --base-map MP_Outskirts --max-players 64
"""

import argparse
import base64
import json
import sys
from pathlib import Path
from typing import Optional


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

    Raises:
        FileNotFoundError: If spatial file doesn't exist
        RuntimeError: If experience creation fails
    """
    if not spatial_path.exists():
        raise FileNotFoundError(f"Spatial file not found: {spatial_path}")

    # Read the spatial.json file
    print(f"Reading spatial data from {spatial_path}...")
    with open(spatial_path, 'r', encoding='utf-8') as f:
        spatial_data = f.read()

    # Base64 encode the spatial data
    print(f"Encoding spatial data (base64)...")
    spatial_base64 = base64.b64encode(spatial_data.encode('utf-8')).decode('utf-8')

    # Create default description if none provided
    if description is None:
        description = (
            f"A custom recreation of {map_name} from Battlefield 1942. "
            f"Features authentic spawn points, vehicle spawners, and gameplay objects."
        )

    print(f"Creating experience structure...")

    # Create the complete experience structure following the official pattern
    # Based on analysis of official example mods (AcePursuit, BombSquad, Exfil, Vertigo)
    # ALL official examples include these universal mutator fields
    experience = {
        "mutators": {
            "MaxPlayerCount_PerTeam": max_players_per_team,
            "AiMaxCount_PerTeam": 0,
            "AiSpawnType": 2,
            "AI_ManDownExperienceType_PerTeam": 1,  # Universal field - AI respawn behavior
            "ModBuilder_GameMode": 2,  # Universal field - game mode configuration
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
                # CRITICAL: Must follow pattern MP_<MapName>-ModBuilderCustom0
                # This is required by Portal to recognize custom map attachments
                "id": f"{base_map}-ModBuilderCustom0",
                "spatialAttachment": {
                    "id": f"{map_name.lower()}-bf1942-spatial",
                    "filename": f"{map_name}.spatial.json",
                    "metadata": "mapIdx=0",
                    "version": "1",
                    "isProcessable": True,
                    "processingStatus": 2,
                    "attachmentData": {
                        "original": spatial_base64,
                        "compiled": ""  # Empty - Portal compiles server-side
                    },
                    "attachmentType": 1,
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

    # Create experiences directory if it doesn't exist
    experiences_dir = Path("experiences")
    experiences_dir.mkdir(exist_ok=True)

    # Write the experience file
    output_file = experiences_dir / f"{map_name}_Experience.json"
    print(f"Writing experience file to {output_file}...")

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(experience, f, indent=2)

    print(f"\n{'='*60}")
    print(f"✅ Created {output_file}")
    print(f"{'='*60}")
    print(f"   Name: {experience['name']}")
    print(f"   Base map: {base_map}")
    print(f"   Game mode: {game_mode}")
    print(f"   Max players: {max_players_per_team * 2} ({max_players_per_team}v{max_players_per_team})")
    print(f"   Spatial data: {len(spatial_data):,} bytes")
    print(f"   Encoded size: {len(spatial_base64):,} bytes")
    print(f"   Total file size: {output_file.stat().st_size:,} bytes")
    print(f"{'='*60}\n")

    return output_file


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create a complete Portal experience file from a .spatial.json map",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Create experience from Kursk.spatial.json with defaults:
    %(prog)s Kursk

  Use custom base map and player count:
    %(prog)s Kursk --base-map MP_Outskirts --max-players 32

  Add custom description:
    %(prog)s Kursk --description "Epic tank battle on the Eastern Front"

Workflow:
  1. First export your .tscn to .spatial.json:
     bash tools/export_map.sh Kursk

  2. Then create the Portal experience file:
     python3 tools/create_experience.py Kursk

  3. Import the experience file in Portal Builder:
     portal.battlefield.com → Import → Select Kursk_Experience.json

Available base maps (choose terrain similar to your map):
  - MP_Tungsten     (Tajikistan - mountains/valleys)
  - MP_Outskirts    (Cairo - desert/urban)
  - MP_Battery      (Gibraltar - rocky terrain)
  - MP_Capstone     (Tajikistan - mountains)
  - MP_Abbasid      (Cairo - urban)
  - MP_Aftermath    (Brooklyn - urban ruins)
  - MP_Dumbo        (Brooklyn - urban)
  - MP_FireStorm    (Turkmenistan - desert)
  - MP_Limestone    (Gibraltar - coastal)
        """
    )

    parser.add_argument(
        "map_name",
        help="Name of the map (e.g., Kursk, El_Alamein)"
    )

    parser.add_argument(
        "--spatial-path",
        type=Path,
        help="Path to .spatial.json file (default: FbExportData/levels/<map_name>.spatial.json)"
    )

    parser.add_argument(
        "--base-map",
        default="MP_Tungsten",
        help="Base map for terrain (default: MP_Tungsten)"
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

    args = parser.parse_args()

    # Determine spatial file path
    if args.spatial_path:
        spatial_path = args.spatial_path
    else:
        spatial_path = Path(f"FbExportData/levels/{args.map_name}.spatial.json")

    if not spatial_path.exists():
        print(f"❌ Error: Spatial file not found: {spatial_path}\n", file=sys.stderr)
        print(f"Available spatial files:", file=sys.stderr)
        levels_dir = Path("FbExportData/levels")
        if levels_dir.exists():
            spatial_files = list(levels_dir.glob("*.spatial.json"))
            if spatial_files:
                for f in sorted(spatial_files):
                    print(f"  - {f.stem}", file=sys.stderr)
            else:
                print(f"  (none found)", file=sys.stderr)
                print(f"\nDid you export the map first?", file=sys.stderr)
                print(f"Run: bash tools/export_map.sh {args.map_name}", file=sys.stderr)
        return 1

    try:
        experience_path = create_experience_file(
            map_name=args.map_name,
            spatial_path=spatial_path,
            base_map=args.base_map,
            max_players_per_team=args.max_players,
            game_mode=args.game_mode,
            description=args.description
        )

        print(f"✅ SUCCESS! Ready to import to Portal\n")
        print(f"Next steps:")
        print(f"1. Go to portal.battlefield.com")
        print(f"2. Click 'IMPORT' button")
        print(f"3. Select: {experience_path.name}")
        print(f"4. Your map will appear in the Map Rotation!")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
