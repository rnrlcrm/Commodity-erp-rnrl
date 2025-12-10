# Internal User Management System - Comprehensive Audit Report
**Date:** December 10, 2025  
**Branch:** `audit/internal-user-management`  
**Scope:** INTERNAL backoffice users only (SUPER_ADMIN + INTERNAL user_type)  
**Exclusions:** EXTERNAL users (business partners) - separate login system via mobile OTP

---

## Executive Summary

This audit evaluates the current state of internal user management (backoffice admin users) for the Cotton ERP system. The system has strong foundational components but is **INCOMPLETE** - missing critical CRUD endpoints and UI pages for day-to-day user management operations.

### Current State: 🟡 PARTIALLY IMPLEMENTED (40% Complete)
- ✅ **User data models** - Complete with proper fields
- ✅ **Authentication** - Login/signup working
- ✅ **Capabilities system** - Permission management exists
- ❌ **User CRUD API** - Missing list, update, delete endpoints
- ❌ **Admin UI** - No user management page exists
- ❌ **User forms** - No create/edit interfaces

---

## 1. Backend Analysis

### 1.1 Data Models ✅ COMPLETE
**File:** `backend/modules/settings/models/settings_models.py`

```python
class User(Base, EventMixin):
    id: UUID (primary key)
    
    # User Type & Isolation
    user_type: str  # "SUPER_ADMIN" | "INTERNAL" | "EXTERNAL"
    organization_id: UUID (nullable)  # For INTERNAL users
    business_partner_id: UUID (nullable)  # For EXTERNAL users only
    
    # Access Control
    allowed_modules: list[str] (nullable)  # RBAC module permissions
    parent_user_id: UUID (nullable)  # For sub-users
    
    # Authentication
    email: str (unique, nullable)
    mobile_number: str (unique, nullable)
    password_hash: str (nullable)
    
    # 2FA
    two_fa_enabled: bool (default=False)
    pin_hash: str (nullable)
    
    # Status
    is_active: bool (default=True)
    is_verified: bool (default=False)
    role: str (nullable)
    full_name: str (nullable)
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
```

**Assessment:**
- ✅ Complete schema with all necessary fields
- ✅ Proper separation of INTERNAL vs EXTERNAL users
- ✅ Supports SUPER_ADMIN (all access) and INTERNAL (org-scoped)
- ✅ Module-based access control via `allowed_modules`
- ✅ Relationships and foreign keys properly defined

---

### 1.2 Repository Layer ⚠️ INCOMPLETE
**File:** `backend/modules/settings/repositories/settings_repositories.py`

**EXISTS:**
```python
class UserRepository:
    ✅ async def get_by_id(user_id) -> Optional[User]
    ✅ async def get_by_email(email) -> Optional[User]
    ✅ async def get_by_mobile(mobile_number) -> Optional[User]
    ✅ async def create(org_id, email, full_name, password_hash) -> User
    ✅ async def get_sub_users(parent_user_id) -> list[User]
    ✅ async def count_sub_users(parent_user_id) -> int
    ✅ async def create_sub_user(...) -> User
    ✅ async def disable_sub_user(sub_user_id) -> None
    ✅ async def enable_sub_user(sub_user_id) -> None
    ✅ async def enable_2fa(user_id, pin_hash) -> None
    ✅ async def disable_2fa(user_id) -> None
```

**MISSING:**
```python
❌ async def list_internal_users(skip, limit, filters) -> list[User]
❌ async def count_internal_users(filters) -> int
❌ async def update_user(user_id, **updates) -> User
❌ async def delete_user(user_id) -> None  # Soft delete preferred
❌ async def update_modules(user_id, modules) -> User
❌ async def search_users(query) -> list[User]
```

**Assessment:**
- ✅ Basic CRUD exists for user creation and retrieval
- ❌ No list/pagination methods for admin UI
- ❌ No update method for editing existing users
- ❌ No delete/deactivate method beyond sub-users
- ❌ No search/filter capabilities

---

### 1.3 Service Layer ⚠️ INCOMPLETE
**File:** `backend/modules/settings/services/settings_services.py`

**EXISTS:**
```python
class AuthService:
    ✅ async def signup(email, password, full_name) -> User
    ✅ async def login(email, password) -> tuple[tokens]
        - Enforces INTERNAL/SUPER_ADMIN only
        - EXTERNAL users rejected with proper error
    ✅ async def login_with_lockout(email, password, lockout_service)
    ✅ async def login_with_otp(mobile_number) -> tuple[tokens]  # EXTERNAL only
    ✅ async def refresh(refresh_token) -> tuple[tokens]
    ✅ async def logout(refresh_token) -> None
    ✅ async def logout_all_devices(user_id) -> int
    ✅ async def create_sub_user(...) -> User  # EXTERNAL users only
    ✅ async def get_sub_users(parent_user_id) -> list[User]
    ✅ async def delete_sub_user(parent_id, sub_user_id)
    ✅ async def disable_sub_user(parent_id, sub_user_id) -> User
    ✅ async def enable_sub_user(parent_id, sub_user_id) -> User
    ✅ async def setup_2fa(user_id, pin) -> None
    ✅ async def verify_pin(email, pin) -> tuple[tokens]
    ✅ async def disable_2fa(user_id) -> None
```

