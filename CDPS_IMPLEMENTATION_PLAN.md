# CAPABILITY-DRIVEN PARTNER SYSTEM (CDPS)
## Implementation Plan for Approval

**Date:** November 28, 2025  
**Status:** 🔴 AWAITING APPROVAL  
**Estimated Duration:** 8-10 working days  
**Files to Modify:** 21 files

---

## 🎯 EXECUTIVE SUMMARY

### What Changes
✅ **REMOVE** `partner_type` enum (seller/buyer/trader/importer/exporter)  
✅ **REMOVE** `trade_classification` enum (domestic/importer/exporter)  
✅ **ADD** Capability-based system with auto-detection  
✅ **ADD** Insider trading prevention (6 rules)  
✅ **KEEP** All service provider logic untouched  
✅ **KEEP** All KYC flows untouched  
✅ **KEEP** All back-office features untouched

### Architecture Impact
- **Zero Breaking Changes** to service providers (broker, transporter, controller, financer, shipping_agent, sub_broker)
- **Zero Breaking Changes** to KYC renewal, notifications, jobs
- **Zero Breaking Changes** to back-office filters, exports, dashboard
- **Data Migration** with 100% backward compatibility

---

## 📊 COMPLETE FILE INVENTORY

### Files to Modify (21 Total)

#### 🔵 Core Partner Module (9 files)
1. `backend/modules/partners/models.py` - Remove partner_type, add capabilities
2. `backend/modules/partners/enums.py` - Add BusinessEntityType, deprecate PartnerType
3. `backend/modules/partners/schemas.py` - Update all schemas
4. `backend/modules/partners/services.py` - Add CapabilityDetectionService
5. `backend/modules/partners/validators.py` - Add InsiderTradingValidator
6. `backend/modules/partners/router.py` - Update endpoints
7. `backend/modules/partners/repositories.py` - Update filters
8. `backend/modules/partners/notifications.py` - Update email templates
9. `backend/modules/partners/events.py` - Add capability events

#### 🟢 Trade Desk Module (4 files)
10. `backend/modules/trade_desk/services/availability_service.py` - Capability validation
11. `backend/modules/trade_desk/services/requirement_service.py` - Capability validation
12. `backend/modules/trade_desk/matching/validators.py` - Insider trading check
13. `backend/modules/trade_desk/schemas/__init__.py` - Remove partner_type

#### 🟡 Risk Module (2 files)
14. `backend/modules/risk/risk_engine.py` - Update validate_partner_role()
15. `backend/modules/risk/schemas.py` - Remove partner_type fields

#### 🟣 Settings Module (1 file)
16. `backend/modules/settings/business_partners/models.py` - Update model

#### 🟠 AI Module (3 files)
17. `backend/ai/assistants/partner_assistant/assistant.py` - Update logic
18. `backend/ai/assistants/partner_assistant/tools.py` - Split methods
19. `backend/ai/prompts/partner/prompts.py` - Update prompts

#### 🔴 Database (2 files)
20. `backend/db/migrations/versions/YYYYMMDD_add_capability_system.py` - New migration
21. `backend/modules/partners/tests/test_capabilities.py` - New test file

---

## 🏗️ IMPLEMENTATION PHASES

### **PHASE 1: Database Schema Changes** (2 days)

#### 1.1 Update Enums (`partners/enums.py`)

**Actions:**
- ✅ ADD `BusinessEntityType` enum
- ✅ ADD new document types: `IEC`, `FOREIGN_TAX_ID`, `FOREIGN_IMPORT_LICENSE`, `FOREIGN_EXPORT_LICENSE`
- ✅ DEPRECATE `PartnerType` enum (keep for migration reference)
- ✅ DELETE `TradeClassification` enum

**Code Changes:**
```python
# ADD
class BusinessEntityType(str, Enum):
    PROPRIETORSHIP = "proprietorship"
    PARTNERSHIP = "partnership"
    LLP = "llp"
    PRIVATE_LIMITED = "private_limited"
    PUBLIC_LIMITED = "public_limited"
    TRUST = "trust"
    SOCIETY = "society"
    LLC = "llc"
    CORPORATION = "corporation"
    FOREIGN_ENTITY = "foreign_entity"

# UPDATE DocumentType - ADD these
class DocumentType(str, Enum):
    # ... existing ...
    IEC = "iec"
    FOREIGN_TAX_ID = "foreign_tax_id"
    FOREIGN_IMPORT_LICENSE = "foreign_import_license"
    FOREIGN_EXPORT_LICENSE = "foreign_export_license"

# DELETE
# class TradeClassification(str, Enum): ...  ❌ DELETE ENTIRE ENUM
```

#### 1.2 Update Models (`partners/models.py`)

**BusinessPartner Model Changes:**

**DELETE columns:**
```python
partner_type = Column(String(20), ...)  # ❌ DELETE
trade_classification = Column(String(20), ...)  # ❌ DELETE
```

**ADD columns:**
```python
# Step 1: Service Provider or Business Entity
is_service_provider = Column(Boolean, default=False, nullable=False, index=True)
service_provider_type = Column(String(50), nullable=True)  # broker, transporter, etc.
business_entity_type = Column(String(50), nullable=True)  # proprietorship, llp, etc.

# Auto Capability Detection
capabilities = Column(
    JSON,
    nullable=False,
    default={
        "domestic_buy": False,
        "domestic_sell": False,
        "import_allowed": False,
        "export_allowed": False,
        "auto_detected": False,
        "detected_from_documents": [],
        "detected_at": None,
        "manual_override": False,
        "override_reason": None
    }
)

# Insider Trading Prevention
master_entity_id = Column(UUID(as_uuid=True), ForeignKey("business_partners.id"), nullable=True)
corporate_group_id = Column(UUID(as_uuid=True), nullable=True, index=True)
is_master_entity = Column(Boolean, default=True, nullable=False)
entity_hierarchy = Column(
    JSON,
    nullable=True,
    default={
        "parent_id": None,
        "branch_ids": [],
        "subsidiary_ids": [],
        "sister_concern_ids": []
    }
)
```

**PartnerOnboardingApplication Model:**
- Apply SAME changes as BusinessPartner

**Settings BusinessPartner Model:**
- Apply SAME changes (minimal version)

#### 1.3 Create Migration Script

**File:** `backend/db/migrations/versions/YYYYMMDD_HHMMSS_add_capability_system.py`

**Migration Steps:**
1. ✅ Add new columns (nullable initially)
2. ✅ Migrate data from old columns
3. ✅ Add indexes and constraints
4. ✅ Drop old columns
5. ✅ Create migration log

**Data Migration Logic:**
```sql
-- Convert partner_type → capabilities
UPDATE business_partners SET
    is_service_provider = CASE 
        WHEN partner_type IN ('broker', 'sub_broker', 'transporter', 'controller', 'financer', 'shipping_agent') 
        THEN true ELSE false 
    END,
    service_provider_type = CASE 
        WHEN partner_type IN ('broker', 'sub_broker', 'transporter', 'controller', 'financer', 'shipping_agent') 
        THEN partner_type ELSE NULL 
    END,
    capabilities = CASE
        WHEN partner_type = 'seller' THEN 
            '{"domestic_buy": false, "domestic_sell": true, "import_allowed": false, "export_allowed": false, ...}'::jsonb
        WHEN partner_type = 'buyer' THEN 
            '{"domestic_buy": true, "domestic_sell": false, ...}'::jsonb
        WHEN partner_type = 'trader' THEN 
            '{"domestic_buy": true, "domestic_sell": true, ...}'::jsonb
        WHEN partner_type = 'importer' THEN 
            '{"domestic_buy": true, "import_allowed": true, ...}'::jsonb
        WHEN partner_type = 'exporter' THEN 
            '{"domestic_sell": true, "export_allowed": true, ...}'::jsonb
        WHEN partner_type IN ('broker', 'sub_broker', 'transporter', 'controller', 'financer', 'shipping_agent') THEN 
            '{"domestic_buy": false, "domestic_sell": false, ...}'::jsonb
    END;
```

**Rollback Strategy:**
```sql
-- Can recreate partner_type from capabilities
UPDATE business_partners SET
    partner_type = CASE
        WHEN is_service_provider = true THEN service_provider_type
        WHEN capabilities->>'domestic_buy' = 'true' AND capabilities->>'domestic_sell' = 'true' THEN 'trader'
        WHEN capabilities->>'domestic_buy' = 'true' THEN 'buyer'
        WHEN capabilities->>'domestic_sell' = 'true' THEN 'seller'
    END;
```

---

### **PHASE 2: Services & Business Logic** (2 days)

