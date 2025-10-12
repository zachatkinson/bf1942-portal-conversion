#!/usr/bin/env python3
"""BF1942 to Godot Heightmap Converter.

Converts BF1942 Heightmap.raw files to Godot-compatible formats.

BF1942 heightmaps are typically:
- 16-bit unsigned integers (RAW format)
- 256x256 or 512x512 resolution
- Height values 0-65535 map to world space heights

Godot supports:
- HeightMapShape3D: For collision (uses Image format)
- MeshInstance3D with PlaneMesh: For visual terrain
- Image formats: R16, RF (32-bit float)

Usage:
    python tools/convert_bf1942_heightmap.py

Output:
    - Kursk_heightmap.png (16-bit grayscale for Godot)
    - Kursk_terrain_mesh.obj (3D mesh for preview)
    - Height statistics and validation report
"""

import struct
from pathlib import Path


def detect_heightmap_dimensions(file_size: int) -> tuple[int, int]:
    """Detect heightmap dimensions from file size.

    Args:
        file_size: File size in bytes

    Returns:
        (width, height) tuple
    """
    # Assume 16-bit per pixel
    total_pixels = file_size // 2

    # Common BF1942 sizes
    if total_pixels == 256 * 256:
        return (256, 256)
    elif total_pixels == 512 * 512:
        return (512, 512)
    elif total_pixels == 1024 * 1024:
        return (1024, 1024)
    else:
        # Try to find square root
        import math

        side = int(math.sqrt(total_pixels))
        if side * side == total_pixels:
            return (side, side)

    raise ValueError(f"Cannot determine dimensions from file size {file_size}")


def read_bf1942_heightmap(filepath: Path) -> tuple[list[list[float]], int, int]:
    """Read BF1942 RAW heightmap file.

    Args:
        filepath: Path to Heightmap.raw

    Returns:
        (heightmap_2d_array, width, height)
    """
    file_size = filepath.stat().st_size
    width, height = detect_heightmap_dimensions(file_size)

    print(f"📐 Detected heightmap size: {width}x{height}")
    print(f"   File size: {file_size} bytes")

    heightmap = []

    with open(filepath, "rb") as f:
        for y in range(height):
            row = []
            for x in range(width):
                # Read 16-bit unsigned integer (little-endian)
                raw_bytes = f.read(2)
                if len(raw_bytes) < 2:
                    raise ValueError(f"Unexpected end of file at {x},{y}")

                value = struct.unpack("<H", raw_bytes)[0]  # unsigned short

                # Convert to float height (0-65535 -> meters)
                # BF1942 typically uses scale factor
                height_meters = value / 65535.0 * 255.0  # Rough estimate

                row.append(height_meters)
            heightmap.append(row)

    return heightmap, width, height


def analyze_heightmap(heightmap: list[list[float]], width: int, height: int) -> None:
    """Analyze and print heightmap statistics."""
    all_heights = [h for row in heightmap for h in row]

    min_h = min(all_heights)
    max_h = max(all_heights)
    avg_h = sum(all_heights) / len(all_heights)

    print("\n" + "=" * 70)
    print("Heightmap Statistics:")
    print("=" * 70)
    print(f"   Dimensions: {width}x{height}")
    print(f"   Total vertices: {len(all_heights):,}")
    print(f"   Min height: {min_h:.2f}m")
    print(f"   Max height: {max_h:.2f}m")
    print(f"   Avg height: {avg_h:.2f}m")
    print(f"   Range: {max_h - min_h:.2f}m")


def export_to_png(heightmap: list[list[float]], width: int, height: int, output_path: Path) -> None:
    """Export heightmap to 16-bit PNG (Godot-compatible).

    Note: Requires PIL/Pillow library.
    """
    try:
        import numpy as np
        from PIL import Image
    except ImportError:
        print("\n⚠️  PIL/Pillow not installed. Skipping PNG export.")
        print("   Install with: pip install Pillow")
        return

    # Normalize to 0-65535 range
    all_heights = [h for row in heightmap for h in row]
    min_h = min(all_heights)
    max_h = max(all_heights)
    range_h = max_h - min_h if max_h != min_h else 1.0

    # Create 16-bit numpy array
    normalized = np.zeros((height, width), dtype=np.uint16)

    for y in range(height):
        for x in range(width):
            # Normalize to 0-65535
            norm_value = int(((heightmap[y][x] - min_h) / range_h) * 65535)
            normalized[y, x] = norm_value

    # Save as 16-bit grayscale PNG
    img = Image.fromarray(normalized, mode="I;16")
    img.save(output_path)

    print(f"\n✅ Exported PNG heightmap: {output_path}")
    print("   Format: 16-bit grayscale")
    print(f"   Resolution: {width}x{height}")


