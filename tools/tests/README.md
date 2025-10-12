# BFPortal SDK Test Suite

Comprehensive test suite for the BF1942 to BF6 Portal conversion tools.

## Test Statistics

- **Total Tests**: 241
- **Passing**: 237 (98.3%)
- **Overall Coverage**: 64%
- **Test Files**: 9

## Test Structure

### Unit Tests

Individual module tests focusing on isolated functionality:

- **test_asset_mapper.py** (31 tests)
  - Asset mapping with level restrictions
  - Keyword-based fallback matching
  - Terrain element detection
  - Coverage: 92%

- **test_con_parser.py** (30 tests)
  - BF1942 .con file parsing
  - Object template extraction
  - Position/rotation/team parsing
  - Coverage: 77%

- **test_coordinate_offset.py** (14 tests)
  - Centroid calculation
  - Offset and scale transformations
  - Transform preservation
  - Coverage: 100%

- **test_game_config.py** (23 tests)
  - Config file loading
  - Validation and error handling
  - Default value handling
  - Coverage: 100%

- **test_refractor_engine.py** (34 tests)
  - Refractor engine behavior
  - Spawn point identification
  - Team classification
  - Bounds calculation
  - Coverage: 41%

- **test_terrain_provider.py** (21 tests)
  - Height sampling
  - Terrain bounds
  - Custom heightmaps
  - Coverage: 52%

- **test_tscn_generator.py** (16 tests)
  - .tscn file generation
  - Transform formatting
  - Resource management
  - Coverage: 95%

- **test_tscn_utils.py** (23 tests)
  - Transform3D parsing
  - Format validation
  - Roundtrip conversion
  - Coverage: 100%

- **test_validation.py** (36 tests)
  - Spawn count validation
  - Height validation
  - Bounds checking
  - Coverage: 97%

### Integration Tests

End-to-end workflow tests combining multiple modules:

- **test_integration.py** (13 tests)
  - Complete asset mapping pipeline
  - Transform pipeline workflows
  - Config loading → usage flows
  - Full BF1942 → Portal conversion
  - Error propagation
  - Statistics aggregation

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

## Coverage Goals

### High Priority (>90%)

- ✅ **Core Interfaces**: 100% (critical data structures)
- ✅ **Coordinate Transforms**: 100% (position calculations)
- ✅ **TSCN Utils**: 100% (file format handling)
- ✅ **Game Config**: 100% (configuration loading)
- ✅ **Validators**: 97% (quality checks)
- ✅ **TSCN Generator**: 95% (file generation)
- ✅ **Map Rebaser**: 97% (base terrain switching)
- ✅ **Asset Mapper**: 92% (asset lookup)

### Medium Priority (70-89%)

- ✅ **CON Parser**: 77% (BF1942 file parsing)

### Lower Priority (50-69%)

- ⚠️ **Refractor Engine**: 41% (engine-specific logic)
- ⚠️ **Terrain Provider**: 52% (heightmap sampling)
- ⚠️ **Map Comparator**: 67% (validation utilities)

### Future Work (<50%)

- ❌ **Orientation Detection**: 0% (not yet implemented)
- ❌ **TSCN Reader**: 35% (partial implementation)
- ❌ **Validation Orchestrator**: 9% (integration layer)
- ❌ **BF1942 Game**: 0% (game-specific parsing)

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