#### 2.1 Capability Detection Service (`partners/services.py`)

**ADD New Class:**
```python
class CapabilityDetectionService:
    """
    Auto-detect capabilities from verified documents
    
    Rules:
    - GST + PAN → domestic_buy & domestic_sell = True
    - IEC → import_allowed & export_allowed = True
    - Foreign Tax ID + Reg → domestic trading in their country
    - Service providers → all capabilities = False
    """
    
    async def detect_capabilities_from_documents(partner_id: UUID) -> Dict
    async def update_partner_capabilities(partner_id: UUID) -> BusinessPartner
    async def manually_override_capabilities(partner_id, capabilities, reason) -> BusinessPartner
```

**Trigger Points:**
- After document upload + OCR verification
- After manual document verification
- After GST/Tax verification
- After partner approval

#### 2.2 Insider Trading Validator (`partners/validators.py`)

**ADD New Class:**
```python
class InsiderTradingValidator:
    """
    Prevent related-party trading
    
    Blocks:
    1. Same entity (buyer_id == seller_id)
    2. Master ↔ Branch
    3. Sibling branches (same master_entity_id)
    4. Same corporate_group_id
    5. Parent ↔ Subsidiary
    6. Sister concerns (same parent)
    """
    
    async def validate_trade_parties(buyer_id: UUID, seller_id: UUID) -> Dict[str, Any]
```

**Returns:**
```python
{
    "allowed": bool,
    "reason": str,
    "violation_type": str | None  # SAME_ENTITY, MASTER_BRANCH_TRADING, etc.
}
```

#### 2.3 Update Existing Services

**Partners Service (`partners/services.py`):**
- ❌ REMOVE all `partner_type` logic
- ✅ ADD capability detection in approval flow
- ✅ UPDATE document processing to trigger capability detection

**Partner Repository (`partners/repositories.py`):**
- ❌ REMOVE `partner_type` filter
- ✅ ADD `is_service_provider` filter
- ✅ ADD `has_buy_capability` filter (JSONB query)
- ✅ ADD `has_sell_capability` filter

---

### **PHASE 3: Trade Desk Integration** (2 days)

#### 3.1 Availability Service (`trade_desk/services/availability_service.py`)

**REPLACE Line ~798-801:**
```python
# ❌ OLD
# TODO: Implement actual validation by checking business_partner.partner_type

# ✅ NEW
async def _validate_seller_capabilities(self, business_partner_id: UUID) -> None:
    """
    Validate seller can post availability
    
    Rules:
    - Service providers CANNOT trade
    - Must have capabilities.domestic_sell = True
    """
    partner = await self.partner_repo.get_by_id(business_partner_id)
    
    if partner.is_service_provider:
        raise ValueError(
            f"Service providers cannot post availabilities. "
            f"Partner is registered as {partner.service_provider_type}."
        )
    
    if not partner.capabilities.get("domestic_sell", False):
        raise ValueError(
            "Partner does not have domestic_sell capability. "
            "Upload GST + PAN documents to enable selling."
        )
```

**Call this method:** Before creating availability

#### 3.2 Requirement Service (`trade_desk/services/requirement_service.py`)

**REPLACE Line ~1432:**
```python
# ❌ OLD
# TODO: Load business partner and check partner_type

# ✅ NEW
async def _validate_buyer_capabilities(self, business_partner_id: UUID) -> None:
    """
    Validate buyer can post requirement
    
    Rules:
    - Service providers CANNOT trade
    - Must have capabilities.domestic_buy = True
    """
    partner = await self.partner_repo.get_by_id(business_partner_id)
    
    if partner.is_service_provider:
        raise ValueError(
            f"Service providers cannot post requirements. "
            f"Partner is registered as {partner.service_provider_type}."
        )
    
    if not partner.capabilities.get("domestic_buy", False):
        raise ValueError(
            "Partner does not have domestic_buy capability. "
            "Upload GST + PAN documents to enable buying."
        )
```

**Call this method:** Before creating requirement

#### 3.3 Matching Validators (`trade_desk/matching/validators.py`)

**ADD to `validate_match_eligibility()` method (after line 100):**
```python
# Insider Trading Validation
from backend.modules.partners.validators import InsiderTradingValidator

insider_validator = InsiderTradingValidator(self.db)
insider_result = await insider_validator.validate_trade_parties(
    buyer_id=requirement.business_partner_id,
    seller_id=availability.business_partner_id,
    db=self.db
)

if not insider_result["allowed"]:
    reasons.append(insider_result["reason"])
    return ValidationResult(is_valid=False, reasons=reasons, warnings=warnings, ai_alerts=ai_alerts)

# Capability Validation
buyer = await self.db.get(BusinessPartner, requirement.business_partner_id)
seller = await self.db.get(BusinessPartner, availability.business_partner_id)

buyer_capabilities = buyer.capabilities or {}
seller_capabilities = seller.capabilities or {}

if not buyer_capabilities.get("domestic_buy", False):
    reasons.append("Buyer does not have domestic_buy capability")

if not seller_capabilities.get("domestic_sell", False):
    reasons.append("Seller does not have domestic_sell capability")
```

---

### **PHASE 4: Risk Engine Updates** (1 day)

#### 4.1 Risk Engine (`risk/risk_engine.py`)

**REPLACE `validate_partner_role()` method (lines 884-994):**
```python
async def validate_partner_role(
    self,
    partner_id: UUID,
    transaction_type: str  # "BUY" or "SELL"
) -> Dict[str, Any]:
    """
    Validate partner has capability for transaction
    
    Capability-Based Validation:
    - BUY requires capabilities.domestic_buy = True
    - SELL requires capabilities.domestic_sell = True
    - Service providers blocked from trading
    """
    partner = await self.db.get(BusinessPartner, partner_id)
    
    if not partner:
        return {"allowed": False, "reason": "Partner not found"}
    
    # Block service providers
    if partner.is_service_provider:
        return {
            "allowed": False,
            "reason": f"Service providers cannot trade. Partner is {partner.service_provider_type}.",
            "violation_type": "SERVICE_PROVIDER_CANNOT_TRADE"
        }
    
    capabilities = partner.capabilities or {}
    
    if transaction_type == "BUY":
        if not capabilities.get("domestic_buy", False):
            return {
                "allowed": False,
                "reason": "Partner does not have domestic_buy capability.",
                "violation_type": "MISSING_BUY_CAPABILITY"
            }
    elif transaction_type == "SELL":
        if not capabilities.get("domestic_sell", False):
            return {
                "allowed": False,
                "reason": "Partner does not have domestic_sell capability.",
                "violation_type": "MISSING_SELL_CAPABILITY"
            }
    
    return {"allowed": True, "reason": "Partner has required capability"}
```

#### 4.2 Risk Schemas (`risk/schemas.py`)

**DELETE Lines 40-45, 199, 206, 346-347:**
```python
# ❌ DELETE
partner_type: str = Field(...)  
@validator('partner_type')
def validate_partner_type(cls, v): ...
```

**No replacement needed** - validation now uses capabilities

---

### **PHASE 5: Schema Updates** (1 day)

#### 5.1 Partner Schemas (`partners/schemas.py`)

**DELETE:**
```python
# Line 35 - ❌ DELETE
partner_type: PartnerType

# Line 50 - ❌ DELETE
partner_type: Optional[PartnerType] = None

# Line 165 - ❌ DELETE
trade_classification: Optional[TradeClassification] = None

# Line 361 - ❌ DELETE
trade_classification: Optional[TradeClassification] = None
```

**ADD:**
```python
class OnboardingApplicationCreate(BaseModel):
    """Step 1: Service Provider or Business Entity"""
    is_service_provider: bool
    service_provider_type: Optional[ServiceProviderType] = None
    business_entity_type: Optional[BusinessEntityType] = None
    
    @validator('service_provider_type')
    def validate_service_provider_type(cls, v, values):
        if values.get('is_service_provider') and not v:
            raise ValueError("service_provider_type required when is_service_provider=True")
        return v
    
    @validator('business_entity_type')
    def validate_business_entity_type(cls, v, values):
        if not values.get('is_service_provider') and not v:
            raise ValueError("business_entity_type required when is_service_provider=False")
        return v


class CapabilityResponse(BaseModel):
    domestic_buy: bool
    domestic_sell: bool
    import_allowed: bool
    export_allowed: bool
    auto_detected: bool
    detected_from_documents: List[str]
    detected_at: Optional[datetime]
    manual_override: bool = False
    override_reason: Optional[str] = None


class BusinessPartnerResponse(BaseModel):
    id: UUID
    is_service_provider: bool
    service_provider_type: Optional[str]
    business_entity_type: Optional[str]
    capabilities: CapabilityResponse
    # ... rest of fields ...
```

