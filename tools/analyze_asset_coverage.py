#!/usr/bin/env python3
"""
Asset Coverage Analysis Tool
Verifies completeness of BF1942→Portal asset mapping system.
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set

def load_json(filepath: Path) -> dict:
    """Load JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def analyze_portal_assets(asset_types_path: Path) -> Dict:
    """Analyze Portal asset catalog."""
    data = load_json(asset_types_path)
    assets = data.get('AssetTypes', [])

    total = len(assets)
    by_category = defaultdict(int)
    usable_on_tungsten = 0
    unrestricted = 0

    for asset in assets:
        asset_type = asset.get('type', '')
        directory = asset.get('directory', '')
        restrictions = asset.get('levelRestrictions', [])

        # Categorize by directory
        if directory:
            category = directory.split('/')[0]
            by_category[category] += 1

        # Check restrictions
        if not restrictions:
            unrestricted += 1
        elif 'MP_Tungsten' in restrictions:
            usable_on_tungsten += 1

    return {
        'total': total,
        'by_category': dict(by_category),
        'usable_on_tungsten': usable_on_tungsten,
        'unrestricted': unrestricted
    }

def analyze_bf1942_catalog(catalog_path: Path) -> Dict:
    """Analyze BF1942 asset catalog."""
    data = load_json(catalog_path)

    total = len(data)
    by_category = defaultdict(int)

    for bf1942_name, info in data.items():
        category = info.get('category', 'unknown')
        by_category[category] += 1

    return {
        'total': total,
        'by_category': dict(by_category),
        'asset_names': set(data.keys())
    }

def analyze_mapping_table(mappings_path: Path) -> Dict:
    """Analyze BF1942→Portal mapping table."""
    data = load_json(mappings_path)

    total = len(data)
    complete = 0
    todo_entries = []
    no_equivalent = []
    with_fallback = 0

    mapped_bf1942_assets = set()

    for bf1942_name, mapping in data.items():
        mapped_bf1942_assets.add(bf1942_name)

        portal_asset = mapping.get('portal_asset', '')
        notes = mapping.get('notes', '')
        fallback = mapping.get('fallback_alternatives', [])

        if portal_asset and portal_asset != 'TODO':
            complete += 1

        if portal_asset == 'TODO' or 'TODO' in notes:
            todo_entries.append(bf1942_name)

        if 'no direct equivalent' in notes.lower() or portal_asset == '':
            no_equivalent.append(bf1942_name)

        if fallback:
            with_fallback += 1

    return {
        'total': total,
        'complete': complete,
        'todo_entries': todo_entries,
        'no_equivalent': no_equivalent,
        'with_fallback': with_fallback,
        'mapped_assets': mapped_bf1942_assets
    }

def analyze_kursk_usage(kursk_path: Path) -> Set[str]:
    """Extract unique BF1942 asset types used in Kursk."""
    data = load_json(kursk_path)

    asset_types = set()

    # Extract from vehicle spawners
    for spawner in data.get('vehicle_spawners', []):
        bf1942_type = spawner.get('bf1942_type', '')
        if bf1942_type:
            asset_types.add(bf1942_type)

    return asset_types

