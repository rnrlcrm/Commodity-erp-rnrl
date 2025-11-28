# CAPABILITY-DRIVEN PARTNER SYSTEM (CDPS)
## FINAL IMPLEMENTATION PLAN - CORRECTED VERSION

**Date:** November 28, 2025  
**Status:** 🟢 READY FOR APPROVAL  
**Estimated Duration:** 10 working days (12 days with deployment)  
**Files to Modify:** 21 files  
**Lines of Code:** +2,568 / -313 (Net: +2,255)  
**Resource Requirement:** 3 developers, 96 hours

---

## 1. 🎯 EXECUTIVE SUMMARY

### The Problem We're Solving

**Current Architecture Issues:**
- **Confusion:** Rigid roles (Buyer, Seller, Trader) don't match real business needs
- **Inflexibility:** Same entity cannot buy AND sell without "Trader" role
- **Non-compliance:** Missing enforcement of Indian trade regulations (IEC requires GST+PAN)
- **Security Risk:** No insider trading prevention between related entities
- **Scalability:** Cannot handle foreign entities or complex corporate structures

**Real-World Example:**
```
ABC Ginning Ltd wants to:
1. Buy raw cotton from farmers (needs "buyer" role)
2. Sell processed cotton to mills (needs "seller" role)
3. Export to Bangladesh (needs "exporter" role)

Current System: Must be marked as "Trader" + "Exporter" 
Problem: Confusing, doesn't reflect actual capabilities
```

### The Solution: Document-Driven Capability System

**New Architecture Philosophy:**
> **Capabilities are GRANTED dynamically based on verified compliance documents, not assigned as static roles.**

**Example:**
```
ABC Ginning Ltd uploads:
✅ GST Certificate (verified) → Grants domestic_buy_india + domestic_sell_india
✅ PAN Card (verified)        → Required for domestic trade
✅ IEC Certificate (verified) → Grants import_allowed + export_allowed

Result: Partner can now buy, sell, import, export based on ACTUAL documents, not manual role assignment.
```

### Core Benefits

#### 1. **Dynamic & Document-Driven**
- Capabilities auto-detected from verified documents
- No manual role assignment confusion
- Audit trail of what documents granted which capabilities

#### 2. **Legally Compliant**
- **Indian Law Enforcement:** IEC MUST have GST+PAN (strict validation)
- **Foreign Entity Separation:** Foreign companies can only trade in home country
- **Insider Trading Prevention:** 4 blocking rules prevent circular trading

#### 3. **Future-Proof Architecture**
- Scales to ANY commodity, ANY country
- Support for complex corporate structures (parent/subsidiary/branches)
- No hardcoded business logic

#### 4. **Zero Breaking Changes**
- **Service Providers:** Broker, Transporter, Controller flows UNCHANGED
- **KYC Workflows:** Renewal, reminders, auto-suspend UNCHANGED
- **Back-Office:** Filters, exports, dashboard UNCHANGED (enhanced)
- **AI Assistant:** Onboarding guidance UNCHANGED (enhanced)
- **Risk Scoring:** Calculation logic UNCHANGED

### What Changes (Technical)

**REMOVE (Old System):**
```python
# ❌ DELETE these rigid roles
partner_type = Enum("seller", "buyer", "trader", "importer", "exporter", ...)
trade_classification = Enum("domestic", "importer", "exporter")
is_buyer = Boolean
is_seller = Boolean
is_trader = Boolean
```

**ADD (New System):**
```python
# ✅ ADD flexible capability system
entity_class = Enum("business_entity", "service_provider")

# If business_entity:
capabilities = JSONB({
    "domestic_buy_india": false,
    "domestic_sell_india": false,
    "domestic_buy_home_country": false,
    "domestic_sell_home_country": false,
    "import_allowed": false,
    "export_allowed": false,
    "auto_detected": false,
    "detected_from_documents": [],
    "manual_override": false,
    "override_reason": null
})

# If service_provider:
service_provider_type = Enum("broker", "transporter", "controller", ...)
```

### What Stays the Same (Zero Changes)

#### ✅ Service Provider Logic - 100% UNCHANGED
```python
# Broker onboarding
if entity_class == "service_provider" and service_provider_type == "broker":
    # ✅ Same documents (GST, PAN)
    # ✅ Same validation (no license required)
    # ✅ Same commission structure
    # ✅ Same approval flow
    # ONLY CHANGE: Step 1 question ("Service Provider or Business Entity?")
```

#### ✅ KYC Flows - 100% UNCHANGED
- KYC renewal (365 days) - Same logic
- KYC reminders (90/60/30/7 days) - Same schedule
- Auto-suspend - Same triggers
- Document verification - Enhanced with capability detection

#### ✅ Back-Office Features - 100% BACKWARD COMPATIBLE
- Filters work the same (enhanced with new capability filters)
- Exports work the same (cosmetic column name changes)
- Dashboard works the same (enhanced with new stats)
- Notifications work the same (cosmetic template updates)

#### ✅ AI Assistant - 100% UNCHANGED
- Same onboarding guidance
- Same document suggestions
- Same timeline estimates
- Enhanced with capability-aware recommendations

#### ✅ Risk Scoring - 100% UNCHANGED
- Same scoring algorithm
- Same risk factors
- Enhanced with capability validation

---

## 2. 🧱 ARCHITECTURE - FINAL MODEL

### A. Two-Tier Entity Classification

**Top Level: Entity Class**
```python
entity_class = Enum("business_entity", "service_provider")
```

**Business Entity Types (10 values):**
```python
business_entity_type = Enum(
    "proprietorship",      # Individual proprietor
    "partnership",         # Partnership firm
    "llp",                # Limited Liability Partnership
    "private_limited",    # Private Limited Company (most common)
    "public_limited",     # Public Limited Company
    "trust",              # Charitable/Religious Trust
    "society",            # Society/NGO
    "llc",                # Limited Liability Company (foreign)
    "corporation",        # Corporation (foreign)
    "foreign_entity"      # Other foreign entity
)
```

**Service Provider Types (6 values):**
```python
service_provider_type = Enum(
    "broker",             # Commission agent for buyers/sellers
    "sub_broker",         # Works under main broker
    "transporter",        # Lorry owner or transport agent
    "controller",         # Quality control/inspection
    "financer",           # Financing services
    "shipping_agent"      # Export/import shipping
)
```

### B. Capability Model (JSONB)

**Capability Structure:**
```json
{
  // INDIAN ENTITIES ONLY
  "domestic_buy_india": false,
  "domestic_sell_india": false,
  
  // FOREIGN ENTITIES ONLY
  "domestic_buy_home_country": false,
  "domestic_sell_home_country": false,
  
  // INTERNATIONAL (BOTH INDIAN & FOREIGN)
  "import_allowed": false,
  "export_allowed": false,
  
  // METADATA (AUTO-GENERATED)
  "auto_detected": false,
  "detected_from_documents": [],
  "detected_at": null,
  "manual_override": false,
  "override_reason": null,
  "last_detection_run": null
}
```

### C. Removed Legacy Fields

**DELETE these columns:**
```python
# ❌ REMOVE - Replaced by entity_class + capabilities
partner_type = Column(Enum(PartnerType))
trade_classification = Column(Enum(TradeClassification))
is_buyer = Column(Boolean)
is_seller = Column(Boolean)
is_trader = Column(Boolean)
```

**Migration Strategy:** All data preserved, converted to capabilities during migration.

---

## 3. 🔐 CAPABILITY DETECTION SERVICE - FINAL RULES

### Overview

**Core Principle:**
> Capabilities are GRANTED based on verified compliance documents, NOT manually assigned.

**Detection Trigger Points:**
1. Document verification (OCR + manual review)
2. Partner approval (final onboarding approval)
3. Manual override by admin (with audit trail)
4. Scheduled re-detection job (nightly)

### Rule A: Indian Domestic Capability

**Requirement:** GST Certificate + PAN Card (both verified)

**Logic:**
```python
async def detect_indian_domestic_capability(partner_id: UUID) -> dict:
    """
    Grants domestic trading rights inside India.
    Requires: GST + PAN both verified.
    """
    docs = await get_verified_documents(partner_id)
    
    has_gst = any(d.document_type == "gst_certificate" and d.verification_status == "verified" for d in docs)
    has_pan = any(d.document_type == "pan_card" and d.verification_status == "verified" for d in docs)
    
    if has_gst and has_pan:
        return {
            "domestic_buy_india": True,
            "domestic_sell_india": True,
            "detected_from_documents": ["GST", "PAN"],
            "auto_detected": True,
            "detected_at": datetime.utcnow()
        }
    
    return {
        "domestic_buy_india": False,
        "domestic_sell_india": False
    }
```

**Example Result:**
```json
{
  "domestic_buy_india": true,
  "domestic_sell_india": true,
  "import_allowed": false,
  "export_allowed": false,
  "detected_from_documents": ["GST", "PAN"],
  "auto_detected": true,
  "detected_at": "2025-11-28T10:30:00Z"
}
```

**Business Impact:**
- Indian companies can buy AND sell domestically with single document set
- No need for "Trader" role - capability-based
- Automatic grant upon document verification

### Rule B: Indian Import/Export (STRICT VALIDATION)

**Critical Rule:** 🔥 **IEC ALONE IS NOT SUFFICIENT**

**Requirement:** IEC + GST + PAN (all three verified)

**Logic:**
```python
async def detect_import_export_capability(partner_id: UUID) -> dict:
    """
    Grants import/export rights.
    
    CRITICAL: IEC must be accompanied by GST + PAN.
    IEC alone = NO import/export capability.
    """
    docs = await get_verified_documents(partner_id)
    
    has_gst = any(d.document_type == "gst_certificate" and d.verification_status == "verified" for d in docs)
    has_pan = any(d.document_type == "pan_card" and d.verification_status == "verified" for d in docs)
    has_iec = any(d.document_type == "iec" and d.verification_status == "verified" for d in docs)
    
    # ALL THREE REQUIRED
    if has_iec and has_gst and has_pan:
        return {
            "import_allowed": True,
            "export_allowed": True,
            "detected_from_documents": ["IEC", "GST", "PAN"],
            "auto_detected": True,
            "detected_at": datetime.utcnow()
        }
    
    # If IEC exists but GST or PAN missing → DENY
    if has_iec and (not has_gst or not has_pan):
        logger.warning(f"Partner {partner_id} has IEC but missing GST/PAN - import/export DENIED")
        return {
            "import_allowed": False,
            "export_allowed": False,
            "detected_from_documents": ["IEC_INCOMPLETE"]
        }
    
    return {
        "import_allowed": False,
        "export_allowed": False
    }
```

**Example Results:**

✅ **Valid Importer/Exporter:**
```json
{
  "domestic_buy_india": true,
  "domestic_sell_india": true,
  "import_allowed": true,
  "export_allowed": true,
  "detected_from_documents": ["GST", "PAN", "IEC"],
  "auto_detected": true
}
```

❌ **Invalid (IEC without GST/PAN):**
```json
{
  "domestic_buy_india": false,
  "domestic_sell_india": false,
  "import_allowed": false,
  "export_allowed": false,
  "detected_from_documents": ["IEC_INCOMPLETE"],
  "auto_detected": false
}
```

**Compliance Reasoning:**
- Indian law requires GST registration for business entities
- PAN is mandatory for all financial transactions
- IEC without GST/PAN indicates incomplete compliance
- System enforces legal requirements automatically

### Rule C: Foreign Domestic Capability

**Critical Rule:** 🌍 **Foreign entities can trade ONLY inside their home country**

**Requirement:** Foreign Tax ID (verified)

**Logic:**
```python
async def detect_foreign_domestic_capability(partner_id: UUID) -> dict:
    """
    Grants domestic trading rights in THEIR home country.
    Requires: Foreign Tax ID verified.
    
    IMPORTANT: Foreign entities CANNOT trade domestically in India
    unless they establish an Indian legal entity with GST+PAN.
    """
    docs = await get_verified_documents(partner_id)
    partner = await get_partner(partner_id)
    
    has_foreign_tax_id = any(
        d.document_type == "foreign_tax_id" and 
        d.verification_status == "verified" 
        for d in docs
    )
    
    if has_foreign_tax_id and partner.country != "India":
        return {
            "domestic_buy_home_country": True,
            "domestic_sell_home_country": True,
            "domestic_buy_india": False,        # ❌ Cannot trade in India
            "domestic_sell_india": False,       # ❌ Cannot trade in India
            "detected_from_documents": ["FOREIGN_TAX_ID"],
            "auto_detected": True,
            "detected_at": datetime.utcnow()
        }
    
    return {
        "domestic_buy_home_country": False,
        "domestic_sell_home_country": False
    }
```

**Example Result (USA Company):**
```json
{
  "domestic_buy_india": false,
  "domestic_sell_india": false,
  "domestic_buy_home_country": true,
  "domestic_sell_home_country": true,
  "import_allowed": false,
  "export_allowed": false,
  "detected_from_documents": ["FOREIGN_TAX_ID"],
  "home_country": "USA"
}
```

**Business Impact:**
- Foreign companies can trade in their home country
- Cannot circumvent Indian regulations by trading domestically without Indian entity
- Clear separation of domestic vs international operations

### Rule D: Foreign Import/Export

**Requirement:** Foreign Import License OR Foreign Export License (verified)

**Logic:**
```python
async def detect_foreign_import_export_capability(partner_id: UUID) -> dict:
    """
    Grants import/export rights for foreign entities.
    Requires: Foreign import/export licenses.
    """
    docs = await get_verified_documents(partner_id)
    
    has_import_license = any(
        d.document_type == "foreign_import_license" and 
        d.verification_status == "verified" 
        for d in docs
    )
    
    has_export_license = any(
        d.document_type == "foreign_export_license" and 
        d.verification_status == "verified" 
        for d in docs
    )
    
    result = {}
    detected_docs = []
    
    if has_import_license:
        result["import_allowed"] = True
        detected_docs.append("FOREIGN_IMPORT_LICENSE")
    else:
        result["import_allowed"] = False
    
    if has_export_license:
        result["export_allowed"] = True
        detected_docs.append("FOREIGN_EXPORT_LICENSE")
    else:
        result["export_allowed"] = False
    
    if detected_docs:
        result["detected_from_documents"] = detected_docs
        result["auto_detected"] = True
        result["detected_at"] = datetime.utcnow()
    
    return result
```

**Example Result (Foreign Exporter Only):**
```json
{
  "domestic_buy_home_country": true,
  "domestic_sell_home_country": true,
  "import_allowed": false,
  "export_allowed": true,
  "detected_from_documents": ["FOREIGN_TAX_ID", "FOREIGN_EXPORT_LICENSE"]
}
```

### Rule E: Service Provider Blocking

**Critical Rule:** 🚫 **Service providers CANNOT trade**

**Logic:**
```python
async def update_partner_capabilities(partner_id: UUID) -> BusinessPartner:
    """
    Main entry point: Detect and update capabilities.
    """
    partner = await self.repo.get_by_id(partner_id)
    
    # Service providers cannot trade
    if partner.entity_class == "service_provider":
        capabilities = {
            "domestic_buy_india": False,
            "domestic_sell_india": False,
            "domestic_buy_home_country": False,
            "domestic_sell_home_country": False,
            "import_allowed": False,
            "export_allowed": False,
            "detected_from_documents": ["SERVICE_PROVIDER_NO_TRADING"],
            "auto_detected": True
        }
        await self.repo.update_capabilities(partner_id, capabilities)
        return partner
    
    # Business entities: Run detection
    # ... detection logic ...
```

