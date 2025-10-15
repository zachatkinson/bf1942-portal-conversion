#!/usr/bin/env python3
"""Vehicle mapping report tool for BF1942 to Portal conversion.

This tool analyzes vehicle mappings and generates reports showing:
- All BF1942 vehicles and their BF6 equivalents
- Vehicles organized by category (Tanks, Aircraft, etc.)
- Coverage statistics for vehicle mapping

Usage:
    python3 tools/portal_vehicle_report.py
    python3 tools/portal_vehicle_report.py --category Tank
    python3 tools/portal_vehicle_report.py --bf6-type Abrams
"""

import argparse
from collections import defaultdict

from bfportal.mappers.vehicle_mapper import VehicleMapper


def print_separator(char: str = "=", length: int = 80) -> None:
    """Print a separator line."""
    print(char * length)


def report_all_mappings(mapper: VehicleMapper) -> None:
    """Generate complete vehicle mapping report.

    Args:
        mapper: Initialized VehicleMapper instance
    """
    print_separator()
    print("BF1942 TO BF6 PORTAL VEHICLE MAPPINGS")
    print_separator()

    mappings = mapper.get_all_mappings()

    print(f"\nTotal Mappings: {len(mappings)}")
    print(f"BF6 Vehicle Types Used: {len(mapper.get_bf6_vehicle_types())}")

    # Group by category
    by_category: dict[str, list[tuple[str, str]]] = defaultdict(list)
    for bf1942_name, mapping in mappings.items():
        by_category[mapping.category].append((bf1942_name, mapping.bf6_vehicle_type))

    # Print by category
    for category in sorted(by_category.keys()):
        vehicles = sorted(by_category[category])
        print(f"\n{'─' * 80}")
        print(f"📦 {category.upper()} ({len(vehicles)} mappings)")
        print(f"{'─' * 80}")

        for bf1942_name, bf6_type in vehicles:
            mapping = mappings[bf1942_name]
            print(f"  {bf1942_name:30s} → {bf6_type:15s} ({mapping.era})")
            if mapping.notes:
                print(f"    ℹ️  {mapping.notes}")

    print_separator()


def report_by_category(mapper: VehicleMapper, category: str) -> None:
    """Generate report for specific vehicle category.

    Args:
        mapper: Initialized VehicleMapper instance
        category: Vehicle category to report on
    """
    print_separator()
    print(f"VEHICLE MAPPINGS: {category.upper()}")
    print_separator()

    mappings = mapper.get_mappings_by_category(category)

    if not mappings:
        print(f"\nNo mappings found for category '{category}'")
        print("\nAvailable categories:")
        all_mappings = mapper.get_all_mappings()
        categories = {m.category for m in all_mappings.values()}
        for cat in sorted(categories):
            print(f"  - {cat}")
        return

    print(f"\nFound {len(mappings)} mappings in category '{category}'")

    for bf1942_name in sorted(mappings.keys()):
        mapping = mappings[bf1942_name]
        print(f"\n{bf1942_name}")
        print(f"  BF6 Type: {mapping.bf6_vehicle_type}")
        print(f"  Era: {mapping.era}")
        print(f"  Category: {mapping.category}")
        if mapping.notes:
            print(f"  Notes: {mapping.notes}")

    print_separator()


def report_bf6_vehicle_type(mapper: VehicleMapper, bf6_type: str) -> None:
    """Show all BF1942 vehicles that map to a specific BF6 type.

    Args:
        mapper: Initialized VehicleMapper instance
        bf6_type: BF6 VehicleType enum value
    """
    print_separator()
    print(f"BF1942 VEHICLES MAPPING TO: {bf6_type}")
    print_separator()

    mappings = mapper.get_all_mappings()
    matching = [
        (name, mapping)
        for name, mapping in mappings.items()
        if mapping.bf6_vehicle_type == bf6_type
    ]

    if not matching:
        print(f"\nNo BF1942 vehicles map to '{bf6_type}'")
        print("\nAvailable BF6 vehicle types:")
        for vtype in mapper.get_bf6_vehicle_types():
            print(f"  - {vtype}")
        return

    print(f"\nFound {len(matching)} BF1942 vehicles mapping to {bf6_type}:")

    # Group by category
    from bfportal.mappers.vehicle_mapper import VehicleMapping

    by_category: dict[str, list[tuple[str, VehicleMapping]]] = defaultdict(list)
    for name, mapping in matching:
        by_category[mapping.category].append((name, mapping))

    for category in sorted(by_category.keys()):
        print(f"\n{category}:")
        for name, mapping in sorted(by_category[category]):
            print(f"  - {name:30s} ({mapping.era})")
            if mapping.notes:
                print(f"    {mapping.notes}")

    print_separator()


def report_coverage(mapper: VehicleMapper) -> None:
    """Generate coverage report showing BF6 vehicle type usage.

    Args:
        mapper: Initialized VehicleMapper instance
    """
    print_separator()
    print("BF6 VEHICLE TYPE COVERAGE")
    print_separator()

    # Count usage of each BF6 type
    usage: dict[str, int] = defaultdict(int)
    mappings = mapper.get_all_mappings()
    for mapping in mappings.values():
        usage[mapping.bf6_vehicle_type] += 1

    # All available BF6 types (from VehicleSpawner.gd enum)
    available_types = [
        "Abrams",
        "Leopard",
        "Cheetah",
        "CV90",
        "Gepard",
        "UH60",
        "Eurocopter",
        "AH64",
        "Vector",
        "Quadbike",
        "Flyer60",
        "JAS39",
        "F22",
        "F16",
        "M2Bradley",
        "SU57",
    ]

    print("\nBF6 VehicleType Usage:")
    print(f"{'Type':15s} {'Count':>8s} {'Bar':>20s}")
    print("─" * 50)

    max_count = max(usage.values()) if usage else 1

    for vtype in sorted(available_types):
        count = usage.get(vtype, 0)
        bar_length = int((count / max_count) * 20) if count > 0 else 0
        bar = "█" * bar_length
        status = "✓" if count > 0 else "✗"
        print(f"{status} {vtype:15s} {count:>5d}    {bar}")

    used = len([v for v in available_types if usage.get(v, 0) > 0])
    print("\n" + "─" * 50)
    print(
        f"Coverage: {used}/{len(available_types)} vehicle types used ({used * 100 // len(available_types)}%)"
    )

    print_separator()


def main() -> None:
    """Main entry point for vehicle mapping report tool."""
    parser = argparse.ArgumentParser(
        description="Generate BF1942 to BF6 Portal vehicle mapping reports"
    )

    parser.add_argument(
        "--category",
        type=str,
        help="Show mappings for specific category (Tank, Fighter, APC, etc.)",
    )

    parser.add_argument(
        "--bf6-type",
        type=str,
        help="Show BF1942 vehicles that map to specific BF6 type (Abrams, Leopard, etc.)",
    )

    parser.add_argument(
        "--coverage", action="store_true", help="Show BF6 vehicle type coverage statistics"
    )

    args = parser.parse_args()

    # Initialize mapper
    mapper = VehicleMapper()

    # Generate requested report
    if args.category:
        report_by_category(mapper, args.category)
    elif args.bf6_type:
        report_bf6_vehicle_type(mapper, args.bf6_type)
    elif args.coverage:
        report_coverage(mapper)
    else:
        # Default: show all mappings
        report_all_mappings(mapper)
        print("\n")
        report_coverage(mapper)


if __name__ == "__main__":
    main()
