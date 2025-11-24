# Engine 2 - Requirement Engine Implementation Plan

**Status:** 🔴 AWAITING APPROVAL  
**Branch:** `feat/trade-desk-requirement-engine`  
**Estimated Timeline:** 5-7 days  
**Prerequisite:** ✅ Engine 1 (Availability) merged to main

---

## 📋 Executive Summary

**Objective:** Build the buyer-side counterpart to Availability Engine. Buyers post their commodity requirements (what they want to buy), and the system intelligently matches them with available inventory.

**Mirror Architecture:** Requirement Engine follows the exact same systematic 8-phase approach that successfully delivered Availability Engine.

**Key Difference:** 
- **Availability** = Sellers say "I HAVE this to sell"
- **Requirement** = Buyers say "I NEED this to buy"

**Core Value:** Enable buyers to broadcast their needs to the market, receive intelligent matches from existing inventory, and get real-time notifications when new compatible inventory becomes available.

---

## 🎯 Business Requirements

### Functional Requirements

1. **Requirement Posting**
   - Buyers post what commodity they want to buy
   - Specify quality parameters (cotton staple length, gold purity, etc.)
   - Define quantity ranges (min/max)
   - Set budget constraints (max price willing to pay)
   - Delivery preferences (location, timeline)
   - Market visibility (public/private)

2. **Smart Matching**
   - Auto-match requirements with existing availabilities
   - Score compatibility (0.0 to 1.0)
   - Quality tolerance fuzzy matching
   - Price range validation
   - Geo-proximity calculation
   - Real-time notifications on new matches

3. **Requirement Lifecycle**
   - Create → Review → Activate → Matched → Fulfilled → Expired
   - Partial fulfillment support (split orders)
   - Requirement updates (trigger re-matching)
   - Cancellation workflow

4. **Multi-Commodity Support**
   - Universal JSONB schema for quality specs
   - Works with ANY commodity (Cotton, Gold, Wheat, Oil, etc.)
   - No schema changes needed for new commodities

5. **AI Integration Hooks**
   - Normalize quality requirements
   - Budget anomaly detection
   - Auto-suggest alternative specifications
   - Predict match probability
   - Vector embeddings for semantic search

### Non-Functional Requirements

1. **Performance:** Sub-200ms for requirement creation, <1s for match search
2. **Scalability:** Support 100K+ active requirements
3. **Concurrency:** AsyncSession for high-throughput matching
4. **Real-time:** WebSocket notifications for new matches
5. **Security:** JWT auth, RBAC, buyer context isolation

---

## 🏗️ Technical Architecture

### Phase 1: Database Schema (Day 1)

**File:** `backend/db/migrations/versions/create_requirement_engine_tables.py`

**Table:** `requirements`

