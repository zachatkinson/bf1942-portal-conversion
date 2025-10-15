#!/usr/bin/env python3
"""Vehicle type mapper for BF1942 to BF6 Portal conversion.

Single Responsibility: Map BF1942 vehicle types to BF6 Portal VehicleType enum values.

This module provides a mapping system that converts BF1942 vehicle identifiers
(like "PanzerIV", "Sherman", "T34") to corresponding BF6 Portal VehicleType
enum values (like "Leopard", "Abrams", "M2Bradley").
"""

from dataclasses import dataclass


@dataclass
class VehicleMapping:
    """Represents a mapping from BF1942 vehicle to BF6 VehicleType.

    Attributes:
        bf1942_name: Original BF1942 vehicle identifier
        bf6_vehicle_type: BF6 Portal VehicleType enum value
        era: Historical era (WW2, Modern)
        category: Vehicle category (Tank, APC, Aircraft, etc.)
        notes: Additional mapping notes
    """

    bf1942_name: str
    bf6_vehicle_type: str
    era: str
    category: str
    notes: str = ""


class VehicleMapper:
    """Maps BF1942 vehicles to BF6 Portal VehicleType enum values.

    Single Responsibility: Provide vehicle type lookups for conversion.

    BF6 Available Vehicle Types (from VehicleSpawner.gd):
    - Abrams (M1 Abrams tank)
    - Leopard (Leopard 2 tank)
    - Cheetah (Light vehicle)
    - CV90 (Combat Vehicle 90 - IFV)
    - Gepard (Anti-air vehicle)
    - UH60 (Black Hawk helicopter)
    - Eurocopter (Tiger helicopter)
    - AH64 (Apache helicopter)
    - Vector (Transport vehicle)
    - Quadbike (Light transport)
    - Flyer60 (Hovercraft)
    - JAS39 (Gripen fighter jet)
    - F22 (Raptor fighter jet)
    - F16 (Fighting Falcon jet)
    - M2Bradley (Bradley IFV)
    - SU57 (Russian fighter jet)
    """

    def __init__(self):
        """Initialize vehicle mapper with BF1942 to BF6 mappings."""
        self._mappings = self._build_mappings()

    def _build_mappings(self) -> dict[str, VehicleMapping]:
        """Build complete BF1942 to BF6 vehicle mapping table.

        Returns:
            Dictionary mapping BF1942 vehicle names to VehicleMapping objects
        """
        mappings: dict[str, VehicleMapping] = {}

        # ========================================
        # TANKS - Heavy Armor
        # ========================================

        # German Tanks → Leopard
        german_tanks = [
            "PanzerIV",
            "Panzer4",
            "PanzerVI",
            "Tiger",
            "TigerTank",
            "PanzerV",
            "Panther",
        ]
        for tank in german_tanks:
            mappings[tank] = VehicleMapping(
                bf1942_name=tank,
                bf6_vehicle_type="Leopard",
                era="WW2",
                category="Tank",
                notes="German WW2 tank → Modern German Leopard 2",
            )

        # American Tanks → Abrams
        american_tanks = [
            "Sherman",
            "ShermanTank",
            "M4Sherman",
            "M4A3",
            "M10",
            "M10Wolverine",
        ]
        for tank in american_tanks:
            mappings[tank] = VehicleMapping(
                bf1942_name=tank,
                bf6_vehicle_type="Abrams",
                era="WW2",
                category="Tank",
                notes="American WW2 tank → Modern American M1 Abrams",
            )

        # Soviet Tanks → Abrams (closest equivalent)
        soviet_tanks = [
            "T34",
            "T-34",
            "T3485",
            "T-34-85",
            "KV1",
            "KV-1",
        ]
        for tank in soviet_tanks:
            mappings[tank] = VehicleMapping(
                bf1942_name=tank,
                bf6_vehicle_type="Abrams",
                era="WW2",
                category="Tank",
                notes="Soviet WW2 tank → Modern M1 Abrams",
            )

        # British Tanks → Leopard
        british_tanks = [
            "Churchill",
            "ChurchillTank",
            "Crusader",
        ]
        for tank in british_tanks:
            mappings[tank] = VehicleMapping(
                bf1942_name=tank,
                bf6_vehicle_type="Leopard",
                era="WW2",
                category="Tank",
                notes="British WW2 tank → Modern Leopard 2",
            )

        # Japanese Tanks → Cheetah (lighter tanks)
        japanese_tanks = [
            "TypeChiHa",
            "Chi-Ha",
            "Type97",
        ]
        for tank in japanese_tanks:
            mappings[tank] = VehicleMapping(
                bf1942_name=tank,
                bf6_vehicle_type="Cheetah",
                era="WW2",
                category="Tank",
                notes="Japanese light WW2 tank → Light modern vehicle",
            )

        # ========================================
        # TANK DESTROYERS & ASSAULT GUNS
        # ========================================

        german_td = [
            "StuG",
            "StuG3",
            "StuGIII",
            "Wespe",
        ]
        for td in german_td:
            mappings[td] = VehicleMapping(
                bf1942_name=td,
                bf6_vehicle_type="CV90",
                era="WW2",
                category="Tank Destroyer",
                notes="German assault gun/TD → Modern IFV",
            )

        american_td = [
            "Priest",
            "M7Priest",
        ]
        for td in american_td:
            mappings[td] = VehicleMapping(
                bf1942_name=td,
                bf6_vehicle_type="M2Bradley",
                era="WW2",
                category="SPG",
                notes="American self-propelled gun → Modern Bradley IFV",
            )

        # ========================================
        # WHEELED VEHICLES & TRANSPORTS
        # ========================================

        # Jeeps & Light Vehicles → Quadbike
        light_vehicles = [
            "Willys",
            "WillysMB",
            "Jeep",
            "Kubelwagen",
            "GAZ",
            "GAZ67",
        ]
        for vehicle in light_vehicles:
            mappings[vehicle] = VehicleMapping(
                bf1942_name=vehicle,
                bf6_vehicle_type="Quadbike",
                era="WW2",
                category="Light Vehicle",
                notes="WW2 light vehicle → Modern quadbike",
            )

        # APCs & Halftracks → Vector
        apcs = [
            "Hanomag",
            "M3",
            "M3A1",
            "Halftrack",
        ]
        for apc in apcs:
            mappings[apc] = VehicleMapping(
                bf1942_name=apc,
                bf6_vehicle_type="Vector",
                era="WW2",
                category="APC",
                notes="WW2 halftrack/APC → Modern Vector transport",
            )

        # ========================================
        # ANTI-AIRCRAFT
        # ========================================

        aa_vehicles = [
            "Flak38",
            "Flak36",
            "Flak88",
            "WirbelWind",
            "M16",
            "M16AAA",
        ]
        for aa in aa_vehicles:
            mappings[aa] = VehicleMapping(
                bf1942_name=aa,
                bf6_vehicle_type="Gepard",
                era="WW2",
                category="Anti-Air",
                notes="WW2 AA vehicle → Modern Gepard SPAAG",
            )

        # ========================================
        # AIRCRAFT - DIVE BOMBERS → ATTACK HELICOPTERS
        # ========================================
        # User preference: Dive bombers (Stuka, IL-2) map to attack helicopters
        # for modern ground attack role

        # Axis Dive Bombers → Eurocopter (non-NATO attack heli)
        axis_bombers = [
            "Ju87",
            "Stuka",
            "Ju88",
        ]
        for aircraft in axis_bombers:
            mappings[aircraft] = VehicleMapping(
                bf1942_name=aircraft,
                bf6_vehicle_type="Eurocopter",
                era="WW2",
                category="Dive Bomber",
                notes="Axis WW2 dive bomber → Modern Eurocopter Tiger (non-NATO attack heli)",
            )

        # Soviet Dive Bombers → AH64 Apache (NATO attack heli)
        soviet_bombers = [
            "IL2",
            "IL-2",
            "Ilyushin",
            "Sturmovik",
        ]
        for aircraft in soviet_bombers:
            mappings[aircraft] = VehicleMapping(
                bf1942_name=aircraft,
                bf6_vehicle_type="AH64",
                era="WW2",
                category="Dive Bomber",
                notes="Soviet WW2 dive bomber → Modern AH-64 Apache (NATO attack heli)",
            )

        # Allied Bombers → JAS39/F16 (prefer ground attack role)
        allied_bombers = [
            "B17",
            "B-17",
            "Lancaster",
        ]
        for bomber in allied_bombers:
            mappings[bomber] = VehicleMapping(
                bf1942_name=bomber,
                bf6_vehicle_type="JAS39",
                era="WW2",
                category="Bomber",
                notes="WW2 strategic bomber → Modern JAS39 multirole",
            )

        # ========================================
        # AIRCRAFT - FIGHTERS (Keep for maps with pure fighters)
        # ========================================

        # Axis Fighters → F16 (prefer multirole)
        axis_fighters = [
            "BF109",
            "Bf109",
            "Me109",
            "Messerschmitt",
            "FW190",
            "Focke-Wulf",
            "Zero",
            "A6M",
        ]
        for fighter in axis_fighters:
            mappings[fighter] = VehicleMapping(
                bf1942_name=fighter,
                bf6_vehicle_type="F16",
                era="WW2",
                category="Fighter",
                notes="Axis WW2 fighter → Modern F-16 multirole (better for ground attack)",
            )

        # Allied Fighters → JAS39/F16
        allied_fighters = [
            "P51",
            "P-51",
            "Mustang",
            "Spitfire",
            "Yak9",
            "Yak-9",
        ]
        for i, fighter in enumerate(allied_fighters):
            # Alternate between JAS39 and F16 for variety
            vehicle_type = "JAS39" if i % 2 == 0 else "F16"
            mappings[fighter] = VehicleMapping(
                bf1942_name=fighter,
                bf6_vehicle_type=vehicle_type,
                era="WW2",
                category="Fighter",
                notes=f"Allied WW2 fighter → Modern {vehicle_type} multirole",
            )

        # ========================================
        # HELICOPTERS
        # ========================================
        # BF1942 had no helicopters, but we can add attack helis for modern gameplay

        # Attack Helicopters (for custom/modern variants)
        attack_helis = [
            "AttackHeli",
            "Apache",
            "AH64",
        ]
        for heli in attack_helis:
            mappings[heli] = VehicleMapping(
                bf1942_name=heli,
                bf6_vehicle_type="AH64",
                era="Modern",
                category="Attack Helicopter",
                notes="Attack helicopter → AH-64 Apache",
            )

        # Transport Helicopters
        transport_helis = [
            "TransportHeli",
            "BlackHawk",
            "UH60",
        ]
        for heli in transport_helis:
            mappings[heli] = VehicleMapping(
                bf1942_name=heli,
                bf6_vehicle_type="UH60",
                era="Modern",
                category="Transport Helicopter",
                notes="Transport helicopter → UH-60 Black Hawk",
            )

        # ========================================
        # BOATS & NAVAL
        # ========================================

        boats = [
            "LandingCraft",
            "LCVP",
            "Higgins",
            "DUKW",
        ]
        for boat in boats:
            mappings[boat] = VehicleMapping(
                bf1942_name=boat,
                bf6_vehicle_type="Flyer60",
                era="WW2",
                category="Naval",
                notes="WW2 landing craft → Modern hovercraft",
            )

        return mappings

    def map_vehicle(self, bf1942_vehicle_name: str) -> str | None:
        """Map BF1942 vehicle name to BF6 VehicleType enum value.

        Args:
            bf1942_vehicle_name: BF1942 vehicle identifier

        Returns:
            BF6 VehicleType enum value (e.g., "Abrams", "Leopard"), or None if unmapped

        Examples:
            >>> mapper = VehicleMapper()
            >>> mapper.map_vehicle("Sherman")
            'Abrams'
            >>> mapper.map_vehicle("PanzerIV")
            'Leopard'
            >>> mapper.map_vehicle("UnknownVehicle")
            None
        """
        # Try exact match first
        if bf1942_vehicle_name in self._mappings:
            return self._mappings[bf1942_vehicle_name].bf6_vehicle_type

        # Try case-insensitive partial match
        name_lower = bf1942_vehicle_name.lower()
        for key, mapping in self._mappings.items():
            if key.lower() in name_lower or name_lower in key.lower():
                return mapping.bf6_vehicle_type

        return None

    def get_mapping_info(self, bf1942_vehicle_name: str) -> VehicleMapping | None:
        """Get complete mapping information for a BF1942 vehicle.

        Args:
            bf1942_vehicle_name: BF1942 vehicle identifier

        Returns:
            VehicleMapping object with full details, or None if unmapped
        """
        if bf1942_vehicle_name in self._mappings:
            return self._mappings[bf1942_vehicle_name]
        return None

    def get_all_mappings(self) -> dict[str, VehicleMapping]:
        """Get all vehicle mappings.

        Returns:
            Dictionary of all BF1942 to BF6 vehicle mappings
        """
        return self._mappings.copy()

    def get_supported_bf1942_vehicles(self) -> list[str]:
        """Get list of all supported BF1942 vehicle names.

        Returns:
            Sorted list of BF1942 vehicle identifiers
        """
        return sorted(self._mappings.keys())

    def get_bf6_vehicle_types(self) -> list[str]:
        """Get list of all BF6 VehicleType enum values used in mappings.

        Returns:
            Sorted list of unique BF6 VehicleType values
        """
        types = {mapping.bf6_vehicle_type for mapping in self._mappings.values()}
        return sorted(types)

    def get_mappings_by_category(self, category: str) -> dict[str, VehicleMapping]:
        """Get all mappings for a specific category.

        Args:
            category: Vehicle category (e.g., "Tank", "Fighter", "APC")

        Returns:
            Dictionary of mappings matching the category
        """
        return {
            name: mapping
            for name, mapping in self._mappings.items()
            if mapping.category.lower() == category.lower()
        }