**MISSING:**
```python
❌ async def list_internal_users(skip, limit, filters) -> tuple[users, total]
❌ async def get_user_by_id(user_id) -> User  # Admin access
❌ async def update_internal_user(user_id, updates) -> User
❌ async def deactivate_internal_user(user_id) -> User
❌ async def reactivate_internal_user(user_id) -> User
❌ async def update_user_modules(user_id, modules) -> User
❌ async def change_user_type(user_id, new_type) -> User  # SUPER_ADMIN only
❌ async def reset_user_password(user_id, new_password) -> None  # Admin reset
```

**Assessment:**
- ✅ Authentication flows complete and secure
- ✅ Login restrictions properly enforce user types
- ✅ Sub-user management exists (but for EXTERNAL users)
- ❌ No admin-level user management methods
- ❌ No methods for updating existing INTERNAL users
- ❌ No user listing/searching for admin dashboards

---

### 1.4 API Endpoints ⚠️ INCOMPLETE
**File:** `backend/modules/settings/router.py`

**EXISTS:**
```python
POST /api/v1/settings/auth/signup
    - Generic signup (deprecated for INTERNAL users)
    - Requires: AUTH_CREATE_ACCOUNT capability

POST /api/v1/settings/auth/signup-internal
    ✅ - INTERNAL user signup with password policy
    ✅ - Requires: AUTH_CREATE_ACCOUNT capability
    ✅ - Enforces password complexity

POST /api/v1/settings/auth/login
    ✅ - INTERNAL/SUPER_ADMIN only (email/password)
    ✅ - EXTERNAL users rejected
    ✅ - Returns JWT tokens or 2FA challenge
    ✅ - Requires: AUTH_LOGIN capability

POST /api/v1/settings/auth/logout
POST /api/v1/settings/auth/logout-all
POST /api/v1/settings/auth/refresh
POST /api/v1/settings/auth/change-password
    ✅ - INTERNAL users only
    ✅ - Revokes all sessions after change

GET /api/v1/settings/auth/me
    ✅ - Returns current user profile

# Sub-user endpoints (EXTERNAL users)
POST /api/v1/settings/auth/sub-users
GET /api/v1/settings/auth/sub-users
DELETE /api/v1/settings/auth/sub-users/{id}
POST /api/v1/settings/auth/sub-users/{id}/disable
POST /api/v1/settings/auth/sub-users/{id}/enable

# 2FA endpoints
POST /api/v1/settings/auth/2fa-setup
POST /api/v1/settings/auth/2fa-verify
POST /api/v1/settings/auth/2fa-disable

# OTP endpoints (EXTERNAL users)
POST /api/v1/settings/auth/send-otp
POST /api/v1/settings/auth/verify-otp
```

**MISSING - CRITICAL ADMIN ENDPOINTS:**
```python
❌ GET /api/v1/settings/users
    - List all INTERNAL users (paginated)
    - Filters: user_type, is_active, organization_id, search query
    - Requires: ADMIN_MANAGE_USERS capability
    - Returns: { users: User[], total: number }

❌ GET /api/v1/settings/users/{user_id}
    - Get single user details (admin access)
    - Requires: ADMIN_MANAGE_USERS capability
    - Returns: User object with full details

❌ POST /api/v1/settings/users
    - Create new INTERNAL user (admin operation)
    - Body: { email, full_name, password, user_type, allowed_modules }
    - Requires: ADMIN_MANAGE_USERS capability
    - Returns: Created user

❌ PUT /api/v1/settings/users/{user_id}
    - Update INTERNAL user details
    - Body: { full_name?, allowed_modules?, user_type? }
    - Requires: ADMIN_MANAGE_USERS capability
    - Returns: Updated user

❌ PATCH /api/v1/settings/users/{user_id}/status
    - Activate/deactivate user
    - Body: { is_active: boolean }
    - Requires: ADMIN_MANAGE_USERS capability
    - Returns: Updated user

❌ DELETE /api/v1/settings/users/{user_id}
    - Soft delete user (set is_active=False)
    - Requires: ADMIN_MANAGE_USERS capability
    - Returns: 204 No Content

❌ POST /api/v1/settings/users/{user_id}/reset-password
    - Admin password reset
    - Body: { new_password }
    - Requires: ADMIN_MANAGE_USERS capability
    - Sends email notification to user
```

**Assessment:**
- ✅ Authentication endpoints complete
- ✅ Password change for self-service works
- ✅ Capability-based authorization in place
- ❌ **NO ADMIN USER MANAGEMENT ENDPOINTS**
- ❌ Cannot list users from admin dashboard
- ❌ Cannot create users via admin UI
- ❌ Cannot edit existing users
- ❌ Cannot deactivate/delete users

---

### 1.5 Capabilities System ✅ COMPLETE
**Files:** 
- `backend/core/auth/capabilities/definitions.py`
- `backend/core/auth/capabilities/decorators.py`
- `backend/modules/capabilities/router.py`

**Relevant Capabilities:**
```python
class Capabilities(str, Enum):
    # User Management
    ADMIN_MANAGE_USERS = "admin.manage_users"  # Create/edit/delete users
    ADMIN_MANAGE_ROLES = "admin.manage_roles"  # Manage role assignments
    ORG_MANAGE_USERS = "org.manage_users"      # Org-scoped user management
    
    # Authentication
    AUTH_CREATE_ACCOUNT = "auth.create_account"
    AUTH_LOGIN = "auth.login"
```

**Decorator Implementation:**
```python
class RequireCapability:
    def __init__(self, required_capability: Capabilities):
        self.required_capability = required_capability
    
    async def __call__(
        self,
        request: Request,
        current_user = Depends(get_current_user)
    ) -> None:
        # SUPER_ADMIN bypass
        if current_user.user_type == "SUPER_ADMIN":
            return None
        
        # Check user capabilities
        user_capabilities = await capability_service.get_user_capabilities(current_user.id)
        if self.required_capability.value not in user_capabilities:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        
        return None
```

