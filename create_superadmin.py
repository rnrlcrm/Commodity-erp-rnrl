#!/usr/bin/env python3
"""
Create Super Admin User via Backend API
Run this in Google Cloud Shell - uses deployed backend service
"""

import requests
import subprocess
import sys

# Backend URL
BACKEND_URL = "https://backend-service-565186585906.us-central1.run.app"

def get_identity_token():
    """Get identity token for authentication"""
    result = subprocess.run(
        ["gcloud", "auth", "print-identity-token", f"--audiences={BACKEND_URL}"],
        capture_output=True,
        text=True
    )
    return result.stdout.strip()

def create_superadmin():
    """Create superadmin user via backend API"""
    
    print("=" * 60)
    print("Creating Super Admin User")
    print("=" * 60)
    
    # Get identity token
    print("\n🔑 Getting authentication token...")
    token = get_identity_token()
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Admin credentials
    admin_data = {
        "email": "admin@rnrl.com",
        "password": "Admin@123",
        "full_name": "Super Administrator"
    }
    
    print(f"\n📝 Creating superadmin: {admin_data['email']}")
    
    # Call signup-internal endpoint (for INTERNAL users)
    try:
        response = requests.post(
            f"{BACKEND_URL}/api/v1/settings/auth/signup-internal",
            headers=headers,
            json=admin_data,
            timeout=10
        )
        
        print(f"\n📡 Response Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("✅ Super Admin created successfully!")
            print("\n📧 Email:    admin@rnrl.com")
            print("🔑 Password: Admin@123")
            print("\n🌐 Login at: https://frontend-service-565186585906.us-central1.run.app/")
            
        elif "already exists" in response.text.lower():
            print("\nℹ️  Super Admin already exists!")
            print("📧 Email:    admin@rnrl.com")
            print("🔑 Password: Admin@123")
            print("\n🌐 Login at: https://frontend-service-565186585906.us-central1.run.app/")
            
        else:
            print("❌ Error creating superadmin:")
            print(f"   Status: {response.status_code}")
            print(f"   Response: {response.text}")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)

if __name__ == '__main__':
    create_superadmin()
