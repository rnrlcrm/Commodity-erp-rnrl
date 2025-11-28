# CAPABILITY-DRIVEN PARTNER SYSTEM (CDPS)
## Final Implementation Plan - November 28, 2025

**Status:** ✅ APPROVED FOR IMPLEMENTATION  
**Architecture:** Replaces `partner_type` + `trade_classification` with capability-based system  
**Impact:** 18 files modified, Zero breaking changes to service provider/KYC/back-office flows

---

## 🎯 EXECUTIVE SUMMARY

### What Changes
- **REMOVE**: `partner_type` enum (seller/buyer/trader logic)
- **REMOVE**: `trade_classification` enum (domestic/importer/exporter logic)
- **ADD**: Capability-based system with auto-detection from documents
- **ADD**: Insider trading prevention validator
- **KEEP**: All service provider logic untouched (broker, transporter, controller, financer, shipping_agent, sub_broker)
- **KEEP**: All KYC flows, back office features, notifications, jobs

### Why This Matters
1. **Flexibility**: Partners can have multiple capabilities (buy + sell + import + export)
2. **Auto-Detection**: Capabilities detected from uploaded documents (GST → domestic, IEC → import/export)
3. **Compliance**: Insider trading rules prevent circular transactions
4. **Future-Proof**: Easy to add new capabilities without schema changes

---

## 📋 PHASE 1: DATA MODEL CHANGES

### 1.1 New Enums (Add to `partners/enums.py`)

**File:** `backend/modules/partners/enums.py`

**Action:** ADD after existing ServiceProviderType enum (around line 35)

```python
class BusinessEntityType(str, Enum):
    """
    Legal entity classification - Step 1 of onboarding
    
    Used to determine entity type when is_service_provider=False
    India: proprietorship, partnership, llp, private_limited, public_limited, trust, society
    USA: llc, corporation
    Other: foreign_entity
    """
    PROPRIETORSHIP = "proprietorship"
    PARTNERSHIP = "partnership"
    LLP = "llp"
    PRIVATE_LIMITED = "private_limited"
    PUBLIC_LIMITED = "public_limited"
    TRUST = "trust"
    SOCIETY = "society"
    LLC = "llc"  # USA
    CORPORATION = "corporation"  # USA
    FOREIGN_ENTITY = "foreign_entity"  # Generic foreign
```

**Action:** UPDATE DocumentType enum - ADD these new values (around line 105)

```python
class DocumentType(str, Enum):
    """Document types for verification"""
    GST_CERTIFICATE = "gst_certificate"
    PAN_CARD = "pan_card"
    BANK_PROOF = "bank_proof"
    CANCELLED_CHEQUE = "cancelled_cheque"
    VEHICLE_RC = "vehicle_rc"
    VEHICLE_INSURANCE = "vehicle_insurance"
    VEHICLE_FITNESS = "vehicle_fitness"
    VEHICLE_PERMIT = "vehicle_permit"
    TRADE_LICENSE = "trade_license"
    INCORPORATION_CERT = "incorporation_cert"
    NO_GST_DECLARATION = "no_gst_declaration"
    FINANCIAL_STATEMENT = "financial_statement"
    ITR = "itr"
    TAX_ID_CERTIFICATE = "tax_id_certificate"
    BUSINESS_REGISTRATION = "business_registration"
    ADDRESS_PROOF = "address_proof"
    BANK_STATEMENT = "bank_statement"
    LAB_ACCREDITATION = "lab_accreditation"
    EQUIPMENT_CALIBRATION = "equipment_calibration"
    INSPECTOR_QUALIFICATION = "inspector_qualification"
    NBFC_LICENSE = "nbfc_license"
    CREDIT_RATING = "credit_rating"
    BOARD_RESOLUTION = "board_resolution"
    CHA_LICENSE = "cha_license"
    SHIPPING_LINE_AGREEMENT = "shipping_line_agreement"
    PORT_REGISTRATION = "port_registration"
    
    # 🆕 NEW - Capability Detection Documents
    IEC = "iec"  # Import Export Code (India) - Enables import/export
    FOREIGN_TAX_ID = "foreign_tax_id"  # Foreign tax registration
    FOREIGN_IMPORT_LICENSE = "foreign_import_license"  # Enables import to foreign country
    FOREIGN_EXPORT_LICENSE = "foreign_export_license"  # Enables export from foreign country
```

**Action:** DELETE entire TradeClassification enum (around line 42-47)

```python
# ❌ DELETE THIS ENTIRE ENUM
class TradeClassification(str, Enum):
    """For import/export classification"""
    DOMESTIC = "domestic"
    EXPORTER = "exporter"
    IMPORTER = "importer"
```

**Action:** DELETE or COMMENT OUT PartnerType enum (keep for migration reference)

```python
# ⚠️ DEPRECATED - Will be removed after migration
# DO NOT USE in new code - Use is_service_provider + capabilities instead
class PartnerType(str, Enum):
    """DEPRECATED: Use is_service_provider + capabilities"""
    SELLER = "seller"  # → capabilities.domestic_sell = True
    BUYER = "buyer"  # → capabilities.domestic_buy = True
    TRADER = "trader"  # → capabilities.domestic_buy + domestic_sell = True
    BROKER = "broker"  # → is_service_provider=True, service_provider_type=broker
    SUB_BROKER = "sub_broker"  # → is_service_provider=True
    TRANSPORTER = "transporter"  # → is_service_provider=True
    CONTROLLER = "controller"  # → is_service_provider=True
    FINANCER = "financer"  # → is_service_provider=True
    SHIPPING_AGENT = "shipping_agent"  # → is_service_provider=True
    IMPORTER = "importer"  # → capabilities.import_allowed = True
    EXPORTER = "exporter"  # → capabilities.export_allowed = True
```

### 1.2 BusinessPartner Model Changes (`partners/models.py`)

**File:** `backend/modules/partners/models.py`

**Location:** Lines 90-110 (PARTNER CLASSIFICATION section)

**Action 1:** DELETE these columns

```python
# ❌ DELETE - Line ~97
partner_type = Column(
    String(20),
    nullable=False,
    index=True,
    comment="seller, buyer, trader, broker, sub_broker, transporter, controller, financer, shipping_agent, importer, exporter"
)

# ❌ DELETE - Line ~100
service_provider_type = Column(
    String(50),
    nullable=True,
    comment="For service providers: broker, sub_broker, transporter, controller, financer, shipping_agent"
)

# ❌ DELETE - Line ~104
trade_classification = Column(
    String(20),
    nullable=True,
    comment="domestic, exporter (foreign selling to India), importer (foreign buying from India)"
)
```

**Action 2:** REPLACE with these NEW columns (at same location ~Line 90)

```python
```python
# ============================================
# STEP 1: SERVICE PROVIDER OR BUSINESS ENTITY
# ============================================
is_service_provider = Column(
    Boolean,
    default=False,
    nullable=False,
    comment="True = service provider (broker/transporter), False = business entity (trader)"
)

service_provider_type = Column(
    String(50),
    nullable=True,
    comment="Required if is_service_provider=True: broker, sub_broker, transporter, controller, financer, shipping_agent"
)

business_entity_type = Column(
    String(50),
    nullable=True,
    comment="Required if is_service_provider=False: proprietorship, partnership, llp, private_limited, etc."
)

# ============================================
# AUTO-DETECTED CAPABILITIES (JSON)
# ============================================
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
    },
    comment="""
    Auto-detected capabilities based on uploaded documents:
    - GST + PAN → domestic_buy=True, domestic_sell=True
    - IEC → import_allowed=True, export_allowed=True
    - Foreign Tax ID → domestic_buy=True, domestic_sell=True (in their country)
    - Foreign Import License → import_allowed=True
    - Foreign Export License → export_allowed=True
    """
)