**Business Impact:**
- Brokers, transporters, controllers cannot buy/sell
- Clear separation of service vs trading entities
- Prevents regulatory issues

---

## 4. 🚫 INSIDER TRADING PREVENTION RULES

### Overview

**Purpose:** Prevent circular trading within related business entities to ensure:
- Market integrity
- Compliance with anti-money laundering (AML) regulations
- Fair pricing (no artificial price manipulation)
- Tax compliance (no transfer pricing abuse)

**Implementation:** InsiderTradingValidator class with 4 blocking rules

### Blocking Rule 1: Same Entity Trading

**Block:** Same partner trading with themselves

**Logic:**
```python
if buyer_id == seller_id:
    return {
        "allowed": False,
        "violation_type": "SAME_ENTITY",
        "reason": "Cannot trade with yourself"
    }
```

**Example:**
```
ABC Ginning Ltd (buyer) ↔ ABC Ginning Ltd (seller)
❌ BLOCKED: Same entity ID
```

### Blocking Rule 2: Master-Branch Trading

**Block:** Master entity trading with its branches OR sibling branches trading

**Logic:**
```python
# Master → Branch
if buyer.is_master_entity and seller.master_entity_id == buyer_id:
    return {
        "allowed": False,
        "violation_type": "MASTER_BRANCH_TRADING",
        "reason": "Cannot trade between master entity and its branch"
    }

# Sibling Branches
if buyer.master_entity_id and seller.master_entity_id:
    if buyer.master_entity_id == seller.master_entity_id:
        return {
            "allowed": False,
            "violation_type": "SIBLING_BRANCH_TRADING",
            "reason": "Cannot trade between branches of same master entity"
        }
```

**Example:**
```
ABC Ginning Ltd (Master)
├── ABC Branch Mumbai (Branch 1)
└── ABC Branch Delhi (Branch 2)

❌ BLOCKED:
- ABC Master ↔ ABC Mumbai
- ABC Master ↔ ABC Delhi
- ABC Mumbai ↔ ABC Delhi
```

### Blocking Rule 3: Corporate Group Trading

**Block:** Trading within same corporate group (parent/subsidiary/sister companies)

**Logic:**
```python
if buyer.corporate_group_id and seller.corporate_group_id:
    if buyer.corporate_group_id == seller.corporate_group_id:
        return {
            "allowed": False,
            "violation_type": "CORPORATE_GROUP_TRADING",
            "reason": "Cannot trade within same corporate group"
        }
```

**Example:**
```
XYZ Group (corporate_group_id: abc-123)
├── XYZ Ginning Pvt Ltd
├── XYZ Trading Pvt Ltd
└── XYZ Exports Pvt Ltd

❌ BLOCKED: Any trade between these 3 companies
```

### Blocking Rule 4: Same GST Trading (India Only)

**Block:** Trading between entities with same GST number

**Logic:**
```python
if buyer.country == "India" and seller.country == "India":
    buyer_gst = await self._get_gst_number(buyer_id)
    seller_gst = await self._get_gst_number(seller_id)
    if buyer_gst and seller_gst and buyer_gst == seller_gst:
        return {
            "allowed": False,
            "violation_type": "SAME_GST_GROUP",
            "reason": "Cannot trade between entities with same GST number"
        }
```

**Example:**
```
GST: 29ABCDE1234F1Z5
├── ABC Factory
└── ABC Warehouse

❌ BLOCKED: Same GST = same legal entity
```

### Integration in Trade Desk

**Matching Validation:**
```python
async def validate_match_eligibility(requirement, availability) -> ValidationResult:
    """
    Validates if requirement and availability can match.
    """
    # 1. Insider trading check
    insider_check = await self.insider_validator.validate_trade_parties(
        buyer_id=requirement.business_partner_id,
        seller_id=availability.business_partner_id,
        db=self.db
    )
    
    if not insider_check["allowed"]:
        reasons.append(
            f"Insider trading violation: {insider_check['violation_type']} - "
            f"{insider_check['reason']}"
        )
    
    # 2. Other validations...
    
    return ValidationResult(
        is_valid=len(reasons) == 0,
        reasons=reasons
    )
```

**Business Impact:**
- Prevents price manipulation
- Ensures fair market operations
- Compliance with regulations
- Clear audit trail

---

## 5. 🌍 TRADE DESK - LOCATION-AWARE VALIDATION

### Overview

**Principle:** Validation logic must check capabilities based on WHERE the trade is happening.

**Example:**
- Indian partner posting availability in India → requires `domestic_sell_india`
- Foreign partner posting availability in their country → requires `domestic_sell_home_country`
- Any partner exporting → requires `export_allowed`

### Availability Posting (Seller Side)

**Validation Logic:**

---

## 📋 CORRECTED ARCHITECTURE SPECIFICATION

### 1. ENTITY CLASSIFICATION (NO CHANGE)

```python
# Two-tier classification
entity_class = Enum("business_entity", "service_provider")

# If business_entity:
business_entity_type = Enum(
    "proprietorship", "partnership", "llp", 
    "private_limited", "public_limited", 
    "trust", "society", "llc", "corporation", "foreign_entity"
)

# If service_provider:
service_provider_type = Enum(
    "broker", "sub_broker", "transporter", 
    "controller", "financer", "shipping_agent"
)
```

---

### 2. REMOVED FIELDS (NO CHANGE)

**DELETE these columns:**
- `partner_type` (old enum)
- `trade_classification` (old enum)
- `is_buyer` (old boolean)
- `is_seller` (old boolean)
- `is_trader` (old boolean)

---

### 3. NEW CAPABILITIES STRUCTURE (UPDATED)

**ADD this column:**
```python
capabilities = Column(JSONB, nullable=False, default={})
```

**Capability Schema:**
```json
{
  // INDIAN ENTITIES
  "domestic_buy_india": false,
  "domestic_sell_india": false,
  
  // FOREIGN ENTITIES
  "domestic_buy_home_country": false,
  "domestic_sell_home_country": false,
  
  // INTERNATIONAL (BOTH INDIAN & FOREIGN)
  "import_allowed": false,
  "export_allowed": false,
  
  // METADATA
  "auto_detected": false,
  "detected_from_documents": [],
  "detected_at": null,
  "manual_override": false,
  "override_reason": null,
  "last_detection_run": null
}
```

---

### 4. CAPABILITY DETECTION RULES (CORRECTED)

#### 🇮🇳 RULE A: INDIAN DOMESTIC TRADING

**Requirement:** GST Certificate + PAN Card (both verified)

**Logic:**
```python
async def detect_indian_domestic_capability(partner_id: UUID) -> dict:
    """
    Grants domestic trading rights in India.
    Requires: GST + PAN both verified.
    """
    docs = await get_verified_documents(partner_id)
    
    has_gst = any(d.document_type == "gst_certificate" and d.verification_status == "verified" for d in docs)
    has_pan = any(d.document_type == "pan_card" and d.verification_status == "verified" for d in docs)
    
    if has_gst and has_pan:
        return {
            "domestic_buy_india": True,
            "domestic_sell_india": True,
            "detected_from_documents": ["GST", "PAN"],
            "auto_detected": True,
            "detected_at": datetime.utcnow()
        }
    
    return {
        "domestic_buy_india": False,
        "domestic_sell_india": False
    }
```

**Example Result:**
```json
{
  "domestic_buy_india": true,
  "domestic_sell_india": true,
  "import_allowed": false,
  "export_allowed": false,
  "detected_from_documents": ["GST", "PAN"]
}
```

---

#### 🌍 RULE B: IMPORT/EXPORT (STRONG VALIDATION)

**Critical Rule:** IEC ALONE is NOT sufficient. Must have GST + PAN + IEC.

**Requirement:** IEC + GST + PAN (all three verified)

**Logic:**
```python
async def detect_import_export_capability(partner_id: UUID) -> dict:
    """
    Grants import/export rights.
    
    STRONG RULE: IEC must be accompanied by GST + PAN.
    IEC alone = NO import/export capability.
    """
    docs = await get_verified_documents(partner_id)
    
    has_gst = any(d.document_type == "gst_certificate" and d.verification_status == "verified" for d in docs)
    has_pan = any(d.document_type == "pan_card" and d.verification_status == "verified" for d in docs)
    has_iec = any(d.document_type == "iec" and d.verification_status == "verified" for d in docs)
    
    # ALL THREE REQUIRED
    if has_iec and has_gst and has_pan:
        return {
            "import_allowed": True,
            "export_allowed": True,
            "detected_from_documents": ["IEC", "GST", "PAN"],
            "auto_detected": True,
            "detected_at": datetime.utcnow()
        }
    
    # If IEC exists but GST or PAN missing → DENY
    if has_iec and (not has_gst or not has_pan):
        logger.warning(f"Partner {partner_id} has IEC but missing GST/PAN - import/export DENIED")
        return {
            "import_allowed": False,
            "export_allowed": False,
            "detected_from_documents": ["IEC_INCOMPLETE"]
        }
    
    return {
        "import_allowed": False,
        "export_allowed": False
    }
```

**Example Results:**

✅ **Valid Indian Importer/Exporter:**
```json
{
  "domestic_buy_india": true,
  "domestic_sell_india": true,
  "import_allowed": true,
  "export_allowed": true,
  "detected_from_documents": ["GST", "PAN", "IEC"]
}
```

❌ **Invalid (IEC but no GST/PAN):**
```json
{
  "domestic_buy_india": false,
  "domestic_sell_india": false,
  "import_allowed": false,
  "export_allowed": false,
  "detected_from_documents": ["IEC_INCOMPLETE"]
}
```

---

#### 🌏 RULE C: FOREIGN DOMESTIC TRADING

**Rule:** Foreign entities can trade domestically ONLY in their home country.

**Requirement:** Foreign Tax ID (verified)

**Logic:**
```python
async def detect_foreign_domestic_capability(partner_id: UUID) -> dict:
    """
    Grants domestic trading rights in THEIR home country.
    Requires: Foreign Tax ID verified.
    """
    docs = await get_verified_documents(partner_id)
    partner = await get_partner(partner_id)
    
    has_foreign_tax_id = any(
        d.document_type == "foreign_tax_id" and 
        d.verification_status == "verified" 
        for d in docs
    )
    
    if has_foreign_tax_id and partner.country != "India":
        return {
            "domestic_buy_home_country": True,
            "domestic_sell_home_country": True,
            "detected_from_documents": ["FOREIGN_TAX_ID"],
            "auto_detected": True,
            "detected_at": datetime.utcnow()
        }
    
    return {
        "domestic_buy_home_country": False,
        "domestic_sell_home_country": False
    }
```

**Example Result (USA Company):**
```json
{
  "domestic_buy_india": false,
  "domestic_sell_india": false,
  "domestic_buy_home_country": true,
  "domestic_sell_home_country": true,
  "import_allowed": false,
  "export_allowed": false,
  "detected_from_documents": ["FOREIGN_TAX_ID"],
  "home_country": "USA"
}
```

---

#### 🚢 RULE D: FOREIGN IMPORT/EXPORT

**Requirement:** Foreign Import License OR Foreign Export License (verified)

**Logic:**
```python
async def detect_foreign_import_export_capability(partner_id: UUID) -> dict:
    """
    Grants import/export rights for foreign entities.
    Requires: Foreign import/export licenses.
    """
    docs = await get_verified_documents(partner_id)
    
    has_import_license = any(
        d.document_type == "foreign_import_license" and 
        d.verification_status == "verified" 
        for d in docs
    )
    
    has_export_license = any(
        d.document_type == "foreign_export_license" and 
        d.verification_status == "verified" 
        for d in docs
    )
    
    result = {}
    detected_docs = []
    
    if has_import_license:
        result["import_allowed"] = True
        detected_docs.append("FOREIGN_IMPORT_LICENSE")
    else:
        result["import_allowed"] = False
    
    if has_export_license:
        result["export_allowed"] = True
        detected_docs.append("FOREIGN_EXPORT_LICENSE")
    else:
        result["export_allowed"] = False
    
    if detected_docs:
        result["detected_from_documents"] = detected_docs
        result["auto_detected"] = True
        result["detected_at"] = datetime.utcnow()
    
    return result
```

**Example Result (Foreign Exporter only):**
```json
{
  "domestic_buy_home_country": true,
  "domestic_sell_home_country": true,
  "import_allowed": false,
  "export_allowed": true,
  "detected_from_documents": ["FOREIGN_TAX_ID", "FOREIGN_EXPORT_LICENSE"]
}
```

---

### 5. COMPLETE DETECTION SERVICE

```python
class CapabilityDetectionService:
    """
    Automatically detects partner capabilities from verified documents.
    
    Detection Rules:
    1. Indian Domestic: GST + PAN → domestic_buy_india, domestic_sell_india
    2. Import/Export: IEC + GST + PAN → import_allowed, export_allowed
    3. Foreign Domestic: Foreign Tax ID → domestic_buy_home_country, domestic_sell_home_country
    4. Foreign International: Foreign licenses → import_allowed, export_allowed
    """
    
    async def update_partner_capabilities(
        self, 
        partner_id: UUID,
        force_redetect: bool = False
    ) -> BusinessPartner:
        """
        Main entry point: Detect and update capabilities.
        """
        partner = await self.repo.get_by_id(partner_id)
        
        # Service providers cannot trade
        if partner.entity_class == "service_provider":
            capabilities = self._get_empty_capabilities()
            capabilities["detected_from_documents"] = ["SERVICE_PROVIDER_NO_TRADING"]
            await self.repo.update_capabilities(partner_id, capabilities)
            return partner
        
        # Detect all capabilities
        capabilities = {}
        
        if partner.country == "India":
            # Indian entity detection
            domestic = await self.detect_indian_domestic_capability(partner_id)
            import_export = await self.detect_import_export_capability(partner_id)
            capabilities.update(domestic)
            capabilities.update(import_export)
        else:
            # Foreign entity detection
            foreign_domestic = await self.detect_foreign_domestic_capability(partner_id)
            foreign_intl = await self.detect_foreign_import_export_capability(partner_id)
            capabilities.update(foreign_domestic)
            capabilities.update(foreign_intl)
        
        # Merge detected documents
        all_docs = set()
        for key in ["detected_from_documents"]:
            if key in capabilities:
                if isinstance(capabilities[key], list):
                    all_docs.update(capabilities[key])
        
        capabilities["detected_from_documents"] = sorted(list(all_docs))
        capabilities["last_detection_run"] = datetime.utcnow().isoformat()
        
        # Update database
        await self.repo.update_capabilities(partner_id, capabilities)
        
        # Emit event
        await self.emitter.emit(CapabilitiesDetectedEvent(
            partner_id=partner_id,
            capabilities=capabilities,
            auto_detected=True
        ))
        
        return await self.repo.get_by_id(partner_id)
    
    def _get_empty_capabilities(self) -> dict:
        """Default empty capabilities."""
        return {
            "domestic_buy_india": False,
            "domestic_sell_india": False,
            "domestic_buy_home_country": False,
            "domestic_sell_home_country": False,
            "import_allowed": False,
            "export_allowed": False,
            "auto_detected": False,
            "detected_from_documents": [],
            "detected_at": None,
            "manual_override": False,
            "override_reason": None,
            "last_detection_run": None
        }
```

