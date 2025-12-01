# 🔥 CRITICAL FIXES - AVAILABILITY & REQUIREMENT ENGINES

**Branch:** `fix/availability-requirement-critical-fixes`  
**Date:** December 1, 2025  
**Status:** AUDIT COMPLETE → READY FOR IMPLEMENTATION

---

## 📋 ISSUES IDENTIFIED

### **ISSUE #1: Role-Based Auth Instead of Capability-Based** ❌

**Current State:**
- Using `get_seller_id_from_user()` and `get_buyer_id_from_user()` helper functions
- Hardcoded role extraction from user context
- No capability checks in routes

**Expected State:**
- Use `@RequireCapability` decorator for all endpoints
- Check capabilities like `AVAILABILITY_CREATE`, `REQUIREMENT_CREATE`
- Remove role-based helpers

**Files Affected:**
- `backend/modules/trade_desk/routes/availability_routes.py`
- `backend/modules/trade_desk/routes/requirement_routes.py`

**Fix:**
```python
# BEFORE (WRONG):
def get_seller_id_from_user(user) -> UUID:
    if user.user_type == "EXTERNAL" and user.business_partner_id:
        return user.business_partner_id
    ...

@router.post("")
async def create_availability(
    request: AvailabilityCreateRequest,
    current_user=Depends(get_current_user),
    ...
):
    seller_id = get_seller_id_from_user(current_user)  # ❌

# AFTER (CORRECT):
@router.post("")
@RequireCapability(Capabilities.AVAILABILITY_CREATE)
async def create_availability(
    request: AvailabilityCreateRequest,
    current_user=Depends(get_current_user),
    ...
):
    seller_id = current_user.business_partner_id  # ✅
```

---

### **ISSUE #2: No EOD Square-Off for Availabilities** ❌

**Current State:**
- Availabilities stay ACTIVE indefinitely until manually marked SOLD/CANCELLED
- No automatic EOD cleanup

**Expected State:**
- All ACTIVE/AVAILABLE positions must square off at EOD (End of Day)
- Timezone-aware EOD calculation (global system, multiple timezones)
- Seller can re-post next day if needed

**Solution:**
1. Add `eod_cutoff` timestamp to Availability model
2. Create cron job to expire availabilities at their timezone's EOD
3. Status transition: ACTIVE → EXPIRED (automatic)

**Implementation:**
```python
# In Availability model:
eod_cutoff = Column(
    TIMESTAMP(timezone=True),
    nullable=False,
    comment='End-of-day cutoff based on location timezone'
)

# Cron job (runs every hour):
async def expire_availabilities_eod():
    """
    Expire availabilities past their EOD cutoff.
    Timezone-aware: Uses location's timezone for EOD calculation.
    """
    now = datetime.now(timezone.utc)
    
    # Find expired availabilities
    expired = await db.execute(
        select(Availability)
        .where(
            Availability.status.in_(['ACTIVE', 'AVAILABLE']),
            Availability.eod_cutoff <= now
        )
    )
    
    for avail in expired.scalars():
        avail.status = AvailabilityStatus.EXPIRED
        # Emit event
        await emit_event('availability.expired', avail.id)
    
    await db.commit()
```

---

### **ISSUE #3: No EOD Square-Off for Requirements** ❌

**Current State:**
- Requirements stay ACTIVE until manually cancelled or fulfilled
- No automatic EOD cleanup

**Expected State:**
- Same as availabilities - must square off at EOD
- Buyer can re-post next day

**Solution:** Same as #2 but for Requirement model

---

### **ISSUE #4: Circular Trading Check is Full-Day, Not Intraday** ❌

**Current State:**
```python
# In risk_engine.py:
func.date(Availability.created_at) == trade_date  # ❌ Full day check
```
This blocks: "Buy at 9 AM, Sell at 3 PM same day" (legitimate day trading)

**Expected State:**
- Allow intraday buy/sell of same commodity
- Only block if CURRENTLY have OPEN position
- Check: Active positions RIGHT NOW, not "created today"

**Fix:**
```python
# BEFORE (blocks entire day):
query = select(Availability).where(
    and_(
        Availability.seller_id == partner_id,
        Availability.commodity_id == commodity_id,
        Availability.status.in_(['AVAILABLE', 'PARTIALLY_SOLD']),
        func.date(Availability.created_at) == trade_date  # ❌
    )
)

# AFTER (only blocks if currently open):
query = select(Availability).where(
    and_(
        Availability.seller_id == partner_id,
        Availability.commodity_id == commodity_id,
        Availability.status.in_(['ACTIVE', 'AVAILABLE', 'PARTIALLY_SOLD']),  # ✅ Currently open
        # No date filter - check if CURRENTLY open
    )
)

# Message: "You currently have OPEN SELL positions for this commodity. 
#          Close them first before creating BUY requirement."
```

---

### **ISSUE #5: Payment Terms Not Mandatory in Requirement** ❌

**Current State:**
```python
# In RequirementCreateRequest:
preferred_payment_terms: Optional[List[UUID]] = None  # ❌ Optional
preferred_delivery_terms: Optional[List[UUID]] = None  # ❌ Optional
```

**Expected State:**
- Buyer MUST specify payment terms
- Buyer MUST specify delivery/passing/weighment terms

**Fix:**
```python
# AFTER:
class RequirementCreateRequest(BaseModel):
    # ... existing fields ...
    
    # 🔥 MANDATORY TERMS
    payment_terms: List[UUID] = Field(
        ...,  # Required
        min_items=1,
        description="MANDATORY: Acceptable payment term IDs (LC, TT, DA, etc.)"
    )
    
    delivery_terms: List[UUID] = Field(
        ...,  # Required
        min_items=1,
        description="MANDATORY: Delivery/passing/weighment term IDs"
    )
    
    weighment_terms: List[UUID] = Field(
        ...,  # Required
        min_items=1,
        description="MANDATORY: Weighment term IDs (seller's scale, buyer's scale, third-party)"
    )
```

