# GCP Sandbox Deployment Guide
# Project: commodity-plafform-sandbox

## 🚀 Quick Start

### Prerequisites
1. GCP account with billing enabled
2. Project created: `commodity-plafform-sandbox`
3. APIs enabled (run setup script)
4. gcloud CLI installed and authenticated

### Deploy Infrastructure

```bash
# From repository root
cd infra/gcp/sandbox

# Run setup script
./setup.sh
```

This will create:
- Cloud SQL (PostgreSQL 15)
- Memorystore (Redis 7)
- VPC Connector
- Storage Buckets
- Pub/Sub Topics
- Service Accounts
- Secrets

**Estimated time:** 15-20 minutes

---

## 📋 Manual Steps After Setup

### 1. Update API Keys in Secret Manager

```bash
# OpenAI API Key
echo -n "sk-your-openai-key" | gcloud secrets versions add openai-key --data-file=-

# Anthropic API Key  
echo -n "sk-your-anthropic-key" | gcloud secrets versions add anthropic-key --data-file=-

# Twilio (optional)
echo -n "your-twilio-token" | gcloud secrets versions add twilio-auth-token --data-file=-

# Stripe (optional)
echo -n "sk_test_your-stripe-key" | gcloud secrets versions add stripe-secret-key --data-file=-
```

### 2. Connect GitHub to Cloud Build

1. Go to: https://console.cloud.google.com/cloud-build/triggers
2. Click "Connect Repository"
3. Select GitHub and authorize
4. Select repository: `rnrlcrm/Commodity-erp-rnrl`
5. Create trigger:
   - **Name:** `deploy-sandbox`
   - **Branch:** `^main$`
   - **Build configuration:** `cloudbuild.yaml`

### 3. Create Service Account Key for GitHub Actions

```bash
# Create CI/CD service account
gcloud iam service-accounts create ci-cd-deployer \
  --display-name="CI/CD Deployer"

# Grant permissions
gcloud projects add-iam-policy-binding commodity-plafform-sandbox \
  --member="serviceAccount:ci-cd-deployer@commodity-plafform-sandbox.iam.gserviceaccount.com" \
  --role="roles/cloudbuild.builds.editor"

gcloud projects add-iam-policy-binding commodity-plafform-sandbox \
  --member="serviceAccount:ci-cd-deployer@commodity-plafform-sandbox.iam.gserviceaccount.com" \
  --role="roles/run.admin"

gcloud projects add-iam-policy-binding commodity-plafform-sandbox \
  --member="serviceAccount:ci-cd-deployer@commodity-plafform-sandbox.iam.gserviceaccount.com" \
  --role="roles/iam.serviceAccountUser"

# Create key
gcloud iam service-accounts keys create ~/gcp-key.json \
  --iam-account=ci-cd-deployer@commodity-plafform-sandbox.iam.gserviceaccount.com

# Copy the JSON content and add to GitHub Secrets as GCP_SA_KEY
cat ~/gcp-key.json
```

### 4. Add GitHub Secret

1. Go to: https://github.com/rnrlcrm/Commodity-erp-rnrl/settings/secrets/actions
2. Click "New repository secret"
3. Name: `GCP_SA_KEY`
4. Value: Paste the entire JSON content from `gcp-key.json`

---

## 🚢 Deployment

### Automatic (via GitHub)
Push to `main` branch triggers automatic deployment:

```bash
git push origin main
```

### Manual (via Cloud Build)
```bash
gcloud builds submit \
  --config=cloudbuild.yaml \
  --timeout=30m
```

---

## 📊 Verify Deployment

### Check Cloud Run services
```bash
gcloud run services list --region=us-central1
```

### Get service URLs
```bash
# Backend
gcloud run services describe backend-service \
  --region=us-central1 \
  --format='value(status.url)'

# Frontend  
gcloud run services describe frontend-service \
  --region=us-central1 \
  --format='value(status.url)'
```

### Test backend health
```bash
BACKEND_URL=$(gcloud run services describe backend-service --region=us-central1 --format='value(status.url)')
curl $BACKEND_URL/health
```

---

## 🔍 Monitoring & Logs

### View logs
```bash
# Backend logs
gcloud run services logs read backend-service --region=us-central1 --limit=50

# Frontend logs
gcloud run services logs read frontend-service --region=us-central1 --limit=50
```

### Cloud Console
- **Cloud Run:** https://console.cloud.google.com/run?project=commodity-plafform-sandbox
- **Cloud SQL:** https://console.cloud.google.com/sql?project=commodity-plafform-sandbox
- **Logs:** https://console.cloud.google.com/logs?project=commodity-plafform-sandbox

---

## 💰 Cost Management

### View current spending
```bash
gcloud billing accounts list
gcloud billing projects describe commodity-plafform-sandbox
```

### Set budget alert
Already configured in setup script for $100/month

### Cost breakdown
- Cloud Run: ~$10-15/month
- Cloud SQL: ~$7/month
- Redis: ~$30/month
- VPC Connector: ~$10/month
- Load Balancer: ~$18/month
- Storage: ~$5/month
- **Total: ~$80-100/month**

---

## 🗑️ Cleanup

To delete all resources:
```bash
./cleanup.sh
```

To delete entire project:
```bash
gcloud projects delete commodity-plafform-sandbox
```

---

## 🐛 Troubleshooting

### Build fails
Check Cloud Build logs:
```bash
gcloud builds list --limit=5
gcloud builds log <BUILD_ID>
```

### Cloud Run service won't start
Check service logs:
```bash
gcloud run services logs read backend-service --region=us-central1
```

### Database connection issues
Verify VPC connector:
```bash
gcloud compute networks vpc-access connectors describe cotton-erp-connector --region=us-central1
```

### Secrets not found
List secrets:
```bash
gcloud secrets list
```

---

## 📱 Mobile App Configuration

Update mobile app to use sandbox backend:

```typescript
// mobile/.env
EXPO_PUBLIC_API_URL=https://backend-service-XXX.run.app
```

Get the URL:
```bash
gcloud run services describe backend-service --region=us-central1 --format='value(status.url)'
```