---

### 6. INSIDER TRADING PREVENTION (NO CHANGE)

**4 Blocking Rules:**

```python
class InsiderTradingValidator:
    """
    Prevents trading between related business entities.
    """
    
    async def validate_trade_parties(
        self,
        buyer_id: UUID,
        seller_id: UUID,
        db: AsyncSession
    ) -> dict:
        """
        Validates that buyer and seller are not related.
        
        Returns:
            {
                "allowed": bool,
                "violation_type": str | None,
                "reason": str
            }
        """
        buyer = await self.repo.get_by_id(buyer_id)
        seller = await self.repo.get_by_id(seller_id)
        
        # Rule 1: Same entity
        if buyer_id == seller_id:
            return {
                "allowed": False,
                "violation_type": "SAME_ENTITY",
                "reason": "Cannot trade with yourself"
            }
        
        # Rule 2: Master-Branch or Sibling Branches
        if buyer.master_entity_id and seller.master_entity_id:
            if buyer.master_entity_id == seller.master_entity_id:
                return {
                    "allowed": False,
                    "violation_type": "SIBLING_BRANCH_TRADING",
                    "reason": "Cannot trade between branches of same master entity"
                }
        
        if buyer.is_master_entity and seller.master_entity_id == buyer_id:
            return {
                "allowed": False,
                "violation_type": "MASTER_BRANCH_TRADING",
                "reason": "Cannot trade between master entity and its branch"
            }
        
        if seller.is_master_entity and buyer.master_entity_id == seller_id:
            return {
                "allowed": False,
                "violation_type": "MASTER_BRANCH_TRADING",
                "reason": "Cannot trade between master entity and its branch"
            }
        
        # Rule 3: Same Corporate Group
        if buyer.corporate_group_id and seller.corporate_group_id:
            if buyer.corporate_group_id == seller.corporate_group_id:
                return {
                    "allowed": False,
                    "violation_type": "CORPORATE_GROUP_TRADING",
                    "reason": "Cannot trade within same corporate group"
                }
        
        # Rule 4: Same GST (Indian entities)
        if buyer.country == "India" and seller.country == "India":
            buyer_gst = await self._get_gst_number(buyer_id)
            seller_gst = await self._get_gst_number(seller_id)
            if buyer_gst and seller_gst and buyer_gst == seller_gst:
                return {
                    "allowed": False,
                    "violation_type": "SAME_GST_GROUP",
                    "reason": "Cannot trade between entities with same GST number"
                }
        
        return {
            "allowed": True,
            "violation_type": None,
            "reason": "Trade parties are not related"
        }
```

---

### 7. TRADE DESK LOGIC (UPDATED)

#### 7.1 Availability Posting Validation

```python
class AvailabilityService:
    """
    Service for creating seller availabilities.
    """
    
    async def _validate_seller_capabilities(
        self,
        partner_id: UUID,
        posting_location: str,  # "India" or country code
        is_export: bool = False
    ) -> None:
        """
        Validates seller can post availability.
        
        Args:
            partner_id: Seller's partner ID
            posting_location: Where availability is posted (India, USA, etc.)
            is_export: Whether this is an export posting
        
        Raises:
            ValueError: If seller lacks required capability
        """
        partner = await self.repo.get_by_id(partner_id)
        
        # Service providers cannot post availabilities
        if partner.entity_class == "service_provider":
            raise ValueError(
                f"Service providers ({partner.service_provider_type}) "
                f"cannot post availabilities"
            )
        
        capabilities = partner.capabilities or {}
        
        # Validate based on location and type
        if is_export:
            if not capabilities.get("export_allowed", False):
                raise ValueError(
                    f"Partner {partner.legal_name} does not have export_allowed capability. "
                    f"Required documents: IEC + GST + PAN (for Indian) or Foreign Export License (for foreign)."
                )
        elif posting_location == "India":
            if not capabilities.get("domestic_sell_india", False):
                raise ValueError(
                    f"Partner {partner.legal_name} does not have domestic_sell_india capability. "
                    f"Required documents: GST + PAN both verified."
                )
        else:
            # Foreign domestic posting
            if not capabilities.get("domestic_sell_home_country", False):
                raise ValueError(
                    f"Partner {partner.legal_name} does not have domestic_sell_home_country capability. "
                    f"Required document: Foreign Tax ID verified."
                )
    
    async def create_availability(
        self,
        data: AvailabilityCreateSchema,
        created_by: UUID
    ) -> Availability:
        """
        Create new availability with capability validation.
        """
        # Validate seller capabilities
        await self._validate_seller_capabilities(
            partner_id=data.business_partner_id,
            posting_location=data.location or "India",
            is_export=data.is_export or False
        )
        
        # Rest of creation logic...
```

#### 7.2 Requirement Posting Validation

```python
class RequirementService:
    """
    Service for creating buyer requirements.
    """
    
    async def _validate_buyer_capabilities(
        self,
        partner_id: UUID,
        buying_location: str,  # "India" or country code
        is_import: bool = False
    ) -> None:
        """
        Validates buyer can post requirement.
        
        Args:
            partner_id: Buyer's partner ID
            buying_location: Where requirement is posted (India, USA, etc.)
            is_import: Whether this is an import requirement
        
        Raises:
            ValueError: If buyer lacks required capability
        """
        partner = await self.repo.get_by_id(partner_id)
        
        # Service providers cannot post requirements
        if partner.entity_class == "service_provider":
            raise ValueError(
                f"Service providers ({partner.service_provider_type}) "
                f"cannot post requirements"
            )
        
        capabilities = partner.capabilities or {}
        
        # Validate based on location and type
        if is_import:
            if not capabilities.get("import_allowed", False):
                raise ValueError(
                    f"Partner {partner.legal_name} does not have import_allowed capability. "
                    f"Required documents: IEC + GST + PAN (for Indian) or Foreign Import License (for foreign)."
                )
        elif buying_location == "India":
            if not capabilities.get("domestic_buy_india", False):
                raise ValueError(
                    f"Partner {partner.legal_name} does not have domestic_buy_india capability. "
                    f"Required documents: GST + PAN both verified."
                )
        else:
            # Foreign domestic buying
            if not capabilities.get("domestic_buy_home_country", False):
                raise ValueError(
                    f"Partner {partner.legal_name} does not have domestic_buy_home_country capability. "
                    f"Required document: Foreign Tax ID verified."
                )
    
    async def create_requirement(
        self,
        data: RequirementCreateSchema,
        created_by: UUID
    ) -> Requirement:
        """
        Create new requirement with capability validation.
        """
        # Validate buyer capabilities
        await self._validate_buyer_capabilities(
            partner_id=data.business_partner_id,
            buying_location=data.location or "India",
            is_import=data.is_import or False
        )
        
        # Rest of creation logic...
```

#### 7.3 Matching Validation

```python
class MatchValidator:
    """
    Validates availability-requirement matches.
    """
    
    async def validate_match_eligibility(
        self,
        requirement: Requirement,
        availability: Availability
    ) -> ValidationResult:
        """
        Validates if requirement and availability can match.
        
        Includes:
        - Capability validation
        - Insider trading check
        - Other business rules
        """
        reasons = []
        
        # 1. Insider trading check
        insider_check = await self.insider_validator.validate_trade_parties(
            buyer_id=requirement.business_partner_id,
            seller_id=availability.business_partner_id,
            db=self.db
        )
        
        if not insider_check["allowed"]:
            reasons.append(
                f"Insider trading violation: {insider_check['violation_type']} - "
                f"{insider_check['reason']}"
            )
        
        # 2. Capability validation
        buyer = await self.partner_repo.get_by_id(requirement.business_partner_id)
        seller = await self.partner_repo.get_by_id(availability.business_partner_id)
        
        buyer_caps = buyer.capabilities or {}
        seller_caps = seller.capabilities or {}
        
        # Check buyer capability
        if requirement.is_import:
            if not buyer_caps.get("import_allowed", False):
                reasons.append("Buyer lacks import_allowed capability")
        elif requirement.location == "India":
            if not buyer_caps.get("domestic_buy_india", False):
                reasons.append("Buyer lacks domestic_buy_india capability")
        else:
            if not buyer_caps.get("domestic_buy_home_country", False):
                reasons.append("Buyer lacks domestic_buy_home_country capability")
        
        # Check seller capability
        if availability.is_export:
            if not seller_caps.get("export_allowed", False):
                reasons.append("Seller lacks export_allowed capability")
        elif availability.location == "India":
            if not seller_caps.get("domestic_sell_india", False):
                reasons.append("Seller lacks domestic_sell_india capability")
        else:
            if not seller_caps.get("domestic_sell_home_country", False):
                reasons.append("Seller lacks domestic_sell_home_country capability")
        
        # 3. Other validations (commodity, quality, quantity, etc.)
        # ... existing logic ...
        
        return ValidationResult(
            is_valid=len(reasons) == 0,
            reasons=reasons
        )
```

---

### 8. SERVICE PROVIDER STRUCTURE (NO CHANGE)

**Service Providers CANNOT trade:**

```python
# Onboarding flow
if entity_class == "service_provider":
    # Ask for service provider type
    service_provider_type = select_from([
        "broker",
        "sub_broker", 
        "transporter",
        "controller",
        "financer",
        "shipping_agent"
    ])
    
    # Set capabilities to all False
    capabilities = {
        "domestic_buy_india": False,
        "domestic_sell_india": False,
        "domestic_buy_home_country": False,
        "domestic_sell_home_country": False,
        "import_allowed": False,
        "export_allowed": False,
        "detected_from_documents": ["SERVICE_PROVIDER_NO_TRADING"],
        "auto_detected": True
    }

# Existing flows UNCHANGED:
# - Broker onboarding (no license required, commission structure)
# - Sub-broker linking to parent broker
# - Transporter type selection (lorry owner vs commission agent)
# - Controller, Financer, Shipping Agent flows
```

---

## 📊 DATABASE SCHEMA CHANGES

### BusinessPartner Model (UPDATED)

```python
class BusinessPartner(Base):
    __tablename__ = "business_partners"
    
    # REMOVE these columns:
    # partner_type = Column(Enum(PartnerType))  ❌ DELETE
    # trade_classification = Column(Enum(TradeClassification))  ❌ DELETE
    # is_buyer = Column(Boolean)  ❌ DELETE
    # is_seller = Column(Boolean)  ❌ DELETE
    # is_trader = Column(Boolean)  ❌ DELETE
    
    # ADD these columns:
    entity_class = Column(
        Enum("business_entity", "service_provider", name="entity_class_enum"),
        nullable=False
    )
    
    # If entity_class == "business_entity"
    business_entity_type = Column(
        Enum(BusinessEntityType),
        nullable=True
    )
    
    # If entity_class == "service_provider"
    service_provider_type = Column(
        Enum(
            "broker", "sub_broker", "transporter", 
            "controller", "financer", "shipping_agent",
            name="service_provider_type_enum"
        ),
        nullable=True
    )
    
    # Document-driven capabilities
    capabilities = Column(JSONB, nullable=False, default={
        "domestic_buy_india": False,
        "domestic_sell_india": False,
        "domestic_buy_home_country": False,
        "domestic_sell_home_country": False,
        "import_allowed": False,
        "export_allowed": False,
        "auto_detected": False,
        "detected_from_documents": [],
        "detected_at": None,
        "manual_override": False,
        "override_reason": None,
        "last_detection_run": None
    })
    
    # Entity hierarchy (for insider trading prevention)
    master_entity_id = Column(UUID(as_uuid=True), ForeignKey("business_partners.id"), nullable=True)
    corporate_group_id = Column(UUID(as_uuid=True), nullable=True)
    is_master_entity = Column(Boolean, default=False)
    entity_hierarchy = Column(JSONB, default={})
    
    # KEEP all other existing columns
    # (legal_name, gstin, pan, country, kyc_status, etc.)
```

### Indexes

```python
# Add JSONB indexes for capability queries
CREATE INDEX idx_capabilities_domestic_buy_india 
ON business_partners ((capabilities->>'domestic_buy_india'));

CREATE INDEX idx_capabilities_domestic_sell_india 
ON business_partners ((capabilities->>'domestic_sell_india'));

CREATE INDEX idx_capabilities_import 
ON business_partners ((capabilities->>'import_allowed'));

CREATE INDEX idx_capabilities_export 
ON business_partners ((capabilities->>'export_allowed'));

CREATE INDEX idx_entity_class 
ON business_partners (entity_class);

CREATE INDEX idx_master_entity 
ON business_partners (master_entity_id);

CREATE INDEX idx_corporate_group 
ON business_partners (corporate_group_id);
```

---

## 🔄 DATA MIGRATION STRATEGY

### Migration Logic (CORRECTED)