---

### **ISSUE #6: Budget Naming - Should be "Target Price"** ❌

**Current State:**
```python
max_budget_per_unit: Decimal = Field(...)  # ❌ Confusing name
preferred_price_per_unit: Optional[Decimal] = None  # ❌ Optional
```

**Expected State:**
- Rename `preferred_price_per_unit` → `target_price_per_unit` (clearer)
- Make it MANDATORY
- Remove `max_budget_per_unit` (or make it optional ceiling)

**Fix:**
```python
# AFTER:
class RequirementCreateRequest(BaseModel):
    # ... existing fields ...
    
    # 🔥 PRICING (Revised)
    target_price_per_unit: Decimal = Field(
        ...,  # MANDATORY
        gt=0,
        description="MANDATORY: Target/desired price per unit (buyer's offer price)"
    )
    
    max_budget_per_unit: Optional[Decimal] = Field(
        None,  # Optional ceiling
        gt=0,
        description="OPTIONAL: Maximum price willing to pay (if different from target)"
    )
```

---

### **ISSUE #7: Price Optional in Requirement (After Match)** ❌

**Current State:**
- Buyer must specify price upfront when creating requirement

**Expected State:**
- Buyer can create requirement WITHOUT price
- After match, seller can offer price OR buyer can offer price
- Negotiation can start from either side

**Solution:**
```python
# Make pricing optional
class RequirementCreateRequest(BaseModel):
    # ... existing fields ...
    
    # 🔥 PRICING (OPTIONAL - for negotiation)
    target_price_per_unit: Optional[Decimal] = Field(
        None,
        gt=0,
        description="OPTIONAL: Target price. If NULL, buyer wants seller to quote."
    )
    
    max_budget_per_unit: Optional[Decimal] = Field(
        None,
        gt=0,
        description="OPTIONAL: Maximum ceiling price"
    )
    
    price_discovery_mode: bool = Field(
        default=False,
        description="If True, buyer wants sellers to quote prices (no buyer price upfront)"
    )
```

---

### **ISSUE #8: Timezone Handling for Global System** ❌

**Current State:**
- No timezone awareness
- EOD uses server time (India)

**Expected State:**
- Each location has timezone
- EOD calculated per location's timezone
- Mumbai seller → 11:59 PM IST
- New York seller → 11:59 PM EST
- London seller → 11:59 PM GMT

**Implementation:**
```python
# In settings_locations table:
ALTER TABLE settings_locations ADD COLUMN timezone VARCHAR(50) DEFAULT 'Asia/Kolkata';

# EOD calculation:
def calculate_eod_cutoff(location_timezone: str) -> datetime:
    """
    Calculate EOD cutoff for given timezone.
    Always midnight (00:00) of NEXT day in that timezone.
    """
    tz = pytz.timezone(location_timezone)
    now_in_tz = datetime.now(tz)
    
    # Next midnight in that timezone
    next_midnight = (now_in_tz + timedelta(days=1)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    
    # Convert to UTC for storage
    return next_midnight.astimezone(pytz.UTC)
```

---

## ✅ IMPLEMENTATION PLAN

### **Phase 1: Database Changes** (30 mins)
1. Add `eod_cutoff` column to `availabilities` table
2. Add `eod_cutoff` column to `requirements` table
3. Add `timezone` column to `settings_locations` table
4. Add migration script

### **Phase 2: Model Updates** (30 mins)
1. Update `Availability` model with `eod_cutoff`
2. Update `Requirement` model with `eod_cutoff`
3. Add timezone handling in location model

### **Phase 3: Schema Changes** (45 mins)
1. Make `payment_terms`, `delivery_terms`, `weighment_terms` MANDATORY in `RequirementCreateRequest`
2. Rename `preferred_price_per_unit` → `target_price_per_unit`
3. Make pricing optional (support price discovery mode)

### **Phase 4: Service Layer Fixes** (1 hour)
1. Remove role-based helpers
2. Add capability checks
3. Update circular trading logic (check CURRENT open positions, not full day)
4. Add timezone-aware EOD calculation

### **Phase 5: Route Updates** (1 hour)
1. Add `@RequireCapability` decorators to all endpoints
2. Update availability routes
3. Update requirement routes

### **Phase 6: Cron Jobs** (45 mins)
1. Create `expire_availabilities_eod.py` job
2. Create `expire_requirements_eod.py` job
3. Schedule jobs (run every hour, check timezone-aware EOD)

### **Phase 7: Testing** (1 hour)
1. Test capability-based auth
2. Test EOD expiry (multiple timezones)
3. Test circular trading (intraday buy/sell allowed)
4. Test mandatory payment terms

---

## 📊 SUMMARY

**Total Issues:** 8 critical  
**Estimated Fix Time:** 5-6 hours  
**Files to Modify:** 12 files  
**Database Changes:** 3 columns added + 1 migration  

**Priority:**
1. 🔴 HIGH: Capability-based auth (#1)
2. 🔴 HIGH: EOD square-off (#2, #3)
3. 🟡 MEDIUM: Circular trading logic (#4)
4. 🟡 MEDIUM: Mandatory payment terms (#5)
5. 🟢 LOW: Naming/UX (#6, #7)
6. 🟢 LOW: Timezone (#8)

---

**Ready for implementation approval?**
