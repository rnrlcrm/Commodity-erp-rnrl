"""
Requirement Engine API Schemas - 2035-Ready

🚀 Enhanced Pydantic schemas with 7 critical enhancements:
1. Intent Layer (intent_type field)
2. AI Market Context Embedding (market_context_embedding)
3. Dynamic Delivery Flexibility (delivery_window, delivery_flexibility_hours)
4. Multi-Commodity Conversion (commodity_equivalents)
5. Negotiation Preferences (negotiation_preferences)
6. Buyer Trust Score (buyer_priority_score)
7. AI Adjustment Events (ai_adjustment endpoints)
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

from backend.modules.common.schemas.responses import ErrorResponse
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


# ========================================================================
# REQUEST SCHEMAS
# ========================================================================

class RequirementCreateRequest(BaseModel):
    """Request schema for creating requirement with all enhancements."""
    
    commodity_id: UUID
    variety_id: Optional[UUID] = None
    
    # Quantity (Min/Max Range for Flexibility)
    min_quantity: Decimal = Field(gt=0, description="Minimum acceptable quantity")
    max_quantity: Decimal = Field(gt=0, description="Maximum desired quantity")
    quantity_unit: str = Field(description="bales, kg, MT, etc.")
    preferred_quantity: Optional[Decimal] = Field(None, gt=0, description="Target/ideal quantity")
    
    # Quality Requirements (Min/Max/Preferred/Exact)
    quality_requirements: Dict[str, Any] = Field(
        description="Quality params with min/max/preferred/exact values"
    )
    
    # Budget & Pricing
    max_budget_per_unit: Decimal = Field(gt=0, description="Maximum price willing to pay")
    preferred_price_per_unit: Optional[Decimal] = Field(None, gt=0, description="Target/desired price")
    total_budget: Optional[Decimal] = Field(None, gt=0, description="Overall budget limit")
    currency_code: str = Field(default="INR", description="ISO 4217 currency code")
    
    # 🚀 Risk Management & Credit Control (Optional - Auto-calculated or fetched)
    buyer_branch_id: Optional[UUID] = Field(
        None, description="Buyer branch ID for internal trade blocking"
    )
    blocked_internal_trades: bool = Field(
        default=True, description="Block matching with same branch sellers"
    )
    
    # Payment & Delivery Preferences
    preferred_payment_terms: Optional[List[UUID]] = Field(
        None, description="Array of acceptable payment term IDs"
    )
    preferred_delivery_terms: Optional[List[UUID]] = Field(
        None, description="Array of acceptable delivery term IDs"
    )
    delivery_locations: Optional[List[Dict[str, Any]]] = Field(
        None, description="Multiple delivery locations with proximity"
    )
    
    # 🚀 ENHANCEMENT #3: Dynamic Delivery Flexibility
    delivery_window_start: Optional[datetime] = Field(
        None, description="Earliest acceptable delivery date"
    )
    delivery_window_end: Optional[datetime] = Field(
        None, description="Latest acceptable delivery date"
    )
    delivery_flexibility_hours: int = Field(
        default=168, ge=0, description="Flexibility window in hours (default: 7 days)"
    )
    
    # Market Visibility & Privacy
    market_visibility: str = Field(
        default="PUBLIC", description="PUBLIC, PRIVATE, RESTRICTED, INTERNAL"
    )
    invited_seller_ids: Optional[List[UUID]] = Field(
        None, description="Seller UUIDs for RESTRICTED visibility"
    )
    
    # Lifecycle
    valid_from: datetime = Field(description="Requirement valid from date")
    valid_until: datetime = Field(description="Requirement valid until date")
    urgency_level: str = Field(
        default="NORMAL", description="URGENT, NORMAL, PLANNING"
    )
    
    # 🚀 ENHANCEMENT #1: Intent Layer
    intent_type: str = Field(
        default="DIRECT_BUY",
        description="DIRECT_BUY, NEGOTIATION, AUCTION_REQUEST, PRICE_DISCOVERY_ONLY"
    )
    
    # 🚀 ENHANCEMENT #4: Multi-Commodity Conversion
    commodity_equivalents: Optional[Dict[str, Any]] = Field(
        None, description="Acceptable commodity substitutions with conversion ratios"
    )
    
    # 🚀 ENHANCEMENT #5: Negotiation Preferences
    negotiation_preferences: Optional[Dict[str, Any]] = Field(
        None, description="Self-negotiation settings and thresholds"
    )
    
    # Metadata
    notes: Optional[str] = Field(None, description="Buyer internal notes")
    attachments: Optional[List[Dict[str, Any]]] = Field(
        None, description="Specification files"
    )
    
    # Auto-publish flag
    auto_publish: bool = Field(
        default=False, description="If True, publish immediately (DRAFT → ACTIVE)"
    )
    
    @field_validator("max_quantity")
    def validate_max_greater_than_min(cls, v, info):
        if "min_quantity" in info.data and v < info.data["min_quantity"]:
            raise ValueError("max_quantity must be >= min_quantity")
        return v
    
    @field_validator("valid_until")
    def validate_valid_until_after_from(cls, v, info):
        if "valid_from" in info.data and v <= info.data["valid_from"]:
            raise ValueError("valid_until must be after valid_from")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "commodity_id": "123e4567-e89b-12d3-a456-426614174000",
                "min_quantity": 50.0,
                "max_quantity": 100.0,
                "quantity_unit": "bales",
                "preferred_quantity": 75.0,
                "quality_requirements": {
                    "staple_length": {"min": 28, "max": 30, "preferred": 29},
                    "micronaire": {"min": 3.8, "max": 4.5},
                    "strength": {"min": 26}
                },
                "max_budget_per_unit": 75000.0,
                "preferred_price_per_unit": 70000.0,
                "total_budget": 5250000.0,
                "currency_code": "INR",
                "delivery_window_start": "2025-12-01T00:00:00Z",
                "delivery_window_end": "2025-12-15T00:00:00Z",
                "delivery_flexibility_hours": 168,
                "market_visibility": "PUBLIC",
                "urgency_level": "NORMAL",
                "intent_type": "DIRECT_BUY",
                "valid_from": "2025-11-25T00:00:00Z",
                "valid_until": "2025-12-31T23:59:59Z",
                "auto_publish": True
            }
        }


class RequirementUpdateRequest(BaseModel):
    """Request schema for updating requirement."""
    
    min_quantity: Optional[Decimal] = Field(None, gt=0)
    max_quantity: Optional[Decimal] = Field(None, gt=0)
    preferred_quantity: Optional[Decimal] = Field(None, gt=0)
    quality_requirements: Optional[Dict[str, Any]] = None
    max_budget_per_unit: Optional[Decimal] = Field(None, gt=0)
    preferred_price_per_unit: Optional[Decimal] = Field(None, gt=0)
    total_budget: Optional[Decimal] = Field(None, gt=0)
    delivery_locations: Optional[List[Dict[str, Any]]] = None
    delivery_window_start: Optional[datetime] = None
    delivery_window_end: Optional[datetime] = None
    delivery_flexibility_hours: Optional[int] = Field(None, ge=0)
    market_visibility: Optional[str] = None
    invited_seller_ids: Optional[List[UUID]] = None
    urgency_level: Optional[str] = None
    commodity_equivalents: Optional[Dict[str, Any]] = None
    negotiation_preferences: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    attachments: Optional[List[Dict[str, Any]]] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "max_budget_per_unit": 78000.0,
                "urgency_level": "URGENT"
            }
        }


class RequirementSearchRequest(BaseModel):
    """Request schema for smart search."""
    
    commodity_id: Optional[UUID] = None
    min_quantity: Optional[Decimal] = Field(None, gt=0)
    max_quantity: Optional[Decimal] = Field(None, gt=0)
    quality_requirements: Optional[Dict[str, Any]] = None
    quality_tolerance: Optional[Dict[str, float]] = Field(
        None, description="Tolerance for each quality param"
    )
    min_budget: Optional[Decimal] = Field(None, gt=0)
    max_budget: Optional[Decimal] = Field(None, gt=0)
    urgency_level: Optional[str] = None
    intent_type: Optional[str] = None
    market_visibility: Optional[List[str]] = None
    buyer_latitude: Optional[float] = Field(None, ge=-90, le=90)
    buyer_longitude: Optional[float] = Field(None, ge=-180, le=180)
    max_distance_km: Optional[float] = Field(None, gt=0)
    min_priority_score: Optional[float] = Field(None, ge=0.5, le=2.0)
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "commodity_id": "123e4567-e89b-12d3-a456-426614174000",
                "min_quantity": 50.0,
                "quality_requirements": {"staple_length": 29.0},
                "quality_tolerance": {"staple_length": 1.0},
                "max_budget": 80000.0,
                "urgency_level": "NORMAL",
                "intent_type": "DIRECT_BUY",
                "min_priority_score": 1.0
            }
        }


class IntentSearchRequest(BaseModel):
    """🚀 Request schema for intent-based search."""
    
    intent_type: str = Field(description="DIRECT_BUY, NEGOTIATION, AUCTION_REQUEST, PRICE_DISCOVERY_ONLY")
    commodity_id: Optional[UUID] = None
    urgency_level: Optional[str] = None
    min_priority_score: Optional[float] = Field(None, ge=0.5, le=2.0)
    skip: int = Field(0, ge=0)
    limit: int = Field(100, ge=1, le=1000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "intent_type": "NEGOTIATION",
                "commodity_id": "123e4567-e89b-12d3-a456-426614174000",
                "urgency_level": "URGENT",
                "min_priority_score": 1.5
            }
        }


class FulfillmentUpdateRequest(BaseModel):
    """Request schema for updating fulfillment."""
    
    purchased_quantity: Decimal = Field(gt=0, description="Quantity purchased")
    amount_spent: Decimal = Field(gt=0, description="Amount spent")
    trade_id: Optional[UUID] = Field(None, description="Trade ID reference")
    
    class Config:
        json_schema_extra = {
            "example": {
                "purchased_quantity": 50.0,
                "amount_spent": 3500000.0,
                "trade_id": "123e4567-e89b-12d3-a456-426614174002"
            }
        }


class CancelRequirementRequest(BaseModel):
    """Request schema for cancelling requirement."""
    
    reason: str = Field(description="Cancellation reason")
    
    class Config:
        json_schema_extra = {
            "example": {
                "reason": "Requirement no longer needed"
            }
        }


# 🚀 ENHANCEMENT #7: AI ADJUSTMENT REQUEST
class AIAdjustmentRequest(BaseModel):
    """🚀 Request schema for applying AI-suggested adjustment."""
    
    adjustment_type: str = Field(
        description="Type: 'budget', 'quality', 'delivery_window', 'commodity_equivalents'"
    )
    new_value: Any = Field(description="New value to apply")
    ai_confidence: float = Field(ge=0.0, le=1.0, description="AI confidence score")
    ai_reasoning: str = Field(description="Human-readable explanation of AI decision")
    market_context: Optional[Dict[str, Any]] = Field(
        None, description="Market data used for decision"
    )
    expected_impact: Optional[str] = Field(
        None, description="Expected impact description"
    )
    auto_apply: bool = Field(
        default=False,
        description="If True, apply immediately. If False, suggest only."
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "adjustment_type": "budget",
                "new_value": 78000.0,
                "ai_confidence": 0.87,
                "ai_reasoning": "Market prices trending up 4% this week. Current budget may miss opportunities.",
                "market_context": {
                    "avg_market_price": 76500.0,
                    "trend": "rising",
                    "confidence": 0.92
                },
                "expected_impact": "Increases match probability by ~15%",
                "auto_apply": False
            }
        }


# ========================================================================
# RESPONSE SCHEMAS
# ========================================================================

class RequirementResponse(BaseModel):
    """Requirement response with all details and enhancements."""
    
    id: UUID
    requirement_number: str
    buyer_partner_id: UUID
    commodity_id: UUID
    variety_id: Optional[UUID]
    created_by_user_id: UUID
    
    # Quantity
    min_quantity: Decimal
    max_quantity: Decimal
    quantity_unit: str
    preferred_quantity: Optional[Decimal]
    
    # Quality
    quality_requirements: Dict[str, Any]
    
    # Budget & Pricing
    max_budget_per_unit: Decimal
    preferred_price_per_unit: Optional[Decimal]
    total_budget: Optional[Decimal]
    currency_code: str
    
    # 🚀 Risk Management & Credit Control
    estimated_trade_value: Optional[Decimal]
    buyer_credit_limit_remaining: Optional[Decimal]
    buyer_exposure_after_trade: Optional[Decimal]
    risk_precheck_status: Optional[str]
    risk_precheck_score: Optional[int]
    buyer_branch_id: Optional[UUID]
    blocked_internal_trades: bool
    buyer_rating_score: Optional[Decimal]
    buyer_payment_performance_score: Optional[int]
    
    # Payment & Delivery
    preferred_payment_terms: Optional[List[str]]
    preferred_delivery_terms: Optional[List[str]]
    delivery_locations: Optional[List[Dict[str, Any]]]
    
    # 🚀 ENHANCEMENT #3: Delivery Flexibility
    delivery_window_start: Optional[datetime]
    delivery_window_end: Optional[datetime]
    delivery_flexibility_hours: int
    
    # Market Visibility
    market_visibility: str
    invited_seller_ids: Optional[List[str]]
    
    # Lifecycle
    status: str
    valid_from: datetime
    valid_until: datetime
    urgency_level: str
    
    # 🚀 ENHANCEMENT #1: Intent Layer
    intent_type: str
    
    # Fulfillment Tracking
    total_matched_quantity: Decimal
    total_purchased_quantity: Decimal
    total_spent: Decimal
    active_negotiation_count: int
    
    # 🚀 ENHANCEMENT #2: AI Market Context Embedding
    market_context_embedding: Optional[List[float]]
    
    # AI Features
    ai_suggested_max_price: Optional[Decimal]
    ai_confidence_score: Optional[int]
    ai_score_vector: Optional[Dict[str, Any]]
    ai_price_alert_flag: bool
    ai_alert_reason: Optional[str]
    ai_recommended_sellers: Optional[List[Dict[str, Any]]]
    
    # 🚀 ENHANCEMENT #4: Commodity Equivalents
    commodity_equivalents: Optional[Dict[str, Any]]
    
    # 🚀 ENHANCEMENT #5: Negotiation Preferences
    negotiation_preferences: Optional[Dict[str, Any]]
    
    # 🚀 ENHANCEMENT #6: Buyer Priority Score
    buyer_priority_score: float
    
    # Metadata
    notes: Optional[str]
    attachments: Optional[List[Dict[str, Any]]]
    
    # Audit
    created_at: datetime
    updated_at: Optional[datetime]
    published_at: Optional[datetime]
    cancelled_at: Optional[datetime]
    cancelled_by_user_id: Optional[UUID]
    cancellation_reason: Optional[str]
    
    class Config:
        from_attributes = True


class RequirementSearchResult(BaseModel):
    """Single search result with match score."""
    
    requirement: RequirementResponse
    match_score: float = Field(ge=0.0, le=1.0, description="AI match score")
    distance_km: Optional[float] = Field(None, description="Distance to closest delivery location")
    buyer_priority_score: float = Field(description="Buyer trust score")
    intent_type: str = Field(description="Buyer intent type")
    remaining_quantity: Decimal = Field(description="Unfulfilled quantity remaining")
    ai_suggested_price: Optional[Decimal] = Field(None, description="AI suggested price")


class RequirementSearchResponse(BaseModel):
    """Search response with multiple results."""
    
    results: List[RequirementSearchResult]
    total: int
    skip: int
    limit: int


# 🚀 ENHANCEMENT #7: AI ADJUSTMENT RESPONSE
class AIAdjustmentResponse(BaseModel):
    """🚀 Response for AI adjustment operation."""
    
    requirement_id: UUID
    adjustment_type: str
    old_value: Any
    new_value: Any
    ai_confidence: float
    ai_reasoning: str
    market_context: Optional[Dict[str, Any]]
    expected_impact: Optional[str]
    applied: bool = Field(description="True if adjustment was applied, False if suggestion only")
    adjusted_at: datetime
    
    class Config:
        json_schema_extra = {
            "example": {
                "requirement_id": "123e4567-e89b-12d3-a456-426614174003",
                "adjustment_type": "budget",
                "old_value": 75000.0,
                "new_value": 78000.0,
                "ai_confidence": 0.87,
                "ai_reasoning": "Market prices trending up 4% this week",
                "applied": False,
                "adjusted_at": "2025-11-24T10:30:00Z"
            }
        }


# 🚀 NEW: REQUIREMENT EVENT HISTORY RESPONSE
class RequirementEventResponse(BaseModel):
    """🚀 Single requirement event from history."""
    
    event_type: str = Field(description="Event type (created, published, budget_changed, etc.)")
    event_data: Dict[str, Any] = Field(description="Event payload")
    occurred_at: datetime = Field(description="When event occurred")
    triggered_by: Optional[UUID] = Field(None, description="User who triggered event")
    
    class Config:
        json_schema_extra = {
            "example": {
                "event_type": "requirement.budget_changed",
                "event_data": {
                    "old_max_budget": 75000.0,
                    "new_max_budget": 78000.0,
                    "budget_change_pct": 4.0,
                    "reason": "Manual update"
                },
                "occurred_at": "2025-11-24T10:30:00Z",
                "triggered_by": "123e4567-e89b-12d3-a456-426614174005"
            }
        }


class RequirementHistoryResponse(BaseModel):
    """🚀 Response for requirement event history."""
    
    requirement_id: UUID
    requirement_number: str
    events: List[RequirementEventResponse]
    total_events: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "requirement_id": "123e4567-e89b-12d3-a456-426614174003",
                "requirement_number": "REQ-2025-000001",
                "events": [],
                "total_events": 15
            }
        }


class DemandStatisticsResponse(BaseModel):
    """Response for total demand statistics."""
    
    commodity_id: UUID
    total_unfulfilled_quantity: Decimal
    total_budget: Decimal
    avg_max_price: Decimal
    avg_preferred_price: Decimal
    active_requirement_count: int
    period_days: int
    
    class Config:
        json_schema_extra = {
            "example": {
                "commodity_id": "123e4567-e89b-12d3-a456-426614174000",
                "total_unfulfilled_quantity": 5000.0,
                "total_budget": 375000000.0,
                "avg_max_price": 76500.0,
                "avg_preferred_price": 73000.0,
                "active_requirement_count": 42,
                "period_days": 30
            }
        }


# 🚀 RISK MANAGEMENT RESPONSE
class RiskPrecheckResponse(BaseModel):
    """Response for risk precheck assessment."""
    
    risk_precheck_status: str = Field(description="PASS, WARN, or FAIL")
    risk_precheck_score: int = Field(ge=0, le=100, description="Risk score (0-100)")
    estimated_trade_value: Optional[Decimal] = Field(None, description="Estimated trade value")
    buyer_exposure_after_trade: Optional[Decimal] = Field(
        None, description="Projected exposure if trade executes"
    )
    risk_factors: List[str] = Field(default_factory=list, description="Identified risk factors")
    buyer_credit_limit_remaining: Optional[Decimal] = Field(None, description="Remaining credit")
    buyer_rating_score: Optional[Decimal] = Field(None, ge=0.0, le=5.0, description="Buyer rating")
    buyer_payment_performance_score: Optional[int] = Field(
        None, ge=0, le=100, description="Payment performance"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "risk_precheck_status": "PASS",
                "risk_precheck_score": 85,
                "estimated_trade_value": 7650000.0,
                "buyer_exposure_after_trade": 2350000.0,
                "risk_factors": [],
                "buyer_credit_limit_remaining": 10000000.0,
                "buyer_rating_score": 4.5,
                "buyer_payment_performance_score": 92
            }
        }

# ErrorResponse imported from modules.common.schemas.responses
