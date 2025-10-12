# BF1942 to BF6 Portal Conversion Project

## Project Overview

This project converts classic Battlefield 1942 maps to Battlefield 6 Portal format by extracting positional and gameplay data from BF1942 and mapping them to equivalent BF6 assets.

**Key Concept**: We're creating "spiritual successors" - extracting positions, dimensions, and gameplay logic from BF1942, then replacing objects with equivalent BF6 assets. This is a recreation/remaster, not a direct port.

## Project Architecture

### Directory Structure

```
PortalSDK/
├── .claude/                    # Project documentation and standards
├── bf1942_source/              # Original BF1942 game files (IGNORED in git)
│   └── Mods/
│       ├── bf1942/            # Base game
│       │   ├── Archives/
│       │   │   └── bf1942/
│       │   │       └── levels/  # ← RFA map archives
│       │   └── init.con
│       ├── XPack1/            # Road to Rome expansion
│       └── XPack2/            # Secret Weapons expansion
├── GodotProject/              # BF6 Portal Godot workspace
│   ├── levels/                # Modern BF6 maps (.tscn files)
│   ├── objects/               # BF6 asset library
│   ├── static/                # Static terrain/assets
│   ├── raw/models/            # Large .glb files (IGNORED in git)
│   └── project.godot
├── FbExportData/              # Export configurations
│   ├── asset_types.json       # Complete BF6 asset catalog
│   ├── level_info.json        # Level metadata
│   └── levels/                # Exported .spatial.json files
├── code/                      # Conversion tools
│   └── gdconverter/           # Existing .tscn ↔ .json converter
├── mods/                      # Example Portal game modes
├── python/                    # Python runtime for tools
├── tools/                     # Conversion toolset
│   ├── portal_convert.py     # Main CLI (all-in-one)
│   ├── portal_*.py           # Modular CLIs
│   └── bfportal/             # Core library modules
├── README.md                  # Project documentation
├── Testing_Guide.md                 # Testing procedures
└── README.html                # Portal SDK documentation
```

## File Format Reference

### BF1942 Formats

#### RFA (Refractor Archive)
- **Purpose**: Compressed archive format for BF1942 assets
- **Location**: `bf1942_source/Mods/bf1942/Archives/bf1942/levels/*.rfa`
- **Structure**: Contains map geometry, textures, and configuration files
- **Example**: `Kursk.rfa`, `Kursk_000.rfa` (patches), `Kursk_003.rfa` (patches)
- **Extraction**: Requires RFA extractor tool (BGA, WinRFA, or custom Python)

#### .con (Configuration) Files
- **Purpose**: Text-based script files for game logic
- **Format**: Custom scripting language
- **Contents**: Object placements, spawn points, game rules, vehicle configs
- **Example**:
  ```
  game.addModPath Mods/BF1942/
  game.setCustomGameVersion 1.6
  ```

#### Other BF1942 Formats
- `.sct` - Script files
- `.sm` - Static mesh files
- `.rs` - Shader/render state files
- `.dds` - Texture files (DirectDraw Surface)

### BF6 Portal Formats

#### .tscn (Godot Scene)
- **Purpose**: Godot 4 scene file defining a BF6 map
- **Format**: Text-based scene description
- **Location**: `GodotProject/levels/*.tscn`
- **Structure**:
  ```
  [gd_scene load_steps=7 format=3]

  [node name="MAP_NAME" type="Node3D"]
  [node name="TEAM_1_HQ" parent="." ...]
  [node name="TEAM_2_HQ" parent="." ...]
  [node name="CombatArea" parent="." ...]
  [node name="Static" type="Node3D" parent="."]
  ```

#### .spatial.json (Export Format)
- **Purpose**: Exported map data for Portal web tool
- **Format**: JSON with transform matrices
- **Location**: `FbExportData/levels/*.spatial.json`
- **Structure**:
  ```json
  {
    "Portal_Dynamic": [],
    "Static": [{
      "name": "Terrain",
      "type": "MP_Name_Terrain",
      "right": {"x": 1.0, "y": 0.0, "z": 0.0},
      "up": {"x": 0.0, "y": 1.0, "z": 0.0},
      "front": {"x": 0.0, "y": 0.0, "z": 1.0},
      "position": {"x": 0.0, "y": 0.0, "z": 0.0}
    }]
  }
  ```