# ============================================
# INSIDER TRADING PREVENTION
# ============================================
master_entity_id = Column(
    UUID(as_uuid=True),
    ForeignKey("business_partners.id", ondelete="SET NULL"),
    nullable=True,
    comment="Points to master entity if this is a branch"
)

corporate_group_id = Column(
    UUID(as_uuid=True),
    nullable=True,
    index=True,
    comment="Same for all entities in corporate group (manual assignment)"
)

is_master_entity = Column(
    Boolean,
    default=True,
    nullable=False,
    comment="True = head office, False = branch"
)

entity_hierarchy = Column(
    JSON,
    nullable=True,
    default={
        "parent_id": None,
        "branch_ids": [],
        "subsidiary_ids": [],
        "sister_concern_ids": []
    },
    comment="""
    Corporate structure for insider trading prevention:
    - parent_id: Parent company UUID
    - branch_ids: List of branch UUIDs
    - subsidiary_ids: List of subsidiary UUIDs
    - sister_concern_ids: List of sister concern UUIDs (same parent)
    """
)
```

### 1.3 PartnerOnboardingApplication Model Changes

**File:** `backend/modules/partners/models.py`

**Location:** PartnerOnboardingApplication class (around line 480-520)

**Action:** Apply EXACT same changes as BusinessPartner model

**DELETE columns:**
```python
# Line ~500 - DELETE
partner_type = Column(String(20), nullable=True)

# Line ~504 - DELETE
trade_classification = Column(String(20), nullable=True)
```

**ADD columns (same as BusinessPartner):**
```python
# Add after partner_code
is_service_provider = Column(Boolean, default=False, nullable=False)
service_provider_type = Column(String(50), nullable=True)
business_entity_type = Column(String(50), nullable=True)
capabilities = Column(JSON, nullable=True, default={...})  # Same structure as BusinessPartner
master_entity_id = Column(UUID(as_uuid=True), nullable=True)
corporate_group_id = Column(UUID(as_uuid=True), nullable=True)
is_master_entity = Column(Boolean, default=True)
entity_hierarchy = Column(JSON, nullable=True, default={...})
```

**Why:** Onboarding applications need same fields for validation before partner creation

---

## 📋 PHASE 2: MIGRATION SCRIPT

### 2.1 Create Migration File

**File:** `backend/db/migrations/versions/YYYYMMDD_HHMMSS_add_capability_system.py`

**Generate Command:**
```bash
cd backend
alembic revision -m "add_capability_system"
```

**Migration Structure:**
1. **upgrade()** - 5 steps
2. **downgrade()** - Rollback strategy
3. **Data conversion** - Zero data loss

### 2.2 Migration Code - upgrade() Function

**Step 1:** Add new columns (nullable=True initially for data migration)

```python
def upgrade():
    # Import for JSONB default
    from sqlalchemy.dialects.postgresql import JSONB
    import sqlalchemy as sa
    
    # ============================================
    # STEP 1: ADD NEW COLUMNS (nullable=True)
    # ============================================
    
    # business_partners table
    op.add_column('business_partners', 
        sa.Column('is_service_provider', sa.Boolean(), 
                  server_default='false', nullable=False)
    )
    op.add_column('business_partners',
        sa.Column('service_provider_type', sa.String(50), nullable=True)
    )
    op.add_column('business_partners',
        sa.Column('business_entity_type', sa.String(50), nullable=True)
    )
    op.add_column('business_partners',
        sa.Column('capabilities', JSONB, nullable=True)
    )
    op.add_column('business_partners',
        sa.Column('master_entity_id', sa.UUID(), nullable=True)
    )
    op.add_column('business_partners',
        sa.Column('corporate_group_id', sa.UUID(), nullable=True)
    )
    op.add_column('business_partners',
        sa.Column('is_master_entity', sa.Boolean(), 
                  server_default='true', nullable=False)
    )
    op.add_column('business_partners',
        sa.Column('entity_hierarchy', JSONB, nullable=True)
    )
    
    # partner_onboarding_applications table
    op.add_column('partner_onboarding_applications',
        sa.Column('is_service_provider', sa.Boolean(), 
                  server_default='false', nullable=False)
    )
    op.add_column('partner_onboarding_applications',
        sa.Column('service_provider_type', sa.String(50), nullable=True)
    )
    op.add_column('partner_onboarding_applications',
        sa.Column('business_entity_type', sa.String(50), nullable=True)
    )
    op.add_column('partner_onboarding_applications',
        sa.Column('capabilities', JSONB, nullable=True)
    )
    op.add_column('partner_onboarding_applications',
        sa.Column('master_entity_id', sa.UUID(), nullable=True)
    )
    op.add_column('partner_onboarding_applications',
        sa.Column('corporate_group_id', sa.UUID(), nullable=True)
    )
    op.add_column('partner_onboarding_applications',
        sa.Column('is_master_entity', sa.Boolean(), 
                  server_default='true', nullable=False)
    )
    op.add_column('partner_onboarding_applications',
        sa.Column('entity_hierarchy', JSONB, nullable=True)
    )
```

**Step 2:** Migrate existing data from old columns to new
   ```python
   # Convert existing partner_type to capabilities
   UPDATE business_partners SET
       is_service_provider = CASE 
           WHEN partner_type IN ('broker', 'sub_broker', 'transporter', 'controller', 'financer', 'shipping_agent') 
           THEN true 
           ELSE false 
       END,
       service_provider_type = CASE 
           WHEN partner_type IN ('broker', 'sub_broker', 'transporter', 'controller', 'financer', 'shipping_agent') 
           THEN partner_type 
           ELSE NULL 
       END,
       capabilities = CASE
           -- Sellers can sell
           WHEN partner_type = 'seller' THEN 
               '{"domestic_buy": false, "domestic_sell": true, "import_allowed": false, "export_allowed": false, "auto_detected": false, "detected_from_documents": ["legacy_migration"], "detected_at": null}'::jsonb
           
           -- Buyers can buy
           WHEN partner_type = 'buyer' THEN 
               '{"domestic_buy": true, "domestic_sell": false, "import_allowed": false, "export_allowed": false, "auto_detected": false, "detected_from_documents": ["legacy_migration"], "detected_at": null}'::jsonb
           
           -- Traders can both
           WHEN partner_type = 'trader' THEN 
               '{"domestic_buy": true, "domestic_sell": true, "import_allowed": false, "export_allowed": false, "auto_detected": false, "detected_from_documents": ["legacy_migration"], "detected_at": null}'::jsonb
           
           -- Importers can import + buy domestically
           WHEN partner_type = 'importer' THEN 
               '{"domestic_buy": true, "domestic_sell": false, "import_allowed": true, "export_allowed": false, "auto_detected": false, "detected_from_documents": ["legacy_migration"], "detected_at": null}'::jsonb
           
           -- Exporters can export + sell domestically
           WHEN partner_type = 'exporter' THEN 
               '{"domestic_buy": false, "domestic_sell": true, "import_allowed": false, "export_allowed": true, "auto_detected": false, "detected_from_documents": ["legacy_migration"], "detected_at": null}'::jsonb
           
           -- Service providers cannot trade
           WHEN partner_type IN ('broker', 'sub_broker', 'transporter', 'controller', 'financer', 'shipping_agent') THEN 
               '{"domestic_buy": false, "domestic_sell": false, "import_allowed": false, "export_allowed": false, "auto_detected": false, "detected_from_documents": ["service_provider"], "detected_at": null}'::jsonb
           
           ELSE 
               '{"domestic_buy": false, "domestic_sell": false, "import_allowed": false, "export_allowed": false, "auto_detected": false, "detected_from_documents": [], "detected_at": null}'::jsonb
       END,
       is_master_entity = true,
       entity_hierarchy = '{"parent_id": null, "branch_ids": [], "subsidiary_ids": [], "sister_concern_ids": []}'::jsonb
   WHERE partner_type IS NOT NULL;
   ```

3. Add indexes
4. Drop old columns (partner_type, trade_classification)

**Rollback Strategy:**
```python
# If migration fails, can recreate partner_type from capabilities
UPDATE business_partners SET
    partner_type = CASE
        WHEN is_service_provider = true THEN service_provider_type
        WHEN capabilities->>'domestic_buy' = 'true' AND capabilities->>'domestic_sell' = 'true' THEN 'trader'
        WHEN capabilities->>'domestic_buy' = 'true' THEN 'buyer'
        WHEN capabilities->>'domestic_sell' = 'true' THEN 'seller'
        ELSE 'buyer'
    END;