```sql
CREATE TABLE requirements (
    -- Primary Key
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Core Fields
    commodity_type VARCHAR(100) NOT NULL,  -- cotton, gold, wheat, oil
    buyer_id UUID NOT NULL,                -- References users.id
    buyer_company_id UUID,                 -- References companies.id (optional)
    
    -- Quantity Specifications
    quantity_required NUMERIC(20, 4) NOT NULL,     -- How much they want
    quantity_min NUMERIC(20, 4),                   -- Minimum acceptable
    quantity_max NUMERIC(20, 4),                   -- Maximum acceptable
    quantity_unit VARCHAR(20) NOT NULL,            -- bales, kg, tons, troy_oz
    quantity_fulfilled NUMERIC(20, 4) DEFAULT 0,   -- Auto-calculated
    
    -- Quality Parameters (JSONB - flexible multi-commodity)
    quality_required JSONB NOT NULL,        -- Required specs {staple_length: 34, purity: 99.9}
    quality_tolerance JSONB,                -- Acceptable ranges {staple_length: [32, 36]}
    
    -- Price Constraints
    budget_max_price NUMERIC(20, 4),        -- Maximum price willing to pay
    budget_total NUMERIC(20, 4),            -- Total budget available
    price_currency VARCHAR(10) DEFAULT 'USD',
    
    -- Delivery Preferences
    delivery_location JSONB,                -- {city, state, country, lat, lng}
    delivery_radius_km INT,                 -- Max delivery distance
    delivery_date_required DATE,            -- When they need it by
    delivery_date_flexible BOOLEAN DEFAULT true,
    
    -- Market Visibility
    visibility VARCHAR(20) DEFAULT 'PUBLIC',  -- PUBLIC, PRIVATE, RESTRICTED
    private_sellers JSONB,                    -- Array of seller IDs (if PRIVATE)
    
    -- Lifecycle Status
    status VARCHAR(20) DEFAULT 'DRAFT',  -- DRAFT, ACTIVE, MATCHED, FULFILLED, EXPIRED, CANCELLED
    approval_status VARCHAR(20) DEFAULT 'PENDING',
    approval_notes TEXT,
    approved_by UUID,
    approved_at TIMESTAMPTZ,
    
    -- AI-Enhanced Fields
    ai_match_vector VECTOR(1536),           -- For semantic search (OpenAI embeddings)
    ai_suggested_alternatives JSONB,        -- AI-suggested alternative specs
    match_count INT DEFAULT 0,              -- Number of compatible availabilities found
    best_match_score NUMERIC(5, 4),         -- Score of best match (0.0 - 1.0)
    
    -- Audit Trail
    created_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    created_by UUID NOT NULL,
    updated_by UUID,
    expires_at TIMESTAMPTZ,                 -- Auto-expire old requirements
    fulfilled_at TIMESTAMPTZ,
    cancelled_at TIMESTAMPTZ,
    cancellation_reason TEXT,
    
    -- Metadata
    notes TEXT,
    internal_reference VARCHAR(100),        -- Buyer's internal PO number
    priority VARCHAR(20) DEFAULT 'NORMAL',  -- URGENT, HIGH, NORMAL, LOW
    tags JSONB,                             -- Array of tags for categorization
    
    -- Constraints
    CONSTRAINT valid_quantity_range CHECK (quantity_min IS NULL OR quantity_max IS NULL OR quantity_min <= quantity_max),
    CONSTRAINT valid_budget CHECK (budget_max_price IS NULL OR budget_max_price > 0),
    CONSTRAINT valid_status CHECK (status IN ('DRAFT', 'ACTIVE', 'MATCHED', 'PARTIALLY_FULFILLED', 'FULFILLED', 'EXPIRED', 'CANCELLED')),
    CONSTRAINT valid_visibility CHECK (visibility IN ('PUBLIC', 'PRIVATE', 'RESTRICTED')),
    CONSTRAINT valid_approval CHECK (approval_status IN ('PENDING', 'APPROVED', 'REJECTED', 'AUTO_APPROVED'))
);

-- Indexes for Performance
CREATE INDEX idx_requirements_buyer ON requirements(buyer_id);
CREATE INDEX idx_requirements_commodity ON requirements(commodity_type);
CREATE INDEX idx_requirements_status ON requirements(status) WHERE status IN ('ACTIVE', 'MATCHED');
CREATE INDEX idx_requirements_visibility ON requirements(visibility);
CREATE INDEX idx_requirements_expires ON requirements(expires_at) WHERE expires_at IS NOT NULL;
CREATE INDEX idx_requirements_created ON requirements(created_at DESC);

-- Composite Indexes for Smart Matching
CREATE INDEX idx_requirements_commodity_status ON requirements(commodity_type, status) 
    WHERE status = 'ACTIVE';
CREATE INDEX idx_requirements_buyer_status ON requirements(buyer_id, status);

-- JSONB Indexes for Quality Search
CREATE INDEX idx_requirements_quality_gin ON requirements USING GIN(quality_required);
CREATE INDEX idx_requirements_quality_tolerance ON requirements USING GIN(quality_tolerance);

-- Vector Index for AI Semantic Search
CREATE INDEX idx_requirements_ai_vector ON requirements USING ivfflat(ai_match_vector vector_cosine_ops)
    WITH (lists = 100);

-- Geo-spatial Index for Delivery Location
CREATE INDEX idx_requirements_delivery_location ON requirements USING GIN(delivery_location);

-- Auto-update Triggers
CREATE TRIGGER update_requirements_updated_at
    BEFORE UPDATE ON requirements
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Auto-calculate quantity_fulfilled
CREATE OR REPLACE FUNCTION calculate_requirement_fulfilled_quantity()
RETURNS TRIGGER AS $$
BEGIN
    -- Recalculate from trade_allocations table (will be created in Engine 5)
    -- Placeholder for now
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

**Estimated Lines:** ~400 lines

---

### Phase 2: Domain Models & Events (Day 1-2)

#### File 1: `backend/modules/trade_desk/enums.py` (UPDATE)

Add new enums:

```python
class RequirementStatus(str, Enum):
    """
    Lifecycle status of a requirement posting.
    
    DRAFT: Created but not yet posted
    ACTIVE: Posted and searching for matches
    MATCHED: Compatible availabilities found
    PARTIALLY_FULFILLED: Some quantity fulfilled
    FULFILLED: Fully fulfilled (converted to trade)
    EXPIRED: Past expiry date
    CANCELLED: Cancelled by buyer
    """
    DRAFT = "DRAFT"
    ACTIVE = "ACTIVE"
    MATCHED = "MATCHED"
    PARTIALLY_FULFILLED = "PARTIALLY_FULFILLED"
    FULFILLED = "FULFILLED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"


class RequirementPriority(str, Enum):
    """
    Urgency level for requirement fulfillment.
    
    URGENT: Need immediately
    HIGH: High priority
    NORMAL: Standard priority
    LOW: Can wait
    """
    URGENT = "URGENT"
    HIGH = "HIGH"
    NORMAL = "NORMAL"
    LOW = "LOW"
