#!/usr/bin/env python3
"""
Complete Asset Coverage Analysis
Analyzes all asset sources and identifies gaps in mapping coverage.
"""

import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

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
    portal_asset_names = set()

    for asset in assets:
        asset_type = asset.get('type', '')
        portal_asset_names.add(asset_type)
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
        'unrestricted': unrestricted,
        'asset_names': portal_asset_names
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
        'asset_names': set(data.keys()),
        'full_data': data
    }

def analyze_mapping_table(mappings_path: Path) -> Dict:
    """Analyze BF1942→Portal mapping table (nested by category)."""
    data = load_json(mappings_path)

    total = 0
    complete = 0
    todo_entries = []
    no_equivalent = []
    with_fallback = 0
    auto_suggested = 0

    mapped_bf1942_assets = set()
    mapped_portal_assets = set()

    # Iterate through nested structure
    for section, assets in data.items():
        if section.startswith('_'):  # Skip metadata
            continue

        if not isinstance(assets, dict):
            continue

        for bf1942_name, mapping in assets.items():
            # Handle both nested dict and direct string values
            if not isinstance(mapping, dict):
                continue

            total += 1
            mapped_bf1942_assets.add(bf1942_name)

            portal_asset = mapping.get('portal_equivalent', '')
            notes = mapping.get('notes', '')
            fallback = mapping.get('fallback_alternatives', [])
            is_auto = mapping.get('auto_suggested', False)

            if portal_asset and portal_asset != 'TODO' and portal_asset != '':
                complete += 1
                mapped_portal_assets.add(portal_asset)

            if is_auto:
                auto_suggested += 1

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
        'auto_suggested': auto_suggested,
        'mapped_bf1942': mapped_bf1942_assets,
        'mapped_portal': mapped_portal_assets
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
    print("COMPLETE ASSET COVERAGE ANALYSIS")
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
    print("Top 10 categories:")
    for category, count in sorted(portal_info['by_category'].items(), key=lambda x: -x[1])[:10]:
        print(f"  {category}: {count}")
    print()

    # Analyze BF1942 catalog
    print("### BF1942 Assets (Cataloged)")
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
    print(f"Total BF1942 assets with mappings: {mapping_info['total']}")
    print(f"Complete mappings (with Portal asset): {mapping_info['complete']}")
    print(f"Auto-suggested mappings: {mapping_info['auto_suggested']}")
    print(f"TODO/incomplete: {len(mapping_info['todo_entries'])}")
    print(f"No Portal equivalent: {len(mapping_info['no_equivalent'])}")
    print(f"With fallback alternatives: {mapping_info['with_fallback']}")
    print(f"Unique Portal assets used: {len(mapping_info['mapped_portal'])}")
    print()

    # Analyze Kursk usage
    print("### Kursk Map Asset Usage")
    print("-" * 80)
    kursk_assets = analyze_kursk_usage(kursk_path)
    print(f"Unique BF1942 asset types in Kursk: {len(kursk_assets)}")
    print(f"Asset types:")
    for asset in sorted(kursk_assets):
        print(f"  - {asset}")
    print()

    # Gap analysis
    print("### CRITICAL GAP ANALYSIS")
    print("-" * 80)
    print()

    # 1. Kursk assets not in BF1942 catalog
    kursk_not_in_catalog = kursk_assets - bf1942_info['asset_names']
    print(f"1. Kursk assets NOT in BF1942 catalog: {len(kursk_not_in_catalog)}")
    if kursk_not_in_catalog:
        print("   ACTION REQUIRED: Add these to bf1942_asset_catalog.json")
        for asset in sorted(kursk_not_in_catalog):
            print(f"   - {asset}")
    print()

    # 2. Kursk assets not in mapping table
    kursk_not_mapped = kursk_assets - mapping_info['mapped_bf1942']
    print(f"2. Kursk assets NOT in mapping table: {len(kursk_not_mapped)}")
    if kursk_not_mapped:
        print("   ACTION REQUIRED: Add mappings to bf1942_to_portal_mappings.json")
        for asset in sorted(kursk_not_mapped):
            # Check if in catalog
            in_catalog = asset in bf1942_info['asset_names']
            status = "in catalog" if in_catalog else "NOT in catalog"
            print(f"   - {asset} ({status})")
    print()

    # 3. Kursk assets with TODO mappings
    kursk_todo = kursk_assets.intersection(set(mapping_info['todo_entries']))
    print(f"3. Kursk assets with TODO mappings: {len(kursk_todo)}")
    if kursk_todo:
        print("   ACTION REQUIRED: Complete these mappings")
        for asset in sorted(kursk_todo):
            print(f"   - {asset}")
    print()

    # 4. BF1942 assets not mapped (general)
    unmapped = bf1942_info['asset_names'] - mapping_info['mapped_bf1942']
    non_kursk_unmapped = unmapped - kursk_assets
    print(f"4. Non-Kursk BF1942 assets unmapped: {len(non_kursk_unmapped)}")
    print(f"   (Low priority - not used in Kursk)")
    print()

    # Coverage metrics
    print("### Coverage Metrics")
    print("-" * 80)

    # Overall mapping coverage
    overall_coverage = (mapping_info['total'] / bf1942_info['total'] * 100) if bf1942_info['total'] > 0 else 0
    print(f"Overall BF1942 mapping coverage: {overall_coverage:.1f}%")
    print(f"  ({mapping_info['total']} of {bf1942_info['total']} BF1942 assets have mapping entries)")
    print()

    # Mapping completion rate
    complete_pct = (mapping_info['complete'] / mapping_info['total'] * 100) if mapping_info['total'] > 0 else 0
    print(f"Mapping completion rate: {complete_pct:.1f}%")
    print(f"  ({mapping_info['complete']} of {mapping_info['total']} mappings have Portal assets)")
    print()

    # Kursk coverage
    kursk_in_catalog = len(kursk_assets - kursk_not_in_catalog)
    kursk_mapped = len(kursk_assets - kursk_not_mapped)

    kursk_catalog_pct = (kursk_in_catalog / len(kursk_assets) * 100) if kursk_assets else 0
    kursk_mapping_pct = (kursk_mapped / len(kursk_assets) * 100) if kursk_assets else 0

    print(f"Kursk asset cataloging: {kursk_catalog_pct:.1f}%")
    print(f"  ({kursk_in_catalog} of {len(kursk_assets)} Kursk assets in catalog)")
    print()

    print(f"Kursk asset mapping: {kursk_mapping_pct:.1f}%")
    print(f"  ({kursk_mapped} of {len(kursk_assets)} Kursk assets have mappings)")
    print()

    # Portal asset utilization
    portal_utilization = (len(mapping_info['mapped_portal']) / portal_info['total'] * 100) if portal_info['total'] > 0 else 0
    print(f"Portal asset utilization: {portal_utilization:.1f}%")
    print(f"  ({len(mapping_info['mapped_portal'])} of {portal_info['total']} Portal assets used in mappings)")
    print()

    # Priority recommendations
    print("### PRIORITY RECOMMENDATIONS")
    print("-" * 80)
    print()

    priority = 1

    if kursk_not_in_catalog:
        print(f"{priority}. CRITICAL: Add {len(kursk_not_in_catalog)} Kursk vehicle spawner types to BF1942 catalog")
        print(f"   File: tools/asset_audit/bf1942_asset_catalog.json")
        print(f"   Assets: {sorted(kursk_not_in_catalog)}")
        print()
        priority += 1

    if kursk_not_mapped:
        print(f"{priority}. CRITICAL: Create {len(kursk_not_mapped)} Portal mappings for Kursk vehicle spawners")
        print(f"   File: tools/asset_audit/bf1942_to_portal_mappings.json")
        print(f"   Section: spawners")
        print(f"   Assets:")
        for asset in sorted(kursk_not_mapped):
            print(f"     - {asset}")
        print()
        priority += 1

    if kursk_todo:
        print(f"{priority}. HIGH: Complete {len(kursk_todo)} TODO mappings for Kursk assets")
        for asset in sorted(kursk_todo):
            print(f"     - {asset}")
        print()
        priority += 1

    if len(mapping_info['todo_entries']) > len(kursk_todo):
        remaining_todos = len(mapping_info['todo_entries']) - len(kursk_todo)
        print(f"{priority}. MEDIUM: Complete {remaining_todos} remaining TODO entries")
        print()
        priority += 1

    if non_kursk_unmapped:
        print(f"{priority}. LOW: Create mappings for {len(non_kursk_unmapped)} non-Kursk BF1942 assets")
        print()
        priority += 1

    print("=" * 80)
    print()
    print("SUMMARY:")
    print(f"  - {len(kursk_not_in_catalog)} Kursk assets missing from catalog")
    print(f"  - {len(kursk_not_mapped)} Kursk assets missing mappings")
    print(f"  - {len(kursk_todo)} Kursk assets with incomplete mappings")
    print()
    if kursk_not_in_catalog or kursk_not_mapped:
        print("  STATUS: INCOMPLETE - Kursk vehicle spawners not fully mapped")
    else:
        print("  STATUS: COMPLETE - All Kursk assets mapped")
    print("=" * 80)

if __name__ == '__main__':
    main()
