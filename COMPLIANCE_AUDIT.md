Agent completed. agent_id: compliance-audit, agent_type: ComplianceExpert, status: completed, description: Full security & GDPR audit, elapsed: 965s, total_turns: 0, duration: 962s

Perfect! Now I'll create the comprehensive audit report:

---

# **COMPREHENSIVE DEVSECOPS & GDPR COMPLIANCE AUDIT**
## CogniData Neuropsychological Testing Application

---

## **CRITICAL FINDINGS** ⚠️

### **1. CRITICAL: Weak JWT Secret Key - Insecure Default**
- **Issue**: JWT secret key uses hardcoded insecure default string instead of requiring strong environment variable
- **Risk Level**: **CRITICAL**
- **DevSecOps Principle**: Secret Management, Defense in Depth
- **File & Line**: `utils/jwt_manager.py:26`
- **Current Code**:
```python
SECRET_KEY = os.getenv("AUTH_SECRET_KEY", "cognidata-default-insecure-key-change-in-production-min-32-chars")
```
- **Impact**: Attackers who know the default key can forge valid JWT tokens and bypass authentication entirely
- **Compliant Fix**:
```python
import secrets
import sys

SECRET_KEY = os.getenv("AUTH_SECRET_KEY")
if not SECRET_KEY or len(SECRET_KEY) < 32:
    print("FATAL: AUTH_SECRET_KEY environment variable must be set to at least 32 random bytes", file=sys.stderr)
    print("Generate one with: python -c 'import secrets; print(secrets.token_urlsafe(32))'", file=sys.stderr)
    sys.exit(1)
```
- **Recommendation**: 
  1. Generate a secure key: `python -c 'import secrets; print(secrets.token_urlsafe(32))'`
  2. Set `AUTH_SECRET_KEY` environment variable to this value
  3. Never commit the key to source control
  4. Fail loudly on startup if key is missing
  5. Rotate keys periodically

---

### **2. CRITICAL: Hardcoded Default Admin Password**
- **Issue**: Default admin password "admin123" is hardcoded and will be created if no users exist
- **Risk Level**: **CRITICAL**
- **DevSecOps Principle**: Credential Management, Least Privilege
- **File & Line**: `utils/auth.py:58, 86` and `tests/test_auth.py:25`
- **Current Code**:
```python
admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
# Creates admin with hardcoded default password
```
- **Impact**: Anyone with knowledge of the codebase can log in as admin with "admin123"
- **Compliant Fix**:
```python
admin_password = os.getenv("ADMIN_PASSWORD")
if not admin_password:
    print("FATAL: ADMIN_PASSWORD environment variable must be set for first-time admin user creation", file=sys.stderr)
    print("Set a strong password: export ADMIN_PASSWORD='your_secure_password'", file=sys.stderr)
    sys.exit(1)
```
- **Recommendation**:
  1. Remove all "admin123" references from code
  2. Require `ADMIN_PASSWORD` environment variable on first startup
  3. Implement a secure admin setup wizard for fresh installations
  4. Document secure password requirements (minimum 12 characters, mixed case, special chars)
  5. Audit all existing deployments and force password changes

---

### **3. CRITICAL: JWT Token Exposed in URL Query Parameters**
- **Issue**: JWT authentication token is stored and transmitted in URL query parameters (`st.query_params["auth_token"]`), making it visible in:
  - Browser history
  - Server logs (referer headers)
  - Proxy logs
  - Browser autocomplete
- **Risk Level**: **CRITICAL**
- **GDPR Article**: Article 32 (Security of Processing)
- **File & Line**: `utils/auth.py:309, 246, 257`
- **Current Code**:
```python
st.query_params["auth_token"] = token  # Token in URL - INSECURE
token = st.query_params.get("auth_token")  # Read from URL
```
- **Impact**: Token interception via logs, browser history, or man-in-the-middle attacks; one of the most severe security flaws
- **Compliant Fix**:
```python
# Use secure HTTP-only session cookies instead of URL parameters
# For Streamlit, implement secure storage via encrypted cookies or server-side sessions only

# Option 1: Use streamlit-cookies-manager for secure cookies (already installed)
from streamlit_cookies_manager import CookieManager

cookies = CookieManager()
cookies["auth_token"] = token
cookies.save()

# Never include in URL - only session ID in URL if needed
# Option 2: Server-side sessions only - no client token exposure
st.session_state.session_id = session_id  # Only ID, token stays server-side
```
- **Recommendation**:
  1. **URGENT**: Migrate from URL-based token storage to secure cookies or server-side sessions
  2. Use `streamlit-cookies-manager` with `HttpOnly` flag (if available)
  3. For maximum security, store only a session ID client-side, keep tokens server-side only
  4. Implement token rotation on each request
  5. Add CSRF protection tokens
  6. Audit all token exposure in logs via grep for "auth_token"

---

### **4. HIGH: Weak Password Hashing Library - Passlib 1.7.4 (Deprecated)**
- **Issue**: `passlib==1.7.4` is outdated (released 2013) and no longer maintained. Code uses bcrypt directly anyway, making passlib unnecessary
- **Risk Level**: **HIGH**
- **DevSecOps Principle**: Dependency Management, Secure Defaults
- **File & Line**: `requirements.txt:25`
- **Current Code**:
```
passlib==1.7.4  # Last release 2013 - DEPRECATED
```
- **Why It's Problem**: 
  - Unmaintained library won't receive security patches
  - May have unknown vulnerabilities from 2013
  - Imports cryptographic code that may be insecure
- **Compliant Fix**:
```
# Remove passlib - use bcrypt directly (already done in code):
# DELETE: passlib==1.7.4
# Keep: bcrypt==4.1.2 (modern, actively maintained)
```
- **Recommendation**:
  1. Remove `passlib` from requirements.txt
  2. Verify bcrypt is used everywhere for password hashing (it is ✓)
  3. Update bcrypt to latest version
  4. Implement quarterly dependency audits using `pip-audit`
  5. Add security scanning to CI/CD pipeline

