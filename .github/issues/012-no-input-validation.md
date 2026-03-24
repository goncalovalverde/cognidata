# No Input Validation - Business Logic Not Enforced

## Context
User inputs are not validated beyond Streamlit's basic range checking:

```python
# app.py lines 130-135
age = st.number_input("Edad", min_value=18, max_value=100, value=65)
education_years = st.number_input("Años de Escolaridad", min_value=0, max_value=25, value=12)
laterality = st.selectbox("Lateralidad", ["diestro", "zurdo", "ambidextro"])
```

Missing validations:
- Education years vs age consistency (e.g., 18 years old with 25 years education)
- Duplicate patient detection
- Cross-field validation
- SQL/NoSQL injection (though SQLAlchemy helps)
- Business rule validation

## Impact
- **Invalid data** can enter the system
- **Business logic errors** go undetected
- **Poor UX** - users don't know what valid input looks like
- **Data quality issues** - garbage in, garbage out
- **Report inconsistencies** - bad data creates misleading reports

## Proposed Remediation

### 1. Create Validation Layer

```python
# utils/validators.py
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []

def validate_patient_data(age: int, education_years: int, laterality: str) -> ValidationResult:
    errors = []
    
    # Basic range validation (Streamlit handles this, but belt-and-suspenders)
    if not (18 <= age <= 100):
        errors.append("Edad debe estar entre 18 y 100 años")
    
    if not (0 <= education_years <= 25):
        errors.append("Escolaridad debe estar entre 0 y 25 años")
    
    # Business logic: minimum education for age
    min_education_for_age = max(0, age - 18)  # Rough estimate
    if education_years > age - 4:  # Can't start school before age 4
        errors.append(f"Con {age} años, es improbable tener {education_years} años de escolaridad")
    
    # Validate laterality
    valid_lateralities = ["diestro", "zurdo", "ambidextro"]
    if laterality not in valid_lateralities:
        errors.append(f"Lateralidad debe ser uno de: {', '.join(valid_lateralities)}")
    
    return ValidationResult(is_valid=len(errors) == 0, errors=errors)
```

### 2. Create Validation Display Component

```python
# components/validation.py
import streamlit as st

def show_validation_errors(result: ValidationResult):
    if not result.is_valid:
        for error in result.errors:
            st.error(f"⚠️ {error}")
        return False
    return True

def show_validation_success(message: str = "✓ Datos válidos"):
    st.success(message)
```

### 3. Use in Patient Form

```python
# app.py - Patient form
with st.form("new_patient_form"):
    age = st.number_input("Edad", min_value=18, max_value=100, value=65)
    education_years = st.number_input("Años de Escolaridad", min_value=0, max_value=25, value=12)
    laterality = st.selectbox("Lateralidad", ["diestro", "zurdo", "ambidextro"])
    
    submitted = st.form_submit_button("Guardar Paciente")
    
    if submitted:
        # Validate before saving
        result = validate_patient_data(age, education_years, laterality)
        
        if result.is_valid:
            # Save patient
            save_patient(age, education_years, laterality)
        else:
            show_validation_errors(result)
```

### 4. Add Duplicate Detection

```python
# services/patient_service.py
def check_duplicate_patient(age: int, education_years: int) -> Optional[Patient]:
    """Check if a similar patient already exists.
    
    For anonymous data, we can only match on demographic characteristics.
    """
    return db.query(Patient).filter(
        Patient.age == age,
        Patient.education_years == education_years,
        Patient.created_at > datetime.utcnow() - timedelta(hours=1)
    ).first()
```

## Labels
`validation`, `data-quality`, `ux`, `medium-priority`

## Effort Estimate
3-4 hours