## BF6 Portal Map Structure

### Required Components

Every BF6 map must have these elements:

#### 1. Team HQs
```gdscript
[node name="TEAM_1_HQ" parent="." node_paths=PackedStringArray("HQArea", "InfantrySpawns") instance=ExtResource("HQ_PlayerSpawner")]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, x, y, z)
AltTeam = 0
ObjId = 1
HQArea = NodePath("HQ_Team1")
InfantrySpawns = [NodePath("SpawnPoint_1_1"), ...]
```

**Properties**:
- `Team`: 1 or 2 (team assignment)
- `AltTeam`: Alternative team (usually 0)
- `ObjId`: Unique identifier for scripting
- `HQArea`: Reference to PolygonVolume defining HQ bounds
- `InfantrySpawns`: Array of SpawnPoint references

#### 2. Spawn Points
```gdscript
[node name="SpawnPoint_1_1" parent="TEAM_1_HQ" instance=ExtResource("SpawnPoint")]
transform = Transform3D(rotation_matrix, x, y, z)
```

**Requirements**:
- Minimum 4 spawn points per team
- Must be children of HQ_PlayerSpawner
- Transform defines position and orientation

#### 3. Combat Area
```gdscript
[node name="CombatArea" parent="." node_paths=PackedStringArray("CombatVolume") instance=ExtResource("CombatArea")]
CombatVolume = NodePath("CollisionPolygon3D")

[node name="CollisionPolygon3D" instance=ExtResource("PolygonVolume") parent="CombatArea"]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, x, y, z)
height = 100.0
points = PackedVector2Array([...])  # 2D boundary points
```

**Properties**:
- `height`: Vertical extent of playable area
- `points`: 2D polygon defining horizontal boundaries
- Players leaving this area are warned/killed

#### 4. Static Layer
```gdscript
[node name="Static" type="Node3D" parent="."]
[node name="MP_Name_Terrain" parent="Static" instance=ExtResource("Terrain")]
[node name="MP_Name_Assets" parent="Static" instance=ExtResource("Assets")]
```

**Purpose**: References pre-built terrain and asset meshes

### Optional Gameplay Objects

- `DeployCam`: Camera view for deploy screen
- `AreaTrigger`: Custom trigger volumes for scripting
- `CapturePoint`: Conquest-style objectives
- `VehicleSpawner`: Vehicle spawn locations
- `AI_Spawner`: Bot spawn points
- `InteractPoint`: Interactive objects
- `WorldIcon`: In-world markers/text

## BF6 Asset System

### Asset Types JSON Structure

Location: `FbExportData/asset_types.json`

```json
{
  "AssetTypes": [{
    "type": "ObjectName",
    "directory": "Category/Subcategory",
    "constants": [
      {"name": "mesh", "type": "string", "value": "MeshName"},
      {"name": "category", "type": "string", "value": "spatial"},
      {"name": "physicsCost", "type": "int", "value": 6}
    ],
    "properties": [
      {"name": "ObjId", "type": "int", "default": -1}
    ],
    "levelRestrictions": ["MP_Battery", "MP_Aftermath"]
  }]
}
```

### Asset Categories

**Architecture**: Buildings, walls, foundations
**Props**: Furniture, vehicles, debris
**Nature**: Trees, plants, terrain features
**LightFixtures**: Lights and illumination
**Gameplay**: HQs, spawners, objectives
**Generic/Common**: Shared assets across maps

### Level Restrictions

Many assets are map-specific due to `levelRestrictions`:
- Assets ONLY usable on specified maps
- Prevents using wrong-era/wrong-theme objects
- Must map BF1942 objects to compatible BF6 equivalents

## Conversion Strategy

### Object Mapping Approach

1. **Extract BF1942 Data**:
   - Object type (e.g., "Bunker_German_01")
   - 3D position (x, y, z)
   - Rotation (pitch, yaw, roll)
   - Scale (if applicable)
   - Team ownership
   - Gameplay properties

2. **Map to BF6 Equivalent**:
   - Lookup in mapping database
   - Consider: size, function, era, theme
   - Example: `Bunker_German_01` → `Military_Bunker_02`

