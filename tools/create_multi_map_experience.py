#!/usr/bin/env python3
"""
Create multi-map Portal experiences from the maps registry.

This tool generates Portal experience files containing multiple BF1942 maps
in a single rotation, based on the maps_registry.json configuration.

Usage:
    python3 tools/create_multi_map_experience.py [options]

Examples:
    # Create experience with all complete maps (default)
    python3 tools/create_multi_map_experience.py

    # Use specific template from registry
    python3 tools/create_multi_map_experience.py --template all_maps_conquest

    # Create experience with specific maps only
    python3 tools/create_multi_map_experience.py --maps kursk el_alamein wake_island

    # Override experience name and description
    python3 tools/create_multi_map_experience.py --name "Custom Experience" --description "My maps"

    # Use custom player count
    python3 tools/create_multi_map_experience.py --max-players 32
"""

import argparse
import base64
import json
import sys
from pathlib import Path
from typing import Any

from bfportal.exporters import create_spatial_attachment


def load_registry(registry_path: Path) -> dict[str, Any]:
    """Load the maps registry."""
    if not registry_path.exists():
        raise FileNotFoundError(f"Maps registry not found: {registry_path}")

    with open(registry_path, encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)
        return data


def filter_maps(
    maps: list[dict[str, Any]], filter_criteria: dict[str, Any]
) -> list[dict[str, Any]]:
    """Filter maps based on criteria."""
    filtered = maps
    for key, value in filter_criteria.items():
        filtered = [m for m in filtered if m.get(key) == value]
    return filtered


def load_spatial_data(map_entry: dict[str, Any], project_root: Path) -> str:
    """Load and base64 encode spatial data for a map."""
    map_id = map_entry["id"]
    spatial_path = (
        project_root / "FbExportData" / "levels" / f"{map_entry['display_name']}.spatial.json"
    )

    if not spatial_path.exists():
        raise FileNotFoundError(
            f"Spatial file not found for {map_id}: {spatial_path}\n"
            f"Run: python3 tools/export_to_portal.py {map_entry['display_name']}"
        )

    with open(spatial_path, encoding="utf-8") as f:
        spatial_data = f.read()

    return base64.b64encode(spatial_data.encode("utf-8")).decode("utf-8")