#### 5.2 Trade Desk Schemas (`trade_desk/schemas/__init__.py`)

**DELETE Line 239:**
```python
partner_type: str  # ❌ DELETE
```

---

### **PHASE 6: Router & API Updates** (1 day)

#### 6.1 Partner Router (`partners/router.py`)

**ADD New Endpoints:**
```python
@router.post("/partners/{partner_id}/capabilities/detect")
async def detect_partner_capabilities(
    partner_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Manually trigger capability detection from documents"""
    service = CapabilityDetectionService(db, emitter)
    partner = await service.update_partner_capabilities(partner_id)
    return {"capabilities": partner.capabilities}


@router.put("/partners/{partner_id}/capabilities/override")
async def override_partner_capabilities(
    partner_id: UUID,
    capabilities: Dict[str, bool],
    reason: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)  # Admin only
):
    """Manually override auto-detected capabilities"""
    service = CapabilityDetectionService(db, emitter)
    partner = await service.manually_override_capabilities(
        partner_id, capabilities, reason, current_user.id
    )
    return {"capabilities": partner.capabilities}


@router.post("/partners/{partner_id}/entity-hierarchy")
async def update_entity_hierarchy(
    partner_id: UUID,
    hierarchy: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """Update corporate structure for insider trading prevention"""
    partner = await partner_repo.get_by_id(partner_id)
    partner.entity_hierarchy = hierarchy
    await db.commit()
    return {"entity_hierarchy": partner.entity_hierarchy}
```

#### 6.2 Update Notification Templates (`partners/notifications.py`)

**REPLACE Line 170:**
```python
# ❌ OLD
- Partner Type: {partner.partner_type}

# ✅ NEW
- Entity Type: {"Service Provider: " + partner.service_provider_type if partner.is_service_provider else "Business Entity: " + partner.business_entity_type}
- Trading Capabilities: 
  {"✓ Can Buy" if partner.capabilities.get("domestic_buy") else "✗ Cannot Buy"}
  {"✓ Can Sell" if partner.capabilities.get("domestic_sell") else "✗ Cannot Sell"}
  {"✓ Import" if partner.capabilities.get("import_allowed") else ""}
  {"✓ Export" if partner.capabilities.get("export_allowed") else ""}
```

---

### **PHASE 7: AI Assistant Updates** (1 day)

#### 7.1 Partner Assistant (`ai/assistants/partner_assistant/assistant.py`)

**REPLACE all `partner_type` logic:**
```python
# ✅ NEW
async def assist_onboarding_start(
    self,
    is_service_provider: bool,
    service_provider_type: Optional[str] = None,
    business_entity_type: Optional[str] = None
) -> Dict:
    if is_service_provider:
        requirements = await self.tools.get_service_provider_requirements(service_provider_type)
        greeting = f"Welcome! Let's get you registered as a {service_provider_type}."
    else:
        requirements = await self.tools.get_business_entity_requirements(business_entity_type)
        greeting = f"Welcome! Let's set up your {business_entity_type} entity."
    
    return {
        "greeting": greeting,
        "requirements": requirements,
        "capabilities_note": "We'll automatically detect your trading capabilities from uploaded documents."
    }
```

#### 7.2 Partner Tools (`ai/assistants/partner_assistant/tools.py`)

**SPLIT into two methods:**
```python
# REPLACE get_onboarding_requirements(partner_type)

async def get_service_provider_requirements(service_provider_type: str) -> Dict:
    """Requirements for service providers (broker, transporter, etc.)"""
    # Existing service provider logic

async def get_business_entity_requirements(business_entity_type: str) -> Dict:
    """Requirements for business entities (traders)"""
    return {
        "documents": ["GST", "PAN", "Bank Proof"],
        "capabilities": {
            "info": "Capabilities auto-detected from documents",
            "GST + PAN": "Enables domestic buying and selling",
            "IEC": "Enables import and export"
        }
    }
```

#### 7.3 Partner Prompts (`ai/prompts/partner/prompts.py`)

**REPLACE Lines 46, 55:**
```python
# ✅ NEW
User is starting partner onboarding.
Step 1: Are they a service provider (broker/transporter) or business entity (trader)?
```

---

### **PHASE 8: Testing** (2 days)

#### 8.1 New Test File: `test_capability_detection.py`

**5 Tests:**
```python
async def test_indian_domestic_detection():
    """GST + PAN → domestic_buy & domestic_sell = True"""
    
async def test_indian_iec_detection():
    """IEC → all capabilities = True"""
    
async def test_foreign_domestic_detection():
    """Foreign Tax ID + Reg → domestic trading"""
    
async def test_foreign_import_detection():
    """Foreign Import License → import_allowed = True"""
    
async def test_foreign_export_detection():
    """Foreign Export License → export_allowed = True"""
```

#### 8.2 New Test File: `test_insider_trading.py`

**5 Tests:**
```python
async def test_same_entity_blocked():
    """buyer_id == seller_id → blocked"""
    
async def test_master_branch_blocked():
    """Master ↔ Branch → blocked"""
    
async def test_sibling_branches_blocked():
    """Same master_entity_id → blocked"""
    
async def test_corporate_group_blocked():
    """Same corporate_group_id → blocked"""
    
async def test_parent_subsidiary_blocked():
    """Parent ↔ Subsidiary → blocked"""
```

#### 8.3 New Test File: `test_trade_desk_capabilities.py`

**3 Tests:**
```python
async def test_service_provider_cannot_post_availability():
    """Broker trying to post availability → raises ValueError"""
    
async def test_service_provider_cannot_post_requirement():
    """Transporter trying to post requirement → raises ValueError"""
    
async def test_valid_partners_can_match():
    """Unrelated partners with capabilities → allowed"""
```

#### 8.4 Update Existing Test Fixtures

**Replace all partner fixtures:**
```python
@pytest.fixture
async def sample_buyer(db):
    """Business entity with buy capability"""
    return BusinessPartner(
        is_service_provider=False,
        business_entity_type="private_limited",
        capabilities={
            "domestic_buy": True,
            "domestic_sell": False,
            "import_allowed": False,
            "export_allowed": False,
            "auto_detected": True,
            "detected_from_documents": ["GST", "PAN"]
        }
    )

@pytest.fixture
async def sample_broker(db):
    """Service provider - cannot trade"""
    return BusinessPartner(
        is_service_provider=True,
        service_provider_type="broker",
        capabilities={
            "domestic_buy": False,
            "domestic_sell": False,
            "import_allowed": False,
            "export_allowed": False,
            "auto_detected": False,
            "detected_from_documents": ["service_provider"]
        }
    )
```

---

## 🔒 ZERO BREAKING CHANGES GUARANTEE

### ✅ UNTOUCHED Components (No Changes)

#### Service Provider Flows
- ✅ Broker onboarding - Exact same flow
- ✅ Sub-broker onboarding - Exact same flow
- ✅ Transporter onboarding - Lorry owner vs commission agent logic UNCHANGED
- ✅ Controller onboarding - Exact same flow
- ✅ Financer onboarding - Exact same flow
- ✅ Shipping agent onboarding - Exact same flow

**Implementation:** `is_service_provider=True` + `service_provider_type` replaces old `partner_type` for service providers

#### KYC Flows
- ✅ KYC renewal tracking (365 days) - UNCHANGED
- ✅ KYC reminders (90/60/30/7 days) - UNCHANGED
- ✅ Auto-suspend job (configurable) - UNCHANGED
- ✅ KYC status management - UNCHANGED
- ✅ Document verification - UNCHANGED (+ triggers capability detection)

#### Back Office Features
- ✅ Advanced filters - NEW filters added, old ones work
- ✅ Export to Excel/CSV - UNCHANGED
- ✅ KYC PDF download - UNCHANGED
- ✅ Dashboard analytics - UNCHANGED
- ✅ Notifications - Email templates updated (minor)
- ✅ Scheduled jobs - UNCHANGED
- ✅ Amendment workflows - UNCHANGED

### 📊 Data Migration Strategy

**Before Migration:**
```
partner_type: "seller"
trade_classification: "domestic"
```

**After Migration:**
```
is_service_provider: false
service_provider_type: null
business_entity_type: "private_limited"
capabilities: {
    "domestic_buy": false,
    "domestic_sell": true,
    "import_allowed": false,
    "export_allowed": false,
    "auto_detected": false,
    "detected_from_documents": ["legacy_migration"],
    "manual_override": false
}
```

**Rollback Available:** Migration includes downgrade() that reconstructs partner_type from capabilities

---

## 📅 IMPLEMENTATION TIMELINE