3. **Transform Coordinates**:
   - BF1942 uses Refractor coordinate system
   - BF6 uses Godot/Frostbite coordinates
   - Apply scale factor and axis conversions
   - Adjust for terrain height differences

4. **Generate .tscn Node**:
   ```gdscript
   [node name="Object_001" parent="." instance=ExtResource("BF6_Asset")]
   transform = Transform3D(right.x, up.x, forward.x,
                           right.y, up.y, forward.y,
                           right.z, up.z, forward.z,
                           pos.x, pos.y, pos.z)
   ObjId = 42
   ```

### Coordinate System Transformations

**BF1942 (Refractor Engine)**:
- Right-handed coordinate system
- Y-up axis
- Units: meters
- Origin: varies per map

**BF6 (Godot/Frostbite)**:
- Right-handed coordinate system
- Y-up axis
- Units: meters
- Origin: map-specific

**Conversion Notes**:
- Both use Y-up, simplifying conversion
- May need to apply rotation offsets
- Scale factor likely 1:1 (both in meters)
- Test with known reference points

### Terrain Strategy

**Challenge**: Cannot import custom BF1942 terrain into BF6

**Solution**:
1. Analyze BF1942 heightmap data (if accessible)
2. Note key terrain features (hills, valleys, water)
3. Select closest matching BF6 terrain template
4. Document manual sculpting needed
5. Use Godot terrain tools for final adjustments

## Coding Standards

### Python Code

**Style**: PEP 8
**Type Hints**: Required for all functions
**Docstrings**: Google-style format

```python
def extract_rfa(archive_path: str, output_dir: str) -> bool:
    """Extract files from a Battlefield 1942 RFA archive.

    Args:
        archive_path: Path to the .rfa file
        output_dir: Directory to extract files to

    Returns:
        True if extraction succeeded, False otherwise

    Raises:
        FileNotFoundError: If archive_path doesn't exist
        PermissionError: If output_dir is not writable
    """
    pass
```

**Naming Conventions**:
- `snake_case` for functions and variables
- `PascalCase` for classes
- `UPPER_CASE` for constants

### TypeScript Code

**Style**: StandardJS or Airbnb style guide
**Type Annotations**: Use TypeScript types, avoid `any`

```typescript
export function OnPlayerJoinGame(eventPlayer: mod.Player): void {
    // Implementation
}
```

### Godot Scripts (.gd)

**Style**: GDScript style guide
**Signals**: Use for event-driven communication
**Static Typing**: Use when possible

```gdscript
extends Node3D

signal player_entered(player: Player)

var spawn_point: Vector3 = Vector3.ZERO

func _ready() -> void:
    pass
```

## Naming Conventions

### File Naming

- **Maps**: `Kursk.tscn`, `El_Alamein.tscn` (match BF1942 names)
- **Scripts**: `rfa_extractor.py`, `object_mapper.py` (descriptive, snake_case)
- **Configs**: `kursk_mapping.json`, `asset_database.json`

### Object IDs

- Use sequential integers starting from 1
- Reserve ranges for object types:
  - 1-99: HQs and spawn points
  - 100-999: Gameplay objects (capture points, triggers)
  - 1000+: Props and environment

### Git Commits

Format: `<type>: <description>`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `refactor`: Code refactoring
- `test`: Test additions/changes
- `chore`: Build/tooling changes

Example: `feat: add RFA extraction for Kursk map data`

## Testing Strategy

**Current Coverage:** 71% overall (2850/3996 statements)
**Target Coverage:** 75-80% (industry best practice)

### Test Coverage Philosophy

#### Is 100% Coverage Worth It?

**No** - 100% test coverage is generally **not the goal** for most software projects.

**Industry Best Practices:**
- **70-80% coverage**: Standard target for production code ✅
- **80-90% coverage**: Excellent for critical business logic
- **90-100% coverage**: Usually overkill, only for safety-critical systems (medical, aerospace)

**Why Not 100%?**

1. **Diminishing Returns**: The last 10-20% often costs as much effort as the first 80%
2. **Coverage ≠ Quality**: 100% line coverage doesn't guarantee bug-free code
   - Coverage only shows which lines were executed, not whether they work correctly
   - Can still have logic errors, edge cases, integration issues
