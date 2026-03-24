# Hardcoded Magic Values - Extract to Configuration

## Context
Classification thresholds are hardcoded directly in the normative calculator logic:

```python
# services/normatives.py lines 213-222
def _classify(self, percentil: float) -> str:
    if percentil >= 75:
        return "Superior"
    elif percentil >= 25:
        return "Normal"
    elif percentil >= 10:
        return "Limítrofe"
    else:
        return "Deficitario"
```

Additional magic values scattered throughout:
- Z-score boundaries for scalar conversion (lines 195-196)
- Education range lookups (lines 91-93)
- Age range lookups (lines 80-82)

## Impact
- **No external configuration** - must modify code to change thresholds
- **Different tests may need different norms** - currently one-size-fits-all
- **Spanish labels hardcoded** - difficult to internationalize
- **Clinical rules buried in code** - should be configurable by clinicians
- **Testing is harder** - must change code to test different scenarios

## Proposed Remediation

### Create Configuration File
```yaml
# config/normatives.yaml
classification:
  labels:
    es:
      superior: "Superior"
      normal: "Normal"
      limitrofe: "Limítrofe"
      deficitario: "Deficitario"
  thresholds:
    superior_min: 75
    normal_min: 25
    limitrofe_min: 10
    # Below limitrofe_min = Deficitario

# Test-specific configurations
tests:
  TMT-A:
    normative_source: "NEURONORMA"
    tables_path: "data/normative_tables/tmt_a.json"
    
  TMT-B:
    normative_source: "NEURONORMA"
    tables_path: "data/normative_tables/tmt_b.json"

  TAVEC:
    normative_source: "NEURONORMA"
    tables_path: "data/normative_tables/tavec.json"
```

### Update Calculator to Use Config
```python
# services/normatives.py
class NormativeCalculator:
    def __init__(self, config_path="config/normatives.yaml"):
        self.config = self._load_config(config_path)
    
    def _classify(self, percentil: float) -> str:
        thresholds = self.config['classification']['thresholds']
        labels = self.config['classification']['labels']['es']
        
        if percentil >= thresholds['superior_min']:
            return labels['superior']
        elif percentil >= thresholds['normal_min']:
            return labels['normal']
        elif percentil >= thresholds['limitrofe_min']:
            return labels['limitrofe']
        return labels['deficitario']
```

## Labels
`configuration`, `refactoring`, `medium-priority`, `i18n`

## Effort Estimate
3-4 hours
