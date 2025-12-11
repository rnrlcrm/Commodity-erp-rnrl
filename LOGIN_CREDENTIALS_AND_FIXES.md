# Login Credentials & Capability System

## ✅ SUPER_ADMIN CREDENTIALS

**Current Password in Database:** `Rnrl@Admin123`

### Login Details:
- **Email:** `admin@rnrl.com`
- **Password:** `Rnrl@Admin123` ← **USE THIS PASSWORD**
- **User Type:** SUPER_ADMIN
- **Capabilities:** 91/91 (100% - Full System Access)

---

## 🔐 How Capability System Works

### 1. **SUPER_ADMIN** (admin@rnrl.com)
- ✅ Has ALL 91 capabilities
- ✅ Can access everything in the system
- ✅ No restrictions on any module
- ✅ Can manage users, organizations, partners, trading, etc.

### 2. **INTERNAL Users** (Back Office Staff)
- Get capabilities based on their assigned role
- Examples: Manager, Director, Accountant, etc.
- Can be assigned specific capabilities via Admin UI
- Access is restricted to what capabilities they have

### 3. **EXTERNAL Users** (Trading Partners)
- Get capabilities based on their business partner relationship
- Examples: Supplier, Buyer, Trader, etc.
- Limited to trading operations relevant to their business
- Cannot access back office functions

---

## 🚫 PUBLIC Endpoints (No Capability Required)

These endpoints should be accessible WITHOUT authentication:

### Auth Endpoints:
- `/api/v1/settings/auth/login` - Login endpoint
- `/api/v1/settings/auth/signup` - Public signup
- `/api/v1/settings/auth/signup-internal` - Internal user signup  
- `/api/v1/settings/auth/refresh` - Token refresh
- `/api/v1/settings/auth/verify-otp` - OTP verification

**Why?** Because users cannot have capabilities until they login first!

---

## 🔧 Fixes Applied

### Issue: Login was returning blank/401 error
**Root Cause:** Login endpoint had `RequireCapability(Capabilities.AUTH_LOGIN)` which created a circular dependency - you need to be logged in to have capabilities, but you need capabilities to login!

### Solution Applied:
Removed capability checks from public auth endpoints in `backend/modules/settings/router.py`:

```python
# BEFORE (Wrong - required auth to login!)
@router.post("/auth/login", tags=["auth"])
async def login(
    ...,
    _check: None = Depends(RequireCapability(Capabilities.AUTH_LOGIN))  ❌
)

# AFTER (Correct - public endpoint)
@router.post("/auth/login", tags=["auth"])
async def login(
    ...,
    # No capability check - public endpoint ✅
)
```

---

## 🎯 Capability System Design

### How It Works:

1. **User Logs In** (No capability required)
   - POST `/api/v1/settings/auth/login`
   - Receives JWT access token
   
2. **Token Contains User Info**
   - User ID, email, user_type
   - Server checks capabilities on each request
   
3. **Protected Endpoints Check Capabilities**
   - Example: `@Depends(RequireCapability(Capabilities.AVAILABILITY_CREATE))`
   - Server queries `user_capabilities` table
   - Allows/denies based on user's capabilities

### Example Flow:

```
1. User: admin@rnrl.com logs in with Rnrl@Admin123
2. Backend: Validates password, returns JWT token
3. User: Makes request to create availability
4. Backend: Checks if user has AVAILABILITY_CREATE capability
5. SUPER_ADMIN: Has all capabilities → Request allowed ✅
6. Normal User: Check their specific capabilities → Allow/Deny accordingly
```

---

## 📊 Capability Categories

| Category | Count | Purpose |
|----------|-------|---------|
| AUTH | 7 | Authentication & authorization |
| ORG | 7 | Organization management |
| PARTNER | 8 | Business partner management |
| COMMODITY | 7 | Commodity trading |
| LOCATION | 5 | Location & warehouse management |
| AVAILABILITY | 11 | Availability management |
| REQUIREMENT | 10 | Requirement management |
| MATCHING | 6 | Matching engine |
| SETTINGS | 4 | System settings |
| INVOICE | 3 | Invoice management |
| CONTRACT | 1 | Contract management |
| PAYMENT | 1 | Payment processing |
| SHIPMENT | 1 | Shipment tracking |
| ADMIN | 7 | Admin operations |
| AUDIT | 2 | Audit logs |
| DATA | 4 | Data import/export |
| PUBLIC | 1 | Public access |
| SYSTEM | 6 | System operations |

---

## 🧪 Test Login

### Using cURL:
```bash
curl -X POST http://localhost:8000/api/v1/settings/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "admin@rnrl.com", "password": "Rnrl@Admin123"}'
```

### Expected Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "expires_in": 3600
}
```

### Frontend Login:
```
URL: http://localhost:3000/login
Email: admin@rnrl.com
Password: Rnrl@Admin123
```

---

## ⚠️ Password Confusion

There were TWO different passwords in the codebase:

1. **`Rnrl@Admin1`** - Used in old production scripts (create_superadmin.py)
2. **`Rnrl@Admin123`** - Used in local validation script ← **CURRENT PASSWORD**

The database currently has `Rnrl@Admin123` because that's what was set by the validation script.

---

## 🔄 Next Steps

1. ✅ Backend fixes applied (public auth endpoints)
2. ✅ SUPER_ADMIN has all 91 capabilities
3. ✅ Password confirmed: `Rnrl@Admin123`
4. 🔄 Test frontend login with correct password
5. 🔄 Create additional INTERNAL users with specific capabilities
6. 🔄 Create EXTERNAL users for trading partners
7. 🔄 Test capability restrictions work correctly

---

## 📝 Summary

- **Password:** `Rnrl@Admin123` (not Rnrl@Admin1)
- **Capability System:** Works for SUPER_ADMIN (all capabilities) + INTERNAL/EXTERNAL (specific capabilities)
- **Public Endpoints:** Login/signup don't require capabilities (fixed)
- **Protected Endpoints:** All other endpoints check user's capabilities
- **Status:** Ready to test! 🚀