3. **Untestable Code**: Some code paths are impractical or impossible to test:
   - OS-specific error paths (Windows vs macOS vs Linux)
   - External service failures (network timeouts, database crashes)
   - Defensive error handling that "should never happen"
   - Platform-specific edge cases
4. **Opportunity Cost**: Time spent chasing 100% could be better spent on:
   - Integration tests and end-to-end workflows
   - Performance testing
   - Documentation
   - New features
   - Security audits

#### Strategic Coverage Targeting

Focus testing efforts on **high-value, high-risk code**:

**High Priority (Target 85-95%):**
- Core conversion pipeline (parsers, mappers, generators)
- User-facing CLI tools (portal_convert.py, portal_validate.py)
- Complex business logic (coordinate transforms, asset mapping)
- Error-prone areas (file I/O, parsing, validation)
- Bug fixes (regression tests)

**Medium Priority (Target 70-80%):**
- Utility scripts (create_experience.py, export_to_portal.py)
- Validation and comparison tools
- Terrain and height calculation

**Lower Priority (Target 40-60%):**
- One-off analysis scripts (compare_terrains.py, scan_all_maps.py)
- Diagnostic tools
- Experimental features

#### Coverage Quality Over Quantity

**Good coverage** means:
- Tests verify behavior, not implementation details
- Tests are maintainable and clear (AAA pattern)
- Tests catch real bugs before production
- Tests document expected behavior

**Bad coverage** means:
- Tests that pass but don't verify anything meaningful
- Brittle tests that break on refactoring
- Tests that duplicate what other tests already verify
- Tests chasing 100% without added value

### Testing Best Practices

All tests must follow these modern best practices:

#### AAA Pattern (Arrange-Act-Assert)

Every test must use the AAA pattern for clarity:

```python
def test_create_experience_file():
    # Arrange - Set up test data and environment
    map_name = "Kursk"
    spatial_path = tmp_path / "Kursk.spatial.json"
    spatial_path.write_text('{"Portal_Dynamic": [], "Static": []}')

    # Act - Execute the code being tested
    result = create_experience_file(
        map_name=map_name,
        spatial_path=spatial_path,
        base_map="MP_Tungsten",
        max_players_per_team=32,
        game_mode="Conquest"
    )

    # Assert - Verify behavior matches expectations
    assert result.exists()
    assert result.name == "Kursk_Experience.json"
```

**Key Points:**
- Separate each phase with blank lines
- Keep each phase focused and clear
- Assert one concept per test (can have multiple assertions for same concept)

#### Test Independence and Isolation

**DO:**
- Each test runs independently
- Tests don't rely on other tests' state
- Use fixtures for shared setup/teardown
- Mock external dependencies (filesystem, network, databases)

**DON'T:**
- Share mutable state between tests
- Rely on test execution order
- Use real external systems (files, networks, DBs)

```python
# Good - Each test is independent
@pytest.fixture
def sample_spatial_data():
    """Fixture provides fresh data for each test."""
    return {"Portal_Dynamic": [], "Static": [{"name": "Terrain"}]}

def test_experience_creation(tmp_path, sample_spatial_data):
    spatial_file = tmp_path / "test.spatial.json"
    spatial_file.write_text(json.dumps(sample_spatial_data))
    # Test uses isolated tmp_path and fresh data
```

#### Flexible Testing - Avoid Brittle Tests

**Test Behavior, Not Implementation:**
```python
# Bad - Tests implementation details (brittle)
def test_export_calls_json_dump():
    with patch('json.dump') as mock_dump:
        export_map("Kursk")
        mock_dump.assert_called_once()  # Breaks if we change JSON library

# Good - Tests external behavior (robust)
def test_export_creates_valid_json(tmp_path):
    output = export_map("Kursk", output_dir=tmp_path)
    data = json.loads(output.read_text())
    assert data["name"] == "Kursk - BF1942 Classic"
```

**Use `autospec=True` for Mocks:**
```python
# Good - autospec ensures mock matches real signature
with patch('tools.bfportal.terrain.terrain_provider.TerrainProvider', autospec=True) as mock:
    mock.return_value.get_height_at_position.return_value = 10.0
```