---

### **5. HIGH: Unencrypted Sensitive Data at Rest**
- **Issue**: Database stores patient neuropsychological test data (raw_data, calculated_scores, qualitative_data) in plaintext SQLite without encryption
- **Risk Level**: **HIGH**
- **GDPR Article**: Article 32 (Security of Processing) - "Appropriate measures to ensure a level of security appropriate to the risk"
- **File & Line**: `models/test_session.py:20-22` and `database/connection.py` (SQLite unencrypted)
- **Current Code**:
```python
raw_data = Column(Text)  # Stores raw test data as plaintext
calculated_scores = Column(Text, nullable=True)
qualitative_data = Column(Text, nullable=True)  # Qualitative observations
```
- **Impact**: If database is stolen/exposed, all sensitive patient neuropsychological data is readable; violates healthcare data protection requirements
- **Compliant Fix**:
```python
from cryptography.fernet import Fernet
import os

# Generate and load encryption key (store securely in env)
ENCRYPTION_KEY = os.getenv("DATA_ENCRYPTION_KEY")
if not ENCRYPTION_KEY:
    ENCRYPTION_KEY = Fernet.generate_key().decode()
    print("WARNING: Generated new encryption key, store this:", ENCRYPTION_KEY)

cipher = Fernet(ENCRYPTION_KEY)

class TestSession(Base):
    __tablename__ = "test_sessions"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    patient_id = Column(String, ForeignKey("patients.id"), nullable=False)
    _raw_data = Column("raw_data", Text)  # Encrypted storage
    
    @property
    def raw_data(self) -> str:
        """Decrypt raw data on read"""
        if self._raw_data:
            return cipher.decrypt(self._raw_data.encode()).decode()
        return None
    
    @raw_data.setter
    def raw_data(self, value: str):
        """Encrypt raw data on write"""
        if value:
            self._raw_data = cipher.encrypt(value.encode()).decode()
```
- **Recommendation**:
  1. Implement field-level encryption for all PII and sensitive data
  2. Use `cryptography` library (battle-tested, NIST-approved)
  3. Rotate encryption keys annually
  4. Consider full-disk encryption for database files
  5. Implement at-rest encryption for backups
  6. Add encryption status monitoring to audit logs

---

### **6. HIGH: No Data Retention/TTL Policy for Personal Data**
- **Issue**: No automatic deletion, anonymization, or retention limit for patient data; violates GDPR right to erasure and data minimization
- **Risk Level**: **HIGH**
- **GDPR Article**: Article 5 (Data Minimization & Storage Limitation), Article 17 (Right to Erasure)
- **File & Line**: All models lack `deleted_at`, `retention_days`, or cleanup logic
- **Current Code**: No TTL/retention logic anywhere
```python
# Patient data has created_at but no deletion/retention mechanism
created_at = Column(DateTime, default=datetime.utcnow)
# Missing: deleted_at, retention_until, is_deleted fields
```
- **Impact**: Data is stored indefinitely, violating GDPR Article 5 (storage limitation); users cannot exercise right to erasure with data still in active use
- **Compliant Fix**:
```python
from sqlalchemy import Boolean
from datetime import datetime, timedelta

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    age = Column(Integer, nullable=False)
    education_years = Column(Integer, nullable=False)
    laterality = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # GDPR compliance: Track deletion and retention
    deleted_at = Column(DateTime, nullable=True)  # When marked for deletion
    is_deleted = Column(Boolean, default=False, index=True)  # Soft delete flag
    retention_until = Column(DateTime, nullable=True)  # When to hard delete
    
    @property
    def is_active(self) -> bool:
        """Check if patient data should be used"""
        return not self.is_deleted
    
    def mark_for_deletion(self):
        """Mark patient for deletion (GDPR right to erasure)"""
        self.deleted_at = datetime.utcnow()
        self.is_deleted = True
        # Hard delete after 30 days (configurable retention)
        self.retention_until = datetime.utcnow() + timedelta(days=30)

# In database/connection.py:
def cleanup_deleted_data():
    """Hard delete data after retention period (call daily)"""
    db = SessionLocal()
    try:
        # Delete patients and related data past retention date
        expired = db.query(Patient).filter(
            Patient.retention_until <= datetime.utcnow(),
            Patient.is_deleted == True
        ).all()
        
        for patient in expired:
            db.delete(patient)  # Cascades to test sessions
        
        db.commit()
    finally:
        db.close()
```
- **Recommendation**:
  1. Add soft-delete fields to all models (deleted_at, is_deleted, retention_until)
  2. Implement 30-day retention period before hard delete (configurable)
  3. Add scheduled cleanup task (run daily via cron or APScheduler)
  4. Document retention policy in terms & conditions
  5. Notify users before deletion (e.g., 7-day warning)
  6. Log all deletions to audit trail with reason
  7. Allow users to request immediate deletion (zero retention)

---

## **HIGH SEVERITY FINDINGS**

### **7. HIGH: SQL Injection Risk via Audit Log String Filtering**
- **Issue**: `AuditLog.details` column uses `.contains()` filter on JSON string without validation, could be vulnerable to SQL injection
- **Risk Level**: **HIGH**
- **DevSecOps Principle**: Input Validation, Parameterized Queries
- **File & Line**: `services/audit.py:183`
- **Current Code**:
```python
return (
    db.query(AuditLog)
    .filter(
        (AuditLog.resource_id.startswith(patient_id[:12]))
        | (AuditLog.details.contains(patient_id[:8]))  # ⚠️ Potential SQLi
    )
    .order_by(AuditLog.timestamp.desc())
    .limit(limit)
    .all()
)
```
- **Impact**: Although SQLAlchemy uses parameterized queries, the `.contains()` on JSON strings could allow pattern-based attacks
- **Compliant Fix**:
```python
import json

def get_patient_history(self, patient_id: str, limit: int = 50):
    """Obtener historial completo de auditoria de un paciente - SAFE"""
    db = SessionLocal()
    try:
        # Only filter by indexed columns (resource_id)
        # Don't search inside JSON details field
        return (
            db.query(AuditLog)
            .filter(AuditLog.resource_id == patient_id[:12])
            .order_by(AuditLog.timestamp.desc())
            .limit(limit)
            .all()
        )
    finally:
        db.close()
```
- **Recommendation**:
  1. Remove `.contains()` filters on text/JSON columns
  2. Use indexed columns only for filtering (resource_id, resource_type, action)
  3. Parse JSON separately in Python if detailed search is needed
  4. Validate patient_id format (UUID) before using in queries
  5. Add input validation layer for all query parameters

