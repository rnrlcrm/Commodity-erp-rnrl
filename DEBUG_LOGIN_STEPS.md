# Login Debug Steps

## Branch: `debug-login-issue`

I've added comprehensive debug logging to trace the login failure. Here's what to do:

## Steps to Debug

### 1. Deploy Frontend with Debug Logs

```bash
# In Cloud Shell
cd ~/Commodity-erp-rnrl
git fetch origin
git checkout debug-login-issue
cd frontend
npm run build
# Deploy to Cloud Run (follow your deployment process)
```

### 2. Test Login and Check Browser Console

1. Open https://frontend-service-565186585906.us-central1.run.app/
2. Open Browser Developer Tools (F12)
3. Go to Console tab
4. Try logging in with:
   - Email: `admin@rnrl.com`
   - Password: `Rnrl@Admin1`
5. Look for debug messages:
   - `[DEBUG] Login started with credentials:`
   - `[DEBUG authService] Login endpoint:`
   - `[DEBUG authService] Full URL:`
   - `[DEBUG] Login error caught:` (if it fails)

### 3. Check Backend Logs

```bash
# Check backend Cloud Run logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=backend-service" \
  --limit 50 \
  --format json \
  --project commodity-plafform-sandbox
```

## What I've Done

### Changes Made:
1. **Fixed Password Hashing Algorithm**
   - Changed from `bcrypt` to `pbkdf2_sha256` to match backend
   - Commit: `eb8b69b` and `24eacda`

2. **Fixed Database Connection**
   - Changed from localhost to Cloud SQL (10.40.0.3:5432)
   - Commit: `1bc2738`

3. **Added Auto-Detection for NOT NULL Columns**
   - Script now automatically detects and fills all required database fields
   - Commit: `dbe3404`

4. **Added Debug Logging** (debug-login-issue branch)
   - Frontend: authStore.ts and authService.ts
   - Shows exact API calls, responses, and errors
   - Commit: `73fc11c`

### Super Admin User Status:
✅ Created successfully via Cloud Run Job
- Email: admin@rnrl.com
- Password: Rnrl@Admin1
- User Type: SUPER_ADMIN
- Password Hash: Using pbkdf2_sha256 (matches backend)

## Potential Issues to Check

### Issue 1: User Not Created
**Symptom:** Error says "Invalid credentials" or "User not found"
**Check:** 
```sql
SELECT id, email, user_type, is_active, password_hash 
FROM users 
WHERE email = 'admin@rnrl.com';
```

### Issue 2: Password Hash Mismatch
**Symptom:** Error says "Invalid credentials" after user is found
**Cause:** Password verification failing
**Solution:** Need to re-run Cloud Run Job after password hash fix

### Issue 3: User Type Issue
**Symptom:** Error says "EXTERNAL users must login via mobile OTP"
**Check:** User type should be 'SUPER_ADMIN', not 'EXTERNAL'

### Issue 4: Missing Organization ID in Token
**Symptom:** Error during token creation
**Check:** SUPER_ADMIN should have organization_id = NULL

### Issue 5: CORS or Network Issue
**Symptom:** Network error, no response from backend
**Check:** 
- Frontend is hitting correct backend URL
- CORS is configured properly
- VPC connector is working

## Expected Debug Output (Success Case)

```
[DEBUG] Login started with credentials: {email: "admin@rnrl.com", passwordLength: 11}
[DEBUG authService] Login endpoint: /settings/auth/login
[DEBUG authService] Full URL: https://backend-service-xxx.run.app/api/v1/settings/auth/login
[DEBUG authService] Credentials: {email: "admin@rnrl.com", passwordLength: 11}
[DEBUG authService] Response status: 200
[DEBUG authService] Response data: {access_token: "...", refresh_token: "..."}
[DEBUG] Login response received: {access_token: "...", refresh_token: "..."}
[DEBUG] Tokens received, storing...
[DEBUG] Fetching current user...
[DEBUG] User fetched: {id: "...", email: "admin@rnrl.com", ...}
[DEBUG] Fetching capabilities...
[DEBUG] Capabilities loaded: X
[DEBUG] Login successful, updating state
```

## Expected Debug Output (Failure Case)

```
[DEBUG] Login started with credentials: {email: "admin@rnrl.com", passwordLength: 11}
[DEBUG authService] Login endpoint: /settings/auth/login
[DEBUG authService] Full URL: https://backend-service-xxx.run.app/api/v1/settings/auth/login
[DEBUG authService] Credentials: {email: "admin@rnrl.com", passwordLength: 11}
[DEBUG] Login error caught: AxiosError {...}
[DEBUG] Error response: {data: {detail: "..."}, status: 401}
[DEBUG] Error data: {detail: "Invalid credentials"}
[DEBUG] Error status: 401
[DEBUG] AuthError created: {message: "Invalid credentials", code: "401"}
```

## Next Steps After Getting Debug Output

1. **Share the console output** - Send me the full debug logs
2. **Check backend logs** - Look for errors on backend side
3. **Verify database** - Run SQL query to confirm user exists
4. **Re-run Cloud Run Job if needed** - If password hash is wrong

## Quick Fix Commands

If you need to delete and recreate the admin user:

```bash
# Delete existing admin
gcloud sql connect [INSTANCE_NAME] --user=commodity_user --database=commodity_erp
# In psql:
DELETE FROM users WHERE email = 'admin@rnrl.com';

# Re-run creation job
gcloud run jobs execute create-superadmin --region=us-central1 --wait
```
