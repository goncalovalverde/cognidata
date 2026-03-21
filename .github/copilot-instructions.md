# CogniData - Neuropsychological Testing Application

A Streamlit-based neuropsychological testing platform for managing patient assessments and calculating NEURONORMA normative scores. 100% Python, designed for local tablet/desktop use by neuropsychologists.

## Running the Application

```bash
# Activate virtual environment
source venv/bin/activate

# Run the app
streamlit run app.py
```

Access at `http://localhost:8501` or use the Network URL for tablet access.

## Testing

Run the complete flow verification:

```bash
python test_complete_flow.py
```

Note: This requires existing patients and test data in the database. Create test data through the Streamlit UI first.

## Architecture Overview

### Core Design Pattern
- **Single monolith approach**: All UI, business logic, and data access in one Streamlit app
- **No REST API**: Direct SQLAlchemy database access throughout
- **Session-based state**: Streamlit's session state manages UI state; SQLite handles persistence

### Data Flow
```
User Input → Streamlit Form → SQLAlchemy ORM → SQLite
                ↓
         Normatives Service (real NEURONORMA tables + interpolation)
                ↓
         Dashboard (Plotly charts) OR PDF Generator (ReportLab)
```

### Key Components

**app.py** (~700 lines)
- Main Streamlit application with page-based navigation
- All UI forms and workflows in a single file
- Pages: Inicio, Pacientes, Tests, Dashboard, Configuración