```

#### File 2: `backend/modules/trade_desk/models/requirement.py` (NEW)

```python
"""
Requirement Model

Represents a buyer's commodity requirement posting.
Mirror of Availability model but from buyer perspective.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any, List
from uuid import UUID

from sqlalchemy import Column, String, Numeric, DateTime, Text, Boolean, Integer, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from pgvector.sqlalchemy import Vector

from backend.core.events.event_mixin import EventMixin
from backend.db.base_class import Base


class Requirement(Base, EventMixin):
    """
    Buyer Requirement Model
    
    Buyers post what they want to buy, system finds compatible sellers.
    """
    __tablename__ = "requirements"
    
    # Primary Key
    id = Column(PGUUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    
    # Core Fields
    commodity_type = Column(String(100), nullable=False, index=True)
    buyer_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    buyer_company_id = Column(PGUUID(as_uuid=True), nullable=True)
    
    # Quantity Specifications
    quantity_required = Column(Numeric(20, 4), nullable=False)
    quantity_min = Column(Numeric(20, 4), nullable=True)
    quantity_max = Column(Numeric(20, 4), nullable=True)
    quantity_unit = Column(String(20), nullable=False)
    quantity_fulfilled = Column(Numeric(20, 4), default=0)
    
    # Quality Parameters
    quality_required = Column(JSONB, nullable=False)
    quality_tolerance = Column(JSONB, nullable=True)
    
    # Price Constraints
    budget_max_price = Column(Numeric(20, 4), nullable=True)
    budget_total = Column(Numeric(20, 4), nullable=True)
    price_currency = Column(String(10), default="USD")
    
    # Delivery Preferences
    delivery_location = Column(JSONB, nullable=True)
    delivery_radius_km = Column(Integer, nullable=True)
    delivery_date_required = Column(DateTime, nullable=True)
    delivery_date_flexible = Column(Boolean, default=True)
    
    # Market Visibility
    visibility = Column(String(20), default="PUBLIC")
    private_sellers = Column(JSONB, nullable=True)
    
    # Lifecycle Status
    status = Column(String(20), default="DRAFT", index=True)
    approval_status = Column(String(20), default="PENDING")
    approval_notes = Column(Text, nullable=True)
    approved_by = Column(PGUUID(as_uuid=True), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # AI Fields
    ai_match_vector = Column(Vector(1536), nullable=True)
    ai_suggested_alternatives = Column(JSONB, nullable=True)
    match_count = Column(Integer, default=0)
    best_match_score = Column(Numeric(5, 4), nullable=True)
    
    # Audit Trail
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(PGUUID(as_uuid=True), nullable=False)
    updated_by = Column(PGUUID(as_uuid=True), nullable=True)
    expires_at = Column(DateTime, nullable=True)
    fulfilled_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    cancellation_reason = Column(Text, nullable=True)
    
    # Metadata
    notes = Column(Text, nullable=True)
    internal_reference = Column(String(100), nullable=True)
    priority = Column(String(20), default="NORMAL")
    tags = Column(JSONB, nullable=True)
    
    # Constraints
    __table_args__ = (
        CheckConstraint("quantity_min IS NULL OR quantity_max IS NULL OR quantity_min <= quantity_max", name="valid_quantity_range"),
        CheckConstraint("budget_max_price IS NULL OR budget_max_price > 0", name="valid_budget"),
        CheckConstraint("status IN ('DRAFT', 'ACTIVE', 'MATCHED', 'PARTIALLY_FULFILLED', 'FULFILLED', 'EXPIRED', 'CANCELLED')", name="valid_status"),
        CheckConstraint("visibility IN ('PUBLIC', 'PRIVATE', 'RESTRICTED')", name="valid_visibility"),
    )
    
    # Business Logic Methods
    
    def can_activate(self) -> bool:
        """Check if requirement can be activated"""
        return (
            self.status == "DRAFT" and
            self.approval_status == "APPROVED" and
            self.quantity_required > 0
        )
    
    def can_match(self) -> bool:
        """Check if requirement can be matched"""
        return self.status in ["ACTIVE", "MATCHED"]
    
    def can_cancel(self) -> bool:
        """Check if requirement can be cancelled"""
        return self.status not in ["FULFILLED", "CANCELLED"]
    
    def update_match_stats(self, match_count: int, best_score: float, user_id: UUID):
        """Update match statistics"""
        self.match_count = match_count
        self.best_match_score = Decimal(str(best_score))
        self.updated_by = user_id
        self.emit_match_stats_updated(user_id, match_count, best_score)
    
    def mark_fulfilled(self, quantity: Decimal, user_id: UUID, trade_id: UUID):
        """Mark requirement as fulfilled (completely or partially)"""
        self.quantity_fulfilled += quantity
        
        if self.quantity_fulfilled >= self.quantity_required:
            self.status = "FULFILLED"
            self.fulfilled_at = datetime.utcnow()
            self.emit_fulfilled(user_id, trade_id)
        else:
            self.status = "PARTIALLY_FULFILLED"
            self.emit_partially_fulfilled(user_id, quantity, trade_id)
        
        self.updated_by = user_id
    
    def cancel(self, reason: str, user_id: UUID):
        """Cancel requirement"""
        if not self.can_cancel():
            raise ValueError(f"Cannot cancel requirement in {self.status} status")
        
        self.status = "CANCELLED"
        self.cancelled_at = datetime.utcnow()
        self.cancellation_reason = reason
        self.updated_by = user_id
        self.emit_cancelled(user_id, reason)
    
    # Event Emission Methods (will integrate with EventMixin)
    
    def emit_created(self, user_id: UUID):
        """Emit requirement.created event"""
        from backend.modules.trade_desk.events.requirement_events import RequirementCreatedEvent
        self.add_domain_event(RequirementCreatedEvent(
            requirement_id=self.id,
            buyer_id=self.buyer_id,
            commodity_type=self.commodity_type,
            quantity_required=float(self.quantity_required),
            quality_required=self.quality_required,
            user_id=user_id
        ))
    
    def emit_updated(self, user_id: UUID, changes: Dict[str, Any]):
        """Emit requirement.updated event"""
        from backend.modules.trade_desk.events.requirement_events import RequirementUpdatedEvent
        self.add_domain_event(RequirementUpdatedEvent(
            requirement_id=self.id,
            changes=changes,
            user_id=user_id
        ))
    
    def emit_match_stats_updated(self, user_id: UUID, match_count: int, best_score: float):
        """Emit requirement.match_stats_updated micro-event"""
        from backend.modules.trade_desk.events.requirement_events import RequirementMatchStatsUpdatedEvent
        self.add_domain_event(RequirementMatchStatsUpdatedEvent(
            requirement_id=self.id,
            match_count=match_count,
            best_match_score=best_score,
            user_id=user_id
        ))
    
    def emit_fulfilled(self, user_id: UUID, trade_id: UUID):
        """Emit requirement.fulfilled event"""
        from backend.modules.trade_desk.events.requirement_events import RequirementFulfilledEvent
        self.add_domain_event(RequirementFulfilledEvent(
            requirement_id=self.id,
            trade_id=trade_id,
            user_id=user_id
        ))
    
    def emit_partially_fulfilled(self, user_id: UUID, quantity: Decimal, trade_id: UUID):
        """Emit requirement.partially_fulfilled event"""
        from backend.modules.trade_desk.events.requirement_events import RequirementPartiallyFulfilledEvent
        self.add_domain_event(RequirementPartiallyFulfilledEvent(
            requirement_id=self.id,
            quantity_fulfilled=float(quantity),
            trade_id=trade_id,
            user_id=user_id
        ))
    
    def emit_cancelled(self, user_id: UUID, reason: str):
        """Emit requirement.cancelled event"""
        from backend.modules.trade_desk.events.requirement_events import RequirementCancelledEvent
        self.add_domain_event(RequirementCancelledEvent(
            requirement_id=self.id,
            reason=reason,
            user_id=user_id
        ))
```

**Estimated Lines:** ~250 lines

#### File 3: `backend/modules/trade_desk/events/requirement_events.py` (NEW)

```python
"""
Requirement Events