---

### **8. HIGH: Audit Log Doesn't Capture Failed Authentication Attempts**
- **Issue**: Audit logging is incomplete - failed login attempts are not logged, making it impossible to detect brute force attacks
- **Risk Level**: **HIGH**
- **DevSecOps Principle**: Logging & Monitoring, Attack Detection
- **File & Line**: `utils/auth.py:288-319` (login function has no audit log for failures)
- **Current Code**:
```python
def login(username: str, password: str) -> bool:
    user = auth_service.authenticate(username, password)
    if user:
        # SUCCESS: logged ✓
        audit_service.log(action="auth.login", ...)
        return True
    
    # FAILURE: NOT logged ✗ - no audit trail
    st.session_state.login_attempts += 1
    return False
```
- **Impact**: Cannot detect credential stuffing/brute force attacks; failed logins disappear from logs
- **Compliant Fix**:
```python
def login(username: str, password: str) -> bool:
    from services.audit import audit_service
    
    user = auth_service.authenticate(username, password)
    
    if user:
        st.session_state.user = user
        st.session_state.authenticated = True
        st.session_state.login_attempts = 0
        
        token = JWTManager.generate_token(user)
        st.session_state.auth_token = token
        
        # Log successful login
        audit_service.log(
            action="auth.login_success",
            resource_type="system",
            details={"username": username, "role": user.role},
        )
        return True
    
    # LOG FAILED ATTEMPT - NEW
    st.session_state.login_attempts += 1
    audit_service.log(
        action="auth.login_failed",
        resource_type="system",
        details={
            "username": username,
            "attempt_number": st.session_state.login_attempts,
            "reason": "invalid_credentials"
        },
    )
    
    return False
```
- **Recommendation**:
  1. Log all authentication attempts (success and failure)
  2. Include attempt count and source IP
  3. Alert on threshold: >5 failed attempts in 15 minutes = account lockout
  4. Implement rate limiting on login endpoint
  5. Send email alert to user on suspicious login activity
  6. Review failed login logs weekly

---

### **9. HIGH: Hospital/Clinic Data Not Anonymized in Audit Logs**
- **Issue**: Audit logs may contain patient IDs in details field, creating PII exposure if logs are shared or exposed
- **Risk Level**: **HIGH**
- **GDPR Article**: Article 32 (Security), Article 5 (Data Minimization)
- **File & Line**: `services/audit.py:89-94, 119, 133`
- **Current Code**:
```python
def log_test_create(self, session_id: str, patient_id: str, test_type: str, scores: dict):
    self.log(
        action=self.ACTIONS["TEST_CREATE"],
        resource_type=self.RESOURCE_TEST_SESSION,
        resource_id=session_id,
        details={
            "patient_id": patient_id[:12] if patient_id else None,  # Partial UUID - still identifies patient
            ...
        },
    )
```
- **Impact**: Even truncated patient IDs can be linked back to patients if audit logs are exposed; violates data minimization principle
- **Compliant Fix**:
```python
def log_test_create(self, session_id: str, patient_id: str, test_type: str, scores: dict):
    """Log test creation WITHOUT patient ID (data minimization)"""
    self.log(
        action=self.ACTIONS["TEST_CREATE"],
        resource_type=self.RESOURCE_TEST_SESSION,
        resource_id=session_id,
        details={
            # Don't include patient_id - log only action performed
            "test_type": test_type,
            "score_count": len(scores) if scores else 0,
            "has_percentile": "percentil" in (scores or {}),
        },
    )
    
    # If you MUST log patient association for compliance audits:
    # Store in separate encrypted audit table with access controls
    # Only accessible by compliance officers via separate secure interface
```
- **Recommendation**:
  1. Remove patient_id from audit log details
  2. Store only session_id and test_id (which are linked to patient in database if needed)
  3. Create separate "compliance audit trail" for sensitive associations
  4. Encrypt compliance audit data separately
  5. Restrict access to compliance data to authorized auditors only
  6. Log access to compliance audit trails themselves

---

### **10. HIGH: Backup Files Not Encrypted**
- **Issue**: Database backups are copied unencrypted to local backup directory; anyone with file access can read all patient data
- **Risk Level**: **HIGH**
- **GDPR Article**: Article 32 (Security of Processing)
- **File & Line**: `app_pages/config.py:44`
- **Current Code**:
```python
def _render_backup_section():
    if st.button("Crear Backup Ahora"):
        backup_filename = f"cognidata_{timestamp}.db"
        shutil.copy2("cognidata.db", f"backups/{backup_filename}")  # Unencrypted copy
        audit_service.log_backup_create(backup_filename)
```
- **Impact**: Backups contain unencrypted sensitive data; theft/exposure of backups = complete data breach
- **Compliant Fix**:
```python
import zipfile
import os
from cryptography.fernet import Fernet
from io import BytesIO

def _render_backup_section():
    if st.button("Crear Backup Ahora"):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"cognidata_{timestamp}.db.zip.enc"
        
        try:
            # Read database file
            with open("cognidata.db", "rb") as f:
                db_content = f.read()
            
            # Encrypt using DATA_ENCRYPTION_KEY
            encryption_key = os.getenv("DATA_ENCRYPTION_KEY")
            if not encryption_key:
                raise ValueError("DATA_ENCRYPTION_KEY not set - cannot create encrypted backups")
            
            cipher = Fernet(encryption_key)
            encrypted_content = cipher.encrypt(db_content)
            
            # Save encrypted backup
            backup_path = f"backups/{backup_filename}"
            with open(backup_path, "wb") as f:
                f.write(encrypted_content)
            
            # Restrict file permissions (read-only for owner)
            os.chmod(backup_path, 0o400)
            
            audit_service.log_backup_create(backup_filename)
            alert(f"Encrypted backup created: {backup_filename}", alert_type="success")
            
        except Exception as e:
            alert(f"Backup error: {str(e)}", alert_type="error")
```
- **Recommendation**:
  1. Encrypt all backups with `DATA_ENCRYPTION_KEY`
  2. Use ZIP + encryption or use `pgcrypto` equivalent for SQLite
  3. Restrict file permissions to 0o400 (read-only owner)
  4. Test backup restoration process monthly
  5. Store backups in a separate secure location
  6. Implement automatic backups with encryption
  7. Require password to restore backups

