# Vehicle Mapping System

**Status**: ✅ Production-ready, fully extensible
**Last Updated**: 2025-10-15

## Overview

This directory contains the vehicle mapping system that translates classic Battlefield vehicle types to modern BF6 Portal VehicleType enum values.

## Current Mappers

### 1. `vehicle_mapper.py` - BF1942 Mapper (WW2 Era)

**Game**: Battlefield 1942 (2002)
**Era**: World War II (1939-1945)
**Vehicles Mapped**: 81 vehicles → 15 BF6 types

**Faction Convention**:
- **Axis powers** (German, Italian, Japanese) → **non-NATO assets**
  - Tanks → Leopard (non-NATO)
  - Fighters → SU57 (non-NATO)
  - Dive Bombers → Eurocopter (non-NATO)

- **Allied powers** (American, British, Soviet) → **NATO/American assets**
  - Tanks → Abrams (NATO)
  - Fighters → F16 (NATO)
  - Dive Bombers → AH64 (NATO)

**Example Usage**:
```python
from tools.bfportal.mappers.vehicle_mapper import VehicleMapper

mapper = VehicleMapper()

# Map BF1942 vehicles to BF6 types
bf6_type = mapper.map_vehicle("Sherman")  # Returns "Abrams"
bf6_type = mapper.map_vehicle("PanzerIV")  # Returns "Leopard"
bf6_type = mapper.map_vehicle("Stuka")  # Returns "Eurocopter"
bf6_type = mapper.map_vehicle("IL2")  # Returns "AH64"

# Get detailed mapping info
info = mapper.get_mapping_info("Sherman")
# VehicleMapping(bf1942_name='Sherman', bf6_vehicle_type='Abrams',
#                era='WW2', category='Tank',
#                notes='American WW2 tank → Modern American M1 Abrams')

# Get all supported vehicles
all_vehicles = mapper.get_supported_bf1942_vehicles()  # 81 vehicles

# Get mappings by category
tanks = mapper.get_mappings_by_category("Tank")  # All tank mappings
```

**Complete Reference**: See `BF1942_VEHICLE_MAPPINGS.md` for comprehensive vehicle catalog

---

## Architecture

### Files

```
mappers/
├── README.md (this file)                     # Overview and usage
├── base_vehicle_mapper.py                    # Abstract base class + protocol
├── vehicle_mapper.py                         # BF1942 mapper (WW2 era)
├── BF1942_VEHICLE_MAPPINGS.md               # Complete BF1942 vehicle reference
└── VEHICLE_MAPPING_EXTENSIBILITY.md         # Guide for adding new mappers
```

### Key Components

#### 1. **VehicleMapping** (Data Class)
Represents a single vehicle mapping with metadata:
```python
@dataclass
class VehicleMapping:
    source_name: str          # Original vehicle identifier
    bf6_vehicle_type: str     # BF6 VehicleType enum value
    era: str                  # Historical era (WW2, Vietnam, Modern, etc.)
    category: str             # Vehicle type (Tank, Fighter, APC, etc.)
    faction: str              # Faction alignment (Axis, Allied, NATO, non-NATO)
    notes: str                # Rationale for mapping
```

#### 2. **IVehicleMapper** (Protocol)
Interface that all vehicle mappers must implement:
```python
class IVehicleMapper(Protocol):
    def map_vehicle(self, source_vehicle_name: str) -> str | None:
        """Map source vehicle to BF6 VehicleType."""
        ...

    def get_mapping_info(self, source_vehicle_name: str) -> VehicleMapping | None:
        """Get detailed mapping info."""
        ...

    def get_all_mappings(self) -> dict[str, VehicleMapping]:
        """Get all mappings."""
        ...
```

#### 3. **BaseVehicleMapper** (Abstract Base Class)
Provides shared implementation for common operations:
- Case-insensitive vehicle matching
- Faction/category filtering
- Validation against BF6 enum
- Utility methods (get_supported_vehicles, get_bf6_vehicle_types, etc.)

**All future mappers should extend this class** for DRY/SOLID compliance.

---

## Extension System

### Scenario 1: BF6 Portal Adds New Vehicle Types

**Example**: Portal adds "T90" (Russian tank), "Challenger2" (British tank)

**Steps**:

1. Update `tools/bfportal/generators/constants/gameplay.py`:
```python
BF6_VEHICLE_TYPE_ENUM = {
    # ... existing ...
    "SU57": 15,
    # New vehicles
    "T90": 16,
    "Challenger2": 17,
}
```