Domain events for requirement lifecycle and matching.
10 event types mirroring availability events.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

from backend.core.events.base import DomainEvent


@dataclass
class RequirementCreatedEvent(DomainEvent):
    """Emitted when a new requirement is created"""
    event_type: str = "requirement.created"
    requirement_id: UUID
    buyer_id: UUID
    commodity_type: str
    quantity_required: float
    quality_required: Dict[str, Any]
    user_id: UUID


@dataclass
class RequirementUpdatedEvent(DomainEvent):
    """Emitted when requirement is updated"""
    event_type: str = "requirement.updated"
    requirement_id: UUID
    changes: Dict[str, Any]
    user_id: UUID


@dataclass
class RequirementActivatedEvent(DomainEvent):
    """Emitted when requirement is activated (posted to market)"""
    event_type: str = "requirement.activated"
    requirement_id: UUID
    visibility: str
    user_id: UUID


@dataclass
class RequirementMatchFoundEvent(DomainEvent):
    """Emitted when compatible availability is found"""
    event_type: str = "requirement.match_found"
    requirement_id: UUID
    availability_id: UUID
    match_score: float
    user_id: UUID


@dataclass
class RequirementMatchStatsUpdatedEvent(DomainEvent):
    """Micro-event: Match statistics updated (real-time UI update)"""
    event_type: str = "requirement.match_stats_updated"
    requirement_id: UUID
    match_count: int
    best_match_score: float
    user_id: UUID


@dataclass
class RequirementPartiallyFulfilledEvent(DomainEvent):
    """Emitted when requirement is partially fulfilled"""
    event_type: str = "requirement.partially_fulfilled"
    requirement_id: UUID
    quantity_fulfilled: float
    trade_id: UUID
    user_id: UUID


@dataclass
class RequirementFulfilledEvent(DomainEvent):
    """Emitted when requirement is fully fulfilled"""
    event_type: str = "requirement.fulfilled"
    requirement_id: UUID
    trade_id: UUID
    user_id: UUID


@dataclass
class RequirementExpiredEvent(DomainEvent):
    """Emitted when requirement expires"""
    event_type: str = "requirement.expired"
    requirement_id: UUID
    user_id: UUID


@dataclass
class RequirementCancelledEvent(DomainEvent):
    """Emitted when requirement is cancelled"""
    event_type: str = "requirement.cancelled"
    requirement_id: UUID
    reason: str
    user_id: UUID


@dataclass
class RequirementBudgetAdjustedEvent(DomainEvent):
    """Emitted when budget constraints are adjusted"""
    event_type: str = "requirement.budget_adjusted"
    requirement_id: UUID
    old_budget: Optional[float]
    new_budget: float
    user_id: UUID
```

**Estimated Lines:** ~120 lines

---

### Phase 3: Repository Layer (Day 2-3)

**File:** `backend/modules/trade_desk/repositories/requirement_repository.py` (NEW)

**Key Methods:**
1. `create()` - Create requirement
2. `get_by_id()` - Get by ID
3. `get_by_buyer()` - Get all requirements for a buyer
4. `search_compatible_availabilities()` - ⭐ CORE: Find matching inventory
5. `update()` - Update requirement
6. `delete()` - Soft delete
7. `get_active_requirements()` - Get all active requirements
8. `get_expiring_soon()` - Get requirements expiring within N days

**Smart Matching Algorithm:**

```python
async def search_compatible_availabilities(
    self,
    requirement: Requirement,
    limit: int = 50
) -> List[Tuple[Availability, float]]:
    """
    Find compatible availabilities for a requirement.
    
    Returns list of (availability, match_score) tuples sorted by score.
    Match score: 0.0 (no match) to 1.0 (perfect match)
    
    Matching Criteria:
    1. Commodity type exact match (mandatory)
    2. Quantity overlap (availability has enough)
    3. Quality compatibility (within tolerance)
    4. Price compatibility (within budget)
    5. Delivery location proximity
    6. AI vector similarity (semantic match)
    """
    
    # Build base query
    query = select(Availability).where(
        Availability.commodity_type == requirement.commodity_type,
        Availability.status == "ACTIVE",
        Availability.quantity_available >= requirement.quantity_min
    )
    
    # Apply visibility filters
    # ... (similar to availability smart_search)
    
    results = await self.session.execute(query)
    availabilities = results.scalars().all()
    
    # Score each availability
    scored_matches = []
    for avail in availabilities:
        score = self._calculate_match_score(requirement, avail)
        if score >= 0.5:  # Minimum threshold
            scored_matches.append((avail, score))
    
    # Sort by score descending
    scored_matches.sort(key=lambda x: x[1], reverse=True)
    
    return scored_matches[:limit]


