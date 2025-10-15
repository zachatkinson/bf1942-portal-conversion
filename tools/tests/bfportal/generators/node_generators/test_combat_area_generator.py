#!/usr/bin/env python3
"""Tests for CombatAreaGenerator ceiling positioning logic.

Tests verify that the CombatArea volume is positioned correctly ABOVE terrain
to act as a vertical ceiling, matching official Portal maps.

Key findings from official maps (MP_Tungsten, MP_Aftermath):
- CombatArea is a CEILING, not a floor boundary
- Positioned ~140m above ground (40-50m above highest terrain)
- Height is 100m (not 200m)
- Prevents players from flying/climbing too high
- Ground boundaries are defined by terrain geometry
"""

import sys
from pathlib import Path

import pytest

# Add tools directory to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from bfportal.core.interfaces import (
    MapBounds,
    MapData,
    Rotation,
    Transform,
    Vector3,
)
from bfportal.generators.components.asset_registry import AssetRegistry
from bfportal.generators.components.transform_formatter import TransformFormatter
from bfportal.generators.node_generators.combat_area_generator import (
    CombatAreaGenerator,
)


@pytest.fixture
def generator():
    """Provide CombatAreaGenerator instance."""
    return CombatAreaGenerator()


@pytest.fixture
def asset_registry():
    """Provide AssetRegistry instance."""
    return AssetRegistry()


@pytest.fixture
def transform_formatter():
    """Provide TransformFormatter instance."""
    return TransformFormatter()


@pytest.fixture
def kursk_map_data():
    """Create MapData matching Kursk terrain (Y=70 to Y=104)."""
    bounds = MapBounds(
        min_point=Vector3(x=-500, y=70, z=-500),
        max_point=Vector3(x=500, y=104, z=500),
        combat_area_polygon=[],
        height=200.0,
    )
    return MapData(
        map_name="Kursk",
        game_mode="Conquest",
        team1_hq=Transform(position=Vector3(0, 0, 0), rotation=Rotation(0, 0, 0)),
        team2_hq=Transform(position=Vector3(0, 0, 0), rotation=Rotation(0, 0, 0)),
        team1_spawns=[],
        team2_spawns=[],
        capture_points=[],
        game_objects=[],
        bounds=bounds,
        metadata={},
    )


def extract_collision_polygon_y(lines):
    """Extract Y position from CollisionPolygon3D transform line.

    The CollisionPolygon3D (child of CombatArea) has the actual position.
    Transform format: Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, x, y, z)
    """
    # Find the CollisionPolygon3D section
    in_collision_section = False
    for line in lines:
        if "CollisionPolygon3D" in line:
            in_collision_section = True
        elif in_collision_section and line.startswith("transform ="):
            parts = line.split(",")
            y_value = float(parts[-2].strip())
            return y_value

    raise AssertionError("No CollisionPolygon3D transform line found")


def test_combat_area_positioned_above_max_terrain(
    generator, asset_registry, transform_formatter, kursk_map_data
):
    """
    Test that CombatArea ceiling is positioned above maximum terrain Y.

    Given: Kursk terrain bounds (min_y=70, max_y=104)
    When: Generating CombatArea
    Then: Y position = 104 + 40 = 144 (40m buffer above highest point)
    """
    # Act
    lines = generator.generate(kursk_map_data, asset_registry, transform_formatter)

    # Assert
    y_pos = extract_collision_polygon_y(lines)
    expected_y = 104 + 40  # max_y + buffer
    assert y_pos == expected_y, f"Expected Y={expected_y}, got Y={y_pos}"


def test_combat_area_ceiling_extends_above_terrain(
    generator, asset_registry, transform_formatter, kursk_map_data
):
    """
    Test that CombatArea ceiling extends well above maximum terrain Y.

    Given: Kursk terrain (min_y=70, max_y=104)
    When: CombatArea positioned at Y=144 with height=100
    Then: Ceiling extends from Y=144 to Y=244, well above terrain
    """
    # Act
    lines = generator.generate(kursk_map_data, asset_registry, transform_formatter)

    # Assert
    y_pos = extract_collision_polygon_y(lines)

    height_line = next((line for line in lines if line.startswith("height =")), None)
    assert height_line is not None, "No height line found"
    height = float(height_line.split("=")[1].strip())

    ceiling_bottom = y_pos
    ceiling_top = y_pos + height

    terrain_max = 104

    assert ceiling_bottom > terrain_max, (
        f"Ceiling bottom ({ceiling_bottom}) should be above terrain max ({terrain_max})"
    )
    assert ceiling_top > ceiling_bottom, (
        f"Ceiling top ({ceiling_top}) should be above ceiling bottom ({ceiling_bottom})"
    )


def test_combat_area_uses_100m_height(
    generator, asset_registry, transform_formatter, kursk_map_data
):
    """Test that CombatArea uses 100m height (official maps standard)."""
    # Act
    lines = generator.generate(kursk_map_data, asset_registry, transform_formatter)

    # Assert
    height_line = next((line for line in lines if line.startswith("height =")), None)
    assert height_line is not None, "No height line found"
    height = float(height_line.split("=")[1].strip())

    # Official maps use 100m, not 200m
    assert height == 100.0


def test_combat_area_with_no_bounds_uses_defaults(generator, asset_registry, transform_formatter):
    """Test that CombatArea uses defaults when bounds not provided."""
    # Arrange
    default_bounds = MapBounds(
        min_point=Vector3(x=-500, y=0, z=-500),
        max_point=Vector3(x=500, y=100, z=500),
        combat_area_polygon=[],
        height=200.0,
    )
    map_data = MapData(
        map_name="NoBoundsMap",
        game_mode="Conquest",
        team1_hq=Transform(position=Vector3(0, 0, 0), rotation=Rotation(0, 0, 0)),
        team2_hq=Transform(position=Vector3(0, 0, 0), rotation=Rotation(0, 0, 0)),
        team1_spawns=[],
        team2_spawns=[],
        capture_points=[],
        game_objects=[],
        bounds=default_bounds,
        metadata={},
    )

    # Act
    lines = generator.generate(map_data, asset_registry, transform_formatter)

    # Assert - should not crash and use default ceiling height
    assert len(lines) > 0
    y_pos = extract_collision_polygon_y(lines)
    assert y_pos == 140.0  # Default ceiling height


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
