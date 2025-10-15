#!/usr/bin/env python3
"""Parser for Battlefield .con (configuration) files.

.con files are text-based script files used by Refractor Engine games
(BF1942, Vietnam, BF2, BF2142) to define objects, properties, and game logic.
"""

import re
from pathlib import Path
from typing import Any

from ..core.exceptions import ParseError
from ..core.interfaces import IParser, Rotation, Team, Transform, Vector3


class ConParser(IParser):
    """Parses Battlefield .con files.

    Example .con file structure:
        ObjectTemplate.create ObjectSpawner MySpawner
        ObjectTemplate.setPosition 100/50/200
        ObjectTemplate.setRotation 0/90/0
        ObjectTemplate.setTeam 1
    """

    def can_parse(self, file_path: Path) -> bool:
        """Check if this parser can handle the file.

        Args:
            file_path: Path to file

        Returns:
            True if file has .con extension
        """
        return file_path.suffix.lower() == ".con"

    def parse(self, file_path: Path) -> dict[str, Any]:
        """Parse .con file and return structured data.

        Args:
            file_path: Path to .con file

        Returns:
            Dictionary with parsed objects and properties

        Raises:
            ParseError: If file cannot be parsed
        """
        if not file_path.exists():
            raise ParseError(f"File not found: {file_path}")

        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                content = f.read()
        except Exception as e:
            raise ParseError(f"Failed to read {file_path}: {e}") from e

        # Parse the content
        objects = self._parse_objects(content)

        return {"file": str(file_path), "objects": objects, "raw_content": content}

    def _parse_objects(self, content: str) -> list[dict[str, Any]]:
        """Parse object definitions from .con file content.

        Args:
            content: File content

        Returns:
            List of object dictionaries
        """
        objects: list[dict[str, Any]] = []
        current_object: dict[str, Any] | None = None

        for line in content.split("\n"):
            line = line.strip()

            # Skip empty lines and comments
            if not line or line.startswith(("rem ", "//")):
                continue

            # ObjectTemplate.create <type> <name> (template definition)
            create_match = re.match(r"ObjectTemplate\.create\s+(\w+)\s+(\w+)", line)
            if create_match:
                if current_object:
                    objects.append(current_object)

                object_type, object_name = create_match.groups()
                current_object = {"name": object_name, "type": object_type, "properties": {}}
                continue

            # Object.create <name> (instance definition - use name as type)
            instance_match = re.match(r"Object\.create\s+(\w+)", line)
            if instance_match:
                if current_object:
                    objects.append(current_object)

                object_name = instance_match.group(1)
                current_object = {
                    "name": object_name,
                    "type": object_name,  # Use instance name as type
                    "properties": {},
                }
                continue

            # If we're inside an object definition, parse properties
            if current_object:
                self._parse_property(line, current_object)

        # Add the last object
        if current_object:
            objects.append(current_object)

        return objects

    def _parse_property(self, line: str, obj: dict[str, Any]) -> None:
        """Parse a property line and add to object.

        Args:
            line: Property line from .con file
            obj: Object dictionary to update
        """
        # ObjectTemplate.setPosition x/y/z
        pos_match = re.match(
            r"ObjectTemplate\.setPosition\s+([\d\.\-eE]+)/([\d\.\-eE]+)/([\d\.\-eE]+)", line
        )
        if pos_match:
            x, y, z = map(float, pos_match.groups())
            obj["position"] = {"x": x, "y": y, "z": z}
            return

        # Object.absolutePosition x/y/z (BF1942 instance format)
        abs_pos_match = re.match(
            r"Object\.absolutePosition\s+([\d\.\-eE]+)/([\d\.\-eE]+)/([\d\.\-eE]+)", line
        )
        if abs_pos_match:
            x, y, z = map(float, abs_pos_match.groups())
            obj["position"] = {"x": x, "y": y, "z": z}
            return

        # ObjectTemplate.setRotation pitch/yaw/roll
        rot_match = re.match(
            r"ObjectTemplate\.setRotation\s+([\d\.\-eE]+)/([\d\.\-eE]+)/([\d\.\-eE]+)", line
        )
        if rot_match:
            pitch, yaw, roll = map(float, rot_match.groups())
            obj["rotation"] = {"pitch": pitch, "yaw": yaw, "roll": roll}
            return

        # Object.rotation pitch/yaw/roll (BF1942 instance format)
        inst_rot_match = re.match(
            r"Object\.rotation\s+([\d\.\-eE]+)/([\d\.\-eE]+)/([\d\.\-eE]+)", line
        )
        if inst_rot_match:
            pitch, yaw, roll = map(float, inst_rot_match.groups())
            obj["rotation"] = {"pitch": pitch, "yaw": yaw, "roll": roll}
            return

        # Object.geometry.scale x/y/z (BF1942 scale format)
        scale_match = re.match(
            r"Object\.geometry\.scale\s+([\d\.\-eE]+)/([\d\.\-eE]+)/([\d\.\-eE]+)", line
        )
        if scale_match:
            x, y, z = map(float, scale_match.groups())
            obj["scale"] = {"x": x, "y": y, "z": z}
            return

        # ObjectTemplate.setTeam <team>
        team_match = re.match(r"ObjectTemplate\.setTeam\s+(\d+)", line)
        if team_match:
            obj["team"] = int(team_match.group(1))
            return

        # Object.setTeam <team> (BF1942 instance format)
        inst_team_match = re.match(r"Object\.setTeam\s+(\d+)", line)
        if inst_team_match:
            obj["team"] = int(inst_team_match.group(1))
            return

        # Generic property: ObjectTemplate.<property> <value>
        prop_match = re.match(r"ObjectTemplate\.(\w+)\s+(.+)", line)
        if prop_match:
            prop_name, prop_value = prop_match.groups()
            obj["properties"][prop_name] = prop_value.strip()
            return

        # Generic property: Object.<property> <value> (BF1942 instance format)
        inst_prop_match = re.match(r"Object\.(\w+)\s+(.+)", line)
        if inst_prop_match:
            prop_name, prop_value = inst_prop_match.groups()
            obj["properties"][prop_name] = prop_value.strip()

    def parse_transform(self, obj_dict: dict[str, Any]) -> Transform | None:
        """Extract Transform from parsed object dictionary.

        Args:
            obj_dict: Parsed object dictionary

        Returns:
            Transform if position/rotation found, None otherwise
        """
        pos_dict = obj_dict.get("position")
        rot_dict = obj_dict.get("rotation")
        scale_dict = obj_dict.get("scale")

        if not pos_dict:
            return None

        position = Vector3(pos_dict.get("x", 0), pos_dict.get("y", 0), pos_dict.get("z", 0))

        rotation = Rotation(0, 0, 0)
        if rot_dict:
            rotation = Rotation(
                rot_dict.get("pitch", 0), rot_dict.get("yaw", 0), rot_dict.get("roll", 0)
            )

        scale = None
        if scale_dict:
            scale = Vector3(
                scale_dict.get("x", 1.0), scale_dict.get("y", 1.0), scale_dict.get("z", 1.0)
            )

        return Transform(position, rotation, scale)

    def parse_team(self, obj_dict: dict[str, Any]) -> Team:
        """Extract team from parsed object dictionary.

        Args:
            obj_dict: Parsed object dictionary

        Returns:
            Team enum value

        Note:
            Falls back to setOSId if setTeam is not present.
            In BF1942, some spawners (like aircraft) only use setOSId.
        """
        team_id = obj_dict.get("team", 0)

        # Fallback: If no explicit team, try OSId (Object Spawn ID)
        # In BF1942, setOSId 1 = Team 1, setOSId 2 = Team 2
        if team_id == 0:
            os_id = obj_dict.get("properties", {}).get("setOSId", "0")
            try:
                team_id = int(os_id)
            except (ValueError, TypeError):
                pass

        if team_id == 1:
            return Team.TEAM_1
        elif team_id == 2:
            return Team.TEAM_2
        else:
            return Team.NEUTRAL