---

### **11. HIGH: No HTTPS/TLS Configuration Documented**
- **Issue**: Streamlit app doesn't enforce HTTPS; JWT tokens and all data transmitted in plaintext if not behind HTTPS proxy
- **Risk Level**: **HIGH**
- **DevSecOps Principle**: Transport Security, Man-in-the-Middle Prevention
- **File & Line**: `app.py` and Streamlit config (no HTTPS configuration)
- **Impact**: All traffic (including tokens, passwords, patient data) can be intercepted in plaintext
- **Compliant Fix**:
```yaml
# .streamlit/config.toml
[server]
# Force HTTPS only (when behind proxy)
enableXsrfProtection = true
enableCORS = false
headless = true

# Set secure headers
[client]
showErrorDetails = false

# Session configuration
[logger]
level = "info"
```
```python
# app.py - Add security headers via Streamlit server config
import streamlit as st

# Add security headers (Streamlit 1.x doesn't support directly, use proxy)
st.set_page_config(
    page_title="CogniData",
    initial_sidebar_state="expanded",
)
```
- **Recommendation**:
  1. Deploy Streamlit behind HTTPS proxy (nginx, Apache, cloud load balancer)
  2. Enforce HSTS (HTTP Strict-Transport-Security) header
  3. Use TLS 1.2+ with strong ciphers
  4. Deploy to cloud platform (AWS, Azure, GCP) with managed HTTPS
  5. Configure CSP (Content-Security-Policy) headers
  6. Use OCSP stapling for certificate validation
  7. Document HTTPS requirement in deployment guide

---

## **MEDIUM SEVERITY FINDINGS**

### **12. MEDIUM: Plaintext IP Address Stored in Audit Logs**
- **Issue**: Client IP addresses stored in plaintext in audit logs; could be used to track user location
- **Risk Level**: **MEDIUM**
- **GDPR Article**: Article 6 (Lawfulness of Processing)
- **File & Line**: `services/audit.py:38-46, 75`
- **Current Code**:
```python
def _get_client_ip(self) -> str:
    try:
        hostname = socket.gethostname()
        self._ip_cache = socket.gethostbyname(hostname)  # Gets server IP, not client IP
    except Exception:
        self._ip_cache = "unknown"
    return self._ip_cache
```
- **Issue**: Code actually gets SERVER IP (not client), but still stores it; also no consent for IP logging
- **Compliant Fix**:
```python
def _get_client_ip(self, request=None) -> Optional[str]:
    """
    Get client IP only if logging is explicitly consented.
    Returns None if IP logging not consented or not needed for security.
    """
    # Only log IP for security-critical events (failed logins, deletions)
    # Not for routine operations
    return None  # By default, don't log IP (GDPR minimization)

def log(
    self,
    action: str,
    resource_type: str,
    resource_id: str = None,
    details: dict = None,
    user_identifier: str = None,
    include_ip: bool = False,  # Explicit opt-in
):
    """Log with optional IP address"""
    db = SessionLocal()
    try:
        ip_address = self._get_client_ip() if include_ip else None
        
        log_entry = AuditLog(
            timestamp=datetime.utcnow(),
            user_identifier=user_identifier or st.session_state.get("user", {}).username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id[:12] if resource_id else None,
            details=json.dumps(details, ensure_ascii=False) if details else None,
            ip_address=ip_address,
        )
        db.add(log_entry)
        db.commit()
```
- **Recommendation**:
  1. Don't log IP addresses by default (data minimization)
  2. Only log IP for security events: failed login attempts, admin changes, deletions
  3. Hash IPs with salt if logging needed (not reversible)
  4. Obtain explicit user consent for IP logging
  5. Implement IP logging only in separate security audit table
  6. Delete IP logs after 90 days (retention policy)

---

### **13. MEDIUM: User Creation/Deletion Not Protected by Role Check in UI**
- **Issue**: User deletion directly calls `delete_user()` without checking if current user has admin role first
- **Risk Level**: **MEDIUM**
- **DevSecOps Principle**: Authorization, Principle of Least Privilege
- **File & Line**: `app_pages/config.py:220, 298`
- **Current Code**:
```python
if st.button(f"❌ Eliminar usuario '{selected_username}'"):
    # No role check - relies only on page-level guard
    delete_user(selected_username)  # Could be called by non-admin
```
- **Impact**: If page-level auth check is bypassed, users could delete other users
- **Compliant Fix**:
```python
def _render_edit_delete_user():
    """Render edit and delete user functionality"""
    from utils.auth import require_role
    
    # Page-level guard - must be admin
    require_role(Role.ADMIN)
    
    # Additional check before delete operation
    if st.button(f"❌ Eliminar usuario '{selected_username}'"):
        user = get_current_user()
        if not auth_service.can_delete(user):  # Service-level check
            st.error("No tienes permiso para eliminar usuarios")
            return
        
        try:
            delete_user(selected_username)
            audit_service.log(
                action="user.delete",
                resource_type="user",
                resource_id=selected_username,
                details={"deleted_by": user.username},
            )
        except Exception as e:
            st.error(f"Error: {str(e)}")
```
- **Recommendation**:
  1. Add `@require_role(Role.ADMIN)` decorator to sensitive pages
  2. Add service-level authorization checks (not just UI)
  3. Log all user management operations with acting user
  4. Require confirmation dialog + OTP for critical operations
  5. Implement 24-hour window for user deletion (not instant)

