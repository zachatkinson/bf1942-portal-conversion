#!/usr/bin/env python3
"""
Validate Portal experience files for correctness and completeness.

This tool validates both single-map and multi-map experience files,
checking for proper structure, required fields, and common issues.

Usage:
    python3 tools/validate_experience.py <experience_file.json>
    python3 tools/validate_experience.py experiences/Kursk_Experience.json
    python3 tools/validate_experience.py experiences/multi/1942_Revisited_Experience.json

Examples:
    # Validate single experience file
    python3 tools/validate_experience.py experiences/Kursk_Experience.json

    # Validate all experience files
    python3 tools/validate_experience.py experiences/*.json

    # Validate with verbose output
    python3 tools/validate_experience.py experiences/Kursk_Experience.json --verbose
"""

import argparse
import base64
import json
import sys
from pathlib import Path
from typing import Any


class ExperienceValidator:
    """Validator for Portal experience files."""

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.info: list[str] = []

    def validate_file(self, experience_path: Path) -> bool:
        """
        Validate a Portal experience file.

        Args:
            experience_path: Path to the experience JSON file

        Returns:
            True if valid, False if errors found
        """
        self.errors = []
        self.warnings = []
        self.info = []

        print(f"\n{'=' * 70}")
        print(f"Validating: {experience_path.name}")
        print(f"{'=' * 70}\n")

        # Check file exists
        if not experience_path.exists():
            self.errors.append(f"File not found: {experience_path}")
            return False

        # Load JSON
        try:
            with open(experience_path, encoding="utf-8") as f:
                experience = json.load(f)
        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON: {e}")
            return False

        # Validate structure
        self._validate_required_fields(experience)
        self._validate_mutators(experience)
        self._validate_team_composition(experience)
        self._validate_map_rotation(experience)
        self._validate_attachments(experience)
        self._validate_mode_consistency(experience)

        # Print results
        self._print_results(experience_path)

        return len(self.errors) == 0

    def _validate_required_fields(self, experience: dict[str, Any]) -> None:
        """Validate required top-level fields."""
        required_fields = [
            "mutators",
            "gameMode",
            "name",
            "description",
            "mapRotation",
            "teamComposition",
            "attachments",
        ]

        for field in required_fields:
            if field not in experience:
                self.errors.append(f"Missing required field: '{field}'")
            elif experience[field] is None:
                self.errors.append(f"Field '{field}' is null")

        # Check field types
        if "name" in experience and not isinstance(experience["name"], str):
            self.errors.append("Field 'name' must be a string")
        elif "name" in experience and len(experience["name"]) == 0:
            self.errors.append("Field 'name' cannot be empty")

        if "description" in experience and not isinstance(experience["description"], str):
            self.errors.append("Field 'description' must be a string")

        if "mapRotation" in experience and not isinstance(experience["mapRotation"], list):
            self.errors.append("Field 'mapRotation' must be an array")

        if "attachments" in experience and not isinstance(experience["attachments"], list):
            self.errors.append("Field 'attachments' must be an array")

    def _validate_mutators(self, experience: dict[str, Any]) -> None:
        """Validate mutators structure and values."""
        if "mutators" not in experience:
            return

        mutators = experience["mutators"]
        if not isinstance(mutators, dict):
            self.errors.append("Field 'mutators' must be an object")
            return

        # Check required mutator fields
        required_mutators = [
            "MaxPlayerCount_PerTeam",
            "ModBuilder_GameMode",
        ]

        for field in required_mutators:
            if field not in mutators:
                self.errors.append(f"Missing required mutator: '{field}'")

        # Validate ModBuilder_GameMode
        if "ModBuilder_GameMode" in mutators:
            mode = mutators["ModBuilder_GameMode"]
            if mode == 0:
                self.info.append("Mode: Custom (local testing only)")
            elif mode == 2:
                self.info.append("Mode: Verified (publishable to Portal)")
            else:
                self.warnings.append(f"Unknown ModBuilder_GameMode value: {mode}")

        # Validate player count
        if "MaxPlayerCount_PerTeam" in mutators:
            max_players = mutators["MaxPlayerCount_PerTeam"]
            # Portal allows int, list, or dict formats
            if isinstance(max_players, (dict, list)):
                # Complex format: per-team configuration
                if self.verbose:
                    self.info.append("Max players: Custom per-team configuration")
            elif isinstance(max_players, int):
                if max_players < 1:
                    self.errors.append("MaxPlayerCount_PerTeam must be at least 1")
                elif max_players > 128:
                    self.errors.append("MaxPlayerCount_PerTeam cannot exceed 128")
                elif max_players > 32:
                    self.warnings.append(
                        f"MaxPlayerCount_PerTeam is {max_players} (Portal recommends 32)"
                    )
                else:
                    self.info.append(
                        f"Max players: {max_players}v{max_players} ({max_players * 2} total)"
                    )
            else:
                self.errors.append(
                    f"MaxPlayerCount_PerTeam has unexpected type: {type(max_players).__name__}"
                )

    def _validate_team_composition(self, experience: dict[str, Any]) -> None:
        """Validate team composition structure."""
        if "teamComposition" not in experience:
            return

        team_comp = experience["teamComposition"]
        if not isinstance(team_comp, list):
            self.errors.append("Field 'teamComposition' must be an array")
            return

        # Portal supports both 2-team (standard) and multi-team configurations
        if len(team_comp) < 2:
            self.errors.append(
                f"teamComposition must have at least 2 teams (found {len(team_comp)})"
            )
            return
        elif len(team_comp) > 2:
            if self.verbose:
                self.info.append(f"Multi-team configuration: {len(team_comp)} teams")

        # Only validate standard 2-team structure in detail
        if len(team_comp) != 2:
            return

        # Validate each team
        for idx, team_entry in enumerate(team_comp):
            if not isinstance(team_entry, list) or len(team_entry) != 2:
                self.errors.append(f"Team {idx + 1} must be [team_id, team_config]")
                continue

            team_id, team_config = team_entry

            if team_id not in [1, 2]:
                self.errors.append(f"Team ID must be 1 or 2 (found {team_id})")

            if not isinstance(team_config, dict):
                self.errors.append(f"Team {team_id} config must be an object")
                continue

            # Check required team fields
            if "humanCapacity" not in team_config:
                self.errors.append(f"Team {team_id} missing 'humanCapacity'")
            # aiCapacity is optional (some experiences don't use AI)
            if "aiCapacity" not in team_config and self.verbose:
                self.info.append(f"Team {team_id} has no AI capacity configured")

    def _validate_map_rotation(self, experience: dict[str, Any]) -> None:
        """Validate map rotation structure."""
        if "mapRotation" not in experience:
            return

        map_rotation = experience["mapRotation"]
        if not isinstance(map_rotation, list):
            self.errors.append("Field 'mapRotation' must be an array")
            return

        if len(map_rotation) == 0:
            self.errors.append("mapRotation cannot be empty")
            return

        # Determine if single or multi-map
        map_count = len(map_rotation)
        if map_count == 1:
            self.info.append("Type: Single-map experience")
        else:
            self.info.append(f"Type: Multi-map experience ({map_count} maps)")

        # Validate each map entry
        for idx, map_entry in enumerate(map_rotation):
            if not isinstance(map_entry, dict):
                self.errors.append(f"Map {idx + 1} must be an object")
                continue

            # Check required fields
            if "id" not in map_entry:
                self.errors.append(f"Map {idx + 1} missing 'id' field")
            else:
                map_id = map_entry["id"]
                # Validate map ID format
                if not map_id.endswith("-ModBuilderCustom0"):
                    self.warnings.append(
                        f"Map {idx + 1} ID should end with '-ModBuilderCustom0' (found: {map_id})"
                    )

            if "spatialAttachment" not in map_entry:
                self.errors.append(f"Map {idx + 1} missing 'spatialAttachment' field")
            else:
                self._validate_spatial_attachment(map_entry["spatialAttachment"], f"Map {idx + 1}")

    def _validate_spatial_attachment(self, attachment: Any, context: str) -> None:
        """Validate spatial attachment structure."""
        if not isinstance(attachment, dict):
            self.errors.append(f"{context} spatialAttachment must be an object")
            return

        # Check required fields
        required_fields = ["id", "filename", "attachmentData", "attachmentType"]
        for field in required_fields:
            if field not in attachment:
                self.errors.append(f"{context} spatialAttachment missing '{field}'")

        # Validate attachment type
        if "attachmentType" in attachment and attachment["attachmentType"] != 1:
            self.errors.append(
                f"{context} spatialAttachment type must be 1 (spatial), found: {attachment['attachmentType']}"
            )

        # Validate attachment data
        if "attachmentData" in attachment:
            attach_data = attachment["attachmentData"]
            if not isinstance(attach_data, dict):
                self.errors.append(f"{context} attachmentData must be an object")
            else:
                if "original" not in attach_data:
                    self.errors.append(f"{context} attachmentData missing 'original' field")
                else:
                    # Validate base64 encoding
                    original = attach_data["original"]
                    if not isinstance(original, str):
                        self.errors.append(f"{context} attachmentData.original must be a string")
                    elif len(original) == 0:
                        self.errors.append(f"{context} attachmentData.original is empty")
                    else:
                        # Try to decode base64
                        try:
                            decoded = base64.b64decode(original)
                            # Try to parse as JSON
                            spatial_data = json.loads(decoded)
                            if self.verbose:
                                self.info.append(f"{context} spatial data: {len(decoded):,} bytes")
                            # Basic spatial structure check
                            if (
                                "Portal_Dynamic" not in spatial_data
                                and "Static" not in spatial_data
                            ):
                                self.warnings.append(
                                    f"{context} spatial data missing 'Portal_Dynamic' or 'Static'"
                                )
                        except Exception as e:
                            self.errors.append(
                                f"{context} attachmentData.original is not valid base64 JSON: {e}"
                            )

        # Check filename
        if "filename" in attachment:
            filename = attachment["filename"]
            if not filename.endswith(".spatial.json"):
                self.warnings.append(
                    f"{context} filename should end with '.spatial.json' (found: {filename})"
                )

    def _validate_attachments(self, experience: dict[str, Any]) -> None:
        """Validate root-level attachments array."""
        if "attachments" not in experience:
            return

        attachments = experience["attachments"]
        if not isinstance(attachments, list):
            self.errors.append("Field 'attachments' must be an array")
            return

        if "mapRotation" not in experience:
            return

        map_rotation = experience["mapRotation"]

        # Check that number of attachments matches number of maps
        # Note: Some experiences may have additional attachments (scripts, etc.)
        if len(attachments) < len(map_rotation):
            self.errors.append(
                f"Attachments count ({len(attachments)}) is less than map rotation count ({len(map_rotation)})"
            )
        elif len(attachments) > len(map_rotation) and self.verbose:
            self.info.append(
                f"Extra attachments: {len(attachments) - len(map_rotation)} (may include scripts/logic)"
            )

        # Check that each attachment has matching spatial attachment in map rotation
        attachment_ids = {att.get("id") for att in attachments if isinstance(att, dict)}
        map_attachment_ids = {
            map_entry.get("spatialAttachment", {}).get("id")
            for map_entry in map_rotation
            if isinstance(map_entry, dict)
        }

        if attachment_ids != map_attachment_ids:
            self.warnings.append(
                "Root-level attachments IDs do not match mapRotation spatialAttachment IDs"
            )

    def _validate_mode_consistency(self, experience: dict[str, Any]) -> None:
        """Validate consistency between mode and game mode."""
        if "mutators" not in experience or "gameMode" not in experience:
            return

        mutators = experience["mutators"]
        game_mode = experience["gameMode"]

        if "ModBuilder_GameMode" in mutators:
            mode = mutators["ModBuilder_GameMode"]

            # Note: Portal examples show that ModBuilderCustom can be used with
            # verified mode (2) when using custom spatial data. The mode determines
            # publishability, not the gameMode string.

            # Only warn if using non-ModBuilderCustom with custom mode
            if mode == 0 and game_mode != "ModBuilderCustom":
                self.warnings.append(
                    f"Custom mode (0) typically uses gameMode 'ModBuilderCustom' (found: {game_mode})"
                )

        self.info.append(f"Game mode: {game_mode}")

    def _print_results(self, experience_path: Path) -> None:
        """Print validation results."""
        # Print info
        if self.info:
            print("ℹ️  Information:")
            for msg in self.info:
                print(f"   {msg}")
            print()

        # Print warnings
        if self.warnings:
            print("⚠️  Warnings:")
            for msg in self.warnings:
                print(f"   - {msg}")
            print()

        # Print errors
        if self.errors:
            print("❌ Errors:")
            for msg in self.errors:
                print(f"   - {msg}")
            print()

        # Print summary
        print(f"{'=' * 70}")
        if len(self.errors) == 0:
            print("✅ VALIDATION PASSED")
            if len(self.warnings) > 0:
                print(f"   ({len(self.warnings)} warning(s))")
        else:
            print("❌ VALIDATION FAILED")
            print(f"   {len(self.errors)} error(s), {len(self.warnings)} warning(s)")
        print(f"{'=' * 70}\n")


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate Portal experience files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Validate single experience:
    %(prog)s experiences/Kursk_Experience.json

  Validate multi-map experience:
    %(prog)s experiences/multi/1942_Revisited_Experience.json

  Validate all experience files:
    %(prog)s experiences/*.json experiences/multi/*.json

  Verbose output:
    %(prog)s experiences/Kursk_Experience.json --verbose
        """,
    )

    parser.add_argument(
        "experience_files",
        nargs="+",
        type=Path,
        help="Path(s) to experience JSON file(s)",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show detailed validation information",
    )

    args = parser.parse_args()

    validator = ExperienceValidator(verbose=args.verbose)
    all_valid = True

    for experience_path in args.experience_files:
        if not validator.validate_file(experience_path):
            all_valid = False

    # Print overall summary if multiple files
    if len(args.experience_files) > 1:
        print(f"\n{'=' * 70}")
        print(f"OVERALL SUMMARY: {len(args.experience_files)} file(s) validated")
        print(f"{'=' * 70}\n")

    return 0 if all_valid else 1


if __name__ == "__main__":
    sys.exit(main())
