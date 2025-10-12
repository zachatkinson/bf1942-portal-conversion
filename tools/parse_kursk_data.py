#!/usr/bin/env python3
"""Kursk Map Data Parser.

Parses BF1942 Kursk .con files to extract object placements, spawn points,
control points, and vehicle spawners for conversion to BF6 Portal format.

Usage:
    python tools/parse_kursk_data.py

Output:
    tools/kursk_extracted_data.json - All parsed gameplay data
"""

import json
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass
class Vector3:
    """3D vector for positions."""

    x: float
    y: float
    z: float

    @classmethod
    def from_string(cls, coord_string: str) -> "Vector3":
        """Parse BF1942 position string (x/y/z format).

        Args:
            coord_string: Position string like "123.45/67.89/012.34"

        Returns:
            Vector3 instance

        Raises:
            ValueError: If format is invalid
        """
        try:
            parts = coord_string.strip().split("/")
            if len(parts) != 3:
                raise ValueError(f"Expected 3 coordinates, got {len(parts)}")
            return cls(x=float(parts[0]), y=float(parts[1]), z=float(parts[2]))
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid position format '{coord_string}': {e}")


@dataclass
class Rotation:
    """Euler rotation angles."""

    pitch: float
    yaw: float
    roll: float

    @classmethod
    def from_string(cls, rotation_string: str) -> "Rotation":
        """Parse BF1942 rotation string (pitch/yaw/roll format).

        Args:
            rotation_string: Rotation string like "0/45.0/0"

        Returns:
            Rotation instance

        Raises:
            ValueError: If format is invalid
        """
        try:
            parts = rotation_string.strip().split("/")
            if len(parts) != 3:
                raise ValueError(f"Expected 3 rotation angles, got {len(parts)}")
            return cls(pitch=float(parts[0]), yaw=float(parts[1]), roll=float(parts[2]))
        except (ValueError, IndexError) as e:
            raise ValueError(f"Invalid rotation format '{rotation_string}': {e}")


@dataclass
class GameObject:
    """Generic game object with position and properties."""

    object_type: str
    position: Vector3
    rotation: Rotation | None = None
    team: int | None = None
    os_id: int | None = None
    properties: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        """Initialize empty properties dict if not provided."""
        if self.properties is None:
            self.properties = {}