**Mock Only External Dependencies:**
```python
# Mock external things (filesystem, network, time)
@patch('pathlib.Path.exists', return_value=True)
@patch('pathlib.Path.read_text', return_value='{"data": "test"}')
def test_load_config(mock_read, mock_exists):
    config = load_config("test.json")
    assert config["data"] == "test"

# Don't mock internal business logic - test it directly
```

#### Pytest Fixtures

**Use fixtures for reusable setup:**
```python
@pytest.fixture
def kursk_tscn_path(tmp_path):
    """Provide path to test .tscn file."""
    tscn = tmp_path / "Kursk.tscn"
    tscn.write_text('[gd_scene format=3]\n[node name="Kursk" type="Node3D"]')
    return tscn

@pytest.fixture
def mock_terrain_provider():
    """Provide mocked terrain provider with default behavior."""
    provider = MagicMock(spec=ITerrainProvider)
    provider.get_height_at_position.return_value = 0.0
    return provider

# Use fixtures in tests
def test_conversion(kursk_tscn_path, mock_terrain_provider):
    result = convert_map(kursk_tscn_path, terrain_provider=mock_terrain_provider)
    assert result.exists()
```

**Fixture Scopes:**
- `function`: Default, runs before each test (most common)
- `module`: Runs once per test module (for expensive setup)
- `session`: Runs once per test session (rarely needed)

#### Descriptive Test Names

```python
# Good - Describes what is being tested and expected outcome
def test_create_experience_with_missing_spatial_file_raises_file_not_found_error():
    pass

def test_export_to_portal_creates_experience_with_base64_encoded_spatial_data():
    pass

# Bad - Vague, doesn't explain what's tested
def test_export():
    pass

def test_error():
    pass
```

**Format:** `test_<function_name>_<scenario>_<expected_result>`

#### Test Organization

**Group Related Tests:**
```python
class TestCreateExperience:
    """Tests for create_experience.py functionality."""

    def test_creates_valid_experience_file(self):
        pass

    def test_encodes_spatial_data_as_base64(self):
        pass

    def test_raises_error_for_missing_spatial_file(self):
        pass
```

**One Concept Per Test:**
```python
# Good - One test per concept
def test_experience_has_correct_map_id():
    exp = create_experience("Kursk", "MP_Tungsten")
    assert exp["mapRotation"][0]["id"] == "MP_Tungsten-ModBuilderCustom0"

def test_experience_has_correct_game_mode():
    exp = create_experience("Kursk", mode="Conquest")
    assert exp["gameMode"] == "Conquest"

# Bad - Tests multiple unrelated concepts
def test_experience_structure():
    exp = create_experience("Kursk")
    assert exp["mapRotation"][0]["id"] == "MP_Tungsten-ModBuilderCustom0"  # Map ID
    assert exp["gameMode"] == "Conquest"  # Game mode
    assert exp["mutators"]["MaxPlayerCount_PerTeam"] == 32  # Player count
    # If this fails, which concept broke?
```

#### Parameterized Tests

**Use `@pytest.mark.parametrize` for multiple scenarios:**
```python
@pytest.mark.parametrize("map_name,base_map,expected_id", [
    ("Kursk", "MP_Tungsten", "MP_Tungsten-ModBuilderCustom0"),
    ("El_Alamein", "MP_Firestorm", "MP_Firestorm-ModBuilderCustom0"),
    ("Wake_Island", "MP_Limestone", "MP_Limestone-ModBuilderCustom0"),
])
def test_map_id_format(map_name, base_map, expected_id):
    exp = create_experience(map_name, base_map)
    assert exp["mapRotation"][0]["id"] == expected_id
```

#### Test Documentation

```python
def test_create_multi_map_experience_filters_incomplete_maps(maps_registry):
    """
    Test that create_multi_map_experience only includes maps with status='complete'.

    Given: Registry with mix of complete/planned maps
    When: Creating multi-map experience with status filter
    Then: Only complete maps are included in mapRotation
    """
    # Arrange
    registry = {
        "maps": [
            {"id": "kursk", "status": "complete"},
            {"id": "el_alamein", "status": "planned"},
        ]
    }

    # Act
    result = create_multi_map_experience(registry, filter={"status": "complete"})

    # Assert
    assert len(result["mapRotation"]) == 1
    assert result["mapRotation"][0]["spatialAttachment"]["id"] == "kursk-bf1942-spatial"
```

