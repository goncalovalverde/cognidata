# 🔒 Critical Security Fixes - Quick Start Guide

## What Changed?

4 critical security vulnerabilities have been fixed. **You MUST set environment variables before running the application.**

## ⚡ Quick Setup (5 minutes)

### Step 1: Generate JWT Secret Key
```bash
python3 -c 'import secrets; print(secrets.token_urlsafe(32))'
```
Copy the output (it will look like: `Drmhze6EPcv0fN_81Bj-nA`)

### Step 2: Set Environment Variables
```bash
# Replace with the key from Step 1
export AUTH_SECRET_KEY='Drmhze6EPcv0fN_81Bj-nA'

# Set a strong admin password (12+ chars, mixed case, numbers, special chars)
export ADMIN_PASSWORD='MySecureAdminPass123!'
```

### Step 3: Update Dependencies
```bash
pip install -r requirements.txt
```
(This removes unmaintained passlib library)

### Step 4: Run the Application
```bash
streamlit run app.py
```

## ✅ What Was Fixed

| Issue | Fix |
|-------|-----|
| 🔴 **JWT Secret Hardcoded** | Now requires `AUTH_SECRET_KEY` environment variable |
| 🔴 **Admin Password "admin123"** | Now requires `ADMIN_PASSWORD` environment variable |
| 🔴 **JWT Tokens in URL** | Now uses secure server-side sessions only |
| 🔴 **Unmaintained Passlib** | Removed - using bcrypt only |

## 🚨 If You Skip This

- ❌ Application will NOT start without `AUTH_SECRET_KEY`
- ❌ Application will NOT start without `ADMIN_PASSWORD`
- ❌ Clear error messages tell you what to do

## 📋 Production Deployment

For production, use a secure secrets management system:

### AWS
```bash
export AUTH_SECRET_KEY=$(aws secretsmanager get-secret-value \
  --secret-id cognidata/jwt-key --query SecretString)
export ADMIN_PASSWORD=$(aws secretsmanager get-secret-value \
  --secret-id cognidata/admin-password --query SecretString)
```

### Azure
```bash
export AUTH_SECRET_KEY=$(az keyvault secret show \
  --vault-name cognidata --name jwt-key --query value)
export ADMIN_PASSWORD=$(az keyvault secret show \
  --vault-name cognidata --name admin-password --query value)
```

### Kubernetes
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cognidata-secrets
data:
  auth-secret-key: <base64-encoded-key>
  admin-password: <base64-encoded-password>
---
apiVersion: apps/v1
kind: Deployment
spec:
  containers:
  - name: cognidata
    env:
    - name: AUTH_SECRET_KEY
      valueFrom:
        secretKeyRef:
          name: cognidata-secrets
          key: auth-secret-key
    - name: ADMIN_PASSWORD
      valueFrom:
        secretKeyRef:
          name: cognidata-secrets
          key: admin-password
```

## 📚 Documentation

For detailed information:
- **SECURITY_FIXES.md** - Full explanation of each fix
- **COMPLIANCE_AUDIT.md** - Complete security audit report
- **.env.example** - Environment variable reference

## 🆘 Troubleshooting

### Error: "FATAL: AUTH_SECRET_KEY environment variable is not set"
**Solution**: Run:
```bash
export AUTH_SECRET_KEY=$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')
streamlit run app.py
```

### Error: "FATAL: ADMIN_PASSWORD environment variable is not set"
**Solution**: Run:
```bash
export ADMIN_PASSWORD='YourSecurePassword123!'
streamlit run app.py
```

### Error: "AUTH_SECRET_KEY must be at least 32 characters"
**Solution**: Make sure you copied the FULL output from step 1:
```bash
python3 -c 'import secrets; key = secrets.token_urlsafe(32); print(f"Length: {len(key)}, Key: {key}")'
export AUTH_SECRET_KEY='the_full_key_from_above'
```

## ✨ New Features

- ✅ Tokens no longer exposed in browser history
- ✅ Tokens no longer visible in server logs
- ✅ Failed logins are now logged for security monitoring
- ✅ Session recovery via secure database lookups

## 📞 Questions?

See **SECURITY_FIXES.md** for comprehensive documentation on all changes.