class ConFileParser:
    """Parser for BF1942 .con configuration files."""

    def __init__(self, file_path: str):
        """Initialize parser.

        Args:
            file_path: Path to .con file
        """
        self.file_path = Path(file_path)
        self.lines: list[str] = []
        self.current_object: dict[str, Any] | None = None
        self.objects: list[dict[str, Any]] = []

    def load(self) -> None:
        """Load .con file into memory.

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        with open(self.file_path, encoding="utf-8", errors="ignore") as f:
            self.lines = [line.rstrip() for line in f]

    def parse(self) -> list[dict[str, Any]]:
        """Parse loaded .con file.

        Returns:
            List of parsed game object dictionaries

        Raises:
            ValueError: If parsing fails
        """
        self.objects = []
        self.current_object = None

        for line_num, line in enumerate(self.lines, 1):
            try:
                self._parse_line(line)
            except Exception as e:
                print(f"WARNING: Error parsing line {line_num}: {e}")
                print(f"  Line: {line}")
                continue

        # Finalize last object if exists
        if self.current_object:
            self.objects.append(self.current_object)

        return self.objects

    def _parse_line(self, line: str) -> None:
        """Parse a single line.

        Args:
            line: Line from .con file
        """
        # Skip empty lines and comments
        stripped = line.strip()
        if not stripped or stripped.startswith(("rem", "if", "endIf")):
            return

        # Object creation: Object.create <type>
        create_match = re.match(r"Object\.create\s+(\w+)", stripped)
        if create_match:
            # Save previous object if exists
            if self.current_object:
                self.objects.append(self.current_object)

            # Start new object
            object_type = create_match.group(1)
            self.current_object = {
                "object_type": object_type,
                "position": None,
                "rotation": None,
                "team": None,
                "os_id": None,
                "properties": {},
            }
            return

        # Only process properties if we have a current object
        if not self.current_object:
            return

        # Position: Object.absolutePosition x/y/z
        pos_match = re.match(r"Object\.absolutePosition\s+([\d\.\-/]+)", stripped)
        if pos_match:
            self.current_object["position"] = Vector3.from_string(pos_match.group(1))
            return

        # Rotation: Object.rotation pitch/yaw/roll
        rot_match = re.match(r"Object\.rotation\s+([\d\.\-/]+)", stripped)
        if rot_match:
            self.current_object["rotation"] = Rotation.from_string(rot_match.group(1))
            return

        # Team: Object.setTeam N
        team_match = re.match(r"Object\.setTeam\s+(\d+)", stripped)
        if team_match:
            self.current_object["team"] = int(team_match.group(1))
            return

        # OS ID: Object.setOSId N
        osid_match = re.match(r"Object\.setOSId\s+(\d+)", stripped)
        if osid_match:
            self.current_object["os_id"] = int(osid_match.group(1))
            return

        # Generic property: Object.property value
        prop_match = re.match(r"Object\.(\w+)\s+(.+)", stripped)
        if prop_match:
            prop_name = prop_match.group(1)
            prop_value = prop_match.group(2).strip()
            self.current_object["properties"][prop_name] = prop_value
            return

    def to_game_objects(self) -> list[GameObject]:
        """Convert parsed data to GameObject instances.

        Returns:
            List of GameObject instances
        """
        game_objects = []

        for obj_data in self.objects:
            if obj_data["position"] is None:
                # Skip objects without positions
                continue

            game_objects.append(
                GameObject(
                    object_type=obj_data["object_type"],
                    position=obj_data["position"],
                    rotation=obj_data["rotation"],
                    team=obj_data["team"],
                    os_id=obj_data["os_id"],
                    properties=obj_data["properties"],
                )
            )

        return game_objects


class KurskDataExtractor:
    """Extracts and organizes all Kursk map data."""

    def __init__(self, kursk_dir: str):
        """Initialize extractor.

        Args:
            kursk_dir: Path to extracted Kursk directory
        """
        self.kursk_dir = Path(kursk_dir)
        self.control_points: list[dict] = []
        self.vehicle_spawners: list[dict] = []
        self.static_objects: list[dict] = []

    def extract_control_points(self) -> list[dict[str, Any]]:
        """Extract control point data.

        Returns:
            List of control point dictionaries
        """
        control_points_file = self.kursk_dir / "Conquest" / "ControlPoints.con"

        if not control_points_file.exists():
            print(f"WARNING: {control_points_file} not found")
            return []

        parser = ConFileParser(str(control_points_file))
        parser.load()
        objects = parser.parse()

        control_points = []
        for obj_data in objects:
            if obj_data["position"]:
                cp_dict = {
                    "name": obj_data["object_type"],
                    "position": asdict(
                        Vector3.from_string(
                            f"{obj_data['position'].x}/{obj_data['position'].y}/{obj_data['position'].z}"
                        )
                    ),
                    "team": obj_data.get("team", 0),
                    "os_id": obj_data.get("os_id"),
                    "properties": obj_data.get("properties", {}),
                }
                control_points.append(cp_dict)

        return control_points

    def extract_vehicle_spawners(self) -> list[dict[str, Any]]:
        """Extract vehicle spawner data.

        Returns:
            List of vehicle spawner dictionaries
        """
        spawns_file = self.kursk_dir / "Conquest" / "ObjectSpawns.con"

        if not spawns_file.exists():
            print(f"WARNING: {spawns_file} not found")
            return []

        parser = ConFileParser(str(spawns_file))
        parser.load()
        parser.parse()

        vehicle_spawners = []
        for obj_data in parser.objects:
            if not obj_data["position"]:
                continue

            spawner_dict = {
                "bf1942_type": obj_data["object_type"],
                "position": asdict(obj_data["position"]),
                "rotation": asdict(obj_data["rotation"]) if obj_data["rotation"] else None,
                "team": obj_data["team"],
                "os_id": obj_data["os_id"],
                "properties": obj_data["properties"],
            }
            vehicle_spawners.append(spawner_dict)

        return vehicle_spawners

    def extract_all(self) -> dict[str, Any]:
        """Extract all Kursk data.

        Returns:
            Dictionary containing all extracted data
        """
        print(f"Extracting data from: {self.kursk_dir}")

        control_points = self.extract_control_points()
        vehicle_spawners = self.extract_vehicle_spawners()

        print(f"  Found {len(control_points)} control points")
        print(f"  Found {len(vehicle_spawners)} vehicle spawners")

        return {
            "map_name": "Kursk",
            "source_game": "Battlefield 1942",
            "target_game": "Battlefield 6 Portal",
            "extraction_date": "2025-10-10",
            "control_points": control_points,
            "vehicle_spawners": vehicle_spawners,
            "statistics": {
                "total_control_points": len(control_points),
                "total_vehicle_spawners": len(vehicle_spawners),
                "axis_spawners": len([s for s in vehicle_spawners if s.get("team") == 1]),
                "allies_spawners": len([s for s in vehicle_spawners if s.get("team") == 2]),
                "neutral_spawners": len(
                    [s for s in vehicle_spawners if s.get("team") is None or s.get("team") == 0]
                ),
            },
        }


def main() -> None:
    """Main entry point."""
    # Paths
    project_root = Path(__file__).parent.parent
    kursk_dir = (
        project_root
        / "bf1942_source"
        / "extracted"
        / "Bf1942"
        / "Archives"
        / "bf1942"
        / "Levels"
        / "Kursk"
    )

    if not kursk_dir.exists():
        print(f"ERROR: Kursk directory not found: {kursk_dir}")
        sys.exit(1)

    # Extract data
    extractor = KurskDataExtractor(str(kursk_dir))
    data = extractor.extract_all()

    # Save to JSON
    output_file = project_root / "tools" / "kursk_extracted_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    print("\n✅ Data extracted successfully!")
    print(f"📄 Saved to: {output_file}")
    print("\nStatistics:")
    print(f"  Control Points: {data['statistics']['total_control_points']}")
    print(f"  Vehicle Spawners: {data['statistics']['total_vehicle_spawners']}")
    print(f"    - Axis: {data['statistics']['axis_spawners']}")
    print(f"    - Allies: {data['statistics']['allies_spawners']}")
    print(f"    - Neutral: {data['statistics']['neutral_spawners']}")


if __name__ == "__main__":
    main()
