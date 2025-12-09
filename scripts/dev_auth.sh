#!/bin/bash
# Local Development - Authenticated Backend Testing
# This script helps developers make authenticated requests to the Cloud Run backend

BACKEND_URL="https://backend-service-565186585906.us-central1.run.app"

echo "🔐 Cotton ERP - Local Development Authentication Helper"
echo "=================================================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "❌ gcloud CLI is not installed"
    echo "Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Check if authenticated
if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" &> /dev/null; then
    echo "❌ You are not authenticated with gcloud"
    echo "Run: gcloud auth login"
    exit 1
fi

echo "✅ Authenticated as: $(gcloud auth list --filter=status:ACTIVE --format='value(account)')"
echo ""

# Function to get identity token
get_token() {
    gcloud auth print-identity-token --audiences="$BACKEND_URL" 2>/dev/null
}

# Function to make authenticated request
auth_curl() {
    local endpoint="$1"
    local method="${2:-GET}"
    local data="$3"
    
    local token=$(get_token)
    if [ -z "$token" ]; then
        echo "❌ Failed to get identity token"
        exit 1
    fi
    
    local url="${BACKEND_URL}${endpoint}"
    echo "🌐 $method $url"
    echo ""
    
    if [ -n "$data" ]; then
        curl -X "$method" \
             -H "Authorization: Bearer $token" \
             -H "Content-Type: application/json" \
             -d "$data" \
             "$url"
    else
        curl -X "$method" \
             -H "Authorization: Bearer $token" \
             "$url"
    fi
    echo ""
}

# Show menu
show_menu() {
    echo ""
    echo "Choose an option:"
    echo "1) Test health endpoint"
    echo "2) Get identity token (export to env)"
    echo "3) Custom curl request"
    echo "4) Exit"
    echo ""
    read -p "Enter choice [1-4]: " choice
    
    case $choice in
        1)
            echo ""
            auth_curl "/health"
            show_menu
            ;;
        2)
            echo ""
            TOKEN=$(get_token)
            echo "export BACKEND_TOKEN='$TOKEN'"
            echo ""
            echo "Copy the above line and run it in your terminal, then use:"
            echo "curl -H \"Authorization: Bearer \$BACKEND_TOKEN\" $BACKEND_URL/health"
            show_menu
            ;;
        3)
            echo ""
            read -p "Enter endpoint path (e.g., /api/v1/users): " endpoint
            read -p "Enter HTTP method [GET]: " method
            method=${method:-GET}
            
            if [ "$method" != "GET" ]; then
                read -p "Enter JSON data (or press Enter to skip): " data
                auth_curl "$endpoint" "$method" "$data"
            else
                auth_curl "$endpoint" "$method"
            fi
            show_menu
            ;;
        4)
            echo "Goodbye!"
            exit 0
            ;;
        *)
            echo "Invalid choice"
            show_menu
            ;;
    esac
}

# Start
show_menu