**Capability Router:**
```python
# Working endpoints
GET /api/v1/capabilities  # List all capabilities
GET /api/v1/capabilities/users/{user_id}  # Get user capabilities
POST /api/v1/capabilities/users/{user_id}/grant  # Grant capability
POST /api/v1/capabilities/users/{user_id}/revoke  # Revoke capability
GET /api/v1/capabilities/me  # Get my capabilities
```

**Assessment:**
- ✅ Complete capability-based authorization system
- ✅ SUPER_ADMIN bypass working correctly
- ✅ ADMIN_MANAGE_USERS capability defined
- ✅ Decorator properly enforces permissions
- ✅ Capability management UI exists (frontend)
- ⚠️ Need to apply ADMIN_MANAGE_USERS to new admin endpoints

---

## 2. Frontend Analysis

### 2.1 Existing Pages ⚠️ INCOMPLETE
**Location:** `frontend/src/pages/backoffice/`

**EXISTS:**
```
✅ DashboardPage.tsx          - Backoffice dashboard
✅ UserCapabilitiesPage.tsx   - Assign/revoke user capabilities
✅ CapabilitiesManagementPage.tsx  - View all capabilities
✅ RiskMonitoringPage.tsx     - Risk management
✅ ComplianceAuditPage.tsx    - Compliance tracking
✅ AccountsFinancePage.tsx    - Financial management
✅ ClearingSettlementPage.tsx - Settlement operations
```

**MISSING:**
```
❌ UserManagementPage.tsx     - CRITICAL: Main user CRUD interface
❌ UserListTable.tsx          - Table component for user listing
❌ UserFormModal.tsx          - Create/edit user modal
❌ UserDetailsDrawer.tsx      - View user details sidebar
```

**Assessment:**
- ✅ Backoffice structure exists
- ✅ Capabilities management UI complete (988 lines)
- ❌ **NO USER MANAGEMENT PAGE**
- ❌ Cannot view list of users
- ❌ Cannot create new users via UI
- ❌ Cannot edit existing users

---

### 2.2 API Service Layer ⚠️ INCOMPLETE
**File:** `frontend/src/services/api/usersService.ts`

**EXISTS:**
```typescript
const usersService = {
    ⚠️ getAllUsers(): Promise<UserWithCapabilities[]>
        // CURRENTLY MOCKED - Returns only current user
        // TODO comment exists: "Replace with actual admin endpoint"
    
    ❌ getUserById(userId: string): Promise<User>
        // Calls `/auth/users/${userId}` - ENDPOINT DOESN'T EXIST
    
    ❌ updateUserStatus(userId: string, isActive: boolean): Promise<User>
        // Calls PATCH `/auth/users/${userId}/status` - ENDPOINT DOESN'T EXIST
    
    ✅ getSubUsers(): Promise<User[]>
        // Works - calls /auth/sub-users (for EXTERNAL users)
}
```

**MISSING:**
```typescript
❌ createUser(userData: CreateUserRequest): Promise<User>
❌ updateUser(userId: string, updates: UpdateUserRequest): Promise<User>
❌ deleteUser(userId: string): Promise<void>
❌ searchUsers(query: string): Promise<User[]>
❌ resetUserPassword(userId: string, newPassword: string): Promise<void>
```

**Assessment:**
- ⚠️ Service file exists but methods are MOCKED or broken
- ❌ getAllUsers returns fake data - not functional
- ❌ getUserById calls non-existent endpoint
- ❌ updateUserStatus calls non-existent endpoint
- ❌ No create/update/delete methods
- ✅ Sub-user methods work (but wrong use case)

---

### 2.3 Type Definitions ✅ COMPLETE
**File:** `frontend/src/types/auth.ts`

```typescript
export interface User {
    id: string;
    email: string;
    full_name: string;
    user_type: 'SUPER_ADMIN' | 'INTERNAL' | 'EXTERNAL';
    capabilities: string[];
    is_active: boolean;
    organization_id?: string;
    parent_user_id?: string;
    role?: string;
    created_at: string;
    updated_at?: string;
}

export interface UserWithCapabilities extends User {
    capabilities_count: number;
    last_login?: string;
}
```

**Assessment:**
- ✅ Complete type definitions
- ✅ Matches backend User schema
- ✅ Properly typed for TypeScript safety

---

## 3. Gap Analysis

### 3.1 Missing Backend Components 🔴 CRITICAL

| Component | Status | Priority | Effort |
|-----------|--------|----------|--------|
| **UserRepository.list_internal_users()** | ❌ Missing | 🔴 Critical | 2 hours |
| **UserRepository.update_user()** | ❌ Missing | 🔴 Critical | 1 hour |
| **UserRepository.delete_user()** | ❌ Missing | 🟡 High | 1 hour |
| **AuthService.list_internal_users()** | ❌ Missing | 🔴 Critical | 2 hours |
| **AuthService.update_internal_user()** | ❌ Missing | 🔴 Critical | 2 hours |
| **AuthService.deactivate_user()** | ❌ Missing | 🟡 High | 1 hour |
| **GET /users endpoint** | ❌ Missing | 🔴 Critical | 3 hours |
| **POST /users endpoint** | ❌ Missing | 🔴 Critical | 2 hours |
| **PUT /users/{id} endpoint** | ❌ Missing | 🔴 Critical | 2 hours |
| **PATCH /users/{id}/status endpoint** | ❌ Missing | 🟡 High | 1 hour |
| **DELETE /users/{id} endpoint** | ❌ Missing | 🟡 High | 1 hour |
| **POST /users/{id}/reset-password** | ❌ Missing | 🟡 High | 2 hours |

