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

### **ISSUE #9: Buyer Preference Saving (Payment/Delivery/Weighment Terms)** ❌

**Current State:**
- Buyer selects terms every time creating requirement
- No option to save preferences

**Expected State:**
- System asks: "Save these terms as default preferences?"
- Buyer can save commonly used terms
- Auto-populate on next requirement creation

**Implementation:**
```python
# New table: buyer_preferences
CREATE TABLE buyer_preferences (
    id UUID PRIMARY KEY,
    buyer_partner_id UUID REFERENCES business_partners(id),
    
    # Default terms
    default_payment_terms JSONB,  # Array of term UUIDs
    default_delivery_terms JSONB,  # Array of term UUIDs
    default_weighment_terms JSONB,  # Array of term UUIDs
    
    # Quick-use presets
    preset_name VARCHAR(100),  # "Standard Purchase", "Urgent Buy", etc.
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(buyer_partner_id, preset_name)
);

# In RequirementCreateRequest:
class RequirementCreateRequest(BaseModel):
    # ... existing fields ...
    
    save_as_preference: bool = Field(
        default=False,
        description="Save these terms as default preference"
    )
    
    preference_preset_name: Optional[str] = Field(
        None,
        description="Name for this preference preset (e.g., 'Standard Purchase')"
    )
    
    load_from_preference: bool = Field(
        default=False,
        description="Load terms from saved preferences"
    )

# Service logic:
async def create_requirement(self, ...):
    # Load preferences if requested
    if request.load_from_preference:
        prefs = await self.get_buyer_preferences(buyer_id)
        if prefs:
            request.payment_terms = prefs.default_payment_terms
            request.delivery_terms = prefs.default_delivery_terms
            request.weighment_terms = prefs.default_weighment_terms
    
    # ... create requirement ...
    
    # Save preferences if requested
    if request.save_as_preference:
        await self.save_buyer_preferences(
            buyer_id=buyer_id,
            payment_terms=request.payment_terms,
            delivery_terms=request.delivery_terms,
            weighment_terms=request.weighment_terms,
            preset_name=request.preference_preset_name
        )
```

---

### **ISSUE #10: Commodity Parameter Validation Missing** ❌

**Current State:**
- Availability & Requirement accept ANY quality parameters in JSONB
- No validation against Commodity Master's CommodityParameter table
- min_value/max_value defined but not enforced

**Expected State:**
- Validate quality_params against commodity's registered parameters
- Enforce min/max ranges from CommodityParameter table
- Reject invalid parameters

**Implementation:**
```python
# In AvailabilityService.create_availability():
async def _validate_quality_parameters(
    self,
    commodity_id: UUID,
    quality_params: dict
) -> None:
    """
    Validate quality parameters against commodity master.
    
    Rules:
    1. Check if parameter is registered in CommodityParameter
    2. Validate min/max ranges
    3. Check mandatory parameters are present
    """
    # Get commodity's registered parameters
    registered_params = await self.db.execute(
        select(CommodityParameter)
        .where(CommodityParameter.commodity_id == commodity_id)
    )
    params_list = registered_params.scalars().all()
    
    # Build validation map
    param_map = {p.parameter_name: p for p in params_list}
    
    # Check each provided parameter
    for param_name, param_value in quality_params.items():
        if param_name not in param_map:
            raise ValueError(
                f"Parameter '{param_name}' is not registered for this commodity. "
                f"Registered parameters: {list(param_map.keys())}"
            )
        
        registered = param_map[param_name]
        
        # Validate NUMERIC type with min/max
        if registered.parameter_type == "NUMERIC":
            value = Decimal(str(param_value))
            
            if registered.min_value and value < registered.min_value:
                raise ValueError(
                    f"{param_name}: {value} is below minimum {registered.min_value}"
                )
            
            if registered.max_value and value > registered.max_value:
                raise ValueError(
                    f"{param_name}: {value} exceeds maximum {registered.max_value}"
                )
        
        # Validate RANGE type
        if registered.parameter_type == "RANGE":
            if not isinstance(param_value, dict) or 'min' not in param_value or 'max' not in param_value:
                raise ValueError(
                    f"{param_name}: RANGE type requires {{min: X, max: Y}} format"
                )
    
    # Check mandatory parameters are present
    mandatory_params = [p.parameter_name for p in params_list if p.is_mandatory]
    missing = set(mandatory_params) - set(quality_params.keys())
    
    if missing:
        raise ValueError(
            f"Missing mandatory parameters: {list(missing)}"
        )
```

---

### **ISSUE #11: Unit Conversion Not Validated** ❌

**Current State:**
- Availability/Requirement accept any quantity_unit
- No validation against commodity's base_unit/trade_unit
- Conversion happens but not validated upfront

**Expected State:**
- Validate quantity_unit is compatible with commodity's base_unit
- Auto-convert using unit_converter.py
- Reject incompatible units (e.g., KG for METER-based commodity)

