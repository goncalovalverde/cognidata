# Global Service Instances - Testing and DI Issues

## Context
Services are instantiated as module-level singletons, making testing and dependency injection difficult:

```python
# services/audit.py line 193
audit_service = AuditService()

# services/normatives.py line 225
calculator = NormativeCalculator()

# services/pdf_generator.py line 401
pdf_generator = NeuroPsychReport()
```

This pattern hides dependencies and makes it hard to:
- Mock services in tests
- Swap implementations
- Configure service behavior

## Impact
- **Testing is harder** - can't easily inject mock implementations
- **Global state** - services are shared across all requests
- **Configuration is harder** - no way to pass config to constructors
- **Coupling** - consumers import from modules, not abstractions

## Proposed Remediation

### Option 1: Explicit Dependency Injection (Recommended for Streamlit)

```python
# services/__init__.py
from functools import lru_cache

@lru_cache(maxsize=1)
def get_audit_service() -> AuditService:
    return AuditService()

@lru_cache(maxsize=1)
def get_calculator() -> NormativeCalculator:
    return NormativeCalculator()

@lru_cache(maxsize=1)
def get_pdf_generator() -> NeuroPsychReport:
    return NeuroPsychReport()
```

```python
# app.py - explicit initialization
from services import get_audit_service, get_calculator

audit_service = get_audit_service()
calculator = get_calculator()

# In tests:
def test_with_mock_audit():
    mock_audit = MockAuditService()
    # Pass mock to components that need it
```

### Option 2: Service Container Pattern

```python
# services/container.py
class ServiceContainer:
    _instance = None
    
    def __init__(self):
        self._services = {}
    
    def register(self, service_type, factory):
        self._services[service_type] = factory
    
    def get(self, service_type):
        if service_type not in self._services:
            self._services[service_type] = self._services[service_type]()
        return self._services[service_type]
    
    def reset(self):
        """For testing - clear all cached instances"""
        self._services = {}
```

### Option 3: Dependency Injection via Constructor

```python
# components/test_form.py
class TestForm:
    def __init__(self, calculator, audit_service):
        self.calculator = calculator
        self.audit_service = audit_service
    
    def submit_test(self, test_data):
        scores = self.calculator.calculate(...)
        self.audit_service.log_test_create(...)
```

## Labels
`architecture`, `testing`, `refactoring`, `low-priority`

## Effort Estimate
2-3 hours