2. Update `vehicle_mapper.py` mappings:
```python
# Soviet Tanks → T90 (better faction match)
soviet_tanks = ["T34", "T-34", "T3485", "T-34-85", "KV1", "KV-1"]
for tank in soviet_tanks:
    mappings[tank] = VehicleMapping(
        bf1942_name=tank,
        bf6_vehicle_type="T90",  # ← Changed from "Abrams"
        era="WW2",
        category="Tank",
        notes="Soviet WW2 tank → T-90 (Russian modern)",
    )
```

3. No other changes needed - generator automatically uses new mappings

**Time**: ~30 minutes per Portal update

---

### Scenario 2: Add New Era Mapper (BF Vietnam, BF2, etc.)

**Example**: User wants to convert BF Vietnam (1960s-1970s) maps

**Steps**:

1. Create new mapper `vietnam_vehicle_mapper.py`:
```python
from .base_vehicle_mapper import BaseVehicleMapper, VehicleMapping


class VietnamVehicleMapper(BaseVehicleMapper):
    """Maps BF Vietnam vehicles to BF6 Portal VehicleType enum values."""

    def get_game_name(self) -> str:
        return "BFVietnam"

    def get_era(self) -> str:
        return "Vietnam"

    def _build_mappings(self) -> dict[str, VehicleMapping]:
        mappings = {}

        # US Helicopters → UH60, AH64
        mappings["UH1"] = VehicleMapping(
            source_name="UH1",
            bf6_vehicle_type="UH60",
            era="Vietnam",
            category="Transport Helicopter",
            faction="US",
            notes="UH-1 Huey → UH-60 Black Hawk"
        )

        mappings["AH1"] = VehicleMapping(
            source_name="AH1",
            bf6_vehicle_type="AH64",
            era="Vietnam",
            category="Attack Helicopter",
            faction="US",
            notes="AH-1 Cobra → AH-64 Apache"
        )

        # ... more mappings ...

        return mappings
```

2. Use new mapper in conversion:
```python
from tools.bfportal.mappers.vietnam_vehicle_mapper import VietnamVehicleMapper

mapper = VietnamVehicleMapper()
bf6_type = mapper.map_vehicle("UH1")  # Returns "UH60"
```

**Time**: 2-4 hours per new era

**See**: `VEHICLE_MAPPING_EXTENSIBILITY.md` for complete guide with Vietnam example

---

## Design Principles

### 1. Single Responsibility Principle (SRP)
- **One mapper per era/game** - `vehicle_mapper.py` only handles BF1942
- Future mappers: `vietnam_vehicle_mapper.py`, `bf2_vehicle_mapper.py`, etc.

### 2. Open/Closed Principle (OCP)
- **Open for extension** - Easy to add new mappers by extending BaseVehicleMapper
- **Closed for modification** - Existing mappers don't change when adding new ones

### 3. Liskov Substitution Principle (LSP)
- **All mappers are interchangeable** - VehicleSpawnerGenerator accepts any IVehicleMapper
- **Same interface** - All implement `map_vehicle()`, `get_mapping_info()`, `get_all_mappings()`

### 4. Interface Segregation Principle (ISP)
- **Minimal interface** - Generators only depend on `map_vehicle()` method
- **Rich interface** - Optional methods available but not required

### 5. Dependency Inversion Principle (DIP)
- **High-level code depends on abstractions** - Generators use IVehicleMapper protocol
- **Low-level code implements interface** - Specific mappers provide implementation

### DRY (Don't Repeat Yourself)
- **Shared logic in BaseVehicleMapper** - Case-insensitive matching, filtering, validation
- **Subclasses only define mappings** - No duplicate code

---

## Single Source of Truth

**BF6 Vehicle Enum**: `tools/bfportal/generators/constants/gameplay.py`

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

**Always update this enum FIRST** when Portal adds new vehicles.

---

## Validation

### Validate Mappings Against BF6 Enum

```python
from tools.bfportal.generators.constants.gameplay import BF6_VEHICLE_TYPE_ENUM

mapper = VehicleMapper()
errors = mapper.validate_mappings(set(BF6_VEHICLE_TYPE_ENUM.keys()))

if errors:
    for error in errors:
        print(f"❌ {error}")
else:
    print("✅ All mappings use valid BF6 VehicleTypes")
```

### Find Unmapped Vehicles