def _calculate_match_score(
    self,
    requirement: Requirement,
    availability: Availability
) -> float:
    """
    Calculate match score between requirement and availability.
    
    Scoring Components (weighted):
    - Quantity match: 20%
    - Quality match: 30%
    - Price match: 25%
    - Location match: 15%
    - AI vector similarity: 10%
    """
    
    score = 0.0
    
    # 1. Quantity Match (20%)
    if availability.quantity_available >= requirement.quantity_required:
        score += 0.20
    elif availability.quantity_available >= requirement.quantity_min:
        # Partial match
        ratio = availability.quantity_available / requirement.quantity_required
        score += 0.20 * ratio
    
    # 2. Quality Match (30%)
    quality_score = self._calculate_quality_match(
        requirement.quality_required,
        requirement.quality_tolerance,
        availability.quality_params
    )
    score += 0.30 * quality_score
    
    # 3. Price Match (25%)
    if requirement.budget_max_price:
        # Check if availability price is within budget
        avail_price = availability.base_price
        if avail_price <= requirement.budget_max_price:
            score += 0.25
        elif avail_price <= requirement.budget_max_price * 1.1:  # 10% tolerance
            score += 0.15
    else:
        score += 0.25  # No budget constraint = perfect match
    
    # 4. Location Match (15%)
    if requirement.delivery_location and availability.origin_location:
        distance_score = self._calculate_proximity_score(
            requirement.delivery_location,
            availability.origin_location,
            requirement.delivery_radius_km
        )
        score += 0.15 * distance_score
    else:
        score += 0.15  # No location constraint
    
    # 5. AI Vector Similarity (10%)
    if requirement.ai_match_vector and availability.ai_score_vector:
        vector_score = self._cosine_similarity(
            requirement.ai_match_vector,
            availability.ai_score_vector
        )
        score += 0.10 * vector_score
    else:
        score += 0.05  # Partial credit if vectors missing
    
    return min(score, 1.0)  # Cap at 1.0
```

**Estimated Lines:** ~700 lines

---

### Phase 4: Service Layer (Day 3-4)

**File:** `backend/modules/trade_desk/services/requirement_service.py` (NEW)

**Key Methods:**
1. `create_requirement()` - Create with AI pipeline
2. `update_requirement()` - Update with change detection
3. `activate_requirement()` - Post to market, trigger matching
4. `search_matches()` - Find compatible availabilities
5. `get_buyer_requirements()` - Get all buyer's requirements
6. `cancel_requirement()` - Cancel with reason
7. `auto_match_new_availability()` - ⭐ Called when new availability posted
8. `refresh_match_stats()` - Recalculate match counts

**AI Integration Pipeline (10 steps for creation):**

```python
async def create_requirement(
    self,
    buyer_id: UUID,
    commodity_type: str,
    quantity_required: Decimal,
    quality_required: Dict[str, Any],
    user: User,
    **kwargs
) -> Requirement:
    """
    Create requirement with AI-enhanced pipeline.
    
    AI Pipeline:
    1. Validate commodity type
    2. Normalize quality requirements
    3. Detect budget anomalies
    4. Calculate AI match vector
    5. Suggest alternative specifications
    6. Find initial compatible matches
    7. Calculate match statistics
    8. Emit domain events
    9. Send notifications
    10. Return requirement with match stats
    """
    
    # Step 1: Validate commodity
    # ...
    
    # Step 2: Normalize quality (AI)
    normalized_quality = await self._normalize_quality_requirements(
        commodity_type, quality_required
    )
    
    # Step 3: Budget anomaly detection (AI)
    if kwargs.get("budget_max_price"):
        await self._detect_budget_anomaly(
            commodity_type,
            kwargs["budget_max_price"],
            quality_required
        )
    
    # Step 4: Calculate AI vector
    ai_vector = await self._calculate_ai_match_vector(
        commodity_type, normalized_quality
    )
    
    # Step 5: AI alternative suggestions
    alternatives = await self._suggest_alternative_specs(
        commodity_type, quality_required
    )
    
    # Create requirement
    requirement = Requirement(
        commodity_type=commodity_type,
        buyer_id=buyer_id,
        quantity_required=quantity_required,
        quality_required=normalized_quality,
        ai_match_vector=ai_vector,
        ai_suggested_alternatives=alternatives,
        created_by=user.id,
        **kwargs
    )
    
    # Step 6-7: Find initial matches
    if requirement.status == "ACTIVE":
        await self._refresh_match_stats(requirement)
    
    # Save
    await self.repo.create(requirement)
    
    # Step 8: Emit events
    requirement.emit_created(user.id)
    await self.event_publisher.publish_all(requirement.collect_events())
    
    # Step 9: Notifications
    await self._notify_compatible_sellers(requirement)
    
    return requirement