| Phase | Duration | Tasks |
|-------|----------|-------|
| **Phase 1** | 2 days | Database schema, models, migration script |
| **Phase 2** | 2 days | Services, validators, capability detection |
| **Phase 3** | 2 days | Trade desk integration, matching validators |
| **Phase 4** | 1 day | Risk engine updates |
| **Phase 5** | 1 day | Schema updates, API contracts |
| **Phase 6** | 1 day | Router updates, new endpoints |
| **Phase 7** | 1 day | AI assistant updates |
| **Phase 8** | 2 days | Testing (13 new tests) |
| **Testing** | 1 day | Full regression testing |
| **Documentation** | 1 day | Update docs, migration guide |

**Total: 8-10 working days**

---

## ✅ PRE-IMPLEMENTATION CHECKLIST

### Database Backup
- [ ] Full database backup before migration
- [ ] Test migration in staging environment
- [ ] Verify rollback works

### Code Review
- [ ] Review all 21 file changes
- [ ] Verify no breaking changes to service providers
- [ ] Verify no breaking changes to KYC flows
- [ ] Verify no breaking changes to back-office

### Testing
- [ ] Run all existing tests (should still pass)
- [ ] Run 13 new tests
- [ ] Manual testing of onboarding flow
- [ ] Manual testing of trade desk

### Deployment
- [ ] Deploy to staging
- [ ] User acceptance testing
- [ ] Deploy to production

---

## 🎯 SUCCESS METRICS

### Before CDPS
- ❌ 11 partner types (rigid classification)
- ❌ 3 trade classifications (limited flexibility)
- ❌ Hard-coded role restrictions
- ❌ No insider trading prevention
- ❌ Manual capability management

### After CDPS
- ✅ 2 main categories (service provider vs business entity)
- ✅ 4 auto-detected capabilities (flexible, multi-capability support)
- ✅ Document-driven capability detection
- ✅ 6 insider trading rules enforced
- ✅ Future-proof for new capabilities

---

## 📝 DETAILED APPROVAL DOCUMENTATION

### APPROVAL SECTION 1: Files to Modify (21 Files)

#### 1.1 Core Partner Module (9 files) - DETAILED CHANGES

**File 1: `backend/modules/partners/models.py`**
- **Lines to Delete:** 97-110 (partner_type, service_provider_type, trade_classification columns)
- **Lines to Add:** 90-150 (new columns: is_service_provider, business_entity_type, capabilities, master_entity_id, corporate_group_id, entity_hierarchy)
- **Impact:** BusinessPartner + PartnerOnboardingApplication models
- **Breaking Change:** NO (migration handles conversion)
- **Estimated Time:** 3 hours

**File 2: `backend/modules/partners/enums.py`**
- **Lines to Add:** After line 35 (BusinessEntityType enum with 10 values)
- **Lines to Add:** After line 105 (4 new DocumentType values: IEC, FOREIGN_TAX_ID, FOREIGN_IMPORT_LICENSE, FOREIGN_EXPORT_LICENSE)
- **Lines to Delete:** 42-47 (TradeClassification enum - entire enum)
- **Lines to Deprecate:** 10-25 (PartnerType enum - add deprecation comment, keep for migration)
- **Breaking Change:** NO (old enums kept until migration complete)
- **Estimated Time:** 1 hour

**File 3: `backend/modules/partners/schemas.py`**
- **Lines to Delete:** 35, 50, 165, 361 (all partner_type and trade_classification fields)
- **Lines to Add:** 30-80 (new OnboardingApplicationCreate with validators)
- **Lines to Add:** 200-220 (CapabilityResponse schema)
- **Lines to Modify:** BusinessPartnerResponse (replace partner_type with is_service_provider + capabilities)
- **Breaking Change:** YES (API contract change - but backward compatible during migration)
- **Estimated Time:** 4 hours

**File 4: `backend/modules/partners/services.py`**
- **Lines to Delete:** 363, 376, 497, 507, 614, 883, 885, 962 (all partner_type references)
- **Lines to Add:** 1000-1300 (new CapabilityDetectionService class - 300 lines)
- **Lines to Modify:** ApprovalService.process_approval() - add capability detection call
- **Lines to Modify:** DocumentProcessingService.verify_document_ocr() - add capability detection trigger
- **Breaking Change:** NO (logic enhancement only)
- **Estimated Time:** 6 hours

**File 5: `backend/modules/partners/validators.py`**
- **Lines to Modify:** Line 46 (replace partner.partner_type check with capabilities check)
- **Lines to Add:** 100-250 (new InsiderTradingValidator class - 150 lines)
- **Breaking Change:** NO (enhanced validation only)
- **Estimated Time:** 4 hours

**File 6: `backend/modules/partners/router.py`**
- **Lines to Add:** 500-600 (3 new endpoints: detect_capabilities, override_capabilities, update_entity_hierarchy)
- **Lines to Modify:** Existing endpoints to use new schema fields
- **Breaking Change:** NO (new endpoints, old ones enhanced)
- **Estimated Time:** 3 hours

**File 7: `backend/modules/partners/repositories.py`**
- **Lines to Delete:** 187, 199, 215-216 (partner_type filter parameter and usage)
- **Lines to Add:** 190-230 (new filters: is_service_provider, has_buy_capability, has_sell_capability with JSONB queries)
- **Breaking Change:** YES (filter parameter change - but optional, so backward compatible)
- **Estimated Time:** 2 hours

**File 8: `backend/modules/partners/notifications.py`**
- **Lines to Modify:** 170 (replace "Partner Type: {partner.partner_type}" with new format)
- **Lines to Add:** 171-175 (new capability display in email)
- **Breaking Change:** NO (cosmetic email change only)
- **Estimated Time:** 1 hour

**File 9: `backend/modules/partners/events.py`**
- **Lines to Add:** 450-550 (3 new event classes: CapabilitiesDetectedEvent, CapabilitiesManuallyOverriddenEvent, CapabilitiesResetToAutoDetectEvent)
- **Breaking Change:** NO (new events only)
- **Estimated Time:** 2 hours

**Partner Module Total:** 9 files, 26 hours estimated

---

#### 1.2 Trade Desk Module (4 files) - DETAILED CHANGES

**File 10: `backend/modules/trade_desk/services/availability_service.py`**
- **Lines to Replace:** 798-801 (TODO comment → full validation method)
- **Lines to Add:** 50-80 (new _validate_seller_capabilities method - 30 lines)
- **Lines to Modify:** create_availability() - add capability validation call before creation
- **Breaking Change:** YES (new validation - but proper, was TODO before)
- **Estimated Time:** 3 hours

**File 11: `backend/modules/trade_desk/services/requirement_service.py`**
- **Lines to Replace:** 1432 (TODO comment → full validation method)
- **Lines to Add:** 100-130 (new _validate_buyer_capabilities method - 30 lines)
- **Lines to Modify:** create_requirement() - add capability validation call before creation
- **Breaking Change:** YES (new validation - but proper, was TODO before)
- **Estimated Time:** 3 hours

**File 12: `backend/modules/trade_desk/matching/validators.py`**
- **Lines to Add:** 105-160 (insider trading validation block - 55 lines)
- **Lines to Add:** 165-185 (capability validation block - 20 lines)
- **Lines to Modify:** validate_match_eligibility() method
- **Breaking Change:** YES (new validation - enhanced matching logic)
- **Estimated Time:** 4 hours

**File 13: `backend/modules/trade_desk/schemas/__init__.py`**
- **Lines to Delete:** 239 (partner_type: str field)
- **Breaking Change:** YES (schema change - but field was unused)
- **Estimated Time:** 0.5 hours

**Trade Desk Module Total:** 4 files, 10.5 hours estimated

---

#### 1.3 Risk Module (2 files) - DETAILED CHANGES

**File 14: `backend/modules/risk/risk_engine.py`**
- **Lines to Replace:** 884-994 (entire validate_partner_role method - 110 lines)
- **New Method:** 884-950 (new capability-based validation - 66 lines)
- **Lines to Delete:** 909, 913, 915, 919, 923, 928, 937, 944, 950, 959, 966 (all partner_type references)
- **Breaking Change:** NO (logic change but same interface)
- **Estimated Time:** 4 hours

**File 15: `backend/modules/risk/schemas.py`**
- **Lines to Delete:** 40-45, 199, 206, 346-347 (all partner_type fields and validators)
- **Breaking Change:** YES (schema change - but field was for validation only)
- **Estimated Time:** 1 hour

**Risk Module Total:** 2 files, 5 hours estimated

---

#### 1.4 Settings Module (1 file) - DETAILED CHANGES

