# Test Coverage Plan: Achieving 75%+ Coverage

> Strategic plan for reaching 75% test coverage across tools/ directory

**Goal:** 75%+ test coverage (commendable by industry standards)
**Current:** 28% overall (1110/3996 statements covered)
**Gap:** 1687 additional statements needed
**Timeline:** Phased approach with checkpoints
**Status:** 🚧 In Progress

---

## Table of Contents

- [Current State](#current-state)
- [Target Breakdown](#target-breakdown)
- [Coverage Strategy](#coverage-strategy)
- [Phase 1: Export Tools (Priority 1)](#phase-1-export-tools-priority-1)
- [Phase 2: CLI Tools (Priority 2)](#phase-2-cli-tools-priority-2)
- [Phase 3: SDK Modules (Priority 3)](#phase-3-sdk-modules-priority-3)
- [Implementation Checklist](#implementation-checklist)
- [Testing Standards](#testing-standards)
- [Progress Tracking](#progress-tracking)
- [Success Criteria](#success-criteria)

---

## Current State

**Overall Coverage:** 28% (tools/ directory)

### Coverage by Component

| Component | Current | Target | Gap | Priority |
|-----------|---------|--------|-----|----------|
| **CLI Scripts** | 0% (0/1995) | 60% (~1197 stmts) | +1197 | High |
| **bfportal SDK** | 56% (1110/2001) | 85% (~1701 stmts) | +591 | Medium |
| **Combined** | 28% (1110/3996) | 75% (~2997 stmts) | +1887 | - |

### Untested Modules (0% Coverage)

**CLI Tools (17 files, 1995 statements):**
- `create_experience.py` (72 stmts) - **PRIORITY 1**
- `create_multi_map_experience.py` (127 stmts) - **PRIORITY 1**
- `export_to_portal.py` (85 stmts) - **PRIORITY 1**
- `portal_convert.py` (220 stmts) - **PRIORITY 2**
- `portal_parse.py` (127 stmts)
- `portal_map_assets.py` (121 stmts)
- `portal_adjust_heights.py` (146 stmts)
- `portal_rebase.py` (92 stmts)
- `portal_validate.py` (179 stmts)
- `rfa_extractor.py` (102 stmts)
- `validate_conversion.py` (45 stmts)
- `validate_tscn.py` (180 stmts)
- `compare_terrains.py` (38 stmts)
- `complete_asset_analysis.py` (229 stmts)
- `filter_real_assets.py` (73 stmts)
- `generate_portal_index.py` (57 stmts)
- `scan_all_maps.py` (102 stmts)

**SDK Modules (0% coverage):**
- `bfportal/indexers/portal_asset_indexer.py` (180 stmts)
- `bfportal/classifiers/asset_classifier.py` (83 stmts)
- `bfportal/orientation/*` (156 stmts total - 4 files)
- `bfportal/engines/refractor/games/bf1942.py` (37 stmts)

### Partially Tested Modules (<60% coverage)

- `bfportal/engines/refractor/refractor_base.py` (41% - 107 missed)
- `bfportal/terrain/terrain_provider.py` (52% - 110 missed)
- `bfportal/validation/tscn_reader.py` (35% - 36 missed)
- `bfportal/validation/validation_orchestrator.py` (9% - 108 missed)

---

## Target Breakdown

### Component-Level Targets

**CLI Scripts: 60% coverage**
- Rationale: Focus on happy path + error handling, skip obscure edge cases
- Target: 1197 statements covered (out of 1995)
- Priority: User-facing tools that customers interact with directly

**bfportal SDK: 85% coverage**
- Rationale: Core business logic requires thorough testing
- Target: 1701 statements covered (out of 2001)
- Priority: Complex algorithms, data transformations, critical infrastructure

**Overall: 75%+ coverage**
- Combined target: 2898+ statements covered (out of 3996)
- This exceeds minimum by ~100 statements for buffer

---

## Coverage Strategy

### Focus Areas (Prioritized)

**Priority 1: Export Tools (284 statements)**
- `create_experience.py` - Wraps spatial data in experience format
- `create_multi_map_experience.py` - Multi-map rotations from registry
- `export_to_portal.py` - All-in-one export pipeline

**Why:** Most user-facing, recently documented, critical workflow

**Priority 2: Main CLI (220 statements)**
- `portal_convert.py` - Master conversion CLI

**Why:** Primary tool for map conversion, high-value testing

**Priority 3: SDK Gaps (891 statements)**
- Complete untested SDK modules
- Improve partially tested modules to 85%+

**Why:** Foundation for all CLI tools, complex business logic

### Testing Approach

**Use AAA Pattern:**
```python
def test_create_experience_with_valid_inputs():
    # Arrange
    spatial_data = {"Portal_Dynamic": [], "Static": []}

    # Act
    result = create_experience("Kursk", spatial_data, "MP_Tungsten", 32)

    # Assert
    assert result["name"] == "Kursk - BF1942 Classic"
```

**Mock External Dependencies:**
- File I/O (Path.read_text, Path.write_text)
- Subprocess calls (gdconverter exports)
- Time-consuming operations

**Test Behavior, Not Implementation:**
- Focus on outputs, not internal method calls
- Use `autospec=True` for mocks
- Avoid brittle tests

---

## Phase 1: Export Tools (Priority 1)

**Goal:** Test the 3 export tools to 60-70% coverage
**Impact:** +170-200 statements → **33-35% overall coverage**

### create_experience.py (72 statements)

**Target:** 60% (~43 statements)

**Test Cases:**
1. ✅ **Happy Path:** Valid spatial file → Creates experience with correct structure
2. ✅ **Base64 Encoding:** Verifies spatial data is base64 encoded
3. ✅ **Map ID Format:** Validates `MP_<Name>-ModBuilderCustom0` format
4. ✅ **Game Mode:** Tests Conquest, Rush, TeamDeathmatch, Breakthrough
5. ✅ **Player Counts:** Tests 16, 32, 64 max players per team
6. ✅ **Custom Mode:** Verifies `ModBuilder_GameMode: 0` is set
7. ❌ **Missing Spatial File:** Raises FileNotFoundError
8. ❌ **Invalid JSON:** Handles corrupted spatial data
9. ❌ **CLI Arguments:** Tests argparse with valid/invalid args
10. ❌ **Output Path:** Verifies experience saved to experiences/ directory

**Files to Create:**
- `tools/tests/test_create_experience.py` (~150-200 lines)

### create_multi_map_experience.py (127 statements)

**Target:** 60% (~76 statements)

**Test Cases:**
1. ✅ **Load Registry:** Reads maps_registry.json correctly
2. ✅ **Filter Maps:** Filters by status="complete"
3. ✅ **Multi-Map Rotation:** Creates mapRotation with multiple entries
4. ✅ **MapIdx Assignment:** Verifies mapIdx=0,1,2,... sequential
5. ✅ **Template Loading:** Uses experience_templates from registry
6. ✅ **Custom Map Selection:** --maps arg overrides template filter
7. ❌ **Missing Spatial Files:** Handles maps without .spatial.json
8. ❌ **Empty Registry:** Handles no matching maps
9. ❌ **Invalid Template:** Template not found in registry
10. ❌ **CLI Arguments:** Tests all command-line options

**Files to Create:**
- `tools/tests/test_create_multi_map_experience.py` (~200-250 lines)
- `tools/tests/fixtures/sample_registry.json` (test data)

### export_to_portal.py (85 statements)

**Target:** 60% (~51 statements)

**Test Cases:**
1. ✅ **All-in-One Export:** Calls export_tscn_to_spatial + create_experience
2. ✅ **Output Files:** Creates both .spatial.json and _Experience.json
3. ✅ **Success Message:** Prints next steps for Portal upload
4. ❌ **Missing .tscn File:** Handles file not found
5. ❌ **Export Failure:** Handles gdconverter export errors
6. ❌ **CLI Arguments:** Tests custom base-map, max-players, etc.
7. ❌ **File Paths:** Verifies correct input/output paths

**Files to Create:**
- `tools/tests/test_export_to_portal.py` (~150-200 lines)

**Shared Fixtures:**
- `tools/tests/conftest.py` additions:
  - `sample_registry()` - Mock maps_registry.json
  - `mock_spatial_file()` - Temp .spatial.json file
  - `mock_tscn_file()` - Temp .tscn file

---

## Phase 2: CLI Tools (Priority 2)

**Goal:** Test portal_convert.py to 60% coverage
**Impact:** +132 statements → **36-38% overall coverage**

### portal_convert.py (220 statements)

**Target:** 60% (~132 statements)

**Test Cases:**
1. ✅ **Full Conversion:** End-to-end map conversion (mocked dependencies)
2. ✅ **CLI Arguments:** All argparse options (--map, --base-terrain, etc.)
3. ✅ **Module Integration:** Calls parse → map → adjust → generate correctly
4. ❌ **Missing Map File:** Handles file not found with helpful error
5. ❌ **Invalid Terrain:** Validates base terrain exists
6. ❌ **Output Path:** Creates .tscn in correct location
7. ❌ **Dry Run Mode:** Tests validation without file writes
8. ❌ **Error Reporting:** Captures and displays errors clearly

**Files to Create:**
- `tools/tests/test_portal_convert.py` (~250-300 lines)

---

## Phase 3: SDK Modules (Priority 3)

**Goal:** Test untested SDK modules + improve partial coverage to 85%
**Impact:** +1385 statements → **70-75% overall coverage**

### Untested SDK Modules

**portal_asset_indexer.py (180 statements) → 70% (~126 stmts)**
- Test Portal asset catalog parsing
- Test JSON/Markdown output generation
- Test asset categorization logic

**asset_classifier.py (83 statements) → 70% (~58 stmts)**
- Test asset type classification
- Test category assignment rules
- Test fallback logic

**orientation/* (156 statements) → 60% (~94 stmts)**
- Test map orientation detection
- Test terrain orientation matching
- Test orientation interfaces

**bf1942.py (37 statements) → 70% (~26 stmts)**
- Test BF1942 game config
- Test map path resolution
- Test era-specific settings

### Improve Partial Coverage Modules

**refractor_base.py (41% → 85%)**
- Add tests for unmocked code paths (107 missed)
- Test error handling branches
- Test edge cases in parsing logic

**terrain_provider.py (52% → 85%)**
- Add tests for height sampling (110 missed)
- Test mesh bounds detection
- Test bilinear interpolation accuracy

**validation_orchestrator.py (9% → 70%)**
- Add integration tests (108 missed)
- Test validation workflows
- Test error reporting

---

## Implementation Checklist

### Phase 1: Export Tools
- [ ] Create `tools/tests/test_create_experience.py`
- [ ] Create `tools/tests/test_create_multi_map_experience.py`
- [ ] Create `tools/tests/test_export_to_portal.py`
- [ ] Add shared fixtures to `tools/tests/conftest.py`
- [ ] Create sample test data files
- [ ] Run coverage: `pytest --cov --cov-report=term-missing`
- [ ] Verify 33-35% overall coverage achieved
- [ ] Commit Phase 1 tests

### Phase 2: CLI Tools
- [ ] Create `tools/tests/test_portal_convert.py`
- [ ] Test all CLI arguments and options
- [ ] Test error handling paths
- [ ] Run coverage: verify 36-38% overall
- [ ] Commit Phase 2 tests

### Phase 3: SDK Modules
- [ ] Create tests for untested SDK modules (5 modules)
- [ ] Improve partial coverage modules (4 modules)
- [ ] Add property-based tests for transforms
- [ ] Run coverage: verify 70-75% overall
- [ ] Commit Phase 3 tests

### Final Verification
- [ ] Run full test suite: `pytest tools/tests`
- [ ] Generate coverage report: `pytest --cov --cov-report=html`
- [ ] Verify 75%+ coverage achieved
- [ ] Update CLAUDE.md with new coverage stats
- [ ] Update Coverage_Report.md
- [ ] Commit final coverage achievement

---

## Testing Standards

**All tests must follow CLAUDE.md testing best practices:**

### ✅ Required Patterns
- AAA Pattern (Arrange-Act-Assert) with blank line separation
- Descriptive test names: `test_<function>_<scenario>_<expected_result>`
- Test independence (no shared mutable state)
- Mock external dependencies only (filesystem, network, subprocess)
- Use `autospec=True` for mocks
- Use pytest fixtures for shared setup
- One concept per test
- Test behavior, not implementation

### ✅ Required Practices
- Type hints in test helper functions
- Docstrings for complex test cases
- Parameterized tests for multiple scenarios (`@pytest.mark.parametrize`)
- Fast tests (mock slow operations)
- Platform-independent tests (use `tmp_path`, not hardcoded paths)
- Clear assertion messages

### ❌ Avoid
- Testing implementation details (internal method calls)
- Brittle tests that break with refactoring
- Shared mutable state between tests
- Real file I/O without `tmp_path`
- Tests that depend on execution order
- Vague test names (`test_export`, `test_error`)

---

## Progress Tracking

**Update this section after each phase:**

### Coverage Milestones

| Milestone | Target | Actual | Date | Status |
|-----------|--------|--------|------|--------|
| Current Baseline | 28% | 28% | 2025-10-12 | ✅ Measured |
| Phase 1 Complete | 33-35% | - | TBD | 🚧 In Progress |
| Phase 2 Complete | 36-38% | - | TBD | ⏳ Pending |
| Phase 3 Complete | 70-75% | - | TBD | ⏳ Pending |
| Final Goal | 75%+ | - | TBD | ⏳ Pending |

### Test Count Progression

| Phase | Tests Added | Total Tests | Coverage Gain |
|-------|-------------|-------------|---------------|
| Baseline | 0 | 241 | - |
| Phase 1 | ~30-40 | 271-281 | +5-7% |
| Phase 2 | ~20-30 | 291-311 | +3-4% |
| Phase 3 | ~80-100 | 371-411 | +35-40% |

---

## Success Criteria

### Phase 1 Success
- ✅ All 3 export tools have 60%+ individual coverage
- ✅ Overall coverage reaches 33-35%
- ✅ All tests follow AAA pattern
- ✅ No brittle tests (implementation-dependent)
- ✅ Fast test execution (<5 seconds for Phase 1 tests)

### Phase 2 Success
- ✅ portal_convert.py has 60%+ coverage
- ✅ Overall coverage reaches 36-38%
- ✅ End-to-end integration test works
- ✅ Error handling paths tested

### Phase 3 Success
- ✅ All untested SDK modules have 60-70% coverage
- ✅ Partial coverage modules reach 85%+
- ✅ Overall coverage reaches 70-75%+
- ✅ Complex algorithms have property-based tests

### Final Success
- ✅ **75%+ overall coverage achieved**
- ✅ All tests pass consistently
- ✅ Coverage report generated (HTML + terminal)
- ✅ Documentation updated with new stats
- ✅ Test suite serves as model for future contributions

---

**Last Updated:** 2025-10-12
**Status:** Phase 1 - In Progress
**Next Action:** Create `test_create_experience.py`

**See Also:**
- [CLAUDE.md](./claude/CLAUDE.md) - Testing best practices
- [Testing_Guide.md](./Testing_Guide.md) - Manual testing procedures
- [Coverage_Report.md](./tools/tests/Coverage_Report.md) - Current coverage details