#### Coverage Exclusions

Use `# pragma: no cover` for lines that shouldn't be tested:
```python
if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())

def __repr__(self):  # pragma: no cover
    return f"Asset({self.name})"
```

#### CLI Testing Best Practices

**Test CLI Tools via Direct Function Calls:**
```python
# Good - Test main() function directly
def test_create_experience_cli_with_valid_args(tmp_path, monkeypatch):
    # Arrange
    monkeypatch.setattr('sys.argv', [
        'create_experience.py',
        'Kursk',
        '--base-map', 'MP_Tungsten',
        '--max-players', '32'
    ])
    # Create mock spatial file
    spatial = tmp_path / "FbExportData/levels/Kursk.spatial.json"
    spatial.parent.mkdir(parents=True)
    spatial.write_text('{}')

    # Act
    exit_code = main()

    # Assert
    assert exit_code == 0
    assert (tmp_path / "experiences/Kursk_Experience.json").exists()
```

**Test Error Handling:**
```python
def test_create_experience_missing_spatial_file_exits_with_error(capsys):
    # Arrange
    sys.argv = ['create_experience.py', 'NonExistent']

    # Act
    exit_code = main()

    # Assert
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "Spatial file not found" in captured.err
```

#### Dependency Injection for Testability

**Design Code for Easy Testing:**
```python
# Good - Dependencies injected, easy to test
def convert_map(
    map_path: Path,
    terrain_provider: ITerrainProvider,
    asset_mapper: IAssetMapper
) -> Path:
    """Convert map using provided dependencies."""
    height = terrain_provider.get_height_at_position(0, 0)
    asset = asset_mapper.map_asset("TreeType1")
    return output_path

# Test with mocks
def test_convert_map(mock_terrain, mock_mapper):
    result = convert_map(Path("map.con"), mock_terrain, mock_mapper)
    assert result.exists()

# Bad - Hard-coded dependencies, hard to test
def convert_map(map_path: Path) -> Path:
    terrain = TerrainProvider()  # Can't mock this
    mapper = AssetMapper()  # Can't mock this
    # ...
```

#### Property-Based Testing for Complex Logic

**Use Hypothesis for coordinate transforms and math:**
```python
from hypothesis import given, strategies as st

@given(
    x=st.floats(min_value=-1000, max_value=1000),
    y=st.floats(min_value=-1000, max_value=1000)
)
def test_coordinate_transform_is_reversible(x, y):
    """Transform and inverse should return original coordinates."""
    # Act
    transformed = transform_bf1942_to_godot(x, y)
    back = transform_godot_to_bf1942(*transformed)

    # Assert
    assert abs(back[0] - x) < 0.01
    assert abs(back[1] - y) < 0.01
```

#### Test Data Management

**Use Conftest for Shared Fixtures:**
```python
# tools/tests/conftest.py
@pytest.fixture
def sample_registry():
    """Provide sample maps registry for all tests."""
    return {
        "maps": [
            {
                "id": "kursk",
                "display_name": "Kursk",
                "status": "complete",
                "base_map": "MP_Tungsten"
            }
        ],
        "experience_templates": {
            "all_maps": {"name": "All Maps", "game_mode": "Conquest"}
        }
    }

@pytest.fixture
def mock_spatial_file(tmp_path):
    """Create a mock spatial.json file."""
    spatial = tmp_path / "test.spatial.json"
    spatial.write_text(json.dumps({
        "Portal_Dynamic": [],
        "Static": [{"name": "Terrain", "type": "MP_Tungsten_Terrain"}]
    }))
    return spatial
```

#### Fast Tests with Proper Mocking

**Mock Slow Operations:**
```python
# Good - Mock file I/O for speed
@patch('pathlib.Path.read_text')
def test_load_large_spatial_file_quickly(mock_read):
    mock_read.return_value = '{"Portal_Dynamic": []}'  # Instant
    data = load_spatial_file("huge.spatial.json")
    assert data["Portal_Dynamic"] == []

# Don't actually read huge files in tests
```

#### Test Error Messages

