# [Critical] Monolithic app.py - Extract into modular pages

## Context
The entire application logic (~1007 lines) lives in a single `app.py` file, violating the Single Responsibility Principle. This creates a God Class anti-pattern where one file handles:
- Patient CRUD operations
- 6 different test forms (TMT-A, TMT-B, TAVEC, Fluidez-FAS, Rey-Copia, Rey-Memoria)
- Dashboard with charts
- PDF generation triggers
- Configuration and backup

## Impact
- **Impossible to test** individual components in isolation
- **High coupling** between UI and business logic
- **Difficult to maintain** or extend with new features
- **No code reuse** possible across pages
- Streamlit's page-based architecture is not being leveraged

## Proposed Remediation

### Phase 1: Create Page Structure
```
app/
  pages/
    __init__.py
    home.py          # Current Inicio page
    patients.py      # Patient management
    tests.py         # Test administration (or split per test)
    dashboard.py     # Analytics and reporting
    config.py        # Settings and backup
  components/
    forms/
      __init__.py
      tmt_form.py
      tavec_form.py
      fluidez_form.py
      rey_form.py
    charts.py
    tables.py
  services/
    patient_service.py
    test_service.py
```

### Phase 2: Extract Business Logic
Move data operations to service layer:
```python
# services/patient_service.py
class PatientService:
    def create_patient(self, age, education, laterality) -> Patient
    def get_patients(self) -> List[Patient]
    def delete_patient(self, patient_id) -> None
```

### Phase 3: Create Shared Components
Extract reusable UI components (forms, charts, tables).

## Labels
`refactoring`, `architecture`, `high-priority`

## Effort Estimate
8-12 hours