**Total Backend Effort:** ~20 hours

---

### 3.2 Missing Frontend Components 🔴 CRITICAL

| Component | Status | Priority | Effort |
|-----------|--------|----------|--------|
| **UserManagementPage.tsx** | ❌ Missing | 🔴 Critical | 6 hours |
| **UserListTable component** | ❌ Missing | 🔴 Critical | 4 hours |
| **UserFormModal component** | ❌ Missing | 🔴 Critical | 4 hours |
| **UserDetailsDrawer component** | ❌ Missing | 🟡 High | 3 hours |
| **usersService.createUser()** | ❌ Missing | 🔴 Critical | 1 hour |
| **usersService.updateUser()** | ❌ Missing | 🔴 Critical | 1 hour |
| **usersService.deleteUser()** | ❌ Missing | 🔴 Critical | 1 hour |
| **usersService.getAllUsers() fix** | ⚠️ Mocked | 🔴 Critical | 0.5 hours |
| **Form validation schemas** | ❌ Missing | 🟡 High | 2 hours |
| **Search/filter UI** | ❌ Missing | 🟡 High | 3 hours |
| **Pagination component** | ❌ Missing | 🟡 High | 2 hours |
| **Module assignment UI** | ❌ Missing | 🟡 High | 3 hours |

**Total Frontend Effort:** ~30.5 hours

---

## 4. Security & Authorization Review

### 4.1 Current Security Posture ✅ GOOD

**Strengths:**
- ✅ **User type isolation:** INTERNAL/EXTERNAL properly separated at login
- ✅ **Password policy:** Enforced for INTERNAL users via signup-internal
- ✅ **Capability-based auth:** ADMIN_MANAGE_USERS capability exists and enforced
- ✅ **SUPER_ADMIN bypass:** Works correctly in decorator
- ✅ **JWT tokens:** Secure token generation with expiry
- ✅ **2FA support:** PIN-based 2FA implemented
- ✅ **Account lockout:** Rate limiting and lockout service exists
- ✅ **Audit logging:** `audit_log()` calls present

**Weaknesses:**
- ⚠️ No endpoints to audit, but authorization pattern is correct
- ⚠️ Need to ensure new admin endpoints use `RequireCapability(Capabilities.ADMIN_MANAGE_USERS)`
- ⚠️ Should add rate limiting to user list endpoint (prevent abuse)

---

### 4.2 Required Security Measures for New Endpoints

```python
# All new admin user endpoints MUST have:
@router.get("/users")
async def list_users(
    ...
    _check: None = Depends(RequireCapability(Capabilities.ADMIN_MANAGE_USERS)),
):
    # SUPER_ADMIN or users with ADMIN_MANAGE_USERS capability
    ...

# Password reset should notify user
@router.post("/users/{user_id}/reset-password")
async def reset_password(
    ...
    _check: None = Depends(RequireCapability(Capabilities.ADMIN_MANAGE_USERS)),
):
    # 1. Reset password
    # 2. Revoke all sessions
    # 3. Send email notification to user
    # 4. Audit log the action
    ...
```

---

## 5. Recommendations & Implementation Plan

### Phase 1: Backend Foundation (Day 1-2, ~20 hours)

#### 1.1 Repository Layer
```python
# backend/modules/settings/repositories/settings_repositories.py

class UserRepository(BaseRepo):
    async def list_users(
        self,
        skip: int = 0,
        limit: int = 100,
        user_type: Optional[str] = None,
        is_active: Optional[bool] = None,
        organization_id: Optional[UUID] = None,
        search_query: Optional[str] = None
    ) -> tuple[list[User], int]:
        """
        List users with pagination and filters.
        For INTERNAL user management only.
        """
        query = select(User)
        
        # Filter by user type (default to INTERNAL and SUPER_ADMIN)
        if user_type:
            query = query.where(User.user_type == user_type)
        else:
            query = query.where(User.user_type.in_(['INTERNAL', 'SUPER_ADMIN']))
        
        # Other filters...
        if is_active is not None:
            query = query.where(User.is_active == is_active)
        
        if organization_id:
            query = query.where(User.organization_id == organization_id)
        
        if search_query:
            search = f"%{search_query}%"
            query = query.where(
                or_(
                    User.email.ilike(search),
                    User.full_name.ilike(search)
                )
            )
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total_result = await self.db.execute(count_query)
        total = total_result.scalar_one()
        
        # Get paginated results
        query = query.offset(skip).limit(limit).order_by(User.created_at.desc())
        result = await self.db.execute(query)
        users = list(result.scalars().all())
        
        return users, total
    
    async def update_user(
        self,
        user_id: UUID,
        **updates
    ) -> User:
        """
        Update user fields.
        Allowed updates: full_name, allowed_modules, user_type (SUPER_ADMIN only)
        """
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Apply updates
        for key, value in updates.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def soft_delete_user(self, user_id: UUID) -> None:
        """
        Soft delete user by setting is_active = False.
        Better than hard delete for audit trail.
        """
        user = await self.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        user.is_active = False
        self.db.add(user)
        await self.db.flush()
```