**Verify User-Facing Error Messages:**
```python
def test_missing_map_shows_helpful_error_message(capsys):
    # Act
    with pytest.raises(SystemExit) as exc_info:
        main(["portal_convert.py", "--map", "DoesNotExist"])

    # Assert
    assert exc_info.value.code == 1
    captured = capsys.readouterr()
    assert "Map file not found" in captured.err
    assert "Available maps:" in captured.err  # Lists alternatives
```

#### Regression Tests

**Add Tests for Every Bug Fix:**
```python
def test_regression_issue_42_terrain_offset():
    """
    Regression test for Issue #42: Terrain was offset by 500m.

    Bug: TerrainProvider didn't account for mesh center offset.
    Fix: Added mesh bounds detection in terrain_provider.py:135
    """
    # Arrange - Reproduce bug conditions
    terrain = TerrainProvider("MP_Tungsten")

    # Act - This should work now
    height = terrain.get_height_at_position(0, 0)

    # Assert - Verify fix
    assert -100 < height < 100  # Reasonable height, not offset
```

#### Test Performance for Critical Paths

**Ensure Conversion Performance:**
```python
import time

def test_convert_large_map_completes_within_30_seconds(large_map_fixture):
    """Conversion should be fast enough for interactive use."""
    start = time.time()

    result = convert_map(large_map_fixture)

    duration = time.time() - start
    assert duration < 30.0, f"Conversion took {duration}s, expected <30s"
    assert result.exists()
```

#### Continuous Integration Best Practices

**Mark Slow Tests:**
```python
@pytest.mark.slow
def test_full_end_to_end_conversion():
    """Full conversion test (slow)."""
    # This runs in CI but skipped in local dev with pytest -m "not slow"
    pass

# Run fast tests: pytest
# Run all tests: pytest -m ""
```

**Platform-Specific Tests:**
```python
import sys
import pytest

@pytest.mark.skipif(sys.platform != "darwin", reason="macOS-specific test")
def test_macos_gdconverter_export():
    """Test export tool on macOS."""
    pass
```

#### Test Coverage Goals by Module Type

**Target Coverage by Component:**
- **CLI Scripts (create_experience.py, etc.):** 60-70% (focus on main workflows)
- **Core SDK (parsers, mappers, generators):** 85-95% (critical business logic)
- **Utility Scripts (compare_terrains.py):** 40-50% (less critical)
- **Overall Target:** 75%+

**Prioritize:**
1. User-facing code (export tools, portal_convert.py)
2. Complex business logic (coordinate transforms, asset mapping)
3. Error-prone areas (file I/O, parsing)
4. Bug fixes (regression tests)

### Unit Tests

**Focus Areas:**
- CLI entry points (portal_convert.py, create_experience.py, etc.)
- Core business logic (parsers, mappers, generators)
- Coordinate transformations and math
- Error handling and validation

**Examples:**
- Test create_experience.py with valid/invalid inputs
- Validate coordinate transformations with known reference points
- Verify asset mapping with sample data
- Test error messages for missing files

### Integration Tests

**Focus Areas:**
- End-to-end workflows (BF1942 → .tscn → .spatial.json)
- Multiple modules working together
- File I/O operations with real (temporary) files

**Examples:**
- Parse BF1942 .con file → Generate .tscn → Validate structure
- Export .tscn → Create experience → Validate Portal format
- Convert map → Validate all required nodes present

### Manual Testing

**Focus Areas:**
- Visual inspection in Godot editor
- Portal web builder import testing
- In-game gameplay validation

**See:** Testing_Guide.md for complete manual testing procedures

## Common Pitfalls & Solutions

### Issue: Large .glb Files Exceed GitHub Limit

**Solution**: Excluded in `.gitignore` under `GodotProject/raw/models/*.glb`

### Issue: Asset Not Available on Target Map

**Solution**: Check `levelRestrictions` in `asset_types.json`, choose alternative

### Issue: Coordinate Mismatch After Conversion

**Solution**: Use reference landmarks (known buildings) to calibrate transform

### Issue: RFA Extraction Fails

**Solution**: Try multiple extractors (BGA, WinRFA), verify archive integrity

## Development Workflow

### 1. Research Phase
- Analyze BF1942 file structure
- Catalog BF6 available assets
- Identify conversion challenges

### 2. Tool Development
- Build/integrate RFA extractor
- Create coordinate transformer
- Develop object mapping system

