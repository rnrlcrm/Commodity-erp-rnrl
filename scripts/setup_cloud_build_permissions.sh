#!/bin/bash
# Setup Cloud Build Permissions for Authenticated Backend Access
# Run this in Google Cloud Shell

set -e

PROJECT_ID="commodity-plafform-sandbox"
REGION="us-central1"
SERVICE_NAME="backend-service"

echo "Setting up Cloud Build permissions for authenticated backend access..."

# Set the project
gcloud config set project $PROJECT_ID

# Get the Cloud Build service account
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")
CLOUDBUILD_SA="${PROJECT_NUMBER}@cloudbuild.gserviceaccount.com"

echo "Project Number: $PROJECT_NUMBER"
echo "Cloud Build Service Account: $CLOUDBUILD_SA"

# Grant Cloud Build the Cloud Run Invoker role
echo "Granting roles/run.invoker to Cloud Build service account..."
gcloud run services add-iam-policy-binding $SERVICE_NAME \
  --region=$REGION \
  --member="serviceAccount:$CLOUDBUILD_SA" \
  --role="roles/run.invoker"

echo "✅ Cloud Build can now invoke the backend service"

# Verify the policy
echo ""
echo "Current IAM policy for $SERVICE_NAME:"
gcloud run services get-iam-policy $SERVICE_NAME --region=$REGION

echo ""
echo "✅ Setup complete! Cloud Build health checks should now work."
