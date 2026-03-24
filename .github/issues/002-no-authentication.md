# [Critical] No Authentication/Authorization - Security Risk

## Context
The application has **zero authentication or authorization** mechanisms. Any user who can access the URL can:
- View all patient records
- Create/modify/delete patient data
- Access neuropsychological test results
- Generate PDF reports with sensitive health data

The audit service has `user_identifier` as optional with comment "para futuro auth" (for future auth).

## Impact
### GDPR Compliance Violations:
- **Article 32**: Security of processing - inadequate access controls
- **Article 5**: Principles relating to processing - no access restrictions
- **Article 32**: Requires "appropriate technical and organisational measures"

### Risk Categories:
1. **Unauthorized data access** - Any user sees all patients
2. **Data manipulation** - Anyone can modify/delete records
3. **Audit trail is meaningless** - No way to tie actions to users
4. **PHI exposure** - Potential HIPAA violation if used in US healthcare

## Proposed Remediation

### Minimum Viable Auth (MVP):
```python
# utils/auth.py
import streamlit as st

def require_auth():
    if "user" not in st.session_state:
        st.warning("Por favor, inicia sesión para continuar.")
        st.stop()

def get_current_user():
    return st.session_state.get("user")
```

### Recommended: Full Auth Flow
1. **Streamlit-auth** or custom session management
2. **Role-based access control (RBAC)**:
   - `admin`: Full access, can delete patients
   - `clinician`: Can create tests, view reports
   - `viewer`: Read-only access
3. **Audit trail with real user IDs** (replace `user_identifier=None`)

### Future: Integration Options
- OAuth2/OIDC (Azure AD, Google, etc.)
- LDAP integration for clinical settings
- MFA for admin accounts

## Labels
`security`, `gdpr`, `high-priority`, `breaking-change`

## Effort Estimate
12-16 hours (MVP) / 20+ hours (production auth)
