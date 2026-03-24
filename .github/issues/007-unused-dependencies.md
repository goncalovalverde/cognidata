# Unused Dependencies in PDF Generator

## Context
The PDF generator imports dependencies that are never used:

```python
# services/pdf_generator.py lines 14-17
import plotly.graph_objects as go  # NEVER USED
import tempfile  # NEVER USED
from typing import Dict, List  # List imported but not used
```

Additionally, the class has dead code and unused helper methods.

## Impact
- **Confusion** - developers wonder if charts are planned
- **Slower imports** - unused modules loaded at startup
- **Larger bundle size** if packaging the app
- **Missed opportunities** - charts could enhance PDF reports

## Proposed Remediation

### 1. Clean Up Imports
```python
# Before (current)
import plotly.graph_objects as go
import tempfile
from typing import Dict, List

# After (cleaned)
from typing import Dict  # Only Dict is used (for type hints)
```

### 2. Consider Adding Charts to PDF
If charts are desired for the PDF report, implement them properly:

```python
def _generate_chart(self, test_names: List[str], pe_scores: List[int]) -> str:
    """Generate a radar chart and return the file path"""
    import plotly.graph_objects as go
    import io
    import base64
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=pe_scores,
        theta=test_names,
        fill='toself',
        name='Perfil del Paciente'
    ))
    
    # Convert to image
    img_buffer = io.BytesIO()
    fig.write_image(img_buffer, format='png')
    img_buffer.seek(0)
    
    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as f:
        f.write(img_buffer.read())
        return f.name
```

## Labels
`cleanup`, `refactoring`, `low-priority`, `enhancement`

## Effort Estimate
1 hour