#### 1.2 Service Layer
```python
# backend/modules/settings/services/settings_services.py

class UserManagementService:
    """
    New service dedicated to admin-level user management.
    Separate from AuthService (which handles authentication).
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.hasher = PasswordHasher()
    
    async def list_internal_users(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: dict = None
    ) -> tuple[list[User], int]:
        """
        List INTERNAL users for admin dashboard.
        Filters: user_type, is_active, organization_id, search_query
        """
        filters = filters or {}
        return await self.user_repo.list_users(
            skip=skip,
            limit=limit,
            **filters
        )
    
    async def get_user_by_id(self, user_id: UUID) -> User:
        """
        Get user details for admin view.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return user
    
    async def create_internal_user(
        self,
        email: str,
        password: str,
        full_name: str,
        user_type: str = 'INTERNAL',
        organization_id: Optional[UUID] = None,
        allowed_modules: Optional[list[str]] = None
    ) -> User:
        """
        Admin creation of INTERNAL user.
        Enforces password policy.
        """
        # Check if user exists
        existing = await self.user_repo.get_by_email(email)
        if existing:
            raise ValueError("User with this email already exists")
        
        # Validate user_type
        if user_type not in ['INTERNAL', 'SUPER_ADMIN']:
            raise ValueError("Can only create INTERNAL or SUPER_ADMIN users")
        
        # INTERNAL users must have organization_id
        if user_type == 'INTERNAL' and not organization_id:
            raise ValueError("INTERNAL users must have organization_id")
        
        # Hash password
        password_hash = self.hasher.hash(password)
        
        # Create user
        user = User(
            id=uuid4(),
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            user_type=user_type,
            organization_id=organization_id,
            allowed_modules=allowed_modules,
            is_active=True,
            is_verified=True  # Admin-created users are pre-verified
        )
        
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        
        return user
    
    async def update_internal_user(
        self,
        user_id: UUID,
        updates: dict
    ) -> User:
        """
        Update INTERNAL user details.
        Allowed: full_name, allowed_modules, organization_id
        """
        # Validate user exists and is INTERNAL
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if user.user_type not in ['INTERNAL', 'SUPER_ADMIN']:
            raise ValueError("Can only update INTERNAL users")
        
        # Filter allowed updates
        allowed_fields = ['full_name', 'allowed_modules', 'organization_id']
        filtered_updates = {
            k: v for k, v in updates.items() 
            if k in allowed_fields
        }
        
        # Update
        updated_user = await self.user_repo.update_user(user_id, **filtered_updates)
        return updated_user
    
    async def deactivate_user(self, user_id: UUID) -> User:
        """
        Deactivate user (soft delete).
        Also revokes all sessions.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        # Deactivate
        user.is_active = False
        self.db.add(user)
        
        # Revoke all refresh tokens
        from backend.modules.settings.models.settings_models import RefreshToken
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False
            )
        )
        tokens = result.scalars().all()
        for token in tokens:
            token.revoked = True
            self.db.add(token)
        
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def reactivate_user(self, user_id: UUID) -> User:
        """
        Reactivate previously deactivated user.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        user.is_active = True
        self.db.add(user)
        await self.db.flush()
        await self.db.refresh(user)
        return user
    
    async def reset_user_password(
        self,
        user_id: UUID,
        new_password: str,
        admin_user_id: UUID
    ) -> None:
        """
        Admin password reset.
        Revokes all sessions and should trigger email notification.
        """
        user = await self.user_repo.get_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        
        if user.user_type not in ['INTERNAL', 'SUPER_ADMIN']:
            raise ValueError("Can only reset password for INTERNAL users")
        
        # Hash new password
        user.password_hash = self.hasher.hash(new_password)
        self.db.add(user)
        
        # Revoke all sessions
        from backend.modules.settings.models.settings_models import RefreshToken
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False
            )
        )
        tokens = result.scalars().all()
        for token in tokens:
            token.revoked = True
            self.db.add(token)
        
        await self.db.flush()
        
        # TODO: Send email notification to user
        # email_service.send_password_reset_notification(user.email)
```