**File 16: `backend/modules/settings/business_partners/models.py`**
- **Lines to Delete:** 43-50 (partner_type column)
- **Lines to Add:** 43-70 (new columns: is_service_provider, capabilities - minimal version)
- **Breaking Change:** NO (minimal model, same migration applies)
- **Estimated Time:** 1 hour

**Settings Module Total:** 1 file, 1 hour estimated

---

#### 1.5 AI Module (3 files) - DETAILED CHANGES

**File 17: `backend/ai/assistants/partner_assistant/assistant.py`**
- **Lines to Delete:** 39, 46, 53, 56, 58, 75, 81, 86, 469, 471, 473 (all partner_type parameters and logic)
- **Lines to Replace:** 35-90 (assist_onboarding_start method - new signature with is_service_provider)
- **Lines to Replace:** 469-480 (_estimate_onboarding_time method - new logic)
- **Breaking Change:** NO (internal AI logic only)
- **Estimated Time:** 3 hours

**File 18: `backend/ai/assistants/partner_assistant/tools.py`**
- **Lines to Replace:** 31-170 (get_onboarding_requirements method → split into 2 methods)
- **Lines to Add:** 30-100 (new get_service_provider_requirements method)
- **Lines to Add:** 105-150 (new get_business_entity_requirements method)
- **Lines to Delete:** 214-280 (old get_document_checklist method signature)
- **Breaking Change:** NO (internal AI tools only)
- **Estimated Time:** 4 hours

**File 19: `backend/ai/prompts/partner/prompts.py`**
- **Lines to Replace:** 46, 55 (partner_type references → new onboarding question)
- **Breaking Change:** NO (prompt changes only)
- **Estimated Time:** 0.5 hours

**AI Module Total:** 3 files, 7.5 hours estimated

---

#### 1.6 Database (2 files) - DETAILED CHANGES

**File 20: `backend/db/migrations/versions/YYYYMMDD_HHMMSS_add_capability_system.py`**
- **Lines to Add:** 1-600 (complete new migration file)
- **Sections:**
  - upgrade() function: 300 lines
  - downgrade() function: 200 lines
  - Data migration SQL: 100 lines
- **Breaking Change:** NO (migration handles everything)
- **Estimated Time:** 8 hours

**File 21: `backend/modules/partners/tests/test_capabilities.py`**
- **Lines to Add:** 1-400 (complete new test file with 13 tests)
- **Test Categories:**
  - Capability detection: 5 tests (150 lines)
  - Insider trading: 5 tests (150 lines)
  - Trade desk: 3 tests (100 lines)
- **Breaking Change:** NO (new tests only)
- **Estimated Time:** 6 hours

**Database Module Total:** 2 files, 14 hours estimated

---

### TOTAL FILE MODIFICATION SUMMARY

| Module | Files | Est. Hours | Breaking Changes | Critical |
|--------|-------|------------|------------------|----------|
| Partners | 9 | 26 | 1 (schemas - backward compatible) | HIGH |
| Trade Desk | 4 | 10.5 | 3 (validations - enhancement) | HIGH |
| Risk | 2 | 5 | 0 (interface unchanged) | MEDIUM |
| Settings | 1 | 1 | 0 | LOW |
| AI | 3 | 7.5 | 0 (internal only) | LOW |
| Database | 2 | 14 | 0 (migration handles) | HIGH |
| **TOTAL** | **21** | **64** | **4 (all mitigated)** | - |

**Estimated Calendar Time:** 64 hours ÷ 8 hours/day = **8 working days**  
**With testing buffer:** 8 + 2 days = **10 working days**

---

### APPROVAL SECTION 2: Implementation Phases - DETAILED BREAKDOWN

#### Phase 1: Database Schema Changes (Days 1-2)

**Day 1 Morning (4 hours):**
- [ ] Update `partners/enums.py` - Add BusinessEntityType, new DocumentTypes
- [ ] Deprecate PartnerType enum (add comments)
- [ ] Delete TradeClassification enum
- [ ] Run tests to ensure enums are importable
- [ ] **Deliverable:** Updated enums file, all imports working

**Day 1 Afternoon (4 hours):**
- [ ] Update `partners/models.py` - BusinessPartner model changes
- [ ] Delete old columns (partner_type, trade_classification)
- [ ] Add new columns (is_service_provider, capabilities, etc.)
- [ ] Update PartnerOnboardingApplication model (same changes)
- [ ] Update `settings/business_partners/models.py` (minimal version)
- [ ] **Deliverable:** Updated models, no syntax errors

**Day 2 Morning (4 hours):**
- [ ] Create migration file `add_capability_system.py`
- [ ] Write upgrade() function with 5 steps
- [ ] Write data migration SQL (convert partner_type → capabilities)
- [ ] Add indexes and constraints
- [ ] **Deliverable:** Complete migration script

**Day 2 Afternoon (4 hours):**
- [ ] Write downgrade() function (rollback strategy)
- [ ] Test migration in local environment
- [ ] Verify data conversion accuracy
- [ ] Test rollback functionality
- [ ] **Deliverable:** Tested migration, rollback verified

**Phase 1 Completion Criteria:**
- ✅ All enums updated and importable
- ✅ All models updated with new columns
- ✅ Migration runs successfully (upgrade)
- ✅ Rollback works (downgrade)
- ✅ No data loss in test environment

---

#### Phase 2: Services & Business Logic (Days 3-4)

**Day 3 Morning (4 hours):**
- [ ] Create `CapabilityDetectionService` class in `partners/services.py`
- [ ] Implement `detect_capabilities_from_documents()` method
- [ ] Implement detection rules (GST+PAN, IEC, Foreign docs)
- [ ] Add service provider blocking logic
- [ ] **Deliverable:** Working capability detection service

**Day 3 Afternoon (4 hours):**
- [ ] Implement `update_partner_capabilities()` method
- [ ] Implement `manually_override_capabilities()` method
- [ ] Add capability events to `partners/events.py`
- [ ] Add trigger points (document verification, approval)
- [ ] **Deliverable:** Auto-detection integrated into workflows

**Day 4 Morning (4 hours):**
- [ ] Create `InsiderTradingValidator` class in `partners/validators.py`
- [ ] Implement `validate_trade_parties()` method
- [ ] Implement 6 validation rules (same entity, master-branch, etc.)
- [ ] Add detailed error messages for each violation type
- [ ] **Deliverable:** Working insider trading validator

**Day 4 Afternoon (4 hours):**
- [ ] Update `partners/services.py` - remove all partner_type logic
- [ ] Update `partners/repositories.py` - new filters
- [ ] Update `partners/notifications.py` - email templates
- [ ] Test all changes with unit tests
- [ ] **Deliverable:** All partner services updated

**Phase 2 Completion Criteria:**
- ✅ Capability detection working end-to-end
- ✅ Insider trading validator blocking related parties
- ✅ All partner_type references removed from services
- ✅ Unit tests passing

---

#### Phase 3: Trade Desk Integration (Days 5-6)

**Day 5 Morning (4 hours):**
- [ ] Update `availability_service.py` - add `_validate_seller_capabilities()`
- [ ] Block service providers from posting availabilities
- [ ] Check capabilities.domestic_sell = True
- [ ] Add validation call in create_availability()
- [ ] Test with various partner types
- [ ] **Deliverable:** Availability validation working

**Day 5 Afternoon (4 hours):**
- [ ] Update `requirement_service.py` - add `_validate_buyer_capabilities()`
- [ ] Block service providers from posting requirements
- [ ] Check capabilities.domestic_buy = True
- [ ] Add validation call in create_requirement()
- [ ] Test with various partner types
- [ ] **Deliverable:** Requirement validation working

**Day 6 Morning (4 hours):**
- [ ] Update `matching/validators.py` - add insider trading check
- [ ] Add capability validation in matching
- [ ] Import and use InsiderTradingValidator
- [ ] Update ValidationResult with new reasons
- [ ] **Deliverable:** Matching validation enhanced

**Day 6 Afternoon (4 hours):**
- [ ] Update `trade_desk/schemas/__init__.py` - remove partner_type
- [ ] Integration testing: create availability → requirement → match
- [ ] Test insider trading blocking
- [ ] Test capability validation
- [ ] **Deliverable:** End-to-end trade desk working

**Phase 3 Completion Criteria:**
- ✅ Service providers cannot post availabilities/requirements
- ✅ Partners without capabilities blocked
- ✅ Insider trading validator integrated into matching
- ✅ All trade desk flows working

---

#### Phase 4: Risk Engine Updates (Day 7)

