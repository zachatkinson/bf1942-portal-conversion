# Vehicle Mapping System - Extensibility Guide

**Purpose**: Document how to extend vehicle mappings when BF6 Portal adds new vehicle types or when converting maps from other Battlefield eras.

**Last Updated**: 2025-10-15
**Author**: Zach Atkinson
**AI Assistant**: Claude (Anthropic)

---

## Architecture Overview

Our vehicle mapping system follows **SOLID principles** for maximum extensibility:

### Single Responsibility Principle
- `vehicle_mapper.py` - ONLY handles BF1942 → BF6 mapping
- `gameplay.py` - ONLY defines BF6 VehicleType enum
- `vehicle_spawner_generator.py` - ONLY generates .tscn nodes
- Future: `vietnam_vehicle_mapper.py`, `bf2_vehicle_mapper.py`, etc.

### Open/Closed Principle
- `VehicleMapper` class is **open for extension** (create subclasses for new eras)
- Mapping logic is **closed for modification** (base behavior doesn't change)

### Liskov Substitution Principle
- All vehicle mappers implement same interface: `map_vehicle(old_name: str) -> str | None`
- Any mapper can be swapped without breaking code

### Interface Segregation Principle
- Mappers expose only what's needed: `map_vehicle()`, `get_mapping_info()`, `get_all_mappings()`
- Generators don't depend on mapper internals

### Dependency Inversion Principle
- High-level code depends on abstract mapper interface
- Low-level mappers implement the interface

---

## Current System Components

### 1. BF6 Vehicle Type Enum (`gameplay.py`)

**Single Source of Truth** for all available BF6 vehicles:

```python
BF6_VEHICLE_TYPE_ENUM = {
    "Abrams": 0,
    "Leopard": 1,
    "Cheetah": 2,
    "CV90": 3,
    "Gepard": 4,
    "UH60": 5,
    "Eurocopter": 6,
    "AH64": 7,
    "Vector": 8,
    "Quadbike": 9,
    "Flyer60": 10,
    "JAS39": 11,
    "F22": 12,
    "F16": 13,
    "M2Bradley": 14,
    "SU57": 15,
}
```

**To Add New BF6 Vehicle**:
1. Update this enum when Portal adds new vehicle
2. All mappers automatically gain access
3. Update mappings to use new vehicle type

### 2. Vehicle Mapper (`vehicle_mapper.py`)

**BF1942-specific mapper** with 81 vehicles → 15 BF6 types:

```python
class VehicleMapper:
    """Maps BF1942 vehicles to BF6 Portal VehicleType enum values."""

    def map_vehicle(self, bf1942_vehicle_name: str) -> str | None:
        """Map BF1942 vehicle name to BF6 VehicleType enum value."""

    def get_mapping_info(self, bf1942_vehicle_name: str) -> VehicleMapping | None:
        """Get complete mapping information for a BF1942 vehicle."""

    def get_all_mappings(self) -> dict[str, VehicleMapping]:
        """Get all vehicle mappings."""
```

**Key Features**:
- Faction-aware: Axis → non-NATO, Allied → NATO
- Era-tagged: All WW2 vehicles documented
- Category-organized: Tank, Fighter, Bomber, etc.
- Extensible: Easy to add new BF1942 vehicles

### 3. Vehicle Spawner Generator (`vehicle_spawner_generator.py`)

**Era-agnostic generator** that works with ANY mapper:

```python
class VehicleSpawnerGenerator(BaseNodeGenerator):
    def __init__(self):
        self.vehicle_mapper = VehicleMapper()  # Could be any mapper

    def generate(self, map_data, asset_registry, transform_formatter):
        # Works with any vehicle mapper that implements map_vehicle()
        bf6_vehicle_type = self.vehicle_mapper.map_vehicle(bf1942_vehicle)
        if bf6_vehicle_type and bf6_vehicle_type in BF6_VEHICLE_TYPE_ENUM:
            enum_index = BF6_VEHICLE_TYPE_ENUM[bf6_vehicle_type]
            # Generate node...
```

---

## Extension Scenarios

### Scenario 1: BF6 Portal Adds New Vehicle Types

**Example**: Portal adds "T90" (Russian tank), "Challenger2" (British tank), "Type99" (Chinese tank)

**Steps**:

1. **Update `gameplay.py`** with new enum values:

```python
BF6_VEHICLE_TYPE_ENUM = {
    # Existing vehicles...
    "SU57": 15,
    # New vehicles
    "T90": 16,         # Russian MBT
    "Challenger2": 17, # British MBT
    "Type99": 18,      # Chinese MBT
}
```

2. **Update `vehicle_mapper.py`** with better mappings:

```python
# NOW we can map Soviet tanks to T90 instead of Abrams
soviet_tanks = ["T34", "T-34", "T3485", "T-34-85", "KV1", "KV-1"]
for tank in soviet_tanks:
    mappings[tank] = VehicleMapping(
        bf1942_name=tank,
        bf6_vehicle_type="T90",  # ← Changed from "Abrams"
        era="WW2",
        category="Tank",
        notes="Soviet WW2 tank → T-90 (Russian modern)",
    )

# British tanks can now use Challenger2
british_tanks = ["Churchill", "ChurchillTank", "Crusader"]
for tank in british_tanks:
    mappings[tank] = VehicleMapping(
        bf1942_name=tank,
        bf6_vehicle_type="Challenger2",  # ← Changed from "Abrams"
        era="WW2",
        category="Tank",
        notes="British WW2 tank → Challenger 2",
    )
```

3. **No other changes needed** - generator automatically uses new mappings

**Time Estimate**: 15-30 minutes

---

### Scenario 2: Convert BF Vietnam Maps

**Example**: User wants to convert BF Vietnam (1960s-1970s era) to Portal

**Steps**:

1. **Create new mapper** `vietnam_vehicle_mapper.py`:

```python
#!/usr/bin/env python3
"""Vehicle type mapper for BF Vietnam to BF6 Portal conversion.

Single Responsibility: Map BF Vietnam vehicle types to BF6 Portal VehicleType enum values.

MAPPING CONVENTION:
==================
    North Vietnam (NVA/VC) → non-NATO assets (Eurocopter, SU57)
    South Vietnam/US → NATO assets (AH64, F16, Abrams)
"""

from dataclasses import dataclass
from typing import Dict

@dataclass
class VehicleMapping:
    """Represents a mapping from BF Vietnam vehicle to BF6 VehicleType."""
    bfvietnam_name: str
    bf6_vehicle_type: str
    era: str
    category: str
    notes: str = ""


class VietnamVehicleMapper:
    """Maps BF Vietnam vehicles to BF6 Portal VehicleType enum values.

    BF Vietnam Vehicle Examples:
    - UH1 Huey → UH60 (transport helicopter)
    - AH1 Cobra → AH64 (attack helicopter)
    - M48 Patton → Abrams (US tank)
    - T54 → Leopard or T90 (NVA tank)
    - Mi8 Hip → Eurocopter (NVA transport)
    - MiG21 → SU57 (NVA fighter)
    - F4 Phantom → F16 (US fighter)
    """

    def __init__(self):
        """Initialize vehicle mapper with BF Vietnam to BF6 mappings."""
        self._mappings = self._build_mappings()

    def _build_mappings(self) -> Dict[str, VehicleMapping]:
        """Build complete BF Vietnam to BF6 vehicle mapping table."""
        mappings: Dict[str, VehicleMapping] = {}

        # ========================================
        # HELICOPTERS (Vietnam-specific)
        # ========================================

        # US Transport Helicopters → UH60
        us_transport_helis = ["UH1", "UH-1", "Huey", "CH47", "Chinook"]
        for heli in us_transport_helis:
            mappings[heli] = VehicleMapping(
                bfvietnam_name=heli,
                bf6_vehicle_type="UH60",
                era="Vietnam",
                category="Transport Helicopter",
                notes="US transport helicopter → UH-60 Black Hawk"
            )

        # US Attack Helicopters → AH64
        us_attack_helis = ["AH1", "AH-1", "Cobra"]
        for heli in us_attack_helis:
            mappings[heli] = VehicleMapping(
                bfvietnam_name=heli,
                bf6_vehicle_type="AH64",
                era="Vietnam",
                category="Attack Helicopter",
                notes="US attack helicopter → AH-64 Apache"
            )

        # NVA Helicopters → Eurocopter
        nva_helis = ["Mi8", "Mi-8", "Hip"]
        for heli in nva_helis:
            mappings[heli] = VehicleMapping(
                bfvietnam_name=heli,
                bf6_vehicle_type="Eurocopter",
                era="Vietnam",
                category="Transport Helicopter",
                notes="NVA transport helicopter → Eurocopter Tiger"
            )

        # ========================================
        # TANKS
        # ========================================

        # US Tanks → Abrams
        us_tanks = ["M48", "M48Patton", "M551", "Sheridan"]
        for tank in us_tanks:
            mappings[tank] = VehicleMapping(
                bfvietnam_name=tank,
                bf6_vehicle_type="Abrams",
                era="Vietnam",
                category="Tank",
                notes="US Vietnam tank → M1 Abrams"
            )

        # NVA Tanks → Leopard (or T90 if available)
        nva_tanks = ["T54", "T-54", "PT76"]
        for tank in nva_tanks:
            mappings[tank] = VehicleMapping(
                bfvietnam_name=tank,
                bf6_vehicle_type="Leopard",  # Or "T90" if Portal adds it
                era="Vietnam",
                category="Tank",
                notes="NVA tank → Leopard 2 (non-NATO)"
            )

        # ========================================
        # AIRCRAFT
        # ========================================

        # US Fighters → F16
        us_fighters = ["F4", "F-4", "Phantom", "F100", "F-100"]
        for fighter in us_fighters:
            mappings[fighter] = VehicleMapping(
                bfvietnam_name=fighter,
                bf6_vehicle_type="F16",
                era="Vietnam",
                category="Fighter",
                notes="US Vietnam fighter → F-16"
            )

        # NVA Fighters → SU57
        nva_fighters = ["MiG21", "MiG-21", "MiG17", "MiG-17"]
        for fighter in nva_fighters:
            mappings[fighter] = VehicleMapping(
                bfvietnam_name=fighter,
                bf6_vehicle_type="SU57",
                era="Vietnam",
                category="Fighter",
                notes="NVA fighter → SU-57"
            )

        # ========================================
        # LIGHT VEHICLES
        # ========================================

        # Jeeps/Light Vehicles → Quadbike
        light_vehicles = ["M151", "Mutt", "M35", "GAZ69"]
        for vehicle in light_vehicles:
            mappings[vehicle] = VehicleMapping(
                bfvietnam_name=vehicle,
                bf6_vehicle_type="Quadbike",
                era="Vietnam",
                category="Light Vehicle",
                notes="Vietnam light vehicle → Quadbike"
            )

        # APCs → Vector or M2Bradley
        us_apcs = ["M113", "M2Bradley"]
        for apc in us_apcs:
            mappings[apc] = VehicleMapping(
                bfvietnam_name=apc,
                bf6_vehicle_type="M2Bradley",
                era="Vietnam",
                category="APC",
                notes="US APC → M2 Bradley"
            )

        nva_apcs = ["BTR60", "BTR-60"]
        for apc in nva_apcs:
            mappings[apc] = VehicleMapping(
                bfvietnam_name=apc,
                bf6_vehicle_type="CV90",
                era="Vietnam",
                category="APC",
                notes="NVA APC → CV90"
            )

        # ========================================
        # BOATS (Vietnam-specific)
        # ========================================

        boats = ["PBR", "PatrolBoat", "Sampan"]
        for boat in boats:
            mappings[boat] = VehicleMapping(
                bfvietnam_name=boat,
                bf6_vehicle_type="Flyer60",
                era="Vietnam",
                category="Naval",
                notes="Vietnam boat → Flyer 60 hovercraft"
            )

        return mappings

    def map_vehicle(self, bfvietnam_vehicle_name: str) -> str | None:
        """Map BF Vietnam vehicle name to BF6 VehicleType enum value.

        Args:
            bfvietnam_vehicle_name: BF Vietnam vehicle identifier

        Returns:
            BF6 VehicleType enum value (e.g., "UH60", "AH64"), or None if unmapped
        """
        # Try exact match first
        if bfvietnam_vehicle_name in self._mappings:
            return self._mappings[bfvietnam_vehicle_name].bf6_vehicle_type

        # Try case-insensitive partial match
        name_lower = bfvietnam_vehicle_name.lower()
        for key, mapping in self._mappings.items():
            if key.lower() in name_lower or name_lower in key.lower():
                return mapping.bf6_vehicle_type

        return None

    def get_mapping_info(self, bfvietnam_vehicle_name: str) -> VehicleMapping | None:
        """Get complete mapping information for a BF Vietnam vehicle."""
        if bfvietnam_vehicle_name in self._mappings:
            return self._mappings[bfvietnam_vehicle_name]
        return None

    def get_all_mappings(self) -> Dict[str, VehicleMapping]:
        """Get all vehicle mappings."""
        return self._mappings.copy()
```

2. **Create Vietnam-specific engine** `bfvietnam.py`:

```python
#!/usr/bin/env python3
"""BF Vietnam game engine implementation."""

from pathlib import Path
from ....core.interfaces import Team
from ..refractor_base import RefractorEngine


class BFVietnamEngine(RefractorEngine):
    """Game engine implementation for Battlefield Vietnam.

    Battlefield Vietnam (2004) - Refractor Engine 1.0 (enhanced)
    """

    def get_game_name(self) -> str:
        return "BFVietnam"

    def get_engine_version(self) -> str:
        return "Refractor 1.0 Enhanced"

    def get_game_mode_default(self) -> str:
        return "Conquest"

    def _swap_teams(self, team: Team) -> Team:
        """Swap teams for Portal conversion.

        - BF Vietnam Team 1 (NVA) → Portal Team 2 (non-NATO)
        - BF Vietnam Team 2 (US/ARVN) → Portal Team 1 (NATO)
        """
        if team == Team.TEAM_1:
            return Team.TEAM_2
        elif team == Team.TEAM_2:
            return Team.TEAM_1
        else:
            return Team.NEUTRAL

    # Inherit team swapping logic from BF1942Engine...
```

3. **Update generator to support multiple mappers**:

```python
class VehicleSpawnerGenerator(BaseNodeGenerator):
    def __init__(self, vehicle_mapper=None):
        """Initialize with optional custom vehicle mapper.

        Args:
            vehicle_mapper: Custom mapper (defaults to BF1942 mapper)
        """
        super().__init__()
        if vehicle_mapper is None:
            from ...mappers.vehicle_mapper import VehicleMapper
            vehicle_mapper = VehicleMapper()
        self.vehicle_mapper = vehicle_mapper
```

4. **Use Vietnam mapper in conversion**:

```python
# In portal_convert.py or vietnam_convert.py
from tools.bfportal.mappers.vietnam_vehicle_mapper import VietnamVehicleMapper

generator = VehicleSpawnerGenerator(vehicle_mapper=VietnamVehicleMapper())
```

**Time Estimate**: 2-4 hours

---

### Scenario 3: Convert BF2/BF2142 (Modern/Future Era)

**Example**: User wants to convert BF2 (modern era) or BF2142 (future era) maps

**Steps**: Same as Vietnam scenario, but create `bf2_vehicle_mapper.py` or `bf2142_vehicle_mapper.py`

**BF2 Vehicle Examples**:
- M1A2 Abrams → Abrams (direct match!)
- T-90 → Leopard or T90 if Portal adds it
- AH-64 Apache → AH64 (direct match!)
- Mi-28 Havoc → Eurocopter
- F-15 Eagle → F22
- Su-30 Flanker → SU57
- LAV-25 → M2Bradley

**BF2142 Vehicle Examples** (futuristic):
- EU Titan Walker → Custom mapping needed
- PAC Hover Tank → Abrams or Leopard
- Gunship → AH64 or Eurocopter
- Transport VTOL → UH60
- Fighter Jets → F22 or SU57

**Time Estimate**: 2-4 hours per era

---

## Best Practices for Extensibility

### 1. One Mapper Per Era

**Do This**:
- `vehicle_mapper.py` - BF1942 (WW2)
- `vietnam_vehicle_mapper.py` - BF Vietnam (1960s-1970s)
- `bf2_vehicle_mapper.py` - BF2 (2000s modern)
- `bf2142_vehicle_mapper.py` - BF2142 (2140s future)

**Don't Do This**:
- `mega_vehicle_mapper.py` - All eras in one file (violates SRP)

### 2. Use Composition, Not Inheritance

**Good** (Dependency Injection):
```python
class VehicleSpawnerGenerator:
    def __init__(self, vehicle_mapper):
        self.vehicle_mapper = vehicle_mapper  # Any mapper
```

**Bad** (Tight Coupling):
```python
class VehicleSpawnerGenerator:
    def __init__(self):
        self.vehicle_mapper = VehicleMapper()  # Only BF1942
```

### 3. Keep Enum as Single Source of Truth

**Always update `gameplay.py` first** when Portal adds vehicles:

```python
# gameplay.py - SINGLE SOURCE OF TRUTH
BF6_VEHICLE_TYPE_ENUM = {
    "Abrams": 0,
    # ... existing ...
    "NewVehicle": 16,  # ← Add here FIRST
}
```

Then update mappers to use new enum value.

### 4. Document Mapping Rationale

**Every mapping should explain WHY**:

```python
mappings["Sherman"] = VehicleMapping(
    bf1942_name="Sherman",
    bf6_vehicle_type="Abrams",
    era="WW2",
    category="Tank",
    notes="American WW2 medium tank → M1 Abrams (NATO) - gameplay role equivalent"
    #     ↑ Explains the reasoning
)
```

### 5. Test Each Mapper Independently

**Create unit tests** for each mapper:

```python
# tests/bfportal/mappers/test_vietnam_vehicle_mapper.py

def test_vietnam_mapper_maps_huey_to_uh60():
    mapper = VietnamVehicleMapper()
    assert mapper.map_vehicle("UH1") == "UH60"
    assert mapper.map_vehicle("Huey") == "UH60"

def test_vietnam_mapper_maps_cobra_to_ah64():
    mapper = VietnamVehicleMapper()
    assert mapper.map_vehicle("AH1") == "AH64"
```

### 6. Use Type Hints for Interface Compatibility

**All mappers should have same interface**:

```python
from typing import Protocol

class VehicleMapperProtocol(Protocol):
    """Interface that all vehicle mappers must implement."""

    def map_vehicle(self, vehicle_name: str) -> str | None:
        """Map source vehicle to BF6 VehicleType."""
        ...

    def get_mapping_info(self, vehicle_name: str) -> VehicleMapping | None:
        """Get detailed mapping info."""
        ...

    def get_all_mappings(self) -> dict[str, VehicleMapping]:
        """Get all mappings."""
        ...
```

Then generators can accept ANY mapper:

```python
def __init__(self, vehicle_mapper: VehicleMapperProtocol):
    self.vehicle_mapper = vehicle_mapper
```

---

## Migration Guide: When Portal Adds Vehicles

### Step-by-Step Process

**Example**: Portal adds "T90", "Challenger2", "Type99" heavy tanks

#### 1. Update BF6 Enum (5 minutes)

```python
# tools/bfportal/generators/constants/gameplay.py
BF6_VEHICLE_TYPE_ENUM = {
    # ... existing ...
    "SU57": 15,
    # New additions
    "T90": 16,
    "Challenger2": 17,
    "Type99": 18,
}
```

#### 2. Review Existing Mappings (10 minutes)

Ask: "Which current mappings could be improved with new vehicles?"

**Current State**:
- Soviet tanks (T34, T-34-85, KV-1) → Abrams ❌ (not ideal)
- British tanks (Churchill, Crusader) → Abrams ❌ (not ideal)

**Desired State**:
- Soviet tanks → T90 ✅ (better faction match)
- British tanks → Challenger2 ✅ (better faction match)

#### 3. Update Mappings (10 minutes)

```python
# tools/bfportal/mappers/vehicle_mapper.py

# Soviet Tanks (Allied) → T90 (Russian modern)
soviet_tanks = ["T34", "T-34", "T3485", "T-34-85", "KV1", "KV-1"]
for tank in soviet_tanks:
    mappings[tank] = VehicleMapping(
        bf1942_name=tank,
        bf6_vehicle_type="T90",  # ← Changed from "Abrams"
        era="WW2",
        category="Tank",
        notes="Soviet WW2 tank → T-90 (Russian modern)",
    )

# British Tanks (Allied) → Challenger2 (British modern)
british_tanks = ["Churchill", "ChurchillTank", "Crusader"]
for tank in british_tanks:
    mappings[tank] = VehicleMapping(
        bf1942_name=tank,
        bf6_vehicle_type="Challenger2",  # ← Changed from "Abrams"
        era="WW2",
        category="Tank",
        notes="British WW2 tank → Challenger 2",
    )
```

#### 4. Update Documentation (5 minutes)

```bash
# Update BF1942_VEHICLE_MAPPINGS.md to reflect new mappings
# Document when Portal update occurred
# Note which maps are affected
```

#### 5. Run Tests (2 minutes)

```bash
python3 -m pytest tools/tests/bfportal/mappers/test_vehicle_mapper.py -v
python3 -m pytest tools/tests/bfportal/generators/test_vehicle_spawner_generator.py -v
```

#### 6. Reconvert Affected Maps (5-10 minutes)

```bash
# Reconvert any maps using updated vehicles
python3 tools/portal_convert.py --map Kursk --base-terrain MP_Tungsten
python3 tools/portal_convert.py --map Berlin --base-terrain MP_Aftermath
# etc...
```

**Total Time**: ~30-40 minutes per Portal vehicle update

---

## Validation Checklist

When creating a new mapper, verify:

- [ ] **Interface Compliance**: Implements `map_vehicle()`, `get_mapping_info()`, `get_all_mappings()`
- [ ] **Type Hints**: All methods have proper type annotations
- [ ] **Documentation**: Docstrings explain mapping convention
- [ ] **Faction Alignment**: Mappings follow consistent Axis/Allied or NVA/US logic
- [ ] **Era Tagging**: All mappings have correct `era` field
- [ ] **Category Organization**: Vehicles grouped by type (Tank, Fighter, etc.)
- [ ] **Rationale Notes**: Each mapping has `notes` explaining reasoning
- [ ] **Enum Compliance**: Only uses vehicles from `BF6_VEHICLE_TYPE_ENUM`
- [ ] **Partial Matching**: Supports case-insensitive name variations
- [ ] **Unit Tests**: Test suite covers all mappings
- [ ] **Integration Test**: End-to-end conversion produces valid .tscn

---

## FAQ

### Q: What if Portal removes a vehicle type?

**A**: Keep old mappings but add fallback:

```python
def map_vehicle(self, vehicle_name: str) -> str | None:
    mapped = self._mappings.get(vehicle_name)
    if mapped and mapped.bf6_vehicle_type in BF6_VEHICLE_TYPE_ENUM:
        return mapped.bf6_vehicle_type
    # Fallback to generic equivalent
    return self._get_fallback(mapped.category)
```

### Q: Should we auto-generate mappers from vehicle lists?

**A**: No - mapping requires human judgment about gameplay roles, faction alignment, and historical equivalence. Keep it manual.

### Q: Can we use the same mapper for BF1942 and its expansion packs?

**A**: Yes - Road to Rome and Secret Weapons use same era/vehicles. One mapper (`vehicle_mapper.py`) covers all.

### Q: What about mod vehicles (custom community vehicles)?

**A**: Create separate `custom_vehicle_mapper.py` or allow user to provide custom mapping JSON.

---

## Summary

Our vehicle mapping system is **fully extensible** and follows **SOLID principles**:

✅ **Single Responsibility**: One mapper per era/game
✅ **Open/Closed**: Easy to add new mappers without modifying existing code
✅ **Liskov Substitution**: All mappers are interchangeable via common interface
✅ **Interface Segregation**: Generators depend only on `map_vehicle()` method
✅ **Dependency Inversion**: High-level code depends on mapper interface, not implementation

**Adding new vehicles**: 30-40 minutes
**Adding new era mapper**: 2-4 hours
**Testing changes**: Automated via pytest

**This system will scale to any future Battlefield game or Portal expansion.**
