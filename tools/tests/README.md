# BFPortal SDK Test Suite

Comprehensive test suite for the BF1942 to BF6 Portal conversion tools.

## Test Statistics

- **Total Tests**: 787
- **Passing**: 787 (100%)
- **Overall Coverage**: 98%
- **Test Files**: 31

## Test Structure

The test suite is organized into **31 test files** covering all aspects of the BF1942 to BF6 Portal conversion pipeline.

### CLI Tools Tests (230 tests)

Command-line interface tools:

- **cli/test_validate_tscn.py** (61 tests) - TSCN file validation
- **cli/test_portal_validate.py** (41 tests) - Portal map validation
- **cli/test_portal_parse.py** (38 tests) - Portal parsing CLI
- **cli/test_portal_convert.py** (25 tests) - Conversion CLI
- **cli/test_validate_conversion.py** (21 tests) - Conversion validation
- **cli/test_portal_rebase.py** (19 tests) - Map rebasing CLI
- **cli/test_create_multi_map_experience.py** (19 tests) - Multi-map experiences
- **cli/test_create_experience.py** (14 tests) - Experience creation
- **cli/test_export_to_portal.py** (11 tests) - Portal export

### Validation Tests (169 tests)

Map and data validation:

- **validation/test_tscn_reader.py** (45 tests) - TSCN parsing
- **validation/test_map_comparator.py** (23 tests) - Map comparison
- **validation/test_validation.py** (22 tests) - Core validators
- **validation/test_validation_orchestrator.py** (13 tests) - Validation orchestration

### Orientation Detection Tests (81 tests)

Map and terrain orientation:

- **orientation/test_terrain_orientation_detector.py** (40 tests) - Terrain orientation
- **orientation/test_map_orientation_detector.py** (24 tests) - Map orientation
- **orientation/test_orientation.py** (17 tests) - Orientation matching

### Parsing & Engine Tests (88 tests)

BF1942 file parsing and engine logic:

- **parsers/test_con_parser.py** (44 tests) - .con file parsing
- **engines/refractor/test_refractor_engine.py** (24 tests) - Refractor engine core
- **engines/refractor/games/test_bf1942.py** (22 tests) - BF1942 game logic
- **engines/refractor/test_refractor_parsing.py** (18 tests) - Refractor parsing

### Asset Management Tests (92 tests)

Asset classification, mapping, and indexing:

- **classifiers/test_asset_classifier.py** (34 tests) - Asset classification
- **mappers/test_asset_mapper.py** (32 tests) - Asset mapping
- **indexers/test_portal_asset_indexer.py** (26 tests) - Asset indexing

### Terrain Tests (41 tests)

Heightmap and terrain processing:

- **terrain/test_terrain_provider.py** (27 tests) - Terrain providers
- **terrain/test_mesh_terrain_provider.py** (14 tests) - Mesh terrain

### Transform Tests (35 tests)

Coordinate and map transformations:

- **transforms/test_coordinate_offset.py** (19 tests) - Coordinate transforms
- **transforms/test_map_rebaser.py** (16 tests) - Map rebasing

### Generator Tests (25 tests)

Map file generation:

- **generators/test_tscn_generator.py** (25 tests) - .tscn generation

### Utility Tests (21 tests)

Helper utilities:

- **utils/test_tscn_utils.py** (21 tests) - TSCN utilities

### Core Infrastructure Tests (19 tests)

Core data structures and configuration:

- **core/test_game_config.py** (19 tests) - Configuration loading

### Integration Tests (13 tests)

End-to-end workflows:

- **integration/test_integration.py** (13 tests) - Full pipeline tests

## Running Tests

### Run All Tests

```bash
python3 -m pytest tools/tests/ -v
```

### Run Specific Test File

```bash
python3 -m pytest tools/tests/test_asset_mapper.py -v
```

### Run Specific Test Class

```bash
python3 -m pytest tools/tests/test_asset_mapper.py::TestAssetMapperBasicMapping -v
```

### Run Specific Test

```bash
python3 -m pytest tools/tests/test_asset_mapper.py::TestAssetMapperBasicMapping::test_map_asset_direct_mapping -v
```

### Run with Short Traceback

```bash
python3 -m pytest tools/tests/ -v --tb=short
```

### Run with Coverage