**Day 7 Morning (4 hours):**
- [ ] Update `risk/risk_engine.py` - replace `validate_partner_role()`
- [ ] Remove all partner_type logic (lines 884-994)
- [ ] Implement capability-based validation
- [ ] Block service providers
- [ ] Check capabilities for BUY/SELL transactions
- [ ] **Deliverable:** New validation method working

**Day 7 Afternoon (4 hours):**
- [ ] Update `risk/schemas.py` - remove partner_type fields
- [ ] Remove partner_type validators
- [ ] Test risk engine with new validation
- [ ] Ensure contract engine still works (uses risk engine)
- [ ] **Deliverable:** Risk engine fully updated

**Phase 4 Completion Criteria:**
- ✅ validate_partner_role() uses capabilities
- ✅ No partner_type references in risk module
- ✅ All risk engine tests passing

---

#### Phase 5: Schema Updates (Day 8 Morning)

**Day 8 Morning (4 hours):**
- [ ] Update `partners/schemas.py` - remove partner_type fields
- [ ] Add OnboardingApplicationCreate with validators
- [ ] Add CapabilityResponse schema
- [ ] Update BusinessPartnerResponse schema
- [ ] Add validation for is_service_provider logic
- [ ] Test schema validation with Pydantic
- [ ] **Deliverable:** All schemas updated

**Phase 5 Completion Criteria:**
- ✅ No partner_type in any schema
- ✅ New onboarding schema validates correctly
- ✅ API contracts updated

---

#### Phase 6: Router & API Updates (Day 8 Afternoon)

**Day 8 Afternoon (4 hours):**
- [ ] Update `partners/router.py` - add 3 new endpoints
- [ ] POST /partners/{id}/capabilities/detect
- [ ] PUT /partners/{id}/capabilities/override
- [ ] POST /partners/{id}/entity-hierarchy
- [ ] Update existing endpoints to use new schemas
- [ ] Test all endpoints with Postman/curl
- [ ] **Deliverable:** API fully functional

**Phase 6 Completion Criteria:**
- ✅ New endpoints working
- ✅ Existing endpoints backward compatible
- ✅ API documentation updated

---

#### Phase 7: AI Assistant Updates (Day 9 Morning)

**Day 9 Morning (4 hours):**
- [ ] Update `ai/assistants/partner_assistant/assistant.py`
- [ ] Replace partner_type with is_service_provider
- [ ] Update assist_onboarding_start() method
- [ ] Update `ai/assistants/partner_assistant/tools.py`
- [ ] Split get_onboarding_requirements() into 2 methods
- [ ] Update `ai/prompts/partner/prompts.py`
- [ ] Test AI assistant flow
- [ ] **Deliverable:** AI assistant working with new system

**Phase 7 Completion Criteria:**
- ✅ AI assistant asks: Service Provider or Business Entity?
- ✅ Onboarding guidance updated
- ✅ No partner_type in AI code

---

#### Phase 8: Testing (Days 9-10)

**Day 9 Afternoon (4 hours):**
- [ ] Create `test_capability_detection.py`
- [ ] Write 5 capability detection tests
- [ ] Test Indian domestic (GST + PAN)
- [ ] Test IEC detection
- [ ] Test foreign partner detection
- [ ] **Deliverable:** Capability detection tests passing

**Day 10 Morning (4 hours):**
- [ ] Create `test_insider_trading.py`
- [ ] Write 5 insider trading tests
- [ ] Test all 6 blocking rules
- [ ] **Deliverable:** Insider trading tests passing

**Day 10 Afternoon (4 hours):**
- [ ] Create `test_trade_desk_capabilities.py`
- [ ] Write 3 trade desk tests
- [ ] Update existing test fixtures (replace partner_type)
- [ ] Run full test suite
- [ ] Fix any failing tests
- [ ] **Deliverable:** All tests passing (existing + new)

**Phase 8 Completion Criteria:**
- ✅ 13 new tests passing
- ✅ All existing tests passing
- ✅ Test coverage >80%

---

### APPROVAL SECTION 3: Zero Breaking Changes - DETAILED GUARANTEE

#### 3.1 Service Provider Flows - UNCHANGED

**Broker Onboarding:**
- **Current Flow:** User selects "Broker" → Enters GST/PAN → No license required → Commission structure → Approval
- **New Flow:** User selects "Service Provider" → Selects "Broker" → Enters GST/PAN → No license required → Commission structure → Approval
- **Change:** Only Step 1 question changes (type selection)
- **Data:** `is_service_provider=True`, `service_provider_type="broker"`
- **Capabilities:** All False (service providers cannot trade)
- **Guaranteed:** Exact same validation, documents, approval flow

**Sub-Broker Onboarding:**
- **Current Flow:** Selects "Sub-Broker" → Links to parent broker → Enters details
- **New Flow:** Service Provider → Sub-Broker → Links to parent → Enters details
- **Change:** Only Step 1
- **Guaranteed:** Parent-child relationship logic unchanged

**Transporter Onboarding:**
- **Current Flow:** Selects "Transporter" → Chooses "Lorry Owner" or "Commission Agent" → Different document requirements
- **New Flow:** Service Provider → Transporter → Chooses type → Same document flow
- **Change:** Only Step 1
- **Guaranteed:** Lorry owner vs commission agent logic 100% preserved

**Controller, Financer, Shipping Agent:**
- **Guaranteed:** Exact same flows, only Step 1 question changes

**Testing:**
```python
# Before
partner = BusinessPartner(partner_type="broker")
assert partner.partner_type == "broker"

# After
partner = BusinessPartner(is_service_provider=True, service_provider_type="broker")
assert partner.is_service_provider == True
assert partner.service_provider_type == "broker"
assert partner.capabilities["domestic_buy"] == False  # Cannot trade
```

---

#### 3.2 KYC Flows - UNCHANGED

**KYC Renewal (365 days):**
- **File:** `partners/jobs.py` - `auto_suspend_expired_kyc_job()`
- **Lines:** NO CHANGES
- **Logic:** Checks `kyc_expiry_date`, not partner_type
- **Guaranteed:** Continues working exactly as before

**KYC Reminders (90/60/30/7 days):**
- **File:** `partners/jobs.py` - `daily_kyc_reminder_job()`
- **Lines:** NO CHANGES
- **Logic:** Queries by `kyc_expiry_date`
- **Guaranteed:** Same reminder schedule

**Auto-Suspend (configurable):**
- **File:** `partners/jobs.py`
- **Lines:** NO CHANGES
- **Logic:** Updates `status` field, not partner_type
- **Guaranteed:** Same suspension logic

**Document Verification:**
- **File:** `partners/services.py` - DocumentProcessingService
- **Change:** ENHANCEMENT - adds capability detection trigger
- **Impact:** After doc verification, capabilities auto-detected
- **Guaranteed:** Existing verification logic untouched, only enhanced

**Testing:**
```python
# Verify KYC job still works
partner = BusinessPartner(
    is_service_provider=False,
    kyc_expiry_date=date.today() + timedelta(days=30)
)
result = await check_kyc_expiry(organization_id, days_threshold=30)
assert partner.id in [p.id for p in result]  # Still found
```

---

#### 3.3 Back-Office Features - UNCHANGED

**Advanced Filters:**
- **File:** `partners/router.py` - GET /partners/list
- **Current Filters:** `partner_type`, `status`, `kyc_status`, `state`, etc.
- **New Filters:** 
  - `is_service_provider` (replaces partner_type for service providers)
  - `has_buy_capability` (new)
  - `has_sell_capability` (new)
  - All other filters UNCHANGED
- **Backward Compatibility:** Old filter `partner_type=seller` can be mapped to `has_sell_capability=True`
- **Guaranteed:** Existing filters continue working

**Export to Excel/CSV:**
- **File:** `partners/router.py` - GET /partners/export
- **Change:** Column headers updated (Partner Type → Entity Type + Capabilities)
- **Logic:** Same export mechanism
- **Guaranteed:** Export still works, just different column names

**KYC PDF Download:**
- **File:** `partners/router.py` - GET /partners/{id}/kyc-register/download
- **Change:** PDF template updated to show capabilities instead of partner_type
- **Logic:** Same PDF generation
- **Guaranteed:** PDF still generated

**Dashboard Analytics:**
- **File:** `partners/router.py` - GET /partners/dashboard/stats
- **Current Stats:** `by_type` (seller, buyer counts)
- **New Stats:** 
  - `by_service_provider` (service provider counts)
  - `by_capabilities` (buy capability, sell capability counts)
- **Change:** Additional stats, not replacement
- **Guaranteed:** Dashboard still shows partner distribution