**Implementation:**
```python
# In AvailabilityService.create_availability():
async def _validate_and_convert_units(
    self,
    commodity_id: UUID,
    quantity: Decimal,
    quantity_unit: str
) -> dict:
    """
    Validate unit compatibility and convert to base unit.
    
    Returns:
        {
            "quantity": original quantity,
            "quantity_unit": original unit,
            "quantity_in_base_unit": converted quantity,
            "base_unit": commodity's base unit,
            "conversion_factor": factor used
        }
    """
    # Get commodity
    commodity_result = await self.db.execute(
        select(Commodity).where(Commodity.id == commodity_id)
    )
    commodity = commodity_result.scalar_one_or_none()
    
    if not commodity:
        raise ValueError(f"Commodity {commodity_id} not found")
    
    # Get unit info from catalog
    from backend.modules.settings.commodities.unit_converter import UnitConverter
    from backend.modules.settings.commodities.unit_catalog import get_unit_info
    
    unit_info = get_unit_info(quantity_unit)
    if not unit_info:
        raise ValueError(
            f"Unknown unit: {quantity_unit}. "
            f"Please use standard units like BALE, KG, MT, CANDY, QUINTAL"
        )
    
    # Validate unit is compatible with commodity's base_unit
    if unit_info["base_unit"] != commodity.base_unit:
        raise ValueError(
            f"Unit '{quantity_unit}' (base: {unit_info['base_unit']}) is incompatible "
            f"with commodity's base unit '{commodity.base_unit}'. "
            f"Please use units based on {commodity.base_unit}."
        )
    
    # Convert to base unit
    quantity_in_base = UnitConverter.convert_to_base(
        quantity=quantity,
        from_unit=quantity_unit,
        base_unit=commodity.base_unit
    )
    
    return {
        "quantity": quantity,
        "quantity_unit": quantity_unit,
        "quantity_in_base_unit": quantity_in_base,
        "base_unit": commodity.base_unit,
        "conversion_factor": unit_info["conversion_factor"]
    }

# Call in create_availability():
unit_validation = await self._validate_and_convert_units(
    commodity_id=commodity_id,
    quantity=total_quantity,
    quantity_unit=quantity_unit
)

# Store in availability
availability.quantity_in_base_unit = unit_validation["quantity_in_base_unit"]
```

---

## 📊 SUMMARY (UPDATED)

**Total Issues:** 11 critical  
**Estimated Fix Time:** 7-8 hours  
**Files to Modify:** 16 files  
**Database Changes:** 4 columns added + 1 new table + 1 migration  

**Priority:**
1. 🔴 HIGH: Capability-based auth (#1)
2. 🔴 HIGH: EOD square-off (#2, #3, #8 - timezone)
3. 🔴 HIGH: Parameter validation (#10)
4. 🔴 HIGH: Unit conversion validation (#11)
5. 🟡 MEDIUM: Circular trading logic (#4)
6. 🟡 MEDIUM: Mandatory payment terms (#5)
7. 🟡 MEDIUM: Buyer preferences (#9)
8. 🟢 LOW: Naming/UX (#6, #7)

---

## ✅ FINAL IMPLEMENTATION CHECKLIST

### Phase 1: Database (1 hour)
- [ ] Add `eod_cutoff` to `availabilities` table
- [ ] Add `eod_cutoff` to `requirements` table
- [ ] Add `timezone` to `settings_locations` table
- [ ] Create `buyer_preferences` table
- [ ] Create migration script

### Phase 2: Models (1 hour)
- [ ] Update `Availability` model
- [ ] Update `Requirement` model
- [ ] Create `BuyerPreference` model
- [ ] Add timezone handling

### Phase 3: Validation Logic (2 hours)
- [ ] Add commodity parameter validation
- [ ] Add unit conversion validation
- [ ] Update circular trading logic (check CURRENT open positions)
- [ ] Add capability checks

### Phase 4: Schemas (1 hour)
- [ ] Make payment/delivery/weighment terms MANDATORY
- [ ] Add buyer preference fields
- [ ] Rename pricing fields
- [ ] Add validation schemas

### Phase 5: Services (2 hours)
- [ ] Remove role-based helpers
- [ ] Add parameter validation in AvailabilityService
- [ ] Add unit validation in AvailabilityService
- [ ] Add parameter validation in RequirementService
- [ ] Add unit validation in RequirementService
- [ ] Add buyer preference service methods
- [ ] Update timezone-aware EOD calculation

### Phase 6: Routes (1 hour)
- [ ] Add `@RequireCapability` to all endpoints
- [ ] Update availability routes
- [ ] Update requirement routes
- [ ] Add buyer preference endpoints

### Phase 7: Cron Jobs (30 mins)
- [ ] Create EOD expiry job for availabilities
- [ ] Create EOD expiry job for requirements
- [ ] Schedule jobs

### Phase 8: Testing (1 hour)
- [ ] Test capability-based auth
- [ ] Test parameter validation
- [ ] Test unit conversion validation
- [ ] Test buyer preferences
- [ ] Test EOD expiry
- [ ] Test circular trading

---

**🎯 READY FOR FINAL APPROVAL?**

Type **"APPROVED"** to begin implementation.