---

### **14. MEDIUM: Plaintext Password Input Not Hidden During Reset**
- **Issue**: Password reset form displays password confirmation in plaintext; no password strength validation
- **Risk Level**: **MEDIUM**
- **DevSecOps Principle**: Secure Input Handling, Password Policy
- **File & Line**: `app_pages/config.py:200-201`
- **Current Code**:
```python
new_password = st.text_input("Nueva Contraseña", type="password")
new_password_confirm = st.text_input("Confirmar Contraseña", type="password")
# No validation of password strength
```
- **Compliant Fix**:
```python
import re

def _validate_password_strength(password: str) -> tuple[bool, str]:
    """
    Validate password meets minimum requirements.
    Returns (is_valid, error_message)
    """
    if len(password) < 12:
        return False, "Contraseña debe tener al menos 12 caracteres"
    if not re.search(r'[A-Z]', password):
        return False, "Debe contener al menos una mayúscula"
    if not re.search(r'[a-z]', password):
        return False, "Debe contener al menos una minúscula"
    if not re.search(r'[0-9]', password):
        return False, "Debe contener al menos un número"
    if not re.search(r'[!@#$%^&*()_+\-=\[\]{};:\'",.<>?/\\|`~]', password):
        return False, "Debe contener al menos un carácter especial"
    return True, ""

def _render_edit_delete_user():
    with st.form("edit_user_form"):
        new_password = st.text_input("Nueva Contraseña", type="password")
        new_password_confirm = st.text_input("Confirmar Contraseña", type="password")
        
        if new_password:
            is_valid, error_msg = _validate_password_strength(new_password)
            if not is_valid:
                st.error(f"❌ {error_msg}")
            else:
                st.success("✅ Contraseña cumple requisitos")
        
        if new_password != new_password_confirm:
            st.error("Las contraseñas no coinciden")
        
        submitted = st.form_submit_button("Cambiar Contraseña")
        
        if submitted:
            is_valid, error_msg = _validate_password_strength(new_password)
            if not is_valid:
                st.error(f"Error de validación: {error_msg}")
            elif new_password != new_password_confirm:
                st.error("Las contraseñas no coinciden")
            else:
                change_password(selected_username, new_password)
                st.success("✅ Contraseña cambiada exitosamente")
```
- **Recommendation**:
  1. Enforce minimum 12 characters (NIST guidance)
  2. Require mixed case + numbers + special characters
  3. Check against common password lists
  4. Implement rate limiting on password changes
  5. Force password reset on first login
  6. Implement password expiration (90 days)
  7. Maintain password history (prevent reuse)

---

### **15. MEDIUM: No CSRF Protection on Forms**
- **Issue**: Streamlit forms lack CSRF tokens; attackers can submit forms on behalf of authenticated users via cross-site requests
- **Risk Level**: **MEDIUM**
- **DevSecOps Principle**: CSRF Protection
- **File & Line**: All `st.form()` calls in app_pages/
- **Current Code**:
```python
with st.form("new_patient_form"):  # No CSRF token
    age = st.number_input("Edad", min_value=18, max_value=100)
    # ... form without CSRF protection
```
- **Compliant Fix**:
```python
import secrets

def _generate_csrf_token():
    """Generate CSRF token for form protection"""
    if "csrf_token" not in st.session_state:
        st.session_state.csrf_token = secrets.token_urlsafe(32)
    return st.session_state.csrf_token

def _verify_csrf_token(submitted_token):
    """Verify CSRF token matches session"""
    return submitted_token == st.session_state.get("csrf_token")

# In form:
csrf_token = _generate_csrf_token()

with st.form("new_patient_form"):
    st.hidden_button("csrf_token", value=csrf_token, key="csrf_input")  # Streamlit limitation
    
    age = st.number_input("Edad", min_value=18, max_value=100)
    education_years = st.number_input("Años de Escolaridad", min_value=0, max_value=25)
    
    submitted = st.form_submit_button("Guardar Paciente")
    
    if submitted:
        # For Streamlit, CSRF is partially mitigated by session-based auth
        # But recommend deploying behind CSRF middleware
        pass
```
- **Recommendation**:
  1. Deploy Streamlit behind CSRF middleware (nginx, Apache, cloud WAF)
  2. Use SameSite=Strict cookie attribute
  3. Implement token-per-request CSRF tokens if possible
  4. Validate Origin and Referer headers
  5. Use AWS WAF, Cloudflare WAF, or similar for additional protection
  6. Test CSRF vulnerability with OWASP ZAP

---

### **16. MEDIUM: No Rate Limiting on Authentication**
- **Issue**: No rate limiting on login attempts; brute force attacks possible
- **Risk Level**: **MEDIUM**
- **DevSecOps Principle**: Attack Prevention, Account Lockout
- **File & Line**: `utils/auth.py:278-319` and Streamlit page
- **Current Code**:
```python
st.session_state.login_attempts += 1
if attempts >= 5:
    st.warning("⏱️ Demasiados intentos. Por favor, espera un momento.")
    # Warning only - no actual lockout
```
- **Compliant Fix**:
```python
from datetime import datetime, timedelta

def _is_account_locked(username: str) -> bool:
    """Check if account is locked due to failed attempts"""
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.username == username).first()
        if not user:
            return False
        
        # Check if locked and lock is still active
        if hasattr(user, 'locked_until') and user.locked_until:
            if datetime.utcnow() < user.locked_until:
                return True  # Still locked
            else:
                # Unlock expired
                user.locked_until = None
                user.failed_login_attempts = 0
                db.commit()
        
        return False
    finally:
        db.close()