```python
def upgrade():
    """Add capability system and migrate existing data."""
    
    # Step 1: Add new columns (nullable temporarily)
    op.add_column('business_partners', sa.Column('entity_class', sa.String(20), nullable=True))
    op.add_column('business_partners', sa.Column('business_entity_type', sa.String(50), nullable=True))
    op.add_column('business_partners', sa.Column('service_provider_type', sa.String(50), nullable=True))
    op.add_column('business_partners', sa.Column('capabilities', JSONB, nullable=True))
    op.add_column('business_partners', sa.Column('master_entity_id', UUID(as_uuid=True), nullable=True))
    op.add_column('business_partners', sa.Column('corporate_group_id', UUID(as_uuid=True), nullable=True))
    op.add_column('business_partners', sa.Column('is_master_entity', sa.Boolean, default=False))
    op.add_column('business_partners', sa.Column('entity_hierarchy', JSONB, default={}))
    
    # Step 2: Migrate data
    connection = op.get_bind()
    
    # 2.1: Service Providers
    connection.execute(sa.text("""
        UPDATE business_partners
        SET 
            entity_class = 'service_provider',
            service_provider_type = CASE partner_type
                WHEN 'broker' THEN 'broker'
                WHEN 'sub_broker' THEN 'sub_broker'
                WHEN 'transporter' THEN 'transporter'
                WHEN 'controller' THEN 'controller'
                WHEN 'financer' THEN 'financer'
                WHEN 'shipping_agent' THEN 'shipping_agent'
            END,
            capabilities = '{
                "domestic_buy_india": false,
                "domestic_sell_india": false,
                "domestic_buy_home_country": false,
                "domestic_sell_home_country": false,
                "import_allowed": false,
                "export_allowed": false,
                "auto_detected": false,
                "detected_from_documents": ["MIGRATED_SERVICE_PROVIDER"],
                "manual_override": false
            }'::jsonb
        WHERE partner_type IN ('broker', 'sub_broker', 'transporter', 'controller', 'financer', 'shipping_agent')
    """))
    
    # 2.2: Business Entities - Domestic Indian (seller, buyer)
    connection.execute(sa.text("""
        UPDATE business_partners
        SET 
            entity_class = 'business_entity',
            business_entity_type = 'private_limited',
            capabilities = CASE partner_type
                WHEN 'seller' THEN '{
                    "domestic_buy_india": false,
                    "domestic_sell_india": true,
                    "domestic_buy_home_country": false,
                    "domestic_sell_home_country": false,
                    "import_allowed": false,
                    "export_allowed": false,
                    "auto_detected": false,
                    "detected_from_documents": ["MIGRATED_FROM_SELLER"],
                    "manual_override": true,
                    "override_reason": "Migrated from legacy seller type"
                }'::jsonb
                WHEN 'buyer' THEN '{
                    "domestic_buy_india": true,
                    "domestic_sell_india": false,
                    "domestic_buy_home_country": false,
                    "domestic_sell_home_country": false,
                    "import_allowed": false,
                    "export_allowed": false,
                    "auto_detected": false,
                    "detected_from_documents": ["MIGRATED_FROM_BUYER"],
                    "manual_override": true,
                    "override_reason": "Migrated from legacy buyer type"
                }'::jsonb
                WHEN 'trader' THEN '{
                    "domestic_buy_india": true,
                    "domestic_sell_india": true,
                    "domestic_buy_home_country": false,
                    "domestic_sell_home_country": false,
                    "import_allowed": false,
                    "export_allowed": false,
                    "auto_detected": false,
                    "detected_from_documents": ["MIGRATED_FROM_TRADER"],
                    "manual_override": true,
                    "override_reason": "Migrated from legacy trader type"
                }'::jsonb
            END
        WHERE partner_type IN ('seller', 'buyer', 'trader')
          AND country = 'India'
          AND trade_classification = 'domestic'
    """))
    
    # 2.3: Business Entities - Indian Importers/Exporters
    connection.execute(sa.text("""
        UPDATE business_partners
        SET 
            entity_class = 'business_entity',
            business_entity_type = 'private_limited',
            capabilities = '{
                "domestic_buy_india": true,
                "domestic_sell_india": true,
                "domestic_buy_home_country": false,
                "domestic_sell_home_country": false,
                "import_allowed": true,
                "export_allowed": true,
                "auto_detected": false,
                "detected_from_documents": ["MIGRATED_FROM_IMPORTER_EXPORTER"],
                "manual_override": true,
                "override_reason": "Migrated from legacy importer/exporter type"
            }'::jsonb
        WHERE partner_type IN ('importer', 'exporter', 'trader')
          AND country = 'India'
          AND trade_classification IN ('importer', 'exporter')
    """))
    
    # 2.4: Foreign Business Entities
    connection.execute(sa.text("""
        UPDATE business_partners
        SET 
            entity_class = 'business_entity',
            business_entity_type = 'foreign_entity',
            capabilities = '{
                "domestic_buy_india": false,
                "domestic_sell_india": false,
                "domestic_buy_home_country": true,
                "domestic_sell_home_country": true,
                "import_allowed": false,
                "export_allowed": false,
                "auto_detected": false,
                "detected_from_documents": ["MIGRATED_FOREIGN_ENTITY"],
                "manual_override": true,
                "override_reason": "Migrated from legacy foreign partner"
            }'::jsonb
        WHERE country != 'India'
    """))
    
    # Step 3: Make columns NOT NULL
    op.alter_column('business_partners', 'entity_class', nullable=False)
    op.alter_column('business_partners', 'capabilities', nullable=False)
    
    # Step 4: Add constraints
    op.create_check_constraint(
        'chk_entity_class_type',
        'business_partners',
        """
        (entity_class = 'business_entity' AND business_entity_type IS NOT NULL AND service_provider_type IS NULL) OR
        (entity_class = 'service_provider' AND service_provider_type IS NOT NULL AND business_entity_type IS NULL)
        """
    )
    
    # Step 5: Add indexes
    op.create_index('idx_capabilities_domestic_buy_india', 'business_partners', 
                    [sa.text("(capabilities->>'domestic_buy_india')")])
    op.create_index('idx_capabilities_domestic_sell_india', 'business_partners', 
                    [sa.text("(capabilities->>'domestic_sell_india')")])
    op.create_index('idx_capabilities_import', 'business_partners', 
                    [sa.text("(capabilities->>'import_allowed')")])
    op.create_index('idx_capabilities_export', 'business_partners', 
                    [sa.text("(capabilities->>'export_allowed')")])
    op.create_index('idx_entity_class', 'business_partners', ['entity_class'])
    op.create_index('idx_master_entity', 'business_partners', ['master_entity_id'])
    
    # Step 6: Drop old columns
    op.drop_column('business_partners', 'partner_type')
    op.drop_column('business_partners', 'trade_classification')
    op.drop_column('business_partners', 'is_buyer')
    op.drop_column('business_partners', 'is_seller')
    op.drop_column('business_partners', 'is_trader')


def downgrade():
    """Rollback to old partner_type system."""
    
    # Step 1: Re-add old columns
    op.add_column('business_partners', sa.Column('partner_type', sa.String(50), nullable=True))
    op.add_column('business_partners', sa.Column('trade_classification', sa.String(50), nullable=True))
    
    # Step 2: Reconstruct partner_type from capabilities
    connection = op.get_bind()
    
    connection.execute(sa.text("""
        UPDATE business_partners
        SET partner_type = CASE
            WHEN entity_class = 'service_provider' THEN service_provider_type
            WHEN capabilities->>'domestic_sell_india' = 'true' AND capabilities->>'domestic_buy_india' = 'true' THEN 'trader'
            WHEN capabilities->>'domestic_sell_india' = 'true' THEN 'seller'
            WHEN capabilities->>'domestic_buy_india' = 'true' THEN 'buyer'
            ELSE 'buyer'
        END,
        trade_classification = CASE
            WHEN capabilities->>'import_allowed' = 'true' OR capabilities->>'export_allowed' = 'true' THEN 'importer'
            ELSE 'domestic'
        END
    """))
    
    # Step 3: Drop new columns
    op.drop_column('business_partners', 'entity_class')
    op.drop_column('business_partners', 'business_entity_type')
    op.drop_column('business_partners', 'service_provider_type')
    op.drop_column('business_partners', 'capabilities')
    op.drop_column('business_partners', 'master_entity_id')
    op.drop_column('business_partners', 'corporate_group_id')
    op.drop_column('business_partners', 'is_master_entity')
    op.drop_column('business_partners', 'entity_hierarchy')
```

---

## 📊 DETAILED FILE INVENTORY FOR APPROVAL

### Files to Modify: 21 Files Across 6 Modules

#### Module 1: Core Partner Module (9 files)

**File 1: `backend/modules/partners/models.py`**
- **Current State:** Contains partner_type, trade_classification columns
- **Changes Required:**
  - DELETE: Lines 97-110 (partner_type, trade_classification, is_buyer, is_seller, is_trader)
  - ADD: Lines 90-160 (entity_class, business_entity_type, service_provider_type, capabilities JSONB, master_entity_id, corporate_group_id, is_master_entity, entity_hierarchy)
- **Breaking Change:** NO (migration handles conversion)
- **Lines of Code:** +70, -14
- **Estimated Time:** 3 hours
- **Testing Impact:** Update 15 test fixtures

**File 2: `backend/modules/partners/enums.py`**
- **Current State:** Contains PartnerType enum (11 values), TradeClassification enum (3 values)
- **Changes Required:**
  - ADD: BusinessEntityType enum (10 values: proprietorship, partnership, llp, private_limited, public_limited, trust, society, llc, corporation, foreign_entity)
  - ADD: ServiceProviderType enum (6 values: broker, sub_broker, transporter, controller, financer, shipping_agent)
  - ADD: DocumentType values (IEC, FOREIGN_TAX_ID, FOREIGN_IMPORT_LICENSE, FOREIGN_EXPORT_LICENSE)
  - DEPRECATE: PartnerType enum (keep for migration reference)
  - DELETE: TradeClassification enum
- **Breaking Change:** NO (old enums kept until migration complete)
- **Lines of Code:** +45, -8
- **Estimated Time:** 1 hour
- **Testing Impact:** None

**File 3: `backend/modules/partners/schemas.py`**
- **Current State:** 18 schemas using partner_type and trade_classification
- **Changes Required:**
  - DELETE: partner_type fields in OnboardingApplicationCreate, BusinessPartnerResponse, BusinessPartnerUpdate (lines 35, 50, 165, 361)
  - ADD: OnboardingApplicationCreate with entity_class + validators (lines 30-90)
  - ADD: CapabilityResponse schema (lines 200-225)
  - ADD: CapabilityOverrideRequest schema (lines 230-245)
  - MODIFY: BusinessPartnerResponse to include capabilities (line 350-380)
- **Breaking Change:** YES (API contract) - Mitigated with backward compatibility layer
- **Lines of Code:** +120, -25
- **Estimated Time:** 4 hours
- **Testing Impact:** Update all API tests

**File 4: `backend/modules/partners/services.py`**
- **Current State:** 1,200 lines, uses partner_type in 15 methods
- **Changes Required:**
  - DELETE: All partner_type references (lines 363, 376, 497, 507, 614, 883, 885, 962)
  - ADD: CapabilityDetectionService class (300 lines, 4 detection methods)
  - MODIFY: ApprovalService.process_approval() - add capability detection trigger
  - MODIFY: DocumentProcessingService.verify_document_ocr() - add capability detection trigger
- **Breaking Change:** NO (logic enhancement)
- **Lines of Code:** +350, -18
- **Estimated Time:** 6 hours
- **Testing Impact:** 8 new unit tests

**File 5: `backend/modules/partners/validators.py`**
- **Current State:** 250 lines, basic validation logic
- **Changes Required:**
  - MODIFY: Line 46 (replace partner_type check with capabilities check)
  - ADD: InsiderTradingValidator class (150 lines, 4 blocking rules)
  - ADD: validate_trade_parties() method
  - ADD: _get_gst_number() helper
  - ADD: _check_corporate_group() helper
- **Breaking Change:** NO (enhanced validation)
- **Lines of Code:** +180, -2
- **Estimated Time:** 4 hours
- **Testing Impact:** 5 new validation tests

**File 6: `backend/modules/partners/router.py`**
- **Current State:** 15 endpoints, 600 lines
- **Changes Required:**
  - ADD: POST /partners/{id}/capabilities/detect (lines 500-530)
  - ADD: PUT /partners/{id}/capabilities/override (lines 535-570)
  - ADD: POST /partners/{id}/entity-hierarchy (lines 575-610)
  - MODIFY: Existing endpoints to use new schemas
- **Breaking Change:** NO (new endpoints, enhanced existing)
- **Lines of Code:** +95, -0
- **Estimated Time:** 3 hours
- **Testing Impact:** 3 new integration tests

**File 7: `backend/modules/partners/repositories.py`**
- **Current State:** 450 lines, filters by partner_type
- **Changes Required:**
  - DELETE: partner_type filter parameters (lines 187, 199, 215-216)
  - ADD: Capability-based filters (lines 190-250):
    - filter_by_entity_class()
    - filter_by_domestic_buy_india()
    - filter_by_domestic_sell_india()
    - filter_by_import_capability()
    - filter_by_export_capability()
  - ADD: JSONB query helpers
- **Breaking Change:** YES (filter parameters) - Backward compatible with optional params
- **Lines of Code:** +75, -12
- **Estimated Time:** 2 hours
- **Testing Impact:** Update 6 repository tests

**File 8: `backend/modules/partners/notifications.py`**
- **Current State:** Email templates reference partner_type
- **Changes Required:**
  - MODIFY: Line 170 (approval email template)
  - REPLACE: "Partner Type: {partner.partner_type}" with capability display
  - ADD: Lines 171-180 (capability summary in email)
- **Breaking Change:** NO (cosmetic email change)
- **Lines of Code:** +12, -2
- **Estimated Time:** 1 hour
- **Testing Impact:** Update 2 email tests

**File 9: `backend/modules/partners/events.py`**
- **Current State:** 10 event classes
- **Changes Required:**
  - ADD: CapabilitiesDetectedEvent class (lines 450-475)
  - ADD: CapabilitiesManuallyOverriddenEvent class (lines 480-505)
  - ADD: CapabilitiesResetToAutoDetectEvent class (lines 510-535)
- **Breaking Change:** NO (new events)
- **Lines of Code:** +90, -0
- **Estimated Time:** 2 hours
- **Testing Impact:** 3 new event tests

**Partner Module Total:** 9 files, 1,007 lines added, 81 lines removed, 26 hours estimated

---

#### Module 2: Trade Desk Module (4 files)

**File 10: `backend/modules/trade_desk/services/availability_service.py`**
- **Current State:** TODO comment at lines 798-801
- **Changes Required:**
  - DELETE: Lines 798-801 (TODO: Validate seller can sell)
  - ADD: _validate_seller_capabilities() method (lines 50-105, 55 lines)
  - MODIFY: create_availability() - add capability validation before creation (line 150)
- **Breaking Change:** YES (new validation blocks invalid postings) - Proper implementation
- **Lines of Code:** +60, -4
- **Estimated Time:** 3 hours
- **Testing Impact:** 4 new service tests

**File 11: `backend/modules/trade_desk/services/requirement_service.py`**
- **Current State:** TODO comment at line 1432
- **Changes Required:**
  - DELETE: Line 1432 (TODO: Validate buyer can buy)
  - ADD: _validate_buyer_capabilities() method (lines 100-155, 55 lines)
  - MODIFY: create_requirement() - add capability validation before creation (line 200)
- **Breaking Change:** YES (new validation blocks invalid postings) - Proper implementation
- **Lines of Code:** +60, -1
- **Estimated Time:** 3 hours
- **Testing Impact:** 4 new service tests

**File 12: `backend/modules/trade_desk/matching/validators.py`**
- **Current State:** Basic matching validation
- **Changes Required:**
  - ADD: Insider trading validation block (lines 105-180, 75 lines)
  - ADD: Capability validation block (lines 185-230, 45 lines)
  - MODIFY: validate_match_eligibility() method to call new validators
  - ADD: Import InsiderTradingValidator
- **Breaking Change:** YES (enhanced matching blocks related parties) - Business requirement
- **Lines of Code:** +125, -0
- **Estimated Time:** 4 hours
- **Testing Impact:** 6 new matching tests

**File 13: `backend/modules/trade_desk/schemas/__init__.py`**
- **Current State:** Contains partner_type field at line 239
- **Changes Required:**
  - DELETE: Line 239 (partner_type: str field in MatchResponse)
- **Breaking Change:** YES (schema change) - Field was informational only, not used
- **Lines of Code:** +0, -1
- **Estimated Time:** 0.5 hours
- **Testing Impact:** Update 1 schema test

**Trade Desk Module Total:** 4 files, 245 lines added, 6 lines removed, 10.5 hours estimated

---

#### Module 3: Risk Module (2 files)

**File 14: `backend/modules/risk/risk_engine.py`**
- **Current State:** validate_partner_role() at lines 884-994 (110 lines)
- **Changes Required:**
  - REPLACE: Entire validate_partner_role() method (lines 884-994)
  - NEW: Capability-based validation logic (66 lines)
  - DELETE: 11 partner_type references (lines 909, 913, 915, 919, 923, 928, 937, 944, 950, 959, 966)
  - ADD: Service provider blocking
  - ADD: Capability checks for BUY/SELL transactions
- **Breaking Change:** NO (same interface, different implementation)
- **Lines of Code:** +66, -110
- **Estimated Time:** 4 hours
- **Testing Impact:** Update 8 risk engine tests