### 3. Conversion Pipeline
```
BF1942 RFA → Extract → Parse .con → Map Objects → Transform Coords → Generate .tscn → Test in Godot
```

### 4. Testing & Iteration
- Load in Godot editor
- Verify object placements
- Adjust mappings as needed
- Export and test in Portal

### 5. Documentation
- Update mapping database
- Document lessons learned
- Create templates for future maps

## Quick Reference

### Start Conversion for New Map

1. Extract RFA: Use BGA tool on Windows or `python tools/rfa_extractor.py` (guidance only)
2. Convert map: `python3 tools/portal_convert.py --map MapName --base-terrain MP_Tungsten`
3. Open in Godot: Load `GodotProject/` project, open `levels/MapName.tscn`
4. Manual refinement: Adjust terrain, verify spawns, test gameplay
5. Export: Use BFPortal tab → "Export Current Level"

### Key Commands

```bash
# Extract RFA (guidance tool - use BGA on Windows for actual extraction)
python3 tools/rfa_extractor.py <input.rfa> <output_dir>

# Convert BF1942 map to Portal (master CLI)
python3 tools/portal_convert.py --map <name> --base-terrain <terrain>

# Validate .tscn
python3 tools/portal_validate.py GodotProject/levels/<name>.tscn

# Export in Godot
# Use BFPortal panel → "Export Current Level" button
```

## Resources

- **Portal SDK README**: `/PortalSDK/README.html`
- **Unofficial Portal Docs**: https://github.com/NodotProject/Unofficial-BF6-Portal-SDK-Docs
- **BF6 Asset Catalog**: `/PortalSDK/FbExportData/asset_types.json`
- **Example Mods**: `/PortalSDK/mods/`
- **BF1942 Modding**: https://bfmods.com
- **RFA Tools**: https://github.com/yann-papouin/bga

## RFA Extraction Tools (Phase 1 Research)

### Challenge

BF1942 maps are stored in .rfa (Refractor Archive) format with LZO compression. Full Python parsing requires reverse engineering the binary format.

### Available Tools

**Windows Tools (Recommended for Initial Extraction):**
1. **BGA (Battlefield Game Archive)** - https://github.com/yann-papouin/bga
   - Most comprehensive, written in Pascal/Delphi
   - GUI with file preview, extract, and repack capabilities

2. **WinRFA** - Classic modding tool with simple GUI

3. **rfaUnpack.exe** - Command-line extractor

**Python Libraries:**
- `python-lzo` - LZO decompression support
- No complete Python RFA parser found (as of 2025-10-10)

### Recommended Approach

**Phase 1 (Current):** Use existing Windows tools
- Extract RFAs on Windows gaming PC using BGA
- Copy extracted files to: `bf1942_source/extracted/Kursk/`
- Alternative: Install Wine on Mac to run BGA.exe

**Phase 3 (Future):** Implement Python RFA parser for automation
- Reverse engineer RFA binary format
- Implement header/file table parsing
- Create automated extraction pipeline

See `tools/README.md` for detailed extraction instructions.

## Project Status

**Current Status**: ✅ Production-ready - Kursk conversion complete with 787-test suite

**Completed Milestones**:
- ✅ Phase 1: RFA extraction and BF1942 data analysis
- ✅ Phase 2: Core library architecture (SOLID design)
- ✅ Phase 3: Modular CLI toolset with DRY/SOLID refactoring
- ✅ Phase 4: Kursk map full conversion (95.3% asset accuracy)
- ✅ Sprint 1: Initial implementation
- ✅ Sprint 2: Bug fixes and stabilization
- ✅ Sprint 3: DRY/SOLID refactoring with comprehensive test suite (787 tests, 98% coverage)

**Test Suite**:
- 787 tests (all passing)
- 98% overall code coverage
- Unit tests + integration tests
- See `tools/tests/README.md` and `tools/tests/Coverage_Report.md`

**Next Steps**:
- Test Kursk in Portal web builder and in-game
- Convert additional BF1942 maps (Wake Island, El Alamein, etc.)
- Add support for other Battlefield games (BF Vietnam, BF2, etc.)

---

*Last Updated*: 2025-10-12
*Project Lead*: Zach Atkinson
*AI Assistant*: Claude (Anthropic)