#### 1.3 API Router
```python
# backend/modules/settings/router.py

# Add to existing router

@router.get("/users", response_model=UserListResponse, tags=["admin", "users"])
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    user_type: Optional[str] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _check: None = Depends(RequireCapability(Capabilities.ADMIN_MANAGE_USERS)),
) -> UserListResponse:
    """
    List INTERNAL users (admin only).
    Requires ADMIN_MANAGE_USERS capability.
    """
    from backend.modules.settings.services.user_management_service import UserManagementService
    
    service = UserManagementService(db)
    
    filters = {}
    if user_type:
        filters['user_type'] = user_type
    if is_active is not None:
        filters['is_active'] = is_active
    if search:
        filters['search_query'] = search
    
    # Apply organization filter for INTERNAL users
    if current_user.user_type == 'INTERNAL':
        filters['organization_id'] = current_user.organization_id
    
    users, total = await service.list_internal_users(skip, limit, filters)
    
    audit_log("users.list", str(current_user.id), "admin", None, {"filters": filters})
    
    return UserListResponse(
        users=[UserOut.model_validate(u) for u in users],
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/users/{user_id}", response_model=UserOut, tags=["admin", "users"])
async def get_user(
    user_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _check: None = Depends(RequireCapability(Capabilities.ADMIN_MANAGE_USERS)),
) -> UserOut:
    """
    Get user details (admin only).
    Requires ADMIN_MANAGE_USERS capability.
    """
    from backend.modules.settings.services.user_management_service import UserManagementService
    from uuid import UUID
    
    service = UserManagementService(db)
    
    try:
        user = await service.get_user_by_id(UUID(user_id))
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    # INTERNAL users can only view users in their org
    if current_user.user_type == 'INTERNAL':
        if user.organization_id != current_user.organization_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return UserOut.model_validate(user)


@router.post("/users", response_model=UserOut, status_code=201, tags=["admin", "users"])
async def create_user(
    payload: CreateInternalUserRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _check: None = Depends(RequireCapability(Capabilities.ADMIN_MANAGE_USERS)),
) -> UserOut:
    """
    Create new INTERNAL user (admin only).
    Requires ADMIN_MANAGE_USERS capability.
    """
    from backend.modules.settings.services.user_management_service import UserManagementService
    
    service = UserManagementService(db)
    
    # INTERNAL users can only create users in their org
    org_id = payload.organization_id
    if current_user.user_type == 'INTERNAL':
        org_id = current_user.organization_id
    
    try:
        user = await service.create_internal_user(
            email=payload.email,
            password=payload.password,
            full_name=payload.full_name,
            user_type=payload.user_type or 'INTERNAL',
            organization_id=org_id,
            allowed_modules=payload.allowed_modules
        )
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    audit_log("user.created", str(current_user.id), "user", str(user.id), {"email": user.email})
    
    return UserOut.model_validate(user)


@router.put("/users/{user_id}", response_model=UserOut, tags=["admin", "users"])
async def update_user(
    user_id: str,
    payload: UpdateInternalUserRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _check: None = Depends(RequireCapability(Capabilities.ADMIN_MANAGE_USERS)),
) -> UserOut:
    """
    Update INTERNAL user (admin only).
    Requires ADMIN_MANAGE_USERS capability.
    """
    from backend.modules.settings.services.user_management_service import UserManagementService
    from uuid import UUID
    
    service = UserManagementService(db)
    
    try:
        # Check access
        existing_user = await service.get_user_by_id(UUID(user_id))
        if current_user.user_type == 'INTERNAL':
            if existing_user.organization_id != current_user.organization_id:
                raise HTTPException(status_code=403, detail="Access denied")
        
        # Update
        updates = payload.model_dump(exclude_unset=True)
        user = await service.update_internal_user(UUID(user_id), updates)
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    audit_log("user.updated", str(current_user.id), "user", user_id, updates)
    
    return UserOut.model_validate(user)


@router.patch("/users/{user_id}/status", response_model=UserOut, tags=["admin", "users"])
async def update_user_status(
    user_id: str,
    payload: UpdateUserStatusRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _check: None = Depends(RequireCapability(Capabilities.ADMIN_MANAGE_USERS)),
) -> UserOut:
    """
    Activate/deactivate user (admin only).
    Requires ADMIN_MANAGE_USERS capability.
    """
    from backend.modules.settings.services.user_management_service import UserManagementService
    from uuid import UUID
    
    service = UserManagementService(db)
    
    try:
        if payload.is_active:
            user = await service.reactivate_user(UUID(user_id))
        else:
            user = await service.deactivate_user(UUID(user_id))
        
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    action = "activated" if payload.is_active else "deactivated"
    audit_log(f"user.{action}", str(current_user.id), "user", user_id, {})
    
    return UserOut.model_validate(user)


@router.post("/users/{user_id}/reset-password", tags=["admin", "users"])
async def admin_reset_password(
    user_id: str,
    payload: AdminPasswordResetRequest,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    _check: None = Depends(RequireCapability(Capabilities.ADMIN_MANAGE_USERS)),
) -> dict:
    """
    Admin password reset (admin only).
    Revokes all user sessions.
    Requires ADMIN_MANAGE_USERS capability.
    """
    from backend.modules.settings.services.user_management_service import UserManagementService
    from uuid import UUID
    
    service = UserManagementService(db)
    
    try:
        await service.reset_user_password(
            UUID(user_id),
            payload.new_password,
            current_user.id
        )
        await db.commit()
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    audit_log("user.password_reset_admin", str(current_user.id), "user", user_id, {})
    
    return {
        "message": "Password reset successfully. All user sessions revoked.",
        "user_id": user_id
    }
```

#### 1.4 Schemas
```python
# backend/modules/settings/schemas/settings_schemas.py

class UserListResponse(BaseModel):
    """Response for user list endpoint."""
    users: list[UserOut]
    total: int
    skip: int
    limit: int


class CreateInternalUserRequest(BaseModel):
    """Request to create INTERNAL user (admin operation)."""
    email: str = Field(..., pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
    password: str = Field(..., min_length=8)
    full_name: str = Field(..., min_length=1)
    user_type: Optional[str] = Field('INTERNAL', pattern="^(INTERNAL|SUPER_ADMIN)$")
    organization_id: Optional[str] = None  # UUID as string
    allowed_modules: Optional[list[str]] = None


class UpdateInternalUserRequest(BaseModel):
    """Request to update INTERNAL user."""
    full_name: Optional[str] = None
    allowed_modules: Optional[list[str]] = None
    organization_id: Optional[str] = None  # UUID as string


class UpdateUserStatusRequest(BaseModel):
    """Request to activate/deactivate user."""
    is_active: bool


class AdminPasswordResetRequest(BaseModel):
    """Request for admin password reset."""
    new_password: str = Field(..., min_length=8)
```

---

### Phase 2: Frontend UI (Day 3-5, ~30.5 hours)