class ConFileSet:
    """Manages a set of related .con files for a map.

    BF1942 maps typically have multiple .con files:
    - Objects.con: Object placements
    - Spawns.con: Spawn points
    - ControlPoints.con: Capture points
    - etc.
    """

    def __init__(self, map_dir: Path):
        """Initialize with map directory.

        Args:
            map_dir: Path to map directory (extracted RFA)
        """
        self.map_dir = map_dir
        self.parser = ConParser()
        self.con_files: list[Path] = []

        # Find all .con files recursively
        if map_dir.exists():
            self.con_files = list(map_dir.rglob("*.con"))

    def find_file(self, pattern: str) -> Path | None:
        """Find a .con file matching a pattern.

        Args:
            pattern: Filename pattern (e.g., "Objects", "Spawns")

        Returns:
            Path to matching file, or None if not found
        """
        pattern_lower = pattern.lower()
        for con_file in self.con_files:
            if pattern_lower in con_file.name.lower():
                return con_file
        return None

    def parse_all(self) -> dict[str, dict[str, Any]]:
        """Parse all .con files in the map directory.

        Returns:
            Dictionary mapping filename to parsed data
        """
        results = {}

        for con_file in self.con_files:
            try:
                parsed = self.parser.parse(con_file)
                results[con_file.name] = parsed
            except ParseError as e:
                print(f"⚠️  Failed to parse {con_file.name}: {e}")

        return results

    def get_objects_by_type(self, object_type: str) -> list[dict[str, Any]]:
        """Get all objects of a specific type from all .con files.

        Args:
            object_type: Object type to search for (e.g., "ControlPoint")

        Returns:
            List of matching objects
        """
        results = []

        for con_file in self.con_files:
            try:
                parsed = self.parser.parse(con_file)
                for obj in parsed["objects"]:
                    if obj["type"] == object_type:
                        results.append(obj)
            except ParseError:
                continue

        return results