**Notifications:**
- **File:** `partners/notifications.py`
- **Change:** Email template line 170 updated (cosmetic)
- **Impact:** Emails show "Business Entity: LLP" instead of "Partner Type: Trader"
- **Guaranteed:** Same notification triggers, same delivery

**Scheduled Jobs:**
- **Files:** `partners/jobs.py`
- **Lines:** NO CHANGES
- **Guaranteed:** All jobs continue running

**Amendment Workflows:**
- **File:** `partners/services.py` - AmendmentService
- **Lines:** NO CHANGES
- **Guaranteed:** Post-approval amendments work same way

**Testing:**
```python
# Verify back-office still works
# Filter by capabilities instead of partner_type
result = await list_partners(
    organization_id=org_id,
    has_sell_capability=True  # Instead of partner_type="seller"
)
assert len(result) > 0

# Export still works
export_file = await export_partners(format="excel")
assert export_file is not None
```

---

### APPROVAL SECTION 4: Migration Strategy - 100% BACKWARD COMPATIBLE

#### 4.1 Pre-Migration State

**Database:**
```sql
-- Existing columns
business_partners:
  - partner_type: 'seller' | 'buyer' | 'trader' | 'broker' | etc.
  - trade_classification: 'domestic' | 'importer' | 'exporter'

-- Existing data (example)
id: 550e8400-e29b-41d4-a716-446655440000
partner_type: 'seller'
trade_classification: 'domestic'
legal_name: 'ABC Ginning Ltd'
```

**Code:**
```python
# Existing usage
partner = await repo.get_by_id(partner_id)
if partner.partner_type == "seller":
    # Can sell logic
```

---

#### 4.2 Migration Execution

**Step 1: Backup**
```bash
# Full database backup
pg_dump cotton_erp > backup_pre_cdps_$(date +%Y%m%d_%H%M%S).sql

# Backup size check
ls -lh backup_pre_cdps_*.sql

# Backup verification
pg_restore --list backup_pre_cdps_*.sql | head -20
```

**Step 2: Run Migration**
```bash
cd backend
alembic upgrade head

# Migration output:
# INFO  [alembic.runtime.migration] Running upgrade xxx -> YYYYMMDD_add_capability_system
# INFO  [alembic.runtime.migration] Adding new columns...
# INFO  [alembic.runtime.migration] Migrating data (0/1250 partners)...
# INFO  [alembic.runtime.migration] Migrating data (500/1250 partners)...
# INFO  [alembic.runtime.migration] Migrating data (1000/1250 partners)...
# INFO  [alembic.runtime.migration] Migrating data (1250/1250 partners) DONE
# INFO  [alembic.runtime.migration] Adding indexes...
# INFO  [alembic.runtime.migration] Dropping old columns...
# INFO  [alembic.runtime.migration] Migration complete!
```

**Step 3: Verify Data**
```sql
-- Check all partners migrated
SELECT COUNT(*) FROM business_partners WHERE capabilities IS NULL;
-- Expected: 0

-- Check service providers
SELECT 
    service_provider_type, 
    COUNT(*) 
FROM business_partners 
WHERE is_service_provider = true 
GROUP BY service_provider_type;

-- Expected:
-- broker: 120
-- transporter: 200
-- controller: 50
-- etc.

-- Check capabilities
SELECT 
    capabilities->>'domestic_buy' as can_buy,
    capabilities->>'domestic_sell' as can_sell,
    COUNT(*)
FROM business_partners
WHERE is_service_provider = false
GROUP BY capabilities->>'domestic_buy', capabilities->>'domestic_sell';

-- Expected:
-- true, false: 380 (old buyers)
-- false, true: 450 (old sellers)
-- true, true: 200 (old traders)
```

---

#### 4.3 Post-Migration State

**Database:**
```sql
-- New columns
business_partners:
  - is_service_provider: boolean
  - service_provider_type: varchar(50) | null
  - business_entity_type: varchar(50) | null
  - capabilities: jsonb
  - master_entity_id: uuid | null
  - corporate_group_id: uuid | null
  - is_master_entity: boolean
  - entity_hierarchy: jsonb

-- Converted data (example)
id: 550e8400-e29b-41d4-a716-446655440000
is_service_provider: false
service_provider_type: null
business_entity_type: 'private_limited'
capabilities: {
    "domestic_buy": false,
    "domestic_sell": true,
    "import_allowed": false,
    "export_allowed": false,
    "auto_detected": false,
    "detected_from_documents": ["legacy_migration"],
    "detected_at": null,
    "manual_override": false,
    "override_reason": "Migrated from seller type"
}
```

**Code:**
```python
# New usage
partner = await repo.get_by_id(partner_id)
if partner.capabilities.get("domestic_sell", False):
    # Can sell logic
```

---

#### 4.4 Rollback Strategy

**If migration fails or needs rollback:**
```bash
# Rollback migration
cd backend
alembic downgrade -1

# Rollback output:
# INFO  [alembic.runtime.migration] Running downgrade YYYYMMDD_add_capability_system -> xxx
# INFO  [alembic.runtime.migration] Re-adding old columns...
# INFO  [alembic.runtime.migration] Reconstructing partner_type from capabilities...
# INFO  [alembic.runtime.migration] Dropping new columns...
# INFO  [alembic.runtime.migration] Rollback complete!
```

**Verify Rollback:**
```sql
-- Check partner_type restored
SELECT partner_type, COUNT(*) 
FROM business_partners 
GROUP BY partner_type;

-- Expected: Original counts
-- seller: 450
-- buyer: 380
-- trader: 200
-- broker: 120
-- etc.

-- Check no data loss
SELECT COUNT(*) FROM business_partners;
-- Expected: Same count as before migration
```

**Alternative: Restore from Backup**
```bash
# If rollback doesn't work, restore from backup
dropdb cotton_erp
createdb cotton_erp
pg_restore -d cotton_erp backup_pre_cdps_*.sql
```

---

#### 4.5 Data Integrity Guarantees

**Guarantee 1: No Data Loss**
```sql
-- Verification query (run before and after)
SELECT 
    COUNT(*) as total_partners,
    COUNT(DISTINCT id) as unique_ids,
    COUNT(*) - COUNT(DISTINCT id) as duplicates
FROM business_partners;

-- Before: total=1250, unique=1250, duplicates=0
-- After: total=1250, unique=1250, duplicates=0
-- ✅ SAME
```

**Guarantee 2: All Relationships Preserved**
```sql
-- Check foreign key integrity
SELECT 
    COUNT(*) as total_documents,
    COUNT(DISTINCT partner_id) as partners_with_docs
FROM partner_documents;

-- Before and After: SAME
```

**Guarantee 3: Capability Mapping Accuracy**
```sql
-- Verify seller → domestic_sell capability
-- (run this BEFORE migration with partner_type='seller')
CREATE TEMP TABLE pre_migration_sellers AS
SELECT id FROM business_partners WHERE partner_type = 'seller';

-- (run this AFTER migration)
SELECT COUNT(*)
FROM pre_migration_sellers p
JOIN business_partners bp ON p.id = bp.id
WHERE bp.capabilities->>'domestic_sell' = 'false';

-- Expected: 0 (all sellers have domestic_sell=true)
```

---

### APPROVAL SECTION 5: Testing Strategy - 13 New Tests

#### 5.1 Capability Detection Tests (5 tests)

**Test 1: Indian Domestic Detection**
```python
async def test_indian_domestic_capability_detection(db, partner_id):
    """
    Given: Partner with GST + PAN documents (both verified)
    When: Capability detection runs
    Then: domestic_buy=True, domestic_sell=True
    """
    # Arrange
    partner = create_partner(country="India")
    upload_document(partner.id, "gst_certificate", verified=True)
    upload_document(partner.id, "pan_card", verified=True)
    
    # Act
    service = CapabilityDetectionService(db, emitter)
    result = await service.update_partner_capabilities(partner.id)
    
    # Assert
    assert result.capabilities["domestic_buy"] == True
    assert result.capabilities["domestic_sell"] == True
    assert result.capabilities["import_allowed"] == False
    assert result.capabilities["export_allowed"] == False
    assert "GST" in result.capabilities["detected_from_documents"]
    assert "PAN" in result.capabilities["detected_from_documents"]
```

**Test 2: Indian IEC Detection**
```python
async def test_indian_iec_capability_detection(db, partner_id):
    """
    Given: Partner with GST + PAN + IEC documents (all verified)
    When: Capability detection runs
    Then: All capabilities = True
    """
    # Arrange
    partner = create_partner(country="India")
    upload_document(partner.id, "gst_certificate", verified=True)
    upload_document(partner.id, "pan_card", verified=True)
    upload_document(partner.id, "iec", verified=True)
    
    # Act
    service = CapabilityDetectionService(db, emitter)
    result = await service.update_partner_capabilities(partner.id)
    
    # Assert
    assert result.capabilities["domestic_buy"] == True
    assert result.capabilities["domestic_sell"] == True
    assert result.capabilities["import_allowed"] == True
    assert result.capabilities["export_allowed"] == True
    assert "IEC" in result.capabilities["detected_from_documents"]
```

