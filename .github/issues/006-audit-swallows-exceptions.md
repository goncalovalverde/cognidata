# Audit Service Swallows Exceptions - Silent Failures

## Context
The audit service silently swallows exceptions without proper error handling:

```python
# services/audit.py lines 79-81
except Exception as e:
    db.rollback()
    print(f"Audit log error: {e}")  # Silent failure!
```

Additionally, the `get_logs` and `get_patient_history` methods have a bare `finally` block that only closes the session but doesn't handle errors:

```python
# services/audit.py lines 160-173
def get_logs(self, ...):
    db = SessionLocal()
    try:
        query = db.query(AuditLog)
        # ... filters ...
        return query.order_by(...).limit(limit).all()
    finally:
        db.close()  # What if db.query() raised an exception?
```

## Impact
- **Audit failures are invisible** to users and operators
- **For GDPR compliance**, audit logging should be considered critical
- **No alerting** when audit system fails
- **Potential data loss** - failed audits are not retried
- **Security risk** - attackers' actions may not be logged

## Why This Matters for Compliance
GDPR Article 32 requires:
> "...a process for regularly testing, assessing and evaluating the effectiveness of technical and organisational measures for ensuring the security of the processing."

If audit logging fails silently:
- Failed tests won't be caught
- Security incidents may not be recorded
- Compliance audits will fail

## Proposed Remediation

### 1. Better Error Handling
```python
# services/audit.py
import logging

logger = logging.getLogger(__name__)

def log(self, action, resource_type, resource_id=None, details=None, user_identifier=None):
    db = SessionLocal()
    try:
        log_entry = AuditLog(...)
        db.add(log_entry)
        db.commit()
    except Exception as e:
        logger.error(f"Audit log failure: {e}", exc_info=True)
        # Option A: Re-raise (fail closed - for critical operations)
        # raise AuditLogError(f"Failed to log {action}") from e
        
        # Option B: Fallback to file logging
        self._fallback_log(action, resource_type, resource_id, details)
        db.rollback()
    finally:
        db.close()
```

### 2. Fallback Mechanism
```python
def _fallback_log(self, action, resource_type, resource_id, details):
    """Write to fallback file if database fails"""
    import json
    fallback_path = "audit_fallback.jsonl"
    with open(fallback_path, "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.utcnow().isoformat(),
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details
        }) + "\n")
```

### 3. Add Metrics/Alerting
```python
# Track audit failures in Prometheus/Grafana
AUDIT_FAILURES.inc()
```

## Labels
`security`, `gdpr`, `error-handling`, `medium-priority`, `reliability`

## Effort Estimate
2-3 hours
