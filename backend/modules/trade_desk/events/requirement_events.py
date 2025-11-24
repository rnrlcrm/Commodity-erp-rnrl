"""
Requirement Events - Engine 2 of 5

Micro-events for real-time matching engine updates, intent-based routing, and audit trail.

Event Types (11 Total - Enhanced from 10):
1. requirement.created - New requirement posted
2. requirement.published - Requirement activated (DRAFT → ACTIVE)
3. requirement.updated - General update
4. requirement.budget_changed - Max budget or preferred price updated
5. requirement.quality_changed - Quality requirements updated
6. requirement.visibility_changed - Market visibility changed
7. requirement.fulfillment_updated - Purchase made (quantity/spend updated)
8. requirement.fulfilled - Fully fulfilled (all quantity purchased)
9. requirement.expired - Past expiry date
10. requirement.cancelled - Cancelled by buyer
11. requirement.ai_adjusted - 🚀 AI modified budget/quality/delivery (ENHANCEMENT #7)
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional
from uuid import UUID


@dataclass
class RequirementCreatedEvent:
    """
    Emitted when new requirement is posted.
    
    Triggers:
    - Intent-based routing (based on intent_type)
    - WebSocket broadcast to commodity.{id}.requirements channel
    - Seller notifications (if market_visibility = PUBLIC)
    - Analytics tracking
    """
    requirement_id: UUID
    buyer_id: UUID
    commodity_id: UUID
    min_quantity: Decimal
    max_quantity: Decimal
    max_budget_per_unit: Decimal
    quality_requirements: Dict[str, Any]
    market_visibility: str
    urgency_level: str
    intent_type: str  # 🚀 ENHANCEMENT #1
    buyer_priority_score: float  # 🚀 ENHANCEMENT #6
    created_by: UUID
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": str(self.requirement_id),
            "buyer_id": str(self.buyer_id),
            "commodity_id": str(self.commodity_id),
            "min_quantity": float(self.min_quantity),
            "max_quantity": float(self.max_quantity),
            "max_budget_per_unit": float(self.max_budget_per_unit),
            "quality_requirements": self.quality_requirements,
            "market_visibility": self.market_visibility,
            "urgency_level": self.urgency_level,
            "intent_type": self.intent_type,
            "buyer_priority_score": self.buyer_priority_score,
            "created_by": str(self.created_by),
            "created_at": self.created_at.isoformat(),
        }


@dataclass
class RequirementPublishedEvent:
    """
    Emitted when requirement transitions from DRAFT → ACTIVE.
    
    Triggers:
    - Intent-based routing:
      * DIRECT_BUY → Immediate matching engine
      * NEGOTIATION → Multi-round negotiation queue
      * AUCTION_REQUEST → Reverse auction module
      * PRICE_DISCOVERY_ONLY → Market insights dashboard
    - Auto-matching with availabilities
    - Seller notifications based on commodity & location
    - requirement.intent_updates WebSocket channel
    """
    requirement_id: UUID
    buyer_id: UUID
    commodity_id: UUID
    quality_requirements: Dict[str, Any]
    max_budget_per_unit: Decimal
    urgency_level: str
    intent_type: str  # 🚀 CRITICAL for routing
    market_visibility: str
    published_by: UUID
    published_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": str(self.requirement_id),
            "buyer_id": str(self.buyer_id),
            "commodity_id": str(self.commodity_id),
            "quality_requirements": self.quality_requirements,
            "max_budget_per_unit": float(self.max_budget_per_unit),
            "urgency_level": self.urgency_level,
            "intent_type": self.intent_type,
            "market_visibility": self.market_visibility,
            "published_by": str(self.published_by),
            "published_at": self.published_at.isoformat(),
        }


@dataclass
class RequirementUpdatedEvent:
    """
    General update event (non-specific changes).
    
    Triggers:
    - Audit trail logging
    - Cache invalidation
    - Matching engine re-scan (if quality/budget changed)
    """
    requirement_id: UUID
    updated_fields: Dict[str, Any]
    updated_by: UUID
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": str(self.requirement_id),
            "updated_fields": self.updated_fields,
            "updated_by": str(self.updated_by),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class RequirementBudgetChangedEvent:
    """
    MICRO-EVENT: Budget constraints changed.
    
    Triggers:
    - Matching engine re-score (price competitiveness recalculation)
    - Seller notifications (if budget increased → more sellers qualify)
    - AI anomaly detection (unrealistic budget check)
    - WebSocket broadcast to watchers
    
    Use Case: Buyer increases budget to get more matches
    """
    requirement_id: UUID
    old_max_budget: Decimal
    new_max_budget: Decimal
    old_preferred_price: Optional[Decimal]
    new_preferred_price: Optional[Decimal]
    budget_change_pct: Decimal
    changed_by: UUID
    changed_at: datetime
    reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": str(self.requirement_id),
            "old_max_budget": float(self.old_max_budget),
            "new_max_budget": float(self.new_max_budget),
            "old_preferred_price": float(self.old_preferred_price) if self.old_preferred_price else None,
            "new_preferred_price": float(self.new_preferred_price) if self.new_preferred_price else None,
            "budget_change_pct": float(self.budget_change_pct),
            "changed_by": str(self.changed_by),
            "changed_at": self.changed_at.isoformat(),
            "reason": self.reason,
        }


@dataclass
class RequirementQualityChangedEvent:
    """
    MICRO-EVENT: Quality requirements changed.
    
    Triggers:
    - Matching engine re-match (quality tolerance recalculation)
    - AI tolerance optimization (suggest relaxing if no matches)
    - WebSocket broadcast to watchers
    - Historical quality tracking
    
    Use Case: Buyer relaxes micronaire from 4.0-4.3 to 3.8-4.5 to get more matches
    """
    requirement_id: UUID
    old_quality_requirements: Dict[str, Any]
    new_quality_requirements: Dict[str, Any]
    changed_parameters: list
    tolerance_change_summary: Optional[str]
    changed_by: UUID
    changed_at: datetime
    reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": str(self.requirement_id),
            "old_quality_requirements": self.old_quality_requirements,
            "new_quality_requirements": self.new_quality_requirements,
            "changed_parameters": self.changed_parameters,
            "tolerance_change_summary": self.tolerance_change_summary,
            "changed_by": str(self.changed_by),
            "changed_at": self.changed_at.isoformat(),
            "reason": self.reason,
        }


@dataclass
class RequirementVisibilityChangedEvent:
    """
    MICRO-EVENT: Market visibility changed.
    
    Triggers:
    - Matching engine re-scan (if changed to PUBLIC)
    - Seller access control update
    - WebSocket targeted broadcast
    
    Use Case: Buyer changes from PRIVATE → PUBLIC (now visible to all sellers)
    """
    requirement_id: UUID
    old_visibility: str
    new_visibility: str
    changed_by: UUID
    changed_at: datetime
    reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": str(self.requirement_id),
            "old_visibility": self.old_visibility,
            "new_visibility": self.new_visibility,
            "changed_by": str(self.changed_by),
            "changed_at": self.changed_at.isoformat(),
            "reason": self.reason,
        }


@dataclass
class RequirementFulfillmentUpdatedEvent:
    """
    MICRO-EVENT: Buyer purchased from an availability (partial fulfillment).
    
    Triggers:
    - Matching engine urgency update (if partially fulfilled)
    - Remaining quantity recalculation
    - WebSocket fulfillment progress update
    - Auto-transition to FULFILLED if max_quantity reached
    
    Use Case: Buyer needed 500 bales, purchased 200, still needs 300
    """
    requirement_id: UUID
    purchased_quantity: Decimal
    amount_spent: Decimal
    total_purchased_quantity: Decimal
    total_spent: Decimal
    remaining_quantity: Decimal
    remaining_budget: Decimal
    fulfillment_percentage: Decimal
    trade_id: Optional[UUID]
    updated_by: UUID
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": str(self.requirement_id),
            "purchased_quantity": float(self.purchased_quantity),
            "amount_spent": float(self.amount_spent),
            "total_purchased_quantity": float(self.total_purchased_quantity),
            "total_spent": float(self.total_spent),
            "remaining_quantity": float(self.remaining_quantity),
            "remaining_budget": float(self.remaining_budget),
            "fulfillment_percentage": float(self.fulfillment_percentage),
            "trade_id": str(self.trade_id) if self.trade_id else None,
            "updated_by": str(self.updated_by),
            "updated_at": self.updated_at.isoformat(),
        }


@dataclass
class RequirementFulfilledEvent:
    """
    Emitted when requirement is fully fulfilled (status → FULFILLED).
    
    Triggers:
    - Matching engine stop (no more matching needed)
    - Analytics success tracking
    - Buyer satisfaction survey
    - AI learning (successful requirement patterns)
    """
    requirement_id: UUID
    buyer_id: UUID
    commodity_id: UUID
    total_quantity_purchased: Decimal
    total_spent: Decimal
    average_price_per_unit: Decimal
    number_of_trades: int
    fulfillment_duration_hours: Optional[float]
    fulfilled_by: UUID
    fulfilled_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": str(self.requirement_id),
            "buyer_id": str(self.buyer_id),
            "commodity_id": str(self.commodity_id),
            "total_quantity_purchased": float(self.total_quantity_purchased),
            "total_spent": float(self.total_spent),
            "average_price_per_unit": float(self.average_price_per_unit),
            "number_of_trades": self.number_of_trades,
            "fulfillment_duration_hours": self.fulfillment_duration_hours,
            "fulfilled_by": str(self.fulfilled_by),
            "fulfilled_at": self.fulfilled_at.isoformat(),
        }


@dataclass
class RequirementExpiredEvent:
    """
    Emitted when requirement expires (valid_until < NOW).
    
    Triggers:
    - Matching engine stop
    - Buyer notification (unfulfilled requirement)
    - Analytics tracking (expiry reasons)
    - AI learning (why didn't it get fulfilled?)
    """
    requirement_id: UUID
    buyer_id: UUID
    commodity_id: UUID
    unfulfilled_quantity: Decimal
    unspent_budget: Decimal
    active_duration_hours: float
    expired_at: datetime
    expiry_reason: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": str(self.requirement_id),
            "buyer_id": str(self.buyer_id),
            "commodity_id": str(self.commodity_id),
            "unfulfilled_quantity": float(self.unfulfilled_quantity),
            "unspent_budget": float(self.unspent_budget),
            "active_duration_hours": self.active_duration_hours,
            "expired_at": self.expired_at.isoformat(),
            "expiry_reason": self.expiry_reason,
        }


@dataclass
class RequirementCancelledEvent:
    """
    Emitted when buyer cancels requirement.
    
    Triggers:
    - Matching engine stop
    - Active negotiation cancellations
    - Analytics tracking
    - Seller notifications (if negotiations active)
    """
    requirement_id: UUID
    buyer_id: UUID
    commodity_id: UUID
    unfulfilled_quantity: Decimal
    cancelled_by: UUID
    cancelled_at: datetime
    cancellation_reason: str
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": str(self.requirement_id),
            "buyer_id": str(self.buyer_id),
            "commodity_id": str(self.commodity_id),
            "unfulfilled_quantity": float(self.unfulfilled_quantity),
            "cancelled_by": str(self.cancelled_by),
            "cancelled_at": self.cancelled_at.isoformat(),
            "cancellation_reason": self.cancellation_reason,
        }


@dataclass
class RequirementAIAdjustedEvent:
    """
    🚀 ENHANCEMENT #7: AI modified requirement parameters.
    
    Emitted when AI adjusts budget, quality tolerances, or delivery window.
    
    Triggers:
    - Explainability dashboard update (show why AI adjusted)
    - Buyer notification (AI suggestion)
    - Audit trail (AI decision tracking)
    - Matching engine re-match with new parameters
    - requirement.intent_updates WebSocket channel
    
    Use Case Examples:
    1. Market sentiment: "AI increased budget from 60K to 62K due to bullish market"
    2. Quality tolerance: "AI relaxed micronaire from 4.0-4.3 to 3.8-4.5 to increase matches by 15%"
    3. Delivery window: "AI extended delivery window by 3 days to improve logistics matching"
    
    Critical for:
    - Autonomous trade engine decision making
    - Transparency & trust in AI
    - Compliance & auditability
    """
    requirement_id: UUID
    adjustment_type: str  # 'budget', 'quality', 'delivery_window', 'multiple'
    old_value: Any
    new_value: Any
    ai_confidence: float  # 0.0 to 1.0
    ai_reasoning: str  # Human-readable explanation
    market_context: Optional[Dict[str, Any]]  # Market conditions that triggered adjustment
    expected_impact: Optional[str]  # "Expected to increase matches by 15%"
    adjusted_by_system: bool  # True if auto-adjusted, False if AI suggested and human approved
    adjusted_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "requirement_id": str(self.requirement_id),
            "adjustment_type": self.adjustment_type,
            "old_value": self.old_value,
            "new_value": self.new_value,
            "ai_confidence": self.ai_confidence,
            "ai_reasoning": self.ai_reasoning,
            "market_context": self.market_context,
            "expected_impact": self.expected_impact,
            "adjusted_by_system": self.adjusted_by_system,
            "adjusted_at": self.adjusted_at.isoformat(),
        }
