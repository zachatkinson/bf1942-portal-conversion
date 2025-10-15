#!/usr/bin/env python3
"""Spawner template parser for BF1942 ObjectSpawner definitions.

Single Responsibility: Parse ObjectSpawnTemplates.con to extract vehicle type mappings.

This module reads BF1942 spawner template definitions and builds a mapping of
spawner names to their team-specific vehicle types. This follows the DRY principle
by centralizing spawner template parsing in one place.
"""

import contextlib
from dataclasses import dataclass
from pathlib import Path

from ..core.interfaces import Team


@dataclass
class SpawnerTemplate:
    """Represents a BF1942 ObjectSpawner template.

    Attributes:
        name: Spawner template name (e.g., "lighttankspawner")
        team1_vehicle: Vehicle type for Team 1/Axis (setObjectTemplate 1)
        team2_vehicle: Vehicle type for Team 2/Allies (setObjectTemplate 2)
        spawn_delay_min: Minimum respawn delay in seconds
        spawn_delay_max: Maximum respawn delay in seconds
        time_to_live: Vehicle lifetime before auto-destroy (0 = infinite)
    """

    name: str
    team1_vehicle: str | None = None
    team2_vehicle: str | None = None
    spawn_delay_min: int = 0
    spawn_delay_max: int = 0
    time_to_live: int = 0

    def get_vehicle_for_team(self, team: Team) -> str | None:
        """Get vehicle type for specific team.

        Args:
            team: Team enum value

        Returns:
            Vehicle type string for that team, or None if not set
        """
        if team == Team.TEAM_1:
            return self.team1_vehicle
        elif team == Team.TEAM_2:
            return self.team2_vehicle
        return None


class SpawnerTemplateParser:
    """Parses ObjectSpawnTemplates.con files to extract vehicle spawner info.

    Single Responsibility: Only parses spawner template definitions.
    DRY Principle: Single source of truth for spawner vehicle mappings.

    BF1942 spawner format:
        ObjectTemplate.create ObjectSpawner lighttankspawner
        ObjectTemplate.setObjectTemplate 2 T34-85
        ObjectTemplate.setObjectTemplate 1 panzeriv
        ObjectTemplate.MinSpawnDelay 40
        ObjectTemplate.MaxSpawnDelay 80

    This parser extracts:
    - Spawner name (e.g., "lighttankspawner")
    - Team 1 vehicle (setObjectTemplate 1 = Axis)
    - Team 2 vehicle (setObjectTemplate 2 = Allies)
    - Spawn timing parameters
    """

    def __init__(self):
        """Initialize spawner template parser."""
        self.templates: dict[str, SpawnerTemplate] = {}

    def parse_template_file(self, template_file: Path) -> None:
        """Parse an ObjectSpawnTemplates.con file.

        Args:
            template_file: Path to ObjectSpawnTemplates.con

        Updates:
            self.templates with parsed spawner definitions
        """
        if not template_file.exists():
            return

        with open(template_file, encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()

        current_template: SpawnerTemplate | None = None

        for line in lines:
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith(("rem ", "//")):
                continue

            # New spawner template
            # Format: ObjectTemplate.create ObjectSpawner lighttankspawner
            # Parts after split(): ["ObjectTemplate.create", "ObjectSpawner", "lighttankspawner"]
            if "ObjectTemplate.create ObjectSpawner" in line:
                parts = line.split()
                if len(parts) >= 3:  # Fixed: 3 parts, not 4
                    spawner_name = parts[2].lower()  # Fixed: index 2, not 3
                    current_template = SpawnerTemplate(name=spawner_name)
                    self.templates[spawner_name] = current_template

            # Vehicle type for specific team
            # Format: ObjectTemplate.setObjectTemplate 2 T34-85
            # Parts after split(): ["ObjectTemplate.setObjectTemplate", "2", "T34-85"]
            elif current_template and "setObjectTemplate" in line:
                parts = line.split()
                if len(parts) >= 3:  # Fixed: 3 parts, not 4
                    team_id = parts[1]  # Fixed: index 1 (team number)
                    vehicle_type = parts[2]  # Fixed: index 2 (vehicle name)

                    if team_id == "1":
                        current_template.team1_vehicle = vehicle_type
                    elif team_id == "2":
                        current_template.team2_vehicle = vehicle_type

            # Spawn timing parameters
            elif current_template and "MinSpawnDelay" in line:
                parts = line.split()
                if len(parts) >= 3:
                    with contextlib.suppress(ValueError):
                        current_template.spawn_delay_min = int(parts[2])

            elif current_template and "MaxSpawnDelay" in line:
                parts = line.split()
                if len(parts) >= 3:
                    with contextlib.suppress(ValueError):
                        current_template.spawn_delay_max = int(parts[2])

            elif current_template and "TimeToLive" in line:
                parts = line.split()
                if len(parts) >= 3:
                    with contextlib.suppress(ValueError):
                        current_template.time_to_live = int(parts[2])

    def parse_directory(self, level_dir: Path) -> None:
        """Parse all ObjectSpawnTemplates.con files in a level directory.

        Searches recursively for ObjectSpawnTemplates.con files (usually in
        Conquest/, TDM/, CTF/ subdirectories) and parses all of them.

        IMPORTANT: Skips SinglePlayer directories as they have different
        vehicle assignments for the campaign (e.g., yak9 instead of Ilyushin).

        Args:
            level_dir: Path to BF1942 level directory

        Updates:
            self.templates with all parsed spawner definitions
        """
        if not level_dir.exists():
            return

        # Find all ObjectSpawnTemplates.con files
        template_files = list(level_dir.glob("**/ObjectSpawnTemplates.con"))

        for template_file in template_files:
            # Skip SinglePlayer directories - they have campaign-specific vehicle assignments
            if "SinglePlayer" in str(template_file) or "Coop" in str(template_file):
                continue
            self.parse_template_file(template_file)

    def get_template(self, spawner_name: str) -> SpawnerTemplate | None:
        """Get spawner template by name.

        Args:
            spawner_name: Name of spawner template (case-insensitive)

        Returns:
            SpawnerTemplate object if found, None otherwise
        """
        return self.templates.get(spawner_name.lower())

    def get_vehicle_type(self, spawner_name: str, team: Team) -> str | None:
        """Get vehicle type for a specific spawner and team.

        Args:
            spawner_name: Name of spawner template
            team: Team enum value

        Returns:
            Vehicle type string, or None if not found

        Example:
            >>> parser = SpawnerTemplateParser()
            >>> parser.parse_directory(Path("Kursk"))
            >>> parser.get_vehicle_type("lighttankspawner", Team.TEAM_1)
            'panzeriv'
            >>> parser.get_vehicle_type("lighttankspawner", Team.TEAM_2)
            'T34-85'
        """
        template = self.get_template(spawner_name)
        if template:
            return template.get_vehicle_for_team(team)
        return None

    def get_all_templates(self) -> dict[str, SpawnerTemplate]:
        """Get all parsed spawner templates.

        Returns:
            Dictionary mapping spawner names to SpawnerTemplate objects
        """
        return self.templates.copy()

    def get_template_count(self) -> int:
        """Get number of parsed spawner templates.

        Returns:
            Count of templates
        """
        return len(self.templates)
