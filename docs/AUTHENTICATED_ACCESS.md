# Authenticated Backend Access Setup

## Overview

Due to organization policies, all Cloud Run services require authenticated access. This document explains how to properly authenticate requests to the backend service from:

- ✅ Cloud Build (CI/CD)
- ✅ Frontend service
- ✅ Local development

## Architecture

```
┌─────────────────┐
│  Cloud Build    │──────┐
│  (CI/CD)        │      │
└─────────────────┘      │
                         │    Identity Token (IAM-based)
┌─────────────────┐      │    ┌──────────────────────┐
│   Frontend      │──────┼───▶│  Backend Service     │
│  (Cloud Run)    │      │    │  (Cloud Run)         │
└─────────────────┘      │    └──────────────────────┘
                         │
┌─────────────────┐      │
│   Developer     │──────┘
│  (Local)        │
└─────────────────┘
```

## Quick Start

### 1. Setup Cloud Build Permissions

Run this in **Google Cloud Shell**:

```bash
cd /path/to/project
./scripts/setup_cloud_build_permissions.sh
```

This grants the Cloud Build service account permission to invoke the backend during health checks.

### 2. Setup Service-to-Service Auth

Run this in **Google Cloud Shell**:

```bash
./scripts/setup_service_auth.sh
```

This configures:
- Frontend → Backend authentication
- Backend → Backend (internal calls)
- Restricted ingress settings

### 3. Update Frontend Code

Replace direct `fetch()` calls with the authenticated API client:

**Before:**
```javascript
const response = await fetch('/api/v1/users');
```

**After:**
```javascript
import { api } from './utils/authenticatedApi';

const response = await api.get('/api/v1/users');
const users = await response.json();
```

### 4. Local Development

For local testing, use the development auth helper:

```bash
./scripts/dev_auth.sh
```

This interactive script allows you to:
- Test the health endpoint
- Get identity tokens
- Make custom authenticated requests

## Files Created

### 1. `cloudbuild.yaml` (Updated)
- Health check now uses `gcloud auth print-identity-token`
- Authenticates with service account identity

### 2. `scripts/setup_cloud_build_permissions.sh`
- Grants Cloud Build service account the `roles/run.invoker` role
- Run in Google Cloud Shell

### 3. `scripts/setup_service_auth.sh`
- Configures frontend and backend service accounts
- Sets up ingress restrictions
- Run in Google Cloud Shell

### 4. `scripts/dev_auth.sh`
- Interactive local development helper
- Gets identity tokens for testing
- Makes authenticated curl requests

### 5. `frontend/src/utils/authenticatedApi.js`
- Frontend utility for authenticated API calls
- Automatically gets identity tokens in Cloud Run
- Falls back to unauthenticated in dev mode

## How It Works

### Cloud Build (CI/CD)
```bash
TOKEN=$(gcloud auth print-identity-token --audiences=https://backend-service-...)
curl -H "Authorization: Bearer $TOKEN" https://backend-service-.../health
```

### Frontend (Cloud Run)
```javascript
// Get identity token from metadata server
const token = await fetch(
  'http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience=...',
  { headers: { 'Metadata-Flavor': 'Google' } }
);

// Use in requests
fetch(url, { headers: { 'Authorization': `Bearer ${token}` } });
```

### Local Development
```bash
# Get token
TOKEN=$(gcloud auth print-identity-token --audiences=https://backend-service-...)

# Use in requests
curl -H "Authorization: Bearer $TOKEN" https://backend-service-.../api/v1/users
```

## IAM Roles Required

| Service Account | Role | Purpose |
|----------------|------|---------|
| Cloud Build (`XXX@cloudbuild.gserviceaccount.com`) | `roles/run.invoker` | Health checks during deployment |
| Frontend Compute SA (`XXX-compute@developer.gserviceaccount.com`) | `roles/run.invoker` | Frontend → Backend API calls |
| Backend Runtime SA (`backend-runtime@PROJECT.iam.gserviceaccount.com`) | `roles/run.invoker` | Internal backend calls |

## Troubleshooting

### 403 Forbidden Error
```bash
# Check IAM policy
gcloud run services get-iam-policy backend-service --region=us-central1

# Verify your account has invoker role
gcloud run services add-iam-policy-binding backend-service \
  --region=us-central1 \
  --member="user:YOUR_EMAIL@domain.com" \
  --role="roles/run.invoker"
```

### Cloud Build Health Check Fails
```bash
# Verify Cloud Build has invoker role
./scripts/setup_cloud_build_permissions.sh
```

### Frontend Can't Access Backend
```bash
# Run service auth setup
./scripts/setup_service_auth.sh

# Verify frontend is using authenticatedApi.js
```

### Local Development Issues
```bash
# Login to gcloud
gcloud auth login

# Get token manually
gcloud auth print-identity-token --audiences=https://backend-service-565186585906.us-central1.run.app

# Test with curl
TOKEN=$(gcloud auth print-identity-token --audiences=https://backend-service-565186585906.us-central1.run.app)
curl -H "Authorization: Bearer $TOKEN" https://backend-service-565186585906.us-central1.run.app/health
```

## Security Best Practices

1. **Never use `allUsers` or `allAuthenticatedUsers`** - Organization policy blocks this
2. **Use specific service accounts** - Grant least-privilege access
3. **Restrict ingress** - Use `internal-and-cloud-load-balancing` when possible
4. **Rotate tokens** - Identity tokens are short-lived (1 hour)
5. **Monitor access** - Check Cloud Run logs for unauthorized attempts

## Next Steps (Optional)

For enterprise-grade security, consider:

### API Gateway
- Centralized authentication
- Rate limiting
- API key management
- Request validation

### Cloud Endpoints
- OpenAPI specification
- JWT validation
- Quota management
- Developer portal

### Cloud Armor
- DDoS protection
- WAF rules
- Geographic restrictions
- Bot detection

## Support

For issues or questions:
1. Check Cloud Run logs: `gcloud run services logs read backend-service --region=us-central1`
2. Verify IAM policies: `gcloud run services get-iam-policy backend-service --region=us-central1`
3. Test with dev script: `./scripts/dev_auth.sh`