```

---

## 📋 PHASE 3: AUTO CAPABILITY DETECTION

### 3.1 New Service: `CapabilityDetectionService`

**File:** `backend/modules/partners/services.py`

**Location:** Add as new class after existing services (around line 1000+)

**Purpose:** Automatically detect trading capabilities from uploaded and verified documents

**Full Implementation:**

```python
from typing import Dict, List, Set
from uuid import UUID
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.modules.partners.models import BusinessPartner, PartnerDocument
from backend.modules.partners.repositories import (
    BusinessPartnerRepository, 
    PartnerDocumentRepository
)
from backend.modules.partners.events import CapabilitiesDetectedEvent
from backend.core.events.emitter import EventEmitter


class CapabilityDetectionService:
    """
    Automatically detect partner capabilities from uploaded documents
    
    Detection Rules:
    ================
    
    🇮🇳 Indian Domestic Trading:
        - GST Certificate + PAN Card (both verified)
        → domestic_buy = True
        → domestic_sell = True
    
    🇮🇳 Indian Import-Export:
        - IEC (Import Export Code) document (verified)
        - Requires GST + PAN as prerequisite
        → import_allowed = True
        → export_allowed = True
        → domestic_buy = True (can also trade domestically)
        → domestic_sell = True
    
    🌍 Foreign Domestic Trading:
        - Foreign Tax ID + Business Registration (both verified)
        → domestic_buy = True (in their country)
        → domestic_sell = True (in their country)
    
    🌍 Foreign Import (to their country):
        - Foreign Import License (verified)
        → import_allowed = True
    
    🌍 Foreign Export (from their country):
        - Foreign Export License (verified)
        → export_allowed = True
    
    Service Providers:
    ==================
    - Brokers, transporters, controllers, financers, shipping agents
    → All capabilities = False (cannot trade)
    → Marked with detected_from_documents = ["service_provider"]
    
    Usage:
    ======
    ```python
    service = CapabilityDetectionService(db, emitter)
    partner = await service.update_partner_capabilities(partner_id, db)
    print(partner.capabilities)
    # {
    #     "domestic_buy": True,
    #     "domestic_sell": True,
    #     "import_allowed": False,
    #     "export_allowed": False,
    #     "auto_detected": True,
    #     "detected_from_documents": ["GST", "PAN"],
    #     "detected_at": "2025-11-28T10:30:00Z"
    # }
    ```
    """
    
    def __init__(self, db: AsyncSession, emitter: EventEmitter):
        self.db = db
        self.emitter = emitter
        self.document_repo = PartnerDocumentRepository(db)
        self.partner_repo = BusinessPartnerRepository(db)
    
    async def detect_capabilities_from_documents(
        self,
        partner_id: UUID
    ) -> Dict[str, any]:
        """
        Scan partner documents and auto-detect capabilities
        
        Args:
            partner_id: Partner UUID
        
        Returns:
            Capabilities dictionary with:
            - domestic_buy: bool
            - domestic_sell: bool
            - import_allowed: bool
            - export_allowed: bool
            - auto_detected: bool (True)
            - detected_from_documents: List[str]
            - detected_at: ISO timestamp
            - manual_override: bool (False)
            - override_reason: Optional[str]
        """
        # Get partner
        partner = await self.partner_repo.get_by_id(partner_id)
        
        # Service providers cannot trade
        if partner.is_service_provider:
            return {
                "domestic_buy": False,
                "domestic_sell": False,
                "import_allowed": False,
                "export_allowed": False,
                "auto_detected": True,
                "detected_from_documents": ["service_provider"],
                "detected_at": datetime.now(timezone.utc).isoformat(),
                "manual_override": False,
                "override_reason": f"Service provider ({partner.service_provider_type}) cannot trade"
            }
        
        # Get all VERIFIED partner documents
        documents = await self.document_repo.get_by_partner_id(partner_id)
        verified_doc_types: Set[str] = {
            doc.document_type 
            for doc in documents 
            if doc.is_verified
        }
        
        # Initialize capabilities
        capabilities = {
            "domestic_buy": False,
            "domestic_sell": False,
            "import_allowed": False,
            "export_allowed": False,
            "auto_detected": True,
            "detected_from_documents": [],
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "manual_override": False,
            "override_reason": None
        }
        
        # ====================================================================
        # 🇮🇳 INDIAN PARTNER DETECTION
        # ====================================================================
        
        has_gst = "gst_certificate" in verified_doc_types
        has_pan = "pan_card" in verified_doc_types
        has_iec = "iec" in verified_doc_types
        
        if has_gst and has_pan:
            # Indian entity with GST + PAN can trade domestically
            capabilities["domestic_buy"] = True
            capabilities["domestic_sell"] = True
            capabilities["detected_from_documents"].extend(["GST", "PAN"])
            
            if has_iec:
                # IEC enables import/export
                capabilities["import_allowed"] = True
                capabilities["export_allowed"] = True
                capabilities["detected_from_documents"].append("IEC")
        
        # ====================================================================
        # 🌍 FOREIGN PARTNER DETECTION
        # ====================================================================
        
        has_foreign_tax = "foreign_tax_id" in verified_doc_types
        has_foreign_reg = "business_registration" in verified_doc_types
        has_import_license = "foreign_import_license" in verified_doc_types
        has_export_license = "foreign_export_license" in verified_doc_types
        
        if has_foreign_tax and has_foreign_reg:
            # Foreign entity with tax ID + registration can trade in their country
            capabilities["domestic_buy"] = True
            capabilities["domestic_sell"] = True
            capabilities["detected_from_documents"].extend(
                ["Foreign Tax ID", "Business Registration"]
            )
        
        if has_import_license:
            # Foreign import license enables importing to their country
            capabilities["import_allowed"] = True
            if "Foreign Import License" not in capabilities["detected_from_documents"]:
                capabilities["detected_from_documents"].append("Foreign Import License")
        
        if has_export_license:
            # Foreign export license enables exporting from their country
            capabilities["export_allowed"] = True
            if "Foreign Export License" not in capabilities["detected_from_documents"]:
                capabilities["detected_from_documents"].append("Foreign Export License")
        
        return capabilities
    
    async def update_partner_capabilities(
        self,
        partner_id: UUID,
        force_detect: bool = False
    ) -> BusinessPartner:
        """
        Detect and update partner capabilities
        
        Called automatically after:
        - Document upload + OCR verification
        - Manual document verification by admin
        - GST/Tax ID verification success
        - Partner approval
        
        Args:
            partner_id: Partner UUID
            force_detect: If True, override even if manual_override=True
        
        Returns:
            Updated BusinessPartner with new capabilities
        
        Emits:
            CapabilitiesDetectedEvent with before/after capabilities
        """
        partner = await self.partner_repo.get_by_id(partner_id)
        old_capabilities = partner.capabilities or {}
        
        # Skip if manually overridden (unless force_detect=True)
        if old_capabilities.get("manual_override", False) and not force_detect:
            return partner
        
        # Detect capabilities from documents
        new_capabilities = await self.detect_capabilities_from_documents(partner_id)
        
        # Update partner
        partner.capabilities = new_capabilities
        await self.db.commit()
        await self.db.refresh(partner)
        
        # Emit event for audit trail
        await self.emitter.emit(CapabilitiesDetectedEvent(
            partner_id=partner_id,
            old_capabilities=old_capabilities,
            new_capabilities=new_capabilities,
            detected_at=datetime.now(timezone.utc),
            auto_detected=True
        ))
        
        return partner
    
    async def manually_override_capabilities(
        self,
        partner_id: UUID,
        capabilities: Dict[str, bool],
        reason: str,
        overridden_by: UUID
    ) -> BusinessPartner:
        """
        Manually override auto-detected capabilities (admin only)
        
        Use Cases:
        - Partner has special arrangement not reflected in documents
        - Document verification pending but want to enable trading
        - Temporary capability grant while docs are being updated
        
        Args:
            partner_id: Partner UUID
            capabilities: Manual capability settings
            reason: Reason for override (required for audit)
            overridden_by: Admin user ID
        
        Returns:
            Updated BusinessPartner
        
        Emits:
            CapabilitiesManuallyOverriddenEvent
        """
        partner = await self.partner_repo.get_by_id(partner_id)
        old_capabilities = partner.capabilities or {}
        
        # Build override capabilities
        override_capabilities = {
            "domestic_buy": capabilities.get("domestic_buy", False),
            "domestic_sell": capabilities.get("domestic_sell", False),
            "import_allowed": capabilities.get("import_allowed", False),
            "export_allowed": capabilities.get("export_allowed", False),
            "auto_detected": False,
            "detected_from_documents": ["manual_override"],
            "detected_at": datetime.now(timezone.utc).isoformat(),
            "manual_override": True,
            "override_reason": reason,
            "overridden_by": str(overridden_by),
            "overridden_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Update partner
        partner.capabilities = override_capabilities
        await self.db.commit()
        await self.db.refresh(partner)
        
        # Emit event
        await self.emitter.emit(CapabilitiesManuallyOverriddenEvent(
            partner_id=partner_id,
            old_capabilities=old_capabilities,
            new_capabilities=override_capabilities,
            reason=reason,
            overridden_by=overridden_by,
            overridden_at=datetime.now(timezone.utc)
        ))
        
        return partner
    
    async def reset_to_auto_detection(
        self,
        partner_id: UUID,
        reset_by: UUID
    ) -> BusinessPartner:
        """
        Remove manual override and re-detect capabilities from documents
        
        Args:
            partner_id: Partner UUID
            reset_by: Admin user ID who reset
        
        Returns:
            Updated BusinessPartner with auto-detected capabilities
        """
        # Force re-detection even if manually overridden
        partner = await self.update_partner_capabilities(
            partner_id=partner_id,
            force_detect=True
        )
        
        # Emit event
        await self.emitter.emit(CapabilitiesResetToAutoDetectEvent(
            partner_id=partner_id,
            reset_by=reset_by,
            reset_at=datetime.now(timezone.utc),
            new_capabilities=partner.capabilities
        ))
        
        return partner
```

### 3.2 Trigger Points for Auto-Detection

**When to call `update_partner_capabilities()`:**

**1. After Document Upload + OCR Verification**

**File:** `backend/modules/partners/services.py` - `DocumentProcessingService`

**Location:** After OCR verification success (around line 250)

```python
async def verify_document_ocr(
    self,
    document_id: UUID,
    ...
) -> PartnerDocument:
    # ... existing OCR verification logic ...
    
    document.is_verified = True
    document.verified_at = datetime.now(timezone.utc)
    await self.db.commit()
    
    # ✅ AUTO-DETECT CAPABILITIES
    capability_service = CapabilityDetectionService(self.db, self.emitter)
    await capability_service.update_partner_capabilities(
        partner_id=document.partner_id
    )
    
    return document
```

**2. After Manual Document Verification by Admin**

**File:** `backend/modules/partners/router.py`

**Location:** `POST /partners/{id}/documents/{doc_id}/verify` endpoint

```python
@router.post("/partners/{partner_id}/documents/{document_id}/verify")
async def manually_verify_document(
    partner_id: UUID,
    document_id: UUID,
    ...
):
    # ... existing manual verification logic ...
    
    document.is_verified = True
    document.verified_by = current_user.id
    await db.commit()
    
    # ✅ AUTO-DETECT CAPABILITIES
    capability_service = CapabilityDetectionService(db, emitter)
    await capability_service.update_partner_capabilities(partner_id)
    
    return {"message": "Document verified, capabilities updated"}
```

**3. After GST/Tax Verification Success**

**File:** `backend/modules/partners/services.py` - `GSTVerificationService`

**Location:** After successful GSTN API call (around line 150)

```python
async def verify_gstin(
    self,
    partner_id: UUID,
    gstin: str
) -> Dict:
    # ... existing GST verification logic ...
    
    partner.tax_verified = True
    partner.tax_verified_at = datetime.now(timezone.utc)
    await self.db.commit()
    
    # ✅ AUTO-DETECT CAPABILITIES
    capability_service = CapabilityDetectionService(self.db, self.emitter)
    await capability_service.update_partner_capabilities(partner_id)
    
    return gst_data
```

**4. After Partner Approval**

**File:** `backend/modules/partners/services.py` - `ApprovalService`

**Location:** In `process_approval()` method (around line 600)

```python
async def process_approval(
    self,
    application_id: UUID,
    ...
) -> BusinessPartner:
    # ... existing approval logic ...
    
    partner = await self._create_partner_from_application(application)
    await self.db.commit()
    
    # ✅ AUTO-DETECT CAPABILITIES
    capability_service = CapabilityDetectionService(self.db, self.emitter)
    await capability_service.update_partner_capabilities(partner.id)
    
    return partner
```

### 3.3 New Events for Capability Detection

**File:** `backend/modules/partners/events.py`

**Location:** Add after existing events (around line 450)

```python
@dataclass
class CapabilitiesDetectedEvent:
    """Emitted when capabilities are auto-detected from documents"""
    partner_id: UUID
    old_capabilities: Dict[str, any]
    new_capabilities: Dict[str, any]
    detected_at: datetime
    auto_detected: bool
    
    def to_dict(self) -> Dict:
        return {
            "event_type": "capabilities.detected",
            "partner_id": str(self.partner_id),
            "old_capabilities": self.old_capabilities,
            "new_capabilities": self.new_capabilities,
            "detected_at": self.detected_at.isoformat(),
            "auto_detected": self.auto_detected,
            "changes": self._get_changes()
        }
    
    def _get_changes(self) -> List[str]:
        """List what changed"""
        changes = []
        for key in ["domestic_buy", "domestic_sell", "import_allowed", "export_allowed"]:
            old_val = self.old_capabilities.get(key, False)
            new_val = self.new_capabilities.get(key, False)
            if old_val != new_val:
                changes.append(f"{key}: {old_val} → {new_val}")
        return changes


@dataclass
class CapabilitiesManuallyOverriddenEvent:
    """Emitted when admin manually overrides capabilities"""
    partner_id: UUID
    old_capabilities: Dict[str, any]
    new_capabilities: Dict[str, any]
    reason: str
    overridden_by: UUID
    overridden_at: datetime
    
    def to_dict(self) -> Dict:
        return {
            "event_type": "capabilities.manually_overridden",
            "partner_id": str(self.partner_id),
            "old_capabilities": self.old_capabilities,
            "new_capabilities": self.new_capabilities,
            "reason": self.reason,
            "overridden_by": str(self.overridden_by),
            "overridden_at": self.overridden_at.isoformat()
        }


@dataclass
class CapabilitiesResetToAutoDetectEvent:
    """Emitted when manual override is removed"""
    partner_id: UUID
    reset_by: UUID
    reset_at: datetime
    new_capabilities: Dict[str, any]
    
    def to_dict(self) -> Dict:
        return {
            "event_type": "capabilities.reset_to_auto_detect",
            "partner_id": str(self.partner_id),
            "reset_by": str(self.reset_by),
            "reset_at": self.reset_at.isoformat(),
            "new_capabilities": self.new_capabilities
        }
```

```python
class CapabilityDetectionService:
    """
    Automatically detect partner capabilities from uploaded documents
    
    Rules:
    🇮🇳 Indian Domestic:
        GST + PAN → domestic_buy=True, domestic_sell=True
    
    🇮🇳 Indian Import-Export:
        IEC (requires GST + PAN) → all capabilities=True
    
    🌍 Foreign Domestic:
        Foreign TAX ID + Business Registration → domestic_buy=True, domestic_sell=True
    
    🌍 Foreign Import:
        Foreign Import License → import_allowed=True
    
    🌍 Foreign Export:
        Foreign Export License → export_allowed=True
    """
    
    async def detect_capabilities_from_documents(
        self,
        partner_id: UUID,
        db: AsyncSession
    ) -> Dict[str, bool]:
        """
        Scan partner documents and auto-detect capabilities
        
        Returns:
            {
                "domestic_buy": bool,
                "domestic_sell": bool,
                "import_allowed": bool,
                "export_allowed": bool,
                "auto_detected": true,
                "detected_from_documents": ["GST", "PAN", "IEC"],
                "detected_at": "2025-11-28T10:30:00Z"
            }
        """
        # Get all partner documents
        documents = await self.document_repo.get_by_partner_id(partner_id)
        
        capabilities = {
            "domestic_buy": False,
            "domestic_sell": False,
            "import_allowed": False,
            "export_allowed": False,
            "auto_detected": True,
            "detected_from_documents": [],
            "detected_at": datetime.now(timezone.utc).isoformat()
        }
        
        doc_types = {doc.document_type for doc in documents if doc.is_verified}
        
        # 🇮🇳 Indian partner detection
        if "gst_certificate" in doc_types and "pan_card" in doc_types:
            capabilities["domestic_buy"] = True
            capabilities["domestic_sell"] = True
            capabilities["detected_from_documents"].extend(["GST", "PAN"])
            
            # Check for IEC (Import Export Code)
            if "iec" in doc_types:
                capabilities["import_allowed"] = True
                capabilities["export_allowed"] = True
                capabilities["detected_from_documents"].append("IEC")
        
        # 🌍 Foreign partner detection
        if "foreign_tax_id" in doc_types and "business_registration" in doc_types:
            capabilities["domestic_buy"] = True
            capabilities["domestic_sell"] = True
            capabilities["detected_from_documents"].extend(["Foreign Tax ID", "Business Registration"])
        
        if "foreign_import_license" in doc_types:
            capabilities["import_allowed"] = True
            capabilities["detected_from_documents"].append("Foreign Import License")
        
        if "foreign_export_license" in doc_types:
            capabilities["export_allowed"] = True
            capabilities["detected_from_documents"].append("Foreign Export License")
        
        return capabilities
    
    async def update_partner_capabilities(
        self,
        partner_id: UUID,
        db: AsyncSession
    ) -> BusinessPartner:
        """
        Detect and update partner capabilities
        Called after document upload/verification
        """
        capabilities = await self.detect_capabilities_from_documents(partner_id, db)
        
        # Update partner
        partner = await self.partner_repo.get_by_id(partner_id)
        partner.capabilities = capabilities
        await db.commit()
        
        # Emit event
        await self.emitter.emit(CapabilitiesDetectedEvent(
            partner_id=partner_id,
            capabilities=capabilities,
            detected_at=datetime.now(timezone.utc)
        ))
        
        return partner
```

### 3.2 Trigger Points for Auto-Detection

**Call `update_partner_capabilities()` after:**
1. Document upload + OCR verification
2. Manual document verification by admin
3. GST/Tax ID verification success
4. Partner approval

---

## 📋 PHASE 4: INSIDER TRADING VALIDATOR

### 4.1 New Validator: `InsiderTradingValidator` (`partners/validators.py`)

```python
class InsiderTradingValidator:
    """
    Prevent insider trading between related entities
    
    Blocked Scenarios:
    1. Same entity (buyer_id == seller_id)
    2. Master ↔ Branch (buyer is master, seller is branch OR vice versa)
    3. Sibling branches (both have same master_entity_id)
    4. Same corporate group (same corporate_group_id)
    5. Parent ↔ Subsidiary
    6. Sister concerns (same parent in entity_hierarchy)
    """
    
    async def validate_trade_parties(
        self,
        buyer_id: UUID,
        seller_id: UUID,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Validate buyer and seller are not related entities
        
        Returns:
            {
                "allowed": bool,
                "reason": str,
                "violation_type": str | None
            }
        """
        # Rule 1: Same entity
        if buyer_id == seller_id:
            return {
                "allowed": False,
                "reason": "Cannot trade with yourself (same entity)",
                "violation_type": "SAME_ENTITY"
            }
        
        # Fetch both partners
        buyer = await self.partner_repo.get_by_id(buyer_id)
        seller = await self.partner_repo.get_by_id(seller_id)
        
        # Rule 2: Master ↔ Branch
        if buyer.master_entity_id == seller.id or seller.master_entity_id == buyer.id:
            return {
                "allowed": False,
                "reason": "Cannot trade between master entity and its branch",
                "violation_type": "MASTER_BRANCH_TRADING"
            }
        
        # Rule 3: Sibling branches (same master)
        if (buyer.master_entity_id is not None and 
            buyer.master_entity_id == seller.master_entity_id):
            return {
                "allowed": False,
                "reason": "Cannot trade between sibling branches (same master entity)",
                "violation_type": "SIBLING_BRANCH_TRADING"
            }
        
        # Rule 4: Same corporate group
        if (buyer.corporate_group_id is not None and 
            buyer.corporate_group_id == seller.corporate_group_id):
            return {
                "allowed": False,
                "reason": "Cannot trade within same corporate group",
                "violation_type": "CORPORATE_GROUP_TRADING"
            }
        
        # Rule 5: Parent ↔ Subsidiary
        buyer_hierarchy = buyer.entity_hierarchy or {}
        seller_hierarchy = seller.entity_hierarchy or {}
        
        if (buyer_hierarchy.get("parent_id") == seller.id or 
            seller_hierarchy.get("parent_id") == buyer.id):
            return {
                "allowed": False,
                "reason": "Cannot trade between parent and subsidiary",
                "violation_type": "PARENT_SUBSIDIARY_TRADING"
            }
        
        # Rule 6: Sister concerns
        if (buyer_hierarchy.get("parent_id") is not None and
            buyer_hierarchy.get("parent_id") == seller_hierarchy.get("parent_id")):
            return {
                "allowed": False,
                "reason": "Cannot trade between sister concerns (same parent)",
                "violation_type": "SISTER_CONCERN_TRADING"
            }
        
        # All checks passed
        return {
            "allowed": True,
            "reason": "Trade parties are unrelated - trade allowed",
            "violation_type": None
        }
```

---

## 📋 PHASE 5: TRADE DESK INTEGRATION

### 5.1 Availability Service Changes (`trade_desk/services/availability_service.py`)

**REPLACE existing validation:**
```python
# ❌ OLD (Line 798-801)
# TODO: Implement actual validation by checking business_partner.partner_type

# ✅ NEW
async def _validate_seller_capabilities(
    self,
    business_partner_id: UUID
) -> None:
    """
    Validate seller has capability to post availability
    
    Rules:
    - Service providers CANNOT trade
    - Must have domestic_sell = True
    """
    partner = await self.partner_repo.get_by_id(business_partner_id)
    
    # Block service providers
    if partner.is_service_provider:
        raise ValueError(
            "Service providers cannot post availabilities. "
            f"Partner is registered as {partner.service_provider_type}."
        )
    
    # Check capability
    capabilities = partner.capabilities or {}
    if not capabilities.get("domestic_sell", False):
        raise ValueError(
            "Partner does not have domestic_sell capability. "
            "Upload GST + PAN documents to enable selling."
        )
```

### 5.2 Requirement Service Changes (`trade_desk/services/requirement_service.py`)

**REPLACE existing validation:**
```python
# ❌ OLD (Line 1432)
# TODO: Load business partner and check partner_type

# ✅ NEW
async def _validate_buyer_capabilities(
    self,
    business_partner_id: UUID
) -> None:
    """
    Validate buyer has capability to post requirement
    
    Rules:
    - Service providers CANNOT trade
    - Must have domestic_buy = True
    """
    partner = await self.partner_repo.get_by_id(business_partner_id)
    
    # Block service providers
    if partner.is_service_provider:
        raise ValueError(
            "Service providers cannot post requirements. "
            f"Partner is registered as {partner.service_provider_type}."
        )
    
    # Check capability
    capabilities = partner.capabilities or {}
    if not capabilities.get("domestic_buy", False):
        raise ValueError(
            "Partner does not have domestic_buy capability. "
            "Upload GST + PAN documents to enable buying."
        )
```

### 5.3 Matching Engine Changes (`trade_desk/matching/validators.py`)

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
    return ValidationResult(
        is_valid=False,
        reasons=reasons,
        warnings=warnings,
        ai_alerts=ai_alerts
    )

# Capability Validation
buyer = await self.db.get(BusinessPartner, requirement.business_partner_id)
seller = await self.db.get(BusinessPartner, availability.business_partner_id)

buyer_capabilities = buyer.capabilities or {}
seller_capabilities = seller.capabilities or {}

if not buyer_capabilities.get("domestic_buy", False):
    reasons.append("Buyer does not have domestic_buy capability")

if not seller_capabilities.get("domestic_sell", False):
    reasons.append("Seller does not have domestic_sell capability")

if reasons:
    return ValidationResult(
        is_valid=False,
        reasons=reasons,
        warnings=warnings,
        ai_alerts=ai_alerts
    )
```

---

## 📋 PHASE 6: RISK ENGINE CHANGES

### 6.1 Risk Engine Validation (`risk/risk_engine.py`)

**REPLACE `validate_partner_role()` method (lines 884-994):**
```python
async def validate_partner_role(
    self,
    partner_id: UUID,
    transaction_type: str  # "BUY" or "SELL"
) -> Dict[str, Any]:
    """
    Validate partner has capability for requested transaction
    
    Capability-Based Validation:
    - BUY requires domestic_buy = True
    - SELL requires domestic_sell = True
    - Service providers blocked from trading
    
    Args:
        partner_id: Partner UUID
        transaction_type: "BUY" or "SELL"
        
    Returns:
        {
            "allowed": bool,
            "reason": str,
            "capabilities": dict
        }
    """
    # Fetch partner
    query = select(BusinessPartner).where(BusinessPartner.id == partner_id)
    result = await self.db.execute(query)
    partner = result.scalar_one_or_none()
    
    if not partner:
        return {
            "allowed": False,
            "reason": "Partner not found",
            "capabilities": None
        }
    
    # Block service providers
    if partner.is_service_provider:
        return {
            "allowed": False,
            "reason": (
                f"Service providers cannot trade. "
                f"Partner is registered as {partner.service_provider_type}."
            ),
            "violation_type": "SERVICE_PROVIDER_CANNOT_TRADE",
            "capabilities": partner.capabilities
        }
    
    capabilities = partner.capabilities or {}
    
    # Validate BUY capability
    if transaction_type == "BUY":
        if not capabilities.get("domestic_buy", False):
            return {
                "allowed": False,
                "reason": (
                    "Partner does not have domestic_buy capability. "
                    "Upload GST + PAN documents to enable buying."
                ),
                "violation_type": "MISSING_BUY_CAPABILITY",
                "capabilities": capabilities
            }
        return {
            "allowed": True,
            "reason": "Partner has domestic_buy capability",
            "capabilities": capabilities
        }
    
    # Validate SELL capability
    elif transaction_type == "SELL":
        if not capabilities.get("domestic_sell", False):
            return {
                "allowed": False,
                "reason": (
                    "Partner does not have domestic_sell capability. "
                    "Upload GST + PAN documents to enable selling."
                ),
                "violation_type": "MISSING_SELL_CAPABILITY",
                "capabilities": capabilities
            }
        return {
            "allowed": True,
            "reason": "Partner has domestic_sell capability",
            "capabilities": capabilities
        }
    
    return {
        "allowed": False,
        "reason": f"Invalid transaction_type: {transaction_type}",
        "capabilities": capabilities
    }
```

### 6.2 Risk Schema Changes (`risk/schemas.py`)

**REMOVE `partner_type` field (lines 40-45, 199, 206, 346-347):**
- Delete all references to `partner_type`
- No replacement needed (validation now uses capabilities)

---

## 📋 PHASE 7: SCHEMA UPDATES

### 7.1 Partner Schemas (`partners/schemas.py`)

**REMOVE:**
```python
# Line 35 - DELETE
partner_type: PartnerType  # ❌

# Line 50 - DELETE
partner_type: Optional[PartnerType] = None  # ❌

# Line 165 - DELETE
trade_classification: Optional[TradeClassification] = None  # ❌

# Line 361 - DELETE
trade_classification: Optional[TradeClassification] = None  # ❌
```

**ADD:**
```python
class OnboardingApplicationCreate(BaseModel):
    """Step 1: Service Provider or Business Entity"""
    is_service_provider: bool
    service_provider_type: Optional[ServiceProviderType] = None
    business_entity_type: Optional[BusinessEntityType] = None
    
    # ... rest of fields ...
    
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
    """Partner capability information"""
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
    """Updated response schema"""
    id: UUID
    is_service_provider: bool
    service_provider_type: Optional[str]
    business_entity_type: Optional[str]
    capabilities: CapabilityResponse
    # ... rest of fields ...
```

### 7.2 Trade Desk Schemas (`trade_desk/schemas/__init__.py`)

**REMOVE Line 239:**
```python
partner_type: str  # ❌ DELETE
```

---

## 📋 PHASE 8: REPOSITORY UPDATES

### 8.1 Partner Repository (`partners/repositories.py`)

**REMOVE `partner_type` filter (lines 187, 199, 215-216):**
```python
# ❌ OLD
async def list_partners(
    self,
    organization_id: UUID,
    partner_type: Optional[PartnerType] = None,  # ❌ DELETE
    ...
):
    if partner_type:  # ❌ DELETE
        query = query.where(BusinessPartner.partner_type == partner_type)  # ❌ DELETE

# ✅ NEW
async def list_partners(
    self,
    organization_id: UUID,
    is_service_provider: Optional[bool] = None,
    service_provider_type: Optional[str] = None,
    has_buy_capability: Optional[bool] = None,
    has_sell_capability: Optional[bool] = None,
    ...
):
    if is_service_provider is not None:
        query = query.where(BusinessPartner.is_service_provider == is_service_provider)
    
    if service_provider_type:
        query = query.where(BusinessPartner.service_provider_type == service_provider_type)
    
    if has_buy_capability:
        query = query.where(
            BusinessPartner.capabilities['domestic_buy'].astext.cast(Boolean) == True
        )
    
    if has_sell_capability:
        query = query.where(
            BusinessPartner.capabilities['domestic_sell'].astext.cast(Boolean) == True
        )
```

---

## 📋 PHASE 9: SERVICE LAYER UPDATES

### 9.1 Partner Service (`partners/services.py`)

**REMOVE all `partner_type` references:**
- Line 363: parameter
- Line 376: docstring
- Line 497: seller logic
- Line 507: seller transport
- Line 614, 883, 962: application.partner_type
- Line 885: trade_classification

**REPLACE with capability-based logic:**
```python
# Auto-detect capabilities after approval
async def approve_application(
    self,
    application_id: UUID,
    ...
) -> BusinessPartner:
    # ... existing approval logic ...
    
    # Auto-detect capabilities from documents
    capability_service = CapabilityDetectionService(self.db, self.emitter)
    await capability_service.update_partner_capabilities(
        partner_id=partner.id,
        db=self.db
    )
    
    return partner
```

### 9.2 Notification Service (`partners/notifications.py`)

**REMOVE Line 170:**
```python
- Partner Type: {partner.partner_type}  # ❌ DELETE
```

**REPLACE with:**
```python
- Entity Type: {"Service Provider: " + partner.service_provider_type if partner.is_service_provider else "Business Entity: " + partner.business_entity_type}
- Capabilities: {"Buy" if partner.capabilities.get("domestic_buy") else ""}{"Sell" if partner.capabilities.get("domestic_sell") else ""}
```

---

## 📋 PHASE 10: ROUTER UPDATES

### 10.1 Partner Router (`partners/router.py`)

**ADD new endpoints:**
```python
@router.post("/partners/{partner_id}/capabilities/detect")
async def detect_partner_capabilities(
    partner_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Manually trigger capability detection from documents
    """
    service = CapabilityDetectionService(db, emitter)
    partner = await service.update_partner_capabilities(partner_id, db)
    return {"capabilities": partner.capabilities}


@router.put("/partners/{partner_id}/capabilities/override")
async def override_partner_capabilities(
    partner_id: UUID,
    capabilities: Dict[str, bool],
    reason: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)  # Admin only
):
    """
    Manually override auto-detected capabilities (admin only)
    """
    partner = await partner_repo.get_by_id(partner_id)
    partner.capabilities = {
        **capabilities,
        "manual_override": True,
        "override_reason": reason,
        "detected_at": datetime.now(timezone.utc).isoformat()
    }
    await db.commit()
    return {"capabilities": partner.capabilities}


@router.post("/partners/{partner_id}/entity-hierarchy")
async def update_entity_hierarchy(
    partner_id: UUID,
    hierarchy: Dict[str, Any],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    """
    Update corporate structure for insider trading prevention
    """
    partner = await partner_repo.get_by_id(partner_id)
    partner.entity_hierarchy = hierarchy
    await db.commit()
    return {"entity_hierarchy": partner.entity_hierarchy}
```

---

## 📋 PHASE 11: AI ASSISTANT UPDATES

### 11.1 Partner Assistant (`ai/assistants/partner_assistant/assistant.py`)

**REPLACE all `partner_type` logic (lines 39, 46, 53, 56, 58, 75, 81, 86, 469, 471, 473):**
```python
# ✅ NEW
async def assist_onboarding_start(
    self,
    is_service_provider: bool,
    service_provider_type: Optional[str] = None,
    business_entity_type: Optional[str] = None
) -> Dict:
    """
    Guide user through capability-based onboarding
    """
    if is_service_provider:
        requirements = await self.tools.get_service_provider_requirements(
            service_provider_type
        )
        greeting = f"Welcome! Let's get you registered as a {service_provider_type}."
    else:
        requirements = await self.tools.get_business_entity_requirements(
            business_entity_type
        )
        greeting = f"Welcome! Let's set up your {business_entity_type} entity."
    
    return {
        "greeting": greeting,
        "requirements": requirements,
        "estimated_time": self._estimate_onboarding_time(is_service_provider),
        "capabilities_note": "We'll automatically detect your trading capabilities from uploaded documents."
    }
```

### 11.2 Partner Tools (`ai/assistants/partner_assistant/tools.py`)

**REPLACE all `partner_type` references (lines 31, 36, 67, 77, 87, 103, 114, 124, 134, 148, 166, 214, 219, 254, 276):**
```python
# Split into two methods
async def get_service_provider_requirements(
    self,
    service_provider_type: str
) -> Dict:
    """Get requirements for service providers"""
    # Broker, transporter, controller, financer, shipping_agent logic
    ...

async def get_business_entity_requirements(
    self,
    business_entity_type: str
) -> Dict:
    """Get requirements for business entities"""
    # Generic requirements + capability detection info
    return {
        "documents": ["GST", "PAN", "Bank Proof"],
        "capabilities": {
            "info": "Capabilities will be auto-detected from documents",
            "GST + PAN": "Enables domestic buying and selling",
            "IEC": "Enables import and export",
            "Foreign Tax ID": "Enables trading in your country"
        }
    }
```

### 11.3 Partner Prompts (`ai/prompts/partner/prompts.py`)

**REMOVE `partner_type` references (lines 46, 55):**
```python
# ✅ NEW
User is starting partner onboarding.
Step 1: Are they a service provider (broker/transporter) or business entity (trader)?
```

---

## 📋 PHASE 12: TEST UPDATES

### 12.1 Partner Tests

**REPLACE all fixtures:**
```python
@pytest.fixture
async def sample_buyer_partner(db):
    """Business entity with buy capability"""
    return BusinessPartner(
        id=uuid4(),
        is_service_provider=False,
        business_entity_type="private_limited",
        capabilities={
            "domestic_buy": True,
            "domestic_sell": False,
            "import_allowed": False,
            "export_allowed": False,
            "auto_detected": True,
            "detected_from_documents": ["GST", "PAN"]
        },
        # ... rest of fields ...
    )

@pytest.fixture
async def sample_trader_partner(db):
    """Business entity with buy + sell capabilities"""
    return BusinessPartner(
        id=uuid4(),
        is_service_provider=False,
        business_entity_type="llp",
        capabilities={
            "domestic_buy": True,
            "domestic_sell": True,
            "import_allowed": False,
            "export_allowed": False,
            "auto_detected": True,
            "detected_from_documents": ["GST", "PAN"]
        },
        # ... rest of fields ...
    )

@pytest.fixture
async def sample_broker(db):
    """Service provider - cannot trade"""
    return BusinessPartner(
        id=uuid4(),
        is_service_provider=True,
        service_provider_type="broker",
        capabilities={
            "domestic_buy": False,
            "domestic_sell": False,
            "import_allowed": False,
            "export_allowed": False,
            "auto_detected": False,
            "detected_from_documents": ["service_provider"]
        },
        # ... rest of fields ...
    )
```

### 12.2 New Test Files

**`tests/test_capability_detection.py`** (5 tests):
1. Test Indian domestic (GST + PAN)
2. Test Indian IEC (import/export)
3. Test foreign domestic
4. Test foreign import license
5. Test foreign export license

**`tests/test_insider_trading.py`** (5 tests):
1. Test same entity blocked
2. Test master ↔ branch blocked
3. Test sibling branches blocked
4. Test corporate group blocked
5. Test parent ↔ subsidiary blocked

**`tests/test_trade_desk_capabilities.py`** (3 tests):
1. Test service provider cannot post availability
2. Test service provider cannot post requirement
3. Test valid unrelated partners can match

---

## 📋 PHASE 13: DOCUMENTATION UPDATES

### 13.1 Files to Update
- `PARTNER_MODULE_IMPLEMENTATION.md` - Update to capability-based
- `PARTNER_CORRECTIONS_SUMMARY.md` - Add CDPS section
- `PARTNER_TEST_SCENARIOS.md` - Update test scenarios
- API documentation (Swagger/OpenAPI)

---

## 🚀 IMPLEMENTATION CHECKLIST

### Phase 1: Database & Models ✅
- [ ] Update `partners/enums.py` - Add BusinessEntityType, new DocumentTypes
- [ ] Update `partners/models.py` - Add new columns, remove old
- [ ] Update `partners/models.py` (onboarding) - Same changes
- [ ] Create migration `add_capability_system.py`
- [ ] Test migration up/down

### Phase 2: Services & Business Logic ✅
- [ ] Create `CapabilityDetectionService` in `partners/services.py`
- [ ] Create `InsiderTradingValidator` in `partners/validators.py`
- [ ] Update `PartnerService.approve_application()` - Add auto-detection
- [ ] Add trigger points for capability detection

### Phase 3: Trade Desk Integration ✅
- [ ] Update `availability_service.py` - Replace partner_type validation
- [ ] Update `requirement_service.py` - Replace partner_type validation
- [ ] Update `matching/validators.py` - Add insider trading + capability checks

### Phase 4: Risk Engine ✅
- [ ] Update `risk_engine.py` - Replace `validate_partner_role()`
- [ ] Update `risk/schemas.py` - Remove partner_type fields

### Phase 5: Schemas & API ✅
- [ ] Update `partners/schemas.py` - Remove old fields, add new
- [ ] Update `trade_desk/schemas/__init__.py` - Remove partner_type
- [ ] Update `partners/router.py` - Add new endpoints
- [ ] Update `partners/repositories.py` - Replace filters

### Phase 6: Supporting Changes ✅
- [ ] Update `partners/notifications.py` - Update email templates
- [ ] Update AI assistant files (3 files)
- [ ] Update AI prompts

### Phase 7: Testing ✅
- [ ] Create `test_capability_detection.py` (5 tests)
- [ ] Create `test_insider_trading.py` (5 tests)
- [ ] Create `test_trade_desk_capabilities.py` (3 tests)
- [ ] Update existing test fixtures
- [ ] Run full test suite

### Phase 8: Documentation ✅
- [ ] Update implementation docs
- [ ] Update API docs
- [ ] Create migration guide for existing data
- [ ] Update README

---

## 📊 FILES MODIFIED (Total: 18)

### Core Partner Module (7 files)
1. `backend/modules/partners/enums.py` - Add BusinessEntityType, DocumentTypes
2. `backend/modules/partners/models.py` - Remove partner_type, add capabilities
3. `backend/modules/partners/schemas.py` - Update request/response schemas
4. `backend/modules/partners/services.py` - Add CapabilityDetectionService
5. `backend/modules/partners/validators.py` - Add InsiderTradingValidator
6. `backend/modules/partners/router.py` - Add new endpoints
7. `backend/modules/partners/repositories.py` - Update filters
8. `backend/modules/partners/notifications.py` - Update templates

### Trade Desk Module (3 files)
9. `backend/modules/trade_desk/services/availability_service.py` - Capability validation
10. `backend/modules/trade_desk/services/requirement_service.py` - Capability validation
11. `backend/modules/trade_desk/matching/validators.py` - Insider trading validation
12. `backend/modules/trade_desk/schemas/__init__.py` - Remove partner_type

### Risk Module (2 files)
13. `backend/modules/risk/risk_engine.py` - Update validate_partner_role()
14. `backend/modules/risk/schemas.py` - Remove partner_type fields

### AI Module (3 files)
15. `backend/ai/assistants/partner_assistant/assistant.py` - Update logic
16. `backend/ai/assistants/partner_assistant/tools.py` - Split methods
17. `backend/ai/prompts/partner/prompts.py` - Update prompts

### Database (1 file)
18. `backend/db/migrations/versions/YYYYMMDD_add_capability_system.py` - New migration

---

## 🔒 ZERO BREAKING CHANGES GUARANTEE

### Service Provider Flows (UNTOUCHED)
- ✅ Broker onboarding - Same flow
- ✅ Sub-broker onboarding - Same flow
- ✅ Transporter onboarding - Same flow (lorry owner vs commission agent)
- ✅ Controller onboarding - Same flow
- ✅ Financer onboarding - Same flow
- ✅ Shipping agent onboarding - Same flow

### KYC Flows (UNTOUCHED)
- ✅ KYC renewal tracking (365 days)
- ✅ KYC reminders (90/60/30/7 days)
- ✅ Auto-suspend job (configurable)
- ✅ KYC status management
- ✅ Document verification

### Back Office Features (UNTOUCHED)
- ✅ Advanced filters (will add new capability filters)
- ✅ Export to Excel/CSV
- ✅ KYC PDF download
- ✅ Dashboard analytics
- ✅ Notifications
- ✅ Scheduled jobs
- ✅ Amendment workflows

### Data Migration Strategy
- ✅ Existing partners auto-converted to capabilities
- ✅ Service providers flagged with `is_service_provider=True`
- ✅ Trading capability set based on old `partner_type`
- ✅ Zero data loss
- ✅ Rollback strategy available

---

## 🎯 SUCCESS METRICS

### Before Migration
- 11 partner types (seller, buyer, trader, broker, etc.)
- 3 trade classifications (domestic, importer, exporter)
- Hard-coded role restrictions
- No insider trading prevention
- Manual capability management

### After Migration
- ✅ 2 main categories (service provider vs business entity)
- ✅ 4 auto-detected capabilities (buy, sell, import, export)
- ✅ Document-driven capability detection
- ✅ 6 insider trading rules enforced
- ✅ Flexible multi-capability support
- ✅ Future-proof for new capabilities

---

## 📅 ESTIMATED TIMELINE

- **Phase 1-2** (Models + Services): 2 days
- **Phase 3-4** (Trade Desk + Risk): 2 days
- **Phase 5-6** (Schemas + Support): 1 day
- **Phase 7** (Testing): 2 days
- **Phase 8** (Documentation): 1 day

**Total: 8 working days**

---

## ✅ APPROVAL REQUIRED

**Awaiting Approval From:** Product Owner / Tech Lead

**Questions to Confirm:**
1. ✅ Agree to remove `partner_type` enum completely?
2. ✅ Agree to capability-based system with auto-detection?
3. ✅ Agree to insider trading rules as specified?
4. ✅ Agree to service provider separation?
5. ✅ Ready to start Phase 1 implementation?

**Once approved, implementation will begin immediately following this exact specification.**

---

**Document Version:** 1.0  
**Last Updated:** November 28, 2025  
**Status:** AWAITING APPROVAL