```bash
# Terminal report
python3 -m pytest tools/tests/ --cov=tools/bfportal --cov-report=term-missing

# HTML report
python3 -m pytest tools/tests/ --cov=tools/bfportal --cov-report=html:tools/tests/htmlcov

# View HTML report
open tools/tests/htmlcov/index.html
```

### Run Only Integration Tests

```bash
python3 -m pytest tools/tests/test_integration.py -v
```

### Run Tests Matching Pattern

```bash
# Run all tests with "mapping" in name
python3 -m pytest tools/tests/ -k "mapping" -v

# Run all tests with "transform" in name
python3 -m pytest tools/tests/ -k "transform" -v
```

## Test Fixtures

Shared test fixtures are defined in `conftest.py`:

### Sample Data Fixtures

- **sample_map_context**: Default MapContext for WW2/open_terrain
- **sample_portal_assets**: Portal asset_types.json with test assets
- **sample_bf1942_mappings**: BF1942 → Portal mappings JSON
- **sample_fallback_keywords**: Asset fallback keywords config
- **sample_game_config**: BF1942 game configuration
- **sample_map_config**: Kursk map configuration
- **sample_conversion_config**: Conversion parameters

All fixtures use pytest's `tmp_path` for isolated, temporary test data.

## Coverage Status

### Overall: 98% Coverage

The test suite has achieved **exceptional coverage** across all modules:

### Perfect Coverage (100%)

- ✅ **Core Interfaces**: 100% (critical data structures)
- ✅ **Coordinate Transforms**: 100% (position calculations)
- ✅ **TSCN Utils**: 100% (file format handling)
- ✅ **Game Config**: 100% (configuration loading)
- ✅ **Validators**: 100% (quality checks)
- ✅ **TSCN Generator**: 100% (file generation)
- ✅ **Map Rebaser**: 100% (base terrain switching)
- ✅ **CON Parser**: 100% (BF1942 file parsing)
- ✅ **Map Comparator**: 100% (validation utilities)
- ✅ **TSCN Reader**: 100% (file reading)
- ✅ **Orientation Detection**: 100% (all modules)
- ✅ **BF1942 Game**: 100% (game-specific parsing)

### Excellent Coverage (90-99%)

- ✅ **Refractor Engine**: 99% (engine-specific logic)
- ✅ **Validation Orchestrator**: 99% (integration layer)
- ✅ **Asset Classifier**: 99% (classification logic)
- ✅ **Terrain Provider**: 98% (heightmap sampling)
- ✅ **Portal Asset Indexer**: 93% (asset indexing)
- ✅ **Asset Mapper**: 92% (asset lookup)

**All critical paths have 100% coverage. Remaining gaps are in rare edge cases and non-critical error handling.**

## Adding New Tests

### 1. Unit Test Structure

```python
#!/usr/bin/env python3
"""Tests for new_module."""

import pytest

from bfportal.module import NewClass


class TestNewClass:
    """Test cases for NewClass."""

    def test_basic_functionality(self):
        """Test basic functionality works."""
        obj = NewClass()
        result = obj.do_something()
        assert result is not None
```

### 2. Using Fixtures

```python
def test_with_sample_data(self, sample_portal_assets):
    """Test using fixture data."""
    obj = NewClass(sample_portal_assets)
    assert obj.is_initialized()
```

### 3. Testing Exceptions

```python
def test_raises_error_on_invalid_input(self):
    """Test proper error handling."""
    obj = NewClass()
    with pytest.raises(ValueError, match="Invalid input"):
        obj.process(None)
```

### 4. Parametrized Tests

```python
@pytest.mark.parametrize("input_val,expected", [
    (0, False),
    (1, True),
    (100, True),
])
def test_multiple_cases(self, input_val, expected):
    """Test with multiple parameter sets."""
    result = process_value(input_val)
    assert result == expected
```

### 5. Integration Tests

```python
class TestCompleteWorkflow:
    """End-to-end workflow test."""

    def test_full_pipeline(self, sample_data):
        """Test complete pipeline from start to finish."""
        # Step 1: Setup
        component_a = ComponentA()
        component_b = ComponentB()

        # Step 2: Process
        intermediate = component_a.process(sample_data)
        final = component_b.transform(intermediate)

        # Step 3: Verify
        assert final.is_valid()
        assert len(final.results) > 0
```

## Continuous Integration

### Pre-Commit Hook

Run tests before committing:

```bash
# In .git/hooks/pre-commit
#!/bin/bash
python3 -m pytest tools/tests/ -v --tb=short
```

### CI Pipeline

Typical CI pipeline steps:

1. Install dependencies: `pip install -r requirements.txt`
2. Run tests: `pytest tools/tests/ -v`
3. Generate coverage: `pytest --cov=tools/bfportal --cov-report=xml`
4. Upload coverage to code quality tools

## Test Organization Principles

### DRY (Don't Repeat Yourself)

- Shared fixtures in `conftest.py`
- Reusable test utilities
- Parametrized tests for similar cases

### Arrange-Act-Assert

```python
def test_example(self):
    # Arrange: Setup test data
    mapper = AssetMapper(assets)

    # Act: Execute the operation
    result = mapper.map_asset("tree", context)

    # Assert: Verify the outcome
    assert result.type == "Tree_Pine"
```

### Single Responsibility

Each test validates one specific behavior or scenario.

### Descriptive Names

Test names clearly describe what is being tested:

- ✅ `test_map_asset_with_level_restrictions_available`
- ❌ `test_map_asset_case2`

## Coverage Analysis

### Viewing Coverage Report

```bash
# Generate HTML coverage report
python3 -m pytest tools/tests/ --cov=tools/bfportal --cov-report=html:tools/tests/htmlcov

# Open in browser
open tools/tests/htmlcov/index.html
```

The HTML report shows:

- Line-by-line coverage highlighting
- Branch coverage
- Missing lines
- Coverage percentages per file

### Coverage Interpretation

- **High Coverage (>90%)**: Well-tested, production-ready
- **Medium Coverage (70-90%)**: Core paths tested, edge cases may be missing
- **Low Coverage (<70%)**: Significant testing gaps, higher risk

### Improving Coverage

Focus on:

1. **Untested branches**: if/else paths not executed
2. **Exception handling**: error cases not triggered
3. **Edge cases**: boundary values, empty inputs, null values
4. **Integration scenarios**: component interactions

## Common Patterns

### Temporary Files

```python
def test_with_temp_file(self, tmp_path):
    """Test using pytest's tmp_path fixture."""
    test_file = tmp_path / "test.json"
    test_file.write_text('{"key": "value"}')

    result = load_json(test_file)
    assert result["key"] == "value"
```

### Mocking

```python
from unittest.mock import Mock, patch

def test_with_mock(self):
    """Test using mocks."""
    mock_terrain = Mock()
    mock_terrain.get_height_at.return_value = 50.0

    obj = HeightAdjuster(mock_terrain)
    result = obj.adjust(Transform(Vector3(0, 0, 0)))

    assert result.position.y == 50.0
```

### Comparing Floats

```python
def test_float_comparison(self):
    """Test with floating point values."""
    result = calculate_distance(0, 0, 3, 4)
    assert result == pytest.approx(5.0, abs=0.01)
```

## Troubleshooting

### Import Errors

Ensure the tools directory is in the Python path:

```python
# In conftest.py
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
```

### Fixture Not Found

Check that fixtures are defined in:

1. `conftest.py` in same directory
2. `conftest.py` in parent directory
3. Test file itself

### Test Discovery Issues

pytest looks for:

- Files matching `test_*.py` or `*_test.py`
- Classes matching `Test*`
- Functions matching `test_*`

### Slow Tests

Use markers to skip slow tests during development:

```python
@pytest.mark.slow
def test_expensive_operation(self):
    """This test takes a long time."""
    pass

# Run without slow tests
pytest -m "not slow"
```

## Best Practices

1. **Test Independence**: Each test should run independently
2. **Fast Tests**: Keep unit tests under 100ms
3. **Clear Failures**: Assert messages should explain what failed
4. **Minimal Setup**: Only create what's needed for the test
5. **Cleanup**: Use fixtures and `tmp_path` for automatic cleanup
6. **Documentation**: Docstrings explain what is being tested
7. **Deterministic**: Tests should produce same results every run
8. **Meaningful Data**: Use realistic test data, not just `foo`/`bar`

## Resources

- [pytest Documentation](https://docs.pytest.org/)
- [pytest-cov Documentation](https://pytest-cov.readthedocs.io/)
- [Python unittest.mock](https://docs.python.org/3/library/unittest.mock.html)
- [Testing Best Practices](https://testdriven.io/blog/testing-best-practices/)

## Contributing

When adding new functionality:

1. Write tests first (TDD approach)
2. Ensure tests pass locally
3. Aim for >90% coverage on new code
4. Add integration tests for workflows
5. Update this README if adding new test categories