**File 15: `backend/modules/risk/schemas.py`**
- **Current State:** partner_type fields in 4 schemas
- **Changes Required:**
  - DELETE: Lines 40-45, 199, 206, 346-347 (all partner_type fields and validators)
- **Breaking Change:** YES (schema change) - Fields were for validation only
- **Lines of Code:** +0, -12
- **Estimated Time:** 1 hour
- **Testing Impact:** Update 3 schema tests

**Risk Module Total:** 2 files, 66 lines added, 122 lines removed, 5 hours estimated

---

#### Module 4: Settings Module (1 file)

**File 16: `backend/modules/settings/business_partners/models.py`**
- **Current State:** Simplified BusinessPartner model
- **Changes Required:**
  - DELETE: Lines 43-50 (partner_type column)
  - ADD: Lines 43-75 (entity_class, business_entity_type, service_provider_type, capabilities)
- **Breaking Change:** NO (settings model follows main model)
- **Lines of Code:** +32, -8
- **Estimated Time:** 1 hour
- **Testing Impact:** Update 2 settings tests

**Settings Module Total:** 1 file, 32 lines added, 8 lines removed, 1 hour estimated

---

#### Module 5: AI Module (3 files)

**File 17: `backend/ai/assistants/partner_assistant/assistant.py`**
- **Current State:** Uses partner_type in 11 locations
- **Changes Required:**
  - DELETE: Lines 39, 46, 53, 56, 58, 75, 81, 86, 469, 471, 473 (all partner_type references)
  - REPLACE: assist_onboarding_start() method signature (lines 35-90)
  - REPLACE: _estimate_onboarding_time() method (lines 469-480)
  - ADD: entity_class parameter handling
- **Breaking Change:** NO (internal AI logic)
- **Lines of Code:** +45, -25
- **Estimated Time:** 3 hours
- **Testing Impact:** Update 5 AI assistant tests

**File 18: `backend/ai/assistants/partner_assistant/tools.py`**
- **Current State:** Single get_onboarding_requirements() method
- **Changes Required:**
  - REPLACE: get_onboarding_requirements() method (lines 31-170)
  - ADD: get_service_provider_requirements() method (lines 30-100, 70 lines)
  - ADD: get_business_entity_requirements() method (lines 105-150, 45 lines)
  - DELETE: Old method signature (lines 214-280)
- **Breaking Change:** NO (internal AI tools)
- **Lines of Code:** +115, -67
- **Estimated Time:** 4 hours
- **Testing Impact:** 4 new tool tests

**File 19: `backend/ai/prompts/partner/prompts.py`**
- **Current State:** Prompts reference partner_type
- **Changes Required:**
  - REPLACE: Lines 46, 55 (partner_type question → entity_class question)
  - UPDATE: Onboarding guidance text
- **Breaking Change:** NO (prompt changes)
- **Lines of Code:** +8, -4
- **Estimated Time:** 0.5 hours
- **Testing Impact:** Update 1 prompt test

**AI Module Total:** 3 files, 168 lines added, 96 lines removed, 7.5 hours estimated

---

#### Module 6: Database (2 files)

**File 20: `backend/db/migrations/versions/YYYYMMDD_HHMMSS_add_capability_system.py`**
- **Current State:** Does not exist (new file)
- **Changes Required:**
  - CREATE: Complete migration file (600 lines)
  - ADD: upgrade() function (350 lines):
    - Add new columns
    - Migrate data (service providers, business entities, importers, foreign)
    - Add constraints and indexes
    - Drop old columns
  - ADD: downgrade() function (250 lines):
    - Re-add old columns
    - Reconstruct partner_type from capabilities
    - Drop new columns
- **Breaking Change:** NO (migration handles everything)
- **Lines of Code:** +600, -0
- **Estimated Time:** 8 hours
- **Testing Impact:** 3 migration tests (upgrade, downgrade, data integrity)

**File 21: `backend/modules/partners/tests/test_capabilities.py`**
- **Current State:** Does not exist (new file)
- **Changes Required:**
  - CREATE: Complete test file (450 lines)
  - ADD: 5 capability detection tests (150 lines)
  - ADD: 5 insider trading tests (150 lines)
  - ADD: 3 trade desk capability tests (100 lines)
  - ADD: Test fixtures and helpers (50 lines)
- **Breaking Change:** NO (new tests)
- **Lines of Code:** +450, -0
- **Estimated Time:** 6 hours
- **Testing Impact:** 13 new tests

**Database Module Total:** 2 files, 1,050 lines added, 0 lines removed, 14 hours estimated

---

### COMPLETE FILE MODIFICATION SUMMARY

| Module | Files | Lines Added | Lines Removed | Net Change | Est. Hours | Critical |
|--------|-------|-------------|---------------|------------|------------|----------|
| Partners | 9 | 1,007 | 81 | +926 | 26 | HIGH |
| Trade Desk | 4 | 245 | 6 | +239 | 10.5 | HIGH |
| Risk | 2 | 66 | 122 | -56 | 5 | MEDIUM |
| Settings | 1 | 32 | 8 | +24 | 1 | LOW |
| AI | 3 | 168 | 96 | +72 | 7.5 | LOW |
| Database | 2 | 1,050 | 0 | +1,050 | 14 | HIGH |
| **TOTAL** | **21** | **2,568** | **313** | **+2,255** | **64** | - |

**Calendar Time:** 64 hours ÷ 8 hours/day = **8 working days**  
**With testing buffer:** 8 + 2 days = **10 working days**

---

## 🧪 COMPREHENSIVE TESTING STRATEGY FOR APPROVAL

### Category 1: Capability Detection Tests (5 tests)

**Test 1: Indian Domestic Capability Detection

```python
async def test_indian_domestic_capability_detection(db):
    """
    Given: Indian partner with GST + PAN (both verified)
    When: Capability detection runs
    Then: domestic_buy_india=True, domestic_sell_india=True
    """
    # Arrange
    partner = await create_partner(country="India")
    await upload_document(partner.id, "gst_certificate", verified=True)
    await upload_document(partner.id, "pan_card", verified=True)
    
    # Act
    service = CapabilityDetectionService(db, emitter)
    result = await service.update_partner_capabilities(partner.id)
    
    # Assert
    assert result.capabilities["domestic_buy_india"] == True
    assert result.capabilities["domestic_sell_india"] == True
    assert result.capabilities["import_allowed"] == False
    assert result.capabilities["export_allowed"] == False
    assert "GST" in result.capabilities["detected_from_documents"]
    assert "PAN" in result.capabilities["detected_from_documents"]
```

### Test 2: IEC Requires GST+PAN (Strong Validation)

```python
async def test_iec_requires_gst_and_pan(db):
    """
    Given: Indian partner with IEC only (no GST/PAN)
    When: Capability detection runs
    Then: import_allowed=False, export_allowed=False
    """
    # Arrange
    partner = await create_partner(country="India")
    await upload_document(partner.id, "iec", verified=True)
    # NO GST or PAN
    
    # Act
    service = CapabilityDetectionService(db, emitter)
    result = await service.update_partner_capabilities(partner.id)
    
    # Assert
    assert result.capabilities["import_allowed"] == False
    assert result.capabilities["export_allowed"] == False
    assert "IEC_INCOMPLETE" in result.capabilities["detected_from_documents"]
```

### Test 3: Valid Import/Export with All 3 Documents

```python
async def test_valid_import_export_with_all_documents(db):
    """
    Given: Indian partner with IEC + GST + PAN (all verified)
    When: Capability detection runs
    Then: All capabilities = True
    """
    # Arrange
    partner = await create_partner(country="India")
    await upload_document(partner.id, "iec", verified=True)
    await upload_document(partner.id, "gst_certificate", verified=True)
    await upload_document(partner.id, "pan_card", verified=True)
    
    # Act
    service = CapabilityDetectionService(db, emitter)
    result = await service.update_partner_capabilities(partner.id)
    
    # Assert
    assert result.capabilities["domestic_buy_india"] == True
    assert result.capabilities["domestic_sell_india"] == True
    assert result.capabilities["import_allowed"] == True
    assert result.capabilities["export_allowed"] == True
    assert "IEC" in result.capabilities["detected_from_documents"]
    assert "GST" in result.capabilities["detected_from_documents"]
    assert "PAN" in result.capabilities["detected_from_documents"]
```

### Test 4: Foreign Domestic Capability

```python
async def test_foreign_domestic_capability(db):
    """
    Given: USA partner with Foreign Tax ID
    When: Capability detection runs
    Then: domestic_buy_home_country=True, domestic_sell_home_country=True
    """
    # Arrange
    partner = await create_partner(country="USA")
    await upload_document(partner.id, "foreign_tax_id", verified=True)
    
    # Act
    service = CapabilityDetectionService(db, emitter)
    result = await service.update_partner_capabilities(partner.id)
    
    # Assert
    assert result.capabilities["domestic_buy_india"] == False
    assert result.capabilities["domestic_sell_india"] == False
    assert result.capabilities["domestic_buy_home_country"] == True
    assert result.capabilities["domestic_sell_home_country"] == True
    assert result.capabilities["import_allowed"] == False
    assert result.capabilities["export_allowed"] == False
```

### Test 5: Trade Desk India Posting Validation

```python
async def test_availability_posting_india_requires_domestic_sell_india(db):
    """
    Given: Partner without domestic_sell_india capability
    When: Try to post availability in India
    Then: Raises ValueError
    """
    # Arrange
    partner = await create_partner(
        country="India",
        capabilities={
            "domestic_buy_india": True,
            "domestic_sell_india": False,  # Missing sell capability
            "import_allowed": False,
            "export_allowed": False
        }
    )
    availability_service = AvailabilityService(db)
    
    # Act & Assert
    with pytest.raises(ValueError) as exc:
        await availability_service._validate_seller_capabilities(
            partner_id=partner.id,
            posting_location="India",
            is_export=False
        )
    
    assert "does not have domestic_sell_india capability" in str(exc.value)
    assert "GST + PAN" in str(exc.value)
```

### Test 6: Service Provider Cannot Trade

```python
async def test_service_provider_cannot_post_availability(db):
    """
    Given: Service provider (broker)
    When: Try to post availability
    Then: Raises ValueError
    """
    # Arrange
    broker = await create_partner(
        entity_class="service_provider",
        service_provider_type="broker"
    )
    availability_service = AvailabilityService(db)
    
    # Act & Assert
    with pytest.raises(ValueError) as exc:
        await availability_service._validate_seller_capabilities(
            partner_id=broker.id,
            posting_location="India",
            is_export=False
        )
    
    assert "service providers" in str(exc.value).lower()
    assert "broker" in str(exc.value).lower()
```

### Test 7: Insider Trading - Same GST Blocked

```python
async def test_insider_trading_same_gst_blocked(db):
    """
    Given: Two partners with same GST number
    When: Try to match availability and requirement
    Then: Blocked with SAME_GST_GROUP violation
    """
    # Arrange
    gst_number = "29ABCDE1234F1Z5"
    buyer = await create_partner(country="India")
    await upload_document(buyer.id, "gst_certificate", data={"gst_number": gst_number})
    
    seller = await create_partner(country="India")
    await upload_document(seller.id, "gst_certificate", data={"gst_number": gst_number})
    
    validator = InsiderTradingValidator(db)
    
    # Act
    result = await validator.validate_trade_parties(
        buyer_id=buyer.id,
        seller_id=seller.id,
        db=db
    )
    
    # Assert
    assert result["allowed"] == False
    assert result["violation_type"] == "SAME_GST_GROUP"
```

---

## 📅 DETAILED IMPLEMENTATION PHASES FOR APPROVAL

### PHASE 1: Database Schema Changes (Days 1-2) - FOUNDATION

#### Day 1 Morning (4 hours) - Enums & Models Setup
**Tasks:**
1. **Update `partners/enums.py`** (1 hour)
   - [ ] Add BusinessEntityType enum (10 values)
   - [ ] Add ServiceProviderType enum (6 values)
   - [ ] Add new DocumentType values (IEC, FOREIGN_TAX_ID, FOREIGN_IMPORT_LICENSE, FOREIGN_EXPORT_LICENSE)
   - [ ] Add deprecation comment to PartnerType enum
   - [ ] Delete TradeClassification enum
   - [ ] Run import tests to verify enums are accessible

2. **Update `partners/models.py` - Part 1** (3 hours)
   - [ ] Add entity_class column (Enum)
   - [ ] Add business_entity_type column (nullable)
   - [ ] Add service_provider_type column (nullable)
   - [ ] Add capabilities column (JSONB with default)
   - [ ] Test model changes with alembic check

**Deliverables:**
- ✅ Updated enums file with new types
- ✅ Model file with new columns (old columns still present)
- ✅ No import errors

**Validation:**
```bash
# Run these commands
cd backend
python -c "from modules.partners.enums import BusinessEntityType; print(BusinessEntityType.PRIVATE_LIMITED)"
alembic check
```

---

#### Day 1 Afternoon (4 hours) - Entity Hierarchy & Constraints
**Tasks:**
1. **Update `partners/models.py` - Part 2** (2 hours)
   - [ ] Add master_entity_id column (UUID, ForeignKey)
   - [ ] Add corporate_group_id column (UUID)
   - [ ] Add is_master_entity column (Boolean)
   - [ ] Add entity_hierarchy column (JSONB)
   - [ ] Add check constraint for entity_class logic

2. **Update `settings/business_partners/models.py`** (1 hour)
   - [ ] Apply same changes (simplified version)
   - [ ] Update imports

3. **Code Review** (1 hour)
   - [ ] Review all model changes
   - [ ] Verify column types and constraints
   - [ ] Check for syntax errors

**Deliverables:**
- ✅ Complete model updates
- ✅ Settings model updated
- ✅ All constraints defined

**Validation:**
```bash
# Validate models
python -c "from modules.partners.models import BusinessPartner; print(BusinessPartner.__table__.columns.keys())"
```

---

#### Day 2 Morning (4 hours) - Migration Script Creation
**Tasks:**
1. **Create Migration File** (4 hours)
   - [ ] Generate migration: `alembic revision -m "add_capability_system"`
   - [ ] Write upgrade() function:
     - [ ] Add new columns (all nullable initially)
     - [ ] Create entity_class enum type
     - [ ] Create service_provider_type enum type
   - [ ] Write data migration SQL:
     - [ ] Service providers conversion (6 types)
     - [ ] Business entities - domestic (seller/buyer/trader)
     - [ ] Business entities - importers/exporters
     - [ ] Foreign entities
   - [ ] Test migration on local database copy

**Deliverables:**
- ✅ Complete migration file (600 lines)
- ✅ Data conversion logic for all partner types
- ✅ Successfully runs upgrade on local DB

**Validation:**
```bash
# Test migration
alembic upgrade head
psql -d cotton_erp -c "SELECT COUNT(*) FROM business_partners WHERE capabilities IS NULL;"
# Expected: 0
```

---

#### Day 2 Afternoon (4 hours) - Migration Testing & Rollback
**Tasks:**
1. **Complete Migration** (2 hours)
   - [ ] Add NOT NULL constraints
   - [ ] Add JSONB indexes (4 indexes)
   - [ ] Add check constraints
   - [ ] Drop old columns (partner_type, trade_classification, etc.)

