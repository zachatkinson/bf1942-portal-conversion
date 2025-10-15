#!/usr/bin/env python3
"""Vehicle type mapper for BF1942 to BF6 Portal conversion.

Single Responsibility: Map BF1942 vehicle types to BF6 Portal VehicleType enum values.

This module provides a mapping system that converts BF1942 vehicle identifiers
(like "PanzerIV", "Sherman", "T34") to corresponding BF6 Portal VehicleType
enum values (like "Leopard", "Abrams", "M2Bradley").

MAPPING CONVENTION (applies to all BF1942 maps):
================================================
    Axis powers → non-NATO assets (Leopard, Eurocopter, SU57)
    Allied powers → NATO/American assets (Abrams, F16, AH64)

This ensures consistent faction alignment across all theaters (Europe, Pacific, Africa):
    - German, Italian, Japanese vehicles → non-NATO modern equivalents
    - American, British, Soviet vehicles → NATO/American modern equivalents

The BF1942Engine automatically swaps teams so:
    - BF1942 Team 1 (Axis) → Portal Team 2 (non-NATO)
    - BF1942 Team 2 (Allied) → Portal Team 1 (NATO/American)
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
        # Convention: Axis → non-NATO (Leopard), Allied → NATO (Abrams)

        # German Tanks (Axis) → Leopard (non-NATO)
        german_tanks = [
            "PanzerIV",
            "Panzer4",
            "panzeriv",
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
                notes="German WW2 tank (Axis) → Leopard 2 (non-NATO)",
            )

        # American Tanks (Allied) → Abrams (NATO)
        american_tanks = [
            "Sherman",
            "sherman",
            "ShermanTank",
            "M4Sherman",
            "M4A3",
            "M10",
            "m10",
            "M10Wolverine",
        ]
        for tank in american_tanks:
            mappings[tank] = VehicleMapping(
                bf1942_name=tank,
                bf6_vehicle_type="Abrams",
                era="WW2",
                category="Tank",
                notes="American WW2 tank (Allied) → M1 Abrams (NATO)",
            )

        # Soviet Tanks (Allied) → Abrams (NATO)
        soviet_tanks = [
            "T34",
            "T-34",
            "T3485",
            "T34-85",
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
                notes="Soviet WW2 tank (Allied) → M1 Abrams (NATO)",
            )

        # British Tanks (Allied) → Abrams (NATO)
        british_tanks = [
            "Churchill",
            "ChurchillTank",
            "Crusader",
        ]
        for tank in british_tanks:
            mappings[tank] = VehicleMapping(
                bf1942_name=tank,
                bf6_vehicle_type="Abrams",
                era="WW2",
                category="Tank",
                notes="British WW2 tank (Allied) → M1 Abrams (NATO)",
            )

        # Japanese Tanks (Axis) → Leopard (non-NATO)
        japanese_tanks = [
            "TypeChiHa",
            "Chi-Ha",
            "chi-ha",
            "Type97",
        ]
        for tank in japanese_tanks:
            mappings[tank] = VehicleMapping(
                bf1942_name=tank,
                bf6_vehicle_type="Leopard",
                era="WW2",
                category="Tank",
                notes="Japanese light WW2 tank (Axis) → Leopard 2 (non-NATO)",
            )

        # ========================================
        # TANK DESTROYERS & ASSAULT GUNS
        # ========================================

        # German TD/assault guns (Axis) → CV90 (non-NATO)
        german_td = [
            "StuG",
            "StuG3",
            "StuGIII",
            "SturmGeschutz",
            "sturmgeschutz",
            "Wespe",
            "wespe",
        ]
        for td in german_td:
            mappings[td] = VehicleMapping(
                bf1942_name=td,
                bf6_vehicle_type="CV90",
                era="WW2",
                category="Tank Destroyer",
                notes="German assault gun/TD (Axis) → CV90 (non-NATO)",
            )

        # American SPG (Allied) → M2Bradley (NATO)
        american_td = [
            "Priest",
            "M7Priest",
            "Sexton",
        ]
        for td in american_td:
            mappings[td] = VehicleMapping(
                bf1942_name=td,
                bf6_vehicle_type="M2Bradley",
                era="WW2",
                category="SPG",
                notes="American self-propelled gun (Allied) → M2Bradley (NATO)",
            )

        # ========================================
        # WHEELED VEHICLES & TRANSPORTS
        # ========================================

        # Jeeps & Light Vehicles → Quadbike
        light_vehicles = [
            "Willys",
            "Willy",
            "willy",
            "WillysMB",
            "Jeep",
            "Kubelwagen",
            "kubelwagen",
            "GAZ",
            "GAZ67",
            "Greyhound",
            "greyhound",
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
            "hanomag",
            "M3",
            "M3A1",
            "m3a1",
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
            "flak38",
            "Flak36",
            "Flak88",
            "WirbelWind",
            "Flakpanzer",
            "FlakPanzer",
            "flakpanzer",
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
        # Convention: Axis → non-NATO, Allied → NATO
        # Dive bombers map to attack helicopters for modern ground attack role

        # Axis Dive Bombers (German) → Eurocopter (non-NATO)
        axis_bombers = [
            "Ju87",
            "Stuka",
            "stuka",
            "Ju88",
            "Ju88A",
        ]
        for aircraft in axis_bombers:
            mappings[aircraft] = VehicleMapping(
                bf1942_name=aircraft,
                bf6_vehicle_type="Eurocopter",
                era="WW2",
                category="Dive Bomber",
                notes="Axis dive bomber → Eurocopter Tiger (non-NATO)",
            )

        # Allied Dive Bombers (Soviet) → AH64 Apache (NATO/American)
        allied_bombers = [
            "IL2",
            "IL-2",
            "Ilyushin",
            "Sturmovik",
        ]
        for aircraft in allied_bombers:
            mappings[aircraft] = VehicleMapping(
                bf1942_name=aircraft,
                bf6_vehicle_type="AH64",
                era="WW2",
                category="Dive Bomber",
                notes="Allied dive bomber → AH-64 Apache (NATO/American)",
            )

        # Allied Heavy Bombers → F16 (NATO/American)
        heavy_bombers = [
            "B17",
            "b17",
            "B-17",
            "Lancaster",
        ]
        for bomber in heavy_bombers:
            mappings[bomber] = VehicleMapping(
                bf1942_name=bomber,
                bf6_vehicle_type="F16",
                era="WW2",
                category="Bomber",
                notes="WW2 strategic bomber (Allied) → F-16 (NATO/American)",
            )

        # ========================================
        # AIRCRAFT - FIGHTERS
        # ========================================
        # Convention: Axis → non-NATO (SU57), Allied → NATO (F16)

        # Axis Fighters (German, Japanese) → SU57 (non-NATO)
        axis_fighters = [
            "BF109",
            "Bf109",
            "bf109",
            "Me109",
            "Messerschmitt",
            "FW190",
            "Focke-Wulf",
            "bf110",
            "Zero",
            "zero",
            "A6M",
        ]
        for fighter in axis_fighters:
            mappings[fighter] = VehicleMapping(
                bf1942_name=fighter,
                bf6_vehicle_type="SU57",
                era="WW2",
                category="Fighter",
                notes="Axis fighter → SU-57 (non-NATO)",
            )

        # Allied Fighters → F16 (NATO/American)
        allied_fighters = [
            "P51",
            "P-51",
            "Mustang",
            "mustang",
            "Spitfire",
            "spitfire",
            "Yak9",
            "yak9",
            "Yak-9",
            "jak9",
            "Corsair",
            "corsair",
        ]
        for fighter in allied_fighters:
            mappings[fighter] = VehicleMapping(
                bf1942_name=fighter,
                bf6_vehicle_type="F16",
                era="WW2",
                category="Fighter",
                notes="Allied fighter → F-16 (NATO/American)",
            )

        # ========================================
        # TRANSPORT AIRCRAFT & HELICOPTERS
        # ========================================
        # Convention: Axis → non-NATO (Eurocopter), Allied → NATO (UH60)

        # Allied Transport Aircraft → UH60 (NATO)
        allied_transports = [
            "C47",
            "c47",
            "Dakota",
            "SBD",
            "sbd",
            "Dauntless",
        ]
        for transport in allied_transports:
            mappings[transport] = VehicleMapping(
                bf1942_name=transport,
                bf6_vehicle_type="UH60",
                era="WW2",
                category="Transport Aircraft",
                notes="Allied transport aircraft → UH-60 Black Hawk (NATO)",
            )

        # German Transport/Recon Aircraft → Eurocopter (non-NATO)
        axis_transports = [
            "Fi156",
            "fi156",
            "Storch",
            "Flettner",
            "flettner",
        ]
        for transport in axis_transports:
            mappings[transport] = VehicleMapping(
                bf1942_name=transport,
                bf6_vehicle_type="Eurocopter",
                era="WW2",
                category="Transport Aircraft",
                notes="Axis transport/recon aircraft → Eurocopter Tiger (non-NATO)",
            )

        # ========================================
        # EXPERIMENTAL & SECRET WEAPONS
        # ========================================
        # Convention: Axis → non-NATO, Allied → NATO

        # Axis Experimental Aircraft → SU57 (non-NATO)
        axis_experimental = [
            "Natter",
            "natter",
            "HO229",
            "ho229",
            "Ho229",
            "Me163",
            "me163",
            "Komet",
            "V2",
            "v2",
        ]
        for experimental in axis_experimental:
            mappings[experimental] = VehicleMapping(
                bf1942_name=experimental,
                bf6_vehicle_type="SU57",
                era="WW2",
                category="Experimental Aircraft",
                notes="Axis experimental/rocket aircraft → SU-57 (non-NATO)",
            )

        # Allied Experimental Aircraft → F16 (NATO)
        allied_experimental = [
            "Goblin",
            "goblin",
            "XF85",
            "xf85",
            "AW52",
            "aw52",
        ]
        for experimental in allied_experimental:
            mappings[experimental] = VehicleMapping(
                bf1942_name=experimental,
                bf6_vehicle_type="F16",
                era="WW2",
                category="Experimental Aircraft",
                notes="Allied experimental aircraft → F-16 (NATO/American)",
            )

        # ========================================
        # ARTILLERY & STATIONARY WEAPONS
        # ========================================
        # These don't convert to vehicles, but map them for completeness

        # Axis Artillery → Gepard (closest available)
        axis_artillery = [
            "Wespe",
            "wespe",
            "Nebelwerfer",
            "nebelwerfer",
            "Wasserfall",
            "wasserfall",
            "Flak36",
            "flak36",
            "Flak88",
            "flak88",
            "PAK40",
            "pak40",
        ]
        for arty in axis_artillery:
            mappings[arty] = VehicleMapping(
                bf1942_name=arty,
                bf6_vehicle_type="Gepard",
                era="WW2",
                category="Artillery",
                notes="Axis artillery/AA → Gepard SPAAG (non-NATO, stationary weapons unsupported)",
            )

        # Allied Artillery → Gepard (closest available)
        allied_artillery = [
            "Katyusha",
            "katyusha",
            "Priest",
            "priest",
            "Sexton",
            "sexton",
        ]
        for arty in allied_artillery:
            mappings[arty] = VehicleMapping(
                bf1942_name=arty,
                bf6_vehicle_type="M2Bradley",
                era="WW2",
                category="Artillery",
                notes="Allied artillery/SPG → M2Bradley (NATO, mobile fire support)",
            )

        # ========================================
        # NAVAL - CAPITAL SHIPS
        # ========================================
        # Large ships don't have Portal equivalents - map to hovercraft as placeholder
        # Convention: Axis → non-NATO themed, Allied → NATO themed

        # Axis Capital Ships → Flyer60 (placeholder)
        axis_capital_ships = [
            "Tirpitz",
            "tirpitz",
            "Bismarck",
            "bismarck",
            "Yamato",
            "yamato",
            "Shokaku",
            "shokaku",
            "Akagi",
            "akagi",
        ]
        for ship in axis_capital_ships:
            mappings[ship] = VehicleMapping(
                bf1942_name=ship,
                bf6_vehicle_type="Flyer60",
                era="WW2",
                category="Naval - Capital Ship",
                notes="Axis capital ship → Flyer60 hovercraft (PLACEHOLDER - capital ships not supported)",
            )

        # Allied Capital Ships → Flyer60 (placeholder)
        allied_capital_ships = [
            "Enterprise",
            "enterprise",
            "Lexington",
            "lexington",
            "PrinceOfWales",
            "princeofwales",
            "Missouri",
            "missouri",
        ]
        for ship in allied_capital_ships:
            mappings[ship] = VehicleMapping(
                bf1942_name=ship,
                bf6_vehicle_type="Flyer60",
                era="WW2",
                category="Naval - Capital Ship",
                notes="Allied capital ship → Flyer60 hovercraft (PLACEHOLDER - capital ships not supported)",
            )

        # ========================================
        # NAVAL - DESTROYERS & CRUISERS
        # ========================================

        # Axis Destroyers → Flyer60
        axis_destroyers = [
            "Hatsuzuki",
            "hatsuzuki",
            "Fletcher",
            "fletcher",
        ]
        for ship in axis_destroyers:
            mappings[ship] = VehicleMapping(
                bf1942_name=ship,
                bf6_vehicle_type="Flyer60",
                era="WW2",
                category="Naval - Destroyer",
                notes="Axis destroyer → Flyer60 hovercraft (placeholder)",
            )

        # Allied Destroyers → Flyer60
        allied_destroyers = [
            "Gato",
            "gato",
            "Type93",
            "type93",
        ]
        for ship in allied_destroyers:
            mappings[ship] = VehicleMapping(
                bf1942_name=ship,
                bf6_vehicle_type="Flyer60",
                era="WW2",
                category="Naval - Destroyer",
                notes="Allied destroyer/submarine → Flyer60 hovercraft (placeholder)",
            )

        # ========================================
        # NAVAL - LANDING CRAFT & SMALL BOATS
        # ========================================

        landing_craft = [
            "LandingCraft",
            "LCVP",
            "lcvp",
            "Higgins",
            "DUKW",
            "dukw",
            "Daihatsu",
            "daihatsu",
            "LCM",
            "lcm",
            "LVT",
            "lvt",
        ]
        for boat in landing_craft:
            mappings[boat] = VehicleMapping(
                bf1942_name=boat,
                bf6_vehicle_type="Flyer60",
                era="WW2",
                category="Naval - Landing Craft",
                notes="WW2 landing craft → Modern Flyer60 hovercraft",
            )

        # ========================================
        # MOTORCYCLES & BICYCLES
        # ========================================

        motorcycles = [
            "Motorcycle",
            "motorcycle",
            "R75",
            "r75",
            "Zundapp",
            "zundapp",
            "Bicycle",
            "bicycle",
        ]
        for cycle in motorcycles:
            mappings[cycle] = VehicleMapping(
                bf1942_name=cycle,
                bf6_vehicle_type="Quadbike",
                era="WW2",
                category="Motorcycle",
                notes="WW2 motorcycle/bicycle → Modern quadbike",
            )

        # ========================================
        # SPECIAL STRUCTURES & OBJECTS
        # ========================================
        # These aren't vehicles but appear in spawner templates
        # Map to closest available vehicle type

        special_objects = [
            "DefGun",
            "defgun",
            "AAGun",
            "aagun",
            "Radar",
            "radar",
            "Factory",
            "factory",
            "ControlTower",
            "controltower",
        ]
        for obj in special_objects:
            mappings[obj] = VehicleMapping(
                bf1942_name=obj,
                bf6_vehicle_type="Gepard",
                era="WW2",
                category="Special Structure",
                notes="WW2 special structure → Gepard (placeholder - structures not supported as vehicles)",
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
