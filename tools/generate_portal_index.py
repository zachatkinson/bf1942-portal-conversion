#!/usr/bin/env python3
"""Generate Portal asset indexes from Portal SDK asset_types.json.

This CLI tool creates searchable indexes and browsable catalogs of all
Portal assets available for BF1942→Portal conversions.

Architecture:
- Follows SOLID principles with separated concerns
- Uses Strategy pattern for different index types
- Uses Facade pattern for simple CLI interface
- Generates derived data structures (not source of truth)

Usage:
    python3 generate_portal_index.py [--portal-sdk PATH]

Output:
    - asset_audit/portal_asset_index.json (machine-readable index)
    - asset_audit/PORTAL_ASSET_CATALOG.md (human-readable catalog)
"""

import sys
from pathlib import Path

# Add tools directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from bfportal.indexers.portal_asset_indexer import PortalAssetIndexerFacade


def main() -> None:
    """Main entry point for Portal asset indexing."""

    # Paths
    portal_sdk_root = Path("FbExportData")
    asset_types_path = portal_sdk_root / "asset_types.json"

    json_output = Path("asset_audit/portal_asset_index.json")
    markdown_output = Path("asset_audit/PORTAL_ASSET_CATALOG.md")

    # Validate Portal SDK file exists
    if not asset_types_path.exists():
        print(f"❌ ERROR: Portal SDK asset file not found: {asset_types_path}")
        print()
        print("Expected location: FbExportData/asset_types.json")
        print("Please ensure Portal SDK is properly installed.")
        sys.exit(1)

    # Banner
    print("=" * 80)
    print("PORTAL ASSET INDEXER")
    print("=" * 80)
    print()
    print(f"📂 Source: {asset_types_path}")
    print(f"📂 JSON Output: {json_output}")
    print(f"📂 Markdown Output: {markdown_output}")
    print()
    print("=" * 80)
    print()

    # Create indexer and generate
    indexer = PortalAssetIndexerFacade(
        asset_types_path=asset_types_path,
        json_output_path=json_output,
        markdown_output_path=markdown_output,
    )

    try:
        index_data = indexer.generate_indexes()

        # Success summary
        print()
        print("=" * 80)
        print("✅ INDEXING COMPLETE")
        print("=" * 80)

        metadata = index_data["_metadata"]
        print("\n📊 Summary:")
        print(f"   • Total assets: {metadata['total_assets']:,}")
        print(f"   • Unrestricted: {metadata['unrestricted_count']:,}")
        print(f"   • Categories: {len(metadata['categories'])}")
        print(f"   • Map-specific: {metadata['total_assets'] - metadata['unrestricted_count']:,}")

        print("\n📁 Generated files:")
        print(f"   • {json_output}")
        print(f"   • {markdown_output}")

        print()
        print("=" * 80)
        print()
        print("Next steps:")
        print("  1. Review: Open PORTAL_ASSET_CATALOG.md to browse Portal assets")
        print("  2. Use: portal_asset_index.json is ready for tool integration")
        print("  3. Map: Create BF1942→Portal mappings with full asset palette visibility")
        print()

    except FileNotFoundError as e:
        print(f"❌ ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ ERROR: Unexpected error during indexing: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