def login(username: str, password: str) -> bool:
    # Check if account is locked
    if _is_account_locked(username):
        audit_service.log(
            action="auth.login_blocked_locked",
            resource_type="system",
            details={"username": username, "reason": "account_locked"},
        )
        st.error("Cuenta bloqueada por demasiados intentos fallidos. Intenta más tarde.")
        return False
    
    user = auth_service.authenticate(username, password)
    
    if user:
        # Success - reset attempts
        st.session_state.user = user
        st.session_state.authenticated = True
        st.session_state.login_attempts = 0
        # ... rest of login
    else:
        # Failure - increment and lock if needed
        st.session_state.login_attempts += 1
        
        # Lock after 5 failed attempts for 30 minutes
        if st.session_state.login_attempts >= 5:
            _lock_account(username, lockout_minutes=30)
            st.error("Cuenta bloqueada por 30 minutos. Contacta a administrador.")
        else:
            st.error(f"Intento {st.session_state.login_attempts}/5")
```
- **Recommendation**:
  1. Implement account lockout after 5 failed attempts
  2. Lock for 30 minutes (exponential backoff: 30 min → 60 min → 24 hr)
  3. Log all lockouts and send alert email
  4. Allow admin to unlock accounts
  5. Implement CAPTCHA after 3 failed attempts
  6. Monitor for brute force patterns (multiple accounts, IPs)
  7. Use fail2ban or cloud WAF rate limiting

---

### **17. MEDIUM: Default Database Path Not Secured**
- **Issue**: Database file is created in application directory with default permissions; readable by any user on the system
- **Risk Level**: **MEDIUM**
- **DevSecOps Principle**: File Permissions, Least Privilege
- **File & Line**: `database/connection.py:12`
- **Current Code**:
```python
DATABASE_PATH = os.getenv("DATABASE_PATH", "cognidata.db")
# Created with default umask (usually 0o644) - world-readable
```
- **Compliant Fix**:
```python
import os
import stat
from pathlib import Path

DATABASE_PATH = os.getenv("DATABASE_PATH", "cognidata.db")

# After database creation, restrict permissions
def _secure_database_file(db_path: str):
    """Ensure database file is only readable/writable by owner"""
    try:
        Path(db_path).chmod(0o600)  # rwx------
        st.write(f"✓ Database permissions secured: 0o600")
    except Exception as e:
        print(f"Warning: Could not secure database permissions: {e}")

# In init_db():
init_db()
_secure_database_file(DATABASE_PATH)
```
- **Recommendation**:
  1. Set database file permissions to 0o600 (owner read/write only)
  2. Store database in /var/lib/cognidata/ (non-user-writable directory)
  3. Use separate user account to run application (not root, not www-data)
  4. Enable SQLite journaling with WAL mode for integrity
  5. Regular file permission audits

---

## **MEDIUM-LOW FINDINGS**

### **18. MEDIUM: Expired Tokens Not Cleaned Up**
- **Issue**: `AuthSession` records are never deleted; database accumulates expired session records indefinitely
- **Risk Level**: **MEDIUM**
- **DevSecOps Principle**: Data Minimization, System Hygiene
- **File & Line**: `services/session_manager.py` (no cleanup logic)
- **Compliant Fix**:
```python
@staticmethod
def cleanup_expired_sessions(older_than_hours: int = 72):
    """
    Delete expired session records older than specified hours.
    Call daily via scheduled task.
    """
    db = SessionLocal()
    try:
        cutoff_time = datetime.utcnow() - timedelta(hours=older_than_hours)
        
        deleted = db.query(AuthSession).filter(
            AuthSession.token_expires_at < cutoff_time
        ).delete()
        
        db.commit()
        
        print(f"Cleaned up {deleted} expired sessions")
        
        audit_service.log(
            action="system.cleanup_sessions",
            resource_type="system",
            details={"expired_sessions_deleted": deleted},
        )
        
        return deleted
    finally:
        db.close()
```
- **Recommendation**:
  1. Schedule daily cleanup of sessions expired >72 hours
  2. Monitor session table growth
  3. Set audit log retention (e.g., 1 year) with cleanup
  4. Implement database maintenance (VACUUM, ANALYZE) monthly

---

### **19. MEDIUM: Qualitative Observations May Contain PII**
- **Issue**: `qualitative_data` field stores observation notes which may contain patient names, personal details, or sensitive health information not anonymized
- **Risk Level**: **MEDIUM**
- **GDPR Article**: Article 9 (Special Category Data - Health)
- **File & Line**: `models/test_session.py:22`
- **Compliant Fix**:
```python
# Add field-level encryption for sensitive text data
class TestSession(Base):
    qualitative_data_encrypted = Column(Text, nullable=True)
    
    def set_qualitative_data(self, data: dict):
        """Store qualitative data encrypted"""
        json_str = json.dumps(data, ensure_ascii=False)
        encrypted = cipher.encrypt(json_str.encode()).decode()
        self.qualitative_data_encrypted = encrypted
    
    def get_qualitative_data(self) -> dict:
        """Retrieve and decrypt qualitative data"""
        if self.qualitative_data_encrypted:
            decrypted = cipher.decrypt(self.qualitative_data_encrypted.encode()).decode()
            return json.loads(decrypted)
        return {}

# Add validation in form:
def _render_tmt_a_form(patient_id: str):
    # ...form inputs...
    observaciones = st.text_area(
        "Observaciones Clínicas",
        placeholder="Evita nombres, familias, o información personal identificable"
    )
    
    # Validation
    if observaciones:
        # Check for obvious PII patterns
        if re.search(r'\b[A-Z][a-z]+\s+[A-Z][a-z]+\b', observaciones):
            st.warning("⚠️ Nota: Parece contener nombres. Por favor, anonimiza.")
