#!/usr/bin/env python3
"""Test scale parsing from BF1942 .con files."""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bfportal.parsers.con_parser import ConParser


def test_scale_parsing():
    """Test that ConParser correctly extracts scale values."""

    # Create test .con content with scale
    test_content = """
Object.create Tree_01
Object.absolutePosition 100/50/200
Object.rotation 0/45/0
Object.geometry.scale 0.88/0.96/0.84
Object.setTeam 0
"""

    # Create temporary test file
    test_file = Path("/tmp/test_scale.con")
    with open(test_file, "w") as f:
        f.write(test_content)

    try:
        # Parse the file
        parser = ConParser()
        result = parser.parse(test_file)

        # Verify object was parsed
        assert len(result["objects"]) == 1, f"Expected 1 object, got {len(result['objects'])}"

        obj = result["objects"][0]

        # Verify scale was extracted
        assert "scale" in obj, "Scale not found in parsed object"

        scale_dict = obj["scale"]
        assert scale_dict["x"] == 0.88, f"Expected x=0.88, got {scale_dict['x']}"
        assert scale_dict["y"] == 0.96, f"Expected y=0.96, got {scale_dict['y']}"
        assert scale_dict["z"] == 0.84, f"Expected z=0.84, got {scale_dict['z']}"

        # Verify transform extraction includes scale
        transform = parser.parse_transform(obj)
        assert transform is not None, "Transform should not be None"
        assert transform.scale is not None, "Transform scale should not be None"
        assert transform.scale.x == 0.88, f"Expected scale.x=0.88, got {transform.scale.x}"
        assert transform.scale.y == 0.96, f"Expected scale.y=0.96, got {transform.scale.y}"
        assert transform.scale.z == 0.84, f"Expected scale.z=0.84, got {transform.scale.z}"

        print("✅ Scale parsing test PASSED")
        print(f"   Parsed scale: {scale_dict}")
        print(
            f"   Transform scale: ({transform.scale.x}, {transform.scale.y}, {transform.scale.z})"
        )

    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()


def test_no_scale_defaults():
    """Test that objects without scale default to (1, 1, 1)."""

    # Create test .con content WITHOUT scale
    test_content = """
Object.create Tree_02
Object.absolutePosition 100/50/200
Object.rotation 0/45/0
Object.setTeam 0
"""

    # Create temporary test file
    test_file = Path("/tmp/test_no_scale.con")
    with open(test_file, "w") as f:
        f.write(test_content)

    try:
        # Parse the file
        parser = ConParser()
        result = parser.parse(test_file)

        obj = result["objects"][0]

        # Verify scale is NOT in raw parsed data (since it wasn't specified)
        assert "scale" not in obj, "Scale should not be present in parsed object"

        # Verify transform extraction defaults to (1, 1, 1)
        transform = parser.parse_transform(obj)
        assert transform is not None, "Transform should not be None"
        assert transform.scale is not None, "Transform scale should not be None (should default)"
        assert transform.scale.x == 1.0, f"Expected default scale.x=1.0, got {transform.scale.x}"
        assert transform.scale.y == 1.0, f"Expected default scale.y=1.0, got {transform.scale.y}"
        assert transform.scale.z == 1.0, f"Expected default scale.z=1.0, got {transform.scale.z}"

        print("✅ Default scale test PASSED")
        print(
            f"   Transform scale (default): ({transform.scale.x}, {transform.scale.y}, {transform.scale.z})"
        )

    finally:
        # Clean up
        if test_file.exists():
            test_file.unlink()


if __name__ == "__main__":
    print("Running scale parsing tests...")
    print("=" * 60)

    test_scale_parsing()
    print()
    test_no_scale_defaults()

    print("=" * 60)
    print("✅ All scale parsing tests PASSED!")