async def auto_match_new_availability(
    self,
    availability: Availability
) -> List[Requirement]:
    """
    ⭐ CRITICAL: Called when new availability is posted.
    
    Find all active requirements that match this availability.
    Notify buyers of new compatible inventory.
    
    This enables real-time "I found what you need!" notifications.
    """
    
    # Find active requirements for this commodity
    active_requirements = await self.repo.get_active_by_commodity(
        availability.commodity_type
    )
    
    matched_requirements = []
    
    for req in active_requirements:
        # Calculate match score
        score = self.repo._calculate_match_score(req, availability)
        
        if score >= 0.5:  # Minimum threshold
            # Update match stats
            req.match_count += 1
            if score > (req.best_match_score or 0):
                req.best_match_score = score
            
            # Emit match found event
            req.emit_match_found(availability.id, score)
            
            matched_requirements.append(req)
            
            # Notify buyer
            await self._notify_buyer_new_match(req, availability, score)
    
    return matched_requirements
```

**AI Integration Hooks (5 TODO placeholders):**

```python
async def _normalize_quality_requirements(
    self, commodity_type: str, quality: Dict[str, Any]
) -> Dict[str, Any]:
    """
    TODO: AI Integration - Normalize quality specs to standard format.
    
    Examples:
    - "34mm" → {"staple_length": 34, "unit": "mm"}
    - "99.9% pure gold" → {"purity": 99.9, "unit": "percent"}
    """
    return quality  # Placeholder


async def _detect_budget_anomaly(
    self, commodity_type: str, budget: Decimal, quality: Dict[str, Any]
):
    """
    TODO: AI Integration - Detect unrealistic budgets.
    
    Alert if budget is significantly below market rate for quality.
    """
    pass


async def _calculate_ai_match_vector(
    self, commodity_type: str, quality: Dict[str, Any]
) -> Optional[List[float]]:
    """
    TODO: AI Integration - Generate embedding vector for semantic search.
    
    Use OpenAI Embeddings API.
    """
    return None


async def _suggest_alternative_specs(
    self, commodity_type: str, quality: Dict[str, Any]
) -> Dict[str, Any]:
    """
    TODO: AI Integration - Suggest alternative quality specifications.
    
    "Can't find 34mm cotton? Try 33-35mm range"
    """
    return {}


async def _cosine_similarity(
    self, vec1: List[float], vec2: List[float]
) -> float:
    """
    TODO: AI Integration - Calculate vector similarity.
    """
    return 0.0
```

**Estimated Lines:** ~900 lines

---

### Phase 5: REST API + Schemas (Day 4-5)

**File 1:** `backend/modules/trade_desk/routes/requirement_routes.py` (NEW)

**Endpoints (11 total):**

```python
# Public Endpoints (Buyers)
POST   /requirements                    # Create requirement
GET    /requirements/search-matches     # Search compatible availabilities
GET    /requirements/my                 # Get my requirements
GET    /requirements/{id}               # Get requirement details
PUT    /requirements/{id}               # Update requirement
DELETE /requirements/{id}               # Cancel requirement
POST   /requirements/{id}/activate      # Activate (post to market)
GET    /requirements/{id}/matches       # Get compatible availabilities
POST   /requirements/{id}/refresh-matches  # Re-run matching algorithm

# Internal Endpoints (System)
POST   /requirements/{id}/mark-fulfilled  # Mark as fulfilled (from Engine 5)
POST   /requirements/{id}/auto-match      # Trigger auto-matching
```

**Authentication & RBAC:**
- All endpoints require JWT authentication via `get_current_user`
- Internal endpoints require RBAC permissions:
  - `requirement.fulfill` - Mark as fulfilled
  - `requirement.auto_match` - Trigger matching

**Example Endpoint:**

```python
@router.post("/requirements", response_model=RequirementResponse)
async def create_requirement(
    data: CreateRequirementRequest,
    current_user: User = Depends(get_current_user),
    service: RequirementService = Depends(get_requirement_service)
):
    """
    Create a new commodity requirement.
    
    Buyers specify what they want to buy, system finds compatible sellers.
    """
    requirement = await service.create_requirement(
        buyer_id=current_user.id,
        commodity_type=data.commodity_type,
        quantity_required=data.quantity_required,
        quality_required=data.quality_required,
        user=current_user,
        # ... other fields
    )
    
    return RequirementResponse.from_orm(requirement)


@router.get("/requirements/{id}/matches", response_model=RequirementMatchesResponse)
async def get_requirement_matches(
    id: UUID,
    current_user: User = Depends(get_current_user),
    service: RequirementService = Depends(get_requirement_service)
):
    """
    Get compatible availabilities for a requirement.
    
    Returns list of availabilities sorted by match score.
    """
    requirement = await service.get_by_id(id)
    
    # Verify ownership
    if requirement.buyer_id != current_user.id:
        raise HTTPException(403, "Not your requirement")
    
    matches = await service.search_matches(requirement)
    
    return RequirementMatchesResponse(
        requirement_id=id,
        matches=[
            MatchResult(
                availability=AvailabilityResponse.from_orm(avail),
                match_score=score
            )
            for avail, score in matches
        ]
    )