2. **Write Rollback Function** (1.5 hours)
   - [ ] Write downgrade() function
   - [ ] Reconstruct partner_type from capabilities
   - [ ] Test rollback on local DB

3. **Data Integrity Verification** (0.5 hours)
   - [ ] Run verification queries
   - [ ] Check counts match before/after
   - [ ] Verify no data loss

**Deliverables:**
- ✅ Complete migration with rollback
- ✅ All indexes created
- ✅ Data integrity verified

**Validation:**
```sql
-- Verify migration
SELECT 
    entity_class,
    COUNT(*) 
FROM business_partners 
GROUP BY entity_class;

-- Test rollback
alembic downgrade -1
SELECT COUNT(*) FROM business_partners WHERE partner_type IS NOT NULL;
-- Then upgrade again
alembic upgrade head
```

**Phase 1 Completion Criteria:**
- ✅ All new columns added
- ✅ Migration runs successfully
- ✅ Rollback works
- ✅ No data loss
- ✅ All indexes created

---

### PHASE 2: Core Business Logic (Days 3-4) - CAPABILITY DETECTION

#### Day 3 Morning (4 hours) - Capability Detection Service
**Tasks:**
1. **Create CapabilityDetectionService class** (4 hours)
   - [ ] Create new file: `partners/services/capability_detection.py`
   - [ ] Implement detect_indian_domestic_capability() method
     - [ ] Check for GST + PAN (both verified)
     - [ ] Return domestic_buy_india, domestic_sell_india
   - [ ] Implement detect_import_export_capability() method
     - [ ] Check for IEC + GST + PAN (all three verified)
     - [ ] Block if IEC exists without GST/PAN
     - [ ] Return import_allowed, export_allowed
   - [ ] Add logging for detection events

**Deliverables:**
- ✅ CapabilityDetectionService with 2 detection methods
- ✅ Proper validation (IEC requires GST+PAN)
- ✅ Comprehensive logging

**Validation:**
```python
# Test detection
service = CapabilityDetectionService(db, emitter)
result = await service.detect_indian_domestic_capability(partner_id)
assert result["domestic_buy_india"] == True
```

---

#### Day 3 Afternoon (4 hours) - Foreign Entity Detection
**Tasks:**
1. **Complete Detection Service** (4 hours)
   - [ ] Implement detect_foreign_domestic_capability() method
     - [ ] Check for Foreign Tax ID (verified)
     - [ ] Return domestic_buy_home_country, domestic_sell_home_country
   - [ ] Implement detect_foreign_import_export_capability() method
     - [ ] Check for Foreign Import/Export licenses
     - [ ] Return import_allowed, export_allowed separately
   - [ ] Implement update_partner_capabilities() main method
     - [ ] Orchestrate all 4 detection rules
     - [ ] Block service providers
     - [ ] Merge results and save to database
   - [ ] Add to `partners/services/__init__.py`

**Deliverables:**
- ✅ Complete CapabilityDetectionService (300 lines)
- ✅ All 4 detection rules implemented
- ✅ Service provider blocking logic

**Validation:**
```python
# Test all rules
service = CapabilityDetectionService(db, emitter)
partner = await service.update_partner_capabilities(partner_id)
assert "detected_from_documents" in partner.capabilities
```

---

#### Day 4 Morning (4 hours) - Insider Trading Validator
**Tasks:**
1. **Create InsiderTradingValidator class** (4 hours)
   - [ ] Create new file: `partners/validators/insider_trading.py`
   - [ ] Implement validate_trade_parties() method
   - [ ] Add Rule 1: Same entity check
   - [ ] Add Rule 2: Master-branch / sibling branches check
   - [ ] Add Rule 3: Corporate group check
   - [ ] Add Rule 4: Same GST check
   - [ ] Implement helper method: _get_gst_number()
   - [ ] Add detailed error messages for each violation

**Deliverables:**
- ✅ InsiderTradingValidator class (150 lines)
- ✅ All 4 blocking rules implemented
- ✅ Clear violation messages

**Validation:**
```python
# Test blocking
validator = InsiderTradingValidator(db)
result = await validator.validate_trade_parties(buyer_id, seller_id, db)
assert result["allowed"] == False
assert result["violation_type"] == "SAME_ENTITY"
```

---

#### Day 4 Afternoon (4 hours) - Integration & Events
**Tasks:**
1. **Add Capability Events** (1.5 hours)
   - [ ] Create `partners/events.py` additions
   - [ ] Add CapabilitiesDetectedEvent
   - [ ] Add CapabilitiesManuallyOverriddenEvent
   - [ ] Add CapabilitiesResetToAutoDetectEvent

2. **Integrate Detection into Workflows** (2.5 hours)
   - [ ] Update DocumentProcessingService.verify_document_ocr()
     - [ ] Add capability detection trigger after verification
   - [ ] Update ApprovalService.process_approval()
     - [ ] Add capability detection trigger after approval
   - [ ] Test integration points

**Deliverables:**
- ✅ 3 new event classes
- ✅ Auto-detection triggers in place
- ✅ Events emitted correctly

**Validation:**
```python
# Verify integration
# Approve document → capability detection should run
await doc_service.verify_document_ocr(doc_id)
partner = await repo.get_by_id(partner_id)
assert partner.capabilities["auto_detected"] == True
```

**Phase 2 Completion Criteria:**
- ✅ CapabilityDetectionService fully functional
- ✅ All 4 detection rules working
- ✅ InsiderTradingValidator blocking related parties
- ✅ Auto-detection integrated into workflows
- ✅ Unit tests written (10 tests)

---

### PHASE 3: Trade Desk Integration (Days 5-6) - VALIDATION LOGIC

#### Day 5 Morning (4 hours) - Availability Service Validation
**Tasks:**
1. **Update AvailabilityService** (4 hours)
   - [ ] Open `trade_desk/services/availability_service.py`
   - [ ] Delete TODO comment at lines 798-801
   - [ ] Implement _validate_seller_capabilities() method:
     - [ ] Check entity_class (block service providers)
     - [ ] Check posting_location parameter
     - [ ] If posting in India → require domestic_sell_india
     - [ ] If export posting → require export_allowed
     - [ ] If foreign posting → require domestic_sell_home_country
     - [ ] Raise ValueError with specific messages
   - [ ] Add validation call in create_availability() method
   - [ ] Update method signature to accept location parameter

**Deliverables:**
- ✅ _validate_seller_capabilities() method (55 lines)
- ✅ Service providers blocked from posting
- ✅ Location-aware validation working

**Validation:**
```python
# Test validation
with pytest.raises(ValueError) as exc:
    await service._validate_seller_capabilities(
        partner_id=broker_id,
        posting_location="India",
        is_export=False
    )
assert "service providers" in str(exc.value)
```

---

#### Day 5 Afternoon (4 hours) - Requirement Service Validation
**Tasks:**
1. **Update RequirementService** (4 hours)
   - [ ] Open `trade_desk/services/requirement_service.py`
   - [ ] Delete TODO comment at line 1432
   - [ ] Implement _validate_buyer_capabilities() method:
     - [ ] Check entity_class (block service providers)
     - [ ] Check buying_location parameter
     - [ ] If buying in India → require domestic_buy_india
     - [ ] If import requirement → require import_allowed
     - [ ] If foreign buying → require domestic_buy_home_country
     - [ ] Raise ValueError with specific messages
   - [ ] Add validation call in create_requirement() method
   - [ ] Update method signature to accept location parameter

**Deliverables:**
- ✅ _validate_buyer_capabilities() method (55 lines)
- ✅ Service providers blocked from posting
- ✅ Location-aware validation working

**Validation:**
```python
# Test validation
partner = create_partner(capabilities={"domestic_buy_india": False})
with pytest.raises(ValueError) as exc:
    await service._validate_buyer_capabilities(
        partner_id=partner.id,
        buying_location="India"
    )
assert "does not have domestic_buy_india" in str(exc.value)
```

---

#### Day 6 Morning (4 hours) - Matching Validation
**Tasks:**
1. **Update MatchValidator** (4 hours)
   - [ ] Open `trade_desk/matching/validators.py`
   - [ ] Import InsiderTradingValidator
   - [ ] Update validate_match_eligibility() method:
     - [ ] Add insider trading check (call validate_trade_parties)
     - [ ] Add buyer capability validation
     - [ ] Add seller capability validation
     - [ ] Add location-aware checks
     - [ ] Append violation reasons to ValidationResult
   - [ ] Add helper methods for capability checks

**Deliverables:**
- ✅ Insider trading check in matching
- ✅ Capability validation in matching
- ✅ Detailed rejection reasons

**Validation:**
```python
# Test matching validation
result = await validator.validate_match_eligibility(requirement, availability)
assert result.is_valid == False
assert "Insider trading violation" in result.reasons[0]
```

---

#### Day 6 Afternoon (4 hours) - Schema Updates & Testing
**Tasks:**
1. **Update Trade Desk Schemas** (1 hour)
   - [ ] Open `trade_desk/schemas/__init__.py`
   - [ ] Delete partner_type field (line 239)

2. **Integration Testing** (3 hours)
   - [ ] Test end-to-end flow:
     - [ ] Create availability (valid partner)
     - [ ] Create requirement (valid partner)
     - [ ] Match them (should succeed)
   - [ ] Test blocking scenarios:
     - [ ] Service provider tries to post → blocked
     - [ ] Partner without capability → blocked
     - [ ] Related parties try to match → blocked
   - [ ] Fix any issues found

**Deliverables:**
- ✅ Schema updated
- ✅ End-to-end flows working
- ✅ All blocking scenarios validated

**Validation:**
```bash
# Run integration tests
pytest backend/modules/trade_desk/tests/test_integration.py -v
```

**Phase 3 Completion Criteria:**
- ✅ Availability posting validates capabilities
- ✅ Requirement posting validates capabilities
- ✅ Matching validates capabilities + insider trading
- ✅ Service providers cannot post
- ✅ Integration tests passing

---

### PHASE 4: Risk Engine & Schemas (Day 7) - SYSTEM-WIDE UPDATES

#### Day 7 Morning (4 hours) - Risk Engine Update
**Tasks:**
1. **Update RiskEngine** (4 hours)
   - [ ] Open `risk/risk_engine.py`
   - [ ] Locate validate_partner_role() method (lines 884-994)
   - [ ] Delete entire method (110 lines)
   - [ ] Implement new validate_partner_role() method:
     - [ ] Accept parameters: partner_id, transaction_type ("BUY"/"SELL")
     - [ ] Get partner from database
     - [ ] Block if entity_class == "service_provider"
     - [ ] If transaction_type == "BUY":
       - [ ] Check capabilities["domestic_buy_india"] OR capabilities["import_allowed"]
     - [ ] If transaction_type == "SELL":
       - [ ] Check capabilities["domestic_sell_india"] OR capabilities["export_allowed"]
     - [ ] Raise appropriate exceptions
   - [ ] Test risk engine with new method

**Deliverables:**
- ✅ New validate_partner_role() method (66 lines)
- ✅ Capability-based validation
- ✅ Service provider blocking

**Validation:**
```python
# Test risk engine
await risk_engine.validate_partner_role(
    partner_id=partner.id,
    transaction_type="SELL"
)
# Should pass if domestic_sell_india or export_allowed
```

---

#### Day 7 Afternoon (4 hours) - Schema Cleanup & Testing
**Tasks:**
1. **Update Risk Schemas** (1 hour)
   - [ ] Open `risk/schemas.py`
   - [ ] Delete partner_type fields (lines 40-45, 199, 206, 346-347)
   - [ ] Update any validators that reference partner_type

2. **Update Partner Schemas** (1.5 hours)
   - [ ] Open `partners/schemas.py`
   - [ ] Delete all partner_type fields
   - [ ] Add OnboardingApplicationCreate with entity_class
   - [ ] Add CapabilityResponse schema
   - [ ] Add CapabilityOverrideRequest schema
   - [ ] Update BusinessPartnerResponse to include capabilities

3. **Testing** (1.5 hours)
   - [ ] Run risk engine tests
   - [ ] Update failing tests
   - [ ] Verify contract engine still works (uses risk engine)

**Deliverables:**
- ✅ All schemas updated
- ✅ No partner_type references in risk module
- ✅ Tests passing

**Validation:**
```bash
pytest backend/modules/risk/tests/ -v
pytest backend/modules/partners/tests/test_schemas.py -v
```

**Phase 4 Completion Criteria:**
- ✅ Risk engine uses capabilities
- ✅ No partner_type in risk module
- ✅ All schemas updated
- ✅ Contract engine working

---

### PHASE 5: API & Repositories (Day 8) - EXTERNAL INTERFACE

#### Day 8 Morning (4 hours) - Repository Updates
**Tasks:**
1. **Update PartnerRepository** (4 hours)
   - [ ] Open `partners/repositories.py`
   - [ ] Delete partner_type filter parameters
   - [ ] Implement new filter methods:
     - [ ] filter_by_entity_class(entity_class: str)
     - [ ] filter_by_domestic_buy_india(value: bool)
     - [ ] filter_by_domestic_sell_india(value: bool)
     - [ ] filter_by_import_capability(value: bool)
     - [ ] filter_by_export_capability(value: bool)
   - [ ] Implement JSONB query helpers
   - [ ] Update list_partners() method to use new filters
   - [ ] Add update_capabilities() method

**Deliverables:**
- ✅ 5 new filter methods
- ✅ JSONB queries working
- ✅ Backward compatibility maintained

**Validation:**
```python
# Test filters
partners = await repo.filter_by_domestic_sell_india(True)
assert all(p.capabilities.get("domestic_sell_india") for p in partners)
```

---

#### Day 8 Afternoon (4 hours) - Router & API Endpoints
**Tasks:**
1. **Update Partner Router** (4 hours)
   - [ ] Open `partners/router.py`
   - [ ] Add POST /partners/{id}/capabilities/detect endpoint
     - [ ] Call CapabilityDetectionService
     - [ ] Return updated capabilities
   - [ ] Add PUT /partners/{id}/capabilities/override endpoint
     - [ ] Accept CapabilityOverrideRequest
     - [ ] Set manual_override = True
     - [ ] Emit override event
   - [ ] Add POST /partners/{id}/entity-hierarchy endpoint
     - [ ] Update master_entity_id, corporate_group_id
   - [ ] Update existing endpoints to use new schemas
   - [ ] Test all endpoints with Postman/curl

**Deliverables:**
- ✅ 3 new API endpoints
- ✅ Existing endpoints updated
- ✅ API documentation updated

**Validation:**
```bash
# Test endpoints
curl -X POST http://localhost:8000/api/partners/{id}/capabilities/detect
curl -X PUT http://localhost:8000/api/partners/{id}/capabilities/override \
  -H "Content-Type: application/json" \
  -d '{"capabilities": {...}, "reason": "Manual correction"}'
```

**Phase 5 Completion Criteria:**
- ✅ All repository filters working
- ✅ 3 new endpoints functional
- ✅ API contracts updated
- ✅ Backward compatibility maintained

---

### PHASE 6: AI & Notifications (Day 9) - SUPPORTING SYSTEMS