#### 2.1 Main User Management Page
```typescript
// frontend/src/pages/backoffice/UserManagementPage.tsx

import { useState, useEffect } from 'react';
import { 
  UserGroupIcon, 
  MagnifyingGlassIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  CheckCircleIcon,
  XCircleIcon,
  KeyIcon,
} from '@heroicons/react/24/outline';
import usersService from '@/services/api/usersService';
import type { User } from '@/types/auth';

export function UserManagementPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterType, setFilterType] = useState<string>('all');
  const [filterStatus, setFilterStatus] = useState<boolean | null>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [pagination, setPagination] = useState({ skip: 0, limit: 50, total: 0 });

  useEffect(() => {
    loadUsers();
  }, [searchQuery, filterType, filterStatus, pagination.skip]);

  const loadUsers = async () => {
    try {
      setLoading(true);
      const response = await usersService.listUsers({
        skip: pagination.skip,
        limit: pagination.limit,
        userType: filterType === 'all' ? undefined : filterType,
        isActive: filterStatus,
        search: searchQuery || undefined,
      });
      setUsers(response.users);
      setPagination(prev => ({ ...prev, total: response.total }));
    } catch (error) {
      console.error('Failed to load users:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = () => {
    setShowCreateModal(true);
  };

  const handleEditUser = (user: User) => {
    setSelectedUser(user);
    setShowEditModal(true);
  };

  const handleDeactivateUser = async (userId: string) => {
    if (!confirm('Are you sure you want to deactivate this user?')) return;
    
    try {
      await usersService.updateUserStatus(userId, false);
      await loadUsers();
    } catch (error) {
      console.error('Failed to deactivate user:', error);
    }
  };

  const handleResetPassword = async (userId: string) => {
    const newPassword = prompt('Enter new temporary password (min 8 characters):');
    if (!newPassword || newPassword.length < 8) {
      alert('Password must be at least 8 characters');
      return;
    }

    try {
      await usersService.resetUserPassword(userId, newPassword);
      alert('Password reset successfully. User will need to login with new password.');
    } catch (error) {
      console.error('Failed to reset password:', error);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-space-50 to-saturn-50 p-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-heading font-bold text-space-900 mb-2">
          User Management
        </h1>
        <p className="text-space-600">
          Manage internal backoffice users, permissions, and access control
        </p>
      </div>

      {/* Controls */}
      <div className="bg-white/80 backdrop-blur-sm border-2 border-space-200/30 rounded-2xl p-6 mb-6">
        <div className="flex items-center gap-4">
          {/* Search */}
          <div className="relative flex-1">
            <MagnifyingGlassIcon className="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-saturn-400" />
            <input
              type="text"
              placeholder="Search users by name or email..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-12 pr-4 py-3 border-2 border-space-200/30 rounded-xl focus:ring-2 focus:ring-saturn-500/50 focus:border-saturn-500"
            />
          </div>

          {/* Filters */}
          <select
            value={filterType}
            onChange={(e) => setFilterType(e.target.value)}
            className="px-4 py-3 border-2 border-space-200/30 rounded-xl focus:ring-2 focus:ring-saturn-500/50"
          >
            <option value="all">All Users</option>
            <option value="SUPER_ADMIN">Super Admin</option>
            <option value="INTERNAL">Internal</option>
          </select>

          <select
            value={filterStatus === null ? 'all' : filterStatus ? 'active' : 'inactive'}
            onChange={(e) => setFilterStatus(
              e.target.value === 'all' ? null : e.target.value === 'active'
            )}
            className="px-4 py-3 border-2 border-space-200/30 rounded-xl focus:ring-2 focus:ring-saturn-500/50"
          >
            <option value="all">All Status</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>

          {/* Create Button */}
          <button
            onClick={handleCreateUser}
            className="flex items-center gap-2 px-6 py-3 bg-saturn-500 text-white rounded-xl hover:bg-saturn-600 transition-colors"
          >
            <PlusIcon className="w-5 h-5" />
            Create User
          </button>
        </div>
      </div>

      {/* User Table */}
      <div className="bg-white/80 backdrop-blur-sm border-2 border-space-200/30 rounded-2xl overflow-hidden">
        {loading ? (
          <div className="p-12 text-center text-space-600">
            Loading users...
          </div>
        ) : users.length === 0 ? (
          <div className="p-12 text-center text-space-600">
            No users found
          </div>
        ) : (
          <table className="w-full">
            <thead className="bg-space-100/50">
              <tr>
                <th className="px-6 py-4 text-left text-sm font-heading font-bold text-space-900">
                  User
                </th>
                <th className="px-6 py-4 text-left text-sm font-heading font-bold text-space-900">
                  Type
                </th>
                <th className="px-6 py-4 text-left text-sm font-heading font-bold text-space-900">
                  Modules
                </th>
                <th className="px-6 py-4 text-left text-sm font-heading font-bold text-space-900">
                  Status
                </th>
                <th className="px-6 py-4 text-left text-sm font-heading font-bold text-space-900">
                  Created
                </th>
                <th className="px-6 py-4 text-right text-sm font-heading font-bold text-space-900">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-space-200/30">
              {users.map((user) => (
                <tr key={user.id} className="hover:bg-space-50/50 transition-colors">
                  <td className="px-6 py-4">
                    <div>
                      <div className="font-medium text-space-900">{user.full_name}</div>
                      <div className="text-sm text-space-600">{user.email}</div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      user.user_type === 'SUPER_ADMIN' 
                        ? 'bg-purple-100 text-purple-800'
                        : 'bg-blue-100 text-blue-800'
                    }`}>
                      {user.user_type}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    <div className="text-sm text-space-600">
                      {user.user_type === 'SUPER_ADMIN' ? (
                        <span className="text-purple-600 font-medium">All Modules</span>
                      ) : user.allowed_modules && user.allowed_modules.length > 0 ? (
                        <span>{user.allowed_modules.length} modules</span>
                      ) : (
                        <span className="text-red-600">No access</span>
                      )}
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    {user.is_active ? (
                      <span className="inline-flex items-center gap-1 text-green-600">
                        <CheckCircleIcon className="w-4 h-4" />
                        Active
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1 text-red-600">
                        <XCircleIcon className="w-4 h-4" />
                        Inactive
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-space-600">
                    {new Date(user.created_at).toLocaleDateString()}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={() => handleEditUser(user)}
                        className="p-2 text-blue-600 hover:bg-blue-50 rounded-lg transition-colors"
                        title="Edit User"
                      >
                        <PencilIcon className="w-5 h-5" />
                      </button>
                      <button
                        onClick={() => handleResetPassword(user.id)}
                        className="p-2 text-amber-600 hover:bg-amber-50 rounded-lg transition-colors"
                        title="Reset Password"
                      >
                        <KeyIcon className="w-5 h-5" />
                      </button>
                      {user.is_active && (
                        <button
                          onClick={() => handleDeactivateUser(user.id)}
                          className="p-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                          title="Deactivate User"
                        >
                          <TrashIcon className="w-5 h-5" />
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}

        {/* Pagination */}
        {pagination.total > pagination.limit && (
          <div className="border-t border-space-200/30 p-4 flex items-center justify-between">
            <div className="text-sm text-space-600">
              Showing {pagination.skip + 1} to {Math.min(pagination.skip + pagination.limit, pagination.total)} of {pagination.total} users
            </div>
            <div className="flex items-center gap-2">
              <button
                disabled={pagination.skip === 0}
                onClick={() => setPagination(prev => ({ ...prev, skip: Math.max(0, prev.skip - prev.limit) }))}
                className="px-4 py-2 border border-space-200 rounded-lg hover:bg-space-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                disabled={pagination.skip + pagination.limit >= pagination.total}
                onClick={() => setPagination(prev => ({ ...prev, skip: prev.skip + prev.limit }))}
                className="px-4 py-2 border border-space-200 rounded-lg hover:bg-space-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Modals */}
      {showCreateModal && (
        <UserFormModal
          mode="create"
          onClose={() => setShowCreateModal(false)}
          onSuccess={() => {
            setShowCreateModal(false);
            loadUsers();
          }}
        />
      )}

      {showEditModal && selectedUser && (
        <UserFormModal
          mode="edit"
          user={selectedUser}
          onClose={() => {
            setShowEditModal(false);
            setSelectedUser(null);
          }}
          onSuccess={() => {
            setShowEditModal(false);
            setSelectedUser(null);
            loadUsers();
          }}
        />
      )}
    </div>
  );
}

export default UserManagementPage;
```

#### 2.2 User Form Modal Component
(Implementation continues with UserFormModal.tsx, usersService updates, etc.)

---

### Phase 3: Testing & Deployment (Day 6, ~8 hours)

1. **Unit Tests** - Repository, service, endpoint tests
2. **Integration Tests** - Full CRUD flow tests
3. **Frontend Tests** - Component and E2E tests
4. **Security Audit** - Verify capabilities, rate limiting
5. **Documentation** - API docs, user guide
6. **Deployment** - Deploy to staging → testing → production

---

## 6. Risk Assessment

### High Risk Items 🔴
1. **No user management UI** - Admins cannot manage users without direct DB access
2. **No user listing endpoint** - Frontend cannot display users
3. **No user update endpoint** - Cannot modify existing users
4. **Mocked frontend services** - User service returns fake data

### Medium Risk Items 🟡
1. **No password reset functionality** - Admins cannot help locked-out users
2. **No user deactivation UI** - Manual DB updates required
3. **No audit trail for user changes** - Limited accountability

### Low Risk Items 🟢
1. **Authentication working** - Login/signup functional
2. **Capabilities system working** - Authorization in place
3. **Data models complete** - Schema supports all requirements

---

## 7. Conclusion

### Summary
The internal user management system has **strong foundations** but is **40% incomplete**. The authentication layer, data models, and capabilities system are production-ready, but critical CRUD operations and admin UI are entirely missing.

### Immediate Actions Required
1. ✅ **Branch created:** `audit/internal-user-management`
2. 🔴 **Implement backend endpoints** (Day 1-2)
3. 🔴 **Build admin UI pages** (Day 3-5)
4. 🟡 **Add testing & deployment** (Day 6)

### Total Effort Estimate
- **Backend:** ~20 hours
- **Frontend:** ~30.5 hours
- **Testing/Deployment:** ~8 hours
- **Total:** ~58.5 hours (~7-8 working days)

### Success Criteria
- ✅ Admins can list all INTERNAL users
- ✅ Admins can create new users via UI
- ✅ Admins can edit user details
- ✅ Admins can activate/deactivate users
- ✅ Admins can reset user passwords
- ✅ All operations require ADMIN_MANAGE_USERS capability
- ✅ SUPER_ADMIN has unrestricted access
- ✅ INTERNAL admins are org-scoped
- ✅ Full audit logging for all operations

---

**Next Steps:** Review this plan and confirm priority before implementation begins.
