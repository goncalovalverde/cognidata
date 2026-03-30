# CogniData Testing Guide

## Overview

CogniData uses **pytest** for comprehensive unit and integration testing. All service layers have automated tests covering happy paths, edge cases, and error handling.

## Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_auth.py             # Authentication tests
├── test_database.py         # Database connection tests
├── test_models.py           # Model validation tests
├── test_normatives.py       # Normative calculation tests
└── test_patient_protocol_service.py  # Protocol service tests (NEW)
```

## Running Tests

### All Tests
```bash
cd /Users/grumbler/devel/cognidata
source venv/bin/activate
python -m pytest tests/ -v
```

### Specific Test File
```bash
python -m pytest tests/test_patient_protocol_service.py -v
```

### Specific Test Class
```bash
python -m pytest tests/test_patient_protocol_service.py::TestPatientProtocolServiceAssign -v
```

### Specific Test Case
```bash
python -m pytest tests/test_patient_protocol_service.py::TestPatientProtocolServiceAssign::test_assign_protocol_creates_new_assignment -v
```

### Quiet Mode (Summary Only)
```bash
python -m pytest tests/ -q
```

### With Coverage Report
```bash
pip install pytest-cov
python -m pytest tests/ --cov=services --cov=models
```

## Current Test Coverage

| Module | Tests | Status |
|--------|-------|--------|
| PatientProtocolService | 27 | ✅ PASSING |
| NormativeCalculator | 11 | ✅ PASSING |
| Database Connection | 9 | ✅ PASSING |
| Models | 8 | ✅ PASSING |
| Authentication | 6 | ✅ PASSING |
| **TOTAL** | **84** | **✅ ALL PASSING** |

## Test Organization

### Test Classes

Tests are organized by functionality:

```python
class TestPatientProtocolServiceAssign:
    """Tests for assign_protocol() method"""
    
    def test_assign_protocol_creates_new_assignment(self):
        """Test creating a new assignment"""
        
    def test_assign_protocol_returns_existing_assignment(self):
        """Test idempotence - existing assignment returned"""
```

### Naming Conventions

- **File**: `test_<module>.py`
- **Class**: `Test<FunctionName>`
- **Method**: `test_<action>_<scenario>`

Examples:
- `test_assign_protocol_creates_new_assignment()` - creates new
- `test_assign_protocol_returns_existing_assignment()` - idempotent
- `test_update_protocol_status_returns_none_if_not_found()` - missing resource

### Arrange-Act-Assert Pattern

All tests follow AAA pattern:

```python
def test_assign_protocol_creates_new_assignment(self, mock_session_local):
    # Arrange - Set up test data and mocks
    patient_id = str(uuid4())
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db
    
    # Act - Call the function
    result = PatientProtocolService.assign_protocol(patient_id, protocol_id)
    
    # Assert - Verify the result
    assert result.status == "pending"
    mock_db.commit.assert_called_once()
```

## Fixtures

Fixtures are defined in `conftest.py` and reused across tests:

### Common Fixtures

```python
@pytest.fixture
def sample_patient_data():
    """Sample patient data"""
    return {
        "age": 65,
        "education_years": 12,
        "laterality": "diestro",
    }

@pytest.fixture
def sample_protocol_data():
    """Sample protocol data"""
    return {
        "name": "Screening Cognitivo",
        "description": "Protocol para rastreio inicial",
        "category": "Rastreio",
    }

@pytest.fixture
def sample_patient_id():
    """Sample patient UUID"""
    from uuid import uuid4
    return str(uuid4())

@pytest.fixture
def sample_protocol_id():
    """Sample protocol UUID"""
    from uuid import uuid4
    return str(uuid4())
```

### Using Fixtures

```python
def test_some_function(self, sample_patient_data, sample_protocol_id):
    # Fixtures are automatically injected
    age = sample_patient_data["age"]
    # ...