```
- **Recommendation**:
  1. Encrypt qualitative_data field
  2. Train clinicians on anonymization
  3. Implement regex pattern detection for names, addresses, phone numbers
  4. Mask detected PII in qualitative text before storage
  5. Show warning when potential PII detected in notes

---

### **20. MEDIUM: Exported PDF Reports Not Password Protected**
- **Issue**: Generated PDF reports contain patient data but are not password protected; anyone with file access can read
- **Risk Level**: **MEDIUM**
- **GDPR Article**: Article 32 (Security of Processing)
- **File & Line**: `services/pdf_generator.py:127` and `app_pages/dashboard.py:448-452`
- **Compliant Fix**:
```python
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
import PyPDF2

class NeuroPsychReport:
    def generate_report(
        self,
        patient_data: Dict,
        test_sessions: List[Dict],
        output_filename: str = None,
        password: str = None
    ) -> str:
        """
        Generate PDF with optional password protection.
        """
        
        filepath = os.path.join(self.output_dir, output_filename)
        
        # ... existing PDF generation code ...
        doc.build(story)
        
        # Add password protection if provided
        if password:
            self._encrypt_pdf(filepath, password)
        
        return filepath
    
    def _encrypt_pdf(self, pdf_path: str, password: str):
        """Encrypt PDF with user password"""
        try:
            # Read the unencrypted PDF
            with open(pdf_path, 'rb') as input_file:
                reader = PyPDF2.PdfReader(input_file)
                writer = PyPDF2.PdfWriter()
                
                # Copy all pages
                for page in reader.pages:
                    writer.add_page(page)
                
                # Encrypt with password (user password prevents viewing)
                writer.encrypt(password)
                
                # Write encrypted PDF
                with open(pdf_path, 'wb') as output_file:
                    writer.write(output_file)
        
        except Exception as e:
            print(f"Warning: Could not encrypt PDF: {e}")

# In dashboard.py:
if st.button("Generar Informe"):
    # ...generate report...
    
    # Require password for PDF
    pdf_password = st.text_input("Contraseña para PDF (dejaenvacío para sin protección):")
    
    st.download_button(
        label="⬇️ Descargar PDF",
        data=pdf_bytes,
        file_name=os.path.basename(pdf_path),
        mime="application/pdf",
    )
    
    st.info("💡 Tip: Protege el PDF con una contraseña fuerte")
```
- **Recommendation**:
  1. Add optional password protection to all PDF reports
  2. Default to encrypted PDFs with auto-generated password
  3. Send password separately to user via email
  4. Implement watermarks with "CONFIDENTIAL" and patient ID
  5. Set PDF permissions: disable printing, copying (if possible)
  6. Delete generated PDFs after 30 days (store download count instead)

---

### **21. MEDIUM: Patient Model Has Unused Encrypted Metadata Field**
- **Issue**: `encrypted_metadata` column exists but is never used, creating confusion about whether data is encrypted
- **Risk Level**: **MEDIUM**
- **DevSecOps Principle**: Clear Intent, Maintainability
- **File & Line**: `models/patient.py:19`
- **Current Code**:
```python
encrypted_metadata = Column(String, nullable=True)  # Unused field
```
- **Compliant Fix**:
```python
# Option A: Remove if not needed
# DELETE the unused column with migration

# Option B: Use it properly for storing encrypted sensitive data
from cryptography.fernet import Fernet
import json

class Patient(Base):
    # ... other fields ...
    
    _encrypted_metadata = Column("encrypted_metadata", String, nullable=True)
    
    def set_metadata(self, metadata_dict: dict):
        """Store encrypted metadata"""
        cipher = Fernet(os.getenv("DATA_ENCRYPTION_KEY"))
        json_str = json.dumps(metadata_dict)
        encrypted = cipher.encrypt(json_str.encode()).decode()
        self._encrypted_metadata = encrypted
    
    def get_metadata(self) -> dict:
        """Retrieve and decrypt metadata"""
        if self._encrypted_metadata:
            cipher = Fernet(os.getenv("DATA_ENCRYPTION_KEY"))
            decrypted = cipher.decrypt(self._encrypted_metadata.encode()).decode()
            return json.loads(decrypted)
        return {}
```
- **Recommendation**:
  1. Decide: Is this field needed?
  2. If YES: Implement encryption/decryption methods
  3. If NO: Remove via migration script
  4. Never leave unused fields in security-sensitive applications
  5. Add field documentation comment

---

### **22. LOW: No Database Connection Pooling for Concurrent Access**
- **Issue**: SessionLocal() creates new connection for each request; may cause SQLite locking under high concurrency
- **Risk Level**: **LOW** (but impacts availability)
- **DevSecOps Principle**: Availability, Resource Management
- **File & Line**: `database/connection.py:30-34`
- **Current Code**:
```python
engine = create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}, echo=False
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```
- **Compliant Fix**:
```python
from sqlalchemy.pool import StaticPool, NullPool

# For SQLite (single file database):
if "sqlite" in DATABASE_URL:
    # Use StaticPool for single-threaded access or NullPool to avoid locks
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False, "timeout": 10},  # 10s timeout
        poolclass=NullPool,  # No connection pooling for SQLite
        echo=False
    )
else:
    # For PostgreSQL (recommended for production):
    from sqlalchemy.pool import QueuePool
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,  # Verify connections before use
        echo=False
    )
```
- **Recommendation**:
  1. For production: Migrate to PostgreSQL (better concurrency)
  2. Add connection timeout handling
  3. Implement connection retry logic
  4. Monitor database lock contention
  5. Add query timeout configuration

---

## **LOW SEVERITY FINDINGS**

### **23. LOW: Incomplete Audit Action Constants**
- **Issue**: AuditLog has BACKUP_CREATE and DATA_EXPORT actions defined but DATA_EXPORT is not actually logged anywhere
- **Risk Level**: **LOW**
- **DevSecOps Principle**: Consistency, Auditability
- **File & Line**: `services/audit.py:14-27`
- **Compliant Fix**: Either implement DATA_EXPORT action or remove from constants:
```python
# If export is implemented, log it:
def log_data_export(self, export_type: str, record_count: int):
    self.log(
        action=self.ACTIONS["DATA_EXPORT"],
        resource_type="system",
        details={
            "export_type": export_type,  # json, csv, pdf
            "records_count": record_count,
        },
    )