def create_multi_map_experience(
    maps: list[dict[str, Any]],
    experience_name: str,
    description: str,
    game_mode: str,
    max_players_per_team: int,
    project_root: Path,
) -> dict[str, Any]:
    """Create a multi-map Portal experience."""
    print(f"\nCreating multi-map experience: {experience_name}")
    print(f"Maps to include: {len(maps)}")
    print("=" * 60)

    map_rotation = []
    attachments = []  # Root-level attachments array (required by Portal UI)

    for idx, map_entry in enumerate(maps):
        map_id = map_entry["id"]
        map_name = map_entry["display_name"]
        base_map = map_entry["base_map"]

        print(f"\n[{idx + 1}/{len(maps)}] Processing {map_name}...")
        print(f"  Base map: {base_map} ({map_entry['base_map_display']})")
        print(f"  Status: {map_entry['status']}")

        if map_entry["status"] != "complete":
            print("  ⚠️  Skipping (not complete)")
            continue

        try:
            spatial_base64 = load_spatial_data(map_entry, project_root)
            print(f"  ✅ Loaded spatial data ({len(spatial_base64):,} bytes)")

            # Create spatial attachment (used in both mapRotation and root attachments)
            spatial_attachment = create_spatial_attachment(
                map_id=map_id,
                map_name=map_name,
                spatial_base64=spatial_base64,
                map_index=idx,
            )

            # Add to map rotation (nested)
            map_rotation.append(
                {
                    "id": f"{base_map}-ModBuilderCustom0",
                    "spatialAttachment": spatial_attachment,
                }
            )

            # CRITICAL: Also add to root-level attachments array
            # Portal requires the spatial attachment in BOTH locations for UI to work
            attachments.append(spatial_attachment)

        except FileNotFoundError as e:
            print(f"  ❌ Error: {e}")
            continue

    if not map_rotation:
        raise RuntimeError("No maps were successfully loaded. Cannot create experience.")

    print(f"\n{'=' * 60}")
    print(f"✅ Successfully loaded {len(map_rotation)} map(s)")
    print(f"{'=' * 60}\n")

    # Create the complete experience structure
    experience = {
        "mutators": {
            "MaxPlayerCount_PerTeam": max_players_per_team,
            "AiMaxCount_PerTeam": 0,
            "AiSpawnType": 2,
            "AI_ManDownExperienceType_PerTeam": 1,
            "ModBuilder_GameMode": 0,  # Custom mode
            "CQ_iModeTime": 60 if game_mode == "Conquest" else 30,
            "AimAssistSnapCapsuleRadiusMultiplier": 1,
            "FriendlyFireDamageReflectionMaxTeamKills": 2,
            "SpawnBalancing_GamemodeStartTimer": 0,
            "SpawnBalancing_GamemodePlayerCountRatio": 0.75,
        },
        "assetRestrictions": {},
        "name": experience_name,
        "description": description,
        "mapRotation": map_rotation,
        "workspace": {},
        "teamComposition": [
            [1, {"humanCapacity": max_players_per_team, "aiCapacity": 0, "aiType": 0}],
            [2, {"humanCapacity": max_players_per_team, "aiCapacity": 0, "aiType": 0}],
        ],
        "gameMode": game_mode,
        "attachments": attachments,  # ✅ Populated with spatial attachments
    }

    return experience


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Create multi-map Portal experiences from maps registry",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Create experience with all complete maps:
    %(prog)s

  Use specific template:
    %(prog)s --template all_maps_conquest

  Include only specific maps:
    %(prog)s --maps kursk el_alamein wake_island

  Override experience details:
    %(prog)s --name "My Custom Experience" --description "Custom map rotation"

  Use different player count:
    %(prog)s --max-players 32
        """,
    )

    parser.add_argument(
        "--template",
        default="all_maps_conquest",
        help="Experience template from registry (default: all_maps_conquest)",
    )

    parser.add_argument(
        "--maps", nargs="+", help="Specific map IDs to include (overrides template filter)"
    )

    parser.add_argument("--name", help="Override experience name from template")

    parser.add_argument("--description", help="Override experience description from template")

    parser.add_argument(
        "--game-mode",
        choices=["Conquest", "Rush", "TeamDeathmatch", "Breakthrough"],
        help="Override game mode from template",
    )

    parser.add_argument(
        "--max-players",
        type=int,
        choices=[16, 32, 64],
        help="Override max players per team from template",
    )

    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("maps_registry.json"),
        help="Path to maps registry (default: maps_registry.json)",
    )

    parser.add_argument(
        "--output",
        type=Path,
        help="Output path for experience file (default: experiences/multi/<name>_Experience.json)",
    )

    args = parser.parse_args()

    # Determine project root
    project_root = Path.cwd()
    registry_path = project_root / args.registry

    try:
        # Load registry
        print(f"Loading maps registry from {registry_path}...")
        registry = load_registry(registry_path)

        # Get template
        if args.template not in registry["experience_templates"]:
            print(f"❌ Error: Template '{args.template}' not found in registry", file=sys.stderr)
            print("\nAvailable templates:", file=sys.stderr)
            for template_name in registry["experience_templates"]:
                print(f"  - {template_name}", file=sys.stderr)
            return 1

        template = registry["experience_templates"][args.template]

        # Determine which maps to include
        all_maps = registry["maps"]

        if args.maps:
            # Specific maps requested
            map_ids = args.maps
            selected_maps = [m for m in all_maps if m["id"] in map_ids]
            missing = set(map_ids) - {m["id"] for m in selected_maps}
            if missing:
                print(f"⚠️  Warning: Maps not found in registry: {', '.join(missing)}")
        else:
            # Use template filter
            map_filter = template.get("map_filter", {})
            selected_maps = filter_maps(all_maps, map_filter)

        if not selected_maps:
            print("❌ Error: No maps matched the criteria", file=sys.stderr)
            return 1

        # Get experience details (with overrides)
        experience_name = args.name or template["name"]
        description = args.description or template["description"]
        game_mode = args.game_mode or template["game_mode"]
        max_players = args.max_players or template["max_players"]

        # Create experience
        experience = create_multi_map_experience(
            maps=selected_maps,
            experience_name=experience_name,
            description=description,
            game_mode=game_mode,
            max_players_per_team=max_players,
            project_root=project_root,
        )

        # Determine output path
        if args.output:
            output_file = args.output
        else:
            experiences_dir = project_root / "experiences" / "multi"
            experiences_dir.mkdir(parents=True, exist_ok=True)
            # Sanitize name for filename
            safe_name = experience_name.replace(" ", "_").replace("-", "_")
            output_file = experiences_dir / f"{safe_name}_Experience.json"

        # Write experience file
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(experience, f, indent=2)

        # Print summary
        print(f"{'=' * 60}")
        print("✅ SUCCESS! Multi-map experience created")
        print(f"{'=' * 60}")
        print(f"\nExperience: {experience_name}")
        print(f"Description: {description}")
        print(f"Game mode: {game_mode}")
        print(f"Max players: {max_players * 2} ({max_players}v{max_players})")
        print(f"Maps in rotation: {len(experience['mapRotation'])}")
        for idx, map_entry in enumerate(experience["mapRotation"]):
            filename = map_entry["spatialAttachment"]["filename"]
            print(f"  {idx + 1}. {filename.replace('.spatial.json', '')}")
        print(f"\nOutput file: {output_file}")
        print(f"File size: {output_file.stat().st_size:,} bytes")
        print("\nNext steps:")
        print("1. Go to portal.battlefield.com")
        print("2. Click 'IMPORT' button")
        print(f"3. Select: {output_file.name}")
        print("4. Map rotation will appear pre-populated - verify and save!")
        print("5. Test your experience in-game!")

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback

        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
