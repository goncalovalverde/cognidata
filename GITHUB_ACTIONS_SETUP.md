# GitHub Actions Setup Guide for CogniData

This guide explains how to use GitHub Actions with CogniData while keeping secrets secure.

## Problem: .env.local Contains Secrets

The `.env.local` file contains sensitive information:
- `ADMIN_PASSWORD` - Admin login password
- `AUTH_SECRET_KEY` - JWT secret for authentication
- `DATA_ENCRYPTION_KEY` - Data encryption key

**These must NEVER be committed to GitHub!**

## Solution: GitHub Secrets

GitHub provides encrypted secret storage that:
✅ Encrypts secrets at rest  
✅ Never exposes secrets in logs  
✅ Masks secrets in workflow output  
✅ Requires authentication to view  

## Setup Instructions

### Step 1: Create GitHub Secrets (One-time)

1. Go to your repository on GitHub
2. Navigate to: **Settings → Secrets and variables → Actions**
3. Click "New repository secret" and add each:

```
Name: ADMIN_PASSWORD
Value: your_admin_password_here
```

```
Name: AUTH_SECRET_KEY
Value: your_32_character_secret_key_here
```

```
Name: DATA_ENCRYPTION_KEY
Value: your_encryption_key_here (if applicable)
```

### Step 2: Use Secrets in Workflows

Workflows automatically have access to repository secrets. Reference them with:

```yaml
env:
  ADMIN_PASSWORD: ${{ secrets.ADMIN_PASSWORD }}
  AUTH_SECRET_KEY: ${{ secrets.AUTH_SECRET_KEY }}
```

These values are:
- ✅ Passed securely to the job
- ✅ Masked in logs (shown as ***)
- ✅ Never stored in workflow files
- ✅ Only accessible during job execution

## Included Workflows

### 1. Test Workflow (`.github/workflows/test.yml`)

Runs on every push and pull request:
- Installs dependencies
- Runs test suite
- Uploads test results

```bash
# Triggered automatically on:
push: main, develop
pull_request: main
```

### 2. Deploy Workflow (`.github/workflows/deploy.yml`)

Runs on push to main branch:
- Validates secrets
- Updates dependencies
- Deploys to production
- Verifies app is running

```bash
# Triggered automatically on:
push: main
# Manual trigger via workflow_dispatch
```

## Local Development

Your local `.env.local` file is NOT used by GitHub Actions (and should never be committed):

```bash
# Local development - environment variables load from .env.local
source venv/bin/activate
streamlit run app.py

# GitHub Actions - secrets come from GitHub Settings, not .env.local
# Workflow automatically passes secrets as environment variables
```

## Security Best Practices

✅ **DO:**
- Use GitHub Secrets for ALL sensitive values
- Use different secrets for dev/staging/prod
- Rotate secrets monthly
- Review who has access to secrets
- Use branch protection rules

❌ **DON'T:**
- Commit `.env.local` to repository
- Hardcode secrets in workflow files
- Use the same secrets for different environments
- Share secrets via email or chat
- Store production credentials in development

## Verify Secrets are Configured

Check that all required secrets exist:

```bash
# This won't work (secrets not visible via CLI), but you can:
# 1. Go to GitHub Settings → Secrets
# 2. Verify ADMIN_PASSWORD, AUTH_SECRET_KEY, and DATA_ENCRYPTION_KEY exist
```

Or run a test workflow and check for "Missing secrets" error in logs.

## Troubleshooting

### Error: "Missing required GitHub Secrets"

**Solution:** 
1. Go to Settings → Secrets and variables → Actions
2. Add ADMIN_PASSWORD and AUTH_SECRET_KEY
3. Trigger workflow manually or push new commit

### Error: "ADMIN_PASSWORD environment variable is not set"

**Possible causes:**
- Secrets not configured in GitHub
- Wrong secret names (case-sensitive!)
- Workflow not using `${{ secrets.SECRET_NAME }}` syntax

**Solution:**
1. Verify secret names in GitHub exactly match workflow (case-sensitive)
2. Verify workflow uses correct syntax: `${{ secrets.ADMIN_PASSWORD }}`
3. Try manual trigger: Actions → Select workflow → Run workflow

### Workflow fails but can't see error details

GitHub masks secret values in logs for security. To debug:
1. Add non-sensitive debug statements
2. Check logs for which step failed
3. Review the workflow step carefully
4. Test locally first: `set -a && source .env.local && set +a && streamlit run app.py`

## For Different Environments

If you deploy to multiple environments (dev, staging, production):

### Option 1: Environment Secrets (Recommended)

Create secrets for each environment:
```
Organization Settings → Environments → dev → Secrets
Organization Settings → Environments → staging → Secrets
Organization Settings → Environments → production → Secrets
```

Update workflows to use specific environment:
```yaml
jobs:
  deploy-prod:
    runs-on: self-hosted
    environment: production  # Uses production secrets only
```

### Option 2: Separate Secret Names

Use different secret names:
```
ADMIN_PASSWORD_DEV=test_password
ADMIN_PASSWORD_PROD=production_password
```

Then in workflow:
```yaml
env:
  ADMIN_PASSWORD: ${{ secrets.ADMIN_PASSWORD_PROD }}
```

## Rotating Secrets

Secrets should be rotated monthly:

1. Generate new value (e.g., new password)
2. Update secret in GitHub Settings
3. Update `.env.local` locally
4. Restart any running instances
5. Update password in database if needed

## Additional Resources

- [GitHub Secrets Documentation](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
- [GitHub Actions Best Practices](https://docs.github.com/en/actions/guides/security-hardening-for-github-actions)
- [GitHub Environments](https://docs.github.com/en/actions/deployment/targeting-different-environments)

## Questions?

If workflows fail with secret-related errors:
1. Check that all secrets are configured
2. Verify secret names match exactly (case-sensitive)
3. Ensure workflows use `${{ secrets.NAME }}` syntax
4. Review action logs for specific error messages