**Test 3: Foreign Domestic Detection**
```python
async def test_foreign_domestic_capability_detection(db, partner_id):
    """
    Given: Foreign partner with Tax ID + Business Registration
    When: Capability detection runs
    Then: domestic_buy=True, domestic_sell=True (in their country)
    """
    # Arrange
    partner = create_partner(country="USA")
    upload_document(partner.id, "foreign_tax_id", verified=True)
    upload_document(partner.id, "business_registration", verified=True)
    
    # Act
    service = CapabilityDetectionService(db, emitter)
    result = await service.update_partner_capabilities(partner.id)
    
    # Assert
    assert result.capabilities["domestic_buy"] == True
    assert result.capabilities["domestic_sell"] == True
    assert result.capabilities["import_allowed"] == False
    assert result.capabilities["export_allowed"] == False
```

**Test 4: Foreign Import License**
**Test 5: Foreign Export License**
(Similar structure)

---

#### 5.2 Insider Trading Tests (5 tests)

**Test 1: Same Entity Blocked**
```python
async def test_insider_trading_same_entity_blocked(db):
    """
    Given: Same partner trying to buy and sell to themselves
    When: validate_trade_parties called
    Then: Blocked with SAME_ENTITY violation
    """
    # Arrange
    partner_id = create_partner()
    validator = InsiderTradingValidator(db)
    
    # Act
    result = await validator.validate_trade_parties(
        buyer_id=partner_id,
        seller_id=partner_id,
        db=db
    )
    
    # Assert
    assert result["allowed"] == False
    assert result["violation_type"] == "SAME_ENTITY"
    assert "cannot trade with yourself" in result["reason"].lower()
```

**Test 2: Master-Branch Blocked**
```python
async def test_insider_trading_master_branch_blocked(db):
    """
    Given: Master entity and its branch
    When: They try to trade
    Then: Blocked with MASTER_BRANCH_TRADING violation
    """
    # Arrange
    master = create_partner(is_master_entity=True)
    branch = create_partner(
        is_master_entity=False,
        master_entity_id=master.id
    )
    validator = InsiderTradingValidator(db)
    
    # Act
    result = await validator.validate_trade_parties(
        buyer_id=master.id,
        seller_id=branch.id,
        db=db
    )
    
    # Assert
    assert result["allowed"] == False
    assert result["violation_type"] == "MASTER_BRANCH_TRADING"
```

**Test 3: Sibling Branches Blocked**
```python
async def test_insider_trading_sibling_branches_blocked(db):
    """
    Given: Two branches with same master_entity_id
    When: They try to trade
    Then: Blocked with SIBLING_BRANCH_TRADING violation
    """
    # Arrange
    master = create_partner(is_master_entity=True)
    branch1 = create_partner(master_entity_id=master.id)
    branch2 = create_partner(master_entity_id=master.id)
    validator = InsiderTradingValidator(db)
    
    # Act
    result = await validator.validate_trade_parties(
        buyer_id=branch1.id,
        seller_id=branch2.id,
        db=db
    )
    
    # Assert
    assert result["allowed"] == False
    assert result["violation_type"] == "SIBLING_BRANCH_TRADING"
```

**Test 4: Corporate Group Blocked**
**Test 5: Parent-Subsidiary Blocked**
(Similar structure)

---

#### 5.3 Trade Desk Capability Tests (3 tests)

**Test 1: Service Provider Cannot Post Availability**
```python
async def test_service_provider_cannot_post_availability(db):
    """
    Given: Partner is service provider (broker)
    When: Try to post availability
    Then: Raises ValueError with specific message
    """
    # Arrange
    broker = create_partner(
        is_service_provider=True,
        service_provider_type="broker"
    )
    availability_service = AvailabilityService(db)
    
    # Act & Assert
    with pytest.raises(ValueError) as exc:
        await availability_service._validate_seller_capabilities(broker.id)
    
    assert "service providers cannot post availabilities" in str(exc.value).lower()
    assert "broker" in str(exc.value).lower()
```

**Test 2: No Buy Capability Cannot Post Requirement**
```python
async def test_no_buy_capability_cannot_post_requirement(db):
    """
    Given: Partner with domestic_buy=False
    When: Try to post requirement
    Then: Raises ValueError
    """
    # Arrange
    partner = create_partner(
        is_service_provider=False,
        capabilities={"domestic_buy": False, "domestic_sell": True, ...}
    )
    requirement_service = RequirementService(db)
    
    # Act & Assert
    with pytest.raises(ValueError) as exc:
        await requirement_service._validate_buyer_capabilities(partner.id)
    
    assert "does not have domestic_buy capability" in str(exc.value).lower()
```

**Test 3: Valid Partners Can Match**
```python
async def test_valid_unrelated_partners_can_match(db):
    """
    Given: Two unrelated partners with proper capabilities
    When: Matching validation runs
    Then: Match is allowed
    """
    # Arrange
    buyer = create_partner(
        capabilities={"domestic_buy": True, ...}
    )
    seller = create_partner(
        capabilities={"domestic_sell": True, ...}
    )
    requirement = create_requirement(business_partner_id=buyer.id)
    availability = create_availability(business_partner_id=seller.id)
    validator = MatchValidator(db, risk_engine, config)
    
    # Act
    result = await validator.validate_match_eligibility(
        requirement, availability
    )
    
    # Assert
    assert result.is_valid == True
    assert len(result.reasons) == 0
```

---

### APPROVAL SECTION 6: Risk Mitigation

#### 6.1 Rollback Plan

**Trigger Conditions:**
- Migration fails (data corruption)
- >10% tests failing post-migration
- Critical production issue within 24 hours
- Data integrity check fails

**Rollback Steps:**
1. Stop all services (30 seconds)
2. Run `alembic downgrade -1` (2 minutes)
3. Verify rollback with SQL checks (1 minute)
4. Restart services (30 seconds)
5. **Total Downtime:** <5 minutes

**Alternative (if alembic rollback fails):**
1. Restore from backup (5-10 minutes depending on DB size)

---

#### 6.2 Testing in Stages

**Stage 1: Local Development**
- Run migration on local DB
- Run all 13 new tests
- Run existing test suite
- Manual testing of flows

**Stage 2: Staging Environment**
- Deploy to staging
- Run migration on staging DB (copy of production)
- Full regression testing
- User acceptance testing (UAT)

**Stage 3: Production (Blue-Green)**
- Deploy to blue environment
- Run migration
- Smoke tests
- Switch traffic to blue
- Monitor for 24 hours
- If issues: switch back to green (instant rollback)

---

### 📝 FINAL APPROVAL CHECKLIST

**Technical Approval:**
- [ ] **Database Schema**: Approve new columns and migration strategy
- [ ] **Data Migration**: Approve conversion logic (partner_type → capabilities)
- [ ] **Breaking Changes**: Acknowledge 4 breaking changes (all mitigated)
- [ ] **Service Providers**: Confirm no changes to broker/transporter/controller flows
- [ ] **KYC Flows**: Confirm no changes to renewal/reminder/auto-suspend
- [ ] **Back-Office**: Confirm filters/exports/dashboard continue working
- [ ] **Timeline**: Approve 8-10 working days

**Business Approval:**
- [ ] **Benefits**: Approve capability-based flexibility
- [ ] **Insider Trading**: Approve 6 blocking rules
- [ ] **Auto-Detection**: Approve document-driven capability detection
- [ ] **Risk**: Approve rollback strategy

**Resource Approval:**
- [ ] **Developer Time**: 64 hours (8 days)
- [ ] **Testing Time**: 16 hours (2 days)
- [ ] **Total**: 10 working days allocated

**Deployment Approval:**
- [ ] **Staging Deployment**: Week of [DATE]
- [ ] **Production Deployment**: Week of [DATE]
- [ ] **Backup Strategy**: Approved
- [ ] **Rollback Plan**: Approved

---

## ✅ APPROVAL SIGNATURE

**Approved By:** ___________________________  
**Title:** ___________________________  
**Date:** ___________________________  
**Signature:** ___________________________

**Implementation Start Date:** ___________________________  
**Expected Completion Date:** ___________________________

---

**Document Status:** 🔴 AWAITING APPROVAL  
**Last Updated:** November 28, 2025  
**Version:** 2.0 - Detailed for Approval