```

**Estimated Lines:** ~500 lines

#### File 2: `backend/modules/trade_desk/schemas/__init__.py` (UPDATE)

Add requirement schemas:

```python
# Request Schemas
class CreateRequirementRequest(BaseModel):
    commodity_type: str
    quantity_required: Decimal
    quantity_min: Optional[Decimal]
    quantity_max: Optional[Decimal]
    quantity_unit: str
    quality_required: Dict[str, Any]
    quality_tolerance: Optional[Dict[str, Any]]
    budget_max_price: Optional[Decimal]
    budget_total: Optional[Decimal]
    delivery_location: Optional[Dict[str, Any]]
    delivery_radius_km: Optional[int]
    delivery_date_required: Optional[datetime]
    visibility: str = "PUBLIC"
    priority: str = "NORMAL"
    notes: Optional[str]


class UpdateRequirementRequest(BaseModel):
    quantity_required: Optional[Decimal]
    quality_required: Optional[Dict[str, Any]]
    budget_max_price: Optional[Decimal]
    delivery_date_required: Optional[datetime]
    # ... other updatable fields


# Response Schemas
class RequirementResponse(BaseModel):
    id: UUID
    commodity_type: str
    buyer_id: UUID
    quantity_required: Decimal
    quantity_fulfilled: Decimal
    quality_required: Dict[str, Any]
    budget_max_price: Optional[Decimal]
    status: str
    match_count: int
    best_match_score: Optional[Decimal]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MatchResult(BaseModel):
    availability: AvailabilityResponse
    match_score: float
    compatibility_details: Dict[str, Any]  # Quality match, price match, etc.


class RequirementMatchesResponse(BaseModel):
    requirement_id: UUID
    total_matches: int
    matches: List[MatchResult]