```python
# After scanning a new map
found_vehicles = ["Sherman", "PanzerIV", "NewTankType"]
unmapped = mapper.get_unmapped_vehicles(found_vehicles)

if unmapped:
    print(f"⚠️ Unmapped vehicles: {unmapped}")
    # Add mappings to vehicle_mapper.py
```

---

## Testing

### Unit Test Example

```python
def test_bf1942_mapper_maps_sherman_to_abrams():
    mapper = VehicleMapper()
    assert mapper.map_vehicle("Sherman") == "Abrams"

def test_bf1942_mapper_maps_panzer_to_leopard():
    mapper = VehicleMapper()
    assert mapper.map_vehicle("PanzerIV") == "Leopard"

def test_bf1942_mapper_axis_vehicles_map_to_non_nato():
    mapper = VehicleMapper()
    axis_mappings = mapper.get_mappings_by_faction("Axis")

    # Verify Axis → non-NATO convention
    for name, mapping in axis_mappings.items():
        assert mapping.bf6_vehicle_type in ["Leopard", "SU57", "Eurocopter"]
```

---

## Integration with Conversion Pipeline

### Used By

1. **VehicleSpawnerGenerator** (`tools/bfportal/generators/node_generators/vehicle_spawner_generator.py`)
   - Converts BF1942 vehicle spawners to Portal VehicleSpawner nodes
   - Uses mapper to determine BF6 VehicleType enum index

2. **RefractorEngine** (`tools/bfportal/engines/refractor/refractor_base.py`)
   - Parses BF1942 ObjectSpawnTemplates.con files
   - Extracts vehicle type assignments from spawner templates

3. **BF1942Engine** (`tools/bfportal/engines/refractor/games/bf1942.py`)
   - Swaps team assignments for Portal conversion
   - Ensures Axis → Team 2 (non-NATO), Allied → Team 1 (NATO)

### Workflow

```
BF1942 Map (.con files)
    ↓
RefractorEngine.parse()  ← Extracts vehicle spawner objects
    ↓
VehicleMapper.map_vehicle()  ← BF1942 type → BF6 type
    ↓
VehicleSpawnerGenerator.generate()  ← Creates .tscn nodes
    ↓
Portal Map (.tscn file)
```

---

## FAQ

### Q: What if a BF1942 vehicle has no good BF6 equivalent?

**A**: Use the closest gameplay role equivalent:
- WW2 heavy tank → Modern MBT (Abrams/Leopard)
- WW2 dive bomber → Modern attack helicopter (AH64/Eurocopter)
- WW2 fighter → Modern multirole jet (F16/JAS39/SU57)

Document the rationale in the `notes` field.

### Q: Can I add custom vehicles not in BF1942?

**A**: Yes - add entries to `_build_mappings()` with `era="Custom"`:
```python
mappings["CustomTank"] = VehicleMapping(
    bf1942_name="CustomTank",
    bf6_vehicle_type="Abrams",
    era="Custom",
    category="Tank",
    notes="Custom modded vehicle"
)
```

### Q: Should I create one mega-mapper for all Battlefield games?

**A**: **No** - violates Single Responsibility Principle. Create separate mappers:
- `vehicle_mapper.py` - BF1942 (WW2)
- `vietnam_vehicle_mapper.py` - BF Vietnam (1960s-1970s)
- `bf2_vehicle_mapper.py` - BF2 (2000s modern)
- `bf2142_vehicle_mapper.py` - BF2142 (2140s future)

### Q: How do I handle expansion packs?

**A**: Same mapper. BF1942 mapper handles base game + Road to Rome + Secret Weapons because they're all WW2 era with same vehicle types.

---

## References

- **Complete Vehicle Catalog**: `BF1942_VEHICLE_MAPPINGS.md`
- **Extensibility Guide**: `VEHICLE_MAPPING_EXTENSIBILITY.md`
- **BF6 VehicleType Enum**: `tools/bfportal/generators/constants/gameplay.py`
- **Base Class**: `base_vehicle_mapper.py`
- **Example Mapper**: `vehicle_mapper.py`

---

## Summary

✅ **Reusable** - BaseVehicleMapper provides shared functionality
✅ **DRY** - No duplicate code across mappers
✅ **SOLID** - Follows all 5 SOLID principles
✅ **Extensible** - Easy to add new mappers for new eras
✅ **Maintainable** - Single source of truth for BF6 enum
✅ **Future-proof** - Ready for Portal expansions and new Battlefield games

**This system will scale to any future Battlefield game or Portal expansion.**