#### Day 9 Morning (4 hours) - AI Assistant Updates
**Tasks:**
1. **Update Partner Assistant** (4 hours)
   - [ ] Open `ai/assistants/partner_assistant/assistant.py`
   - [ ] Replace all partner_type with entity_class
   - [ ] Update assist_onboarding_start() method:
     - [ ] Ask: "Service Provider or Business Entity?"
     - [ ] If service provider → ask type
     - [ ] If business entity → ask type
   - [ ] Update _estimate_onboarding_time() method
   - [ ] Open `ai/assistants/partner_assistant/tools.py`
   - [ ] Split get_onboarding_requirements() into:
     - [ ] get_service_provider_requirements()
     - [ ] get_business_entity_requirements()
   - [ ] Open `ai/prompts/partner/prompts.py`
   - [ ] Update prompt templates

**Deliverables:**
- ✅ AI assistant uses entity_class
- ✅ Onboarding flow updated
- ✅ Requirements split by entity type

**Validation:**
```python
# Test AI assistant
response = await assistant.assist_onboarding_start(
    entity_class="service_provider",
    service_provider_type="broker"
)
assert "broker" in response.lower()
```

---

#### Day 9 Afternoon (4 hours) - Notifications & Services
**Tasks:**
1. **Update Notification Templates** (1 hour)
   - [ ] Open `partners/notifications.py`
   - [ ] Update approval email template (line 170)
   - [ ] Replace partner_type display with capabilities
   - [ ] Add capability summary section

2. **Update Partner Services** (2 hours)
   - [ ] Open `partners/services.py`
   - [ ] Remove all remaining partner_type references
   - [ ] Update any service methods using old fields
   - [ ] Test all service methods

3. **Code Review** (1 hour)
   - [ ] Search codebase for "partner_type"
   - [ ] Search codebase for "trade_classification"
   - [ ] Ensure all references removed or deprecated

**Deliverables:**
- ✅ Email templates updated
- ✅ No partner_type in services
- ✅ Codebase clean

**Validation:**
```bash
# Search for old references
grep -r "partner_type" backend/modules/partners/ | grep -v "migration" | grep -v ".pyc"
# Should return minimal results (only deprecation comments)
```

**Phase 6 Completion Criteria:**
- ✅ AI assistant working with new system
- ✅ Notifications showing capabilities
- ✅ No active partner_type references
- ✅ All services updated

---

### PHASE 7: Comprehensive Testing (Day 10) - VALIDATION

#### Day 10 Morning (4 hours) - Unit Tests
**Tasks:**
1. **Create New Test File** (4 hours)
   - [ ] Create `partners/tests/test_capabilities.py`
   - [ ] Write Test 1: Indian domestic detection (GST+PAN)
   - [ ] Write Test 2: IEC requires GST+PAN (strong validation)
   - [ ] Write Test 3: Valid import/export (all 3 docs)
   - [ ] Write Test 4: Foreign domestic capability
   - [ ] Write Test 5: Foreign import/export licenses
   - [ ] Write Test 6: Same entity blocked
   - [ ] Write Test 7: Master-branch blocked
   - [ ] Write Test 8: Sibling branches blocked
   - [ ] Write Test 9: Corporate group blocked
   - [ ] Write Test 10: Same GST blocked
   - [ ] Write Test 11: Service provider cannot post availability
   - [ ] Write Test 12: No buy capability cannot post requirement
   - [ ] Write Test 13: Valid unrelated partners can match

**Deliverables:**
- ✅ 13 new tests (450 lines)
- ✅ All tests passing
- ✅ Test coverage >85%

**Validation:**
```bash
pytest backend/modules/partners/tests/test_capabilities.py -v --cov
```

---

#### Day 10 Afternoon (4 hours) - Integration & Regression Testing
**Tasks:**
1. **Update Existing Test Fixtures** (2 hours)
   - [ ] Update all test fixtures to use entity_class
   - [ ] Replace partner_type with capabilities in fixtures
   - [ ] Update factory functions

2. **Run Full Test Suite** (1.5 hours)
   - [ ] Run all partner module tests
   - [ ] Run all trade desk module tests
   - [ ] Run all risk module tests
   - [ ] Run all AI module tests
   - [ ] Fix any failing tests

3. **Manual Testing** (0.5 hours)
   - [ ] Test onboarding flow end-to-end
   - [ ] Test capability auto-detection
   - [ ] Test availability/requirement posting
   - [ ] Test matching with insider trading

**Deliverables:**
- ✅ All existing tests updated
- ✅ Full test suite passing
- ✅ Manual testing complete

**Validation:**
```bash
# Run full suite
pytest backend/modules/partners/ -v
pytest backend/modules/trade_desk/ -v
pytest backend/modules/risk/ -v
pytest backend/ai/ -v

# Check coverage
pytest --cov=backend/modules/partners --cov-report=html
```

**Phase 7 Completion Criteria:**
- ✅ 13 new tests passing
- ✅ All existing tests passing
- ✅ Test coverage >80%
- ✅ Manual testing successful

---

### PHASE 8: Deployment (Days 11-12) - PRODUCTION ROLLOUT

#### Day 11: Staging Deployment
**Tasks:**
1. **Deploy to Staging** (2 hours)
   - [ ] Create staging deployment branch
   - [ ] Deploy code to staging environment
   - [ ] Backup staging database
   - [ ] Run migration on staging

2. **Staging Validation** (4 hours)
   - [ ] Verify all partners migrated correctly
   - [ ] Run data integrity checks
   - [ ] Test all API endpoints
   - [ ] Test capability detection
   - [ ] Test insider trading blocking

3. **User Acceptance Testing** (2 hours)
   - [ ] Stakeholder testing of key flows
   - [ ] Gather feedback
   - [ ] Fix any issues

**Deliverables:**
- ✅ Staging deployment successful
- ✅ Migration verified on production-like data
- ✅ UAT complete

---

#### Day 12: Production Deployment
**Tasks:**
1. **Pre-Deployment** (1 hour)
   - [ ] Final code review
   - [ ] Backup production database
   - [ ] Schedule deployment window

2. **Production Deployment** (2 hours)
   - [ ] Deploy to blue environment (blue-green deployment)
   - [ ] Run migration on production database
   - [ ] Verify migration success
   - [ ] Run smoke tests

3. **Cutover & Monitoring** (1 hour)
   - [ ] Switch traffic to blue environment
   - [ ] Monitor error rates
   - [ ] Monitor API response times
   - [ ] Check capability detection running

4. **Post-Deployment** (4 hours)
   - [ ] 24-hour monitoring
   - [ ] Address any issues
   - [ ] Gather metrics
   - [ ] Document lessons learned

**Deliverables:**
- ✅ Production deployment successful
- ✅ Zero downtime achieved
- ✅ All systems operational
- ✅ Rollback plan ready (if needed)

**Phase 8 Completion Criteria:**
- ✅ Code deployed to production
- ✅ Migration successful
- ✅ All services running normally
- ✅ No critical errors in 24 hours

---

## 📝 COMPREHENSIVE APPROVAL CHECKLIST

### SECTION A: Technical Architecture Approval

#### A1. Database Schema Changes ✅
**Approve the following database changes:**

- [ ] **DELETE Columns:**
  - `partner_type` (VARCHAR) - 11 enum values
  - `trade_classification` (VARCHAR) - 3 enum values
  - `is_buyer` (BOOLEAN)
  - `is_seller` (BOOLEAN)
  - `is_trader` (BOOLEAN)

- [ ] **ADD Columns:**
  - `entity_class` (ENUM: "business_entity", "service_provider") - NOT NULL
  - `business_entity_type` (ENUM: 10 values) - NULLABLE
  - `service_provider_type` (ENUM: 6 values) - NULLABLE
  - `capabilities` (JSONB) - NOT NULL with default {}
  - `master_entity_id` (UUID, ForeignKey) - NULLABLE
  - `corporate_group_id` (UUID) - NULLABLE
  - `is_master_entity` (BOOLEAN) - Default FALSE
  - `entity_hierarchy` (JSONB) - Default {}

- [ ] **ADD Indexes:**
  - `idx_capabilities_domestic_buy_india` (JSONB index)
  - `idx_capabilities_domestic_sell_india` (JSONB index)
  - `idx_capabilities_import` (JSONB index)
  - `idx_capabilities_export` (JSONB index)
  - `idx_entity_class` (Standard index)
  - `idx_master_entity` (Standard index)
  - `idx_corporate_group` (Standard index)

- [ ] **ADD Constraints:**
  - Check constraint: entity_class + type consistency
  - Foreign key: master_entity_id → business_partners.id

**Impact:** ~1,250 existing partners will be migrated  
**Downtime:** <5 minutes for migration  
**Rollback Time:** <3 minutes if needed

**Approved By:** _________________ **Date:** _________

---

#### A2. Capability Detection Rules ✅
**Approve the following auto-detection logic:**

**Rule A: Indian Domestic Trading**
```
IF (GST Certificate verified) AND (PAN Card verified):
  ✅ GRANT domestic_buy_india = TRUE
  ✅ GRANT domestic_sell_india = TRUE
```

**Rule B: Indian Import/Export (STRONG VALIDATION)**
```
IF (IEC verified) AND (GST verified) AND (PAN verified):
  ✅ GRANT import_allowed = TRUE
  ✅ GRANT export_allowed = TRUE

IF (IEC verified) AND (GST missing OR PAN missing):
  ❌ DENY import_allowed
  ❌ DENY export_allowed
  ⚠️  LOG WARNING: "IEC incomplete - requires GST+PAN"
```

**Rule C: Foreign Domestic Trading**
```
IF (Foreign Tax ID verified):
  ✅ GRANT domestic_buy_home_country = TRUE
  ✅ GRANT domestic_sell_home_country = TRUE
  ❌ DENY domestic_buy_india
  ❌ DENY domestic_sell_india
```

**Rule D: Foreign Import/Export**
```
IF (Foreign Import License verified):
  ✅ GRANT import_allowed = TRUE

IF (Foreign Export License verified):
  ✅ GRANT export_allowed = TRUE
```

**Rule E: Service Providers**
```
IF (entity_class = "service_provider"):
  ❌ DENY ALL trading capabilities
  ✅ SET detected_from_documents = ["SERVICE_PROVIDER_NO_TRADING"]
```

**Business Impact:**
- Partners gain capabilities automatically upon document verification
- Manual overrides available for exceptions
- Clear audit trail of capability changes

**Approved By:** _________________ **Date:** _________

---

#### A3. Insider Trading Prevention ✅
**Approve the following blocking rules:**

**Blocking Rule 1: Same Entity**
```
IF (buyer_id == seller_id):
  ❌ BLOCK with reason: "Cannot trade with yourself"
```

**Blocking Rule 2: Master-Branch Trading**
```
IF (buyer.is_master_entity AND seller.master_entity_id == buyer.id):
  ❌ BLOCK with reason: "Cannot trade between master entity and its branch"

IF (seller.is_master_entity AND buyer.master_entity_id == seller.id):
  ❌ BLOCK with reason: "Cannot trade between master entity and its branch"
```

**Blocking Rule 3: Sibling Branches**
```
IF (buyer.master_entity_id == seller.master_entity_id) AND (master_entity_id IS NOT NULL):
  ❌ BLOCK with reason: "Cannot trade between branches of same master entity"
```

**Blocking Rule 4: Corporate Group**
```
IF (buyer.corporate_group_id == seller.corporate_group_id) AND (corporate_group_id IS NOT NULL):
  ❌ BLOCK with reason: "Cannot trade within same corporate group"
```

**Blocking Rule 5: Same GST Group (India only)**
```
IF (buyer.country == "India") AND (seller.country == "India"):
  IF (buyer.gst_number == seller.gst_number) AND (gst_number IS NOT NULL):
    ❌ BLOCK with reason: "Cannot trade between entities with same GST number"
```

**Business Impact:**
- Prevents circular trading within related entities
- Compliance with regulatory requirements
- Reduces financial risk

**Approved By:** _________________ **Date:** _________

---

#### A4. Trade Desk Validation Logic ✅
**Approve the following posting validations:**

**Availability Posting (Seller Side):**
```python
# Service Providers
IF (entity_class == "service_provider"):
  ❌ REJECT with: "Service providers cannot post availabilities"

# India Domestic Posting
IF (posting_location == "India") AND (is_export == False):
  REQUIRE: capabilities["domestic_sell_india"] == True
  REJECT with: "Missing domestic_sell_india capability. Required: GST+PAN verified"

# Export Posting
IF (is_export == True):
  REQUIRE: capabilities["export_allowed"] == True
  REJECT with: "Missing export_allowed capability. Required: IEC+GST+PAN verified"

# Foreign Domestic Posting
IF (posting_location != "India") AND (is_export == False):
  REQUIRE: capabilities["domestic_sell_home_country"] == True
  REJECT with: "Missing domestic_sell_home_country capability. Required: Foreign Tax ID verified"
```

**Requirement Posting (Buyer Side):**
```python
# Service Providers
IF (entity_class == "service_provider"):
  ❌ REJECT with: "Service providers cannot post requirements"

# India Domestic Buying
IF (buying_location == "India") AND (is_import == False):
  REQUIRE: capabilities["domestic_buy_india"] == True
  REJECT with: "Missing domestic_buy_india capability. Required: GST+PAN verified"

# Import Buying
IF (is_import == True):
  REQUIRE: capabilities["import_allowed"] == True
  REJECT with: "Missing import_allowed capability. Required: IEC+GST+PAN verified"

# Foreign Domestic Buying
IF (buying_location != "India") AND (is_import == False):
  REQUIRE: capabilities["domestic_buy_home_country"] == True
  REJECT with: "Missing domestic_buy_home_country capability. Required: Foreign Tax ID verified"
```

**Matching Validation:**
```python
# Insider Trading Check
result = await InsiderTradingValidator.validate_trade_parties(buyer_id, seller_id)
IF (result["allowed"] == False):
  ❌ REJECT match with: result["reason"]

# Capability Check
VALIDATE buyer has required buying capability
VALIDATE seller has required selling capability
IF (any validation fails):
  ❌ REJECT match with specific reason
```

**Business Impact:**
- Prevents invalid postings before they enter the system
- Clear error messages guide partners to complete required documents
- Automated compliance enforcement

**Approved By:** _________________ **Date:** _________

---

### SECTION B: Data Migration Approval

#### B1. Migration Strategy ✅
**Approve the following data conversion logic:**

**Service Providers (broker, sub_broker, transporter, controller, financer, shipping_agent):**
```sql
UPDATE business_partners SET
  entity_class = 'service_provider',
  service_provider_type = [old partner_type value],
  capabilities = '{
    "domestic_buy_india": false,
    "domestic_sell_india": false,
    "domestic_buy_home_country": false,
    "domestic_sell_home_country": false,
    "import_allowed": false,
    "export_allowed": false,
    "auto_detected": false,
    "detected_from_documents": ["MIGRATED_SERVICE_PROVIDER"]
  }'
WHERE partner_type IN ('broker', 'sub_broker', 'transporter', 'controller', 'financer', 'shipping_agent')
```
**Expected:** ~350 partners

**Domestic Sellers:**
```sql
UPDATE business_partners SET
  entity_class = 'business_entity',
  business_entity_type = 'private_limited',
  capabilities = '{
    "domestic_buy_india": false,
    "domestic_sell_india": true,
    "import_allowed": false,
    "export_allowed": false,
    "manual_override": true,
    "override_reason": "Migrated from legacy seller type"
  }'
WHERE partner_type = 'seller' AND country = 'India' AND trade_classification = 'domestic'
```
**Expected:** ~450 partners