def export_to_obj(
    heightmap: list[list[float]], width: int, height: int, output_path: Path, scale: float = 1.0
) -> None:
    """Export heightmap to OBJ mesh for visualization.

    Args:
        heightmap: 2D height array
        width, height: Dimensions
        output_path: Output .obj file
        scale: XZ scale factor (default 1.0 meter per vertex)
    """
    print("\n📦 Exporting OBJ mesh...")

    with open(output_path, "w") as f:
        f.write("# Kursk Heightmap Mesh\n")
        f.write("# Converted from BF1942 Heightmap.raw\n")
        f.write(f"# Dimensions: {width}x{height}\n\n")

        # Write vertices
        f.write("# Vertices\n")
        for y in range(height):
            for x in range(width):
                vx = x * scale
                vy = heightmap[y][x]
                vz = y * scale
                f.write(f"v {vx} {vy} {vz}\n")

        # Write faces (quads as two triangles)
        f.write("\n# Faces\n")
        for y in range(height - 1):
            for x in range(width - 1):
                # Vertex indices (1-based in OBJ)
                v1 = y * width + x + 1
                v2 = y * width + (x + 1) + 1
                v3 = (y + 1) * width + (x + 1) + 1
                v4 = (y + 1) * width + x + 1

                # Two triangles per quad
                f.write(f"f {v1} {v2} {v3}\n")
                f.write(f"f {v1} {v3} {v4}\n")

    print(f"✅ Exported OBJ mesh: {output_path}")
    print(f"   Vertices: {width * height:,}")
    print(f"   Faces: {(width - 1) * (height - 1) * 2:,}")


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    bf1942_heightmap = (
        project_root
        / "bf1942_source"
        / "extracted"
        / "Bf1942"
        / "Archives"
        / "bf1942"
        / "Levels"
        / "Kursk"
        / "Heightmap.raw"
    )

    output_dir = project_root / "GodotProject" / "terrain"
    output_dir.mkdir(exist_ok=True)

    png_output = output_dir / "Kursk_heightmap.png"
    obj_output = output_dir / "Kursk_terrain.obj"

    print("=" * 70)
    print("BF1942 to Godot Heightmap Converter")
    print("=" * 70)
    print(f"\nInput: {bf1942_heightmap}")

    if not bf1942_heightmap.exists():
        print("\n❌ ERROR: Heightmap not found!")
        print(f"   Expected: {bf1942_heightmap}")
        print("\nPlease extract Kursk.rfa first:")
        print("   See tools/README.md for RFA extraction instructions")
        return 1

    # Read heightmap
    print("\n🔧 Reading BF1942 heightmap...")
    heightmap, width, height = read_bf1942_heightmap(bf1942_heightmap)

    # Analyze
    analyze_heightmap(heightmap, width, height)

    # Export PNG (for Godot HeightMapShape3D)
    print("\n🔧 Exporting to PNG format...")
    export_to_png(heightmap, width, height, png_output)

    # Export OBJ (for visualization/preview)
    print("\n🔧 Exporting to OBJ mesh...")
    export_to_obj(heightmap, width, height, obj_output, scale=4.0)  # 4m per vertex

    print("\n" + "=" * 70)
    print("✅ Conversion complete!")
    print("=" * 70)
    print("\nNext steps:")
    print("  1. Import Kursk_heightmap.png into Godot")
    print("  2. Create HeightMapShape3D collision shape")
    print("  3. Create MeshInstance3D with terrain material")
    print("  4. Replace MP_Tungsten_Terrain with Kursk terrain")
    print("\nSee: https://docs.godotengine.org/en/stable/classes/class_heightmapshape3d.html")

    return 0


if __name__ == "__main__":
    exit(main())
