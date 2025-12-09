#!/bin/bash
# Configure Backend Service for Secure Service-to-Service Communication
# Run this in Google Cloud Shell

set -e

PROJECT_ID="commodity-plafform-sandbox"
REGION="us-central1"
BACKEND_SERVICE="backend-service"
FRONTEND_SERVICE="frontend-service"

echo "Configuring secure service-to-service communication..."
echo ""

# Set the project
gcloud config set project $PROJECT_ID

# Get project number
PROJECT_NUMBER=$(gcloud projects describe $PROJECT_ID --format="value(projectNumber)")

echo "Step 1: Grant frontend service permission to invoke backend"
echo "-----------------------------------------------------------"

# Get frontend service account
FRONTEND_SA="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"

# Grant frontend the ability to invoke backend
gcloud run services add-iam-policy-binding $BACKEND_SERVICE \
  --region=$REGION \
  --member="serviceAccount:$FRONTEND_SA" \
  --role="roles/run.invoker"

echo "✅ Frontend can now invoke backend"
echo ""

echo "Step 2: Grant backend runtime service account invoker role (for internal calls)"
echo "--------------------------------------------------------------------------------"

BACKEND_SA="backend-runtime@${PROJECT_ID}.iam.gserviceaccount.com"

gcloud run services add-iam-policy-binding $BACKEND_SERVICE \
  --region=$REGION \
  --member="serviceAccount:$BACKEND_SA" \
  --role="roles/run.invoker"

echo "✅ Backend can invoke itself"
echo ""

echo "Step 3: Configure ingress settings for enhanced security"
echo "---------------------------------------------------------"

# Update backend to restrict ingress
gcloud run services update $BACKEND_SERVICE \
  --region=$REGION \
  --ingress=internal-and-cloud-load-balancing

echo "✅ Backend ingress restricted to internal and load balancer traffic"
echo ""

echo "Step 4: Verify IAM policy"
echo "-------------------------"
gcloud run services get-iam-policy $BACKEND_SERVICE --region=$REGION

echo ""
echo "✅ Service-to-service authorization configured successfully!"
echo ""
echo "Summary:"
echo "--------"
echo "✓ Frontend can invoke backend with identity tokens"
echo "✓ Backend can make internal calls to itself"
echo "✓ External direct access requires authentication"
echo "✓ Ingress limited to internal traffic and load balancers"
echo ""
echo "Next steps:"
echo "-----------"
echo "1. Update frontend to use authenticatedApi.js for all backend calls"
echo "2. Test the deployment with: ./scripts/dev_auth.sh"
echo "3. Monitor Cloud Run logs for authentication issues"