# If export is NOT implemented, remove the constant:
# DELETE: "DATA_EXPORT": "data.export",
```
- **Recommendation**: Complete DATA_EXPORT functionality or clean up unused constants

---

### **24. LOW: Error Messages May Leak Information**
- **Issue**: Authentication error messages differentiate between "user not found" and "invalid password", allowing username enumeration
- **Risk Level**: **LOW**
- **DevSecOps Principle**: Information Disclosure Prevention
- **File & Line**: `utils/auth.py:125-135`
- **Current Code** (in service):
```python
db_user = db.query(DBUser).filter(
    DBUser.username == username,
    DBUser.is_active == True
).first()

if not db_user:
    return None  # Implicitly different from wrong password

if not self._verify_password(password, db_user.password_hash):
    return None  # Same return as not found
```
- **Compliant Fix**:
```python
def authenticate(self, username: str, password: str) -> Optional[User]:
    """Authenticate user - generic error messages prevent username enumeration"""
    self._ensure_admin_exists()
    
    db = SessionLocal()
    try:
        db_user = db.query(DBUser).filter(
            DBUser.username == username,
            DBUser.is_active == True
        ).first()
        
        # Always verify password (even if user not found) to prevent timing attacks
        if not db_user:
            # Hash a dummy password to take similar time
            bcrypt.checkpw(b"dummy", bcrypt.gensalt())
            return None
        
        if not self._verify_password(password, db_user.password_hash):
            return None
        
        # Success
        return User(...)
    finally:
        db.close()

# In UI - use generic error message:
if not login(username, password):
    st.error("❌ Credenciales inválidas")  # Don't say "user not found"
```
- **Recommendation**:
  1. Use generic error messages: "Invalid credentials"
  2. Implement constant-time comparisons (bcrypt does this)
  3. Slow down failed attempts (optional 100ms delay)
  4. Don't enumerate users via error messages

---

## **SUMMARY & PRIORITY ACTIONS**

### **Critical (Immediate):**
1. ✅ **#1**: Change JWT secret from hardcoded default → Require environment variable
2. ✅ **#2**: Remove hardcoded admin password "admin123" → Require env var setup
3. ✅ **#3**: Move JWT token from URL parameters → Use secure HTTP-only cookies or server-side only
4. ✅ **#4**: Update passlib requirement → Remove (unmaintained since 2013)

### **High (This Week):**
5. ✅ **#5**: Implement encryption for test_session data fields
6. ✅ **#6**: Add data retention/TTL policy with soft deletes
7. ✅ **#7**: Fix audit log SQL injection risk
8. ✅ **#8**: Log failed authentication attempts
9. ✅ **#9**: Remove patient IDs from audit logs
10. ✅ **#10**: Encrypt backup files

### **Medium (This Sprint):**
11. ✅ **#11**: Document HTTPS/TLS deployment requirement
12-22. Additional medium-level findings above

### **Low (Backlog):**
23-24. Low severity improvements

---

## **COMPLIANCE MATRIX**

| Finding | GDPR Article | DevSecOps Principle | Risk | Status |
|---------|--------------|-------------------|------|--------|
| JWT Secret | 32 | Secret Mgmt | CRITICAL | ❌ OPEN |
| Admin Password | 32 | Credentials | CRITICAL | ❌ OPEN |
| JWT in URL | 32 | Transport Security | CRITICAL | ❌ OPEN |
| Passlib Update | 32 | Dependencies | HIGH | ❌ OPEN |
| Data Encryption | 5, 32 | Encryption at Rest | HIGH | ❌ OPEN |
| Data Retention | 5, 17 | Data Minimization | HIGH | ❌ OPEN |
| Audit SQL | 32 | Input Validation | HIGH | ❌ OPEN |
| Failed Logins | 32 | Monitoring | HIGH | ❌ OPEN |
| Audit Logs PII | 5, 9 | Data Minimization | HIGH | ❌ OPEN |
| Backup Encryption | 32 | Encryption | HIGH | ❌ OPEN |
| HTTPS Enforcement | 32 | Transport Security | HIGH | ⚠️ CONFIG |

---

## **RECOMMENDED DEPLOYMENT ARCHITECTURE**

```
┌─────────────────────────────────────────────────────────────┐
│ User Browser (HTTPS only)                                   │
└─────────────────┬───────────────────────────────────────────┘
                  │ TLS 1.3
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ WAF + Load Balancer (AWS ALB, Cloudflare, etc.)            │
│ - CSRF protection                                           │
│ - Rate limiting                                             │
│ - DDoS protection                                           │
│ - Force HTTPS redirect                                      │
└─────────────────┬───────────────────────────────────────────┘
                  │ Internal HTTPS
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ Streamlit Application Server                                │
│ - Environment variables loaded from secure vault            │
│ - Session storage in encrypted database                    │
│ - Session-based auth (not URL tokens)                      │
└─────────────────┬───────────────────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────────────────┐
│ PostgreSQL Database (encrypted at rest)                     │
│ - Field-level encryption for sensitive data                │
│ - Automated encrypted backups                              │
│ - Access logs & monitoring                                 │
└─────────────────────────────────────────────────────────────┘
                  
Environment Variables (AWS Secrets Manager / Azure Key Vault):
  - AUTH_SECRET_KEY (32+ random bytes)
  - ADMIN_PASSWORD (strong password)
  - DATA_ENCRYPTION_KEY (Fernet key)
  - DATABASE_URL (PostgreSQL connection string)
```

---

**Audit completed**: Comprehensive review of 30+ Python files covering authentication, database, audit logging, and GDPR compliance. All findings documented with compliant code fixes.