**Domestic Buyers:**
```sql
UPDATE business_partners SET
  entity_class = 'business_entity',
  business_entity_type = 'private_limited',
  capabilities = '{
    "domestic_buy_india": true,
    "domestic_sell_india": false,
    "import_allowed": false,
    "export_allowed": false,
    "manual_override": true,
    "override_reason": "Migrated from legacy buyer type"
  }'
WHERE partner_type = 'buyer' AND country = 'India' AND trade_classification = 'domestic'
```
**Expected:** ~380 partners

**Domestic Traders:**
```sql
UPDATE business_partners SET
  entity_class = 'business_entity',
  business_entity_type = 'private_limited',
  capabilities = '{
    "domestic_buy_india": true,
    "domestic_sell_india": true,
    "import_allowed": false,
    "export_allowed": false,
    "manual_override": true,
    "override_reason": "Migrated from legacy trader type"
  }'
WHERE partner_type = 'trader' AND country = 'India' AND trade_classification = 'domestic'
```
**Expected:** ~200 partners

**Indian Importers/Exporters:**
```sql
UPDATE business_partners SET
  entity_class = 'business_entity',
  business_entity_type = 'private_limited',
  capabilities = '{
    "domestic_buy_india": true,
    "domestic_sell_india": true,
    "import_allowed": true,
    "export_allowed": true,
    "manual_override": true,
    "override_reason": "Migrated from legacy importer/exporter type"
  }'
WHERE country = 'India' AND trade_classification IN ('importer', 'exporter')
```
**Expected:** ~120 partners

**Foreign Entities:**
```sql
UPDATE business_partners SET
  entity_class = 'business_entity',
  business_entity_type = 'foreign_entity',
  capabilities = '{
    "domestic_buy_home_country": true,
    "domestic_sell_home_country": true,
    "import_allowed": false,
    "export_allowed": false,
    "manual_override": true,
    "override_reason": "Migrated from legacy foreign partner"
  }'
WHERE country != 'India'
```
**Expected:** ~50 partners

**Total Partners to Migrate:** ~1,250  
**Expected Migration Time:** 2-3 minutes  
**Data Loss Risk:** ZERO (all data preserved, rollback available)

**Approved By:** _________________ **Date:** _________

---

#### B2. Rollback Strategy ✅
**Approve the following rollback mechanism:**

**Automatic Rollback (via alembic downgrade):**
```python
def downgrade():
    # Step 1: Re-add old columns
    op.add_column('business_partners', sa.Column('partner_type', sa.String(50)))
    op.add_column('business_partners', sa.Column('trade_classification', sa.String(50)))
    
    # Step 2: Reconstruct partner_type from capabilities
    connection.execute("""
        UPDATE business_partners SET
          partner_type = CASE
            WHEN entity_class = 'service_provider' THEN service_provider_type
            WHEN capabilities->>'domestic_sell_india' = 'true' AND 
                 capabilities->>'domestic_buy_india' = 'true' THEN 'trader'
            WHEN capabilities->>'domestic_sell_india' = 'true' THEN 'seller'
            WHEN capabilities->>'domestic_buy_india' = 'true' THEN 'buyer'
            ELSE 'buyer'
          END,
          trade_classification = CASE
            WHEN capabilities->>'import_allowed' = 'true' OR 
                 capabilities->>'export_allowed' = 'true' THEN 'importer'
            ELSE 'domestic'
          END
    """)
    
    # Step 3: Drop new columns
    op.drop_column('business_partners', 'entity_class')
    op.drop_column('business_partners', 'capabilities')
    # ... drop other new columns
```

**Manual Rollback (via database backup):**
```bash
# If automatic rollback fails
pg_restore -d cotton_erp backup_pre_cdps_YYYYMMDD_HHMMSS.sql
```

**Rollback Trigger Conditions:**
- Migration fails with data corruption
- >10% of tests fail post-migration
- Critical production issue within 24 hours
- Data integrity check fails

**Rollback Execution Time:** <5 minutes  
**Data Loss in Rollback:** ZERO (capabilities stored with override_reason for traceability)

**Approved By:** _________________ **Date:** _________

---

### SECTION C: Business Impact Approval

#### C1. Service Provider Flows - ZERO CHANGES ✅
**Confirm the following flows remain UNCHANGED:**

- [ ] **Broker Onboarding:**
  - Same documents required (GST, PAN)
  - Same validation (no license required)
  - Same commission structure setup
  - **ONLY CHANGE:** Step 1 question changes from "Select Partner Type" to "Service Provider or Business Entity?"

- [ ] **Sub-Broker Onboarding:**
  - Same parent broker linking
  - Same hierarchy structure
  - Same commission sharing

- [ ] **Transporter Onboarding:**
  - Same type selection (Lorry Owner vs Commission Agent)
  - Same different document requirements
  - Same vehicle registration flow

- [ ] **Controller, Financer, Shipping Agent:**
  - Same onboarding flows
  - Same document requirements
  - Same approval processes

**Confirmed:** Service provider logic 100% preserved, only classification method changes.

**Approved By:** _________________ **Date:** _________

---

#### C2. KYC Flows - ZERO CHANGES ✅
**Confirm the following KYC processes remain UNCHANGED:**

- [ ] **KYC Renewal (365 days):**
  - Same auto-renewal schedule
  - Same document requirements
  - Same notification triggers

- [ ] **KYC Reminders:**
  - Same 90/60/30/7 day reminder schedule
  - Same email templates (with cosmetic capability display update)
  - Same escalation process

- [ ] **Auto-Suspend Logic:**
  - Same configurable suspension rules
  - Same status field updates
  - Same reactivation process

- [ ] **Document Verification:**
  - Same OCR processing
  - Same manual verification
  - **ENHANCEMENT:** Capability auto-detection triggered after verification

**Confirmed:** KYC flows 100% preserved, capability detection is additive enhancement.

**Approved By:** _________________ **Date:** _________

---

#### C3. Back-Office Features - BACKWARD COMPATIBLE ✅
**Confirm the following features continue working:**

- [ ] **Advanced Filters:**
  - Old filter: `partner_type=seller` maps to `has_sell_capability=true`
  - New filters: `entity_class`, `has_buy_capability`, `has_sell_capability`, `has_import_capability`, `has_export_capability`
  - All existing filters (status, kyc_status, state, city) unchanged

- [ ] **Excel/CSV Export:**
  - Same export mechanism
  - **COSMETIC CHANGE:** Column "Partner Type" → "Entity Type" + "Capabilities"
  - Same data completeness

- [ ] **KYC PDF Download:**
  - Same PDF generation
  - **COSMETIC CHANGE:** Shows capabilities instead of partner_type
  - Same format and branding

- [ ] **Dashboard Analytics:**
  - Same dashboard layout
  - **ENHANCEMENT:** Additional stats (by_capabilities, by_service_provider)
  - Existing stats preserved

- [ ] **Notifications:**
  - Same notification triggers
  - Same delivery mechanisms
  - **COSMETIC CHANGE:** Email content shows capabilities

**Confirmed:** Back-office features enhanced, not broken.

**Approved By:** _________________ **Date:** _________

---

### SECTION D: Testing & Quality Approval

#### D1. Test Coverage ✅
**Approve the following testing plan:**

**New Tests (13 tests, 450 lines):**
1. ✅ Indian domestic capability detection (GST+PAN)
2. ✅ IEC requires GST+PAN (strong validation)
3. ✅ Valid import/export with all 3 docs
4. ✅ Foreign domestic capability
5. ✅ Foreign import/export licenses
6. ✅ Same entity blocked (insider trading)
7. ✅ Master-branch blocked (insider trading)
8. ✅ Sibling branches blocked (insider trading)
9. ✅ Corporate group blocked (insider trading)
10. ✅ Same GST blocked (insider trading)
11. ✅ Service provider cannot post availability
12. ✅ No buy capability cannot post requirement
13. ✅ Valid unrelated partners can match

**Updated Tests (~50 existing tests):**
- All test fixtures updated to use entity_class
- All assertions updated to check capabilities
- All mocks updated for new schemas

**Test Coverage Target:** >80% for new code  
**Regression Test Suite:** All existing tests must pass

**Approved By:** _________________ **Date:** _________

---

#### D2. Quality Gates ✅
**Approve the following quality requirements:**

- [ ] **Code Quality:**
  - All new code follows existing patterns
  - Type hints for all public methods
  - Docstrings for all classes and complex methods
  - No code smells (SonarQube passing)

- [ ] **Performance:**
  - JSONB queries optimized with indexes
  - Capability detection <500ms per partner
  - No N+1 query issues
  - Migration completes in <5 minutes for 10,000 partners

- [ ] **Security:**
  - No SQL injection risks (using parameterized queries)
  - Capability overrides require authentication + authorization
  - Audit trail for all capability changes
  - Insider trading rules cannot be bypassed

- [ ] **Documentation:**
  - API documentation updated
  - README updated with new architecture
  - Migration guide created
  - Rollback procedure documented

**Approved By:** _________________ **Date:** _________

---

### SECTION E: Resource & Timeline Approval

#### E1. Development Resources ✅
**Approve the following resource allocation:**

| Phase | Days | Hours | Developer(s) | Dependencies |
|-------|------|-------|--------------|--------------|
| Phase 1: Database Schema | 2 | 16 | Backend Lead | None |
| Phase 2: Capability Detection | 2 | 16 | Backend Dev 1 | Phase 1 |
| Phase 3: Trade Desk Integration | 2 | 16 | Backend Dev 2 | Phase 2 |
| Phase 4: Risk Engine | 1 | 8 | Backend Dev 1 | Phase 3 |
| Phase 5: API & Repositories | 1 | 8 | Backend Dev 2 | Phase 4 |
| Phase 6: AI & Notifications | 1 | 8 | Backend Dev 1 | Phase 5 |
| Phase 7: Testing | 1 | 8 | QA Team | Phase 6 |
| Phase 8: Deployment | 2 | 16 | DevOps + Backend Lead | Phase 7 |
| **TOTAL** | **12** | **96** | **3 developers** | - |

**Buffer:** 2 days included for unforeseen issues  
**Actual Implementation:** 10 working days  
**Total Calendar Time:** 12 working days (2.5 weeks)

**Approved By:** _________________ **Date:** _________

---

#### E2. Deployment Schedule ✅
**Approve the following deployment timeline:**

**Week 1 (Days 1-5):** Implementation
- Day 1-2: Database schema changes
- Day 3-4: Capability detection service
- Day 5: Insider trading validator

**Week 2 (Days 6-10):** Integration & Testing
- Day 6-7: Trade desk integration
- Day 8: API & repositories
- Day 9: AI & notifications
- Day 10: Testing

**Week 3 (Days 11-12):** Deployment
- Day 11: Staging deployment + UAT
- Day 12: Production deployment + monitoring

**Deployment Window:** [SPECIFY DATE]  
**Rollback Window:** Within 24 hours if issues detected

**Approved By:** _________________ **Date:** _________

---

### SECTION F: Risk Mitigation Approval

#### F1. Identified Risks ✅
**Approve mitigation strategies for these risks:**

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Migration data corruption | Low | High | Full database backup, tested rollback |
| Breaking API changes | Medium | High | Backward compatibility layer, staged rollout |
| Performance degradation | Low | Medium | JSONB indexes, query optimization, load testing |
| Insider trading bypass | Low | High | Comprehensive test coverage, security review |
| Capability detection errors | Medium | Medium | Manual override capability, audit logging |
| Service provider workflow breaks | Low | High | Zero changes to existing logic, extensive testing |

**Approved By:** _________________ **Date:** _________

---

#### F2. Rollback Triggers ✅
**Approve automatic rollback if ANY condition met:**

- [ ] Migration fails with data integrity errors
- [ ] >10% of test suite fails post-deployment
- [ ] Critical production errors (5xx) increase >20%
- [ ] API response time degrades >50%
- [ ] User-reported critical bugs >5 within 4 hours
- [ ] Stakeholder requests rollback

**Rollback Authority:** Backend Lead + DevOps Lead (joint decision)  
**Rollback Execution:** <5 minutes  
**Rollback Validation:** <10 minutes

**Approved By:** _________________ **Date:** _________

---

## ✅ FINAL APPROVAL SIGNATURES

### Technical Approval
**Approved By:** _________________________________  
**Title:** Backend Lead / Technical Architect  
**Date:** _______________  
**Signature:** _________________________________

**Comments:** ___________________________________________________________

---

### Business Approval
**Approved By:** _________________________________  
**Title:** Product Manager / Business Owner  
**Date:** _______________  
**Signature:** _________________________________

**Comments:** ___________________________________________________________

---

### Quality Assurance Approval
**Approved By:** _________________________________  
**Title:** QA Lead  
**Date:** _______________  
**Signature:** _________________________________

**Comments:** ___________________________________________________________

---

### Operations Approval
**Approved By:** _________________________________  
**Title:** DevOps Lead / Operations Manager  
**Date:** _______________  
**Signature:** _________________________________

**Comments:** ___________________________________________________________

---

### Executive Approval
**Approved By:** _________________________________  
**Title:** CTO / Engineering Director  
**Date:** _______________  
**Signature:** _________________________________

**Comments:** ___________________________________________________________

---

## 📌 POST-APPROVAL ACTIONS

### Upon Approval:
1. [ ] Create implementation branch: `feature/cdps-capability-system`
2. [ ] Schedule kickoff meeting with development team
3. [ ] Set up project tracking board
4. [ ] Schedule daily standups for implementation period
5. [ ] Create deployment runbook
6. [ ] Schedule staging deployment window
7. [ ] Schedule production deployment window
8. [ ] Notify stakeholders of timeline

### Implementation Start Date: _______________
### Expected Staging Deployment: _______________
### Expected Production Deployment: _______________
### Go-Live Date: _______________

---

**Document Status:** 🟢 READY FOR APPROVAL  
**Version:** 3.0 - Final Comprehensive Version  
**Last Updated:** November 28, 2025  
**Next Review:** Upon approval

---

**Document Status:** 🟢 READY FOR APPROVAL  
**Last Updated:** November 28, 2025  
**Version:** 3.0 - Final Corrected Version

---

## 📌 KEY CHANGES FROM PREVIOUS VERSION

### 1. Capability Field Names (UPDATED)
- **Old:** `domestic_buy`, `domestic_sell`
- **New:** `domestic_buy_india`, `domestic_sell_india`, `domestic_buy_home_country`, `domestic_sell_home_country`

### 2. IEC Validation (STRENGTHENED)
- **Old:** IEC alone grants import/export
- **New:** IEC requires GST+PAN (all three verified)

### 3. Foreign Entity Logic (CLARIFIED)
- **Old:** Foreign entities could trade domestically anywhere
- **New:** Foreign entities trade domestically ONLY in their home country

### 4. Trade Desk Validation (LOCATION-AWARE)
- **Old:** Generic capability checks
- **New:** Location-specific checks (India vs home country)

### 5. Migration Logic (CORRECTED)
- Updated data conversion to use new field names
- Added manual_override flags for migrated data
- Improved rollback reconstruction

---

**This is the final corrected specification. All previous ambiguities resolved.**