**models/** - SQLAlchemy ORM models
- `Patient`: Anonymous patient data (UUID, age, education, laterality only - GDPR compliant)
- `TestSession`: Individual neuropsychological test results with JSON-serialized fields

**services/normatives.py** - NEURONORMA calculation engine
- Loads real normative tables from JSON files in `data/normative_tables/`
- Implements linear interpolation for raw scores between table entries
- Converts raw scores → Scaled Score (PE) → Percentile → Classification
- Falls back to simulated calculation for tests without tables yet

**services/pdf_generator.py** - Professional PDF reports
- ReportLab-based report generation
- Color-coded results (green/blue/yellow/red by performance level)
- Includes patient data, test results table, clinical observations

**database/connection.py** - SQLAlchemy setup
- SQLite database: `cognidata.db`
- Session management with context managers
- `init_db()` must be called before any database operations

## Neuropsychological Tests Implemented

Six tests with complete NEURONORMA normative calculations:

1. **TMT-A/TMT-B** (Trail Making Test): Time and errors → PE/percentile
2. **TAVEC** (Verbal Learning): 5 trials + interference + recall → PE/percentile  
3. **Fluidez Fonológica F-A-S**: Word count per letter → PE/percentile
4. **Figura de Rey - Copia**: Copy accuracy (0-36 points) → PE/percentile
5. **Figura de Rey - Memoria**: Recall after delay → PE/percentile

### Test Data Structure

Each `TestSession` stores:
- **raw_data**: Test-specific measurements (JSON serialized)
  - TMT: `{tiempo, errores}`
  - TAVEC: `{ensayo_1, ensayo_2, ..., lista_b, recuerdo_inmediato, ...}`
  - Fluidez: `{letra_f, letra_a, letra_s}`
  - Rey: `{puntuacion, tiempo}` or `{puntuacion, tiempo_demora}`
- **calculated_scores**: `{puntuacion_escalar, percentil, z_score, clasificacion, norma_aplicada}`
- **qualitative_data**: `{observaciones, checklist_items}` (clinical notes)

## NEURONORMA Normative Tables

Located in `data/normative_tables/*.json`

### Table Structure
```json
{
  "test_name": "TMT-A",
  "age_ranges": [
    {
      "age_min": 50,
      "age_max": 64,
      "education_ranges": [
        {
          "education_min": 0,
          "education_max": 7,
          "conversion_table": [
            {"raw_score": 30, "pe": 16, "percentile": 93.2},
            ...
          ]
        }
      ]
    }
  ]
}
```

### Adding New Tables
1. Create JSON file in `data/normative_tables/` following existing format
2. Add mapping to `NormativeCalculator.test_files` dict in `normatives.py` line 23
3. Restart application to reload tables

Currently implemented: TMT-A, TAVEC, Fluidez-FAS  
Need tables: TMT-B, Rey-Copia, Rey-Memoria

## Database Schema

**patients**
- `id` (String, UUID primary key)
- `age` (Integer)
- `education_years` (Integer)
- `laterality` (String: diestro/zurdo/ambidextro)
- `created_at` (DateTime)
- `encrypted_metadata` (String, nullable - for future use)

**test_sessions**
- `id` (String, UUID primary key)
- `patient_id` (Foreign key to patients)
- `test_type` (String: 'TMT-A', 'TMT-B', etc.)
- `date` (DateTime)
- `raw_data` (Text, JSON serialized)
- `calculated_scores` (Text, JSON serialized)
- `qualitative_data` (Text, JSON serialized)

### Accessing JSON Fields
```python
session = TestSession(...)
session.set_raw_data({"tiempo": 45, "errores": 2})
data = session.get_raw_data()  # Returns dict
```

## Key Conventions

### 1. GDPR-First Data Model
- **Never store**: Names, DNI, emails, addresses, phone numbers
- **Only store**: Age, education years, laterality (anonymous demographics)
- Patient identification via UUID only
- Deletion cascades from Patient → TestSessions (right to be forgotten)

### 2. Streamlit Page Pattern
All pages in `app.py` follow this structure:
```python
if page == "🧪 Tests":
    st.header("🧪 Realizar Test")
    
    # 1. Patient selection (required for all test operations)
    db = SessionLocal()
    patients = db.query(Patient).all()
    selected = st.selectbox(...)
    
    # 2. Test type selection
    test_type = st.selectbox("Tipo de Test", ["TMT-A", "TMT-B", ...])
    
    # 3. Test-specific form
    with st.form(f"form_{test_type}"):
        # Test-specific fields
        submitted = st.form_submit_button("💾 Calcular y Guardar")
        
        if submitted:
            # 4. Create TestSession
            session = TestSession(patient_id=..., test_type=...)
            session.set_raw_data({...})
            
            # 5. Calculate NEURONORMA scores
            result = calculator.calculate(test_type, raw_score, age, education)
            session.set_calculated_scores(result)
            
            # 6. Save and show results
            db.add(session)
            db.commit()
            st.success(f"PE: {result['puntuacion_escalar']}")
    
    db.close()
```

### 3. Normative Calculation Pattern
```python
from services.normatives import calculator

# Extract the appropriate raw score for each test
if test_type == "TMT-A":
    raw_score = tiempo_segundos  # Lower is better
elif test_type == "TAVEC":
    raw_score = sum(ensayos_1_a_5)  # Higher is better
elif test_type == "Fluidez-FAS":
    raw_score = letra_f + letra_a + letra_s

# Calculate always uses same interface
result = calculator.calculate(
    test_type=test_type,
    raw_score=raw_score,
    age=patient.age,
    education_years=patient.education_years
)

# Result structure is consistent
{
    'puntuacion_escalar': 14,      # PE: 1-19, mean=10, SD=3
    'percentil': 86.4,             # 0-100
    'z_score': 1.1,                # Standard deviations from mean
    'clasificacion': 'Superior',   # Superior/Normal/Limítrofe/Deficitario
    'norma_aplicada': {
        'fuente': 'NEURONORMA',    # or 'Simulado'
        'test': 'TMT-A',
        'rango_edad': '65-100',
        'rango_educacion': '8-12'
    }
}
```

### 4. PDF Generation Pattern
```python
from services.pdf_generator import pdf_generator

# Prepare patient data dict
patient_dict = {
    'id': patient.id,
    'age': patient.age,
    'education_years': patient.education_years,
    'laterality': patient.laterality
}

# Prepare sessions data (list of dicts)
sessions_data = [
    {
        'test_type': session.test_type,
        'date': session.date,
        'raw_data': session.get_raw_data(),
        'calculated_scores': session.get_calculated_scores(),
        'qualitative_data': session.get_qualitative_data()
    }
    for session in sessions
]

# Generate PDF
pdf_path = pdf_generator.generate_report(
    patient_data=patient_dict,
    sessions_data=sessions_data
)

# pdf_path is in reports/ directory
```

### 5. Database Session Management
Always use context pattern:
```python
db = SessionLocal()
try:
    # Query and operations
    patients = db.query(Patient).filter(...).all()
    db.add(new_object)
    db.commit()
finally:
    db.close()
```

In Streamlit context, sessions are typically opened at page start and closed at page end.

### 6. Plotly Chart Pattern
Dashboard uses two main chart types:

**Radar Chart** (Cognitive Profile):
```python
fig = go.Figure(data=go.Scatterpolar(
    r=[pe1, pe2, pe3, ...],         # Scaled scores
    theta=['TMT-A', 'TMT-B', ...],   # Test names
    fill='toself'
))
fig.add_trace(go.Scatterpolar(
    r=[10, 10, 10, ...],  # Population mean line
    theta=test_names,
    line=dict(dash='dash', color='green')
))
```

**Bar Chart** (Percentiles with color coding):
```python
colors = ['#22c55e' if p >= 75 else '#3b82f6' if p >= 25 else 
          '#eab308' if p >= 10 else '#ef4444' for p in percentiles]
          
fig = go.Figure(data=go.Bar(
    x=test_names,
    y=percentiles,
    marker_color=colors
))
```

## Project Structure Decisions

### Why Streamlit (not Next.js + FastAPI)?
- **Target user**: Neuropsychologist using local tablet/desktop
- **Deployment**: Local only, no public hosting needed
- **Development speed**: 10x faster (no webpack, no dual codebases)
- **Maintenance**: Single Python codebase vs JavaScript + Python
- **Scientific libraries**: Native NumPy/SciPy/Plotly integration

### Why SQLite (not PostgreSQL)?
- **Portability**: Single `.db` file, easy backup
- **No server**: Zero infrastructure for local use
- **Sufficient scale**: Hundreds of patients, thousands of tests (acceptable for single practitioner)
- **SQLAlchemy ORM**: Can migrate to PostgreSQL later if needed without code changes

### Why Monolith (not microservices)?
- **Simplicity**: All code in ~700 lines across 8 files
- **Performance**: No network overhead for test calculations
- **Debugging**: Single stack trace, no distributed logging
- **Deployment**: `streamlit run app.py` - that's it

## Common Development Tasks

### Add a New Neuropsychological Test

1. **Update test type options** in `app.py`:
   ```python
   test_type = st.selectbox("Tipo de Test", [
       "TMT-A", "TMT-B", "TAVEC", "Fluidez-FAS", 
       "Rey-Copia", "Rey-Memoria",
       "New-Test"  # Add here
   ])
   ```

2. **Add form fields** in the Tests page:
   ```python
   elif test_type == "New-Test":
       with st.form("form_new_test"):
           field1 = st.number_input("Field 1", ...)
           field2 = st.number_input("Field 2", ...)
           submitted = st.form_submit_button("💾 Calcular y Guardar")
           
           if submitted:
               raw_score = calculate_raw_score(field1, field2)
               # ... standard pattern
   ```

3. **Create normative table** in `data/normative_tables/new_test.json`

4. **Update calculator mapping** in `services/normatives.py`

5. **Add to Dashboard charts** - test name will auto-appear in queries

### Modify Normative Calculation Logic

All calculation logic is in `services/normatives.py`:
- **Real tables**: `_calculate_from_table()` handles interpolation
- **Simulated**: `_calculate_simulated()` for fallback
- **PE to percentile**: `_pe_to_percentile()` conversion
- **Classification**: `_get_classification()` thresholds

### Customize PDF Report Format

Edit `services/pdf_generator.py`:
- **Styles**: `_get_styles()` defines fonts and colors
- **Header**: `_add_header()` 
- **Patient section**: `_add_patient_info()`
- **Results table**: `_add_test_results_table()` with color coding
- **Footer**: `_add_footer()`

Change colors by modifying hex codes in color mappings.

### Add Clinical Checklist Items

Checklist data is stored in `qualitative_data` JSON field:
```python
session.set_qualitative_data({
    'observaciones': "Clinical notes...",
    'checklist': {
        'atencion_sostenida': True,
        'inhibicion_respuesta': False,
        'perseveraciones': True
    }
})
```

Add checklist UI in the test forms section of `app.py`.

## Backup and Data Management

**Manual Backup** (currently implemented):
- Configuration page → "Crear Backup Ahora"
- Copies `cognidata.db` to `backups/cognidata_YYYYMMDD_HHMMSS.db`

**Restore**:
```bash
cp backups/cognidata_20260318_120000.db cognidata.db
```

**Future**: Automated scheduled backups planned (see roadmap in README.md)

## Interpreting Scores

**Puntuación Escalar (PE)**:
- Scale: 1-19
- Mean: 10
- SD: 3
- 13-19: Superior
- 7-12: Normal  
- 4-6: Limítrofe (borderline, needs monitoring)
- 1-3: Deficitario (impaired, intervention recommended)

**Percentiles**:
- P75+: Superior (top 25% of population)
- P25-P74: Normal (middle 50%)
- P10-P24: Limítrofe (bottom 25% but not impaired)
- <P10: Deficitario (bottom 10%, clinically significant)

**Z-scores**: Standard deviations from mean (0 = average, +1 = one SD above)

## Important Notes

### Data Privacy (GDPR Compliance)
- This codebase implements privacy-by-design
- Never add fields for personal identifiers to Patient model
- All patient references use UUID only
- Database can be shared for research (already anonymized)
- Deletion is permanent and cascades to all related test sessions

### Clinical Validation
- Current NEURONORMA tables are **approximations** from literature
- **Before clinical use**: Verify against official NEURONORMA publications
- Consider regional variations (Catalonia vs Madrid vs other Spanish regions)
- Age/education ranges may differ by publication version

### Tablet Usage
- Streamlit works perfectly on iPad/Android tablets
- Use Network URL shown in console (e.g., `http://192.168.1.236:8501`)
- Both devices must be on same WiFi network
- Touch interface fully supported (forms, buttons, charts)

### Known Limitations
- **No authentication**: App assumes single trusted user on local network
- **No multi-user**: SQLite handles concurrent reads but limit concurrent writes
- **No undo**: Test deletions are permanent (database backups recommended)
- **Limited export**: PDF only, no CSV/Excel export yet