def main():
    """Main analysis function."""
    base_path = Path('/Users/zach/Downloads/PortalSDK')

    portal_path = base_path / 'FbExportData' / 'asset_types.json'
    bf1942_catalog_path = base_path / 'tools' / 'asset_audit' / 'bf1942_asset_catalog.json'
    mappings_path = base_path / 'tools' / 'asset_audit' / 'bf1942_to_portal_mappings.json'
    kursk_path = base_path / 'tools' / 'kursk_extracted_data.json'

    print("=" * 80)
    print("ASSET COVERAGE REPORT")
    print("=" * 80)
    print()

    # Analyze Portal assets
    print("### Portal Assets (Available)")
    print("-" * 80)
    portal_info = analyze_portal_assets(portal_path)
    print(f"Total Portal assets: {portal_info['total']}")
    print(f"Unrestricted assets: {portal_info['unrestricted']}")
    print(f"Usable on MP_Tungsten: {portal_info['usable_on_tungsten']}")
    print()
    print("By category:")
    for category, count in sorted(portal_info['by_category'].items(), key=lambda x: -x[1])[:10]:
        print(f"  {category}: {count}")
    print()

    # Analyze BF1942 catalog
    print("### BF1942 Assets (Source)")
    print("-" * 80)
    bf1942_info = analyze_bf1942_catalog(bf1942_catalog_path)
    print(f"Total BF1942 assets cataloged: {bf1942_info['total']}")
    print()
    print("By category:")
    for category, count in sorted(bf1942_info['by_category'].items(), key=lambda x: -x[1]):
        print(f"  {category}: {count}")
    print()

    # Analyze mapping table
    print("### Mapping Table Status")
    print("-" * 80)
    mapping_info = analyze_mapping_table(mappings_path)
    print(f"Total mappings: {mapping_info['total']}")
    print(f"Complete mappings: {mapping_info['complete']}")
    print(f"TODO/incomplete: {len(mapping_info['todo_entries'])}")
    print(f"No Portal equivalent: {len(mapping_info['no_equivalent'])}")
    print(f"With fallback alternatives: {mapping_info['with_fallback']}")
    print()

    # Analyze Kursk usage
    print("### Kursk Map Asset Usage")
    print("-" * 80)
    kursk_assets = analyze_kursk_usage(kursk_path)
    print(f"Unique BF1942 asset types in Kursk: {len(kursk_assets)}")
    print(f"Asset types: {sorted(kursk_assets)}")
    print()

    # Gap analysis
    print("### Gap Analysis")
    print("-" * 80)

    # BF1942 assets not in mapping table
    unmapped = bf1942_info['asset_names'] - mapping_info['mapped_assets']
    print(f"BF1942 assets NOT in mapping table: {len(unmapped)}")

    # Critical: Kursk assets not mapped
    kursk_unmapped = kursk_assets - mapping_info['mapped_assets']
    print(f"Kursk assets NOT mapped: {len(kursk_unmapped)}")
    if kursk_unmapped:
        print("  CRITICAL - These are used in Kursk:")
        for asset in sorted(kursk_unmapped):
            print(f"    - {asset}")
    print()

    # Kursk assets with TODO mappings
    kursk_todo = kursk_assets.intersection(set(mapping_info['todo_entries']))
    print(f"Kursk assets with TODO mappings: {len(kursk_todo)}")
    if kursk_todo:
        print("  Need Portal equivalents:")
        for asset in sorted(kursk_todo):
            print(f"    - {asset}")
    print()

    # Non-Kursk unmapped (lower priority)
    non_kursk_unmapped = unmapped - kursk_assets
    print(f"Non-Kursk unmapped assets: {len(non_kursk_unmapped)}")
    if len(non_kursk_unmapped) <= 20:
        print("  Assets:")
        for asset in sorted(non_kursk_unmapped):
            print(f"    - {asset}")
    print()

    # Summary
    print("### Coverage Summary")
    print("-" * 80)
    coverage_pct = (mapping_info['total'] / bf1942_info['total'] * 100) if bf1942_info['total'] > 0 else 0
    complete_pct = (mapping_info['complete'] / mapping_info['total'] * 100) if mapping_info['total'] > 0 else 0
    kursk_coverage_pct = ((len(kursk_assets) - len(kursk_unmapped)) / len(kursk_assets) * 100) if kursk_assets else 0

    print(f"Overall BF1942 mapping coverage: {coverage_pct:.1f}%")
    print(f"Mapping completion rate: {complete_pct:.1f}%")
    print(f"Kursk-specific coverage: {kursk_coverage_pct:.1f}%")
    print()

    # Recommendations
    print("### Recommendations")
    print("-" * 80)

    if kursk_unmapped:
        print("1. CRITICAL: Create mappings for Kursk assets:")
        for asset in sorted(kursk_unmapped):
            print(f"   - {asset}")
        print()

    if kursk_todo:
        print("2. HIGH PRIORITY: Complete TODO mappings for Kursk assets:")
        for asset in sorted(kursk_todo):
            print(f"   - {asset}")
        print()

    if len(mapping_info['todo_entries']) > len(kursk_todo):
        print(f"3. MEDIUM PRIORITY: Complete {len(mapping_info['todo_entries']) - len(kursk_todo)} remaining TODO entries")
        print()

    if unmapped:
        print(f"4. LOW PRIORITY: Create mappings for {len(unmapped)} unmapped BF1942 assets")
        print()

    print("=" * 80)

if __name__ == '__main__':
    main()