```

## Mocking Strategy

### Database Mocking

Use `@patch` decorator to mock `SessionLocal`:

```python
@patch("services.patient_protocol_service.SessionLocal")
def test_assign_protocol(self, mock_session_local):
    mock_db = MagicMock()
    mock_session_local.return_value = mock_db
    
    # Mock query chain
    mock_db.query.return_value.filter.return_value.first.return_value = None
    
    # Call function
    result = PatientProtocolService.assign_protocol(...)
    
    # Verify database calls
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
```

### Object Mocking

Use `MagicMock(spec=ClassName)` for type safety:

```python
mock_protocol = MagicMock(spec=Protocol)
mock_protocol.id = str(uuid4())
mock_protocol.name = "Test Protocol"
```

### Session Management Verification

Always verify session cleanup:

```python
mock_db.close.assert_called_once()  # Ensure session closed
```

## PatientProtocolService Tests

### Test Coverage (27 tests)

#### assign_protocol() - 4 tests
- ✅ Creates new assignment when none exists
- ✅ Returns existing assignment (idempotent)
- ✅ Respects custom assigned_by value
- ✅ Closes session on error

#### get_patient_protocols() - 3 tests
- ✅ Returns list of protocols
- ✅ Returns empty list when none assigned
- ✅ Uses joinedload for eager-loading relationships

#### update_protocol_status() - 4 tests
- ✅ Changes protocol status
- ✅ Supports "completed" status
- ✅ Returns None if assignment not found
- ✅ Closes session on error

#### unassign_protocol() - 3 tests
- ✅ Deletes protocol assignment
- ✅ Returns False if not found
- ✅ Closes session on error

#### get_available_protocols() - 2 tests
- ✅ Excludes already-assigned protocols
- ✅ Returns all when none assigned

#### get_protocol_completion_status() - 6 tests
- ✅ Returns "empty" when no tests in protocol
- ✅ Returns "pending" when 0 tests completed
- ✅ Returns "in_progress" when some completed
- ✅ Returns "completed" when all tests done
- ✅ Returns None if protocol not found
- ✅ Calculates percentage correctly

#### get_patient_protocols_for_protocol() - 3 tests
- ✅ Returns list of assignments
- ✅ Returns empty list if none
- ✅ Uses joinedload for eager-loading

#### Integration Tests - 2 tests
- ✅ assign → get workflow
- ✅ Status lifecycle: pending → in_progress → completed

## Best Practices

### 1. Keep Tests Isolated
- Each test should be independent
- Don't rely on test execution order
- Clean up resources in `finally` blocks

### 2. Use Descriptive Names
```python
# ✅ Good - Clear what's being tested
def test_update_protocol_status_returns_none_if_not_found(self):
    
# ❌ Bad - Vague
def test_update_status(self):
```

### 3. Test One Thing
```python
# ✅ Good - One assertion per test
def test_assign_protocol_sets_pending_status(self):
    result = PatientProtocolService.assign_protocol(...)
    assert result.status == "pending"

# ❌ Bad - Multiple concerns
def test_assign_protocol(self):
    result = PatientProtocolService.assign_protocol(...)
    assert result.status == "pending"
    assert result.assigned_by == "system"
    assert db.commit.called
```

### 4. Mock External Dependencies
```python
# ✅ Good - Mocks database
@patch("services.patient_protocol_service.SessionLocal")
def test_something(self, mock_session):
    # Test doesn't depend on real DB

# ❌ Bad - Uses real database
def test_something(self):
    # Slow, fragile, requires DB setup
```

### 5. Verify Error Cases
```python
def test_unassign_protocol_returns_false_if_not_found(self):
    """Test missing resource handling"""
    result = PatientProtocolService.unassign_protocol("p_id", "pr_id")
    assert result is False
```

### 6. Test Session Management
```python
def test_closes_session_on_error(self, mock_session_local):
    """Verify cleanup even on exception"""
    mock_db.query.side_effect = Exception("DB error")
    
    with pytest.raises(Exception):
        PatientProtocolService.assign_protocol(...)
    
    mock_db.close.assert_called_once()  # Cleanup verified
```

## Common Patterns

### Testing with Multiple Mock Returns

```python
call_count = [0]
def mock_query_impl(model):
    query_mock = MagicMock()
    if call_count[0] == 0:
        # First call returns X
        query_mock.filter.return_value.all.return_value = [("id",)]
    else:
        # Second call returns Y
        query_mock.filter.return_value.all.return_value = [object]
    call_count[0] += 1
    return query_mock

mock_db.query = mock_query_impl
```

### Testing Query Chains

```python
mock_query = MagicMock()
mock_filter = MagicMock()
mock_options = MagicMock()

mock_db.query.return_value = mock_query
mock_query.filter.return_value = mock_filter
mock_filter.options.return_value = mock_options
mock_options.all.return_value = [mock_obj]
```

### Verifying Method Calls

```python
# Single call
mock_db.commit.assert_called_once()

# Not called
mock_db.delete.assert_not_called()

# Multiple calls
assert mock_db.commit.call_count >= 2

# Called with specific args
mock_db.add.assert_called_once_with(expected_obj)
```

## Debugging Tests

### Run with Full Traceback
```bash
python -m pytest tests/ --tb=long
```

### Run with Print Output
```bash
python -m pytest tests/ -s  # Shows print() statements
```

### Run in Debug Mode
```bash
python -m pytest tests/ --pdb  # Drops to debugger on failure
```

### List Tests Without Running
```bash
python -m pytest tests/ --collect-only
```

## Future Testing Goals

1. **Coverage Report**: Target 80%+ code coverage
2. **Integration Tests**: Test complete workflows end-to-end
3. **E2E Tests**: Streamlit UI testing
4. **Performance Tests**: Check response times
5. **CI Pipeline**: GitHub Actions for automated testing

## References

- [pytest Documentation](https://docs.pytest.org/)
- [unittest.mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Pytest Fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)

## Quick Links

- **Run All Tests**: `python -m pytest tests/ -v`
- **Run Single File**: `python -m pytest tests/test_patient_protocol_service.py -v`
- **Quiet Output**: `python -m pytest tests/ -q`
- **With Coverage**: `python -m pytest tests/ --cov=services`
