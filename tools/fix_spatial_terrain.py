#!/usr/bin/env python3
"""Fix spatial.json by resetting terrain to (0,0,0) and adjusting all objects.

Portal requires base terrain meshes to be at (0,0,0) with no transform.
This script:
1. Finds the terrain transform in spatial.json
2. Resets terrain position to (0,0,0)
3. Applies the inverse terrain transform to all Portal_Dynamic objects

Usage:
    python3 tools/fix_spatial_terrain.py <spatial.json>
"""

import json
import sys
from pathlib import Path


def fix_spatial_terrain(spatial_path: Path) -> None:
    """Fix spatial.json terrain and object positions for Portal compatibility."""
    print(f"🔧 Fixing {spatial_path.name}...")
    
    # Load spatial.json
    with open(spatial_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Find terrain and get its transform
    terrain_offset_x = 0.0
    terrain_offset_y = 0.0
    terrain_offset_z = 0.0
    
    for obj in data.get('Static', []):
        if 'Terrain' in obj.get('type', ''):
            pos = obj.get('position', {})
            terrain_offset_x = pos.get('x', 0.0)
            terrain_offset_y = pos.get('y', 0.0)
            terrain_offset_z = pos.get('z', 0.0)
            
            print(f"   📐 Found terrain at: ({terrain_offset_x:.2f}, {terrain_offset_y:.2f}, {terrain_offset_z:.2f})")
            
            # Reset terrain to (0, 0, 0)
            obj['position'] = {'x': 0.0, 'y': 0.0, 'z': 0.0}
            print(f"   ✅ Reset terrain to: (0, 0, 0)")
            break
    
    if terrain_offset_x == 0 and terrain_offset_y == 0 and terrain_offset_z == 0:
        print("   ℹ️  Terrain already at (0, 0, 0) - no fix needed")
        return
    
    # Apply inverse terrain transform to all Portal_Dynamic objects
    # (subtract terrain offset from object positions)
    adjusted_count = 0
    for obj in data.get('Portal_Dynamic', []):
        if 'position' in obj:
            pos = obj['position']
            pos['x'] -= terrain_offset_x
            pos['y'] -= terrain_offset_y
            pos['z'] -= terrain_offset_z
            adjusted_count += 1
    
    print(f"   ✅ Adjusted {adjusted_count} Portal_Dynamic objects")
    
    # Also adjust Static objects (except terrain)
    static_adjusted = 0
    for obj in data.get('Static', []):
        if 'Terrain' not in obj.get('type', '') and 'position' in obj:
            pos = obj['position']
            pos['x'] -= terrain_offset_x
            pos['y'] -= terrain_offset_y
            pos['z'] -= terrain_offset_z
            static_adjusted += 1
    
    if static_adjusted > 0:
        print(f"   ✅ Adjusted {static_adjusted} Static objects")
    
    # Save fixed spatial.json
    with open(spatial_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Fixed {spatial_path}")
    print(f"   Terrain: (0, 0, 0)")
    print(f"   Objects shifted by: ({-terrain_offset_x:.2f}, {-terrain_offset_y:.2f}, {-terrain_offset_z:.2f})")


def main() -> int:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python3 tools/fix_spatial_terrain.py <spatial.json>")
        return 1
    
    spatial_path = Path(sys.argv[1])
    
    if not spatial_path.exists():
        print(f"❌ File not found: {spatial_path}")
        return 1
    
    try:
        fix_spatial_terrain(spatial_path)
        return 0
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