```

**Estimated Lines:** +300 lines to existing schemas file

---

### Phase 6: WebSocket Channels (Day 5)

**File:** `backend/modules/trade_desk/websockets/requirement_channels.py` (NEW)

**Channels:**
1. `requirement.{id}.matches` - Real-time match updates
2. `buyer.{buyer_id}.requirements` - Buyer's requirement feed
3. `requirement.match_found` - Global match notifications

**Integration:** Reuse existing WebSocket infrastructure from Availability Engine.

**Estimated Lines:** ~200 lines

---

### Phase 7: Testing (Day 5-6)

**Test Files (7 files):**

1. `backend/tests/trade_desk/test_requirement_model.py` (~200 lines)
   - Test Requirement model methods
   - Test event emission
   - Test business logic validation

2. `backend/tests/trade_desk/test_requirement_repository.py` (~300 lines)
   - Test CRUD operations
   - Test `search_compatible_availabilities()`
   - Test match scoring algorithm
   - Test quality/price/location matching

3. `backend/tests/trade_desk/test_requirement_service.py` (~350 lines)
   - Test requirement creation pipeline
   - Test `auto_match_new_availability()`
   - Test match stats refresh
   - Test notification triggers

4. `backend/tests/trade_desk/test_requirement_api.py` (~400 lines)
   - Test all 11 REST endpoints
   - Test authentication/authorization
   - Test validation errors
   - Test workflow: create → activate → match → fulfill

5. `backend/tests/trade_desk/test_matching_algorithm.py` (~300 lines)
   - Test match scoring components
   - Test quality tolerance matching
   - Test price range validation
   - Test geo-proximity calculation
   - Test edge cases

6. `backend/tests/trade_desk/test_requirement_multi_commodity.py` (~250 lines)
   - Test Cotton requirements
   - Test Gold requirements
   - Test Wheat requirements
   - Test cross-commodity compatibility

7. `backend/tests/trade_desk/conftest.py` (UPDATE ~100 lines)
   - Add requirement fixtures
   - Add matching test data
   - Add buyer user fixtures

**Target:** 100% test coverage, all tests passing

**Estimated Lines:** ~1,900 lines total

---

### Phase 8: Documentation (Day 6-7)

**Files:**

1. `REQUIREMENT_ENGINE_IMPLEMENTATION.md` (~400 lines)
   - Technical documentation
   - Database schema explanation
   - Matching algorithm details
   - API endpoint guide

2. `REQUIREMENT_ENGINE_COMPLETE.md` (~600 lines)
   - Complete implementation summary
   - Test results
   - Deployment checklist
   - Next steps (Engine 3)

**Estimated Lines:** ~1,000 lines

---

## 📊 Deliverables Summary

| Phase | Component | Files | Est. Lines | Days |
|-------|-----------|-------|-----------|------|
| 1 | Database Schema | 1 migration | ~400 | 1 |
| 2 | Models & Events | 3 files (1 update, 2 new) | ~500 | 1-2 |
| 3 | Repository | 1 file | ~700 | 2-3 |
| 4 | Service Layer | 1 file | ~900 | 3-4 |
| 5 | REST API + Schemas | 2 files (1 new, 1 update) | ~800 | 4-5 |
| 6 | WebSocket | 1 file | ~200 | 5 |
| 7 | Testing | 7 files (6 new, 1 update) | ~1,900 | 5-6 |
| 8 | Documentation | 2 files | ~1,000 | 6-7 |
| **TOTAL** | | **18 files** | **~6,400 lines** | **5-7 days** |

**Additional Updates:**
- Update `__init__.py` files (6 files) to export new components
- Update API router registration
- Update Alembic migration chain

---

## 🔗 Integration Points

### With Engine 1 (Availability)

1. **Bi-directional Matching:**
   - When buyer creates requirement → search existing availabilities
   - When seller posts availability → notify matching requirements

2. **Shared Enums:**
   - `MarketVisibility` (PUBLIC, PRIVATE, RESTRICTED)
   - `ApprovalStatus` (PENDING, APPROVED, REJECTED)
   - `PriceType` (FIXED, MATRIX, NEGOTIABLE)

3. **Shared Services:**
   - AI vector calculation (same embedding model)
   - Quality normalization (same commodity rules)
   - Geo-proximity calculation (same algorithm)

### With Engine 3 (Matching - Future)

- Requirement and Availability will feed into Matching Engine
- Matching Engine will create `Match` entities
- Match entities link requirement_id ↔ availability_id

### With Engine 5 (Trade Finalization - Future)

- When trade finalized → call `mark_fulfilled()` on requirement
- When trade finalized → call `mark_sold()` on availability

---

## 🎯 Success Metrics

**Code Quality:**
- ✅ 100% test coverage (all tests passing)
- ✅ Type hints on all functions
- ✅ Docstrings on all public methods
- ✅ Consistent with Engine 1 patterns

**Performance:**
- ✅ Sub-200ms requirement creation
- ✅ <1 second for match search
- ✅ <100ms for match score calculation
- ✅ Efficient database queries (explain analyze)

**Functionality:**
- ✅ Multi-commodity support validated
- ✅ Match scoring algorithm accurate
- ✅ Real-time notifications working
- ✅ RBAC permissions enforced
- ✅ Event sourcing complete

**Documentation:**
- ✅ API documentation complete
- ✅ Architecture diagrams
- ✅ Deployment runbook
- ✅ Developer guide

---

## 🚀 Deployment Checklist

- [ ] Database migration tested on staging
- [ ] All tests passing (pytest 100%)
- [ ] API endpoints tested (Postman/curl)
- [ ] WebSocket channels tested
- [ ] Load testing (100 concurrent users)
- [ ] Security audit (RBAC, SQL injection, XSS)
- [ ] Documentation review
- [ ] Code review (PR approval)
- [ ] Merge to main
- [ ] Tag release: `v1.1.0-requirement-engine`

---

## ⚠️ Critical Decisions Needed

Before starting implementation, please confirm:

### 1. Auto-Matching Behavior

**Question:** When new availability is posted, should we automatically notify buyers with matching requirements?

**Options:**
- A) ✅ **YES** - Real-time "We found what you need!" notifications (RECOMMENDED)
- B) NO - Buyers manually search for matches

**Recommendation:** Option A (2035-level experience)

### 2. Requirement Visibility

**Question:** Should requirements support PRIVATE visibility (buyer only wants specific sellers to see)?

**Options:**
- A) ✅ **YES** - Support PUBLIC/PRIVATE/RESTRICTED like availabilities (RECOMMENDED)
- B) NO - All requirements are PUBLIC

**Recommendation:** Option A (mirrors Availability symmetry)

### 3. Requirement Expiry

**Question:** Auto-expire old requirements?

**Options:**
- A) ✅ **YES** - Auto-expire after 30 days (configurable) (RECOMMENDED)
- B) NO - Requirements live forever until manually cancelled

**Recommendation:** Option A (prevents stale data)

### 4. Partial Fulfillment

**Question:** Allow requirement to be fulfilled by multiple availabilities?

**Options:**
- A) ✅ **YES** - Buyer needs 1000 bales, can buy 500 + 300 + 200 from different sellers (RECOMMENDED)
- B) NO - All-or-nothing fulfillment

**Recommendation:** Option A (realistic for large orders)

### 5. Match Notification Strategy

**Question:** How to notify buyers when new compatible inventory is posted?

**Options:**
- A) ✅ **Real-time WebSocket** + Email + In-app notification (RECOMMENDED)
- B) Email only
- C) In-app notification only

**Recommendation:** Option A (multi-channel for critical matches)

---

## 📝 Implementation Approach

**Same Systematic Process as Engine 1:**

1. ✅ Create feature branch: `feat/trade-desk-requirement-engine`
2. Implement Phase 1 (Database) → Commit
3. Implement Phase 2 (Models) → Commit
4. Implement Phase 3 (Repository) → Commit
5. Implement Phase 4 (Service) → Commit
6. Implement Phase 5 (API) → Commit
7. Implement Phase 6 (WebSocket) → Commit
8. Implement Phase 7 (Tests) → Commit → **Verify all passing**
9. Implement Phase 8 (Docs) → Commit
10. Final review → Merge to main → Tag release

**No shortcuts. No rushing. Complete each phase fully before moving to next.**

---

## 🎯 Final Notes

**This is NOT just CRUD.** This is:

- ⚡ Real-time match notifications ("We found what you need!")
- 🧠 AI-powered compatibility scoring
- 🌍 Multi-commodity global trading platform
- 🔄 Bi-directional matching (buyers ↔ sellers)
- 📊 Event-sourced audit trail
- 🎯 2035-level features in 2025

**Estimated Total Effort:** 5-7 days (same as Engine 1)

**Ready to build the future of commodity trading. Awaiting your approval to proceed.**

---

## ✅ APPROVAL REQUIRED

**Please confirm:**
1. ✅ Architecture approved (mirror of Engine 1)
2. ✅ Feature scope approved (all phases)
3. ✅ Critical decisions confirmed (auto-matching, visibility, expiry, partial fulfillment, notifications)
4. ✅ Timeline acceptable (5-7 days)

**Once approved, will start Phase 1 (Database Schema) immediately.**

---

*Generated on: November 24, 2025*  
*Branch: feat/trade-desk-requirement-engine*  
*For: Cotton ERP - Trade Desk Module - Engine 2 of 5*
