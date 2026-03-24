# Long Method - _build_test_results Needs Refactoring

## Context
The `_build_test_results` method in `services/pdf_generator.py` is 85 lines and does too much:

```python
# services/pdf_generator.py lines 188-273
def _build_test_results(self, test_sessions: List[Dict]) -> List:
    """Construir sección de resultados de tests"""
    # 1. Creates subtitle paragraph
    # 2. Handles empty test_sessions case
    # 3. Builds summary table header
    # 4. Iterates through sessions to build rows
    # 5. Extracts scores from each session
    # 6. Applies conditional row colors
    # 7. Creates and styles the Table object
    # 8. Builds individual test detail sections
```

This violates the Single Responsibility Principle - one method handling multiple concerns.

## Impact
- **Hard to understand** - method does many different things
- **Hard to test** - can't test individual behaviors in isolation
- **Hard to modify** - changing table format affects everything
- **Code duplication risk** - similar patterns in dashboard and PDF

## Proposed Remediation

```python
# services/pdf_generator.py

def _build_test_results(self, test_sessions: List[Dict]) -> List:
    """Build the complete test results section"""
    elements = []
    elements.extend(self._build_results_header())
    
    if not test_sessions:
        elements.extend(self._build_no_data_message())
        return elements
    
    elements.extend(self._build_results_summary_table(test_sessions))
    elements.append(Spacer(1, 0.5*cm))
    elements.extend(self._build_results_detail_sections(test_sessions))
    
    return elements

def _build_results_header(self) -> List:
    """Create the section header"""
    return [Paragraph("Resultados de Evaluación", self.styles['CustomHeading'])]

def _build_no_data_message(self) -> List:
    """Show message when no tests available"""
    return [Paragraph("<i>No hay datos de tests disponibles</i>", 
                      self.styles['CustomBody'])]

def _build_results_summary_table(self, test_sessions: List[Dict]) -> List:
    """Build the summary results table"""
    table_data = self._prepare_table_data(test_sessions)
    table_style = self._build_table_style(test_sessions)
    
    table = Table(table_data, colWidths=[3.5*cm, 2.5*cm, 1.5*cm, 1.5*cm, 2*cm, 3*cm])
    table.setStyle(TableStyle(table_style))
    
    return [table]

def _prepare_table_data(self, test_sessions: List[Dict]) -> List[List[str]]:
    """Extract and format data for table"""
    headers = ['Test', 'Fecha', 'PB', 'PE', 'Percentil', 'Clasificación']
    rows = []
    
    for session in test_sessions:
        rows.append(self._format_session_row(session))
    
    return [headers] + rows

def _format_session_row(self, session: Dict) -> List[str]:
    """Format a single session for table display"""
    test_type = session.get('test_type', 'N/A')
    fecha = self._format_date(session.get('date'))
    scores = session.get('calculated_scores', {})
    
    return [
        test_type,
        fecha,
        str(self._extract_main_score(test_type, session.get('raw_data', {}))),
        str(scores.get('puntuacion_escalar', 'N/A')),
        str(scores.get('percentil', 'N/A')),
        scores.get('clasificacion', 'N/A')
    ]

def _build_results_detail_sections(self, test_sessions: List[Dict]) -> List:
    """Build individual detail sections for each test"""
    elements = []
    for session in test_sessions:
        elements.extend(self._build_test_detail(session))
        elements.append(Spacer(1, 0.3*cm))
    return elements
```

## Labels
`refactoring`, `clean-code`, `low-priority`

## Effort Estimate
1-2 hours
